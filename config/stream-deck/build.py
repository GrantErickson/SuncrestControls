#!/usr/bin/env python3
"""Builds the lobby Stream Deck configuration from one definition.

Run:  python config/stream-deck/build.py

Produces, from the tables in this file:
  config/stream-deck/lobby.companionconfig   importable Companion file
  config/stream-deck/icons/*.svg, *.png      key icons
  docs/14-stream-deck-pages.md               page-by-page reference
  docs/images/stream-deck-doors.png          door layout
  docs/images/stream-deck-rack.png           rack layout

It needs only Python and an installed Chrome or Edge, which draws the icons.
Nothing here runs at the church. Once the file is imported, Companion is the
live copy, and this script is only for rebuilding before that point.
"""
import base64
import json
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
WING_IP, SPLAY_IP, WIIM_IP = "192.168.50.20", "192.168.50.30", "192.168.50.40"

ZONES = [  # number, name, matrix, default fader in dB, page, icon
    (1, "Mains", 1, -6, 8, "speaker"),
    (2, "Outdoor", 2, -10, 9, "tree"),
    (3, "Soffit", 3, -10, 10, "soffit"),
    (4, "Bathrooms", 4, -12, 11, "restroom"),
    (5, "Vestibule", 5, -12, 12, "door"),
]
SOURCES = [  # name, Wing send source, label on key, icon
    ("Auditorium", "/bus/14", "Auditorium", "church"),
    ("Playlist", "/bus/15", "Playlist", "note"),
    ("Bluetooth", "/bus/16", "Bluetooth", "bluetooth"),
    ("Lobby Mix", "/main/1", "Lobby\nMix", "mic"),
]
PRESETS = [  # number, name, label on key, icon
    (1, "Sunday Morning", "Sunday\nMorning", "sunrise"),
    (2, "Everyday", "Everyday", "calendar"),
    (3, "Bright", "Bright", "sun"),
    (4, "Evening", "Evening", "sunset"),
    (5, "Event", "Event", "people"),
    (6, "Walkthrough", "Walk-\nthrough", "steps"),
    (7, "Seasonal", "Seasonal", "star"),
    (8, "Night", "Night", "moon"),
]
PLAYLISTS = [(1, "Morning"), (2, "Everyday"), (3, "Evening"), (4, "Seasonal")]
SCENES = [  # library name, label, icon, source per zone
    ("Sunday Feed", "Sunday\nFeed", "church", ["Auditorium", "Off", "Off", "Auditorium", "Auditorium"]),
    ("Music Inside", "Inside", "home", ["Playlist", "Off", "Off", "Playlist", "Playlist"]),
    ("Music Everywhere", "Every-\nwhere", "broadcast", ["Playlist"] * 5),
    ("Lobby Event", "Lobby\nEvent", "mic", ["Lobby Mix", "Off", "Off", "Lobby Mix", "Lobby Mix"]),
    ("Bluetooth", "Bluetooth", "bluetooth", ["Bluetooth", "Off", "Off", "Bluetooth", "Bluetooth"]),
    ("All Audio Off", "All Audio\nOff", "mute", ["Off"] * 5),
]
HOLD_MS = 1500        # door front key
IPAD_HOLD_MS = 1000   # rack iPad Mode key
IDLE_MS = 30000       # door returns to its front screen
AFTER_PRESS_MS = 5000 # door returns after a choice

COLORS = {  # category: resting background, active background
    "light": (0x3A2A08, 0xC77700),
    "audio": (0x0D2A45, 0x1673C8),
    "music": (0x241A45, 0x6A40D0),
    "nav": (0x23272D, 0x4A5361),
    "off": (0x401515, 0xB33A2E),
    "ipad": (0x2E1A47, 0x8E3FC9),
    "status": (0x101418, 0x101418),
    "lcd": (0x101418, 0x101418),
}
WHITE, GREY, LOCKED_BG = 0xFFFFFF, 0x6B7380, 0x14171B

# ---------------------------------------------------------------- entities
_counter = [0]


def nid():
    _counter[0] += 1
    return f"e{_counter[0]:05d}"


def val(v):
    return {"isExpression": False, "value": v}


def expr(s):
    return {"isExpression": True, "value": s}


def wrap(o):
    return {k: (v if isinstance(v, dict) and "isExpression" in v else val(v)) for k, v in o.items()}


def action(conn, definition, children=None, **options):
    e = {"type": "action", "id": nid(), "definitionId": definition, "connectionId": conn,
         "options": wrap(options)}
    if children:
        e["children"] = children
    return e


def press(loc):
    return action("internal", "button_pressrelease", location=loc, force=True, duration=0)


def wait(ms):
    return action("internal", "wait", time=expr(str(ms)))


def setvar(name, value):
    return action("internal", "custom_variable_set_value", name=name, create=False, value=str(value))


def setpage(n):
    return action("internal", "set_page", surfaceId="self", page=n)


def check(expression):
    return {"type": "feedback", "id": nid(), "definitionId": "check_expression",
            "connectionId": "internal", "options": {"expression": expr(expression)}}


def when(expression, then, otherwise=None):
    return action("internal", "logic_if", children={
        "condition": [check(expression)], "actions": then, "else_actions": otherwise or []})


def osc(path):
    return action("splay", "send_blank", path=path)


def wiim(command):
    return action("wiim", "get", url=f"httpapi.asp?command={command}", header="",
                  jsonResultDataVariable="", result_stringify=True, statusCodeVariable="")


def wing_send(src, mx, on):
    return action("wing", "set-send-mute", src=src, dest=f"/mtx/{mx}", mainDest=f"/mtx/{mx}",
                  mute="0" if on else "1")


def wing_mute(mx, muted):
    return action("wing", "set-mute", sel=f"/mtx/{mx}", mute="1" if muted else "0")


FADE = dict(fadeDuration=0, fadeAlgorithm="linear", fadeType="ease-in-out")


def wing_level(mx, db):
    return action("wing", "set-fader", sel=f"/mtx/{mx}", level=db, **FADE)


def wing_delta(mx, db):
    return action("wing", "fader-delta", sel=f"/mtx/{mx}", delta=db, **FADE)


# ---------------------------------------------------------------- pages
@dataclass
class Key:
    page: int
    row: int
    col: int
    label: str = ""
    icon: str | None = None
    cat: str = "nav"
    down: list = field(default_factory=list)
    hold: tuple | None = None        # (ms, actions)
    left: list | None = None
    right: list | None = None
    fb: list = field(default_factory=list)  # (expression, style)
    does: str = ""
    size: int = 14
    align: str = "center:bottom"
    art: str | None = None           # raw image name, for door front tiles

    @property
    def loc(self):
        return f"{self.page}/{self.row}/{self.col}"


PAGES = {
    1: ("Door Front", "door"), 2: ("Door Lights", "door"), 3: ("Door Audio", "door"),
    4: ("Rack Home", "rack"), 5: ("Rack Music", "rack"),
    6: ("Rack Lights A", "rack"), 7: ("Rack Lights B", "rack"),
    8: ("Zone Mains", "rack"), 9: ("Zone Outdoor", "rack"), 10: ("Zone Soffit", "rack"),
    11: ("Zone Bathrooms", "rack"), 12: ("Zone Vestibule", "rack"),
    20: ("Library Zones 1-4", "library"), 21: ("Library Zone 5, Lights, Music", "library"),
}
BOUNDS = {"door": (3, 5), "rack": (4, 4), "library": (4, 8)}
KEYS: dict[str, Key] = {}


