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

## Decision log

Newest first. Add a row whenever a decision is made or changed.

| Date | Decision | Status |
|---|---|---|
| 2026-11-16 | The audio power key shows the state by color and says what a press does: green with Turn Audio Off while the audio is on, red with Turn Audio On while it's off. It turns green as soon as Auditorium or Music turns the audio on | Decided |
| 2026-11-16 | Audio Off turns every zone off, then powers the amplifiers down, and stays lit while they are off. Its look and label changed the same day, in the row above. Pressed again it turns the system on with nothing playing. Auditorium, Music, Bluetooth and Lobby Event are exclusive toggles that turn the system on. Everywhere, Inside, playlists and zone keys also turn it on. The Volume, Mics and zone dials do nothing while it's off, and their panels say Off. Close Up and the night schedule power it down | Decided |
| 2026-11-16 | A Furman CN-1800S sequencer powers the amplifiers, with its delay set short. Companion switches it through a Shelly Pro 1 relay on the Furman's remote terminals, in maintained mode. The Wing Rack, WiiM and Bluetooth receiver stay on all the time | Proposed, pending bench test 15 and the amplifiers' current draw |
| 2026-11-15 | Dials speed up when turned quickly: clicks under 120 ms apart move 2 steps, under 50 ms move 4, and a report of several clicks counts each, up to 8 steps. Reversing or changing dial starts slow. Tuned with `turn_medium_ms` and `turn_fast_ms` in Companion | Proposed, pending a feel test on the hardware |
| 2026-11-15 | Every station, the rack and each door, is a Stream Deck + with the same pages: Home on page 1, More 2, Playlists 3, zones 4 to 8. Each door's surface group starts on Home with every page, and doors are locked out by taking pages out of their group. The door front screen, Door Controls page and Door test emulator are gone | Decided |
| 2026-11-15 | Doors open to one Door Controls page: Lights Off, Lights 1 to 3 and a lights ring; Audio Off, Auditorium, Music, Lobby Event and a volume ring; Dimmer, Brighter, Quieter, Louder and Back. Door Audio is gone. The file includes a Door test emulator in the Door 1 group | Replaced the same day: every station is a Stream Deck + with shared pages |
| 2026-11-15 | The Volume dial moves the fader of whatever is playing: Bus 14, 15 or 16, or Main 1 in a Lobby Event. Room buttons reset Bus 14 to 16 but not Main 1. Zone faders change only on zone pages | Decided |
| 2026-11-15 | Companion keeps its own copy of zone levels, mic level and mute, a Volume offset from normal, and shows the Wing's values when it reports them, with a NO WING badge otherwise. Keys hide Companion's status marks. Artwork redrawn: bigger icons, brighter resting tiles, bulb icons for Lights 1 to 3 | Proposed, pending a look on the hardware |
| 2026-11-15 | The Stream Deck file carries the Elgato surface integration and four surface groups, Rack and Door 1 to 3, with startup pages and page permissions. Each deck joins its group | Proposed, pending bench test 13 |
| 2026-11-15 | The Stream Deck file uses Companion 5 layered buttons: lit and locked key art, and live touch-strip panels with level bars. Its 60 images live in Companion's image library | Proposed, pending bench test 13 |
| 2026-11-15 | Looks are saved at any station by holding a Lights key for 3 seconds, which also writes them to Companion's startup values so exports keep them | Proposed, pending bench test 7 |
| 2026-11-15 | Doors show Lights Off, Lights 1 to 3, a level ring, Dimmer and Brighter, in place of the eight named presets | Replaced: doors share the rack's pages |
| 2026-11-15 | Companion sends the lights as Art-Net to the ODE through its generic-artnet module. The S-Play Mini is dropped | Decided |
| 2026-11-15 | Lighting engine for the light dials, replacing the S-Play Mini, which can't dim live: DMX Core 100, Lumen, Pharos LPC, QLC+ or Companion's own Art-Net module | Replaced: Companion's own Art-Net module was chosen |
| 2026-11-15 | Wireless mics reach every zone in every source mode through their own bus, and the Mic dial sets their level | Decided |
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
