# Stream Deck pages

This is every Stream Deck page, key by key, with what runs behind each one. It is generated from [build.py](../config/stream-deck/build.py), together with the importable file and the artwork, so all of them match.

Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig) into Companion instead of building these by hand. [Companion setup](07-companion-setup.md) has the steps.

**Status:** The file has 191 buttons and has not yet been imported into a real Companion. Its format, every action and every button element were checked against the Companion 5.1.3 and module source, every expression in it was parsed and run, and its logic passed 133 simulated checks. [Bench test 13](09-testing.md) is the real proof.

## How a press reaches the hardware

Real keys don't talk to hardware directly. Each one runs a block on a Library page, so a change happens in one place.

| Target | Connection | Message | Example |
| --- | --- | --- | --- |
| Wing Rack | `wing`, 192.168.50.20 | Wing OSC through the Behringer module | `/bus/14/send/MX1/on` = 1 |
| ODE Mk3 | `dmx`, 192.168.50.31, Art-Net universe 0 | Channel values through the Art-Net module | `1-8,166;9-32,166;` |
| WiiM | `wiim`, https://192.168.50.40/ | HTTPS GET to `httpapi.asp?command=` | `MCUKeyShortClick:1` |

Key addresses read page/row/column from 0, the same form Companion uses. Rows and columns start at the top left.

On the Stream Deck +, rows 0 and 1 are the keys, row 2 is the touch strip, and row 3 is the dials.

## How it looks

Amber is lighting, warm white is the linear lights, blue is audio, violet is music, teal is the mics, purple is the iPad and red is off. A lit key, bright with a white icon, is the active choice. In iPad Mode, lighting keys go grey and show a lock. A green key with a check mark has just saved a look.

The touch strip shows a live panel above each dial: what the dial does, its value, and a level bar that moves as you turn it.

Labels are live text, so you can rename a key in Companion without touching its artwork. The artwork is in [config/stream-deck/icons](../config/stream-deck/icons): 144-pixel keys, drawn larger than the Stream Deck +'s 120-pixel keys so they stay sharp, and 200 by 100 touch strip panels, the size of each strip segment.

Inside Companion the same 60 images live in the image library, stored once, and keys refer to them by name, such as `$(image:tile_light_level2_active)`. Replacing an image there changes every key that uses it.

## Pages

Every station is a Stream Deck + with 8 keys, a touch strip and 4 dials, and they all share these pages. The rack and each door have their own surface group, which sets the pages that station may use. Every group starts on Home with every page, so to lock a door out of something, untick its page in that door's group.

The first two dials and the last one do the same thing on every page, so hands learn them. The third dial is the volume of whatever the page is about.

![Stream Deck pages](images/stream-deck-pages.png)

### Page 1: Home

| Key | Shows | Does | What runs behind it |
| --- | --- | --- | --- |
| `1/0/0` | Lights Off | Fades the lights out. Turning All Lights brings them back | Run `22/0/3` Lights Off |
| `1/0/1` | Lights 1 | Tap for Lights 1. Hold 3 seconds to save the lights as they are now into it | Tap:<br>&nbsp;&nbsp;Run `22/0/0` Look 1<br>Hold 3 s:<br>&nbsp;&nbsp;Run `22/0/5` Save 1 |
| `1/0/2` | Lights 2 | Tap for Lights 2. Hold 3 seconds to save the lights as they are now into it | Tap:<br>&nbsp;&nbsp;Run `22/0/1` Look 2<br>Hold 3 s:<br>&nbsp;&nbsp;Run `22/0/6` Save 2 |
| `1/0/3` | Lights 3 | Tap for Lights 3. Hold 3 seconds to save the lights as they are now into it | Tap:<br>&nbsp;&nbsp;Run `22/0/2` Look 3<br>Hold 3 s:<br>&nbsp;&nbsp;Run `22/0/7` Save 3 |
| `1/1/0` | Audio Off | Runs All Audio Off on all five zones | Run `21/2/5` Room All Audio Off |
| `1/1/1` | Auditorium | Runs Auditorium on all five zones | Run `21/2/0` Room Auditorium |
| `1/1/2` | Music | Plays the playlist inside, unless music is already playing | If no zone is on Playlist:<br>&nbsp;&nbsp;Run `21/2/1` Room Music Inside |
| `1/1/3` | More | Opens More | This surface goes to page 2 |
| `1/2/0` | ALL LIGHTS (live) | Touch strip: the All Lights level, Off, or iPad | Nothing |
| `1/2/1` | LINEAR (live) | Touch strip: the linear lights level | Nothing |
| `1/2/2` | Zone and source (live) | Touch strip: what is playing, and its volume from normal | Nothing |
| `1/2/3` | MICS (live) | Touch strip: the mic level, or Muted | Nothing |
| `1/3/0` | Dial: All Lights | Turn to dim or brighten every light, 5% a click, more when turned quickly. Push to turn the lights off or back on | Push:<br>&nbsp;&nbsp;Run `22/0/4` Lights On/Off<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all-`<br>&nbsp;&nbsp;Run `22/1/5` All Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all+`<br>&nbsp;&nbsp;Run `22/1/4` All Up |
| `1/3/1` | Dial: Linear | Turn to set just the linear lights, 5% a click, more when turned quickly. Push to put them back to the look | Push:<br>&nbsp;&nbsp;Run `22/2/0` Linear Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin-`<br>&nbsp;&nbsp;Run `22/1/7` Linear Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin+`<br>&nbsp;&nbsp;Run `22/1/6` Linear Up |
| `1/3/2` | Dial: Volume | Turn for the volume of whatever is playing, 1 dB a click, more when turned quickly: the auditorium feed, music, Bluetooth or the lobby mix. Push to put it back to normal | Push:<br>&nbsp;&nbsp;Run `22/2/7` Volume Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `vol-`<br>&nbsp;&nbsp;Run `22/2/2` Volume Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `vol+`<br>&nbsp;&nbsp;Run `22/2/1` Volume Up |
| `1/3/3` | Dial: Mics | Turn for mic volume, 1 dB a click, more when turned quickly, up to 0 dB. Push to mute or unmute the mics | Push:<br>&nbsp;&nbsp;Run `22/2/5` Mic Mute<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic-`<br>&nbsp;&nbsp;Run `22/2/4` Mic Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic+`<br>&nbsp;&nbsp;Run `22/2/3` Mic Up |

### Page 2: More