def add(page, row, col, **kw):
    k = Key(page, row, col, **kw)
    assert k.loc not in KEYS, k.loc
    KEYS[k.loc] = k
    return k


def zone_block(z, s):
    """Library location of a zone/source block. s 0-3 is a source, 4 is Off."""
    return f"20/{z - 1}/{s}" if z <= 4 else f"21/0/{s}"


LIGHT = {n: f"21/1/{n - 1}" for n, *_ in PRESETS}
ALL_OFF, IPAD_TOGGLE, MUSIC_STOP = "21/2/0", "21/2/1", "21/2/2"
DEFAULT_LEVELS, MUSIC_PLAY, MUSIC_START = "21/0/5", "21/0/6", "21/0/7"
PLAYLIST_LOC = {n: f"21/2/{n + 2}" for n, _ in PLAYLISTS}
SCENE_LOC = {s[0]: f"21/3/{i}" for i, s in enumerate(SCENES)}

PRESETS_MODE = "$(custom:light_mode) == 'presets'"
IPAD_MODE = "$(custom:light_mode) == 'ipad'"
NONE_PLAYLIST = " && ".join(f"$(custom:z{z}_src) != 'Playlist'" for z, *_ in ZONES)
ANY_PLAYLIST = " || ".join(f"$(custom:z{z}_src) == 'Playlist'" for z, *_ in ZONES)
LOCKED = {"bgcolor": LOCKED_BG, "color": GREY}


def active(cat):
    return {"bgcolor": COLORS[cat][1], "color": WHITE}


def scene_expr(zones):
    return " && ".join(f"$(custom:z{i + 1}_src) == '{s}'" for i, s in enumerate(zones))


def build_library():
    for z, name, mx, _, _, _ in ZONES:
        for s, (source, _, _, icon) in enumerate(SOURCES):
            acts = [wing_send(src, mx, src == SOURCES[s][1]) for _, src, _, _ in SOURCES]
            acts += [wing_mute(mx, False), setvar(f"z{z}_src", source)]
            add(*map(int, zone_block(z, s).split("/")), label=f"Z{z}\n{source}", icon=icon,
                cat="audio", down=acts, size=12, does=f"{name} plays {source}")
        add(*map(int, zone_block(z, 4).split("/")), label=f"Z{z}\nOff", icon="mute", cat="off",
            down=[wing_mute(mx, True), setvar(f"z{z}_src", "Off")], size=12, does=f"{name} off")
    add(21, 0, 5, label="Default\nLevels", icon="sliders", size=12, does="Resets every zone fader",
        down=[wing_level(mx, db) for _, _, mx, db, _, _ in ZONES])
    add(21, 0, 6, label="Music\nPlay", icon="note", cat="music", size=12,
        does="Starts the chosen playlist, then turns on shuffle and repeat",
        down=[wiim("MCUKeyShortClick:$(custom:music_n)"), wait(2000), wiim("setPlayerCmd:loopmode:2")])
    add(21, 0, 7, label="Music\nStart", icon="note", cat="music", size=12,
        does="Starts music only if nothing is already playing it",
        down=[when(NONE_PLAYLIST, [press(MUSIC_PLAY)])])
    for n, name, _, icon in PRESETS:
        add(21, 1, n - 1, label=f"L{n}\n{name}", icon=icon, cat="light", size=12,
            does=f"Plays the {name} look, unless iPad Mode is on",
            down=[when(PRESETS_MODE, [osc(f"/lobby/preset/{n}"), setvar("light_preset", name),
                                      setvar("light_preset_n", n)])])
    add(21, 2, 0, label="All Off", icon="power", cat="off", size=12,
        does="Stops all looks, unless iPad Mode is on",
        down=[when(PRESETS_MODE, [osc("/lobby/off"), setvar("light_preset", "Off"),
                                  setvar("light_preset_n", 0)])])
    add(21, 2, 1, label="iPad\nToggle", icon="tablet", cat="ipad", size=12,
        does="Hands lighting to the iPad, or takes it back",
        down=[when(PRESETS_MODE, [osc("/lobby/off"), setvar("light_mode", "ipad")], [
            setvar("light_mode", "presets"),
            when("$(custom:light_preset_n) != '0'", [osc("/lobby/preset/$(custom:light_preset_n)")]),
        ])])
    add(21, 2, 2, label="Music\nStop", icon="mute", cat="music", size=12,
        does="Stops the player once no zone is using it",
        down=[when(NONE_PLAYLIST, [wiim("setPlayerCmd:stop")])])
    for n, name in PLAYLISTS:
        add(21, 2, n + 2, label=f"P{n}\n{name}", icon="note", cat="music", size=12,
            does=f"Chooses {name}. Plays it now, or starts Music Inside if the room is silent",
            down=[setvar("music_n", n), setvar("music_name", name), wait(50),
                  when(ANY_PLAYLIST, [press(MUSIC_PLAY)], [press(SCENE_LOC["Music Inside"])])])
    for i, (name, label, icon, zones) in enumerate(SCENES):
        uses_music = "Playlist" in zones
        acts = [press(MUSIC_START), wait(50)] if uses_music else []
        for z, source in enumerate(zones, 1):
            s = [x[0] for x in SOURCES].index(source) if source != "Off" else 4
            acts.append(press(zone_block(z, s)))
        acts.append(press(DEFAULT_LEVELS))
        if not uses_music:
            acts += [wait(200), press(MUSIC_STOP)]
        add(21, 3, i, label=f"Room\n{name}", icon=icon, cat="off" if name == "All Audio Off" else "audio",
            size=12, down=acts, does="Sets all five zones and their default levels")


def nav(page, row, col, target, label, icon, does=None):
    return add(page, row, col, label=label, icon=icon, down=[setpage(target)],
               does=does or f"Opens {PAGES[target][0]}")


