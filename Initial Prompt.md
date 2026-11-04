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
11. **Music:** We have Spotify. A playlist we can keep updated online would be great, and a few to choose from would be cool. We could also download music.
12. **Bluetooth:** The rack is on the side of the lobby and can be used for Bluetooth.

### Ownership

13. **Long-term care:** Not sure who owns it yet, but we do have technical people. The core setup shouldn't need to change much, and things like light settings and playlists should be easy for lay people to change.

## Decision log

Newest first. Add a row whenever a decision is made or changed.

| Date | Decision | Status |
|---|---|---|
| 2026-11-04 | The `docs/` folder is the long-term record of the plan | Decided |
| 2026-11-04 | Playlists run on a WiiM Pro Plus with Spotify presets, with licensing still to settle | Proposed, licensing open |
| 2026-11-04 | Door stations use a front screen and mounting height first, with covers only if needed | Proposed |
| 2026-11-04 | iPad Mode is set from the rack station and locks the door stations | Proposed, pending bench test |
| 2026-11-04 | ODE Mk3 merges presets and iPad over Art-Net, with sACN priority as Plan B | Proposed, pending bench test |
| 2026-11-04 | S-Play Mini stores the presets, one playlist each, with a limit of eight | Proposed, pending bench test |
| 2026-11-04 | Launch with static looks and add active looks later | Decided |
| 2026-11-04 | Use one system for lighting and audio, run by Bitfocus Companion with Stream Decks | Proposed, pending bench test |
| 2026-11-04 | Speaker zones live in Wing Rack matrices | Proposed, pending bench test |
| 2026-11-04 | Rack station is required and handles audio and lighting. Audio at the doors is optional | Decided |
| 2026-11-04 | Emergency lighting stays outside this system | Decided |
| 2026-11-04 | Auditorium feed is an analog run to the Wing Rack | Decided |