| Key | Shows | Does | What runs behind it |
| --- | --- | --- | --- |
| `2/0/0` | Bluetooth | Runs Bluetooth on all five zones | Run `21/2/4` Room Bluetooth |
| `2/0/1` | Lobby Event | Runs Lobby Event on all five zones | Run `21/2/3` Room Lobby Event |
| `2/0/2` | Everywhere | Runs Music Everywhere on all five zones | Run `21/2/2` Room Music Everywhere |
| `2/0/3` | Playlists | Opens Playlists | This surface goes to page 3 |
| `2/1/0` | Zones | Opens the first zone page | This surface goes to page 4 |
| `2/1/1` | Close Up | Hold 1.5 seconds to turn off the lights and every zone, and leave iPad Mode | Hold 1.5 s:<br>&nbsp;&nbsp;Run `22/2/6` Close Up |
| `2/1/2` | iPad Mode | Hold 1 second to hand the lights to the iPad, or to take them back | Hold 1 s:<br>&nbsp;&nbsp;Run `22/1/3` iPad Toggle |
| `2/1/3` | Home | Opens Home | This surface goes to page 1 |
| `2/2/0` | ALL LIGHTS (live) | Touch strip: the All Lights level, Off, or iPad | Nothing |
| `2/2/1` | LINEAR (live) | Touch strip: the linear lights level | Nothing |
| `2/2/2` | Zone and source (live) | Touch strip: what is playing, and its volume from normal | Nothing |
| `2/2/3` | MICS (live) | Touch strip: the mic level, or Muted | Nothing |
| `2/3/0` | Dial: All Lights | Turn to dim or brighten every light, 5% a click, more when turned quickly. Push to turn the lights off or back on | Push:<br>&nbsp;&nbsp;Run `22/0/4` Lights On/Off<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all-`<br>&nbsp;&nbsp;Run `22/1/5` All Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all+`<br>&nbsp;&nbsp;Run `22/1/4` All Up |
| `2/3/1` | Dial: Linear | Turn to set just the linear lights, 5% a click, more when turned quickly. Push to put them back to the look | Push:<br>&nbsp;&nbsp;Run `22/2/0` Linear Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin-`<br>&nbsp;&nbsp;Run `22/1/7` Linear Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin+`<br>&nbsp;&nbsp;Run `22/1/6` Linear Up |
| `2/3/2` | Dial: Volume | Turn for the volume of whatever is playing, 1 dB a click, more when turned quickly: the auditorium feed, music, Bluetooth or the lobby mix. Push to put it back to normal | Push:<br>&nbsp;&nbsp;Run `22/2/7` Volume Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `vol-`<br>&nbsp;&nbsp;Run `22/2/2` Volume Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `vol+`<br>&nbsp;&nbsp;Run `22/2/1` Volume Up |
| `2/3/3` | Dial: Mics | Turn for mic volume, 1 dB a click, more when turned quickly, up to 0 dB. Push to mute or unmute the mics | Push:<br>&nbsp;&nbsp;Run `22/2/5` Mic Mute<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic-`<br>&nbsp;&nbsp;Run `22/2/4` Mic Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic+`<br>&nbsp;&nbsp;Run `22/2/3` Mic Up |

### Page 3: Playlists

| Key | Shows | Does | What runs behind it |
| --- | --- | --- | --- |
| `3/0/0` | Morning | Chooses and plays Morning | Run `21/1/1` P1 Morning |
| `3/0/1` | Everyday | Chooses and plays Everyday | Run `21/1/2` P2 Everyday |
| `3/0/2` | Evening | Chooses and plays Evening | Run `21/1/3` P3 Evening |
| `3/0/3` | Seasonal | Chooses and plays Seasonal | Run `21/1/4` P4 Seasonal |
| `3/1/0` | Inside | Runs Music Inside on all five zones | Run `21/2/1` Room Music Inside |
| `3/1/1` | Everywhere | Runs Music Everywhere on all five zones | Run `21/2/2` Room Music Everywhere |
| `3/1/2` | Back | Opens More | This surface goes to page 2 |
| `3/1/3` | Home | Opens Home | This surface goes to page 1 |
| `3/2/0` | ALL LIGHTS (live) | Touch strip: the All Lights level, Off, or iPad | Nothing |
| `3/2/1` | LINEAR (live) | Touch strip: the linear lights level | Nothing |
| `3/2/2` | Zone and source (live) | Touch strip: what is playing, and its volume from normal | Nothing |
| `3/2/3` | MICS (live) | Touch strip: the mic level, or Muted | Nothing |
| `3/3/0` | Dial: All Lights | Turn to dim or brighten every light, 5% a click, more when turned quickly. Push to turn the lights off or back on | Push:<br>&nbsp;&nbsp;Run `22/0/4` Lights On/Off<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all-`<br>&nbsp;&nbsp;Run `22/1/5` All Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all+`<br>&nbsp;&nbsp;Run `22/1/4` All Up |
| `3/3/1` | Dial: Linear | Turn to set just the linear lights, 5% a click, more when turned quickly. Push to put them back to the look | Push:<br>&nbsp;&nbsp;Run `22/2/0` Linear Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin-`<br>&nbsp;&nbsp;Run `22/1/7` Linear Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin+`<br>&nbsp;&nbsp;Run `22/1/6` Linear Up |
| `3/3/2` | Dial: Volume | Turn for the volume of whatever is playing, 1 dB a click, more when turned quickly: the auditorium feed, music, Bluetooth or the lobby mix. Push to put it back to normal | Push:<br>&nbsp;&nbsp;Run `22/2/7` Volume Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `vol-`<br>&nbsp;&nbsp;Run `22/2/2` Volume Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `vol+`<br>&nbsp;&nbsp;Run `22/2/1` Volume Up |
| `3/3/3` | Dial: Mics | Turn for mic volume, 1 dB a click, more when turned quickly, up to 0 dB. Push to mute or unmute the mics | Push:<br>&nbsp;&nbsp;Run `22/2/5` Mic Mute<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic-`<br>&nbsp;&nbsp;Run `22/2/4` Mic Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic+`<br>&nbsp;&nbsp;Run `22/2/3` Mic Up |

### Pages 4 to 8: Zones

All five zone pages match. Page 4 is shown here. The others use their own matrix and variable.

| Page | Zone | Matrix | Variable | Normal fader |
| --- | --- | --- | --- | --- |
| 4 | Mains | MX1 | `z1_src`, `z1_level` | -6 dB |
| 5 | Outdoor | MX2 | `z2_src`, `z2_level` | -10 dB |
| 6 | Soffit | MX3 | `z3_src`, `z3_level` | -10 dB |
| 7 | Bathrooms | MX4 | `z4_src`, `z4_level` | -12 dB |
| 8 | Vestibule | MX5 | `z5_src`, `z5_level` | -12 dB |