def build_doors():
    # Page 1, front screen: artwork, status, and one hold key
    for r in range(3):
        for c in range(5):
            if (r, c) not in ((2, 1), (2, 3)):
                add(1, r, c, art=f"front-{r}-{c}", cat="status", does="Artwork, no action")
    add(1, 2, 1, label="Lights\n$(custom:light_preset)", cat="status", align="center:center", size=14,
        does="Shows the current look",
        fb=[(IPAD_MODE, {"text": "iPad in\ncontrol", "bgcolor": COLORS["ipad"][1], "color": WHITE})])
    add(1, 2, 3, label="Hold for\nlights", icon="hand", cat="light", size=14,
        does="Hold 1.5 seconds to open Door Lights. Returns here after 30 seconds. Does nothing in iPad Mode",
        hold=(HOLD_MS, [when(PRESETS_MODE, [setpage(2), wait(IDLE_MS), setpage(1)])]),
        fb=[(IPAD_MODE, {"text": "Locked", "bgcolor": LOCKED_BG, "color": GREY})])
    # Page 2, lights
    spots = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2)]
    for (r, c), (n, name, label, icon) in zip(spots, PRESETS):
        add(2, r, c, label=label, icon=icon, cat="light", does=f"Plays {name}, then returns to the front screen",
            down=[press(LIGHT[n]), wait(AFTER_PRESS_MS), setpage(1)],
            fb=[(f"$(custom:light_preset_n) == '{n}'", active("light")), (IPAD_MODE, LOCKED)])
    add(2, 2, 0, label="All Off", icon="power", cat="off", does="Stops all looks, then returns to the front screen",
        down=[press(ALL_OFF), wait(AFTER_PRESS_MS), setpage(1)],
        fb=[("$(custom:light_preset_n) == '0'", active("off")), (IPAD_MODE, LOCKED)])
    nav(2, 2, 3, 3, "Audio", "speaker")
    nav(2, 2, 4, 1, "Back", "back", "Returns to the front screen")
    # Page 3, audio
    for c, (name, label, cat) in enumerate([("Sunday Feed", "Sunday\nFeed", "audio"),
                                            ("Music Inside", "Music", "music"),
                                            ("Lobby Event", "Lobby\nEvent", "audio")]):
        icon = {"Sunday Feed": "church", "Music Inside": "note", "Lobby Event": "mic"}[name]
        add(3, 0, c, label=label, icon=icon, cat=cat, does=f"Runs {name}, then returns to the front screen",
            down=[press(SCENE_LOC[name]), wait(AFTER_PRESS_MS), setpage(1)],
            fb=[(scene_expr(dict((s[0], s[3]) for s in SCENES)[name]), active(cat))])
    add(3, 0, 4, label="All Audio\nOff", icon="mute", cat="off",
        does="Turns off every zone, then returns to the front screen",
        down=[press(SCENE_LOC["All Audio Off"]), wait(AFTER_PRESS_MS), setpage(1)],
        fb=[(scene_expr(["Off"] * 5), active("off"))])
    nav(3, 2, 3, 2, "Lights", "bulb")
    nav(3, 2, 4, 1, "Back", "back", "Returns to the front screen")


def dial(page, col, zone):
    z, name, mx, _, zpage, _ = zone
    add(page, 2, col, label=f"{name}\n$(wing:mtx{mx}_level) dB", cat="lcd", align="center:center", size=14,
        does=f"Touch strip: shows the {name} level, or Off",
        fb=[(f"$(custom:z{z}_src) == 'Off'", {"text": f"{name}\nOff", "bgcolor": LOCKED_BG, "color": GREY})])
    add(page, 3, col, label=f"Dial\n{name}", cat="nav",
        does=f"Turn for {name} volume, 1 dB per click, stopping at 0 dB and -60 dB. Press to open {PAGES[zpage][0]}",
        down=[setpage(zpage)],
        left=[when(f"$(wing:mtx{mx}_level) > -60", [wing_delta(mx, -1)])],
        right=[when(f"$(wing:mtx{mx}_level) < 0", [wing_delta(mx, 1)])])


def build_rack():
    home_dials = [ZONES[0], ZONES[1], ZONES[2], ZONES[4]]
    scenes = {s[0]: s for s in SCENES}

    def scene_key(page, r, c, name, label=None, cat="audio"):
        s = scenes[name]
        add(page, r, c, label=label or s[1], icon=s[2], cat=cat, does=f"Runs {name} on all five zones",
            down=[press(SCENE_LOC[name])], fb=[(scene_expr(s[3]), active(cat))])

    # Page 4, home
    scene_key(4, 0, 0, "Sunday Feed")
    add(4, 0, 1, label="Music", icon="note", cat="music",
        does="Runs Music Inside if the room is not already on music, then opens Rack Music",
        down=[when(NONE_PLAYLIST, [press(SCENE_LOC["Music Inside"])]), setpage(5)],
        fb=[(ANY_PLAYLIST, active("music"))])
    scene_key(4, 0, 2, "Lobby Event")
    scene_key(4, 0, 3, "Bluetooth")
    scene_key(4, 1, 0, "All Audio Off", cat="off")
    nav(4, 1, 1, 8, "Zones", "sliders", "Opens the first zone page")
    add(4, 1, 2, label="Lights", icon="bulb", cat="light", does="Opens Rack Lights A", down=[setpage(6)],
        fb=[(IPAD_MODE, {"text": "iPad\nLights", "bgcolor": COLORS["ipad"][1], "color": WHITE})])
    ipad_key(4, 1, 3)
    for c, zone in enumerate(home_dials):
        dial(4, c, zone)
    # Page 5, music
    for n, name in PLAYLISTS:
        add(5, 0, n - 1, label=name, icon="note", cat="music", does=f"Chooses and plays {name}",
            down=[press(PLAYLIST_LOC[n])],
            fb=[(f"$(custom:music_n) == '{n}' && ({ANY_PLAYLIST})", active("music"))])
    scene_key(5, 1, 0, "Music Inside", "Inside", "music")
    scene_key(5, 1, 1, "Music Everywhere", "Every-\nwhere", "music")
    scene_key(5, 1, 2, "All Audio Off", cat="off")
    nav(5, 1, 3, 4, "Home", "home")
    for c, zone in enumerate(home_dials):
        dial(5, c, zone)
    # Pages 6 and 7, lights
    spots = {1: (6, 0, 0), 2: (6, 0, 1), 3: (6, 0, 2), 4: (6, 0, 3), 5: (6, 1, 0),
             6: (7, 0, 0), 7: (7, 0, 1), 8: (7, 0, 2)}
    for n, name, label, icon in PRESETS:
        add(*spots[n], label=label, icon=icon, cat="light", does=f"Plays {name}", down=[press(LIGHT[n])],
            fb=[(f"$(custom:light_preset_n) == '{n}'", active("light")), (IPAD_MODE, LOCKED)])
    for p, c in ((6, 1), (7, 1)):
        add(p, 1, c, label="All Off", icon="power", cat="off", does="Stops all looks", down=[press(ALL_OFF)],
            fb=[("$(custom:light_preset_n) == '0'", active("off")), (IPAD_MODE, LOCKED)])
    nav(6, 1, 2, 7, "More", "next")
    nav(6, 1, 3, 4, "Home", "home")
    ipad_key(7, 0, 3)
    nav(7, 1, 2, 6, "Back", "back")
    nav(7, 1, 3, 4, "Home", "home")
    for p in (6, 7):
        add(p, 2, 0, label="Lights\n$(custom:light_preset)", cat="lcd", align="center:center",
            does="Touch strip: shows the current look",
            fb=[(IPAD_MODE, {"text": "iPad in\ncontrol", "bgcolor": COLORS["ipad"][1], "color": WHITE})])
    # Pages 8 to 12, zones
    for i, zone in enumerate(ZONES):
        z, name, mx, _, page, icon = zone
        for s, (source, _, label, sicon) in enumerate(SOURCES):
            if source == "Playlist":
                acts = [press(MUSIC_START), wait(50), press(zone_block(z, s))]
            else:
                acts = [press(zone_block(z, s)), wait(200), press(MUSIC_STOP)]
            add(page, 0, s, label=label, icon=sicon, cat="audio", does=f"{name} plays {source}", down=acts,
                fb=[(f"$(custom:z{z}_src) == '{source}'", active("audio"))])
        add(page, 1, 0, label=f"{name}\nOff", icon="mute", cat="off", does=f"Turns off {name}",
            down=[press(zone_block(z, 4)), wait(200), press(MUSIC_STOP)],
            fb=[(f"$(custom:z{z}_src) == 'Off'", active("off"))])
        prev_z, next_z = ZONES[(i - 1) % 5], ZONES[(i + 1) % 5]
        nav(page, 1, 1, prev_z[4], "Prev\nZone", "prev", f"Opens {prev_z[1]}")
        nav(page, 1, 2, next_z[4], "Next\nZone", "next", f"Opens {next_z[1]}")
        nav(page, 1, 3, 4, "Home", "home")
        dial(page, 0, zone)
        add(page, 2, 1, label=f"Source\n$(custom:z{z}_src)", cat="lcd", align="center:center",
            does="Touch strip: shows this zone's source")


