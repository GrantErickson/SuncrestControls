#!/usr/bin/env python3
"""Builds the lobby Stream Deck configuration from one definition.

Run:  python config/stream-deck/build.py

Produces, from the tables in this file:
  config/stream-deck/lobby.companionconfig   importable Companion 5.1 file
  config/stream-deck/icons/*.svg, *.png      key and touch-strip artwork
  docs/14-stream-deck-pages.md               page-by-page reference
  docs/images/stream-deck-pages.png          the pages, drawn from the real buttons

It needs only Python and an installed Chrome or Edge, which draws the artwork.
Nothing here runs at the church. Once the file is imported, Companion is the
live copy, and this script is only for rebuilding before that point.

Every button is a Companion 5 layered button: artwork, a live label, and for the
touch strip, bars drawn from variables. Every expression
in the file is parsed and run by the small evaluator below before anything is written.
"""
import base64
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ICONS = HERE / "icons"
DOC = ROOT / "docs" / "14-stream-deck-pages.md"
IMAGES = ROOT / "docs" / "images"

# ---------------------------------------------------------------- the system
WING_IP, ODE_IP, WIIM_IP = "192.168.50.20", "192.168.50.31", "192.168.50.40"
POWER_IP = "192.168.50.45"  # network relay that closes the Furman sequencer's remote contact, which powers the amps
ARTNET_UNIVERSE = 0

ZONES = [  # number, name, matrix, default fader in dB, page, icon
    (1, "Mains", 1, -6, 4, "speaker"),
    (2, "Outdoor", 2, -10, 5, "tree"),
    (3, "Soffit", 3, -10, 6, "soffit"),
    (4, "Bathrooms", 4, -12, 7, "restroom"),
    (5, "Vestibule", 5, -12, 8, "door"),
]
SOURCES = [  # name, Wing send source, label on key, icon
    ("Auditorium", "/bus/14", "Auditorium", "church"),
    ("Playlist", "/bus/15", "Playlist", "note"),
    ("Bluetooth", "/bus/16", "Bluetooth", "bluetooth"),
    ("Lobby Mix", "/main/1", "Lobby Mix", "mic"),
]
MIC_BUS = 13  # wireless mics, always sent to every zone matrix
LOOKS = [  # number, linear %, fixtures %. Starting points: holding a Lights key saves over them
    (1, 35, 35),
    (2, 65, 65),
    (3, 100, 100),
]
LIGHT_GROUPS = [  # DMX channels, level that drives them, DMX value at 100%, what they are
    ("1-8", "lt_linear", 255, "Linear house lights, through 0-10V decoders"),
    ("9-32", "lt_fix", 255, "Every other fixture's intensity channel"),
]
STATIC_CHANNELS = []  # (DMX channels, value), for channels that never change, like a fixture's mode
PLAYLISTS = [(1, "Morning", "sunrise"), (2, "Everyday", "calendar"), (3, "Evening", "sunset"),
             (4, "Seasonal", "star")]
SCENES = [  # name, label on key, icon, source per zone
    ("Auditorium", "Auditorium", "church", ["Auditorium", "Off", "Off", "Auditorium", "Auditorium"]),
    ("Music Inside", "Inside", "home", ["Playlist", "Off", "Off", "Playlist", "Playlist"]),
    ("Music Everywhere", "Everywhere", "broadcast", ["Playlist"] * 5),
    ("Lobby Event", "Lobby Event", "mic", ["Lobby Mix", "Off", "Off", "Lobby Mix", "Lobby Mix"]),
    ("Bluetooth", "Bluetooth", "bluetooth", ["Bluetooth", "Off", "Off", "Bluetooth", "Bluetooth"]),
    ("All Audio Off", "Audio Off", "mute", ["Off"] * 5),
]
LIGHT_STEP = 5         # percent per dial step
TURN_MEDIUM_MS, TURN_FAST_MS = 120, 50  # starting values: clicks closer together than these count as a quicker turn
TURN_MEDIUM, TURN_FAST = 2, 4           # steps per click when the dial turns at medium or fast speed
TURN_MAX = 8                            # the most steps one report from the dial can make
FADE_MS, QUICK_MS = 2000, 150
IPAD_HOLD_MS = 1000
SAVE_HOLD_MS = 3000
CLOSE_HOLD_MS = 1500
SAVED_MS = 2000
VOL_MIN, VOL_MAX = -60, 0          # every zone fader stays inside this range
SRC_MIN, SRC_MAX = -60, 6          # the Volume dial moves the playing source's fader inside this range
VOLUME_SOURCES = [  # zone source, its Wing fader, the variable that keeps it, panel title, color
    ("Auditorium", "/bus/14", "aud_level", "AUDITORIUM", "audio"),
    ("Playlist", "/bus/15", "music_level", "MUSIC", "music"),
    ("Bluetooth", "/bus/16", "bt_level", "BLUETOOTH", "audio"),
    ("Lobby Mix", "/main/1", "lobby_level", "LOBBY MIX", "audio"),
]
MIC_MIN, MIC_MAX = -60, 0
MIC_START = -10                    # Bus 13's level in the Lobby Base snapshot

ACCENTS = {  # one color per kind of key. Every tile, bar and ring color is worked out from these
    "light": "#ffb52e", "linear": "#f2d49b", "audio": "#4aa8ff", "music": "#a888ff", "mic": "#3fd6c2",
    "off": "#ff6b57", "nav": "#9aa6b5", "ipad": "#c27bff", "save": "#3fd68a", "power": "#38c172",
}


