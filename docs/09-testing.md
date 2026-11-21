# Testing

Buy one Stream Deck + with a Network Dock and the ODE Mk3 first, then pass these 15 tests before ordering the rest. Each one covers something the documentation couldn't confirm. Test 15 needs the Furman and the relay, so it can wait until they arrive.

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
| 13 | Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig) into Companion 5.1.3 or newer | 11 pages, 4 connections, 64 variables, 4 triggers and 113 library images appear with no log errors. Every key shows its artwork, each page's picture lines up across its keys, and each key runs its [listed action](14-stream-deck-pages.md) | Report the error, fix `build.py` and import again. Build the keys by hand from the same reference if it can't be fixed. If a picture breaks at the bezels, measure the deck and set `KEY_GAP` in `build.py` |
| 14 | Put the + in the Door 1 group and take More out of that group's pages. Press **More**, then choose a look and a source | More stays on Home, and every Home key and dial works like the rack's. iPad Mode locks the lighting keys on every station, including one rebooted during it | Clear the More key on door decks by surface, or report the Companion behavior |
| 15 | Wire the relay to the Furman. Press Turn Audio Off, then Auditorium, Auditorium again, Music, and Auditorium. Restart Companion with the audio on, then with it off | The power key turns red and says Turn Audio On, the Furman sequences the amplifiers off, and the Volume, Mics, Bluetooth and Zone dials do nothing while their panels are grey. Auditorium turns the amplifiers on, the power key turns green and says Turn Audio Off, and the sound plays within a few seconds, and pressing it again silences it with the amplifiers still on. Music and Auditorium swap. After each restart the amplifiers match the power key, and the speakers never pop | Check the Furman's key switch and DIP switches 5 and 7. If the relay won't do, switch the Furman with its BB-RS232 adapter instead |

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
- [ ] Companion and Wing backups are saved in the repo
