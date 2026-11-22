# Testing

Buy one Stream Deck + with a Network Dock and the ODE Mk3 first, then pass these 16 tests before ordering the rest. Each one covers something the documentation couldn't confirm. Test 15 needs the Juice Goose and the speaker plugs, so it can wait until they arrive.

| # | Test | Pass means | If it fails |
| --- | --- | --- | --- |
| 1 | Cut power to the dock and Companion, repeatedly | The door reconnects by itself within a minute | Use [Companion Satellite](https://companion.free/user-guide/surfaces/satellite) on a Pi at the door |
| 2 | Leave the door station running for two weeks | No dropped connections | Same as test 1 |
| 3 | Press Lights Off and Lights 1 to 3 from a door and the rack, then turn both light dials | Each look fades in over 2 seconds, and the dials move the lights smoothly with no steps or flicker | Raise the Quick fade in `22/1/2`, or lower the Art-Net module's fade interval |
| 4 | With the lights on, stop Companion, wait a minute, then start it | Record whether the ODE holds the last look or goes dark after 4 seconds. Either way, the look returns 5 seconds after Companion starts | If dark is unacceptable, look for an ODE hold-last-look setting, or plan the lighting iPad as the fallback |
| 5 | Enter iPad Mode and run the iPad over Wi-Fi | Smooth control and no flicker | Try Plan B, sACN priority |
| 6 | Close the lighting app during iPad Mode | The lights do something acceptable | Try Plan B, sACN priority |
| 7 | Set the light dials, hold Lights 2 for 3 seconds, then pick Lights 3 and back to Lights 2 from a door | The key turns green and says Saved, and Lights 2 returns exactly as saved. An export shows the new values as startup values | Check the Save block on page 22 |
| 8 | Change sends, mutes and faders from Companion | All 20 sends and 5 matrices respond | Send OSC directly on port 2223, such as `/bus/14/send/MX1/on` |
| 9 | Keep the Wing app open while using Companion | Button status stays correct | See the note below |
| 10 | Recall a band snapshot | Zones don't change | Set scope on each band snapshot |
| 11 | Start a WiiM preset by HTTP with no phone nearby | The playlist plays, including a song added after the preset was saved | Try the [Companion Spotify module](https://github.com/bitfocus/companion-module-spotify-remote) or another player |
| 12 | Turn and push all four Stream Deck + dials, slowly and quickly, on Home, Light Control, Audio Source and Audio Zones | Each follows smoothly and the strip shows its value and bar. Slow turns move one step a click and quick turns skip ahead, and a quick turn still stops exactly at each limit. Volume moves whatever is playing, reads Normal at -20 dB, and stops at +6 dB (26 dB over normal) and at -60 dB, the Area dial moves only the picked area, the Bluetooth dial moves Bluetooth whether or not it plays, the Zone dial moves only the picked zone and stops it at 0 dB, the mics stop at 0 dB, and pushing Mics mutes them. Unplug the Wing's network cable: NO WING appears and the dials keep moving, and plugging it back in makes the panels follow the Wing again | Use keys for volume up and down |
| 13 | Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig) into Companion 5.1.3 or newer | 23 pages, 14 connections, 75 variables, 4 triggers and 173 library images appear with no log errors. Every key shows its artwork, each page's picture lines up across its keys, and each key runs its [listed action](14-stream-deck-pages.md) | Report the error, fix `build.py` and import again. Build the keys by hand from the same reference if it can't be fixed. If a picture breaks at the bezels, measure the deck and set `KEY_GAP` in `build.py` |
| 14 | Put the + in the Door 1 group and take More out of that group's pages. Press **More**, then choose a look and a source | More stays on Home, and every Home key and dial works like the rack's. iPad Mode locks the lighting keys on every station, including one rebooted during it | Clear the More key on door decks by surface, or report the Companion behavior |
| 15 | Set up the Juice Goose with UDP on and the speaker plugs with Third Party Compatibility on. Press Turn Audio Off, then Auditorium, Auditorium again, Music, and Auditorium. Restart Companion with the audio on, then with it off | The power key turns red and says Turn Audio On, the speaker plugs turn off, then the Juice Goose's pods go off 3, 2, 1, and the Volume, Mics, Bluetooth and Zone dials do nothing while their panels are grey. Auditorium sequences the pods on 1, 2, 3, then turns the speaker plugs on, the power key turns green and says Turn Audio Off, and the sound plays within a few seconds, and pressing it again silences it with the amplifiers still on. Music and Auditorium swap. After each restart the amplifiers and the plugs match the power key, and the speakers never pop. The front rocker doesn't override Companion | If the Juice Goose ignores `DEACTIVATE`, try the manual's other spelling, `DECACTIVATE`. If it ignores everything, check UDP is enabled, or switch the `power` connection to TCP port 33333. If Companion can't find a plug, turn on Third Party Compatibility in the Kasa app and check the plug's address |
| 16 | On More, press Turn TVs On, then open TVs and each TV's page. Choose each thing a TV can show, turn a TV off and on with its switch, then press Turn TVs Off. With one TV and the ATEM connected, repeat it watching that TV and its ATEM output in ATEM Software Control, starting from the TV in standby | Every TV comes on showing its default, the lit key matches what each TV shows, a TV turned back on shows its default again, and every TV goes off. With only some TVs on, the More key stays green and says how many. The TV wakes within a few seconds on the right input. Stream, Announcements, Custom and SDI change its ATEM output and no other. Local HDMI shows the wall plate. USB only turns it on | If the TV won't turn on from standby, check Remote start, or Control remotely on newer firmware. If its `tv` connection is red, check Simple IP control is on and the TV's address. If it turns on but ignores the input, look at the TV's last reply, `$(tv1:tcp_response)` for TV 1, on Companion's Variables page: `*SAINPT0000000000000000` means it took the input, and sixteen F's mean it refused. If the input is wrong after waking, raise `TV_WAKE_MS` in `build.py`. If the ATEM doesn't change, check the `atem` connection, the route to it, and the output number in the TV's Send block on pages 25 to 28 |

Test 9 matters because the Wing [allows one active subscription](https://github.com/bitfocus/companion-module-behringer-wing), and the newest subscriber is the only receiver. If status goes stale, commands should still work. Trust the custom variables for status rather than the Wing's reported state.

## Build order

1. **Bench.** Run the tests above.
2. **Lighting and doors.** Set the patch, save the three looks in the room, install door stations, and hand them to volunteers.
3. **Audio.** Configure the Wing Rack and build the rack station.
4. **Extras.** Add the schedule and active looks.

## Commissioning checklist

- [ ] Every look works from every door and from the rack, and the dials work
- [ ] Every zone plays each source, and only the chosen one
- [ ] Zone levels are set during a real service
- [ ] Turning off the whole rack and back on returns the last look
- [ ] An iPad event rehearsal runs from start to finish
- [ ] A band rehearsal runs with the Wing app and the zones working together
- [ ] Bluetooth pairs from an ordinary phone
- [ ] Someone new can choose a look and save one without help
- [ ] The audio power key turns the amplifiers off and back on, with no pop from any speaker
- [ ] Every TV comes on with its default from Turn TVs On, and each shows all six choices
- [ ] Every TV has its fixed address, Simple IP control and Remote start on, Idle TV standby and BRAVIA Sync off, and its `tv` connection is green. The TV sheet has its serial, MAC address and firmware
- [ ] Each TV's ATEM output is named for it in ATEM Software Control, and production knows not to route those outputs
- [ ] Companion and Wing backups are saved in the repo