def mix(a, b, t):
    """Blend two #rrggbb colors, t=0 gives a and t=1 gives b."""
    ca, cb = [[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in (a, b)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


PALETTE = {  # rest top, rest bottom, glyph at rest, active top, active bottom, accent for bars and rings
    cat: (mix(c, "#000000", 0.62), mix(c, "#000000", 0.82), mix(c, "#ffffff", 0.22),
          c, mix(c, "#000000", 0.40), c)
    for cat, c in ACCENTS.items()
}
LOCKED_ART = ("#272a2f", "#131518", "#5d646d")
TRACK = "#262b32"
DIM = "#59616b"
BADGE = "#ff9d3c"
TEXT_REST, TEXT_ACTIVE, TEXT_DIM = 0xF2F5F8, 0xFFFFFF, 0x6B7480
LABEL_OUTLINE = "rgba(0,0,0,0.45)"


def accent(cat):
    return PALETTE[cat][5]


# ---------------------------------------------------------------- entities
_counter = [0]


def nid(prefix="e"):
    _counter[0] += 1
    return f"{prefix}{_counter[0]:05d}"


def val(v):
    return {"isExpression": False, "value": v}


def expr(s):
    return {"isExpression": True, "value": s}


def is_wrapped(v):
    return isinstance(v, dict) and "isExpression" in v


def wrap(o):
    return {k: (v if is_wrapped(v) else val(v)) for k, v in o.items()}


ARTNET_UPGRADE = 1  # the generic-artnet module has two upgrade scripts, and these actions are already current


def action(conn, definition, children=None, upgrade=None, **options):
    e = {"type": "action", "id": nid(), "definitionId": definition, "connectionId": conn,
         "options": wrap(options)}
    if upgrade is not None:
        e["upgradeIndex"] = upgrade
    if children:
        e["children"] = children
    return e


def press(loc):
    return action("internal", "button_pressrelease", location=loc, force=True, duration=0)


def wait(ms):
    return action("internal", "wait", time=expr(str(ms)))


def setvar(name, value):
    return action("internal", "custom_variable_set_value", name=name, create=False,
                  value=value if is_wrapped(value) else str(value))


def keep(name):
    """Writes a variable's current value to its startup value, so exports and backups carry it."""
    return action("internal", "custom_variable_sync_to_default", name=name)


def setexpr(name, expression):
    return setvar(name, expr(expression))


def setpage(n):
    return action("internal", "set_page", surfaceId="self", page=n)


def check(expression):
    return {"type": "feedback", "id": nid(), "definitionId": "check_expression",
            "connectionId": "internal", "options": {"expression": expr(expression)}}


def when(expression, then, otherwise=None):
    return action("internal", "logic_if", children={
        "condition": [check(expression)], "actions": then, "else_actions": otherwise or []})


def wiim(command):
    return action("wiim", "get", url=f"httpapi.asp?command={command}", header="",
                  jsonResultDataVariable="", result_stringify=True, statusCodeVariable="")


def wing_send(src, mx, on):
    return action("wing", "set-send-mute", src=src, dest=f"/mtx/{mx}", mainDest=f"/mtx/{mx}",
                  mute="0" if on else "1")


def wing_mute(sel, muted):
    return action("wing", "set-mute", sel=sel, mute={True: "1", False: "0", None: "-1"}[muted])


FADE = dict(fadeDuration=0, fadeAlgorithm="linear", fadeType="ease-in-out")


def wing_level(sel, db):
    return action("wing", "set-fader", sel=sel, level=db, **FADE)


def wing_delta(sel, db):
    return action("wing", "fader-delta", sel=sel, delta=db, **FADE)


def dmx_send(ms):
    return action("dmx", "set_complex", upgrade=ARTNET_UPGRADE, params="$(custom:dmx_cmd)", duration=ms)


def relay(on):
    """Closes or opens the relay on the Furman's remote terminals, so it sequences the amplifiers on or off."""
    return action("power", "get", url=f"rpc/Switch.Set?id=0&on={'true' if on else 'false'}", header="",
                  jsonResultDataVariable="", result_stringify=True, statusCodeVariable="")


# ---------------------------------------------------------------- expressions
class X(str):
    """Marks an expression part inside tmpl()."""


def tmpl(*parts):
    """A Companion template string. Plain parts are text, X() parts are expressions."""
    return "`" + "".join("${" + p + "}" if isinstance(p, X) else p for p in parts) + "`"


IPAD = "$(custom:light_mode) == 'ipad'"
DECK = "$(custom:light_mode) == 'deck'"
ALL, LIN, FIX, LOOK = "$(custom:lt_all)", "$(custom:lt_linear)", "$(custom:lt_fix)", "$(custom:lt_look)"
LIGHTS_ON = f"{ALL} > 0"
TURN_N = "$(custom:turn_n)"  # steps for the dial click being handled, set by the dial before its block runs


def turn_speed(key):
    """Steps for one dial report: the clicks it reports, times more when they come quickly in one direction."""
    return ("d = $(this:delta);\n"
            "c = isNumber(d) ? max(1, abs(d)) : 1;\n"
            "g = unixNow() - $(custom:turn_ms);\n"
            f"f = $(custom:turn_key) != '{key}' ? 1 : (g < $(custom:turn_fast_ms) ? {TURN_FAST} : "
            f"(g < $(custom:turn_medium_ms) ? {TURN_MEDIUM} : 1));\n"
            f"min({TURN_MAX}, c * f)")


def turned(key):
    """The first actions of every dial turn: work out its speed, then remember when and which way it turned."""
    return [setexpr("turn_n", turn_speed(key)), setexpr("turn_ms", "unixNow()"), setvar("turn_key", key)]


def plays(source):
    """True while any zone plays this source."""
    return " || ".join(f"$(custom:z{z}_src) == '{source}'" for z, *_ in ZONES)


NONE_PLAYLIST = " && ".join(f"$(custom:z{z}_src) != 'Playlist'" for z, *_ in ZONES)
ANY_PLAYLIST = plays("Playlist")
POWERED = "$(custom:audio_power) == 1"  # the amplifiers are on
UNPOWERED = f"!({POWERED})"


def tracked(wing_var, custom):
    """The Wing's level when it reports one, otherwise the level Companion has been keeping in step."""
    return f"({wing_var} == '-oo' ? -90 : (isNumber({wing_var}) ? {wing_var} : $(custom:{custom})))"


ZONE_NOW = {z: tracked(f"$(wing:mtx{mx}_level)", f"z{z}_level") for z, _, mx, *_ in ZONES}
MIC_NOW = tracked(f"$(wing:bus{MIC_BUS}_level)", "mic_level")
MIC_MUTED = f"(isNumber($(wing:bus{MIC_BUS}_mute)) ? $(wing:bus{MIC_BUS}_mute) : $(custom:mic_muted)) == 1"
WING_ONLINE = "isNumber($(wing:mtx1_level)) || $(wing:mtx1_level) == '-oo'"


def _first_source():
    chain = "'Off'"
    for z, *_ in reversed(ZONES):
        chain = f"$(custom:z{z}_src) != 'Off' ? $(custom:z{z}_src) : ({chain})"
    return chain


# What the Volume dial controls: the source of the first zone that is on, or nothing while the audio is off
CUR_SRC = f"({POWERED} ? ({_first_source()}) : 'Off')"
SRC_NOW = {name: tracked(f"$(wing:{sel.strip('/').replace('/', '')}_level)", var)
           for name, sel, var, _, _ in VOLUME_SOURCES}


def with_source(body):
    """An expression that first works out the playing source (c) and its fader level (v)."""
    chain = "0"
    for name, *_ in reversed(VOLUME_SOURCES):
        chain = f"c == '{name}' ? {SRC_NOW[name]} : ({chain})"
    return f"c = {CUR_SRC};\nv = {chain};\n{body}"


def source_pick(values, otherwise):
    """A chain picking a value by the playing source, which must already be in c."""
    chain = otherwise
    for name, value in reversed(list(values.items())):
        chain = f"c == '{name}' ? {value} : ({chain})"
    return chain


def level_var(sel):
    kind, n = sel.strip("/").split("/")
    return f"$(wing:{kind}{n}_level)"


def db_text(level):
    return tmpl(X(f"round({level})"), " dB")


def db_pct(level, lo, hi):
    return f"max(0, min(100, ({level} - ({lo})) * 100 / {hi - lo}))"


def fader_step(var, now, sel, lo, hi, sign):
    """Moves a fader by this turn's steps in dB, inside lo to hi. Companion's copy and the Wing move by the same amount."""
    if sign > 0:
        cond, target = f"{now} < {hi}", f"min({hi}, {now} + {TURN_N})"
    else:
        cond, target = f"{now} > {lo}", f"max({lo}, {now} - {TURN_N})"
    return when(cond, [setexpr(var, target), wing_delta(sel, expr(f"{target} - {now}"))])


def zone_step(z, mx, sign):
    """One dial report on a zone's volume."""
    return fader_step(f"z{z}_level", ZONE_NOW[z], f"/mtx/{mx}", VOL_MIN, VOL_MAX, sign)


def scene_expr(zones):
    return " && ".join(f"$(custom:z{i + 1}_src) == '{s}'" for i, s in enumerate(zones))


def compute_expr():
    parts = []
    for channels, variable, full, _ in LIGHT_GROUPS:
        parts += [f"{channels},", X(f"round({full} * k * $(custom:{variable}) / 100)"), ";"]
    for channels, value in STATIC_CHANNELS:
        parts += [f"{channels},", X(f"{IPAD} ? 0 : {value}"), ";"]
    return f"k = {IPAD} ? 0 : {ALL} / 100;\n" + tmpl(*parts)


# ---------------------------------------------------------------- pages
@dataclass
class Key:
    page: int
    row: int
    col: int
    label: str = ""
    icon: str | None = None
    cat: str = "nav"
    kind: str = "key"                # key, strip, dial, lib
    down: list = field(default_factory=list)
    up: list = field(default_factory=list)
    hold: tuple | None = None        # (ms, actions), run while held
    left: list | None = None
    right: list | None = None
    fb: list = field(default_factory=list)  # (expression, state): active, locked or saved
    labels: dict = field(default_factory=dict)  # label to show in a state, when it changes
    does: str = ""
    show: dict | None = None         # the display, for touch strip keys

    @property
    def loc(self):
        return f"{self.page}/{self.row}/{self.col}"


PAGES = {  # every station is a Stream Deck +, and they all share these pages
    1: ("Home", "deck"), 2: ("More", "deck"), 3: ("Playlists", "deck"),
    4: ("Zone Mains", "deck"), 5: ("Zone Outdoor", "deck"), 6: ("Zone Soffit", "deck"),
    7: ("Zone Bathrooms", "deck"), 8: ("Zone Vestibule", "deck"),
    20: ("Library: Zones", "library"), 21: ("Library: Music and Rooms", "library"),
    22: ("Library: Lights and Dials", "library"),
}
BOUNDS = {"deck": (4, 4), "library": (4, 8)}
KEYS: dict[str, Key] = {}


def add(page, row, col, **kw):
    k = Key(page, row, col, **kw)
    assert k.loc not in KEYS, k.loc
    KEYS[k.loc] = k
    return k


def at(loc):
    return tuple(int(x) for x in loc.split("/"))


def zone_block(z, s):
    """Library location of a zone/source block. s 0-3 is a source, 4 is Off."""
    return f"20/{z - 1}/{s}" if z <= 4 else f"21/0/{s}"


DEFAULT_LEVELS, MUSIC_PLAY, MUSIC_START, MUSIC_STOP = "21/0/5", "21/0/6", "21/0/7", "21/1/0"
PLAYLIST_LOC = {n: f"21/1/{n}" for n, *_ in PLAYLISTS}
SCENE_LOC = {s[0]: f"21/2/{i}" for i, s in enumerate(SCENES)}
POWER_ON, POWER_OFF = "21/3/0", "21/3/1"
STOP_LOC = {source: f"21/3/{i + 2}" for i, (source, *_) in enumerate(SOURCES)}
LOOK_LOC = {n: f"22/0/{n - 1}" for n, *_ in LOOKS}
LIGHTS_OFF, LIGHTS_TOGGLE = "22/0/3", "22/0/4"
SAVE_LOC = {n: f"22/0/{n + 4}" for n, *_ in LOOKS}
COMPUTE, APPLY_FADE, APPLY_QUICK, IPAD_TOGGLE = "22/1/0", "22/1/1", "22/1/2", "22/1/3"
ALL_UP, ALL_DOWN, LIN_UP, LIN_DOWN = "22/1/4", "22/1/5", "22/1/6", "22/1/7"
LIN_RESET, VOL_UP, VOL_DOWN, MIC_UP, MIC_DOWN, MIC_MUTE, CLOSE_UP, VOL_RESET = (
    "22/2/0", "22/2/1", "22/2/2", "22/2/3", "22/2/4", "22/2/5", "22/2/6", "22/2/7")


def lib(loc, label, down, does):
    return add(*at(loc), label=label, kind="lib", down=down, does=does)


def look_level(n, group):
    return f"$(custom:look{n}_{group})"


def current_look(group):
    chain = look_level(LOOKS[-1][0], group)
    for n, *_ in reversed(LOOKS[:-1]):
        chain = f"{LOOK} == {n} ? {look_level(n, group)} : ({chain})"
    return chain


def build_library():
    # Page 20 and row 0 of page 21: one block per zone and source
    for z, name, mx, _, _, _ in ZONES:
        sel = f"/mtx/{mx}"
        for s, (source, _, _, _) in enumerate(SOURCES):
            acts = [wing_send(src, mx, src == SOURCES[s][1]) for _, src, _, _ in SOURCES]
            acts += [wing_mute(sel, False), setvar(f"z{z}_src", source)]
            lib(zone_block(z, s), f"Z{z}\n{source}", acts, f"{name} plays {source}")
        lib(zone_block(z, 4), f"Z{z}\nOff", [wing_mute(sel, True), setvar(f"z{z}_src", "Off")], f"{name} off")
    normal = []
    for z, _, mx, db, _, _ in ZONES:
        normal += [wing_level(f"/mtx/{mx}", db), setvar(f"z{z}_level", db)]
    for name, sel, var, _, _ in VOLUME_SOURCES:
        if name != "Lobby Mix":  # Main 1 belongs to whoever is mixing the band, so room buttons leave it alone
            normal += [wing_level(sel, 0), setvar(var, 0)]
    lib(DEFAULT_LEVELS, "Default\nLevels", normal,
        "Resets every zone fader to its normal level, and the auditorium, music and Bluetooth faders to 0 dB")
    # Music
    lib(MUSIC_PLAY, "Music\nPlay", [wiim("MCUKeyShortClick:$(custom:music_n)"), wait(2000),
                                    wiim("setPlayerCmd:loopmode:2")],
        "Starts the chosen playlist, then turns on shuffle and repeat")
    lib(MUSIC_START, "Music\nStart", [when(NONE_PLAYLIST, [press(MUSIC_PLAY)])],
        "Starts music only if nothing is already playing it")
    lib(MUSIC_STOP, "Music\nStop", [when(NONE_PLAYLIST, [wiim("setPlayerCmd:stop")])],
        "Stops the player once no zone is using it")
    for n, name, _ in PLAYLISTS:
        lib(PLAYLIST_LOC[n], f"P{n}\n{name}",
            [setvar("music_n", n), setvar("music_name", name), wait(50),
             when(ANY_PLAYLIST, [press(MUSIC_PLAY)], [press(SCENE_LOC["Music Inside"])])],
            f"Chooses {name}. Plays it now, or starts Music Inside if the room is silent")
    # Row 2 of page 21: the whole-room scenes. A scene that plays anything turns the amplifiers on first
    for name, _, _, zones in SCENES:
        uses_music = "Playlist" in zones
        acts = [press(POWER_ON)] if any(z != "Off" for z in zones) else []
        acts += [press(MUSIC_START), wait(50)] if uses_music else []
        for z, source in enumerate(zones, 1):
            s = [x[0] for x in SOURCES].index(source) if source != "Off" else 4
            acts.append(press(zone_block(z, s)))
        acts.append(press(DEFAULT_LEVELS))
        if not uses_music:
            acts += [wait(200), press(MUSIC_STOP)]
        lib(SCENE_LOC[name], f"Room\n{name}", acts, "Sets all five zones and their normal levels" +
            (", and turns the audio system on" if any(z != "Off" for z in zones)
             else ". It leaves the amplifiers as they are"))
    # Row 3 of page 21: amplifier power, and turning one source off
    lib(POWER_ON, "Power\nOn", [setvar("audio_power", 1), relay(True)],
        "Turns the audio system on: the relay closes and the Furman sequences the amplifiers on")
    lib(POWER_OFF, "Power\nOff", [press(SCENE_LOC["All Audio Off"]), wait(500), setvar("audio_power", 0),
                                  relay(False)],
        "Turns every zone off and stops the music, then opens the relay so the Furman sequences the amplifiers off")
    for source, _, label, _ in SOURCES:
        acts = [when(f"$(custom:z{z}_src) == '{source}'", [press(zone_block(z, 4))]) for z, *_ in ZONES]
        if source == "Playlist":
            acts += [wait(200), press(MUSIC_STOP)]
        lib(STOP_LOC[source], f"Stop\n{label}", acts,
            f"Turns off every zone playing {source}, and leaves the other zones and the amplifiers alone")

    # Page 22: lights. Levels live in variables, and one block turns them into DMX
    for n, *_ in LOOKS:
        lib(LOOK_LOC[n], f"Look {n}", [when(DECK, [
            setvar("lt_look", n), setvar("lt_all", 100),
            setexpr("lt_linear", look_level(n, "linear")), setexpr("lt_fix", look_level(n, "fix")),
            wait(20), press(APPLY_FADE)])],
            f"Fades to Lights {n} at full, unless iPad Mode is on")
    lib(LIGHTS_OFF, "Lights\nOff", [when(DECK, [setvar("lt_all", 0), wait(20), press(APPLY_FADE)])],
        "Fades the lights out and keeps the look, so the All Lights dial can bring it back")
    lib(LIGHTS_TOGGLE, "Lights\nOn/Off", [when(DECK, [when(LIGHTS_ON, [press(LIGHTS_OFF)], [
        setvar("lt_all", 100), wait(20), press(APPLY_FADE)])])],
        "Turns the lights off, or back on to the last look")
    for n, *_ in LOOKS:
        lib(SAVE_LOC[n], f"Save {n}", [when(f"{DECK} && {LIGHTS_ON}", [
            setexpr(f"look{n}_linear", f"round({LIN} * {ALL} / 100)"),
            setexpr(f"look{n}_fix", f"round({FIX} * {ALL} / 100)"),
            wait(20), keep(f"look{n}_linear"), keep(f"look{n}_fix"),
            setvar("lt_look", n), setvar("lt_all", 100),
            setexpr("lt_linear", look_level(n, "linear")), setexpr("lt_fix", look_level(n, "fix")),
            setvar("lt_saved", n), wait(20), press(APPLY_QUICK),
            wait(SAVED_MS), setvar("lt_saved", 0)])],
            f"Saves the lights as they are now into Lights {n}")
    lib(COMPUTE, "Compute\nDMX", [setexpr("dmx_cmd", compute_expr())],
        "Works out every channel from the levels. The patch lives here")
    lib(APPLY_FADE, "Apply\nFade", [press(COMPUTE), wait(20), dmx_send(FADE_MS)],
        f"Sends the levels to the ODE over {FADE_MS / 1000:g} seconds")
    lib(APPLY_QUICK, "Apply\nQuick", [press(COMPUTE), wait(20), dmx_send(QUICK_MS)],
        "Sends the levels to the ODE right away, for the dials")
    lib(IPAD_TOGGLE, "iPad\nToggle", [when(DECK, [setvar("light_mode", "ipad"), wait(20), press(APPLY_FADE)],
                                           [setvar("light_mode", "deck"), wait(20), press(APPLY_FADE)])],
        "Hands the lights to the iPad by fading Companion's output out, or takes them back")
    for loc, label, var, sign in ((ALL_UP, "All\nUp", ALL, 1), (ALL_DOWN, "All\nDown", ALL, -1),
                                  (LIN_UP, "Linear\nUp", LIN, 1), (LIN_DOWN, "Linear\nDown", LIN, -1)):
        name = re.search(r"custom:(\w+)", var).group(1)
        value = (f"min(100, {var} + {LIGHT_STEP} * {TURN_N})" if sign > 0
                 else f"max(0, {var} - {LIGHT_STEP} * {TURN_N})")
        lib(loc, label, [when(DECK, [setexpr(name, value), wait(10), press(APPLY_QUICK)])],
            f"{'Raises' if sign > 0 else 'Lowers'} {'all lights' if var == ALL else 'the linear lights'} "
            f"by {LIGHT_STEP}% for each step in `turn_n`, stopping at {'100' if sign > 0 else '0'}%")
    lib(LIN_RESET, "Linear\nReset", [when(DECK, [setexpr("lt_linear", current_look("linear")), wait(20),
                                                  press(APPLY_FADE)])],
        "Puts the linear lights back to the current look's level")
    def source_step(sign):
        return [when(f"{CUR_SRC} == '{name}'", [fader_step(var, SRC_NOW[name], sel, SRC_MIN, SRC_MAX, sign)])
                for name, sel, var, _, _ in VOLUME_SOURCES]

    lib(VOL_UP, "Volume\nUp", source_step(1),
        f"Raises whatever is playing by 1 dB for each step in `turn_n`, up to {SRC_MAX} dB over normal")
    lib(VOL_DOWN, "Volume\nDown", source_step(-1),
        f"Lowers whatever is playing by 1 dB for each step in `turn_n`, down to {SRC_MIN} dB")
    lib(VOL_RESET, "Volume\nReset", [when(f"{CUR_SRC} == '{name}'", [wing_level(sel, 0), setvar(var, 0)])
                                      for name, sel, var, _, _ in VOLUME_SOURCES],
        "Puts whatever is playing back to its normal level, 0 dB")
    mic = f"/bus/{MIC_BUS}"
    lib(MIC_UP, "Mic\nUp", [when(POWERED, [fader_step("mic_level", MIC_NOW, mic, MIC_MIN, MIC_MAX, 1)])],
        f"Raises the mic bus by 1 dB for each step in `turn_n`, stopping at {MIC_MAX} dB. Only while the audio is on")
    lib(MIC_DOWN, "Mic\nDown", [when(POWERED, [fader_step("mic_level", MIC_NOW, mic, MIC_MIN, MIC_MAX, -1)])],
        f"Lowers the mic bus by 1 dB for each step in `turn_n`, stopping at {MIC_MIN} dB. Only while the audio is on")
    lib(MIC_MUTE, "Mic\nMute", [when(POWERED, [when(MIC_MUTED, [wing_mute(mic, False), setvar("mic_muted", 0)],
                                                     [wing_mute(mic, True), setvar("mic_muted", 1)])])],
        "Mutes or unmutes the mic bus. Only while the audio is on")
    lib(CLOSE_UP, "Close\nUp", [setvar("light_mode", "deck"), wait(20), press(LIGHTS_OFF), press(POWER_OFF)],
        "Leaves iPad Mode, then turns off the lights and the audio system")


# ---------------------------------------------------------------- displays
def light_display():
    return {
        "title": "ALL LIGHTS", "art": "light",
        "value": f"{IPAD} ? 'iPad' : ({LIGHTS_ON} ? " + tmpl(X(ALL), "%") + " : 'Off')",
        "pct": f"{IPAD} ? 0 : {ALL}",
        "color": f"{IPAD} ? '{accent('ipad')}' : '{accent('light')}'",
        "value_color": f"{IPAD} ? '{accent('ipad')}' : ({LIGHTS_ON} ? '#ffffff' : '{DIM}')",
    }


LINEAR_DISPLAY = {
    "title": "LINEAR", "art": "linear",
    "value": f"{IPAD} ? 'iPad' : " + tmpl(X(LIN), "%"),
    "pct": f"{IPAD} ? 0 : {LIN}",
    "color": f"{IPAD} ? '{accent('ipad')}' : ({LIGHTS_ON} ? '{accent('linear')}' : '{DIM}')",
    "value_color": f"{IPAD} ? '{accent('ipad')}' : ({LIGHTS_ON} ? '#ffffff' : '{DIM}')",
}
VOLUME_DISPLAY = {
    "title": f"c = {CUR_SRC};\n" + source_pick({n: f"'{t}'" for n, _, _, t, _ in VOLUME_SOURCES}, "'VOLUME'"),
    "title_expr": True, "art": "audio",
    "value": with_source("c == 'Off' ? 'Off' : (round(v) == 0 ? 'Normal' : "
                         + tmpl(X("v > 0 ? '+' : ''"), X("round(v)"), " dB") + ")"),
    "pct": with_source(f"c == 'Off' ? 0 : max(0, min(100, (v - ({SRC_MIN})) * 100 / {SRC_MAX - SRC_MIN}))"),
    "tick": -SRC_MIN * 100 / (SRC_MAX - SRC_MIN),
    "color": f"c = {CUR_SRC};\n" + source_pick({n: f"'{accent(cat)}'" for n, _, _, _, cat in VOLUME_SOURCES},
                                                f"'{DIM}'"),
    "value_color": f"c = {CUR_SRC};\nc == 'Off' ? '{DIM}' : '#ffffff'",
    "badge": f"!({WING_ONLINE})",
    "dim": UNPOWERED,
}
MIC_DISPLAY = {
    "title": "MICS", "art": "mic",
    "value": f"{UNPOWERED} ? 'Off' : ({MIC_MUTED} ? 'Muted' : " + db_text(MIC_NOW) + ")",
    "pct": f"{UNPOWERED} ? 0 : " + db_pct(MIC_NOW, MIC_MIN, MIC_MAX),
    "color": f"{UNPOWERED} ? '{DIM}' : ({MIC_MUTED} ? '{accent('off')}' : '{accent('mic')}')",
    "value_color": f"{UNPOWERED} ? '{DIM}' : ({MIC_MUTED} ? '{accent('off')}' : '#ffffff')",
    "badge": f"!({WING_ONLINE})",
    "dim": UNPOWERED,
}


def zone_display(zone):
    z, name, mx, *_ = zone
    src = f"$(custom:z{z}_src)"
    return {
        "title": tmpl(name.upper(), " · ", X(src)), "title_expr": True, "art": f"zone-{zone[5]}",
        "value": f"{src} == 'Off' ? 'Off' : " + db_text(ZONE_NOW[z]),
        "pct": db_pct(ZONE_NOW[z], VOL_MIN, VOL_MAX),
        "color": f"{src} == 'Off' ? '{DIM}' : '{accent('audio')}'",
        "value_color": f"{src} == 'Off' ? '{DIM}' : '#ffffff'",
        "dim": UNPOWERED,
    }


# ---------------------------------------------------------------- keys people use
def nav(page, row, col, target, label, icon, does=None):
    return add(page, row, col, label=label, icon=icon, down=[setpage(target)],
               does=does or f"Opens {PAGES[target][0]}")


def scene_key(page, r, c, name, label=None, cat="audio"):
    s = next(x for x in SCENES if x[0] == name)
    return add(page, r, c, label=label or s[1], icon=s[2], cat=cat, does=f"Runs {name} on all five zones",
               down=[press(SCENE_LOC[name])], fb=[(scene_expr(s[3]), "active")])


SOURCE_NOUN = {"Auditorium": "the auditorium feed", "Playlist": "music", "Bluetooth": "Bluetooth",
               "Lobby Mix": "the lobby mix"}


def source_key(page, r, c, scene, source, label, icon, cat="audio"):
    """A toggle: plays its room scene, which replaces whatever else plays, or turns its source off when lit."""
    return add(page, r, c, label=label, icon=icon, cat=cat, fb=[(plays(source), "active")],
               down=[when(plays(source), [press(STOP_LOC[source])], [press(SCENE_LOC[scene])])],
               does=f"Lit while {SOURCE_NOUN[source]} plays. Press to play {scene}, turning the audio system on if it "
                    f"is off and replacing anything else playing. Press again to turn {SOURCE_NOUN[source]} off")


def audio_power_key(page, r, c):
    """The audio power key. Its color shows the state, green for on and red for off, and its label says what a
    press does."""
    add(page, r, c, label="Turn Audio Off", icon="power", cat="off",
        fb=[(POWERED, "on"), (UNPOWERED, "active")], labels={"active": "Turn Audio On"},
        down=[when(POWERED, [press(POWER_OFF)], [press(POWER_ON)])],
        does="Green while the audio is on, saying Turn Audio Off: press to turn every zone off, then the amplifiers. "
             "Red while it's off, saying Turn Audio On: press to turn the system on with nothing playing. "
             "Auditorium and Music also turn it on")


def lights_off_key(page, r, c):
    add(page, r, c, label="Lights Off", icon="bulb_off", cat="off", down=[press(LIGHTS_OFF)],
        does="Fades the lights out. Turning All Lights brings them back",
        fb=[(f"!({LIGHTS_ON})", "active"), (IPAD, "locked")])


def look_key(page, r, c, n):
    add(page, r, c, label=f"Lights {n}", icon=f"level{n}", cat="light",
        fb=[(f"{LOOK} == {n} && {LIGHTS_ON}", "active"), (IPAD, "locked"), (f"$(custom:lt_saved) == {n}", "saved")],
        labels={"saved": "Saved"}, up=[press(LOOK_LOC[n])], hold=(SAVE_HOLD_MS, [press(SAVE_LOC[n])]),
        does=f"Tap for Lights {n}. Hold {SAVE_HOLD_MS // 1000} seconds to save the lights as they are now into it")


def strip(page, col, show, does):
    add(page, 2, col, kind="strip", show=show, cat=show["art"], does=does)


def dial(page, col, label, push, left, right, does, turn):
    """A dial. `turn` names it, so quick clicks in one direction speed up only that dial."""
    add(page, 3, col, kind="dial", label=label, down=push, left=turned(f"{turn}-") + left,
        right=turned(f"{turn}+") + right, does=does)


def deck_dials(page, zone=None):
    strip(page, 0, light_display(), "Touch strip: the All Lights level, Off, or iPad")
    dial(page, 0, "All Lights", [press(LIGHTS_TOGGLE)], [press(ALL_DOWN)], [press(ALL_UP)],
         f"Turn to dim or brighten every light, {LIGHT_STEP}% a click, more when turned quickly. "
         "Push to turn the lights off or back on", "all")
    strip(page, 1, LINEAR_DISPLAY, "Touch strip: the linear lights level")
    dial(page, 1, "Linear", [press(LIN_RESET)], [press(LIN_DOWN)], [press(LIN_UP)],
         f"Turn to set just the linear lights, {LIGHT_STEP}% a click, more when turned quickly. "
         "Push to put them back to the look", "lin")
    if zone is None:
        strip(page, 2, VOLUME_DISPLAY, "Touch strip: what is playing, and its volume from normal, or Off")
        dial(page, 2, "Volume", [press(VOL_RESET)], [press(VOL_DOWN)], [press(VOL_UP)],
             "Turn for the volume of whatever is playing, 1 dB a click, more when turned quickly: the auditorium "
             "feed, music, Bluetooth or the lobby mix. Push to put it back to normal. Does nothing while the audio "
             "is off or nothing plays", "vol")
    else:
        z, name, mx, db, *_ = zone
        strip(page, 2, zone_display(zone), f"Touch strip: {name} source and level")
        dial(page, 2, name, [when(POWERED, [wing_level(f"/mtx/{mx}", db), setvar(f"z{z}_level", db)])],
             [when(POWERED, [zone_step(z, mx, -1)])], [when(POWERED, [zone_step(z, mx, 1)])],
             f"Turn for {name} volume, 1 dB a click, more when turned quickly. Push to put {name} back to {db} dB. "
             "Does nothing while the audio is off", f"z{z}")
    strip(page, 3, MIC_DISPLAY, "Touch strip: the mic level, Muted, or Off while the audio is off")
    dial(page, 3, "Mics", [press(MIC_MUTE)], [press(MIC_DOWN)], [press(MIC_UP)],
         f"Turn for mic volume, 1 dB a click, more when turned quickly, up to {MIC_MAX} dB. "
         "Push to mute or unmute the mics. Does nothing while the audio is off", "mic")


def ipad_key(page, r, c):
    add(page, r, c, label="iPad Mode", icon="tablet", cat="ipad", labels={"active": "iPad Mode On"},
        does=f"Hold {IPAD_HOLD_MS / 1000:g} second to hand the lights to the iPad, or to take them back",
        hold=(IPAD_HOLD_MS, [press(IPAD_TOGGLE)]), fb=[(IPAD, "active")])


def build_pages():
    # Page 1, home
    lights_off_key(1, 0, 0)
    for n, *_ in LOOKS:
        look_key(1, 0, n, n)
    audio_power_key(1, 1, 0)
    source_key(1, 1, 1, "Auditorium", "Auditorium", "Auditorium", "church")
    source_key(1, 1, 2, "Music Inside", "Playlist", "Music", "note", cat="music")
    nav(1, 1, 3, 2, "More", "more")
    deck_dials(1)
    # Page 2, more
    source_key(2, 0, 0, "Bluetooth", "Bluetooth", "Bluetooth", "bluetooth")
    source_key(2, 0, 1, "Lobby Event", "Lobby Mix", "Lobby Event", "mic")
    scene_key(2, 0, 2, "Music Everywhere", cat="music")
    add(2, 0, 3, label="Playlists", icon="playlist", cat="music", down=[setpage(3)], does="Opens Playlists",
        fb=[(ANY_PLAYLIST, "active")])
    nav(2, 1, 0, ZONES[0][4], "Zones", "sliders", "Opens the first zone page")
    add(2, 1, 1, label="Close Up", icon="closeup", cat="off", hold=(CLOSE_HOLD_MS, [press(CLOSE_UP)]),
        does=f"Hold {CLOSE_HOLD_MS / 1000:g} seconds to turn off the lights and the audio system, and leave iPad Mode",
        fb=[(f"!({LIGHTS_ON}) && {UNPOWERED}", "active")])
    ipad_key(2, 1, 2)
    nav(2, 1, 3, 1, "Home", "home")
    deck_dials(2)
    # Page 3, playlists
    for n, name, icon in PLAYLISTS:
        add(3, 0, n - 1, label=name, icon=icon, cat="music", down=[press(PLAYLIST_LOC[n])],
            does=f"Chooses and plays {name}", fb=[(f"$(custom:music_n) == {n} && ({ANY_PLAYLIST})", "active")])
    scene_key(3, 1, 0, "Music Inside", cat="music")
    scene_key(3, 1, 1, "Music Everywhere", cat="music")
    nav(3, 1, 2, 2, "Back", "back", "Opens More")
    nav(3, 1, 3, 1, "Home", "home")
    deck_dials(3)
    # Pages 4 to 8, zones
    for i, zone in enumerate(ZONES):
        z, name, mx, _, page, icon = zone
        for s, (source, _, label, sicon) in enumerate(SOURCES):
            if source == "Playlist":
                acts = [press(POWER_ON), press(MUSIC_START), wait(50), press(zone_block(z, s))]
            else:
                acts = [press(POWER_ON), press(zone_block(z, s)), wait(200), press(MUSIC_STOP)]
            add(page, 0, s, label=label, icon=sicon, cat="audio", down=acts,
                does=f"{name} plays {source}, turning the audio system on if it is off",
                fb=[(f"$(custom:z{z}_src) == '{source}'", "active")])
        add(page, 1, 0, label=f"{name} Off", icon="mute", cat="off", does=f"Turns off {name}",
            down=[press(zone_block(z, 4)), wait(200), press(MUSIC_STOP)],
            fb=[(f"$(custom:z{z}_src) == 'Off'", "active")])
        prev_z, next_z = ZONES[(i - 1) % 5], ZONES[(i + 1) % 5]
        nav(page, 1, 1, prev_z[4], prev_z[1], "prev", f"Opens {prev_z[1]}")
        nav(page, 1, 2, next_z[4], next_z[1], "next", f"Opens {next_z[1]}")
        nav(page, 1, 3, 1, "Home", "home")
        deck_dials(page, zone)


TRIGGERS = {}


def trigger(tid, name, order, enabled, event, options, actions, condition=None, does=""):
    TRIGGERS[tid] = {
        "does": does,
        "control": {
            "type": "trigger", "options": {"name": name, "enabled": enabled, "sortOrder": order},
            "actions": actions, "condition": [check(condition)] if condition else [],
            "events": [{"id": nid(), "type": event, "enabled": True, "options": options}],
            "localVariables": [],
        },
    }


def build_triggers():
    trigger("startup_recovery", "Startup recovery", 0, True, "startup", {"delay": 5000},
            [press(APPLY_FADE), when(POWERED, [relay(True)], [relay(False)])],
            does="Five seconds after Companion starts, fades the lights back to where they were, and sends the audio "
                 "power state to the relay again so they agree. In iPad Mode, it keeps Companion's light output at zero")
    trigger("schedule_sunday", "Schedule: Sunday arrival", 1, False, "timeofday",
            {"time": "07:30:00", "days": [0]},
            [press(LOOK_LOC[3]), press(SCENE_LOC["Auditorium"])], DECK,
            does="Off at first. Sunday 7:30: Lights 3 and the auditorium feed, unless iPad Mode is on")
    trigger("schedule_weekday", "Schedule: Weekday open", 2, False, "timeofday",
            {"time": "08:00:00", "days": [1, 2, 3, 4, 5]},
            [press(LOOK_LOC[2]), press(SCENE_LOC["Music Inside"])], DECK,
            does="Off at first. Weekdays 8:00: Lights 2 and music inside, unless iPad Mode is on")
    trigger("schedule_night", "Schedule: Night shutdown", 3, False, "timeofday",
            {"time": "22:00:00", "days": [0, 1, 2, 3, 4, 5, 6]},
            [press(CLOSE_UP)],
            does="Off at first. Nightly 22:00: Close Up, which also leaves iPad Mode so doors can't stay locked")


VARIABLES = {  # name: (description, default)
    "light_mode": ("deck, or ipad while the iPad has the lights", "deck"),
    "lt_look": ("Number of the current look", "2"),
    "lt_all": ("All Lights level, 0 to 100. 0 is off", "0"),
    "lt_linear": ("Linear lights level, 0 to 100", "65"),
    "lt_fix": ("Other fixtures level, 0 to 100", "65"),
    **{f"look{n}_{g}": (f"Lights {n} {'linear' if g == 'linear' else 'fixtures'} level, saved by holding its key",
                        str(lin if g == "linear" else fix))
       for n, lin, fix in LOOKS for g in ("linear", "fix")},
    "lt_saved": ("Look just saved, shown on its key for two seconds", "0"),
    "dmx_cmd": ("The DMX channels and values last sent to the ODE", ""),
    **{var: (f"{title.title()} fader in dB, kept in step with the Wing", "0") for _, _, var, title, _ in VOLUME_SOURCES},
    **{f"z{z}_level": (f"{name} fader in dB, kept in step with the Wing", str(db)) for z, name, _, db, *_ in ZONES},
    "mic_level": ("Mic bus fader in dB, kept in step with the Wing", str(MIC_START)),
    "mic_muted": ("1 while the mics are muted", "0"),
    "music_n": ("Number of the chosen playlist", "1"),
    "music_name": ("Name of the chosen playlist", "Morning"),
    **{f"z{z}_src": (f"{name} source, or Off", "Off") for z, name, *_ in ZONES},
    "audio_power": ("1 while the audio system is on, 0 while the amplifiers are off", "0"),
    "turn_fast_ms": (f"Dial clicks closer together than this, in ms, move {TURN_FAST} steps each. 0 turns it off",
                     str(TURN_FAST_MS)),
    "turn_medium_ms": (f"Dial clicks closer together than this, in ms, move {TURN_MEDIUM} steps each. 0 turns it off",
                       str(TURN_MEDIUM_MS)),
    "turn_n": ("Steps for the dial click being handled, worked out from how fast it turned", "1"),
    "turn_ms": ("When a dial last clicked, in ms", "0"),
    "turn_key": ("Which dial last clicked, and which way", ""),
}
PERSIST_OFF = {"lt_saved", "turn_n", "turn_ms", "turn_key"}
WING_VARIABLES = ({f"mtx{mx}_level" for _, _, mx, *_ in ZONES} | {f"bus{MIC_BUS}_level", f"bus{MIC_BUS}_mute"}
                  | {f"{sel.strip('/').replace('/', '')}_level" for _, sel, *_ in VOLUME_SOURCES})


# ---------------------------------------------------------------- artwork
_S = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
def stroke(width):
    return _S.replace('stroke-width="1.8"', f'stroke-width="{width}"')


_BULB = "M9.5 18h5M10.5 21h3M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"
_SPEAKER = "M3.5 9.5v5H7l4.5 4v-13L7 9.5z"


def _rays(cx, cy, r1, r2, count=8):
    out = []
    for i in range(count):
        a = i * 2 * math.pi / count
        out.append(f"M{cx + r1 * math.sin(a):.2f} {cy - r1 * math.cos(a):.2f}"
                   f"L{cx + r2 * math.sin(a):.2f} {cy - r2 * math.cos(a):.2f}")
    return "".join(out)


def _level(n):
    """A bulb that fills and throws more, longer rays as the level rises."""
    glass = ("M12 7.4a5 5 0 0 0-3 9c.6.5.9 1.1.9 1.8h4.2c0-.7.3-1.3.9-1.8a5 5 0 0 0-3-9z")
    bulb = (f'<path d="{glass}" fill="currentColor" fill-opacity="{0.12 + 0.28 * n:.2f}"/>'
            '<path d="M9.9 20.6h4.2M10.7 23h2.6"/>')
    angles = {1: [-45, 0, 45], 2: [-70, -35, 0, 35, 70], 3: [-90, -60, -30, 0, 30, 60, 90]}[n]
    reach = {1: 1.6, 2: 2.3, 3: 3.0}[n]
    rays = ""
    for deg in angles:
        a = math.radians(deg)
        r1, r2 = 6.6, 6.6 + reach
        rays += (f"M{12 + r1 * math.sin(a):.2f} {12.4 - r1 * math.cos(a):.2f}"
                 f"L{12 + r2 * math.sin(a):.2f} {12.4 - r2 * math.cos(a):.2f}")
    return bulb + f'<path d="{rays}"/>'


def _sun_small(cx):
    return f'<circle cx="{cx}" cy="12" r="3"/><path d="{_rays(cx, 12, 5, 7)}"/>'


GLYPHS = {
    "level1": _level(1), "level2": _level(2), "level3": _level(3),
    "bulb": f'<path d="{_BULB}"/>',
    "bulb_off": f'<path d="{_BULB}" stroke-opacity=".75"/><path d="M4 3.5 20 19.5"/>',
    "linear": '<rect x="3" y="5" width="18" height="4" rx="2"/><path d="M6.5 12.5 5 17M12 12.5V18M17.5 12.5 19 17"/>',
    "dimmer": _sun_small(9) + '<path d="M16.5 12h5"/>',
    "brighter": _sun_small(9) + '<path d="M16.5 12h5M19 9.5v5"/>',
    "speaker": f'<path d="{_SPEAKER}M15 9a4 4 0 0 1 0 6M17.5 6.5a7.5 7.5 0 0 1 0 11"/>',
    "mute": f'<path d="{_SPEAKER}M15.5 9.5l5 5M20.5 9.5l-5 5"/>',
    "power": '<path d="M12 3v8.5M6.6 6.2a8 8 0 1 0 10.8 0"/>',
    "quieter": f'<path d="{_SPEAKER}M15.5 12h5"/>',
    "louder": f'<path d="{_SPEAKER}M15.5 12h5M18 9.5v5"/>',
    "note": '<path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    "playlist": '<path d="M3.5 6h11M3.5 11h11M3.5 16h6M19 7v9.5"/><circle cx="16.5" cy="17" r="2.5"/><path d="M19 7l2.5-1"/>',
    "church": '<path d="M12 2v5M10 4h4M12 7l7 5v9H5v-9zM10 21v-5a2 2 0 0 1 4 0v5"/>',
    "bluetooth": '<path d="M7 7l10 10-5 5V2l5 5L7 17"/>',
    "mic": '<rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3M9 21h6"/>',
    "broadcast": '<path d="M12 12v.01M8.5 8.5a5 5 0 0 0 0 7M15.5 8.5a5 5 0 0 1 0 7M5.6 5.6a9 9 0 0 0 0 12.8M18.4 5.6a9 9 0 0 1 0 12.8"/>',
    "home": '<path d="M3 11.5 12 4l9 7.5M5.5 10v10h13V10M10 20v-6h4v6"/>',
    "more": '<circle cx="5.5" cy="12" r="1.7" fill="currentColor"/><circle cx="12" cy="12" r="1.7" fill="currentColor"/>'
            '<circle cx="18.5" cy="12" r="1.7" fill="currentColor"/>',
    "back": '<path d="M10 6l-6 6 6 6M4 12h16"/>',
    "prev": '<path d="M15 5l-7 7 7 7"/>',
    "next": '<path d="M9 5l7 7-7 7"/>',
    "sliders": '<path d="M6 4v6M6 14v6M12 4v2M12 10v10M18 4v10M18 18v2M3.5 12h5M9.5 8h5M15.5 16h5"/>',
    "tablet": '<rect x="5" y="2.5" width="14" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "closeup": '<path d="M13 21V3H4v18M2 21h13M10 12v.01M16 12h6M19 9l3 3-3 3"/>',
    "sunrise": '<path d="M3 19h18M7 19a5 5 0 0 1 10 0M12 6v3M5 11.5l2 2M19 11.5l-2 2M12 3.5l-2 2M12 3.5l2 2"/>',
    "sunset": '<path d="M3 19h18M7 19a5 5 0 0 1 10 0M12 3v6M9 6.5 12 9.5 15 6.5M5 12.5l2 2M19 12.5l-2 2"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h2M14 14h2"/>',
    "star": '<path d="M12 3l2.7 5.9 6.3.8-4.6 4.4 1.2 6.4L12 17l-5.6 3.5 1.2-6.4L3 9.7l6.3-.8z"/>',
    "tree": '<path d="M12 3l5.5 7H15l4 6H5l4-6H6.5zM12 16v5"/>',
    "soffit": '<path d="M2 12 12 4l10 8M5 14.5h14M9 14.5v2a3 3 0 0 0 6 0v-2"/>',
    "restroom": '<circle cx="7" cy="5" r="2"/><path d="M7 8.5v6.5M4.5 11h5M7 15l-2 6M7 15l2 6M12 3v18"/>'
                '<circle cx="17" cy="5" r="2"/><path d="M17 8.5 14 16h6zM15.5 16v5M18.5 16v5"/>',
    "door": '<path d="M6 21V3h12v18M3 21h18M14.5 12v.01"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M7.5 12.5l3 3 6-6.5"/>',
}

SVG = 'xmlns="http://www.w3.org/2000/svg"'


def tile_svg(icon, cat, state):
    """A key's artwork: a lit or resting tile with a large icon. The label is live text drawn on top."""
    glow = state in ("active", "saved", "on")
    if state == "locked":
        top, bottom, glyph = LOCKED_ART
    elif state == "on":  # a lit power key, green whatever the key's own color
        p = PALETTE["power"]
        top, bottom, glyph = p[3], p[4], "#ffffff"
    elif state == "saved":
        p = PALETTE["save"]
        top, bottom, glyph, icon = p[3], p[4], "#ffffff", "check"
    elif state == "active":
        p = PALETTE[cat]
        top, bottom, glyph = p[3], p[4], "#ffffff"
    else:
        p = PALETTE[cat]
        top, bottom, glyph = p[0], p[1], p[2]
    parts = [
        f'<svg {SVG} width="144" height="144" viewBox="0 0 144 144"><defs>',
        f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
        f'<stop offset="1" stop-color="{bottom}"/></linearGradient>',
        '<radialGradient id="glow" cx=".5" cy=".3" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".38"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>',
        '<rect width="144" height="144" fill="url(#g)"/>',
        '<ellipse cx="72" cy="42" rx="62" ry="44" fill="url(#glow)"/>' if glow else "",
        f'<g transform="translate(36,5) scale(3)" color="{glyph}" {stroke(1.9)}>{GLYPHS[icon]}</g>',
    ]
    if state == "locked":
        parts.append(f'<g transform="translate(106,5) scale(1.35)" color="#8a939e" {stroke(2.2)}>'
                     f'{GLYPHS["lock"]}</g>')
    parts.append("</svg>")
    return "".join(parts)


STRIP_ICONS = {"light": "bulb", "linear": "linear", "audio": "speaker", "mic": "mic"}


def strip_svg(cat, icon):
    color = accent(cat)
    return (f'<svg {SVG} width="200" height="100" viewBox="0 0 200 100"><defs>'
            f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{color}" stop-opacity=".22"/>'
            f'<stop offset=".7" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            '<rect width="200" height="100" fill="#0b0d10"/><rect width="200" height="100" fill="url(#g)"/>'
            '<path d="M199.5 8v84" stroke="#fff" stroke-opacity=".08"/>'
            f'<g transform="translate(9,10) scale(1.3)" color="{color}" {_S}>{GLYPHS[icon]}</g></svg>')


def art_key(k):
    """The artwork names a key needs, with their SVG source and size."""
    out = {}
    if k.kind == "key":
        states = ["rest"] + [s for _, s in k.fb]
        for s in states:
            out[f"tile-{k.cat}-{k.icon}-{s}"] = (tile_svg(k.icon, k.cat, s), 144, 144)
    elif k.kind == "strip":
        icon = STRIP_ICONS.get(k.cat) or k.cat.split("-", 1)[1]
        cat = k.cat if k.cat in PALETTE else "audio"
        out[f"strip-{k.cat}"] = (strip_svg(cat, icon), 200, 100)
    return out


def browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/usr/bin/google-chrome", "/usr/bin/chromium"):
        if os.path.exists(p):
            return p
    sys.exit("Chrome or Edge is needed to draw the artwork.")


def chrome(profile, *args):
    return subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-first-run",
                           "--hide-scrollbars", f"--user-data-dir={profile}", *args],
                          capture_output=True, text=True, timeout=180)