def ipad_key(page, r, c):
    add(page, r, c, label="iPad\nMode", icon="tablet", cat="ipad",
        does="Hold 1 second to hand lighting to the iPad, or to take it back",
        hold=(IPAD_HOLD_MS, [press(IPAD_TOGGLE)]),
        fb=[(IPAD_MODE, {"text": "iPad\nMode ON", "bgcolor": COLORS["ipad"][1], "color": WHITE})])


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
    trigger("startup_recovery", "Startup recovery", 0, True, "startup", {"delay": 60000}, [
        when(PRESETS_MODE, [
            when("$(custom:light_preset_n) != '0'", [osc("/lobby/preset/$(custom:light_preset_n)")],
                 [osc("/lobby/off")])])],
        does="Sixty seconds after Companion starts, replays the last look. Leaves the lights alone in iPad Mode")
    trigger("schedule_sunday", "Schedule: Sunday arrival", 1, False, "timeofday",
            {"time": "07:30:00", "days": [0]},
            [press(LIGHT[1]), press(SCENE_LOC["Sunday Feed"])], PRESETS_MODE,
            does="Off at first. Sunday 7:30: Sunday Morning lights and Sunday Feed, unless iPad Mode is on")
    trigger("schedule_weekday", "Schedule: Weekday open", 2, False, "timeofday",
            {"time": "08:00:00", "days": [1, 2, 3, 4, 5]},
            [press(LIGHT[2]), press(SCENE_LOC["Music Inside"])], PRESETS_MODE,
            does="Off at first. Weekdays 8:00: Everyday lights and Music Inside, unless iPad Mode is on")
    trigger("schedule_night", "Schedule: Night shutdown", 3, False, "timeofday",
            {"time": "22:00:00", "days": [0, 1, 2, 3, 4, 5, 6]},
            [setvar("light_mode", "presets"), wait(50), press(ALL_OFF), press(SCENE_LOC["All Audio Off"])],
            does="Off at first. Nightly 22:00: leaves iPad Mode so doors can't stay locked, then all off")


VARIABLES = {  # name: (description, default)
    "light_mode": ("presets or ipad", "presets"),
    "light_preset": ("Name of the current look", "Everyday"),
    "light_preset_n": ("Number of the current look, 0 for off", "2"),
    "music_n": ("Number of the chosen playlist", "1"),
    "music_name": ("Name of the chosen playlist", "Morning"),
    **{f"z{z}_src": (f"{name} source, or Off", "Off") for z, name, *_ in ZONES},
}

# ---------------------------------------------------------------- icons
_S = 'fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
GLYPHS = {
    "sunrise": '<path d="M3 19h18M7 19a5 5 0 0 1 10 0M12 6v3M5 11.5l2 2M19 11.5l-2 2M12 3.5l-2 2M12 3.5l2 2"/>',
    "sunset": '<path d="M3 19h18M7 19a5 5 0 0 1 10 0M12 3v6M9 6.5 12 9.5 15 6.5M5 12.5l2 2M19 12.5l-2 2"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h2M14 14h2"/>',
    "sun": '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3 7 7M17 17l1.7 1.7M5.3 18.7 7 17M17 7l1.7-1.7"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20v-1a6.5 6.5 0 0 1 13 0v1M16 4.7a3.5 3.5 0 0 1 0 6.6M18 13.2a6.5 6.5 0 0 1 3.5 5.8v1"/>',
    "steps": '<ellipse cx="8" cy="7.5" rx="2.6" ry="4"/><path d="M6 14.5h4"/><ellipse cx="16" cy="12.5" rx="2.6" ry="4"/><path d="M14 19.5h4"/>',
    "star": '<path d="M12 3l2.7 5.9 6.3.8-4.6 4.4 1.2 6.4L12 17l-5.6 3.5 1.2-6.4L3 9.7l6.3-.8z"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4 7 7 0 0 0 20 14.5z"/><path d="M17 3.5v3M15.5 5h3"/>',
    "power": '<path d="M12 3v9M6.3 6.8a8 8 0 1 0 11.4 0"/>',
    "hand": '<path d="M9 12V5a1.5 1.5 0 0 1 3 0v6M12 10.5a1.5 1.5 0 0 1 3 0V12M15 11.5a1.5 1.5 0 0 1 3 0V16a6 6 0 0 1-6 6h-1a6 6 0 0 1-5-2.7L3.7 15.2a1.5 1.5 0 0 1 2.4-1.8L9 15.5"/>',
    "bulb": '<path d="M9.5 18h5M10.5 21h3M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>',
    "speaker": '<path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5zM15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>',
    "mute": '<path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5zM16 9.5l5 5M21 9.5l-5 5"/>',
    "back": '<path d="M10 6l-6 6 6 6M4 12h16"/>',
    "prev": '<path d="M15 5l-7 7 7 7"/>',
    "next": '<path d="M9 5l7 7-7 7"/>',
    "home": '<path d="M3 11.5 12 4l9 7.5M5.5 10v10h13V10M10 20v-6h4v6"/>',
    "note": '<path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    "church": '<path d="M12 2v5M10 4h4M12 7l7 5v9H5v-9zM10 21v-5a2 2 0 0 1 4 0v5"/>',
    "bluetooth": '<path d="M7 7l10 10-5 5V2l5 5L7 17"/>',
    "mic": '<rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3M9 21h6"/>',
    "tablet": '<rect x="5" y="2.5" width="14" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "sliders": '<path d="M6 4v6M6 14v6M12 4v2M12 10v10M18 4v10M18 18v2M3.5 12h5M9.5 8h5M15.5 16h5"/>',
    "tree": '<path d="M12 3l5.5 7H15l4 6H5l4-6H6.500zM12 16v5"/>',
    "soffit": '<path d="M2 12 12 4l10 8M5 14.500h14M9 14.500v2a3 3 0 0 0 6 0v-2"/>',
    "restroom": '<circle cx="7" cy="5" r="2"/><path d="M7 8.500v6.500M4.500 11h5M7 15l-2 6M7 15l2 6M12 3v18"/><circle cx="17" cy="5" r="2"/><path d="M17 8.500 14 16h6zM15.500 16v5M18.500 16v5"/>',
    "door": '<path d="M6 21V3h12v18M3 21h18M14.500 12v.01"/>',
    "broadcast": '<path d="M12 12v.01M8.500 8.500a5 5 0 0 0 0 7M15.500 8.500a5 5 0 0 1 0 7M5.600 5.600a9 9 0 0 0 0 12.800M18.400 5.600a9 9 0 0 1 0 12.800"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
}
ART = """<svg xmlns="http://www.w3.org/2000/svg" width="720" height="432" viewBox="0 0 720 432">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#14233f"/><stop offset=".55" stop-color="#7a4a5e"/><stop offset=".85" stop-color="#e8934a"/>
<stop offset="1" stop-color="#ffc56b"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe6a8" stop-opacity=".9"/>
<stop offset="1" stop-color="#ffc56b" stop-opacity="0"/></radialGradient></defs>
<rect width="720" height="432" fill="url(#sky)"/><circle cx="360" cy="222" r="250" fill="url(#glow)"/>
<circle cx="360" cy="222" r="58" fill="#fff3cf"/>
<path d="M0 330C110 290 220 275 330 300S560 345 720 285V432H0z" fill="#3b2a3f"/>
<path d="M0 385C150 335 270 345 380 365S610 395 720 350V432H0z" fill="#1c1626"/></svg>"""


