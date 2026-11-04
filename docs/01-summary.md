# Summary

One controller, Bitfocus Companion, will run lobby lighting and audio from Stream Decks at the doors and beside the rack. The core is configuration, not custom code. Lay people change light looks and playlists without touching it.

The design is not final until the bench tests pass. Those tests are cheap, and they cover the few things the manufacturers' documents could not confirm.

| # | Your answer | What it means for the design |
| --- | --- | --- |
| 1 | One DMX universe | One preset player and one DMX node are enough |
| 2 | Emergency lights are separate, with batteries | No bypass hardware in this system |
| 3 | Covers, height, or a do-nothing front screen | Start with a front screen and a sensible height, and add covers only if needed |
| 4 | Static is fine, active would be nice | Launch with static looks and add active ones later |
| 5 | iPad overrides the door stations | iPad Mode locks the door stations out of lighting |
| 6 | Schedule is a nice-to-have | Add it after launch using Companion time-of-day triggers |
| 7 | Analog run from the auditorium | A balanced stereo pair into two Wing Rack inputs |
| 8 | Each zone has an amp channel | Zones can be fully independent |
| 9 | Audio is required at the rack, optional at doors | The rack station does everything. Doors get lighting first |
| 10 | Band is handled, with analog and AES50 | Zones must not collide with band outputs |
| 11 | Spotify playlists, a few to choose from | A streaming player with selectable playlists, under the church music license |
| 12 | Bluetooth at the rack | A receiver in the rack, feeding one Wing input |
| 13 | Technical people exist, lay people change content | Separate what lay people change from the core setup |