def render_art(profile, tmp):
    sources = {}
    for k in KEYS.values():
        sources.update(art_key(k))
    for f in list(ICONS.glob("*.png")) + list(ICONS.glob("*.svg")):
        f.unlink()
    ICONS.mkdir(exist_ok=True)
    for name, (svg, _, _) in sources.items():
        (ICONS / f"{name}.svg").write_text(svg + "\n", encoding="utf-8")
    page = tmp / "render.html"
    page.write_text("""<!doctype html><pre id="out"></pre><script>
const items=%s;
const load=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);
  i.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(s)))});
const png=c=>c.toDataURL('image/png').split(',')[1];
const thumb=(src,w,h)=>{const c=document.createElement('canvas');c.width=64;c.height=Math.round(64*h/w);
  const x=c.getContext('2d');x.imageSmoothingQuality='high';x.drawImage(src,0,0,c.width,c.height);return png(c)};
(async()=>{const out={};
for(const [n,[s,w,h]] of Object.entries(items)){const c=document.createElement('canvas');c.width=w;c.height=h;
  c.getContext('2d').drawImage(await load(s),0,0,w,h);out[n]=png(c);out[n+'@preview']=thumb(c,w,h)}
document.getElementById('out').textContent=JSON.stringify(out)})();
</script>""" % json.dumps(sources), encoding="utf-8")
    result = chrome(profile, "--virtual-time-budget=20000", "--dump-dom", page.as_uri())
    match = re.search(r'<pre id="out">(.*?)</pre>', result.stdout, re.S)
    if not match or not match.group(1):
        sys.exit("Artwork rendering failed:\n" + result.stderr[-600:])
    images = json.loads(match.group(1))
    for name, data in images.items():
        if name.endswith("@preview"):
            PREVIEWS[name[:-8]] = "data:image/png;base64," + data
        else:
            (ICONS / f"{name}.png").write_bytes(base64.b64decode(data))
    return {name: "data:image/png;base64," + data for name, data in images.items() if not name.endswith("@preview")}