def icon_svg(name):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="144" height="144" viewBox="0 0 144 144">'
            f'<g transform="translate(35,5) scale(3.1)" {_S}>{GLYPHS[name]}</g></svg>')


def browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/usr/bin/google-chrome", "/usr/bin/chromium"):
        if os.path.exists(p):
            return p
    sys.exit("Chrome or Edge is needed to draw the icons.")


def chrome(profile, *args):
    return subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-first-run",
                           "--hide-scrollbars", f"--user-data-dir={profile}", *args],
                          capture_output=True, text=True, timeout=120)


def render_icons(profile, tmp):
    ICONS.mkdir(exist_ok=True)
    sources = {name: icon_svg(name) for name in GLYPHS}
    for name, svg in sources.items():
        (ICONS / f"{name}.svg").write_text(svg + "\n", encoding="utf-8")
    (ICONS / "front-art.svg").write_text(ART, encoding="utf-8")
    page = tmp / "render.html"
    page.write_text("""<!doctype html><pre id="out"></pre><script>
const icons=%s, art=%s;
const load=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);
  i.src='data:image/svg+xml;base64,'+btoa(s)});
(async()=>{const out={};
for(const [n,s] of Object.entries(icons)){const c=document.createElement('canvas');c.width=c.height=144;
  c.getContext('2d').drawImage(await load(s),0,0);out[n]=c.toDataURL('image/png').split(',')[1]}
const a=await load(art);
for(let r=0;r<3;r++)for(let k=0;k<5;k++){const c=document.createElement('canvas');c.width=c.height=144;
  c.getContext('2d').drawImage(a,k*144,r*144,144,144,0,0,144,144);
  out['front-'+r+'-'+k]=c.toDataURL('image/png').split(',')[1]}
document.getElementById('out').textContent=JSON.stringify(out)})();
</script>""" % (json.dumps(sources), json.dumps(ART)), encoding="utf-8")
    result = chrome(profile, "--virtual-time-budget=10000", "--dump-dom", page.as_uri())
    match = re.search(r'<pre id="out">(.*?)</pre>', result.stdout, re.S)
    if not match or not match.group(1):
        sys.exit("Icon rendering failed:\n" + result.stderr[-600:])
    images = json.loads(match.group(1))
    for name, data in images.items():
        (ICONS / f"{name}.png").write_bytes(base64.b64decode(data))
    return images


# ---------------------------------------------------------------- the file
def button(key, images):
    style = {"text": key.label, "textExpression": False, "size": key.size, "alignment": key.align,
             "pngalignment": "center:center", "color": WHITE, "bgcolor": COLORS[key.cat][0],
             "show_topbar": False, "png64": images.get(key.art or key.icon) if (key.art or key.icon) else None}
    feedbacks = []
    for expression, s in key.fb:
        f = check(expression)
        f["style"] = dict(s)
        f["isInverted"] = val(False)
        if s.get("bgcolor") == LOCKED_BG and key.icon:
            f["style"]["png64"] = images["lock"]
        feedbacks.append(f)
    sets = {"down": key.down, "up": []}
    options = {"runWhileHeld": []}
    if key.hold:
        sets[str(key.hold[0])] = key.hold[1]
        options["runWhileHeld"] = [key.hold[0]]
    rotary = key.left is not None
    if rotary:
        sets["rotate_left"], sets["rotate_right"] = key.left, key.right
    return {"type": "button", "options": {"stepProgression": "auto", "rotaryActions": rotary},
            "style": style, "feedbacks": feedbacks,
            "steps": {"0": {"action_sets": sets, "options": options}}, "localVariables": []}


def export(images):
    pages = {}
    for number, (name, _) in PAGES.items():
        controls = {}
        for key in KEYS.values():
            if key.page == number:
                controls.setdefault(str(key.row), {})[str(key.col)] = button(key, images)
        pages[str(number)] = {"name": name, "controls": controls,
                              "gridSize": {"minColumn": 0, "maxColumn": 7, "minRow": 0, "maxRow": 3}}
    return {
        "version": 12, "type": "full", "companionBuild": "suncrest-build-script",
        "pages": pages,
        "triggers": {k: v["control"] for k, v in TRIGGERS.items()}, "triggerCollections": [],
        "custom_variables": {name: {"description": d, "defaultValue": v, "persistCurrentValue": True,
                                    "sortOrder": i} for i, (name, (d, v)) in enumerate(VARIABLES.items())},
        "customVariablesCollections": [], "connectionCollections": [],
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
            "splay": {"label": "splay", "moduleId": "generic-osc", "enabled": True, "isFirstInit": False,
                      "lastUpgradeIndex": 3, "sortOrder": 1, "updatePolicy": "stable",
                      "config": {"host": SPLAY_IP, "targetPort": 8000, "protocol": "udp", "listen": False,
                                 "feedbackPort": "8001"}},
            "wiim": {"label": "wiim", "moduleId": "generic-http", "enabled": True, "isFirstInit": False,
                     "lastUpgradeIndex": 3, "sortOrder": 2, "updatePolicy": "stable",
                     "config": {"prefix": f"https://{WIIM_IP}/", "proxyAddress": "", "authType": "none",
                                "authUser": "", "authPassword": "", "rejectUnauthorized": False,
                                "insecureHTTPParser": False}},
        },
    }


# ---------------------------------------------------------------- checks
ALLOWED = {  # (connection, definition): option names, taken from the module and Companion source
    ("internal", "button_pressrelease"): {"location", "force", "duration"},
    ("internal", "custom_variable_set_value"): {"name", "create", "value"},
    ("internal", "set_page"): {"surfaceId", "page"},
    ("internal", "wait"): {"time"},
    ("internal", "logic_if"): set(),
    ("internal", "check_expression"): {"expression"},
    ("wing", "set-send-mute"): {"src", "dest", "mainDest", "mute"},
    ("wing", "set-mute"): {"sel", "mute"},
    ("wing", "set-fader"): {"sel", "level", *FADE},
    ("wing", "fader-delta"): {"sel", "delta", *FADE},
    ("splay", "send_blank"): {"path"},
    ("wiim", "get"): {"url", "header", "jsonResultDataVariable", "result_stringify", "statusCodeVariable"},
}


def walk(entities):
    for e in entities:
        yield e
        for group in e.get("children", {}).values():
            yield from walk(group)


def all_entity_lists():
    for k in KEYS.values():
        yield k.loc, k.down
        yield k.loc, [check(x) for x, _ in k.fb]
        for extra in (k.left, k.right, k.hold[1] if k.hold else None):
            if extra:
                yield k.loc, extra
    for tid, t in TRIGGERS.items():
        yield tid, t["control"]["actions"]
        yield tid, t["control"]["condition"]


