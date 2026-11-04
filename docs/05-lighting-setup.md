# Lighting setup

The S-Play Mini holds up to eight presets, and the ODE Mk3 turns them into DMX on your one universe. Each preset is one S-Play playlist, started by an OSC message from Companion.

Eight is a hard ceiling. The [S-Play Mini manual](https://support.enttec.com/user-manuals/s-play-mini) lists 8 playlists, 16 cues and 16 triggers. ENTTEC's [product page](https://www.enttec.com/product/lighting-show-controller/s-play-mini-2-universe-smart-light-show-controller/) lists higher numbers, so plan on the manual and check your unit.

## Wire the DMX

1. Address every fixture and 0-10V decoder, and record them on a DMX patch sheet.
2. Run ODE Port 1 to the fixture DMX line, and terminate the end of the line.
3. Run a short DMX cable from ODE Port 2 to the S-Play DMX port. This lets the S-Play capture exactly what is on the lights.

## Set up the ODE Mk3

Steps follow the [ODE Mk3 manual](https://support.enttec.com/user-manuals/ode-mk3).

1. Connect the ODE alone and browse to its address. Without DHCP it falls back to 192.168.0.10.
2. On the Settings tab, turn off DHCP and set 192.168.50.31.
3. Set Port 1 to DMX OUT, Art-Net, universe 0, merge HTP.
4. Set Port 2 to DMX OUT, Art-Net, universe 0, merge HTP.
5. Save, then record the settings in the repo.

## Set up the S-Play Mini

1. Connect the S-Play alone and browse to its address. The default login is `user` and `123456`.
2. On the Settings page, set 192.168.50.30. The unit reboots.
3. Download a backup from the Storage page, then change the password.
4. In Output Settings, set Out 1 to Art-Net, universe 0, unicast to 192.168.50.31, at 30 FPS.
5. Set the DMX port as an input so it can capture from the ODE.
6. Confirm OSC input is on port 8000, the default.
7. In Settings, turn on **Restrict to one active playlist per Group**. This is what makes presets replace each other instead of merging.
8. Leave **Send black frame when all playlists stopped** on.

## Build the presets

These names are starting points. Rename them after walking the room.

| Preset | Suggested use | OSC address |
| --- | --- | --- |
| Sunday Morning | Services | /lobby/preset/1 |
| Everyday | Weekday hours | /lobby/preset/2 |
| Bright | Cleaning and setup | /lobby/preset/3 |
| Evening | Warm evening look | /lobby/preset/4 |
| Event | Receptions and gatherings | /lobby/preset/5 |
| Walkthrough | Low light for moving through | /lobby/preset/6 |
| Seasonal | Christmas, Easter and similar | /lobby/preset/7 |
| Night | Late hours | /lobby/preset/8 |
| All Off | Stops every playlist | /lobby/off |

1. On the Triggers page, create one OSC trigger per row above. Addresses must start with `/`.
2. Create a static cue for each preset. Choose **All/W** for single-channel dimmers and house lights.
3. Set the look by typing values and pressing **Set DMX**, or capture a live look with **DMX Snapshot**.
4. Preview the cue, then save it.
5. Create a playlist for each preset, put its cue on the timeline, and set Play Count to Infinity.
6. Set the cue's fade time. Two to three seconds feels natural in a lobby.
7. Put all eight playlists in the same Group.
8. Set each playlist's Start Trigger to its preset, and its Stop Trigger to All Off.
9. Test each preset with the S-Play play button, then by OSC from Companion.

The manual doesn't say whether one trigger can stop several playlists. If it can't, make **All Off** a blank preset, which uses one of the eight.

## Connect the iPad

For Luminair, follow [ENTTEC's Wi-Fi guide](https://support.enttec.com/dmx/edmx-art-net-sacn-networking/edmx-art-net-sacn-sending-over-wifi):

1. Join the AV Wi-Fi.
2. Tap the status icon in the upper right and select Art-Net.
3. Confirm output is enabled and that universe and subnet are 0.
4. Open node settings and select the ODE at 192.168.50.31. This switches Luminair to unicast.

For your own app, send Art-Net to 192.168.50.31, universe 0, from one IP address.

## How the iPad override works

The ODE merges two sources and the highest level wins. Pressing **iPad Mode** stops the S-Play, which sends black, so the iPad's levels are the only ones left. Companion also locks the door stations.

- **One iPad at a time.** The ODE [ignores any third source](https://support.enttec.com/user-manuals/ode-mk3).
- **If the iPad drops.** The ODE discards a lost source after 4 seconds. What the lights do next is a bench test.
- **Plan B.** Switch S-Play, ODE and iPad to sACN, with the S-Play at priority 50. The iPad then wins automatically, and lights fall back to the last preset if it stops. Use this only if Luminair's sACN proves stable on your Wi-Fi.

## Temporary lights

Put special-occasion fixtures on unused addresses at the end of the universe. Presets leave those channels at 0, and the iPad controls them.

## Adding active looks later

Active looks are a content change, not a redesign. There are two routes:

- **Effect cue.** Build gradients and effects in the S-Play web interface.
- **Dynamic cue.** Press iPad Mode, run the look from the iPad, and record it with **Start Rec**. Turn on **Perfect Loop** to end cleanly.

Every active look uses part of the 16-cue limit. Run recordings in iPad Mode, since the manual says the S-Play shouldn't output on the same universe while recording.
