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
- [ ] Run the Samsung home TV test on the Main Lobby TV, a UN50U8000FDXZA at 192.168.0.126: pairing, power from standby and from fully off, and the HDMI 1 and 2 keys. Then decide Samsung or Sony for the lobby. See [TVs](15-tvs.md#trying-a-samsung-home-tv)
- [ ] Set up one BRAVIA 3 II on the bench and check Remote start and Simple IP control turn it on and switch its inputs, before ordering the other six. See [TVs](15-tvs.md#setting-up-each-bravia-3-ii)
- [ ] Fill in the [TV sheet](../config/network/tvs.csv) as the TVs go up: location, size, serial, MAC address and firmware
- [ ] Decide how Companion and the Wing app iPad reach the Wing at 192.168.0.30, outside the planned 192.168.50 network: move the AV VLAN to 192.168.0, or route UDP 2223 to the Wing. See [Network plan](04-network-plan.md)
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
- [ ] Set Bus 13's fader so the mic, on channel 1, stays below feedback in every zone with its fader at +10 dB, the top of the Mics dial
- [ ] Choose whether swiping the touch strip turns pages. The setup turns it off