def validate():
    errors, ids = [], set()
    for k in KEYS.values():
        rows, cols = BOUNDS[PAGES[k.page][1]]
        if k.row >= rows or k.col >= cols:
            errors.append(f"{k.loc} is outside its surface")
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
            if not all(isinstance(v, dict) and "isExpression" in v for v in e["options"].values()):
                errors.append(f"{where}: unwrapped option on {spec}")
            if e["definitionId"] == "button_pressrelease" and e["options"]["location"]["value"] not in KEYS:
                errors.append(f"{where}: press target {e['options']['location']['value']} is missing")
            if e["definitionId"] == "set_page" and e["options"]["page"]["value"] not in PAGES:
                errors.append(f"{where}: page {e['options']['page']['value']} is missing")
            for option in e["options"].values():
                text = str(option["value"])
                for name in re.findall(r"\$\(custom:(\w+)\)", text):
                    if name not in VARIABLES:
                        errors.append(f"{where}: unknown variable {name}")
            if e["definitionId"] == "custom_variable_set_value" and e["options"]["name"]["value"] not in VARIABLES:
                errors.append(f"{where}: sets unknown variable")
    for k in KEYS.values():
        for name in re.findall(r"\$\(custom:(\w+)\)", k.label):
            if name not in VARIABLES:
                errors.append(f"{k.loc}: label uses unknown variable {name}")
    return errors


class Sim:
    """Walks the actions the way Companion would, and records what reaches the hardware."""

    def __init__(self):
        self.vars = {n: v for n, (_, v) in VARIABLES.items()}
        self.levels = {mx: -6.0 for mx in range(1, 6)}
        self.sends, self.mutes, self.log, self.page = {}, {}, [], 1

    def text(self, s):
        return re.sub(r"\$\(custom:(\w+)\)", lambda m: self.vars[m.group(1)], str(s))

    def truth(self, expression):
        s = re.sub(r"\$\(custom:(\w+)\)", lambda m: repr(self.vars[m.group(1)]), expression)
        s = re.sub(r"\$\(wing:mtx(\d)_level\)", lambda m: str(self.levels[int(m.group(1))]), s)
        return bool(eval(s.replace("&&", " and ").replace("||", " or ")))

    def run(self, actions):
        for a in actions:
            o = {k: v["value"] for k, v in a["options"].items()}
            d = a["definitionId"]
            if d == "button_pressrelease":
                self.run(KEYS[o["location"]].down)
            elif d == "logic_if":
                chosen = all(self.truth(c["options"]["expression"]["value"]) for c in a["children"]["condition"])
                self.run(a["children"]["actions" if chosen else "else_actions"])
            elif d == "custom_variable_set_value":
                self.vars[o["name"]] = self.text(o["value"])
            elif d == "set_page":
                self.page = o["page"]
            elif d == "send_blank":
                self.log.append(("osc", self.text(o["path"])))
            elif d == "get":
                self.log.append(("wiim", self.text(o["url"]).split("=", 1)[1]))
            elif d == "set-send-mute":
                self.sends[(o["src"], o["dest"])] = o["mute"] == "0"
            elif d == "set-mute":
                self.mutes[o["sel"]] = o["mute"] == "1"
            elif d == "set-fader":
                self.levels[int(o["sel"][-1])] = float(o["level"])
            elif d == "fader-delta":
                self.levels[int(o["sel"][-1])] += float(o["delta"])

    def press(self, loc, held=False):
        key = KEYS[loc]
        self.run(key.hold[1] if held else key.down)

    def hears(self, z):
        """The one source a zone hears, from the Wing state rather than the variables."""
        mx = f"/mtx/{ZONES[z - 1][2]}"
        if self.mutes.get(mx, True):
            return "Off"
        on = [name for name, src, _, _ in SOURCES if self.sends.get((src, mx))]
        assert len(on) == 1, (z, on)
        return on[0]


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
            s.press(SCENE_LOC["Sunday Feed"])
            before = [s.hears(i) for i in range(1, 6)]
            s.press(f"{ZONES[z - 1][4]}/0/{s_index}")
            before[z - 1] = source
            ok(f"{name} on {source}", [s.hears(i) for i in range(1, 6)] == before)
    # Lights
    for n, name, *_ in PRESETS:
        s = Sim()
        door = next(k for k in KEYS.values() if k.page == 2 and k.icon == PRESETS[n - 1][3])
        s.page = 2
        s.press(door.loc)
        ok(f"door preset {n}", s.log == [("osc", f"/lobby/preset/{n}")] and s.vars["light_preset"] == name
           and s.page == 1)
    s = Sim()
    s.press("1/2/3", held=True)
    ok("hold opens lights, then idle return", s.page == 1)
    # iPad Mode locks doors, rack presets and the hold key, then restores
    s = Sim()
    s.press(LIGHT[3])
    s.log.clear()
    s.press("4/1/3", held=True)
    ok("iPad Mode stops presets", s.log == [("osc", "/lobby/off")] and s.vars["light_mode"] == "ipad")
    s.log.clear()
    s.page = 1
    s.press("2/0/0")
    s.press("2/2/0")
    s.press("6/0/0")
    ok("presets locked in iPad Mode", s.log == [])
    s.page = 1
    s.run(KEYS["1/2/3"].hold[1])
    ok("front key locked in iPad Mode", s.page == 1)
    s.press("7/0/3", held=True)
    ok("leaving restores the last look", s.log == [("osc", "/lobby/preset/3")] and s.vars["light_mode"] == "presets")
    s = Sim()
    s.press(ALL_OFF)
    s.press("4/1/3", held=True)
    s.log.clear()
    s.press("4/1/3", held=True)
    ok("leaving after All Off stays dark", s.log == [])
    # Music starts once, stops when unused, and survives zone changes
    start = ("wiim", "MCUKeyShortClick:1")
    s = Sim()
    s.press(SCENE_LOC["Music Inside"])
    ok("music starts once", s.log.count(start) == 1)
    s.log.clear()
    s.press(SCENE_LOC["Music Everywhere"])
    ok("no restart when already playing", start not in s.log)
    s.log.clear()
    s.press(SCENE_LOC["Sunday Feed"])
    ok("music stops when unused", ("wiim", "setPlayerCmd:stop") in s.log)
    s = Sim()
    s.press("4/0/1")
    ok("Music from silence plays Inside and opens the page",
       s.vars["z1_src"] == "Playlist" and s.vars["z2_src"] == "Off" and s.log.count(start) == 1 and s.page == 5)
    s.press(SCENE_LOC["Music Everywhere"])
    s.press("4/0/1")
    ok("Music does not cut back an Everywhere room", s.vars["z2_src"] == "Playlist" and s.page == 5)
    s = Sim()
    s.press("5/0/1")
    ok("playlist key in a silent room starts Inside",
       s.vars["z1_src"] == "Playlist" and ("wiim", "MCUKeyShortClick:2") in s.log
       and s.vars["z2_src"] == "Off")
    s.log.clear()
    s.press("5/0/2")
    ok("playlist key while playing swaps it", ("wiim", "MCUKeyShortClick:3") in s.log and s.vars["music_n"] == "3")
    s = Sim()
    s.press(SCENE_LOC["Music Inside"])
    s.log.clear()
    s.press("8/0/0")
    ok("music keeps going while another zone uses it", ("wiim", "setPlayerCmd:stop") not in s.log)
    # Dials stop at both ends
    s = Sim()
    s.levels[1] = 0.0
    s.run(KEYS["4/3/0"].right)
    ok("dial stops at 0 dB", s.levels[1] == 0.0)
    s.levels[1] = -60.0
    s.run(KEYS["4/3/0"].left)
    ok("dial stops at -60 dB", s.levels[1] == -60.0)
    s.levels[1] = -10.0
    s.run(KEYS["4/3/0"].right)
    ok("dial raises", s.levels[1] == -9.0)
    # Triggers
    s = Sim()
    s.vars["light_preset_n"] = "4"
    s.run(TRIGGERS["startup_recovery"]["control"]["actions"])
    ok("startup replays the look", s.log == [("osc", "/lobby/preset/4")])
    s = Sim()
    s.vars["light_mode"] = "ipad"
    s.run(TRIGGERS["startup_recovery"]["control"]["actions"])
    ok("startup leaves iPad alone", s.log == [])
    s.run(TRIGGERS["schedule_night"]["control"]["actions"])
    ok("night clears iPad Mode and turns off", s.vars["light_mode"] == "presets" and ("osc", "/lobby/off") in s.log)
    failed = [n for n, passed in checks if not passed]
    return len(checks), failed