# ---------------------------------------------------------------- layered buttons
def el_base(eid, name, etype, x, y, w, h, enabled=True, rotation=True):
    e = {"id": eid, "name": name, "usage": "auto", "type": etype, "pinnedProperties": [],
         "enabled": enabled if is_wrapped(enabled) else val(enabled), "opacity": val(100),
         "x": val(x), "y": val(y), "width": w if is_wrapped(w) else val(w), "height": val(h)}
    if rotation:
        e["rotation"] = val(0)
    return e


def P(v):
    return v if is_wrapped(v) else val(v)


def el_canvas(decoration):
    return {"id": "canvas", "name": "Canvas", "usage": "auto", "type": "canvas",
            "decoration": val(decoration), "showStatusIcons": val("none")}


def el_box(eid, name, x, y, w, h, color, radius=0, enabled=True, opacity=100):
    e = el_base(eid, name, "box", x, y, w, h, enabled)
    e["opacity"] = val(opacity)
    e["pinnedProperties"] = ["color"]
    e.update(color=P(color), cornerRadius=val(radius), borderWidth=val(0), borderColor=val(0),
             borderPosition=val("inside"))
    return e


def el_image(eid, name, x, y, w, h, data, fill="fill"):
    e = el_base(eid, name, "image", x, y, w, h)
    e["pinnedProperties"] = ["base64Image", "halign", "valign"]
    e.update(base64Image=P(data), halign=val("center"), valign=val("center"), fillMode=val(fill))
    return e


def el_text(eid, name, x, y, w, h, text, size, color, halign="center", valign="center", bold=False,
            outline=0xFF000000, enabled=True):
    e = el_base(eid, name, "text", x, y, w, h, enabled)
    e["pinnedProperties"] = ["text", "fontsize", "fontsizeAllowShrink", "color", "halign", "valign"]
    e.update(text=P(text), fontsize=val(size), fontsizeAllowShrink=val(True), font=val("companion-sans"),
             weight=val("bold" if bold else "normal"), styles=val([]), color=P(color),
             outlineColor=val(outline), halign=val(halign), valign=val(valign))
    return e


LIBRARY: dict[str, str] = {}  # image library name: PNG data URL, stored once and shared by every button
PREVIEWS: dict[str, str] = {}  # artwork name: 64-pixel thumbnail, for Companion's image library list
LIBRARY_SOURCE: dict[str, str] = {}  # image library name: artwork name


def img(images, name):
    """A reference to an image in Companion's image library, which the import file carries once."""
    lib_name = name.replace("-", "_")
    LIBRARY[lib_name] = images[name]
    LIBRARY_SOURCE[lib_name] = name
    return f"$(image:{lib_name})"


def around(program, template):
    """Wrap the last statement of a possibly multi-statement expression, eg the bar width around a level."""
    head, sep, last = program.rpartition("\n")
    return head + sep + template.replace("{}", f"({last})")


def label_size(text):
    return 44 if "\n" in text else 56


def style_feedback(expression, overrides):
    f = check(expression)
    f["isInverted"] = val(False)
    f["styleOverrides"] = [{"overrideId": nid("o"), "elementId": e, "elementProperty": p, "override": P(v)}
                           for e, p, v in overrides]
    return f


def layers_for(k, images):
    """The button's elements and its style feedbacks."""
    if k.kind in ("lib", "dial"):
        bg = "#13171c" if k.kind == "lib" else "#0b0d10"
        text = k.label if k.kind == "lib" else f"◀ {k.label} ▶"
        return [el_canvas("border"), el_box("bg", "Background", 0, 0, 100, 100, bg),
                el_text("label", "Label", 4, 4, 92, 92, text, 30, 0xC9D1DB, bold=k.kind == "dial")], []
    if k.kind == "strip":
        s = k.show
        title = expr(s["title"]) if s.get("title_expr") else s["title"]
        pct = s["pct"]
        title_color = accent(k.cat if k.cat in PALETTE else "audio")
        if s.get("dim"):  # a panel that greys out while its dial does nothing
            title_color = expr(f"{s['dim']} ? '{DIM}' : '{title_color}'")
        panel = el_image("art", "Panel", 0, 0, 100, 100, img(images, f"strip-{k.cat}"))
        if s.get("dim"):
            panel["opacity"] = expr(f"{s['dim']} ? 35 : 100")
        layers = [
            el_canvas("none"),
            panel,
            el_text("title", "Title", 25, 6, 72 if not s.get("badge") else 46, 26, title, 82,
                    title_color, halign="left", bold=True),
            el_text("value", "Value", 25, 31, 72, 40, expr(s["value"]), 100, expr(s["value_color"]),
                    halign="left", bold=True),
            el_box("track", "Track", 6, 79, 88, 9, TRACK, radius=100),
            el_box("fill", "Level", 6, 79, expr(around(pct, "88 * {} / 100")), 9, expr(s["color"]), radius=100,
                   enabled=expr(around(pct, "{} > 0"))),
        ]
        if s.get("tick") is not None:
            layers.append(el_box("tick", "Normal", 6 + 88 * s["tick"] / 100 - 0.6, 75, 1.2, 17, "#ffffff", opacity=60))
        if s.get("badge"):
            layers.append(el_text("badge", "No Wing", 70, 6, 27, 26, "NO WING", 70, BADGE, halign="right", bold=True,
                                  enabled=expr(s["badge"])))
        return layers, []
    # A normal key: tile artwork with a live label
    rest = img(images, f"tile-{k.cat}-{k.icon}-rest")
    layers = [
        el_canvas("border"),
        el_box("bg", "Background", 0, 0, 100, 100, PALETTE[k.cat][1]),
        el_image("art", "Artwork", 0, 0, 100, 100, rest),
        el_text("label", "Label", 3, 63, 94, 34, k.label, label_size(k.label), TEXT_REST, bold=True,
                outline=LABEL_OUTLINE),
    ]
    feedbacks = []
    for expression, state in k.fb:
        overrides = [("art", "base64Image", img(images, f"tile-{k.cat}-{k.icon}-{state}")),
                     ("label", "color", TEXT_DIM if state == "locked" else TEXT_ACTIVE)]
        if state in k.labels:
            overrides.append(("label", "text", k.labels[state]))
        feedbacks.append(style_feedback(expression, overrides))
    return layers, feedbacks


def control(k, images):
    layers, feedbacks = layers_for(k, images)
    sets = {"down": k.down, "up": k.up}
    options = {"runWhileHeld": []}
    if k.hold:
        sets[str(k.hold[0])] = k.hold[1]
        options["runWhileHeld"] = [k.hold[0]]
    rotary = k.left is not None
    if rotary:
        sets["rotate_left"], sets["rotate_right"] = k.left, k.right
    return {"type": "button-layered",
            "options": {"stepProgression": "auto", "rotaryActions": rotary, "canModifyStyleInApis": False,
                        "notes": k.does},
            "style": {"layers": layers}, "feedbacks": feedbacks,
            "steps": {"0": {"action_sets": sets, "options": options}}, "localVariables": []}


DECK_PAGES = [p for p, (_, kind) in PAGES.items() if kind == "deck"]
SURFACE_GROUPS = {  # group id: (name, startup page, pages it may use). One group per deck, so each keeps its own page.
    # Every station starts with every page. Narrow a door's pages in Companion to lock it out of them
    "group:rack": ("Rack", 1, DECK_PAGES),
    **{f"group:door{n}": (f"Door {n}", 1, DECK_PAGES) for n in (1, 2, 3)},
}


def surface_groups():
    return {gid: {"name": name, "use_last_page": False, "startup_page": start, "last_page": start,
                  "never_lock": False, "restrict_pages": True, "allowed_pages": pages}
            for gid, (name, start, pages) in SURFACE_GROUPS.items()}


LIBRARY_TIME = 1794787200000  # 2026-11-15, fixed so rebuilds only change what really changed


def image_library():
    out = []
    for i, (name, data) in enumerate(sorted(LIBRARY.items())):
        preview_image = PREVIEWS[LIBRARY_SOURCE[name]]
        size = len(base64.b64decode(data.split(",", 1)[1]))
        out.append({"info": {"name": name, "description": "Built by build.py", "originalSize": size,
                             "previewSize": len(base64.b64decode(preview_image.split(",", 1)[1])),
                             "createdAt": LIBRARY_TIME, "modifiedAt": LIBRARY_TIME,
                             "checksum": hashlib.sha1(data.encode()).hexdigest(), "mimeType": "image/png",
                             "sortOrder": i},
                    "originalImage": data, "previewImage": preview_image})
    return out


def export():
    pages = {}
    for number, (name, _) in PAGES.items():
        controls = {}
        for key in KEYS.values():
            if key.page == number:
                controls.setdefault(str(key.row), {})[str(key.col)] = CONTROLS[key.loc]
        pages[str(number)] = {"name": name, "controls": controls,
                              "gridSize": {"minColumn": 0, "maxColumn": 7, "minRow": 0, "maxRow": 3}}
    return {
        "version": 12, "type": "full", "companionBuild": "suncrest-build-script",
        "pages": pages,
        "triggers": {k: v["control"] for k, v in TRIGGERS.items()}, "triggerCollections": [],
        "custom_variables": {name: {"description": d, "defaultValue": v, "persistCurrentValue": name not in PERSIST_OFF,
                                    "sortOrder": i} for i, (name, (d, v)) in enumerate(VARIABLES.items())},
        "customVariablesCollections": [], "connectionCollections": [],
        "imageLibrary": image_library(), "imageLibraryCollections": [],
        # Surfaces: no decks (they are matched by serial number when plugged in), but the groups they join,
        # and the Elgato integration, so a full reset still leaves USB Stream Decks working
        "surfaces": {}, "surfaceGroups": surface_groups(), "surfacesRemote": {},
        "surfaceInstances": {"elgato": {"label": "elgato", "moduleId": "elgato-stream-deck", "enabled": True,
                                        "isFirstInit": False, "lastUpgradeIndex": -1, "updatePolicy": "stable",
                                        "sortOrder": 0}},
        "surfaceInstanceCollections": [],
        "instances": {
            "wing": {"label": "wing", "moduleId": "behringer-wing", "enabled": True, "isFirstInit": False,
                     "lastUpgradeIndex": 1, "sortOrder": 0, "updatePolicy": "stable",
                     "config": {"host": WING_IP, "model": "rack", "fadeUpdateRate": 50,
                                "statusPollUpdateRate": 3000, "variableUpdateRate": 100,
                                "prefetchVariablesOnStartup": True, "show-advanced-options": False,
                                "requestTimeout": 200, "panicOnLostRequest": False,
                                "startupVariableRequestChunkSize": 500, "startupVariableRequestChunkWait": 100,
                                "subscriptionInterval": 9000, "enableOscForwarding": False,
                                "oscForwardingHost": "", "oscForwardingPort": 2223}},
            "dmx": {"label": "dmx", "moduleId": "generic-artnet", "enabled": True, "isFirstInit": False,
                    "lastUpgradeIndex": ARTNET_UPGRADE, "sortOrder": 1, "updatePolicy": "stable",
                    "config": {"host": ODE_IP, "universe": ARTNET_UNIVERSE, "timer_slow": 1000, "timer_fast": 40}},
            "wiim": {"label": "wiim", "moduleId": "generic-http", "enabled": True, "isFirstInit": False,
                     "lastUpgradeIndex": 3, "sortOrder": 2, "updatePolicy": "stable",
                     "config": {"prefix": f"https://{WIIM_IP}/", "proxyAddress": "", "authType": "none",
                                "authUser": "", "authPassword": "", "rejectUnauthorized": False,
                                "insecureHTTPParser": False}},
            "power": {"label": "power", "moduleId": "generic-http", "enabled": True, "isFirstInit": False,
                      "lastUpgradeIndex": 3, "sortOrder": 3, "updatePolicy": "stable",
                      "config": {"prefix": f"http://{POWER_IP}/", "proxyAddress": "", "authType": "none",
                                 "authUser": "", "authPassword": "", "rejectUnauthorized": True,
                                 "insecureHTTPParser": False}},
        },
    }


