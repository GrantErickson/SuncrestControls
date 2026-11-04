# Testing

Buy one door station, the Stream Deck +, the S-Play Mini and the ODE Mk3 first, then pass these 14 tests before ordering the rest. Each one covers something the documentation couldn't confirm.

| # | Test | Pass means | If it fails |
| --- | --- | --- | --- |
| 1 | Cut power to the dock and Companion, repeatedly | The door reconnects by itself within a minute | Use [Companion Satellite](https://companion.free/user-guide/surfaces/satellite) on a Pi at the door |
| 2 | Leave the door station running for two weeks | No dropped connections | Same as test 1 |
| 3 | Press all eight presets in turn | Each replaces the last with a clean fade | Review playlist Groups |
| 4 | Send `/lobby/off` once | Every playlist stops | Make All Off a blank preset |
| 5 | Enter iPad Mode and run the iPad over Wi-Fi | Smooth control and no flicker | Try Plan B, sACN priority |
| 6 | Close the lighting app during iPad Mode | The lights do something acceptable | Try Plan B, sACN priority |
| 7 | Capture a look with DMX Snapshot through ODE Port 2 | The saved cue matches the lights | Point Luminair at the S-Play while capturing |
| 8 | Change sends, mutes and faders from Companion | All 20 sends and 5 matrices respond | Send OSC directly on port 2223, such as `/bus/14/send/MX1/on` |
| 9 | Keep the Wing app open while using Companion | Button status stays correct | See the note below |
| 10 | Recall a band snapshot | Zones don't change | Set scope on each band snapshot |
| 11 | Start a WiiM preset by HTTP with no phone nearby | The playlist plays, including a song added after the preset was saved | Try the [Companion Spotify module](https://github.com/bitfocus/companion-module-spotify-remote) or another player |
| 12 | Turn the Stream Deck + dials | Zone volume follows smoothly, and the strip shows the level. Volume stops at 0 dB and -60 dB | Use keys for volume up and down |
| 13 | Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig) into Companion 5.1.2 or newer | All pages, 3 connections, 10 variables and 4 triggers appear, with no log errors, and each key runs its [listed action](14-stream-deck-pages.md) | Report the error, fix `build.py` and import again. Build the keys by hand from the same reference if it can't be fixed |
| 14 | Hold the front key, press a door preset, and leave a door idle | Hold opens lights, a choice returns in 5 seconds, and idle returns in 30 seconds. iPad Mode locks these keys on every door, including one rebooted during it | Change the times in the key, or send doors to a locked page by surface ID |

Test 9 matters because the Wing [allows one active subscription](https://github.com/bitfocus/companion-module-behringer-wing), and the newest subscriber is the only receiver. If status goes stale, commands should still work. Trust the custom variables for status rather than the Wing's reported state.

## Build order

1. **Bench.** Run the tests above.
2. **Lighting and doors.** Program presets, install door stations, and hand them to volunteers.
3. **Audio.** Configure the Wing Rack and build the rack station.
4. **Extras.** Add the schedule, active looks and door audio.

## Commissioning checklist

- [ ] Every preset works from every door and from the rack
- [ ] Every zone plays each source, and only the chosen one
- [ ] Zone levels are set during a real service
- [ ] Turning off the whole rack and back on returns the last lighting preset
- [ ] An iPad event rehearsal runs from start to finish
- [ ] A band rehearsal runs with the Wing app and the zones working together
- [ ] Bluetooth pairs from an ordinary phone
- [ ] Someone new can choose a preset without help
- [ ] Companion, S-Play and Wing backups are saved in the repo
