# Suncrest Controls: Project Brief

This is the living brief for the project. Add new answers and decisions here as they are made. The original brief is kept as written so we can always see where this started.

Plan and setup guide: [docs/README.md](docs/README.md). A formatted copy for reading and commenting is at https://claude.ai/artifact/2PVPHuZFu2TsG3WzzC3UW4.

## Original brief

I am needing to figure out the controls for our new church building. There a re multiple pieces and some may require some code to make happen. I would love to  find non-code solutions, but I want it to be a great experience for the people who use it. Here is what I am planning. 
Let's start with the lobby. 
I need a system to control the lighting. 
1. All the lights are DMX controllable and are basically fixed. We might from time to time add a few lights for special occasions. The linear 0-10v house lights are DMX as well. 
2. I need to have a few wall stations that will allow users to turn on and off the system. They need to be able to choose general presets that should cover 98% of uses. We probably need at least 8.
3. Labeled buttons on a device like this would work. https://www.springtree.net/product/deluxe-satellite-dmx-wall-station-ssd-8.
4. However, doing something like a streamdeck would also be nice with the lighted LCD displays, but not sure if it is worth the work to potentially integrate with something like companion.
5. We also need a switch to control the option of using an iPad with software like Luminair or Luimen that we are working on in another repo. This will give specific control for more complex events. 
6. There are going to be 2-3 remote stations by the entry doors and they will have a cat-6 cable run to each. 
What should I consider and what questions do you have. I am trying to figure out what the best lighting solution is in tthis case. 

Additionally, I need to be able to control the audio in the room. We will have a Wing Rack that is dedicated to the space. 
1. The lobby will have five sets of speakers. 
- 2 main speakers for the lobby. These will be traditional speakers meant for voice and music. 
- 2 outdoor speakers that wil be used for the courtyard area and for youth events outside.
- under soffit speakers for outside the other part of the building 70v. 
- bathroom speakers
- Speakers in the vestibule so the greeters can hear what is going on and have music at times. 
2. Generally there will be one source for all the speakers. 
- If there is a worship service going on or on a Sunday morning, the audio from the Behringer Wing in the auditorium will provide a feed.
- If there isn't there needs to be something that is playing a playlist or something to just have music going. 
- The Lobby has the Wing Rack which will have wireless mics and places for a band and for events in the lobby this would be used. This is most likely that the person running this will use the Wing App on the iPad for control. We do still neeed to be able to control the speaker sources. 
- We need a bluetooth option so someone could play specific music. 
- We need to be able to turn speakers on and off and assign them sources independently. 
- But the most common situation is that they would all have the same things. They probably need volume adjustments. 
- I was thinking about using a streamdeck and having a main page where the general controls are and individual pages for each set of speakers to do custom things. The options on the main page would override and reset the sysetm easily. 

The reason I bring up both the lighting and the audio is that while the audio could be controlled from a single point, the lighting needs to be by the doors. The lighting could be probably be simple, but if I am going to have to do the streamdecks for the audio could I just use a single custom system for the whole thing giving audio and lighting control on each stream deck. 

Pleas ask questions and help me work through the best technical solution for this.

## Answers to the design questions (2026-11-04)

### Lighting

1. **DMX size:** One DMX universe.
2. **Emergency lighting:** Handled separately, with batteries on some of the lights. It is not part of this control system.
3. **Door station access:** We might need covers of some sort. Other options are mounting them a little higher, or a front screen that doesn't really do anything and needs a next-page action to get to the changes.
4. **Preset type:** Static is fine. Active would be nice, but it could get harder to program.
5. **iPad and door stations:** The iPad overrides the door stations.
6. **Schedule:** Would be great, but it isn't a hard requirement.

### Audio

7. **Auditorium feed:** An analog run from the auditorium Wing to the lobby Wing Rack.
8. **Amps:** Each zone gets its own amp channel.
9. **Audio control location:** Audio control at the doors would be cool but isn't critical. We need audio control near the rack that holds all the equipment, and that spot can also be a lighting control station.
10. **Band:** Already figured out. There will be analog and an AES50 stage box.
11. **Music:** We have Spotify. A playlist we can keep updated online would be great, and a few to choose from would be cool. We could also download music. The church has a more expansive music license.
12. **Bluetooth:** The rack is on the side of the lobby and can be used for Bluetooth.

### Ownership