# ---------------------------------------------------------------- expression evaluator
class ExprError(Exception):
    pass


_TOKEN = re.compile(r"""
    (?P<ws>[ \t\r]+)|(?P<nl>\n)|(?P<comment>//[^\n]*)|
    (?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)|
    (?P<var>\$\([a-z_]+:[A-Za-z0-9_]+\))|
    (?P<str>'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|
    (?P<id>[A-Za-z_]\w*)|
    (?P<op>===|!==|==|!=|<=|>=|&&|\|\||\?\?|\*\*|[-+*/%<>!?:(),;=\[\]])""", re.X)


def _template_end(src, i):
    """Index of the closing backtick of a template that opens at src[i]."""
    j = i + 1
    while j < len(src):
        ch = src[j]
        if ch == "\\":
            j += 2
            continue
        if ch == "`":
            return j
        if src.startswith("${", j):
            depth, j = 1, j + 2
            while depth and j < len(src):
                if src[j] == "`":
                    j = _template_end(src, j) + 1
                    continue
                if src[j] in "'\"":
                    q, j = src[j], j + 1
                    while src[j] != q:
                        j += 2 if src[j] == "\\" else 1
                depth += {"{": 1, "}": -1}.get(src[j], 0)
                j += 1
            continue
        j += 1
    raise ExprError("unclosed template")


def _template_parts(body):
    parts, j, text = [], 0, ""
    while j < len(body):
        if body.startswith("${", j):
            depth, k = 1, j + 2
            while depth:
                if body[k] == "`":
                    k = _template_end(body, k) + 1
                    continue
                depth += {"{": 1, "}": -1}.get(body[k], 0)
                k += 1
            parts += [text, ("expr", body[j + 2:k - 1])]
            text, j = "", k
        else:
            text += body[j]
            j += 1
    return parts + [text]


def tokenize(src):
    out, i = [], 0
    while i < len(src):
        if src[i] == "`":
            end = _template_end(src, i)
            out.append(("tpl", _template_parts(src[i + 1:end])))
            i = end + 1
            continue
        m = _TOKEN.match(src, i)
        if not m:
            raise ExprError(f"bad character {src[i]!r} in {src!r}")
        kind = m.lastgroup
        if kind not in ("ws", "comment"):
            out.append((kind, m.group()))
        i = m.end()
    return out


BIN = {"||": 3, "??": 3, "&&": 4, "==": 7, "!=": 7, "===": 7, "!==": 7, "<": 8, ">": 8, "<=": 8, ">=": 8,
       "+": 10, "-": 10, "*": 11, "/": 11, "%": 11, "**": 12}


class Parser:
    def __init__(self, tokens):
        self.t, self.i = tokens, 0

    def peek(self, offset=0):
        j = self.i + offset
        return self.t[j] if j < len(self.t) else (None, None)

    def take(self, value=None):
        tok = self.peek()
        if value is not None and tok[1] != value:
            raise ExprError(f"expected {value}, got {tok[1]}")
        self.i += 1
        return tok

    def program(self):
        statements = []
        while self.peek()[0] is not None:
            if self.peek()[0] == "nl" or self.peek()[1] == ";":
                self.i += 1
                continue
            if self.peek()[0] == "id" and self.peek(1)[1] == "=":
                name = self.take()[1]
                self.take("=")
                statements.append(("assign", name, self.expression()))
            else:
                statements.append(("expr", self.expression()))
            if self.peek()[0] not in (None, "nl") and self.peek()[1] != ";":
                raise ExprError(f"unexpected {self.peek()[1]}")
        if not statements:
            raise ExprError("empty expression")
        return statements

    def expression(self):
        cond = self.binary(0)
        if self.peek()[1] == "?":
            self.take("?")
            a = self.expression()
            self.take(":")
            return ("?", cond, a, self.expression())
        return cond

    def binary(self, level):
        left = self.unary()
        while True:
            op = self.peek()[1] if self.peek()[0] == "op" else None
            if op not in BIN or BIN[op] <= level:
                return left
            self.take()
            right = self.binary(BIN[op] - (1 if op == "**" else 0))
            left = ("bin", op, left, right)

    def unary(self):
        if self.peek()[0] == "op" and self.peek()[1] in ("!", "-", "+"):
            return ("un", self.take()[1], self.unary())
        return self.postfix()

    def postfix(self):
        node = self.primary()
        while self.peek()[1] in ("(", "["):
            if self.take()[1] == "(":
                args = []
                while self.peek()[1] != ")":
                    args.append(self.expression())
                    if self.peek()[1] == ",":
                        self.take()
                self.take(")")
                node = ("call", node, args)
            else:
                index = self.expression()
                self.take("]")
                node = ("index", node, index)
        return node

    def primary(self):
        kind, v = self.take()
        if kind == "num":
            return ("lit", float(v))
        if kind == "str":
            return ("lit", re.sub(r"\\(.)", r"\1", v[1:-1]))
        if kind == "tpl":
            return ("tpl", [p if isinstance(p, str) else Parser(tokenize(p[1])).expression() for p in v])
        if kind == "var":
            conn, name = v[2:-1].split(":")
            return ("var", conn, name)
        if kind == "id":
            return {"true": ("lit", True), "false": ("lit", False), "null": ("lit", None),
                    "undefined": ("lit", None), "PI": ("lit", math.pi)}.get(v, ("name", v))
        if v == "(":
            node = self.expression()
            self.take(")")
            return node
        if v == "[":
            items = []
            while self.peek()[1] != "]":
                items.append(self.expression())
                if self.peek()[1] == ",":
                    self.take()
            self.take("]")
            return ("list", items)
        raise ExprError(f"unexpected {v!r}")


def to_num(v):
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return 0.0
        try:
            return float(s)
        except ValueError:
            return math.nan
    return math.nan


def truthy(v):
    if v is None or v is False or v == "":
        return False
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v != 0 and not math.isnan(v)
    return True


def js_str(v):
    if v is None:
        return "undefined"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        if math.isnan(v):
            return "NaN"
        return str(int(v)) if v == int(v) else repr(v)
    return str(v)