# ---------------------------------------------------------------- reference doc
def plain(label):
    """A key label as one line of readable text, for the reference doc."""
    text = label.replace("-\n", "").replace("\n", " ")
    text = text.replace("$(custom:light_preset)", "(current look)")
    text = re.sub(r"\$\(wing:mtx\d_level\) dB", "(level)", text)
    return re.sub(r"\$\(custom:z\d_src\)", "(current)", text)


def name_of(loc):
    return plain(KEYS[loc].label)


def describe(actions, indent=0):
    out, pad = [], "  " * indent
    for a in actions:
        o = {k: v["value"] for k, v in a["options"].items()}
        d = a["definitionId"]
        if d == "button_pressrelease":
            out.append(f"{pad}Run `{o['location']}` {name_of(o['location'])}")
        elif d == "wait":
            out.append(f"{pad}Wait {int(a['options']['time']['value']) / 1000:g} s")
        elif d == "custom_variable_set_value":
            out.append(f"{pad}Set `{o['name']}` to `{o['value']}`")
        elif d == "set_page":
            out.append(f"{pad}This surface goes to page {o['page']}")
        elif d == "logic_if":
            cond = a["children"]["condition"][0]["options"]["expression"]["value"]
            cond = {PRESETS_MODE: "lights are on presets", NONE_PLAYLIST: "no zone is on Playlist",
                    ANY_PLAYLIST: "any zone is on Playlist"}.get(cond, f"`{cond}`")
            out.append(f"{pad}If {cond}:")
            out += describe(a["children"]["actions"], indent + 1)
            if a["children"]["else_actions"]:
                out.append(f"{pad}Otherwise:")
                out += describe(a["children"]["else_actions"], indent + 1)
        elif d == "send_blank":
            out.append(f"{pad}S-Play OSC `{o['path']}`")
        elif d == "get":
            out.append(f"{pad}WiiM `{o['url'].split('=', 1)[1]}`")
        elif d == "set-send-mute":
            bus = o["src"].replace("/bus/", "/bus/")
            mx = o["dest"].split("/")[-1]
            out.append(f"{pad}Wing `{bus}/send/MX{mx}/on` = {1 if o['mute'] == '0' else 0}")
        elif d == "set-mute":
            out.append(f"{pad}Wing `{o['sel']}/mute` = {o['mute']}")
        elif d == "set-fader":
            out.append(f"{pad}Wing `{o['sel']}/fdr` = {o['level']} dB")
        elif d == "fader-delta":
            out.append(f"{pad}Wing `{o['sel']}/fdr` {int(o['delta']):+d} dB")
    return out


def behind(key):
    lines = []
    if key.hold:
        lines.append(f"Hold {key.hold[0] / 1000:g} s:")
        lines += describe(key.hold[1], 1)
    lines += describe(key.down)
    if key.left is not None:
        lines = ["Press:"] + describe(key.down, 1) + ["Turn left:"] + describe(key.left, 1) + \
                ["Turn right:"] + describe(key.right, 1)
    return "<br>".join(line.replace("  ", "&nbsp;&nbsp;") for line in lines) or "Nothing"


