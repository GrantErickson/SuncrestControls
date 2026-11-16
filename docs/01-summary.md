# Summary

One controller, Bitfocus Companion, will run lobby lighting and audio from identical Stream Deck + stations at the doors and beside the rack. The core is configuration, not custom code. Lay people change light looks and playlists without touching it.

The design is not final until the bench tests pass. Those tests are cheap, and they cover the few things the manufacturers' documents could not confirm.

| # | Your answer | What it means for the design |
| --- | --- | --- |
| 1 | One DMX universe | Companion sends one Art-Net universe, and one DMX node is enough |
| 2 | Emergency lights are separate, with batteries | No bypass hardware in this system |
| 3 | Covers, height, or a do-nothing front screen | Start with a sensible height and each door limited to the pages it needs. Add a PIN lockout or covers only if needed |
| 4 | Static is fine, active would be nice | Launch with static looks and add active ones later |
| 5 | iPad overrides the door stations | iPad Mode locks the door stations out of lighting |
| 6 | Schedule is a nice-to-have | Add it after launch using Companion time-of-day triggers |
| 7 | Analog run from the auditorium | A balanced stereo pair into two Wing Rack inputs |
| 8 | Each zone has an amp channel | Zones can be fully independent |
| 9 | Audio is required at the rack, optional at doors | Every station has lights and audio on its main page. Each door's group can drop the other pages |
| 10 | Band is handled, with analog and AES50 | Zones must not collide with band outputs |
| 11 | Spotify playlists, a few to choose from | A streaming player with selectable playlists, under the church music license |
| 12 | Bluetooth at the rack | A receiver in the rack, feeding one Wing input |
| 13 | Technical people exist, lay people change content | Lay people save a light look by holding its key, and change playlists outside Companion |
| 17, 18 | A Stream Deck + at the rack, with a simple main page | Lights Off and Lights 1 to 3 on top, Audio Off, Auditorium, Music and More below |
| 20 | Dials for all lights, linear lights, volume and mics. Mics always on | Companion sends the lights itself, and the mics reach every zone through their own bus |
| 28 | Volume follows what is selected, not the mains | The Volume dial moves the fader of whatever is playing |
| 29 | Every station is a Stream Deck +, with the same functionality | All stations share one set of pages, and you lock doors out of pages in Companion |