| Key | Shows | Does | What runs behind it |
| --- | --- | --- | --- |
| `4/0/0` | Auditorium | Mains plays Auditorium | Run `20/0/0` Z1 Auditorium<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `4/0/1` | Playlist | Mains plays Playlist | Run `21/0/7` Music Start<br>Wait 0.05 s<br>Run `20/0/1` Z1 Playlist |
| `4/0/2` | Bluetooth | Mains plays Bluetooth | Run `20/0/2` Z1 Bluetooth<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `4/0/3` | Lobby Mix | Mains plays Lobby Mix | Run `20/0/3` Z1 Lobby Mix<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `4/1/0` | Mains Off | Turns off Mains | Run `20/0/4` Z1 Off<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `4/1/1` | Vestibule | Opens Vestibule | This surface goes to page 8 |
| `4/1/2` | Outdoor | Opens Outdoor | This surface goes to page 5 |
| `4/1/3` | Home | Opens Home | This surface goes to page 1 |
| `4/2/0` | ALL LIGHTS (live) | Touch strip: the All Lights level, Off, or iPad | Nothing |
| `4/2/1` | LINEAR (live) | Touch strip: the linear lights level | Nothing |
| `4/2/2` | Zone and source (live) | Touch strip: Mains source and level | Nothing |
| `4/2/3` | MICS (live) | Touch strip: the mic level, or Muted | Nothing |
| `4/3/0` | Dial: All Lights | Turn to dim or brighten every light, 5% a click, more when turned quickly. Push to turn the lights off or back on | Push:<br>&nbsp;&nbsp;Run `22/0/4` Lights On/Off<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all-`<br>&nbsp;&nbsp;Run `22/1/5` All Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `all+`<br>&nbsp;&nbsp;Run `22/1/4` All Up |
| `4/3/1` | Dial: Linear | Turn to set just the linear lights, 5% a click, more when turned quickly. Push to put them back to the look | Push:<br>&nbsp;&nbsp;Run `22/2/0` Linear Reset<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin-`<br>&nbsp;&nbsp;Run `22/1/7` Linear Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `lin+`<br>&nbsp;&nbsp;Run `22/1/6` Linear Up |
| `4/3/2` | Dial: Mains | Turn for Mains volume, 1 dB a click, more when turned quickly. Push to put Mains back to -6 dB | Push:<br>&nbsp;&nbsp;Wing `/mtx/1/fdr` = -6 dB<br>&nbsp;&nbsp;Set `z1_level` to `-6`<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `z1-`<br>&nbsp;&nbsp;If `($(wing:mtx1_level) == '-oo' ? -90 : (isNumber($(wing:mtx1_level)) ? $(wing:mtx1_level) : $(custom:z1_level))) > -60`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `z1_level` to `max(-60, ($(wing:mtx1_level) == '-oo' ? -90 : (isNumber($(wing:mtx1_level)) ? $(wing:mtx1_level) : $(custom:z1_level))) - $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/mtx/1/fdr` moves by the same amount<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `z1+`<br>&nbsp;&nbsp;If `($(wing:mtx1_level) == '-oo' ? -90 : (isNumber($(wing:mtx1_level)) ? $(wing:mtx1_level) : $(custom:z1_level))) < 0`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `z1_level` to `min(0, ($(wing:mtx1_level) == '-oo' ? -90 : (isNumber($(wing:mtx1_level)) ? $(wing:mtx1_level) : $(custom:z1_level))) + $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/mtx/1/fdr` moves by the same amount |
| `4/3/3` | Dial: Mics | Turn for mic volume, 1 dB a click, more when turned quickly, up to 0 dB. Push to mute or unmute the mics | Push:<br>&nbsp;&nbsp;Run `22/2/5` Mic Mute<br>Turn left:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic-`<br>&nbsp;&nbsp;Run `22/2/4` Mic Down<br>Turn right:<br>&nbsp;&nbsp;Set `turn_n` from how fast the dial turned (see Dial speed)<br>&nbsp;&nbsp;Set `turn_ms` to `unixNow()`<br>&nbsp;&nbsp;Set `turn_key` to `mic+`<br>&nbsp;&nbsp;Run `22/2/3` Mic Up |

## Dial speed

Every dial speeds up when it's turned quickly. A slow click moves one step: 5% for the lights, 1 dB for audio. Clicks closer together than `turn_medium_ms` move 2 steps each, and closer than `turn_fast_ms` move 4. They start at 120 and 50 ms. Turning the other way, or turning a different dial, starts slow again. When the deck reports several clicks at once, each counts, and one report moves at most 8 steps. Levels still stop at their limits.

Each turn first sets `turn_n` with this expression, shown for All Lights turning right. `$(this:delta)` is the number of clicks the deck reported, and `unixNow()` is the time in milliseconds:

```
d = $(this:delta);
c = isNumber(d) ? max(1, abs(d)) : 1;
g = unixNow() - $(custom:turn_ms);
f = $(custom:turn_key) != 'all+' ? 1 : (g < $(custom:turn_fast_ms) ? 4 : (g < $(custom:turn_medium_ms) ? 2 : 1));
min(8, c * f)
```

Then the dial's block moves by `turn_n` steps. To change the feel, set `turn_medium_ms` and `turn_fast_ms` on the Variables page. Set both to 0 for one step a click.

## Lighting math

Companion keeps the lights as levels, and one block turns them into DMX. `lt_all` is the All Lights dial. `lt_linear` and `lt_fix` are the levels of the linear lights and of every other fixture. A Lights key sets `lt_all` to 100 and copies that look's two saved levels in. Lights Off sets `lt_all` to 0 and keeps the rest, which is why turning All Lights brings the same look back.

Every channel's value is its full value, times `lt_all`, times its group's level. In iPad Mode every value is 0, so the iPad's levels are the only ones the ODE sees. This is the expression in `22/1/0` Compute DMX:

```
k = $(custom:light_mode) == 'ipad' ? 0 : $(custom:lt_all) / 100;
`1-8,${round(255 * k * $(custom:lt_linear) / 100)};9-32,${round(255 * k * $(custom:lt_fix) / 100)};`
```

| Channels | Level | Full value | What they are |
| --- | --- | --- | --- |
| 1-8 | `lt_linear` | 255 | Linear house lights, through 0-10V decoders |
| 9-32 | `lt_fix` | 255 | Every other fixture's intensity channel |

These channels are placeholders until the DMX patch sheet exists. To change the patch, edit `22/1/0` in Companion, or `LIGHT_GROUPS` in build.py before the first import. A fixture with a color mix that never changes can put those channels in `STATIC_CHANNELS`.

## Library

No surface shows these pages. Keep them where they are, because every real key points to them by address.

### Page 20: Zones 1 to 4

| Key | Block | Does | Sends |
| --- | --- | --- | --- |
| `20/0/0` | Z1 Auditorium | Mains plays Auditorium | Wing `/bus/14/send/MX1/on` = 1<br>Wing `/bus/15/send/MX1/on` = 0<br>Wing `/bus/16/send/MX1/on` = 0<br>Wing `/main/1/send/MX1/on` = 0<br>Wing `/mtx/1/mute` = 0<br>Set `z1_src` to `Auditorium` |
| `20/0/1` | Z1 Playlist | Mains plays Playlist | Wing `/bus/14/send/MX1/on` = 0<br>Wing `/bus/15/send/MX1/on` = 1<br>Wing `/bus/16/send/MX1/on` = 0<br>Wing `/main/1/send/MX1/on` = 0<br>Wing `/mtx/1/mute` = 0<br>Set `z1_src` to `Playlist` |
| `20/0/2` | Z1 Bluetooth | Mains plays Bluetooth | Wing `/bus/14/send/MX1/on` = 0<br>Wing `/bus/15/send/MX1/on` = 0<br>Wing `/bus/16/send/MX1/on` = 1<br>Wing `/main/1/send/MX1/on` = 0<br>Wing `/mtx/1/mute` = 0<br>Set `z1_src` to `Bluetooth` |
| `20/0/3` | Z1 Lobby Mix | Mains plays Lobby Mix | Wing `/bus/14/send/MX1/on` = 0<br>Wing `/bus/15/send/MX1/on` = 0<br>Wing `/bus/16/send/MX1/on` = 0<br>Wing `/main/1/send/MX1/on` = 1<br>Wing `/mtx/1/mute` = 0<br>Set `z1_src` to `Lobby Mix` |
| `20/0/4` | Z1 Off | Mains off | Wing `/mtx/1/mute` = 1<br>Set `z1_src` to `Off` |
| `20/1/0` | Z2 Auditorium | Outdoor plays Auditorium | Wing `/bus/14/send/MX2/on` = 1<br>Wing `/bus/15/send/MX2/on` = 0<br>Wing `/bus/16/send/MX2/on` = 0<br>Wing `/main/1/send/MX2/on` = 0<br>Wing `/mtx/2/mute` = 0<br>Set `z2_src` to `Auditorium` |
| `20/1/1` | Z2 Playlist | Outdoor plays Playlist | Wing `/bus/14/send/MX2/on` = 0<br>Wing `/bus/15/send/MX2/on` = 1<br>Wing `/bus/16/send/MX2/on` = 0<br>Wing `/main/1/send/MX2/on` = 0<br>Wing `/mtx/2/mute` = 0<br>Set `z2_src` to `Playlist` |
| `20/1/2` | Z2 Bluetooth | Outdoor plays Bluetooth | Wing `/bus/14/send/MX2/on` = 0<br>Wing `/bus/15/send/MX2/on` = 0<br>Wing `/bus/16/send/MX2/on` = 1<br>Wing `/main/1/send/MX2/on` = 0<br>Wing `/mtx/2/mute` = 0<br>Set `z2_src` to `Bluetooth` |
| `20/1/3` | Z2 Lobby Mix | Outdoor plays Lobby Mix | Wing `/bus/14/send/MX2/on` = 0<br>Wing `/bus/15/send/MX2/on` = 0<br>Wing `/bus/16/send/MX2/on` = 0<br>Wing `/main/1/send/MX2/on` = 1<br>Wing `/mtx/2/mute` = 0<br>Set `z2_src` to `Lobby Mix` |
| `20/1/4` | Z2 Off | Outdoor off | Wing `/mtx/2/mute` = 1<br>Set `z2_src` to `Off` |
| `20/2/0` | Z3 Auditorium | Soffit plays Auditorium | Wing `/bus/14/send/MX3/on` = 1<br>Wing `/bus/15/send/MX3/on` = 0<br>Wing `/bus/16/send/MX3/on` = 0<br>Wing `/main/1/send/MX3/on` = 0<br>Wing `/mtx/3/mute` = 0<br>Set `z3_src` to `Auditorium` |
| `20/2/1` | Z3 Playlist | Soffit plays Playlist | Wing `/bus/14/send/MX3/on` = 0<br>Wing `/bus/15/send/MX3/on` = 1<br>Wing `/bus/16/send/MX3/on` = 0<br>Wing `/main/1/send/MX3/on` = 0<br>Wing `/mtx/3/mute` = 0<br>Set `z3_src` to `Playlist` |
| `20/2/2` | Z3 Bluetooth | Soffit plays Bluetooth | Wing `/bus/14/send/MX3/on` = 0<br>Wing `/bus/15/send/MX3/on` = 0<br>Wing `/bus/16/send/MX3/on` = 1<br>Wing `/main/1/send/MX3/on` = 0<br>Wing `/mtx/3/mute` = 0<br>Set `z3_src` to `Bluetooth` |
| `20/2/3` | Z3 Lobby Mix | Soffit plays Lobby Mix | Wing `/bus/14/send/MX3/on` = 0<br>Wing `/bus/15/send/MX3/on` = 0<br>Wing `/bus/16/send/MX3/on` = 0<br>Wing `/main/1/send/MX3/on` = 1<br>Wing `/mtx/3/mute` = 0<br>Set `z3_src` to `Lobby Mix` |
| `20/2/4` | Z3 Off | Soffit off | Wing `/mtx/3/mute` = 1<br>Set `z3_src` to `Off` |
| `20/3/0` | Z4 Auditorium | Bathrooms plays Auditorium | Wing `/bus/14/send/MX4/on` = 1<br>Wing `/bus/15/send/MX4/on` = 0<br>Wing `/bus/16/send/MX4/on` = 0<br>Wing `/main/1/send/MX4/on` = 0<br>Wing `/mtx/4/mute` = 0<br>Set `z4_src` to `Auditorium` |
| `20/3/1` | Z4 Playlist | Bathrooms plays Playlist | Wing `/bus/14/send/MX4/on` = 0<br>Wing `/bus/15/send/MX4/on` = 1<br>Wing `/bus/16/send/MX4/on` = 0<br>Wing `/main/1/send/MX4/on` = 0<br>Wing `/mtx/4/mute` = 0<br>Set `z4_src` to `Playlist` |
| `20/3/2` | Z4 Bluetooth | Bathrooms plays Bluetooth | Wing `/bus/14/send/MX4/on` = 0<br>Wing `/bus/15/send/MX4/on` = 0<br>Wing `/bus/16/send/MX4/on` = 1<br>Wing `/main/1/send/MX4/on` = 0<br>Wing `/mtx/4/mute` = 0<br>Set `z4_src` to `Bluetooth` |
| `20/3/3` | Z4 Lobby Mix | Bathrooms plays Lobby Mix | Wing `/bus/14/send/MX4/on` = 0<br>Wing `/bus/15/send/MX4/on` = 0<br>Wing `/bus/16/send/MX4/on` = 0<br>Wing `/main/1/send/MX4/on` = 1<br>Wing `/mtx/4/mute` = 0<br>Set `z4_src` to `Lobby Mix` |
| `20/3/4` | Z4 Off | Bathrooms off | Wing `/mtx/4/mute` = 1<br>Set `z4_src` to `Off` |

### Page 21: Zone 5, music and rooms

| Key | Block | Does | Sends |
| --- | --- | --- | --- |
| `21/0/0` | Z5 Auditorium | Vestibule plays Auditorium | Wing `/bus/14/send/MX5/on` = 1<br>Wing `/bus/15/send/MX5/on` = 0<br>Wing `/bus/16/send/MX5/on` = 0<br>Wing `/main/1/send/MX5/on` = 0<br>Wing `/mtx/5/mute` = 0<br>Set `z5_src` to `Auditorium` |
| `21/0/1` | Z5 Playlist | Vestibule plays Playlist | Wing `/bus/14/send/MX5/on` = 0<br>Wing `/bus/15/send/MX5/on` = 1<br>Wing `/bus/16/send/MX5/on` = 0<br>Wing `/main/1/send/MX5/on` = 0<br>Wing `/mtx/5/mute` = 0<br>Set `z5_src` to `Playlist` |
| `21/0/2` | Z5 Bluetooth | Vestibule plays Bluetooth | Wing `/bus/14/send/MX5/on` = 0<br>Wing `/bus/15/send/MX5/on` = 0<br>Wing `/bus/16/send/MX5/on` = 1<br>Wing `/main/1/send/MX5/on` = 0<br>Wing `/mtx/5/mute` = 0<br>Set `z5_src` to `Bluetooth` |
| `21/0/3` | Z5 Lobby Mix | Vestibule plays Lobby Mix | Wing `/bus/14/send/MX5/on` = 0<br>Wing `/bus/15/send/MX5/on` = 0<br>Wing `/bus/16/send/MX5/on` = 0<br>Wing `/main/1/send/MX5/on` = 1<br>Wing `/mtx/5/mute` = 0<br>Set `z5_src` to `Lobby Mix` |
| `21/0/4` | Z5 Off | Vestibule off | Wing `/mtx/5/mute` = 1<br>Set `z5_src` to `Off` |
| `21/0/5` | Default Levels | Resets every zone fader to its normal level, and the auditorium, music and Bluetooth faders to 0 dB | Wing `/mtx/1/fdr` = -6 dB<br>Set `z1_level` to `-6`<br>Wing `/mtx/2/fdr` = -10 dB<br>Set `z2_level` to `-10`<br>Wing `/mtx/3/fdr` = -10 dB<br>Set `z3_level` to `-10`<br>Wing `/mtx/4/fdr` = -12 dB<br>Set `z4_level` to `-12`<br>Wing `/mtx/5/fdr` = -12 dB<br>Set `z5_level` to `-12`<br>Wing `/bus/14/fdr` = 0 dB<br>Set `aud_level` to `0`<br>Wing `/bus/15/fdr` = 0 dB<br>Set `music_level` to `0`<br>Wing `/bus/16/fdr` = 0 dB<br>Set `bt_level` to `0` |
| `21/0/6` | Music Play | Starts the chosen playlist, then turns on shuffle and repeat | WiiM `MCUKeyShortClick:$(custom:music_n)`<br>Wait 2 s<br>WiiM `setPlayerCmd:loopmode:2` |
| `21/0/7` | Music Start | Starts music only if nothing is already playing it | If no zone is on Playlist:<br>&nbsp;&nbsp;Run `21/0/6` Music Play |
| `21/1/0` | Music Stop | Stops the player once no zone is using it | If no zone is on Playlist:<br>&nbsp;&nbsp;WiiM `setPlayerCmd:stop` |
| `21/1/1` | P1 Morning | Chooses Morning. Plays it now, or starts Music Inside if the room is silent | Set `music_n` to `1`<br>Set `music_name` to `Morning`<br>Wait 0.05 s<br>If any zone is on Playlist:<br>&nbsp;&nbsp;Run `21/0/6` Music Play<br>Otherwise:<br>&nbsp;&nbsp;Run `21/2/1` Room Music Inside |
| `21/1/2` | P2 Everyday | Chooses Everyday. Plays it now, or starts Music Inside if the room is silent | Set `music_n` to `2`<br>Set `music_name` to `Everyday`<br>Wait 0.05 s<br>If any zone is on Playlist:<br>&nbsp;&nbsp;Run `21/0/6` Music Play<br>Otherwise:<br>&nbsp;&nbsp;Run `21/2/1` Room Music Inside |
| `21/1/3` | P3 Evening | Chooses Evening. Plays it now, or starts Music Inside if the room is silent | Set `music_n` to `3`<br>Set `music_name` to `Evening`<br>Wait 0.05 s<br>If any zone is on Playlist:<br>&nbsp;&nbsp;Run `21/0/6` Music Play<br>Otherwise:<br>&nbsp;&nbsp;Run `21/2/1` Room Music Inside |
| `21/1/4` | P4 Seasonal | Chooses Seasonal. Plays it now, or starts Music Inside if the room is silent | Set `music_n` to `4`<br>Set `music_name` to `Seasonal`<br>Wait 0.05 s<br>If any zone is on Playlist:<br>&nbsp;&nbsp;Run `21/0/6` Music Play<br>Otherwise:<br>&nbsp;&nbsp;Run `21/2/1` Room Music Inside |
| `21/2/0` | Room Auditorium | Sets all five zones and their normal levels | Run `20/0/0` Z1 Auditorium<br>Run `20/1/4` Z2 Off<br>Run `20/2/4` Z3 Off<br>Run `20/3/0` Z4 Auditorium<br>Run `21/0/0` Z5 Auditorium<br>Run `21/0/5` Default Levels<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `21/2/1` | Room Music Inside | Sets all five zones and their normal levels | Run `21/0/7` Music Start<br>Wait 0.05 s<br>Run `20/0/1` Z1 Playlist<br>Run `20/1/4` Z2 Off<br>Run `20/2/4` Z3 Off<br>Run `20/3/1` Z4 Playlist<br>Run `21/0/1` Z5 Playlist<br>Run `21/0/5` Default Levels |
| `21/2/2` | Room Music Everywhere | Sets all five zones and their normal levels | Run `21/0/7` Music Start<br>Wait 0.05 s<br>Run `20/0/1` Z1 Playlist<br>Run `20/1/1` Z2 Playlist<br>Run `20/2/1` Z3 Playlist<br>Run `20/3/1` Z4 Playlist<br>Run `21/0/1` Z5 Playlist<br>Run `21/0/5` Default Levels |
| `21/2/3` | Room Lobby Event | Sets all five zones and their normal levels | Run `20/0/3` Z1 Lobby Mix<br>Run `20/1/4` Z2 Off<br>Run `20/2/4` Z3 Off<br>Run `20/3/3` Z4 Lobby Mix<br>Run `21/0/3` Z5 Lobby Mix<br>Run `21/0/5` Default Levels<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `21/2/4` | Room Bluetooth | Sets all five zones and their normal levels | Run `20/0/2` Z1 Bluetooth<br>Run `20/1/4` Z2 Off<br>Run `20/2/4` Z3 Off<br>Run `20/3/2` Z4 Bluetooth<br>Run `21/0/2` Z5 Bluetooth<br>Run `21/0/5` Default Levels<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |
| `21/2/5` | Room All Audio Off | Sets all five zones and their normal levels | Run `20/0/4` Z1 Off<br>Run `20/1/4` Z2 Off<br>Run `20/2/4` Z3 Off<br>Run `20/3/4` Z4 Off<br>Run `21/0/4` Z5 Off<br>Run `21/0/5` Default Levels<br>Wait 0.2 s<br>Run `21/1/0` Music Stop |

### Page 22: Lights and dials

| Key | Block | Does | Sends |
| --- | --- | --- | --- |
| `22/0/0` | Look 1 | Fades to Lights 1 at full, unless iPad Mode is on | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_look` to `1`<br>&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:look1_linear)`<br>&nbsp;&nbsp;Set `lt_fix` to `$(custom:look1_fix)`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/0/1` | Look 2 | Fades to Lights 2 at full, unless iPad Mode is on | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_look` to `2`<br>&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:look2_linear)`<br>&nbsp;&nbsp;Set `lt_fix` to `$(custom:look2_fix)`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/0/2` | Look 3 | Fades to Lights 3 at full, unless iPad Mode is on | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_look` to `3`<br>&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:look3_linear)`<br>&nbsp;&nbsp;Set `lt_fix` to `$(custom:look3_fix)`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/0/3` | Lights Off | Fades the lights out and keeps the look, so the All Lights dial can bring it back | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_all` to `0`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/0/4` | Lights On/Off | Turns the lights off, or back on to the last look | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;If the lights are on:<br>&nbsp;&nbsp;&nbsp;&nbsp;Run `22/0/3` Lights Off<br>&nbsp;&nbsp;Otherwise:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/0/5` | Save 1 | Saves the lights as they are now into Lights 1 | If the deck has the lights and they are on:<br>&nbsp;&nbsp;Set `look1_linear` to `round($(custom:lt_linear) * $(custom:lt_all) / 100)`<br>&nbsp;&nbsp;Set `look1_fix` to `round($(custom:lt_fix) * $(custom:lt_all) / 100)`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Keep `look1_linear` as its startup value<br>&nbsp;&nbsp;Keep `look1_fix` as its startup value<br>&nbsp;&nbsp;Set `lt_look` to `1`<br>&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:look1_linear)`<br>&nbsp;&nbsp;Set `lt_fix` to `$(custom:look1_fix)`<br>&nbsp;&nbsp;Set `lt_saved` to `1`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick<br>&nbsp;&nbsp;Wait 2 s<br>&nbsp;&nbsp;Set `lt_saved` to `0` |
| `22/0/6` | Save 2 | Saves the lights as they are now into Lights 2 | If the deck has the lights and they are on:<br>&nbsp;&nbsp;Set `look2_linear` to `round($(custom:lt_linear) * $(custom:lt_all) / 100)`<br>&nbsp;&nbsp;Set `look2_fix` to `round($(custom:lt_fix) * $(custom:lt_all) / 100)`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Keep `look2_linear` as its startup value<br>&nbsp;&nbsp;Keep `look2_fix` as its startup value<br>&nbsp;&nbsp;Set `lt_look` to `2`<br>&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:look2_linear)`<br>&nbsp;&nbsp;Set `lt_fix` to `$(custom:look2_fix)`<br>&nbsp;&nbsp;Set `lt_saved` to `2`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick<br>&nbsp;&nbsp;Wait 2 s<br>&nbsp;&nbsp;Set `lt_saved` to `0` |
| `22/0/7` | Save 3 | Saves the lights as they are now into Lights 3 | If the deck has the lights and they are on:<br>&nbsp;&nbsp;Set `look3_linear` to `round($(custom:lt_linear) * $(custom:lt_all) / 100)`<br>&nbsp;&nbsp;Set `look3_fix` to `round($(custom:lt_fix) * $(custom:lt_all) / 100)`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Keep `look3_linear` as its startup value<br>&nbsp;&nbsp;Keep `look3_fix` as its startup value<br>&nbsp;&nbsp;Set `lt_look` to `3`<br>&nbsp;&nbsp;Set `lt_all` to `100`<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:look3_linear)`<br>&nbsp;&nbsp;Set `lt_fix` to `$(custom:look3_fix)`<br>&nbsp;&nbsp;Set `lt_saved` to `3`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick<br>&nbsp;&nbsp;Wait 2 s<br>&nbsp;&nbsp;Set `lt_saved` to `0` |
| `22/1/0` | Compute DMX | Works out every channel from the levels. The patch lives here | Set `dmx_cmd` from the levels (see Lighting math) |
| `22/1/1` | Apply Fade | Sends the levels to the ODE over 2 seconds | Run `22/1/0` Compute DMX<br>Wait 0.02 s<br>Art-Net to the ODE: `$(custom:dmx_cmd)`, fading 2 s |
| `22/1/2` | Apply Quick | Sends the levels to the ODE right away, for the dials | Run `22/1/0` Compute DMX<br>Wait 0.02 s<br>Art-Net to the ODE: `$(custom:dmx_cmd)`, fading 0.15 s |
| `22/1/3` | iPad Toggle | Hands the lights to the iPad by fading Companion's output out, or takes them back | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `light_mode` to `ipad`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade<br>Otherwise:<br>&nbsp;&nbsp;Set `light_mode` to `deck`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/1/4` | All Up | Raises all lights by 5% for each step in `turn_n`, stopping at 100% | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_all` to `min(100, $(custom:lt_all) + 5 * $(custom:turn_n))`<br>&nbsp;&nbsp;Wait 0.01 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick |
| `22/1/5` | All Down | Lowers all lights by 5% for each step in `turn_n`, stopping at 0% | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_all` to `max(0, $(custom:lt_all) - 5 * $(custom:turn_n))`<br>&nbsp;&nbsp;Wait 0.01 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick |
| `22/1/6` | Linear Up | Raises the linear lights by 5% for each step in `turn_n`, stopping at 100% | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_linear` to `min(100, $(custom:lt_linear) + 5 * $(custom:turn_n))`<br>&nbsp;&nbsp;Wait 0.01 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick |
| `22/1/7` | Linear Down | Lowers the linear lights by 5% for each step in `turn_n`, stopping at 0% | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_linear` to `max(0, $(custom:lt_linear) - 5 * $(custom:turn_n))`<br>&nbsp;&nbsp;Wait 0.01 s<br>&nbsp;&nbsp;Run `22/1/2` Apply Quick |
| `22/2/0` | Linear Reset | Puts the linear lights back to the current look's level | If the deck has the lights, not the iPad:<br>&nbsp;&nbsp;Set `lt_linear` to `$(custom:lt_look) == 1 ? $(custom:look1_linear) : ($(custom:lt_look) == 2 ? $(custom:look2_linear) : ($(custom:look3_linear)))`<br>&nbsp;&nbsp;Wait 0.02 s<br>&nbsp;&nbsp;Run `22/1/1` Apply Fade |
| `22/2/1` | Volume Up | Raises whatever is playing by 1 dB for each step in `turn_n`, up to 6 dB over normal | If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Auditorium'`:<br>&nbsp;&nbsp;If `($(wing:bus14_level) == '-oo' ? -90 : (isNumber($(wing:bus14_level)) ? $(wing:bus14_level) : $(custom:aud_level))) < 6`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `aud_level` to `min(6, ($(wing:bus14_level) == '-oo' ? -90 : (isNumber($(wing:bus14_level)) ? $(wing:bus14_level) : $(custom:aud_level))) + $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/bus/14/fdr` moves by the same amount<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Playlist'`:<br>&nbsp;&nbsp;If `($(wing:bus15_level) == '-oo' ? -90 : (isNumber($(wing:bus15_level)) ? $(wing:bus15_level) : $(custom:music_level))) < 6`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `music_level` to `min(6, ($(wing:bus15_level) == '-oo' ? -90 : (isNumber($(wing:bus15_level)) ? $(wing:bus15_level) : $(custom:music_level))) + $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/bus/15/fdr` moves by the same amount<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Bluetooth'`:<br>&nbsp;&nbsp;If `($(wing:bus16_level) == '-oo' ? -90 : (isNumber($(wing:bus16_level)) ? $(wing:bus16_level) : $(custom:bt_level))) < 6`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `bt_level` to `min(6, ($(wing:bus16_level) == '-oo' ? -90 : (isNumber($(wing:bus16_level)) ? $(wing:bus16_level) : $(custom:bt_level))) + $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/bus/16/fdr` moves by the same amount<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Lobby Mix'`:<br>&nbsp;&nbsp;If `($(wing:main1_level) == '-oo' ? -90 : (isNumber($(wing:main1_level)) ? $(wing:main1_level) : $(custom:lobby_level))) < 6`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `lobby_level` to `min(6, ($(wing:main1_level) == '-oo' ? -90 : (isNumber($(wing:main1_level)) ? $(wing:main1_level) : $(custom:lobby_level))) + $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/main/1/fdr` moves by the same amount |
| `22/2/2` | Volume Down | Lowers whatever is playing by 1 dB for each step in `turn_n`, down to -60 dB | If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Auditorium'`:<br>&nbsp;&nbsp;If `($(wing:bus14_level) == '-oo' ? -90 : (isNumber($(wing:bus14_level)) ? $(wing:bus14_level) : $(custom:aud_level))) > -60`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `aud_level` to `max(-60, ($(wing:bus14_level) == '-oo' ? -90 : (isNumber($(wing:bus14_level)) ? $(wing:bus14_level) : $(custom:aud_level))) - $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/bus/14/fdr` moves by the same amount<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Playlist'`:<br>&nbsp;&nbsp;If `($(wing:bus15_level) == '-oo' ? -90 : (isNumber($(wing:bus15_level)) ? $(wing:bus15_level) : $(custom:music_level))) > -60`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `music_level` to `max(-60, ($(wing:bus15_level) == '-oo' ? -90 : (isNumber($(wing:bus15_level)) ? $(wing:bus15_level) : $(custom:music_level))) - $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/bus/15/fdr` moves by the same amount<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Bluetooth'`:<br>&nbsp;&nbsp;If `($(wing:bus16_level) == '-oo' ? -90 : (isNumber($(wing:bus16_level)) ? $(wing:bus16_level) : $(custom:bt_level))) > -60`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `bt_level` to `max(-60, ($(wing:bus16_level) == '-oo' ? -90 : (isNumber($(wing:bus16_level)) ? $(wing:bus16_level) : $(custom:bt_level))) - $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/bus/16/fdr` moves by the same amount<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Lobby Mix'`:<br>&nbsp;&nbsp;If `($(wing:main1_level) == '-oo' ? -90 : (isNumber($(wing:main1_level)) ? $(wing:main1_level) : $(custom:lobby_level))) > -60`:<br>&nbsp;&nbsp;&nbsp;&nbsp;Set `lobby_level` to `max(-60, ($(wing:main1_level) == '-oo' ? -90 : (isNumber($(wing:main1_level)) ? $(wing:main1_level) : $(custom:lobby_level))) - $(custom:turn_n))`<br>&nbsp;&nbsp;&nbsp;&nbsp;Wing `/main/1/fdr` moves by the same amount |
| `22/2/3` | Mic Up | Raises the mic bus by 1 dB for each step in `turn_n`, stopping at 0 dB | If `($(wing:bus13_level) == '-oo' ? -90 : (isNumber($(wing:bus13_level)) ? $(wing:bus13_level) : $(custom:mic_level))) < 0`:<br>&nbsp;&nbsp;Set `mic_level` to `min(0, ($(wing:bus13_level) == '-oo' ? -90 : (isNumber($(wing:bus13_level)) ? $(wing:bus13_level) : $(custom:mic_level))) + $(custom:turn_n))`<br>&nbsp;&nbsp;Wing `/bus/13/fdr` moves by the same amount |
| `22/2/4` | Mic Down | Lowers the mic bus by 1 dB for each step in `turn_n`, stopping at -60 dB | If `($(wing:bus13_level) == '-oo' ? -90 : (isNumber($(wing:bus13_level)) ? $(wing:bus13_level) : $(custom:mic_level))) > -60`:<br>&nbsp;&nbsp;Set `mic_level` to `max(-60, ($(wing:bus13_level) == '-oo' ? -90 : (isNumber($(wing:bus13_level)) ? $(wing:bus13_level) : $(custom:mic_level))) - $(custom:turn_n))`<br>&nbsp;&nbsp;Wing `/bus/13/fdr` moves by the same amount |
| `22/2/5` | Mic Mute | Mutes or unmutes the mic bus | If `(isNumber($(wing:bus13_mute)) ? $(wing:bus13_mute) : $(custom:mic_muted)) == 1`:<br>&nbsp;&nbsp;Wing `/bus/13/mute` = 0<br>&nbsp;&nbsp;Set `mic_muted` to `0`<br>Otherwise:<br>&nbsp;&nbsp;Wing `/bus/13/mute` = 1<br>&nbsp;&nbsp;Set `mic_muted` to `1` |
| `22/2/6` | Close Up | Leaves iPad Mode, then turns off the lights and every zone | Set `light_mode` to `deck`<br>Wait 0.02 s<br>Run `22/0/3` Lights Off<br>Run `21/2/5` Room All Audio Off |
| `22/2/7` | Volume Reset | Puts whatever is playing back to its normal level, 0 dB | If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Auditorium'`:<br>&nbsp;&nbsp;Wing `/bus/14/fdr` = 0 dB<br>&nbsp;&nbsp;Set `aud_level` to `0`<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Playlist'`:<br>&nbsp;&nbsp;Wing `/bus/15/fdr` = 0 dB<br>&nbsp;&nbsp;Set `music_level` to `0`<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Bluetooth'`:<br>&nbsp;&nbsp;Wing `/bus/16/fdr` = 0 dB<br>&nbsp;&nbsp;Set `bt_level` to `0`<br>If `($(custom:z1_src) != 'Off' ? $(custom:z1_src) : ($(custom:z2_src) != 'Off' ? $(custom:z2_src) : ($(custom:z3_src) != 'Off' ? $(custom:z3_src) : ($(custom:z4_src) != 'Off' ? $(custom:z4_src) : ($(custom:z5_src) != 'Off' ? $(custom:z5_src) : ('Off')))))) == 'Lobby Mix'`:<br>&nbsp;&nbsp;Wing `/main/1/fdr` = 0 dB<br>&nbsp;&nbsp;Set `lobby_level` to `0` |

## Triggers

| Trigger | Starts | Does |
| --- | --- | --- |
| Startup recovery | On | Five seconds after Companion starts, fades the lights back to where they were. In iPad Mode, it keeps Companion's output at zero |
| Schedule: Sunday arrival | Off | Off at first. Sunday 7:30: Lights 3 and the auditorium feed, unless iPad Mode is on |
| Schedule: Weekday open | Off | Off at first. Weekdays 8:00: Lights 2 and music inside, unless iPad Mode is on |
| Schedule: Night shutdown | Off | Off at first. Nightly 22:00: Close Up, which also leaves iPad Mode so doors can't stay locked |

The three schedule triggers import turned off. Set their times and turn them on after launch.

## Custom variables

All of these keep their value through a restart, except `lt_saved`.

| Variable | Holds | Starts as |
| --- | --- | --- |
| `light_mode` | deck, or ipad while the iPad has the lights | deck |
| `lt_look` | Number of the current look | 2 |
| `lt_all` | All Lights level, 0 to 100. 0 is off | 0 |
| `lt_linear` | Linear lights level, 0 to 100 | 65 |
| `lt_fix` | Other fixtures level, 0 to 100 | 65 |
| `look1_linear` | Lights 1 linear level, saved by holding its key | 35 |
| `look1_fix` | Lights 1 fixtures level, saved by holding its key | 35 |
| `look2_linear` | Lights 2 linear level, saved by holding its key | 65 |
| `look2_fix` | Lights 2 fixtures level, saved by holding its key | 65 |
| `look3_linear` | Lights 3 linear level, saved by holding its key | 100 |
| `look3_fix` | Lights 3 fixtures level, saved by holding its key | 100 |
| `lt_saved` | Look just saved, shown on its key for two seconds | 0 |
| `dmx_cmd` | The DMX channels and values last sent to the ODE | (empty) |
| `aud_level` | Auditorium fader in dB, kept in step with the Wing | 0 |
| `music_level` | Music fader in dB, kept in step with the Wing | 0 |
| `bt_level` | Bluetooth fader in dB, kept in step with the Wing | 0 |
| `lobby_level` | Lobby Mix fader in dB, kept in step with the Wing | 0 |
| `z1_level` | Mains fader in dB, kept in step with the Wing | -6 |
| `z2_level` | Outdoor fader in dB, kept in step with the Wing | -10 |
| `z3_level` | Soffit fader in dB, kept in step with the Wing | -10 |
| `z4_level` | Bathrooms fader in dB, kept in step with the Wing | -12 |
| `z5_level` | Vestibule fader in dB, kept in step with the Wing | -12 |
| `mic_level` | Mic bus fader in dB, kept in step with the Wing | -10 |
| `mic_muted` | 1 while the mics are muted | 0 |
| `music_n` | Number of the chosen playlist | 1 |
| `music_name` | Name of the chosen playlist | Morning |
| `z1_src` | Mains source, or Off | Off |
| `z2_src` | Outdoor source, or Off | Off |
| `z3_src` | Soffit source, or Off | Off |
| `z4_src` | Bathrooms source, or Off | Off |
| `z5_src` | Vestibule source, or Off | Off |
| `turn_fast_ms` | Dial clicks closer together than this, in ms, move 4 steps each. 0 turns it off | 50 |
| `turn_medium_ms` | Dial clicks closer together than this, in ms, move 2 steps each. 0 turns it off | 120 |
| `turn_n` | Steps for the dial click being handled, worked out from how fast it turned | 1 |
| `turn_ms` | When a dial last clicked, in ms | 0 |
| `turn_key` | Which dial last clicked, and which way | (empty) |

## Change it later

- **Change how fast the dials speed up.** On the Variables page, set `turn_fast_ms` and `turn_medium_ms`. Clicks closer together than those many milliseconds move 4 or 2 steps instead of 1. Raise them to speed up sooner, or set both to 0 for one step a click.

- **Change a look.** At any station, set the lights with the two light dials, then hold Lights 1, 2 or 3 for 3 seconds. The key turns green and says Saved. Every station and schedule uses the new look at once.
- **Rename a playlist.** Change the label on page 3 and the name in its Library block.
- **Use SharePoint playlists.** Edit one block, `21/0/6` Music Play. Change its first WiiM command to `setPlayerCmd:playlist:<address of the playlist>:0`. Nothing else moves.
- **Change a room scene.** Edit its block on row 2 of page 21. Every station and schedule key follows.
- **Change a normal level.** Edit `21/0/5`.
- **Change the patch.** Edit `22/1/0`, as described in Lighting math.
- **Add a station.** Add the surface in Companion, give it its own surface group starting on page 1, and untick the pages it shouldn't use. Nothing in the pages changes.

After any change, export the configuration from Companion and commit it next to this file. From then on, that export is the live copy and `build.py` is only a record of the first version.