def page_table(number):
    rows = ["| Key | Shows | Does | What runs behind it |", "| --- | --- | --- | --- |"]
    keys = sorted((k for k in KEYS.values() if k.page == number), key=lambda k: (k.row, k.col))
    keys = [k for k in keys if not k.art]
    for k in keys:
        rows.append(f"| `{k.loc}` | {plain(k.label)} | {k.does} | {behind(k)} |")
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
      "[build.py](../config/stream-deck/build.py), together with the importable file and the icons, so all of them match.\n")
    a("Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig) into Companion instead of "
      "building these by hand. [Companion setup](07-companion-setup.md) has the steps.\n")
    a(f"**Status:** The file has {count} keys and has not yet been imported into a real Companion. "
      "Its format and every action were checked against the Companion 5.1.2 and module source, and its logic "
      f"passed {checks} simulated checks. [Bench test 13](09-testing.md) is the real proof.\n")
    a("## How a press reaches the hardware\n")
    a("Real keys don't talk to hardware directly. Each one runs a block on a Library page, so a change happens in one place.\n")
    a("| Target | Connection | Message | Example |\n| --- | --- | --- | --- |\n"
      f"| Wing Rack | `wing`, {WING_IP} | Wing OSC through the Behringer module | `/bus/14/send/MX1/on` = 1 |\n"
      f"| S-Play Mini | `splay`, {SPLAY_IP} port 8000 | OSC, no arguments | `/lobby/preset/1` |\n"
      f"| WiiM | `wiim`, https://{WIIM_IP}/ | HTTPS GET to `httpapi.asp?command=` | `MCUKeyShortClick:1` |\n")
    a("Key addresses read page/row/column from 0, the same form Companion uses. Rows and columns start at the top left.\n")
    a("On the Stream Deck +, rows 0 and 1 are the keys, row 2 is the touch strip, and row 3 is the dials.\n")
    a("## Colors\n")
    a("Amber is lighting, blue is audio, violet is music, purple is the iPad, and red is off. A brighter key is the active "
      "choice. In iPad Mode, lighting keys go dark and show a lock.\n")
    a("The labels are live text, so you can rename a key in Companion without touching its icon. Icons are in "
      "[config/stream-deck/icons](../config/stream-deck/icons). Each is 144 pixels square, which suits the 72-pixel MK.2 keys and the 120-pixel Stream Deck + keys.\n")
    a("## Door pages\n")
    a("Doors use a 15-key deck, in 3 rows of 5.\n")
    a("![Door Stream Deck pages](images/stream-deck-doors.png)\n")
    for n in (1, 2, 3):
        a(f"### Page {n}: {PAGES[n][0]}\n")
        if n == 1:
            a("The 13 picture keys are one image cut into tiles, and they do nothing. Replace them with the church logo when you have it.\n")
        a(page_table(n) + "\n")
    a("## Rack pages\n")
    a("The rack uses a Stream Deck + with 8 keys, a touch strip and 4 dials.\n")
    a("![Rack Stream Deck pages](images/stream-deck-rack.png)\n")
    for n in range(4, 8):
        a(f"### Page {n}: {PAGES[n][0]}\n")
        a(page_table(n) + "\n")
    a("### Pages 8 to 12: Zones\n")
    a("All five zone pages match. Page 8 is shown here. The others use their own matrix and variable.\n")
    a("| Page | Zone | Matrix | Variable | Default fader |\n| --- | --- | --- | --- | --- |")
    for z, name, mx, db, page, _ in ZONES:
        a(f"| {page} | {name} | MX{mx} | `z{z}_src` | {db} dB |")
    a("")
    a(page_table(8) + "\n")
    a("## Library\n")
    a("No surface shows these pages. Keep them where they are, because every real key points to them by address.\n")
    a("### Page 20: Zones 1 to 4\n")
    a(library_table(20) + "\n")
    a("### Page 21: Zone 5, lights and music\n")
    a(library_table(21) + "\n")
    a("## Triggers\n")
    a("| Trigger | Starts | Does |\n| --- | --- | --- |")
    for t_ in TRIGGERS.values():
        c = t_["control"]
        a(f"| {c['options']['name']} | {'On' if c['options']['enabled'] else 'Off'} | {t_['does']} |")
    a("\nThe three schedule triggers import turned off. Set their times and turn them on after launch.\n")
    a("## Custom variables\n")
    a("All of these keep their value through a restart.\n")
    a("| Variable | Holds | Starts as |\n| --- | --- | --- |")
    for name, (d, v) in VARIABLES.items():
        a(f"| `{name}` | {d} | {v} |")
    a("\n## Change it later\n")
    a("- **Rename a look.** Change the label on the door key and rack key, and the name in its Library block. The look itself lives in the S-Play.\n"
      "- **Rename a playlist.** Change the label on page 5 and the name in its Library block.\n"
      "- **Use SharePoint playlists.** Edit one block, `21/0/6` Music Play. Change its first WiiM command to `setPlayerCmd:playlist:<address of the playlist>:0`. Nothing else moves.\n"
      "- **Change a room scene.** Edit its block on row 3 of page 21. Every door, rack and schedule key follows.\n"
      "- **Change a default level.** Edit `21/0/5`.\n"
      "- **Add a door.** Add the surface in Companion and limit it to pages 1 to 3. Nothing in the pages changes.\n")
    a("After any change, export the configuration from Companion and commit it next to this file. From then on, that export is the "
      "live copy and `build.py` is only a record of the first version.\n")
    DOC.write_text("\n".join(t), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- layout images
def sample(text):
    text = text.replace("$(custom:light_preset)", "Everyday")
    text = re.sub(r"\$\(wing:mtx\d_level\)", "-6.0", text)
    return re.sub(r"\$\(custom:z\d_src\)", "Playlist", text)


def key_html(key, images):
    if key is None:
        return '<div class="key empty"></div>'
    bg = f"#{COLORS[key.cat][0]:06x}"
    image = key.art or key.icon
    img = f'<img src="data:image/png;base64,{images[image]}">' if image else ""
    cls = "center" if key.align == "center:center" else "bottom"
    text = sample(key.label).replace("\n", "<br>")
    return f'<div class="key" style="background:{bg}">{img}<span class="{cls}">{text}</span></div>'


def layout(numbers, kind, images, path, width):
    rows, cols = (3, 5) if kind == "door" else (2, 4)
    cards = []
    for n in numbers:
        grid = "".join(key_html(KEYS.get(f"{n}/{r}/{c}"), images) for r in range(rows) for c in range(cols))
        extra = ""
        if kind == "rack":
            strip = "".join(
                f'<div class="seg">{sample(KEYS[f"{n}/2/{c}"].label).replace(chr(10), "<br>")}</div>'
                if f"{n}/2/{c}" in KEYS else '<div class="seg"></div>' for c in range(4))
            dials = "".join(f'<div class="dial{"" if f"{n}/3/{c}" in KEYS else " idle"}"></div>' for c in range(4))
            extra = f'<div class="strip">{strip}</div><div class="dials">{dials}</div>'
        cards.append(f'<div class="card"><h2>Page {n}: {PAGES[n][0]}</h2>'
                     f'<div class="deck {kind}"><div class="grid" style="grid-template-columns:repeat({cols},82px)">'
                     f'{grid}</div>{extra}</div></div>')
    note = ("Hold the amber key to open the lights. In iPad Mode, the status key turns purple and the lights stay locked."
            if kind == "door" else "Dials set volume. A bright key is the active choice.")
    html = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;padding:28px;width:{width}px;background:#f3f1ec;font-family:'Segoe UI',Arial,sans-serif;color:#1c2024}}
h1{{font-size:26px;margin:0 0 4px}} p{{margin:0 0 22px;color:#555}}
.wrap{{display:flex;flex-wrap:wrap;gap:26px}} h2{{font-size:15px;margin:0 0 8px;font-weight:600}}
.deck{{background:#17191c;border-radius:16px;padding:16px;display:inline-block}}
.grid{{display:grid;gap:9px}} .key{{width:82px;height:82px;border-radius:9px;position:relative;overflow:hidden;color:#fff}}
.key.empty{{background:#0d0e10}} .key img{{width:100%;height:100%;display:block}}
.key span{{position:absolute;left:0;right:0;text-align:center;font-size:12.5px;line-height:14px;font-weight:600}}
.key span.bottom{{bottom:6px}} .key span.center{{top:50%;transform:translateY(-50%)}}
.strip{{display:grid;grid-template-columns:repeat(4,82px);gap:9px;margin-top:10px;background:#0b0c0e;border-radius:6px}}
.seg{{height:50px;color:#fff;font-size:11.5px;line-height:15px;text-align:center;display:flex;align-items:center;justify-content:center}}
.dials{{display:grid;grid-template-columns:repeat(4,82px);gap:9px;margin-top:10px;justify-items:center}}
.dial{{width:46px;height:46px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#555,#26282c);border:2px solid #3a3d42}}
.dial.idle{{opacity:.35}}</style>
<h1>{'Door stations' if kind == 'door' else 'Rack station'}</h1><p>{note} Companion draws the final text, so spacing will differ slightly.</p>
<div class="wrap">{''.join(cards)}</div>"""
    page = path.with_suffix(".html")
    page.write_text(html, encoding="utf-8")
    return page


def main():
    build_library()
    build_doors()
    build_rack()
    build_triggers()
    errors = validate()
    count, failed = tests()
    print(f"keys: {len(KEYS)}  structure errors: {len(errors)}  logic checks: {count}  failed: {len(failed)}")
    for line in errors + failed:
        print("  FAIL", line)
    if errors or failed:
        sys.exit(1)
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        profile = str(tmp / "profile")
        images = render_icons(profile, tmp)
        data = export(images)
        out = HERE / "lobby.companionconfig"
        out.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
        kb = out.stat().st_size // 1024
        print(f"config: {kb} KB, icons: {len(images)}")
        IMAGES.mkdir(exist_ok=True)
        real = sum(1 for k in KEYS.values() if PAGES[k.page][1] != "library")
        write_doc(len(KEYS), count)
        for numbers, kind, name, width, height in (
                ([1, 2, 3], "door", "stream-deck-doors", 1490, 500),
                ([4, 5, 6, 7, 8], "rack", "stream-deck-rack", 1250, 880)):
            page = layout(numbers, kind, images, tmp / name, width)
            target = IMAGES / f"{name}.png"
            chrome(profile, f"--screenshot={target}", f"--window-size={width + 56},{height}", page.as_uri())
            print(name, target.exists(), target.stat().st_size // 1024, "KB")
        print(f"surface keys: {real}, library blocks: {len(KEYS) - real}")


if __name__ == "__main__":
    main()
