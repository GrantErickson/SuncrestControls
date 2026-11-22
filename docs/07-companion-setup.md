# Companion setup

Companion holds the button layouts, the logic and the lights. Every page, artwork image and action comes from one file you import, so nothing runs custom code at the church.

[Stream Deck pages](14-stream-deck-pages.md) lists every key and what runs behind it.

## Install it

1. Install Debian or Ubuntu Server on the mini PC.
2. In the BIOS, set the PC to power on after AC power returns.
3. Set its static address to 192.168.50.10.
4. As root, run the [official headless install script](https://github.com/bitfocus/companion-pi): `curl https://raw.githubusercontent.com/bitfocus/companion-pi/main/install.sh | bash`
5. Run `sudo companion-update` and choose the current stable release. That was v5.1.3 on 2026-11-15.
6. Browse to `http://192.168.50.10:8000`.
7. Turn on the [Admin UI Password](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md). It only stops casual browsing, which is why the VLAN matters.
8. On the Protocols page, turn off remote protocols you aren't using.

## Import the configuration

1. Open [Import/Export](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/import-export.md) and choose [lobby.companionconfig](../config/stream-deck/lobby.companionconfig).
2. On the **Full import** tab, leave every available category selected, including the **Image Library**, and choose **Full Reset then Import**. Only do this on a new install, because it replaces what is there.
3. Open Connections and confirm the fourteen below. Companion uses the newest installed version of each module, so if one reports a missing module, install it from the Modules page.
4. Run [bench test 13](09-testing.md).

| Connection | Module | Settings in the file |
| --- | --- | --- |
| `wing` | [behringer-wing](https://github.com/bitfocus/companion-module-behringer-wing) | Desk IP 192.168.50.20, desk type Wing Rack |
| `dmx` | [generic-artnet](https://github.com/bitfocus/companion-module-generic-artnet) | Receiver 192.168.50.31, the ODE, universe 0 |
| `wiim` | [generic-http](https://github.com/bitfocus/companion-module-generic-http) | Base URL `https://192.168.50.40/`, unauthorized certificates accepted |
| `power` | [generic-tcp-udp](https://github.com/bitfocus/companion-module-generic-tcp-udp) | UDP to 192.168.50.45, port 30333, the Juice Goose iP-1520 that sequences the rack's switched outlets |
| `speaker1`, `speaker2` | [tplink-kasasmartplug](https://github.com/bitfocus/companion-module-tplink-kasasmartplug) | Plug IP 192.168.50.46 and 192.168.50.47, network scan off, polling on. The Kasa plugs on the powered speakers |
| `atem` | [bmd-atem](https://github.com/bitfocus/companion-module-bmd-atem) | Placeholder address 192.168.10.240, the ATEM's factory address, model 4 M/E Constellation HD. The production ATEM, which feeds each TV from its own output |
| `tv1` to `tv7` | [generic-tcp-udp](https://github.com/bitfocus/companion-module-generic-tcp-udp) | TCP to 192.168.50.81 to .87, port 20060, Sony's Simple IP control. The Sony BRAVIA 3 II TVs |

The WiiM uses a self-signed certificate, which is why the file accepts it. The file holds pages, variables, triggers, connections, 173 artwork images, the Elgato Stream Deck surface integration, and four surface groups. It doesn't hold the decks themselves or passwords, so add those next. Replace the ATEM's placeholder address in `atem` once the real one is known. The TVs need no key. [TVs](15-tvs.md#setting-up-each-bravia-3-ii) has the settings on each TV, and the [TV sheet](../config/network/tvs.csv) lists them.

Companion 5 drives USB Stream Decks through a surface integration. A full reset replaces the integrations with the ones in the file, which is why the file carries the Elgato one. An import that resets surfaces from a file without it leaves every Stream Deck showing Offline.

The artwork lives in Companion's image library, and each key refers to it by name, such as `$(image:dawn_r0c2_level2_active)`. To change a picture everywhere it appears, replace that one image in the library.

## Add the surfaces

Every station is a Stream Deck +, and they all share the same pages. The file includes a surface group for each deck, with its startup page and page permissions already set. Each door has its own group, because the decks in a group always show the same page. The groups import empty, because Companion knows decks by serial number, so you add each deck from its own settings.

| Group | Starts on | Can use |
| --- | --- | --- |
| Rack | Page 1, Home | Pages 1 to 6, every page |
| Door 1, Door 2, Door 3 | Page 1, Home | Pages 1 to 6, until you lock a door out of some |

1. Plug the rack Stream Deck + into the Companion host by USB. The install script handles Linux USB permissions.
2. Power each door dock over PoE, then give it its static address on the dock itself.
3. In Companion, open [Surfaces, then Remote Surfaces](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/surfaces.md). Each dock appears in the **Discover Surfaces** panel with its address. Click **Add Connection** beside it. If a dock isn't discovered, use **Add Remote Surface Connection**, choose **elgato**, and type its address. A dock has no row on the Surfaces page until it has a connection. [Elgato's guide](https://www.elgato.com/explorer/products/stream-deck/how-to-set-up-stream-deck-network-dock/) covers the dock itself.
4. In the Configured Surfaces list, click each deck and set **Surface Group** to its group. The rack goes in Rack, and each door in its own Door group.
5. On each Stream Deck +, turn off page turning by swiping the touch strip, so a stray swipe can't move a volunteer to another page.

Groups also make a spare easy to swap in: put the new deck in the old one's group, and nothing else changes. Because every station is the same deck, one spare covers them all.

## Lock a door out of pages

Every station starts with every page. To keep a door to the basics, open **Surfaces**, click that door's group, and take pages out of its allowed pages. Page restriction is already on in the file. Do this for each door group.

| Page | Holds | Locking it out stops |
| --- | --- | --- |
| 1, Home | Lights Off, Lights 1 to 3, the audio power key, Auditorium, Music, and the four dials | Keep it. Every station needs it |
| 2, More | Light Control, Audio Source, Audio Zones, Playlists, iPad Mode, Turn TVs On or Off, and TVs | Leaving iPad Mode, and the pages below, which are only reached from More |
| 3, Playlists | Seven playlists | Changing the playlist |
| 4, Light Control | Each light area on its own | Setting single areas |
| 5, Audio Source | Auditorium, Music, Bluetooth, Lobby Stage and the Bluetooth level | Playing Bluetooth or the Lobby Stage, and setting the Bluetooth level |
| 6, Audio Zones | Each zone on or off, and its volume | Changing a single zone |
| 7, TVs | A key for each TV, opening its page | Reaching any single TV. Turn TVs On and Off stays on More |
| 8 to 14, one for each TV | That TV on or off, and what it shows | Changing that TV. Take out the pages of TVs a door has no business with |

A key that opens a page the group can't use sends that deck to its first allowed page instead, which is Home. So on a door locked out of More, **More** simply stays on Home. Companion 5.1.3's surface groups work this way.

Keys on Home and the four dials can't be locked by page. That includes saving a look by holding a Lights key for 3 seconds, which works at any station that has Home.

## Trying the file on a Windows PC

You can try the whole file at a desk before the church hardware exists. Lights and audio won't respond, but every key, dial and display works.

1. Quit the Elgato Stream Deck app from the system tray. While it runs, it holds the deck and Companion can't draw on it.
2. Import the file as above.
3. Connect the deck:
   - **On USB:** open **Surfaces**. If the + shows **Offline**, check the right-hand panel (**Show Settings** on a narrow window): **Elgato Stream Deck** must be listed under surface integrations and turned on. If it's missing, choose **Add Surface Integration** and add it. Then press **Rescan USB**.
   - **On a Network Dock:** open **Surfaces, then Remote Surfaces**, find the dock in **Discover Surfaces**, and click **Add Connection**. A full reset clears these connections, so add it again after every full import.
4. On the Surfaces page, click the + and set **Surface Group** to **Rack**. It shows page 1, Home.

A deck outside any group also starts on page 1, so it shows Home before you assign it.

To try a door's group, set the +'s **Surface Group** to **Door 1**. It works exactly like the rack until you take pages out of that group. Set it back to **Rack** when you finish.

## How the pages are arranged

| Page | Name | Used by |
| --- | --- | --- |
| 1 | Home | Every station |
| 2 | More | Every station, unless locked out |
| 3 | Playlists | Every station, unless locked out |
| 4 | Light Control | Every station, unless locked out |
| 5 | Audio Source | Every station, unless locked out |
| 6 | Audio Zones | Every station, unless locked out |
| 7 | TVs | Every station, unless locked out |
| 8 to 14 | Main Lobby TV, Right Lobby TV, Cafe TV, Entry Hall TV, Kitchen TV, Meeting Room TV, Back Stage TV | Every station, unless locked out |
| 20 to 26 | Library, the shared building blocks | No surface |

The Library is why this stays maintainable. Each real key runs a Library block with **Button: Trigger press and release**, so a change happens in one place. Pages 15 to 19 are empty.

## The main page

| Top row | Lights Off | Lights 1 | Lights 2 | Lights 3 |
| --- | --- | --- | --- | --- |
| **Bottom row** | **Turn Audio Off**, or **Turn Audio On** | **Auditorium** | **Music** | **More** |
| **Dials** | **All Lights** | **Linear** | **Volume** | **Mics** |

The touch strip shows each dial's value and a level bar above it. The first two dials and the last one do the same thing on every page. The third dial follows the page: Volume on Home, More, Playlists and the TV pages, the picked area on Light Control, Bluetooth on Audio Source, and the picked zone on Audio Zones.

| Dial | Turn | Push |
| --- | --- | --- |
| All Lights | Every light, 5% a click | Lights off, or back on |
| Linear | Just the linear lights, 5% a click | Back to the look's level |
| Volume | Whatever is playing, 1 dB a click, up to 26 dB over normal. The panel names it and reads Normal, or how far from it | What's playing back to normal |
| Area, on Light Control | The picked area, 5% a click. With the lights off, turning up brings that area on by itself | That area back to the look's level |
| Bluetooth, on Audio Source | Bluetooth's level, 1 dB a click, playing or not, up to 26 dB over normal | Bluetooth back to normal |
| Zone, on Audio Zones | The picked zone, 1 dB a click | That zone back to its normal level |
| Mics | The mic bus, 1 dB a click, up to 0 dB | Mute or unmute the mics |

Every dial speeds up when it's turned quickly. A slow click moves one step, as above. Clicks less than 120 ms apart move 2 steps each, and less than 50 ms apart move 4. Turning the other way, or another dial, starts slow again, and levels still stop at their limits. Each turn works this out from Companion's `$(this:delta)`, the clicks the deck reported, and the time since the last click.

While the audio system is off, the Volume, Mics, Bluetooth and Zone dials do nothing, and their panels say Off and go grey.

To change the feel, set `turn_medium_ms` and `turn_fast_ms` on the Variables page. Raise them to speed up sooner, or set both to 0 for one step a click. [Stream Deck pages](14-stream-deck-pages.md#dial-speed) has the details.

Tapping a Lights key plays it. Holding one for 3 seconds saves the lights as they are now into it, and the key turns green and says Saved.

The Volume dial controls whatever is playing, as the source of the first zone that's on: the auditorium feed on Bus 14, music on Bus 15, Bluetooth on Bus 16, or the lobby stage on Main 1. The panel's title names it. Normal is -20 dB on that fader, so the dial has 26 dB to go up before it stops at +6 dB, and 40 dB to go down to -60 dB. Room buttons put Bus 14 and 15 back to normal. They leave Bus 16 at the level the Bluetooth dial set, and Main 1 to whoever is mixing the band.

Companion keeps its own copy of every zone level, each source fader, the mic level and the mic mute, and moves the Wing in step. When the Wing reports a level, the panels show the Wing's. When it doesn't, as on a desk with no Wing, the dials still move and the panels show Companion's copy, with an orange **NO WING** badge on the Volume and Mics panels.

The keys don't show Companion's status marks, such as the red ! for a device it can't reach or the green arrow while a key's actions run. The NO WING badge and the Connections page cover that instead.

## More, and the pages below it

More is the jumping-off point. Its dials match Home's, and **Home** is in the bottom-right corner of every page.

| Top row | Light Control | Audio Source | Audio Zones | Playlists |
| --- | --- | --- | --- | --- |
| **Bottom row** | **iPad Mode** | **Turn TVs Off**, or **Turn TVs On** | **TVs** | **Home** |

- **Light Control** has a key for each light area: Cafe, Chandeliers, Entry Hall, Sconces, Soffit, Fireplace and Outside. Tap one to pick it, and the third dial, Area, sets it. Each key is lit while its area is on, with its level along the bottom, and the picked one has a white ring. The looks hold every area's level, so Lights 1 to 3 reset them all and holding a Lights key saves them all. With the lights off, turning an area up brings it on by itself.
- **Playlists** has Morning, Everyday, Evening, Seasonal, Calm, Pop and Upbeat, and Home. A playlist key is lit while it plays. In a silent room it starts music inside, like Music on Home. For music outside too, switch the entries on in Audio Zones.
- **Audio Source** shows Auditorium, Music, Bluetooth and Lobby Stage, each lit while it plays. They toggle like the keys on Home. The third dial sets the Bluetooth level, playing or not, and keeps it.
- **Audio Zones** has a key for each zone: Lobby, Main Entry, North Entry, Bathrooms and Vestibule. Tap one to pick it. The switch beside Vestibule names the picked zone and turns it on or off: green and saying Turn Off while it plays, red and saying Turn On while it's off. A zone switched on plays what the other zones are playing, or the source played last if nothing is, and turns the audio system on if it's off. The third dial, Zone, sets the picked zone's volume.

- **Turn TVs Off** or **Turn TVs On** switches every TV at once. It's green while any TV is on, saying Turn TVs Off, with how many are on when it isn't all of them. It's red while they're all off, saying Turn TVs On, and a press turns each TV on showing its default.
- **TVs** opens a page with a key for each TV: Main Lobby, Right Lobby, Cafe, Entry Hall, Kitchen, Meeting Room and Back Stage. Each is green while that TV is on, with what it shows above its name, and red while it's off. Tap one to open that TV's page.
- **Each TV's page** starts with a switch that names the TV: green and saying Turn Off while it's on, red and saying Turn On while it's off. The next six keys choose what it shows: Stream, Announcements, Custom, SDI, USB and Local HDMI. The one it shows is lit, and choosing one turns the TV on. Back returns to TVs, whose last key is Home. [TVs](15-tvs.md) has the defaults and how the TVs connect.

Blank keys show their piece of the page's picture and do nothing.

## Audio power

The bottom row of Home turns the audio system on and off, as well as choosing what plays. The first key shows the state by its color, and its label says what a press does. A Juice Goose iP-1520 powers the rack gear that turns off with the audio, the amplifiers among them, through the `power` connection. Kasa smart plugs power the powered speakers, through `speaker1` and `speaker2`. [Audio setup](06-audio-setup.md#audio-power) has the setup.

| Key | While the audio is off | While it's on |
| --- | --- | --- |
| Audio power key | Red, saying Turn Audio On. Press to turn the system on, with nothing playing | Green, saying Turn Audio Off. Press to turn every zone off, stop the music, then turn the amplifiers off |
| Auditorium, Music, Bluetooth, Lobby Stage | Press to turn the system on and play that source | Lit while its source plays anywhere. Press a lit key to turn its source off, leaving the system on. Press another to swap to it |
| A playlist, the zone switch | Press to turn the system on and play | Plays, as before |
| Volume, Mics, Bluetooth and Zone dials | Do nothing. Their panels say Off and go grey | Work as usual |
| The night schedule | Stays off | Turns the lights, every TV and the audio system off |

`audio_power` holds the state, 1 for on and 0 for off. Only two Library blocks talk to the Juice Goose and the plugs, `21/3/0` Power On and `21/3/1` Power Off, so a different power switch means editing those two and the startup trigger.

Turning on, the Juice Goose sequences its pods on a second apart, amplifiers last, and the speaker plugs turn on 2.5 seconds later. Turning off goes the other way: speakers first, then the pods, amplifiers first. Sound starts within a few seconds of a source key. The Wing Rack, the WiiM and the Bluetooth receiver stay on all the time, so Companion never loses them.

## The whole-room buttons

Each one runs one Library block per zone and resets every matrix fader to its normal level. Because they set every zone, pressing any of them resets the room. Auditorium, Music, Bluetooth and Lobby Stage also toggle, as [Audio power](#audio-power) describes. These zone choices are starting points, and you change one by editing its block on row 2 of page 21. The mics reach every zone that's on, whatever its source.

| Button | Lobby | Main Entry | North Entry | Bathrooms | Vestibule |
| --- | --- | --- | --- | --- | --- |
| Auditorium | Auditorium | Off | Off | Auditorium | Auditorium |
| Music, Inside | Playlist | Off | Off | Playlist | Playlist |
| Music Everywhere, a Library block with no key, for schedules | Playlist | Playlist | Playlist | Playlist | Playlist |
| Lobby Stage | Lobby Stage | Off | Off | Lobby Stage | Lobby Stage |
| Bluetooth | Bluetooth | Off | Off | Bluetooth | Bluetooth |
| Turn Audio Off, before the amplifiers go off | Off | Off | Off | Off | Off |

The player follows the zones. It starts when the first zone goes to Playlist, and it stops when the last zone leaves. Pressing a playlist in a silent room also runs Music, Inside, so a volunteer always hears a result.

## iPad Mode

Hold **iPad Mode** on the More page for 1 second. The hold stops a stray press from blacking out the lobby.

**Entering iPad Mode** fades Companion's lighting output to zero over 2 seconds and sets `light_mode` to `ipad`.

**Leaving iPad Mode** sets `light_mode` to `deck` and fades the last look back in, unless the lights were off.

Every lighting key and dial checks `light_mode` before it acts, and the check lives in the Library. In iPad Mode the lighting keys go grey with a lock, the light dials stop, and the touch strip says **iPad** on every station. A station that restarts during an event locks too, because nothing is stored on the deck.

Any station that can open More can leave iPad Mode. Lock the doors out of More to keep your rule that the iPad overrides the doors. Tell the iPad operator to close the lighting app first.

## Close Up

**Close Up** is a Library block, `22/2/6`, that turns off the lights, every TV and the audio system and leaves iPad Mode, so the doors can't stay locked. The night schedule runs it, and no key does. To shut down by hand, press **Lights Off** and **Turn Audio Off** on Home, and **Turn TVs Off** on More.

## The startup trigger

Companion sends the lights, so a restart matters. Five seconds after Companion starts, the **Startup recovery** trigger fades the lights back to where they were. In iPad Mode it keeps Companion's light output at zero. It also sends the audio power state to the Juice Goose and the speaker plugs again, so they agree.

## Turn on the schedule after launch

The file includes three time-of-day triggers, turned off. Set their times, then turn them on. The first two skip themselves during iPad Mode, so a schedule never interrupts an event.

| When | Action |
| --- | --- |
| Sunday, before first arrivals | Lights 3 and the auditorium feed |
| Weekday opening time | Lights 2 and music inside |
| Every night | Close Up, which also turns the audio system off and leaves iPad Mode |

## Set up backups

In Settings, open [Backups](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md) and add a weekly backup rule. After any planned change, also [export the configuration](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/import-export.md) as YAML and commit it to the repo. From then on, that export is the live record.

Saving a look writes it into its variables' startup values, so exports carry the current looks.