def loose_eq(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    return to_num(a) == to_num(b)


FUNCS = {
    "round": lambda x: math.floor(to_num(x) + 0.5),
    "floor": lambda x: math.floor(to_num(x)), "ceil": lambda x: math.ceil(to_num(x)),
    "abs": lambda x: abs(to_num(x)),
    "min": lambda *a: min(to_num(x) for x in a), "max": lambda *a: max(to_num(x) for x in a),
    "isNumber": lambda x: not math.isnan(to_num(x)) and not (isinstance(x, str) and x.strip() == ""),
    "toFixed": lambda x, dp: f"{to_num(x):.{int(to_num(dp))}f}",
    "unixNow": None,  # the clock: the simulator supplies it through its variable lookup
}


def evaluate(node, get, temps):
    kind = node[0]
    if kind == "lit":
        return node[1]
    if kind == "var":
        return get(node[1], node[2])
    if kind == "name":
        if node[1] not in temps:
            raise ExprError(f"unknown name {node[1]}")
        return temps[node[1]]
    if kind == "tpl":
        return "".join(p if isinstance(p, str) else js_str(evaluate(p, get, temps)) for p in node[1])
    if kind == "list":
        return [evaluate(x, get, temps) for x in node[1]]
    if kind == "index":
        seq, i = evaluate(node[1], get, temps), evaluate(node[2], get, temps)
        try:
            return seq[int(to_num(i))]
        except (IndexError, TypeError, ValueError):
            return None
    if kind == "?":
        return evaluate(node[2] if truthy(evaluate(node[1], get, temps)) else node[3], get, temps)
    if kind == "un":
        v = evaluate(node[2], get, temps)
        return {"!": lambda: not truthy(v), "-": lambda: -to_num(v), "+": lambda: to_num(v)}[node[1]]()
    if kind == "call":
        if node[1][0] != "name" or node[1][1] not in FUNCS:
            raise ExprError(f"unknown function {node[1]}")
        if node[1][1] == "unixNow":
            return to_num(get("clock", "now"))
        return FUNCS[node[1][1]](*[evaluate(a, get, temps) for a in node[2]])
    if kind == "bin":
        op = node[1]
        a = evaluate(node[2], get, temps)
        if op == "&&":
            return evaluate(node[3], get, temps) if truthy(a) else a
        if op == "||":
            return a if truthy(a) else evaluate(node[3], get, temps)
        if op == "??":
            return a if a is not None else evaluate(node[3], get, temps)
        b = evaluate(node[3], get, temps)
        if op in ("==", "!="):
            return loose_eq(a, b) == (op == "==")
        if op in ("===", "!=="):
            return (type(a) is type(b) and a == b) == (op == "===")
        x, y = to_num(a), to_num(b)
        if op in ("<", ">", "<=", ">="):
            return {"<": x < y, ">": x > y, "<=": x <= y, ">=": x >= y}[op]
        if op == "/":
            return x / y if y else (math.nan if x == 0 or math.isnan(x) else math.copysign(math.inf, x))
        if op == "%":
            return math.fmod(x, y) if y else math.nan
        return {"+": lambda: x + y, "-": lambda: x - y, "*": lambda: x * y, "**": lambda: x ** y}[op]()
    raise ExprError(f"cannot evaluate {kind}")


def run_expression(src, get):
    temps, result = {}, None
    for statement in Parser(tokenize(src)).program():
        if statement[0] == "assign":
            temps[statement[1]] = evaluate(statement[2], get, temps)
        else:
            result = evaluate(statement[1], get, temps)
    return result


# ---------------------------------------------------------------- checks
ALLOWED = {  # (connection, definition): option names, taken from the module and Companion source
    ("internal", "button_pressrelease"): {"location", "force", "duration"},
    ("internal", "custom_variable_set_value"): {"name", "create", "value"},
    ("internal", "custom_variable_sync_to_default"): {"name"},
    ("internal", "set_page"): {"surfaceId", "page"},
    ("internal", "wait"): {"time"},
    ("internal", "logic_if"): set(),
    ("internal", "check_expression"): {"expression"},
    ("wing", "set-send-mute"): {"src", "dest", "mainDest", "mute"},
    ("wing", "set-mute"): {"sel", "mute"},
    ("wing", "set-fader"): {"sel", "level", *FADE},
    ("wing", "fader-delta"): {"sel", "delta", *FADE},
    ("dmx", "set_complex"): {"params", "duration"},
    ("wiim", "get"): {"url", "header", "jsonResultDataVariable", "result_stringify", "statusCodeVariable"},
    ("power", "get"): {"url", "header", "jsonResultDataVariable", "result_stringify", "statusCodeVariable"},
}
ELEMENT_PROPS = {  # from Companion 5.1.3 StyleLayersModel
    "canvas": {"decoration", "showStatusIcons"},
    "box": {"enabled", "opacity", "x", "y", "width", "height", "rotation", "color", "cornerRadius",
            "borderWidth", "borderColor", "borderPosition"},
    "image": {"enabled", "opacity", "x", "y", "width", "height", "rotation", "base64Image", "halign",
              "valign", "fillMode"},
    "text": {"enabled", "opacity", "x", "y", "width", "height", "rotation", "text", "fontsize",
             "fontsizeAllowShrink", "font", "weight", "styles", "color", "outlineColor", "halign", "valign"},
    "circle": {"enabled", "opacity", "x", "y", "width", "height", "color", "startAngle", "endAngle",
               "drawSlice", "borderOnlyArc", "borderWidth", "borderColor", "borderPosition"},
}
META = {"id", "name", "usage", "type", "pinnedProperties"}


def walk(entities):
    for e in entities:
        yield e
        for group in e.get("children", {}).values():
            yield from walk(group)


def all_entity_lists():
    for k in KEYS.values():
        for extra in (k.down, k.up, [check(x) for x, _ in k.fb], k.left, k.right, k.hold[1] if k.hold else None):
            if extra:
                yield k.loc, extra
    for tid, t in TRIGGERS.items():
        yield tid, t["control"]["actions"]
        yield tid, t["control"]["condition"]


def check_refs(where, text, errors):
    for conn, name in re.findall(r"\$\(([a-z]+):(\w+)\)", str(text)):
        if conn == "custom" and name not in VARIABLES:
            errors.append(f"{where}: unknown variable {name}")
        elif conn == "wing" and name not in WING_VARIABLES:
            errors.append(f"{where}: unexpected Wing variable {name}")
        elif conn == "image" and name not in LIBRARY:
            errors.append(f"{where}: missing library image {name}")
        elif conn == "this" and name != "delta":
            errors.append(f"{where}: unexpected variable this:{name}")
        elif conn not in ("custom", "wing", "image", "this"):
            errors.append(f"{where}: unexpected variable {conn}:{name}")


def check_expression_text(where, src, errors):
    try:
        Parser(tokenize(src)).program()
    except (ExprError, IndexError) as e:
        errors.append(f"{where}: expression does not parse: {e}: {src!r}")
    check_refs(where, src, errors)


def validate(controls):
    errors, ids = [], set()
    for k in KEYS.values():
        rows, cols = BOUNDS[PAGES[k.page][1]]
        if k.row >= rows or k.col >= cols:
            errors.append(f"{k.loc} is outside its surface")
        if PAGES[k.page][1] == "deck" and k.row == 2 and k.kind != "strip":
            errors.append(f"{k.loc}: only touch strip displays belong on row 2")
        if k.left is not None and k.row != 3:
            errors.append(f"{k.loc}: dials live on row 3")
        if k.up and not k.hold:
            errors.append(f"{k.loc}: release actions are only for keys that also hold")
    for where, entities in all_entity_lists():
        for e in walk(entities):
            spec = (e["connectionId"], e["definitionId"])
            if spec not in ALLOWED:
                errors.append(f"{where}: unknown {spec}")
                continue
            if set(e["options"]) - ALLOWED[spec]:
                errors.append(f"{where}: bad options on {spec}")
            if e["id"] in ids and e["definitionId"] != "check_expression":
                errors.append(f"{where}: repeated id {e['id']}")
            ids.add(e["id"])
            for name, option in e["options"].items():
                if not is_wrapped(option):
                    errors.append(f"{where}: unwrapped option {name} on {spec}")
                    continue
                if option["isExpression"]:
                    check_expression_text(where, option["value"], errors)
                else:
                    check_refs(where, option["value"], errors)
            o = {k: v["value"] for k, v in e["options"].items()}
            if e["definitionId"] == "button_pressrelease" and o["location"] not in KEYS:
                errors.append(f"{where}: press target {o['location']} is missing")
            if e["definitionId"] == "set_page" and o["page"] not in PAGES:
                errors.append(f"{where}: page {o['page']} is missing")
            if e["definitionId"].startswith("custom_variable_") and o["name"] not in VARIABLES:
                errors.append(f"{where}: sets unknown variable {o['name']}")
    for loc, c in controls.items():
        layers = c["style"]["layers"]
        if layers[0]["type"] != "canvas":
            errors.append(f"{loc}: the canvas must be the first layer")
        element_ids = set()
        for el in layers:
            props = set(el) - META
            if props != ELEMENT_PROPS[el["type"]]:
                errors.append(f"{loc}: {el['type']} element {el['id']} has {sorted(props ^ ELEMENT_PROPS[el['type']])}")
            element_ids.add(el["id"])
            for name in props:
                if not is_wrapped(el[name]):
                    errors.append(f"{loc}: {el['id']}.{name} is not wrapped")
                elif el[name]["isExpression"]:
                    check_expression_text(f"{loc} {el['id']}.{name}", el[name]["value"], errors)
                else:
                    check_refs(f"{loc} {el['id']}.{name}", el[name]["value"], errors)
        for f in c["feedbacks"]:
            check_expression_text(f"{loc} feedback", f["options"]["expression"]["value"], errors)
            for o in f["styleOverrides"]:
                if o["elementId"] not in element_ids:
                    errors.append(f"{loc}: override for missing element {o['elementId']}")
                else:
                    el = next(x for x in layers if x["id"] == o["elementId"])
                    if o["elementProperty"] not in ELEMENT_PROPS[el["type"]]:
                        errors.append(f"{loc}: override of unknown property {o['elementProperty']}")
    return errors


class Sim:
    """Walks the actions the way Companion would, and records what reaches the hardware."""

    def __init__(self, connected=True):
        """connected=False is a desk test with no Wing: its actions go nowhere and its variables are empty."""
        self.vars = {n: v for n, (_, v) in VARIABLES.items()}
        self.connected = connected
        self.wing = {f"mtx{mx}_level": float(db) for _, _, mx, db, *_ in ZONES} if connected else {}
        if connected:
            self.wing.update({f"bus{MIC_BUS}_level": float(MIC_START), f"bus{MIC_BUS}_mute": 0})
            self.wing.update({f"{sel.strip('/').replace('/', '')}_level": 0.0 for _, sel, *_ in VOLUME_SOURCES})
        self.sends, self.mutes, self.log, self.page = {}, {}, [], 1
        self.dmx = [0] * 512
        self.kept = {}
        self.clock, self.this = 1_000_000, {}

    def get(self, conn, name):
        if conn == "image":
            return LIBRARY.get(name)
        if conn == "clock":
            return self.clock
        if conn == "this":
            return self.this.get(name)
        return self.vars.get(name) if conn == "custom" else self.wing.get(name)

    def eval(self, src):
        return run_expression(src, self.get)

    def text(self, s):
        return re.sub(r"\$\(([a-z]+):(\w+)\)", lambda m: js_str(self.get(m.group(1), m.group(2))), str(s))

    def option(self, option):
        return self.eval(option["value"]) if option["isExpression"] else option["value"]

    def level_name(self, sel):
        kind, n = sel.strip("/").split("/")
        return f"{kind}{n}_level"

    def run(self, actions):
        for a in actions:
            o = {k: self.option(v) for k, v in a["options"].items()} if a["definitionId"] != "logic_if" else {}
            d = a["definitionId"]
            if d == "button_pressrelease":
                key = KEYS[o["location"]]
                self.run(key.down)
                self.run(key.up)
            elif d == "logic_if":
                chosen = all(truthy(self.eval(c["options"]["expression"]["value"])) for c in a["children"]["condition"])
                self.run(a["children"]["actions" if chosen else "else_actions"])
            elif d == "custom_variable_set_value":
                v = a["options"]["value"]
                self.vars[o["name"]] = o["value"] if v["isExpression"] else self.text(v["value"])
            elif d == "set_page":
                self.page = o["page"]
            elif d == "get" and a["connectionId"] == "power":
                self.log.append(("power", "on" if self.text(o["url"]).endswith("on=true") else "off"))
            elif d == "get":
                self.log.append(("wiim", self.text(o["url"]).split("=", 1)[1]))
            elif a["connectionId"] == "wing" and not self.connected:
                pass
            elif d == "set-send-mute":
                self.sends[(o["src"], o["dest"])] = o["mute"] == "0"
            elif d == "set-mute":
                sel = o["sel"]
                muted = not self.mutes.get(sel, False) if o["mute"] == "-1" else o["mute"] == "1"
                self.mutes[sel] = muted
                kind, n = sel.strip("/").split("/")
                self.wing[f"{kind}{n}_mute"] = int(muted)
            elif d == "set-fader":
                self.wing[self.level_name(o["sel"])] = float(o["level"])
            elif d == "fader-delta":
                name = self.level_name(o["sel"])
                self.wing[name] = max(-90.0, to_num(self.wing.get(name, -90.0))) + float(o["delta"])
            elif d == "set_complex":
                params = self.text(o["params"])
                self.log.append(("dmx", params))
                for group in filter(None, params.split(";")):
                    channels, value = group.split(",")
                    first, _, last = channels.partition("-")
                    for ch in range(int(first), int(last or first) + 1):
                        self.dmx[ch - 1] = int(float(value))
            elif d == "custom_variable_sync_to_default":
                self.kept[o["name"]] = self.vars[o["name"]]
            elif d == "wait":
                pass
            else:
                raise AssertionError(f"Sim does not know {d}")

    def turn(self, loc, side, clicks=1, gap=1000):
        """Turns a dial: `clicks` in one report from the deck, `gap` ms after the last report."""
        self.clock += gap
        self.this = {"delta": clicks if side == "right" else -clicks}
        self.run(getattr(KEYS[loc], side))
        self.this = {}

    def press(self, loc, held=False):
        key = KEYS[loc]
        self.run(key.down)
        self.run(key.hold[1] if held else key.up)

    def hears(self, z):
        """The one source a zone hears, from the Wing state rather than the variables."""
        mx = f"/mtx/{ZONES[z - 1][2]}"
        if self.mutes.get(mx, True):
            return "Off"
        on = [name for name, src, _, _ in SOURCES if self.sends.get((src, mx))]
        assert len(on) == 1, (z, on)
        return on[0]

    def channel(self, group):
        """The DMX value on the first channel of a light group."""
        return self.dmx[int(LIGHT_GROUPS[group][0].split("-")[0]) - 1]

    def show(self, loc, field_name):
        return self.eval(KEYS[loc].show[field_name])


def dmx_of(percent_all, percent_group):
    return math.floor(255 * percent_all / 100 * percent_group / 100 + 0.5)


def tests():
    checks = []

    def ok(name, condition):
        checks.append((name, bool(condition)))

    # Every room scene reaches the Wing exactly as the table says, from any starting scene
    for first in SCENES:
        for name, _, _, zones in SCENES:
            s = Sim()
            s.press(SCENE_LOC[first[0]])
            s.press(SCENE_LOC[name])
            ok(f"{first[0]} then {name}", [s.hears(z) for z in range(1, 6)] == zones)
    # Every zone and source works, and leaves the other zones alone
    for z, name, *_ in ZONES:
        for s_index, (source, *_rest) in enumerate(SOURCES):
            s = Sim()
            s.press(SCENE_LOC["Auditorium"])
            before = [s.hears(i) for i in range(1, 6)]
            s.press(f"{ZONES[z - 1][4]}/0/{s_index}")
            before[z - 1] = source
            ok(f"{name} on {source}", [s.hears(i) for i in range(1, 6)] == before)
    # Lights: looks, off and the dials
    for n, lin, fix in LOOKS:
        s = Sim()
        s.press(f"1/0/{n}")
        ok(f"Lights {n} plays", s.channel(0) == dmx_of(100, lin) and s.channel(1) == dmx_of(100, fix)
           and s.vars["lt_look"] == str(n))
    s = Sim()
    s.press("1/0/2")
    s.press("1/0/0")
    ok("Lights Off goes dark and keeps the look", s.channel(0) == 0 and s.channel(1) == 0 and s.vars["lt_look"] == "2")
    s.turn("1/3/0", "right")
    ok("All Lights brings the look back from off", s.channel(0) == dmx_of(LIGHT_STEP, 65))
    s.run(KEYS["1/3/0"].down)
    ok("pushing All Lights turns off", s.channel(0) == 0)
    s.run(KEYS["1/3/0"].down)
    ok("pushing again turns on at full", s.channel(0) == dmx_of(100, 65) and s.vars["lt_all"] == "100")
    for _ in range(30):
        s.turn("1/3/0", "right")
    ok("All Lights stops at 100%", s.vars["lt_all"] == 100)
    for _ in range(30):
        s.turn("1/3/0", "left")
    ok("All Lights stops at 0%", s.vars["lt_all"] == 0 and s.channel(1) == 0)
    s = Sim()
    s.press("1/0/3")
    s.turn("1/3/1", "left")
    s.turn("1/3/1", "left")
    ok("Linear moves only the linear lights", s.channel(0) == dmx_of(100, 90) and s.channel(1) == dmx_of(100, 100))
    s.run(KEYS["1/3/1"].down)
    ok("pushing Linear restores the look", s.channel(0) == dmx_of(100, 100))
    s.turn("1/3/0", "left")
    ok("All Lights scales every group", s.channel(0) == dmx_of(95, 100) and s.channel(1) == dmx_of(95, 100))
    # Dials speed up when turned quickly, one dial and one direction at a time
    s = Sim()
    s.press("1/0/2")
    s.turn("1/3/0", "left", gap=400)
    s.turn("1/3/0", "left", gap=400)
    ok("slow clicks move one step each", s.vars["lt_all"] == 90)
    s.turn("1/3/0", "left", gap=80)
    ok("medium clicks move two steps each", s.vars["lt_all"] == 80)
    s.turn("1/3/0", "left", gap=20)
    ok("fast clicks move four steps each", s.vars["lt_all"] == 60)
    s.turn("1/3/0", "right", gap=20)
    ok("turning back the other way starts slow", s.vars["lt_all"] == 65)
    s.turn("1/3/1", "left", gap=20)
    ok("another dial starts slow", s.vars["lt_linear"] == 60)
    s.turn("1/3/0", "left", clicks=3, gap=400)
    ok("a report of several clicks moves that many steps", s.vars["lt_all"] == 50)
    s.turn("1/3/0", "left", clicks=3, gap=10)
    ok(f"one report moves at most {TURN_MAX} steps", s.vars["lt_all"] == 50 - LIGHT_STEP * TURN_MAX)
    s = Sim()
    s.press(SCENE_LOC["Music Inside"])
    for _ in range(3):
        s.turn("1/3/2", "right", gap=20)
    ok("a fast Volume turn stops exactly at 6 dB over normal", s.wing["bus15_level"] == float(SRC_MAX)
       and s.vars["music_level"] == SRC_MAX)
    s.turn("4/3/2", "left", gap=20)
    s.turn("4/3/2", "left", gap=20)
    ok("zone dials speed up too", s.wing["mtx1_level"] == -6.0 - 1 - TURN_FAST and s.vars["z1_level"] == -11)
    s.turn("1/3/3", "left", gap=20)
    s.turn("1/3/3", "left", gap=20)
    ok("the Mics dial speeds up too", s.wing[f"bus{MIC_BUS}_level"] == MIC_START - 1 - TURN_FAST)
    s = Sim(connected=False)
    s.press(SCENE_LOC["Music Inside"])
    s.turn("1/3/2", "left", gap=20)
    s.turn("1/3/2", "left", gap=20)
    ok("speed works with no Wing", s.vars["music_level"] == -1 - TURN_FAST)
    s = Sim()
    s.vars.update(turn_fast_ms="0", turn_medium_ms="0")
    s.press("1/0/2")
    for _ in range(3):
        s.turn("1/3/0", "left", gap=20)
    ok("setting both speeds to 0 turns the speed-up off", s.vars["lt_all"] == 85)
    # Saving a look
    s = Sim()
    s.press("1/0/2")
    for _ in range(4):
        s.turn("1/3/0", "left")
    for _ in range(3):
        s.turn("1/3/1", "right")
    before = (s.channel(0), s.channel(1))
    s.press("1/0/1", held=True)
    ok("holding Lights 1 saves the lights as they are", s.vars["look1_linear"] == round(80 * 80 / 100)
       and s.vars["look1_fix"] == round(65 * 80 / 100) and s.vars["lt_look"] == "1")
    ok("saving doesn't change the lights", abs(s.channel(0) - before[0]) <= 1 and abs(s.channel(1) - before[1]) <= 1)
    ok("saving shows Saved, then clears", s.vars["lt_saved"] == "0")
    ok("saving writes the look to its startup value, so exports keep it",
       s.kept == {"look1_linear": s.vars["look1_linear"], "look1_fix": s.vars["look1_fix"]})
    s.press("1/0/3")
    s.press("1/0/1")
    ok("Lights 1 plays what was saved", abs(s.channel(0) - before[0]) <= 1 and abs(s.channel(1) - before[1]) <= 1)
    s = Sim()
    s.press("1/0/0")
    s.press("1/0/2", held=True)
    ok("saving while off does nothing", s.vars["look2_linear"] == "65")
    # Stations: the rack and every door share the same pages and start on Home
    groups = surface_groups()
    ok("every station starts on Home with every page", all(
        g["startup_page"] == 1 and g["allowed_pages"] == DECK_PAGES for g in groups.values()) and len(groups) == 4)
    ok("pages are numbered from 1 with no gaps", DECK_PAGES == list(range(1, len(DECK_PAGES) + 1)))
    # iPad Mode
    s = Sim()
    s.press("1/0/3")
    s.press("2/1/2", held=True)
    ok("iPad Mode fades Companion's output out", s.vars["light_mode"] == "ipad" and s.channel(0) == 0 and s.channel(1) == 0)
    for loc in ("1/0/1", "1/0/0", "1/0/2"):
        s.press(loc)
    s.turn("1/3/0", "right")
    s.turn("1/3/1", "right")
    s.press("1/0/1", held=True)
    ok("lights are locked in iPad Mode", s.channel(0) == 0 and s.vars["lt_look"] == "3" and s.vars["look1_linear"] == "35")
    ok("the strip shows iPad", s.show("1/2/0", "value") == "iPad")
    s.press("2/1/2", held=True)
    ok("leaving iPad Mode restores the look", s.vars["light_mode"] == "deck" and s.channel(0) == 255)
    s = Sim()
    s.press("1/0/0")
    s.press("2/1/2", held=True)
    s.press("2/1/2", held=True)
    ok("leaving after Lights Off stays dark", s.channel(0) == 0)
    # Music starts once, stops when unused, and survives zone changes
    start = ("wiim", "MCUKeyShortClick:1")
    s = Sim()
    s.press(SCENE_LOC["Music Inside"])
    ok("music starts once", s.log.count(start) == 1)
    s.log.clear()
    s.press(SCENE_LOC["Music Everywhere"])
    ok("no restart when already playing", start not in s.log)
    s.log.clear()
    s.press(SCENE_LOC["Auditorium"])
    ok("music stops when unused", ("wiim", "setPlayerCmd:stop") in s.log)
    s = Sim()
    s.press("1/1/2")
    ok("Music from silence plays inside", s.vars["z1_src"] == "Playlist" and s.vars["z2_src"] == "Off"
       and s.log.count(start) == 1)
    s.press(SCENE_LOC["Music Everywhere"])
    s.press("1/1/2")
    ok("Music lit by Everywhere turns the music off everywhere", all(
        s.vars[f"z{z}_src"] == "Off" for z, *_ in ZONES) and ("wiim", "setPlayerCmd:stop") in s.log)
    s = Sim()
    s.press("3/0/1")
    ok("playlist key in a silent room starts Inside", s.vars["z1_src"] == "Playlist"
       and ("wiim", "MCUKeyShortClick:2") in s.log and s.vars["z2_src"] == "Off")
    s.log.clear()
    s.press("3/0/2")
    ok("playlist key while playing swaps it", ("wiim", "MCUKeyShortClick:3") in s.log and s.vars["music_n"] == "3")
    s = Sim()
    s.press(SCENE_LOC["Music Inside"])
    s.log.clear()
    s.press("4/0/0")
    ok("music keeps going while another zone uses it", ("wiim", "setPlayerCmd:stop") not in s.log)
    # Volume follows whatever is playing, with the Wing connected
    s = Sim()
    s.turn("1/3/2", "right")
    ok("Volume does nothing with every zone off", s.wing["bus15_level"] == 0.0 and s.show("1/2/2", "value") == "Off"
       and s.show("1/2/2", "title") == "VOLUME")
    s.press(SCENE_LOC["Music Inside"])
    s.turn("1/3/2", "right")
    ok("Volume moves the music while music plays", s.wing["bus15_level"] == 1.0 and s.wing["bus14_level"] == 0.0
       and s.wing["mtx1_level"] == -6.0 and s.show("1/2/2", "value") == "+1 dB" and s.show("1/2/2", "title") == "MUSIC")
    s.press(SCENE_LOC["Auditorium"])
    ok("a room button puts the music back to normal", s.wing["bus15_level"] == 0.0
       and s.show("1/2/2", "title") == "AUDITORIUM" and s.show("1/2/2", "value") == "Normal")
    s.turn("1/3/2", "left")
    s.turn("1/3/2", "left")
    ok("Volume moves the auditorium feed while it plays", s.wing["bus14_level"] == -2.0
       and s.wing["bus15_level"] == 0.0 and s.show("1/2/2", "value") == "-2 dB")
    s.run(KEYS["1/3/2"].down)
    ok("pushing Volume puts it back to normal", s.wing["bus14_level"] == 0.0 and s.show("1/2/2", "value") == "Normal")
    for _ in range(10):
        s.turn("1/3/2", "right")
    ok("Volume stops at 6 dB over normal", s.wing["bus14_level"] == float(SRC_MAX))
    s.wing["bus14_level"] = -60.0
    s.turn("1/3/2", "left")
    ok("Volume stops at -60 dB", s.wing["bus14_level"] == -60.0)
    s.press(SCENE_LOC["Lobby Event"])
    s.wing["main1_level"] = -3.0
    s.turn("1/3/2", "right")
    ok("in a Lobby Event, Volume moves Main 1", s.wing["main1_level"] == -2.0 and s.show("1/2/2", "title") == "LOBBY MIX")
    s.press(SCENE_LOC["Lobby Event"])
    ok("room buttons leave Main 1 to the band's mixer", s.wing["main1_level"] == -2.0)
    s = Sim()
    s.press("4/0/1")
    s.press("5/0/0")
    s.turn("1/3/2", "right")
    ok("with mixed zones, Volume follows the first zone that is on", s.wing["bus15_level"] == 1.0
       and s.wing["bus14_level"] == 0.0)
    # Zone and mic dials, with the audio system on and nothing playing
    s = Sim()
    s.press("1/1/0")
    s.turn("4/3/2", "right")
    s.turn("4/3/2", "right")
    ok("zone dial moves only its zone", s.wing["mtx1_level"] == -4.0 and s.wing["mtx2_level"] == -10.0
       and s.vars["z1_level"] == -4.0)
    s.run(KEYS["4/3/2"].down)
    ok("pushing the zone dial restores it", s.wing["mtx1_level"] == -6.0)
    s.wing["mtx1_level"] = "-oo"
    s.turn("4/3/2", "right")
    ok("a zone dial lifts a zone from -oo", s.wing["mtx1_level"] == -89.0)
    s = Sim()
    s.press("1/1/0")
    s.wing[f"bus{MIC_BUS}_level"] = 0.0
    s.turn("1/3/3", "right")
    ok("Mics stop at 0 dB", s.wing[f"bus{MIC_BUS}_level"] == 0.0)
    s.run(KEYS["1/3/3"].down)
    ok("pushing Mics mutes them", s.show("1/2/3", "value") == "Muted" and s.wing[f"bus{MIC_BUS}_mute"] == 1)
    s.run(KEYS["1/3/3"].down)
    ok("pushing again unmutes", s.show("1/2/3", "value") == "0 dB")
    s.wing[f"bus{MIC_BUS}_level"] = -20.0
    ok("the Mics panel follows the Wing, not Companion's copy", s.show("1/2/3", "value") == "-20 dB")
    ok("no badge while the Wing reports", s.eval(KEYS["1/2/2"].show["badge"]) is False)
    s = Sim()
    s.press(SCENE_LOC["Music Inside"])
    ok("zone strip shows source and level", s.show("4/2/2", "title") == "MAINS · Playlist"
       and s.show("4/2/2", "value") == "-6 dB" and s.show("4/2/2", "pct") == 90)
    s.press("1/0/2")
    s.turn("1/3/0", "left")
    ok("lights strip shows the level", s.show("1/2/0", "value") == "95%")
    # The same dials on a desk with no Wing: Companion keeps the levels, and the panels say so
    s = Sim(connected=False)
    ok("no Wing shows the badge", s.eval(KEYS["1/2/2"].show["badge"]) is True)
    s.press(SCENE_LOC["Music Inside"])
    s.turn("1/3/2", "right")
    s.turn("1/3/2", "right")
    ok("Volume moves with no Wing", s.show("1/2/2", "value") == "+2 dB" and s.vars["music_level"] == 2.0)
    s.run(KEYS["1/3/2"].down)
    ok("pushing Volume resets with no Wing", s.show("1/2/2", "value") == "Normal")
    s.turn("1/3/3", "left")
    ok("Mics move with no Wing", s.show("1/2/3", "value") == f"{MIC_START - 1} dB")
    s.run(KEYS["1/3/3"].down)
    ok("Mics mute with no Wing", s.show("1/2/3", "value") == "Muted")
    s.turn("4/3/2", "left")
    s.press(SCENE_LOC["Music Inside"])
    ok("zone dial with no Wing", s.show("4/2/2", "value") == "-6 dB")
    # Close Up and triggers
    s = Sim()
    s.press("1/0/3")
    s.press(SCENE_LOC["Lobby Event"])
    s.press("2/1/2", held=True)
    s.press("2/1/1", held=True)
    ok("Close Up turns everything off and leaves iPad Mode", s.vars["light_mode"] == "deck" and s.channel(0) == 0
       and [s.hears(z) for z in range(1, 6)] == ["Off"] * 5)
    ok("Close Up turns the audio system off", s.vars["audio_power"] == "0" and s.log[-1] == ("power", "off"))
    s = Sim()
    s.vars.update(lt_all="70", lt_linear="50")
    s.run(TRIGGERS["startup_recovery"]["control"]["actions"])
    ok("startup restores the lights", s.channel(0) == dmx_of(70, 50))
    ok("startup sends the relay off while the audio is off", s.log[-1] == ("power", "off"))
    s.vars["audio_power"] = "1"
    s.run(TRIGGERS["startup_recovery"]["control"]["actions"])
    ok("startup sends the relay on while the audio is on", s.log[-1] == ("power", "on"))
    s.vars["light_mode"] = "ipad"
    s.run(TRIGGERS["startup_recovery"]["control"]["actions"])
    ok("startup in iPad Mode keeps output at zero", s.channel(0) == 0)
    s.run(TRIGGERS["schedule_night"]["control"]["actions"])
    ok("night clears iPad Mode and turns off", s.vars["light_mode"] == "deck" and s.vars["lt_all"] == "0")
    s = Sim()
    s.run(TRIGGERS["schedule_sunday"]["control"]["actions"])
    ok("Sunday schedule: Lights 3 and the auditorium", s.channel(0) == 255 and s.hears(1) == "Auditorium"
       and s.vars["audio_power"] == "1")
    s.run(TRIGGERS["schedule_night"]["control"]["actions"])
    ok("night schedule turns the audio system off", s.vars["audio_power"] == "0" and s.log[-1] == ("power", "off"))
    # Audio power, and the source keys that toggle
    lit = lambda st, loc: any(truthy(st.eval(x)) for x, state in KEYS[loc].fb if state == "active")  # noqa: E731

    def label_of(st, loc):
        """The label and art state a key shows now. Like Companion, a later feedback wins over an earlier one."""
        k, shown = KEYS[loc], (KEYS[loc].label, "rest")
        for x, state in k.fb:
            if truthy(st.eval(x)):
                shown = (k.labels.get(state, shown[0]), state)
        return shown
    s = Sim()
    ok("the system starts off, with the power key red and saying Turn Audio On", s.vars["audio_power"] == "0"
       and lit(s, "1/1/0") and label_of(s, "1/1/0") == ("Turn Audio On", "active"))
    s.turn("1/3/3", "right")
    s.run(KEYS["1/3/3"].down)
    s.turn("4/3/2", "right")
    s.run(KEYS["4/3/2"].down)
    ok("while off, the Mics and zone dials do nothing", s.wing[f"bus{MIC_BUS}_level"] == MIC_START
       and s.wing[f"bus{MIC_BUS}_mute"] == 0 and s.wing["mtx1_level"] == -6.0 and not s.log)
    ok("while off, the Volume and Mics panels say Off and grey out", s.show("1/2/2", "value") == "Off"
       and s.show("1/2/3", "value") == "Off" and s.show("1/2/3", "pct") == 0 and s.eval(KEYS["1/2/3"].show["dim"])
       and s.eval(KEYS["1/2/2"].show["dim"]))
    s.press("1/1/0")
    ok("the power key, pressed while off, turns the system on with nothing playing", s.vars["audio_power"] == "1"
       and label_of(s, "1/1/0") == ("Turn Audio Off", "on")
       and s.log == [("power", "on")] and not lit(s, "1/1/0")
       and [s.vars[f"z{z}_src"] for z, *_ in ZONES] == ["Off"] * 5)
    ok("once on, the Mics panel shows its level", s.show("1/2/3", "value") == f"{MIC_START} dB"
       and not s.eval(KEYS["1/2/3"].show["dim"]))
    s = Sim()
    s.press("1/1/1")
    ok("Auditorium from off turns the system on, and the power key turns green", s.vars["audio_power"] == "1"
       and label_of(s, "1/1/0") == ("Turn Audio Off", "on")
       and s.log.count(("power", "on")) == 1 and s.hears(1) == "Auditorium" and lit(s, "1/1/1"))
    s.log.clear()
    s.press("1/1/1")
    ok("Auditorium pressed again turns it off and leaves the system on", s.vars["audio_power"] == "1"
       and [s.hears(z) for z in range(1, 6)] == ["Off"] * 5 and not lit(s, "1/1/1") and not lit(s, "1/1/0")
       and ("power", "off") not in s.log)
    s.press("1/1/1")
    s.press("1/1/2")
    ok("Music while Auditorium plays swaps them", lit(s, "1/1/2") and not lit(s, "1/1/1")
       and [s.hears(z) for z in range(1, 6)] == SCENES[1][3])
    s.press("1/1/1")
    ok("Auditorium while Music plays swaps them back, and stops the player", lit(s, "1/1/1") and not lit(s, "1/1/2")
       and ("wiim", "setPlayerCmd:stop") in s.log)
    s.log.clear()
    s.press("1/1/0")
    ok("Turn Audio Off turns every zone off, then the amplifiers", s.vars["audio_power"] == "0"
       and label_of(s, "1/1/0") == ("Turn Audio On", "active")
       and [s.hears(z) for z in range(1, 6)] == ["Off"] * 5 and s.log[-1] == ("power", "off")
       and not lit(s, "1/1/1"))
    s = Sim()
    s.press("1/1/1")
    s.press("5/0/1")
    s.log.clear()
    s.press("1/1/1")
    ok("Auditorium off leaves another zone's music playing", s.hears(2) == "Playlist" and s.hears(1) == "Off"
       and ("wiim", "setPlayerCmd:stop") not in s.log)
    s = Sim()
    s.press("1/1/2")
    ok("Music from off turns the system on, and the power key turns green", s.vars["audio_power"] == "1"
       and label_of(s, "1/1/0") == ("Turn Audio Off", "on") and s.hears(1) == "Playlist")
    for loc, source in (("2/0/0", "Bluetooth"), ("2/0/1", "Lobby Mix")):
        s = Sim()
        s.press(loc)
        on = s.vars["audio_power"] == "1" and s.hears(1) == source and lit(s, loc)
        s.press(loc)
        ok(f"{source} toggles like Auditorium", on and s.hears(1) == "Off" and not lit(s, loc))
    s = Sim()
    s.press("6/0/2")
    ok("a zone page source key turns the system on", s.vars["audio_power"] == "1" and s.hears(3) == "Bluetooth")
    s = Sim()
    s.press("3/0/3")
    ok("a playlist key turns the system on", s.vars["audio_power"] == "1" and s.hears(1) == "Playlist")
    # Every display evaluates in every state without an error
    states = [Sim(), Sim(), Sim(), Sim(connected=False), Sim()]
    states[1].press("1/0/2")
    states[1].press(SCENE_LOC["Music Everywhere"])
    states[2].press("1/1/0")
    states[2].press("2/1/2", held=True)
    states[2].wing.update({"mtx1_level": "-oo", f"bus{MIC_BUS}_mute": 1})
    states[4].press("1/1/1")
    bad = []
    for st in states:
        for loc, c in CONTROLS.items():
            for el in c["style"]["layers"]:
                for name, v in el.items():
                    if is_wrapped(v) and v["isExpression"]:
                        try:
                            st.eval(v["value"])
                        except Exception as e:  # noqa: BLE001
                            bad.append(f"{loc} {el['id']}.{name}: {e}")
    ok("every display evaluates" + (": " + "; ".join(bad[:3]) if bad else ""), not bad)
    failed = [n for n, passed in checks if not passed]
    return len(checks), failed


# ---------------------------------------------------------------- reference doc
def plain(label):
    """A key label as one line of readable text, for the reference doc."""
    return label.replace("-\n", "").replace("\n", " ")


def name_of(loc):
    k = KEYS[loc]
    return plain(k.label) if k.label else (k.show or {}).get("title", "")


CONDITIONS = {DECK: "the deck has the lights, not the iPad", NONE_PLAYLIST: "no zone is on Playlist",
              LIGHTS_ON: "the lights are on", f"{DECK} && {LIGHTS_ON}": "the deck has the lights and they are on",
              POWERED: "the audio system is on",
              **{plays(source): f"any zone is on {source}" for source, *_ in SOURCES},
              **{f"$(custom:z{z}_src) == '{source}'": f"{name} is on {source}"
                 for z, name, *_ in ZONES for source, *_ in SOURCES}}


def describe(actions, indent=0):
    out, pad = [], "  " * indent
    for a in actions:
        o = {k: v["value"] for k, v in a["options"].items()}
        d = a["definitionId"]
        if d == "button_pressrelease":
            out.append(f"{pad}Run `{o['location']}` {name_of(o['location'])}")
        elif d == "wait":
            out.append(f"{pad}Wait {int(o['time']) / 1000:g} s")
        elif d == "custom_variable_sync_to_default":
            out.append(f"{pad}Keep `{o['name']}` as its startup value")
        elif d == "custom_variable_set_value":
            v = a["options"]["value"]
            if o["name"] == "turn_n":
                out.append(f"{pad}Set `turn_n` from how fast the dial turned (see Dial speed)")
            elif v["isExpression"] and "\n" in v["value"]:
                out.append(f"{pad}Set `{o['name']}` from the levels (see Lighting math)")
            else:
                out.append(f"{pad}Set `{o['name']}` to `{v['value']}`")
        elif d == "set_page":
            out.append(f"{pad}This surface goes to page {o['page']}")
        elif d == "logic_if":
            cond = a["children"]["condition"][0]["options"]["expression"]["value"]
            out.append(f"{pad}If {CONDITIONS.get(cond, f'`{cond}`')}:")
            out += describe(a["children"]["actions"], indent + 1)
            if a["children"]["else_actions"]:
                out.append(f"{pad}Otherwise:")
                out += describe(a["children"]["else_actions"], indent + 1)
        elif d == "set_complex":
            out.append(f"{pad}Art-Net to the ODE: `$(custom:dmx_cmd)`, fading {int(o['duration']) / 1000:g} s")
        elif d == "get" and a["connectionId"] == "power":
            on = o["url"].endswith("on=true")
            out.append(f"{pad}Relay {'closes' if on else 'opens'}: the Furman sequences the amplifiers "
                       f"{'on' if on else 'off'}")
        elif d == "get":
            out.append(f"{pad}WiiM `{o['url'].split('=', 1)[1]}`")
        elif d == "set-send-mute":
            mx = o["dest"].split("/")[-1]
            out.append(f"{pad}Wing `{o['src']}/send/MX{mx}/on` = {1 if o['mute'] == '0' else 0}")
        elif d == "set-mute":
            out.append(f"{pad}Wing `{o['sel']}/mute` " + ("toggles" if o["mute"] == "-1" else f"= {o['mute']}"))
        elif d == "set-fader":
            out.append(f"{pad}Wing `{o['sel']}/fdr` = {o['level']} dB")
        elif d == "fader-delta":
            if a["options"]["delta"]["isExpression"]:
                out.append(f"{pad}Wing `{o['sel']}/fdr` moves by the same amount")
            else:
                out.append(f"{pad}Wing `{o['sel']}/fdr` {int(o['delta']):+d} dB")
    return out


def behind(key):
    lines = []
    if key.left is not None:
        lines = ["Push:"] + describe(key.down, 1) + ["Turn left:"] + describe(key.left, 1) + \
                ["Turn right:"] + describe(key.right, 1)
    else:
        if key.up:
            lines += ["Tap:"] + describe(key.up, 1)
        if key.hold:
            lines.append(f"Hold {key.hold[0] / 1000:g} s:")
            lines += describe(key.hold[1], 1)
        lines += describe(key.down)
    return "<br>".join(line.replace("  ", "&nbsp;&nbsp;") for line in lines) or "Nothing"


def shows(key):
    if key.kind == "strip":
        return f"{key.show['title'] if not key.show.get('title_expr') else 'Zone and source'} (live)"
    if key.kind == "dial":
        return f"Dial: {key.label}"
    return plain(key.label)


def page_table(number):
    rows = ["| Key | Shows | Does | What runs behind it |", "| --- | --- | --- | --- |"]
    keys = sorted((k for k in KEYS.values() if k.page == number), key=lambda k: (k.row, k.col))
    for k in keys:
        rows.append(f"| `{k.loc}` | {shows(k)} | {k.does} | {behind(k)} |")
    return "\n".join(rows)


def library_table(number):
    rows = ["| Key | Block | Does | Sends |", "| --- | --- | --- | --- |"]
    for k in sorted((k for k in KEYS.values() if k.page == number), key=lambda k: (k.row, k.col)):
        rows.append(f"| `{k.loc}` | {plain(k.label)} | {k.does} | {behind(k)} |")
    return "\n".join(rows)


def write_doc(count, checks):
    t = []
    a = t.append
    a("# Stream Deck pages\n")
    a("This is every Stream Deck page, key by key, with what runs behind each one. It is generated from "
      "[build.py](../config/stream-deck/build.py), together with the importable file and the artwork, so all of them match.\n")
    a("Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig) into Companion instead of "
      "building these by hand. [Companion setup](07-companion-setup.md) has the steps.\n")
    a(f"**Status:** The file has {count} buttons and has not yet been imported into a real Companion. Its format, "
      "every action and every button element were checked against the Companion 5.1.3 and module source, every "
      f"expression in it was parsed and run, and its logic passed {checks} simulated checks. "
      "[Bench test 13](09-testing.md) is the real proof.\n")
    a("## How a press reaches the hardware\n")
    a("Real keys don't talk to hardware directly. Each one runs a block on a Library page, so a change happens in one place.\n")
    a("| Target | Connection | Message | Example |\n| --- | --- | --- | --- |\n"
      f"| Wing Rack | `wing`, {WING_IP} | Wing OSC through the Behringer module | `/bus/14/send/MX1/on` = 1 |\n"
      f"| ODE Mk3 | `dmx`, {ODE_IP}, Art-Net universe {ARTNET_UNIVERSE} | Channel values through the Art-Net module | `1-8,166;9-32,166;` |\n"
      f"| WiiM | `wiim`, https://{WIIM_IP}/ | HTTPS GET to `httpapi.asp?command=` | `MCUKeyShortClick:1` |\n"
      f"| Amplifier power | `power`, http://{POWER_IP}/ | HTTP GET to a Shelly Pro 1 relay, wired to the Furman "
      "sequencer's remote terminals | `rpc/Switch.Set?id=0&on=true` |\n")
    a("Key addresses read page/row/column from 0, the same form Companion uses. Rows and columns start at the top left.\n")
    a("On the Stream Deck +, rows 0 and 1 are the keys, row 2 is the touch strip, and row 3 is the dials.\n")
    a("## How it looks\n")
    a("Amber is lighting, warm white is the linear lights, blue is audio, violet is music, teal is the mics, purple "
      "is the iPad and red is off. A lit key, bright with a white icon, is the active choice. In iPad Mode, "
      "lighting keys go grey and show a lock. A green key with a check mark has just saved a look. While the audio "
      "system is off, the audio power key is red and says Turn Audio On, and the audio panels on the touch strip go "
      "grey. While it is on, that key is green and says Turn Audio Off.\n")
    a("The touch strip shows a live panel above each dial: what the dial does, its value, and a level bar that moves "
      "as you turn it.\n")
    a("Labels are live text, so you can rename a key in Companion without touching its artwork. The artwork is in "
      "[config/stream-deck/icons](../config/stream-deck/icons): 144-pixel keys, drawn larger than the Stream Deck +'s "
      "120-pixel keys so they stay sharp, and 200 by 100 touch strip panels, the size of each strip segment.\n")
    a(f"Inside Companion the same {len(LIBRARY)} images live in the image library, stored once, and keys refer to "
      "them by name, such as `$(image:tile_light_level2_active)`. Replacing an image there changes every key that "
      "uses it.\n")
    a("## Pages\n")
    a("Every station is a Stream Deck + with 8 keys, a touch strip and 4 dials, and they all share these pages. "
      "The rack and each door have their own surface group, which sets the pages that station may use. Every group "
      "starts on Home with every page, so to lock a door out of something, untick its page in that door's group.\n")
    a("The first two dials and the last one do the same thing on every page, so hands learn them. The third dial is "
      "the volume of whatever the page is about.\n")
    a("![Stream Deck pages](images/stream-deck-pages.png)\n")
    for n in (1, 2, 3):
        a(f"### Page {n}: {PAGES[n][0]}\n")
        a(page_table(n) + "\n")
    first, last = ZONES[0][4], ZONES[-1][4]
    a(f"### Pages {first} to {last}: Zones\n")
    a(f"All five zone pages match. Page {first} is shown here. The others use their own matrix and variable.\n")
    a("| Page | Zone | Matrix | Variable | Normal fader |\n| --- | --- | --- | --- | --- |")
    for z, name, mx, db, page, _ in ZONES:
        a(f"| {page} | {name} | MX{mx} | `z{z}_src`, `z{z}_level` | {db} dB |")
    a("")
    a(page_table(first) + "\n")
    a("## Audio power\n")
    a("A Furman sequencer powers the amplifiers. Companion switches it through a network relay, a Shelly Pro 1, "
      "whose contact is wired to the Furman's remote terminals. Closing the contact sequences the amplifiers on, "
      "and opening it sequences them off. The Wing Rack, the WiiM and the Bluetooth receiver stay on all the time, "
      "so Companion can always reach them and a source plays as soon as the amplifiers are up. "
      "[Audio setup](06-audio-setup.md#amplifier-power) has the wiring.\n")
    a("`audio_power` holds the state: 1 while the system is on, 0 while it is off. Two blocks change it, "
      f"`{POWER_ON}` Power On and `{POWER_OFF}` Power Off, and only they talk to the relay.\n")
    a("| Key | While the audio is off | While it's on |\n| --- | --- | --- |\n"
      "| Audio power key | Red, saying Turn Audio On. Press to turn the system on, with nothing playing | Green, "
      "saying Turn Audio Off. Press to turn every zone off, stop the music, then turn the amplifiers off |\n"
      "| Auditorium, Music, Bluetooth, Lobby Event | Press to turn the system on and play that source | Lit while "
      "its source plays anywhere. Press a lit key to turn its source off, leaving the system on. Press another to "
      "swap to it |\n"
      "| Everywhere, Inside, a playlist, a zone's source | Press to turn the system on and play | Plays, as before |\n"
      "| Volume and Mics dials, zone dials | Do nothing. Their panels say Off and go grey | Work as usual |\n"
      "| Close Up, and the night schedule | Stay off | Turn the lights and the audio system off |\n")
    a("Only Auditorium, Music, Bluetooth and Lobby Event toggle. Everywhere, Inside and the playlist keys choose "
      "where and what plays, so pressing them again keeps playing. On a zone page, the zone's Off key turns that "
      "zone off.\n")
    a("Five seconds after Companion starts, the startup trigger sends the relay the state in `audio_power`, so the "
      "two always agree. To use a different power switch, such as Furman's own BB-RS232 adapter, change only "
      "those two blocks and that trigger.\n")
    a("## Dial speed\n")
    a(f"Every dial speeds up when it's turned quickly. A slow click moves one step: {LIGHT_STEP}% for the lights, "
      f"1 dB for audio. Clicks closer together than `turn_medium_ms` move {TURN_MEDIUM} steps each, and closer than "
      f"`turn_fast_ms` move {TURN_FAST}. They start at {TURN_MEDIUM_MS} and {TURN_FAST_MS} ms. Turning the other way, "
      "or turning a different dial, starts slow again. When the deck reports several clicks at once, each counts, "
      f"and one report moves at most {TURN_MAX} steps. Levels still stop at their limits.\n")
    a("Each turn first sets `turn_n` with this expression, shown for All Lights turning right. "
      "`$(this:delta)` is the number of clicks the deck reported, and `unixNow()` is the time in milliseconds:\n")
    a("```\n" + turn_speed("all+") + "\n```\n")
    a("Then the dial's block moves by `turn_n` steps. To change the feel, set `turn_medium_ms` and `turn_fast_ms` "
      "on the Variables page. Set both to 0 for one step a click.\n")
    a("## Lighting math\n")
    a("Companion keeps the lights as levels, and one block turns them into DMX. `lt_all` is the All Lights dial. "
      "`lt_linear` and `lt_fix` are the levels of the linear lights and of every other fixture. A Lights key sets "
      "`lt_all` to 100 and copies that look's two saved levels in. Lights Off sets `lt_all` to 0 and keeps the rest, "
      "which is why turning All Lights brings the same look back.\n")
    a("Every channel's value is its full value, times `lt_all`, times its group's level. In iPad Mode every value is 0, "
      "so the iPad's levels are the only ones the ODE sees. This is the expression in `22/1/0` Compute DMX:\n")
    a("```\n" + compute_expr() + "\n```\n")
    a("| Channels | Level | Full value | What they are |\n| --- | --- | --- | --- |")
    for channels, variable, full, what in LIGHT_GROUPS:
        a(f"| {channels} | `{variable}` | {full} | {what} |")
    a("\nThese channels are placeholders until the DMX patch sheet exists. To change the patch, edit `22/1/0` in "
      "Companion, or `LIGHT_GROUPS` in build.py before the first import. A fixture with a color mix that never "
      "changes can put those channels in `STATIC_CHANNELS`.\n")
    a("## Library\n")
    a("No surface shows these pages. Keep them where they are, because every real key points to them by address.\n")
    a("### Page 20: Zones 1 to 4\n")
    a(library_table(20) + "\n")
    a("### Page 21: Zone 5, music, rooms and power\n")
    a(library_table(21) + "\n")
    a("### Page 22: Lights and dials\n")
    a(library_table(22) + "\n")
    a("## Triggers\n")
    a("| Trigger | Starts | Does |\n| --- | --- | --- |")
    for t_ in TRIGGERS.values():
        c = t_["control"]
        a(f"| {c['options']['name']} | {'On' if c['options']['enabled'] else 'Off'} | {t_['does']} |")
    a("\nThe three schedule triggers import turned off. Set their times and turn them on after launch.\n")
    a("## Custom variables\n")
    a("All of these keep their value through a restart, except " +
      ", ".join(f"`{n}`" for n in VARIABLES if n in PERSIST_OFF) + ".\n")
    a("| Variable | Holds | Starts as |\n| --- | --- | --- |")
    for name, (d, v) in VARIABLES.items():
        a(f"| `{name}` | {d} | {v or '(empty)'} |")
    a("\n## Change it later\n")
    a(f"- **Change how fast the dials speed up.** On the Variables page, set `turn_fast_ms` and `turn_medium_ms`. "
      f"Clicks closer together than those many milliseconds move {TURN_FAST} or {TURN_MEDIUM} steps instead of 1. "
      f"Raise them to speed up sooner, or set both to 0 for one step a click.\n")
    a(f"- **Change a look.** At any station, set the lights with the two light dials, then hold Lights 1, 2 or 3 for "
      f"{SAVE_HOLD_MS // 1000} seconds. The key turns green and says Saved. Every station and schedule uses the new look at once.\n"
      "- **Rename a playlist.** Change the label on page 3 and the name in its Library block.\n"
      "- **Use SharePoint playlists.** Edit one block, `21/0/6` Music Play. Change its first WiiM command to "
      "`setPlayerCmd:playlist:<address of the playlist>:0`. Nothing else moves.\n"
      "- **Change a room scene.** Edit its block on row 2 of page 21. Every station and schedule key follows.\n"
      "- **Change a normal level.** Edit `21/0/5`.\n"
      "- **Change the patch.** Edit `22/1/0`, as described in Lighting math.\n"
      "- **Add a station.** Add the surface in Companion, give it its own surface group starting on page 1, and untick "
      "the pages it shouldn't use. Nothing in the pages changes.\n"
      f"- **Use a different power switch.** Edit `{POWER_ON}` Power On, `{POWER_OFF}` Power Off and the startup "
      "trigger. Every key that powers the system goes through those two blocks.\n")
    a("After any change, export the configuration from Companion and commit it next to this file. From then on, that export is the "
      "live copy and `build.py` is only a record of the first version.\n")
    DOC.write_text("\n".join(t), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- layout images
def resolve(sim, v):
    if not is_wrapped(v):
        return v
    return sim.eval(v["value"]) if v["isExpression"] else (sim.text(v["value"]) if isinstance(v["value"], str) else v["value"])


def css_color(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"#{int(v) & 0xFFFFFF:06x}"
    return str(v)


def arc_path(cx, cy, r, start, end):
    def point(deg):
        a = math.radians(deg)
        return cx + r * math.sin(a), cy - r * math.cos(a)
    (x1, y1), (x2, y2) = point(start), point(end)
    large = 1 if (end - start) % 360 > 180 else 0
    return f"M{x1:.2f} {y1:.2f}A{r:.2f} {r:.2f} 0 {large} 1 {x2:.2f} {y2:.2f}"


def preview(ctrl, sim, w, h):
    """HTML that draws a button the way Companion's layered renderer will, for the layout images."""
    layers = {el["id"]: dict(el) for el in ctrl["style"]["layers"]}
    for f in ctrl["feedbacks"]:
        if truthy(sim.eval(f["options"]["expression"]["value"])):
            for o in f["styleOverrides"]:
                layers[o["elementId"]][o["elementProperty"]] = o["override"]
    out = []
    for el in layers.values():
        if el["type"] == "canvas":
            continue
        g = {name: resolve(sim, v) for name, v in el.items() if is_wrapped(v)}
        if not truthy(g["enabled"]):
            continue
        x, y, ww, hh = g["x"] * w / 100, g["y"] * h / 100, to_num(g["width"]) * w / 100, g["height"] * h / 100
        box = (f"position:absolute;left:{x:.1f}px;top:{y:.1f}px;width:{ww:.1f}px;height:{hh:.1f}px;"
               f"opacity:{to_num(g['opacity']) / 100:g}")
        if el["type"] == "box":
            radius = g["cornerRadius"] / 100 * min(ww, hh) / 2
            out.append(f'<div style="{box};background:{css_color(g["color"])};border-radius:{radius:.1f}px"></div>')
        elif el["type"] == "image":
            out.append(f'<img style="{box}" src="{g["base64Image"]}">')
        elif el["type"] == "text":
            inner = hh * 0.97
            size = g["fontsize"] * inner / 100 / 1.2
            align = {"left": "flex-start", "center": "center", "right": "flex-end"}
            out.append(f'<div class="fit" style="{box};display:flex;align-items:{align[g["valign"]]};'
                       f'justify-content:{align[g["halign"]]};text-align:{g["halign"]};color:{css_color(g["color"])};'
                       f'font-weight:{700 if g["weight"] == "bold" else 500};font-size:{size:.1f}px;line-height:1.2">'
                       f'<span>{html.escape(js_str(g["text"])).replace(chr(10), "<br>")}</span></div>')
        elif el["type"] == "circle":
            stroke = g["borderWidth"] / 100 * max(w, h)
            r = min(ww, hh) / 2 - stroke / 2
            cx, cy = x + ww / 2, y + hh / 2
            path = arc_path(cx, cy, r, g["startAngle"], to_num(g["endAngle"]))
            out.append(f'<svg style="position:absolute;left:0;top:0" width="{w}" height="{h}"><path d="{path}" '
                       f'fill="none" stroke="{css_color(g["borderColor"])}" stroke-width="{stroke:.1f}" '
                       f'stroke-linecap="round"/></svg>')
    return f'<div class="btn" style="width:{w}px;height:{h}px">{"".join(out)}</div>'


def sample_state(ipad=False):
    s = Sim()
    s.press("1/0/2")
    s.turn("1/3/0", "left")
    s.turn("1/3/0", "left")
    s.turn("1/3/0", "left")
    s.turn("1/3/0", "left")
    s.press(SCENE_LOC["Music Inside"])
    s.wing[f"bus{MIC_BUS}_level"] = -8.0
    if ipad:
        s.press("2/1/2", held=True)
    return s


def layout(cards, path, width, title, note):
    rows, cols, size = 2, 4, 104
    html_cards = []
    for n, caption, sim in cards:
        grid = "".join(
            preview(CONTROLS[f"{n}/{r}/{c}"], sim, size, size) if f"{n}/{r}/{c}" in CONTROLS
            else f'<div class="btn empty" style="width:{size}px;height:{size}px"></div>'
            for r in range(rows) for c in range(cols))
        cell_w = (cols * size + (cols - 1) * 10) / 4
        strip = "".join(preview(CONTROLS[f"{n}/2/{c}"], sim, int(cell_w), int(cell_w / 2)) for c in range(4))
        dials = "".join(f'<div class="dialcell"><div class="dial"></div><div class="dlabel">'
                        f'{html.escape(KEYS[f"{n}/3/{c}"].label)}</div></div>' for c in range(4))
        extra = f'<div class="strip">{strip}</div><div class="dials">{dials}</div>'
        html_cards.append(f'<div class="card"><h2>{html.escape(caption)}</h2><div class="deck">'
                          f'<div class="grid" style="grid-template-columns:repeat({cols},{size}px)">{grid}</div>'
                          f'{extra}</div></div>')
    page = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;padding:28px;width:{width}px;background:#f3f1ec;font-family:'Segoe UI',Arial,sans-serif;color:#1c2024}}
h1{{font-size:26px;margin:0 0 4px}} p{{margin:0 0 22px;color:#555;max-width:{width - 40}px}}
.wrap{{display:flex;flex-wrap:wrap;gap:28px}} h2{{font-size:15px;margin:0 0 8px;font-weight:600}}
.deck{{background:#17191c;border-radius:18px;padding:16px;display:inline-block;box-shadow:0 6px 18px rgba(0,0,0,.18)}}
.grid{{display:grid;gap:10px}} .btn{{position:relative;overflow:hidden;border-radius:10px;background:#000}}
.btn.empty{{background:#0d0e10}} .fit span{{white-space:nowrap;display:inline-block}}
.strip{{display:flex;margin-top:12px;border-radius:6px;overflow:hidden}} .strip .btn{{border-radius:0}}
.dials{{display:grid;grid-template-columns:repeat(4,1fr);margin-top:12px;justify-items:center}}
.dialcell{{display:flex;flex-direction:column;align-items:center;gap:6px}}
.dial{{width:50px;height:50px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#5a5d63,#232528);
border:2px solid #3a3d42;box-shadow:inset 0 -3px 6px rgba(0,0,0,.4)}}
.dlabel{{color:#aab3bf;font-size:12px;font-weight:600}}</style>
<h1>{html.escape(title)}</h1><p>{html.escape(note)}</p><div class="wrap">{''.join(html_cards)}</div>
<script>for(const d of document.querySelectorAll('.fit')){{const s=d.firstElementChild;let f=parseFloat(d.style.fontSize);
while((s.offsetWidth>d.clientWidth*0.96||s.offsetHeight>d.clientHeight*1.02)&&f>5){{f-=0.5;d.style.fontSize=f+'px'}}}}</script>"""
    target = path.with_suffix(".html")
    target.write_text(page, encoding="utf-8")
    return target


CONTROLS: dict[str, dict] = {}


def main():
    build_library()
    build_pages()
    build_triggers()
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        profile = str(tmp / "profile")
        images = render_art(profile, tmp)
        for k in KEYS.values():
            CONTROLS[k.loc] = control(k, images)
        errors = validate(CONTROLS)
        count, failed = tests()
        print(f"buttons: {len(KEYS)}  structure errors: {len(errors)}  logic checks: {count}  failed: {len(failed)}")
        for line in errors[:40] + failed:
            print("  FAIL", line)
        if errors or failed:
            sys.exit(1)
        data = export()
        out = HERE / "lobby.companionconfig"
        out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"config: {out.stat().st_size // 1024} KB, artwork: {len(images)}")
        IMAGES.mkdir(exist_ok=True)
        write_doc(len(KEYS), count)
        live, ipad, off = sample_state(), sample_state(ipad=True), sample_state()
        off.press("1/1/0")
        for cards, name, width, height, title, note in (
                ([(1, "Page 1: Home", live), (2, "Page 2: More", live), (3, "Page 3: Playlists", live),
                  (4, "Page 4: Zone Mains", live), (1, "Home in iPad Mode", ipad), (1, "Home with the audio off", off)],
                 "stream-deck-pages", 1540, 1060, "Stream Deck + pages, shared by every station",
                 "The touch strip shows each dial's value live. Shown with Lights 2 at 80%, music playing inside, "
                 "and the mics at -8 dB. The last two cards show the lights locked in iPad Mode, and the audio "
                 "system off, with the power key red and saying Turn Audio On, and the Volume and Mics dials greyed out."),):
            page = layout(cards, tmp / name, width, title, note)
            target = IMAGES / f"{name}.png"
            chrome(profile, f"--screenshot={target}", f"--window-size={width + 56},{height}",
                   "--virtual-time-budget=5000", page.as_uri())
            print(name, target.exists(), target.stat().st_size // 1024, "KB")
        real = sum(1 for k in KEYS.values() if PAGES[k.page][1] != "library")
        print(f"surface buttons: {real}, library blocks: {len(KEYS) - real}")


if __name__ == "__main__":
    main()