13. **Long-term care:** Not sure who owns it yet, but we do have technical people. The core setup shouldn't need to change much, and things like light settings and playlists should be easy for lay people to change.

### Follow-up answers

14. **SharePoint:** We use SharePoint through Teams a lot. Playlists of files could be a folder with a subfolder for each playlist, holding MP3 files. That could clean up the Spotify situation, and we wouldn't need to keep Spotify software updated. If there's an easy way to use Spotify long-term, that would probably be better.
15. **Stream Deck configuration:** Create the configuration for each page, what goes behind it to drive the hardware, the icons, and a layout.
16. **Wall mount:** Is there a Stream Deck wall mount?
17. **Rack deck (2026-11-11):** Should the rack use a regular Stream Deck or a Stream Deck + with dials? Adjusting volumes like on the Wing makes knobs appealing, but the + has fewer buttons. Is volume up/down keys with easy paging better than knobs with fewer keys, and does the + do paging?
18. **Rack main page (2026-11-11):** The + XL is cool but might be too much for volunteers. Proposed main page: lights on at dim levels 1, 2 and 3; lights off; audio on from the stream; audio on from the auditorium; audio off; a volume knob, a brightness override knob and a mic volume knob. That covers the basics and stays simple.
19. **First import (2026-11-15):** The configuration was loaded into Companion, but no buttons showed. The Stream Deck + is on hand, and it needs to handle both lighting and audio.
20. **Rack main page layout (2026-11-15):** Off goes on the left of each row. Top row: Lights Off, Lights 1, 2 and 3. Bottom row: Audio Off, Auditorium, Music and More. Dials, left to right: all lights, just the linear lights, overall volume and mic volume. The mics should be on all the time, and the mic dial controls their volume.
21. **Lighting software (2026-11-15):** Should we build software for the lights so we can just control them? Lumen, already in development, might work for this.
22. **Other lighting options (2026-11-15):** What other options are there for lighting control? A much simpler custom app is possible, but Lumen might work well. Is there something third party?
23. **Lighting engine (2026-11-15):** Go with Companion for DMX.
24. **Graphics (2026-11-15):** Build out the Companion configuration with all the graphics needed to make it intuitive, interactive and beautiful.
25. **Surface offline (2026-11-15):** After importing, the Stream Deck + shows Offline in Companion. The Remote Surfaces pane shows a device on the network. How is the surface configured from the imported file?
26. **Test deck on the network (2026-11-15):** The test Stream Deck + has an IP address but no row on the Surfaces page, so it's on the network, most likely through a Network Dock.
27. **First real run (2026-11-15):** It works on the Stream Deck +. The Volume and Mics knobs didn't change anything on a desk with no Wing, and the icons didn't look that great.
28. **Doors and volume (2026-11-15):** The door stations should work like the rack home, with the three light settings and some audio. The volume should be for the auditorium or music, whatever is selected, not the mains.
29. **Every station is a Stream Deck + (2026-11-15):** All the devices are Stream Deck + decks. Assume for now they all have the same functionality, and the doors will be locked out of functionality by page.
30. **Dial speed (2026-11-15):** The dials move one number per detent. Turned quickly they should skip ahead, and turned slowly they should move one at a time.
31. **Rack power (2026-11-16):** Rack power switching, probably from Furman, turns off when Audio Off is pressed. Auditorium turns the system on if it's off and plays the auditorium, and Music does the same for music. Audio Off powers the audio system down, and the Volume and Mics dials show as off and disabled, working only while the system is on. Audio Off becomes a toggle that turns the system back on. Auditorium and Music are exclusive toggles: press once for on and again for off, and pressing one while the other is on swaps them.
32. **Audio key look (2026-11-16):** The audio button should change when the audio comes on, to show that it's on. While it's off and highlighted, it should say Turn Audio On. Pressing Auditorium or Music should turn on the audio. The first version wasn't intuitive.
33. **Home look (2026-11-19):** The buttons on the main page could look better. Maybe a cool background image that spans them all, and better all around, with more color and polish.
34. **More page (2026-11-20):** More is a jumping-off point. Playlists stays where it is and opens the playlists that are available. Light Control leads to finer lighting, where you select a light and adjust it with a knob. The areas are things like Cafe, Chandeliers, Entry Hall, Sconces, Soffit, Fireplace and Outside. Audio Source shows the audio sources and which is selected: the ones from the main page plus Bluetooth and Lobby Stage, and Bluetooth should have a knob for its level. Audio Zones turns audio on or off and adjusts the volume in each location: Lobby, Bathrooms, North Entry, Main Entry and Vestibule. iPad Mode toggles DMX control from the station. A Home key. A few keys can stay blank for now. The knobs stay the same on More, and the icons should look as nice as the main page.
35. **More page details (2026-11-20):** The zones, in order, are Lobby, Main Entry (the courtyard speakers), North Entry (the soffit speakers), Bathrooms and Vestibule. On Audio Zones, tap a zone to pick it, and a key beside it turns it on or off. The Bluetooth knob is the third dial on Audio Source, so the lights and mic dials stay put. Drop both Close Up and the per-zone source pages.
36. **Playlists (2026-11-20):** Remove the Inside and Everywhere buttons from the Playlists page, and add Calm, Pop, Upbeat and Instrumental. With only 8 keys, keep Home in the corner and show 7 playlists, which leaves Instrumental out for now.
37. **Zone colors and the Main Entry icon (2026-11-20):** On Audio Zones, North Entry and Bathrooms aren't red or orange enough when they're off. It should be clear whether a zone is on or off, so the on versions should be more green and the off versions more red. The Main Entry icon should show an overhang, maybe with doors, since the covered area is what identifies it.
38. **Volume headroom (2026-11-20):** The third dial's overall level doesn't leave enough headroom, and there isn't enough room to make it louder. Make normal lower, probably -20 dB.
39. **Green lights key (2026-11-20):** For consistency, the selected lights key in the top row of Home should be green, so it's obvious that the lights and the audio are both on.
40. **DMX patch sheet (2026-11-21):** With the screens mostly done, work moves to the configuration and the remote devices, starting with the DMX devices. Make a document to work from, probably a spreadsheet, listing the light or lights each entry controls, how many channels it takes, what those channels are for, and its starting channel.
41. **Dimmers (2026-11-21):** Several lights are 0-10V, each controlled through DMX on a single channel, and all the 0-10V is in one ETC UFMP8 Foundry Mini Panel with 8 channels, taking 1 to 8. The rest are line voltage on a PD804-DMX-120 and a PD408-DMX-120. Fill the patch sheet with a position for each, with a column for the controller. Since these are only dimmers, use one row per thing being dimmed, one per channel.
42. **Rack power and speaker plugs (2026-11-21):** Use a [Juice Goose iP-1520](https://goknight.com/juice-goose-ip-1520-web-based-power-controller/) web-based power controller to sequence power for the audio in the rack, and a couple of [Kasa EP10 smart plugs](https://www.amazon.com/Kasa-Smart-Required-Certified-EP10P2/dp/B091FXQQMQ) to switch the powered speakers. Add them to the configuration.
43. **TVs (2026-11-21):** On the More page, add a TVs on/off button that turns all the TVs on or off. Each TV needs a page where it can be turned on or off and its content selected: the stream, announcements, the USB stick in the TV, a custom global signal, or local HDMI. The TVs are Main Lobby, Right Lobby, Cafe, Entry Hall, Kitchen, Meeting Room and Back Stage. When the TVs come on, there needs to be a mapping of what appears on each by default. The icons should look nice.
44. **TV control and the ATEM (2026-11-21):** The TVs are planned as Sony BRAVIA, which have Companion control. Samsung might be used if they can be made to work, so which will work reliably? All the inputs come from an ATEM 4 M/E, with each TV on a different output. Companion controls each TV by switching it to the HDMI input connected, through an SDI to HDMI converter, to the ATEM, then changes that ATEM output to one of the input streams. Eventually there will be a button that turns on everything, but not yet.
45. **ATEM, sources and TV model (2026-11-22):** The ATEM is a Blackmagic Design ATEM 4 M/E Constellation HD. M/E 1 is the stream, input 20 is announcements, and input 19 is custom. Assume the TVs are Sony BRAVIA 3 II.
46. **TV sheet (2026-11-22):** Make a file to list the TVs and their IP addresses, and so on.
47. **SDI option and the ATEM (2026-11-22):** Keep the USB key, and add another SDI option. The ATEM outputs are fine. The ATEM is always on. Use a placeholder for the ATEM address.
48. **Wing address (2026-11-22):** The Wing is at 192.168.0.30.
49. **Mic channel (2026-11-22):** The mic is on channel 1, and that is what the dial adjusts.

## Decision log

Newest first. Add a row whenever a decision is made or changed.

| Date | Decision | Status |
|---|---|---|
| 2026-11-22 | The mic is on Wing channel 1 (`MIC_CH`). The Mics dial moves `/ch/1`'s fader from -60 to 0 dB, starting at -10 dB, and pushing it mutes `/ch/1`; the panel reads `ch1_level` and `ch1_mute`. Channel 1 still reaches every zone through Bus 13, post-fader, whose fader is now set once as the ceiling below feedback and never moved by Companion. Channel 1 joins the Global Safes | Decided by the user |
| 2026-11-22 | `WING_IP` is 192.168.0.30, the Wing Rack's real address, replacing the example 192.168.50.20. The rest of the network plan stays on the example 192.168.50, so either the AV VLAN moves to 192.168.0, or Companion and the Wing app iPad reach the Wing by a route on UDP 2223 | Address given by the user. Which network, pending |
| 2026-11-22 | TV pages get a sixth choice, SDI (BNC plug icon), another ATEM source in `atem_sdi`, Black (0) until chosen. USB stays. Each TV page is now its switch, Stream, Announcements, Custom, SDI, USB, Local HDMI and Back; Home leaves the TV pages and stays on the TVs page. Each TV now has two Library rows (Send, On, Off; then six Show blocks), two TVs a page on pages 25 to 28, with the All TVs blocks at 28/2. ATEM outputs 18 to 24 confirmed. The ATEM is always on. `ATEM_IP` is the factory address 192.168.10.240 as a placeholder (`ATEM_IP_PLACEHOLDER`) | Decided by the user. The SDI source, a friendlier name for it, and the real ATEM address pending |
| 2026-11-22 | The TV sheet is `config/network/tvs.csv`, one row per TV: name, location, make and model, size, serial, MAC and IP address, Companion connection, control, deck page, ATEM output and its name, what feeds HDMI 1 and 2, converter, default, firmware, status and notes. build.py keeps its own copy of the names, addresses, outputs and defaults | Done. Fill in as the TVs go up |
| 2026-11-22 | TVs are Sony BRAVIA 3 II, a home model. Sony requires HTTPS for REST control on TVs released since August 1, 2025 (for Europe's radio rules, maybe wider), and the sony-bravia module is HTTP only, so `tv1` to `tv7` now use Sony's Simple IP control: generic-tcp-udp, TCP 20060, 24-byte messages ending in a line feed (`*SCPOWR…1` on, `…0` off, `*SCINPT0000000100000001` HDMI 1), with replies saved to `$(tvN:tcp_response)`. No pre-shared key. Each TV needs Remote start (or Control remotely) and Simple IP control on, Idle TV standby and BRAVIA Sync off. USB can't be selected over Simple IP, so it stays on the remote. The ATEM is a 4 M/E Constellation HD (24 outputs, `atem` model 20), so outputs 18 to 24 fit, and 3G-SDI converters do. Sources: Stream M/E 1 Program (10010), Announcements input 20, Custom input 19 | Decided by the user's answers. Test one TV on the bench before ordering the rest. Since the SDI row above: outputs confirmed, USB stays, ATEM always on, placeholder address |
| 2026-11-21 | TV control: Sony BRAVIA through Companion's sony-bravia module (REST API, pre-shared key), connections `tv1` to `tv7` at .81 to .87. Professional Displays recommended over home models; Samsung commercial displays (MDC, samsung-display module) are the fallback, and Samsung home TVs aren't dependable. The production ATEM feeds each TV from its own output over SDI to HDMI 1; Local HDMI is HDMI 2. Each Send block turns the TV off, or on, sets its ATEM output (`atem` connection, bmd-atem) to the source in `atem_stream`, `atem_announcements` or `atem_custom` and the TV's input, then sends the picture again 3 s later. USB only turns the TV on until it's tried on a real TV | Decided by the user's plan. Replaced 2026-11-22: BRAVIA 3 II over Simple IP control, Constellation HD and the sources, in the row above |
| 2026-11-21 | A button that turns everything on: lights, audio and TVs | Wanted later, not yet |
| 2026-11-21 | TVs: More's two blank keys become Turn TVs On or Off, green while any TV is on (with how many when only some are) and red while they're all off, and TVs, which opens page 7 with a key for each TV, green while it's on with what it shows and red while it's off. Pages 8 to 14 are one for each TV: a switch that names it, then Stream, Announcements, Custom, USB and Local HDMI, Back and Home. A TV that comes on shows its default, not its last choice, and choosing what it shows turns it on. Each TV's state is `tv<n>_src`, Library pages 25 and 26 hold its blocks, and its Send block stays empty until the TVs and the video system are chosen. Close Up turns every TV off, and startup sends every TV its state. The TV pages have their own picture, the blue hour, and magenta marks what a TV shows | Decided. Since the TV control row above, the Send blocks are filled in |
| 2026-11-21 | TV defaults: the stream in the Kitchen and Back Stage, announcements on the other five, including the Meeting Room, so it never starts on a blank laptop input | Proposed, pending confirmation |
| 2026-11-21 | A Juice Goose iP-1520 replaces the Furman CN-1800S and the Shelly Pro 1. Companion's `power` connection sends it console commands over UDP port 30333 with the generic TCP/UDP module: `DEACTIVATE`, then `SEQUP1` or `SEQDOWN1`, so pods 1 to 3 sequence a second apart. Its unswitched outlet feeds the always-on gear, pods 2 and 3 the amplifiers, and pod 1 is free. Two Kasa EP10 plugs on the powered speakers get their own connections, `speaker1` and `speaker2` at 192.168.50.46 and .47, through the Kasa Smart Plug module, with Third Party Compatibility on in the Kasa app. The speakers come on 2.5 seconds after the pods start and go off a second before they do | Decided. Outlet use and the speakers' zone proposed, pending bench test 15 |
| 2026-11-21 | Three dimmer controllers on the one universe: an ETC UFMP8 Foundry Mini Panel for the 0-10V lights on 1 to 8, a Digital Lighting Systems PD804-DMX-120 (8 forward-phase dimmers, 4 A each) on 9 to 16, and a DLS PD408-DMX-120 (4 dimmers, 8 A each) on 17 to 20. The patch sheet has one row for each output, with Controller, Output, Dimming, Load and Max load columns, every output Open until a light is assigned. Companion's area placeholders (9 to 32) wait for the Areas to be filled in | Decided. Pack addresses 9 and 17 proposed |
| 2026-11-21 | The DMX patch sheet is `config/network/dmx-patch.csv`, one row per light: its area, location, make and model, DMX mode, start channel, channel count, end channel, what each channel does, and status. It starts with the placeholder channels Companion sends today, and proposes 481 to 512 for temporary lights. build.py still has its own copy of the channels | Replaced the same day: one row per controller output, in the row above |
| 2026-11-20 | On Home, the Lights key playing glows green instead of amber, matching the green audio power key, and Lights Off stays red while the lights are off. Green means on and red means off across the deck. Light Control's areas stay amber | Decided |
| 2026-11-20 | Normal for the source faders, Bus 14, 15 and 16 and Main 1, is -20 dB instead of 0 dB, so the Volume and Bluetooth dials have 26 dB to go up before they stop at +6 dB, and 40 dB to go down. Room buttons, Default Levels and pushing the dials put them back to -20 dB. The sound at Normal is 20 dB quieter unless the gain is made up upstream | Decided |
| 2026-11-20 | Each zone key on Audio Zones glows green while it plays and red while it's off, matching the switch and the audio power key, so its state doesn't depend on its piece of the dusk picture. Its level bar is green while it plays. The Main Entry icon is now a broad overhang over double doors, with the covered space shaded | Decided |
| 2026-11-20 | Playlists shows seven playlists, Morning, Everyday, Evening, Seasonal, Calm, Pop and Upbeat, with Home in the corner. Each plays the WiiM preset of the same number. Inside, Everywhere and Back are gone from the page. Instrumental is left out for lack of a key. Music Everywhere stays as a Library block with no key | Decided |
| 2026-11-20 | More is the jumping-off point: Light Control, Audio Source, Audio Zones and Playlists on top, then iPad Mode, two blank keys and Home. Its dials match Home's. Pages 4 to 6 are Light Control, Audio Source and Audio Zones. The five per-zone pages are dropped, so a zone no longer gets its own source. Close Up leaves the deck, and only the night schedule runs it | Decided. Since 2026-11-21 the two blank keys are Turn TVs On or Off and TVs |
| 2026-11-20 | Light Control has seven areas: Cafe, Chandeliers, Entry Hall, Sconces, Soffit, Fireplace and Outside. Each has its own level, which the looks save and All Lights scales. Tap an area to pick it, with a white ring, and the third dial, Area, sets it. With the lights off, turning an area up brings it on by itself. Its DMX channels are placeholders | Proposed, pending the patch sheet |
| 2026-11-20 | Audio Source shows Auditorium, Music, Bluetooth and Lobby Stage, lit while they play and toggling like Home's keys. Its third dial sets the Bluetooth level whether or not it plays, and room buttons no longer reset that level. Lobby Event and Lobby Mix are renamed Lobby Stage | Decided |
| 2026-11-20 | The zones are Lobby, Main Entry (the courtyard pair), North Entry (70V under the soffit), Bathrooms and Vestibule, replacing Mains, Outdoor and Soffit. On Audio Zones, tap a zone to pick it. A switch names the picked zone and turns it on or off, green with Turn Off while it plays and red with Turn On while it's off, and the third dial, Zone, sets its volume. A zone switched on plays what the other zones play, or the source played last, and turns the system on | Decided |
| 2026-11-20 | Every page has a picture: dawn on Home, dusk on More, Playlists, Audio Source and Audio Zones, and night with the northern lights on Light Control. Blank keys show their piece of it | Proposed, pending a look on the hardware |
| 2026-11-19 | Home's eight keys share one picture, the sun cresting a ridge at dawn. Over the lights row the sky brightens from Lights Off, under the moon, to Lights 3, and the audio keys stand on the ridges. The touch strip is a lake reflecting the sky. A key that is on glows in its own color over its piece of the picture, with a bright ring. The picture allows for the bezel between keys through `KEY_GAP` in build.py, which is an estimate. Other pages keep their plain tiles for now | Proposed, pending a look on the hardware. Since 2026-11-20 every page has a picture |
| 2026-11-16 | The audio power key shows the state by color and says what a press does: green with Turn Audio Off while the audio is on, red with Turn Audio On while it's off. It turns green as soon as Auditorium or Music turns the audio on | Decided |
| 2026-11-16 | Audio Off turns every zone off, then powers the amplifiers down, and stays lit while they are off. Its look and label changed the same day, in the row above. Pressed again it turns the system on with nothing playing. Auditorium, Music, Bluetooth and Lobby Event are exclusive toggles that turn the system on. Everywhere, Inside, playlists and zone keys also turn it on. The Volume, Mics and zone dials do nothing while it's off, and their panels say Off. Close Up and the night schedule power it down | Decided |
| 2026-11-16 | A Furman CN-1800S sequencer powers the amplifiers, with its delay set short. Companion switches it through a Shelly Pro 1 relay on the Furman's remote terminals, in maintained mode. The Wing Rack, WiiM and Bluetooth receiver stay on all the time | Replaced 2026-11-21 by the Juice Goose iP-1520 |
| 2026-11-15 | Dials speed up when turned quickly: clicks under 120 ms apart move 2 steps, under 50 ms move 4, and a report of several clicks counts each, up to 8 steps. Reversing or changing dial starts slow. Tuned with `turn_medium_ms` and `turn_fast_ms` in Companion | Proposed, pending a feel test on the hardware |
| 2026-11-15 | Every station, the rack and each door, is a Stream Deck + with the same pages: Home on page 1, More 2, Playlists 3, zones 4 to 8. Each door's surface group starts on Home with every page, and doors are locked out by taking pages out of their group. The door front screen, Door Controls page and Door test emulator are gone | Decided. Since 2026-11-20 pages 4 to 6 are Light Control, Audio Source and Audio Zones |
| 2026-11-15 | Doors open to one Door Controls page: Lights Off, Lights 1 to 3 and a lights ring; Audio Off, Auditorium, Music, Lobby Event and a volume ring; Dimmer, Brighter, Quieter, Louder and Back. Door Audio is gone. The file includes a Door test emulator in the Door 1 group | Replaced the same day: every station is a Stream Deck + with shared pages |
| 2026-11-15 | The Volume dial moves the fader of whatever is playing: Bus 14, 15 or 16, or Main 1 in a Lobby Event. Room buttons reset Bus 14 to 16 but not Main 1. Zone faders change only on zone pages | Decided |
| 2026-11-15 | Companion keeps its own copy of zone levels, mic level and mute, a Volume offset from normal, and shows the Wing's values when it reports them, with a NO WING badge otherwise. Keys hide Companion's status marks. Artwork redrawn: bigger icons, brighter resting tiles, bulb icons for Lights 1 to 3 | Proposed, pending a look on the hardware |
| 2026-11-15 | The Stream Deck file carries the Elgato surface integration and four surface groups, Rack and Door 1 to 3, with startup pages and page permissions. Each deck joins its group | Proposed, pending bench test 13 |
| 2026-11-15 | The Stream Deck file uses Companion 5 layered buttons: lit and locked key art, and live touch-strip panels with level bars. Its 60 images live in Companion's image library | Proposed, pending bench test 13 |
| 2026-11-15 | Looks are saved at any station by holding a Lights key for 3 seconds, which also writes them to Companion's startup values so exports keep them | Proposed, pending bench test 7 |
| 2026-11-15 | Doors show Lights Off, Lights 1 to 3, a level ring, Dimmer and Brighter, in place of the eight named presets | Replaced: doors share the rack's pages |
| 2026-11-15 | Companion sends the lights as Art-Net to the ODE through its generic-artnet module. The S-Play Mini is dropped | Decided |
| 2026-11-15 | Lighting engine for the light dials, replacing the S-Play Mini, which can't dim live: DMX Core 100, Lumen, Pharos LPC, QLC+ or Companion's own Art-Net module | Replaced: Companion's own Art-Net module was chosen |
| 2026-11-15 | Wireless mics reach every zone in every source mode through their own bus, and the Mic dial sets their level | Decided. Since 2026-11-22 the dial moves channel 1, the mic, and the bus is fixed |
| 2026-11-15 | Rack main page: Lights Off, 1, 2 and 3 on top; Audio Off, Auditorium, Music and More below; dials for all lights, linear lights, volume and mic | Decided |
| 2026-11-11 | Rack deck stays a Stream Deck +, with a simple main page of 7 keys and 3 knobs: light levels 1 to 3, lights off, stream, auditorium, audio off, and knobs for volume, brightness and mic | Stream Deck + decided, the + XL is too much for volunteers. Layout replaced by the 2026-11-15 row |
| 2026-11-11 | Rack deck: Stream Deck + XL (36 keys, 6 dials), Stream Deck + (8 keys, 4 dials) or a keys-only deck | Replaced by the row above |
| 2026-11-04 | Door deck: Stream Deck Module 15 Keys or MK.2 | Replaced on 2026-11-15: every station is a Stream Deck + |
| 2026-11-04 | iPad Mode is held for one second, so a stray press cannot black out the lobby | Proposed |
| 2026-11-04 | Page 3 becomes Door Audio with room buttons | Replaced on 2026-11-15 by the single Door Controls page |
| 2026-11-04 | Doors lock by checking `light_mode`, replacing the Door iPad page and any door surface IDs | Proposed, pending bench test |
| 2026-11-04 | Stream Deck pages, icons and the import file live in `config/stream-deck/`, built by one script | Proposed, pending bench test |
| 2026-11-04 | Playlist source: SharePoint folders or Spotify | Open, SharePoint folders recommended |
| 2026-11-04 | Lobby music is covered by the church's broader music license | Decided |
| 2026-11-04 | The `docs/` folder is the long-term record of the plan | Decided |
| 2026-11-04 | Playlists run on a WiiM Pro Plus, which can play Spotify presets or m3u playlists of files | Proposed, pending bench test |
| 2026-11-04 | Door stations use a front screen and mounting height first, with covers only if needed | Changed on 2026-11-15: mounting height and page lockout per door, with no front screen |
| 2026-11-04 | iPad Mode is set from the rack station and locks the door stations | Proposed, pending bench test. Since 2026-11-15, any station with the More page can set it, so lock doors out of More |
| 2026-11-04 | ODE Mk3 merges presets and iPad over Art-Net, with sACN priority as Plan B | Proposed, pending bench test. Since 2026-11-15 the two sources are Companion and the iPad |
| 2026-11-04 | S-Play Mini stores the presets, one playlist each, with a limit of eight | Dropped on 2026-11-15, because it can't drive the light dials |
| 2026-11-04 | Launch with static looks and add active looks later | Decided |
| 2026-11-04 | Use one system for lighting and audio, run by Bitfocus Companion with Stream Decks | Proposed, pending bench test |
| 2026-11-04 | Speaker zones live in Wing Rack matrices | Proposed, pending bench test |
| 2026-11-04 | Rack station is required and handles audio and lighting. Audio at the doors is optional | Decided |
| 2026-11-04 | Emergency lighting stays outside this system | Decided |
| 2026-11-04 | Auditorium feed is an analog run to the Wing Rack | Decided |
