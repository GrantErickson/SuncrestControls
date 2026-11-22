# Open items

The church's broader music license settles the licensing question, so these remaining items are checks and small decisions.

- [ ] Choose the playlist source, SharePoint folders or Spotify, and record the church's music license in the brief
- [ ] Choose two or three door stations
- [ ] Choose which pages each door may use, and set them in its surface group
- [ ] Choose a shelf or angled plate for the Stream Deck + at each door
- [ ] Confirm the band doesn't need Wing Rack Local outputs 1 to 7
- [ ] Confirm mounting height with the architect
- [ ] Name a primary and backup technical owner
- [ ] Fill in the [DMX patch sheet](../config/network/dmx-patch.csv) as fixtures are chosen and addressed
- [ ] Fill in the real DMX patch in `22/1/0` Compute DMX, from the patch sheet, including which fixtures belong to each light area: Cafe, Chandeliers, Entry Hall, Sconces, Soffit, Fireplace and Outside
- [ ] Measure a Stream Deck + key and the gap between two keys, and set `KEY_GAP` in build.py so each page's picture lines up across the keys
- [ ] Decide what goes on the two blank keys on Audio Source, if anything
- [ ] Walk the room and save Lights 1 to 3 by holding each key
- [ ] Confirm the default zone choices for each whole-room button
- [ ] Ask the fire alarm contractor whether audio must mute on alarm. The Juice Goose has no alarm input, so if it must, plan another way
- [ ] Add up the current draw of everything on the Juice Goose, which is rated 20 A, and give it a 20 A circuit with a NEMA 5-20 receptacle
- [ ] Decide what goes on Juice Goose pod 1, if anything
- [ ] Confirm which zone the powered speakers serve, and that the AV Wi-Fi reaches their Kasa plugs
- [ ] Set up one BRAVIA 3 II on the bench and check Remote start and Simple IP control turn it on and switch its inputs, before ordering the other six. See [TVs](15-tvs.md#setting-up-each-bravia-3-ii)
- [ ] Fill in the [TV sheet](../config/network/tvs.csv) as the TVs go up: location, size, serial, MAC address and firmware
- [ ] Get the ATEM's real address and route UDP 9910 to it from the Companion host, then replace the placeholder, 192.168.10.240, in the `atem` connection
- [ ] Choose the ATEM source for the SDI key, now Black, and whether to give the key a friendlier name
- [ ] Count the ATEM's control connections with production, since Companion adds one
- [ ] Confirm what each TV shows when it comes on. The proposal: the stream in the Kitchen and Back Stage, announcements everywhere else
- [ ] Decide whether the morning schedules turn the TVs on
- [ ] Later, not yet: one button that turns everything on, the lights, the audio and the TVs
- [ ] Confirm battery lights come on with no help from DMX
- [ ] Confirm the Denon DN-200BR is still available, or pick another receiver with line outputs
- [ ] Confirm the starting matrix levels and the seven playlist names, and that the WiiM holds seven presets
- [ ] Pass all 16 bench tests, including the first real import of the Stream Deck file and test 4, what the ODE does when Companion stops
- [ ] Set the mic channel levels so Bus 13 at 0 dB stays below feedback in every zone
- [ ] Choose whether swiping the touch strip turns pages. The setup turns it off
