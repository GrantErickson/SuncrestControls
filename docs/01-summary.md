# Summary

One controller, Bitfocus Companion, will run lobby lighting, audio and TVs from identical Stream Deck + stations at the doors and beside the rack. The core is configuration, not custom code. Lay people change light looks and playlists without touching it.

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
| 17, 18 | A Stream Deck + at the rack, with a simple main page | Lights Off and Lights 1 to 3 on top, the audio power key, Auditorium, Music and More below |
| 20 | Dials for all lights, linear lights, volume and mics. Mics always on | Companion sends the lights itself, and the mics reach every zone through their own bus |
| 28 | Volume follows what is selected, not the mains | The Volume dial moves the fader of whatever is playing |
| 29 | Every station is a Stream Deck +, with the same functionality | All stations share one set of pages, and you lock doors out of pages in Companion |
| 31, 32 | The audio key turns off the rack power and shows whether it's on. Auditorium and Music are exclusive toggles that turn it on | A Juice Goose iP-1520 sequences the amplifiers' power and Kasa plugs switch the powered speakers, both commanded by Companion. The audio key is green and says Turn Audio Off while the audio is on, and red and says Turn Audio On while it's off. The audio dials rest while it's off |
| 33 | Better-looking buttons, with a picture that spans them | Each page shows one picture across its keys: dawn on Home, dusk on More and the audio pages, night on Light Control, and the blue hour on the TV pages. A lit key glows in its color with a bright ring |
| 34 | More is a jumping-off point: Light Control, Audio Source, Audio Zones, Playlists, iPad Mode and Home | Light Control and Audio Zones work by tapping an area or zone, then turning a dial. Audio Source shows what plays, with a Bluetooth level dial. Close Up and the per-zone source pages are gone |
| 36 | Playlists: drop Inside and Everywhere, add Calm, Pop and Upbeat | Seven playlists and Home, each playing the WiiM preset of the same number |
| 43 | TVs: a switch for them all on More, and a page for each TV to turn it on or off and choose Stream, Announcements, USB, Custom or Local HDMI | More has Turn TVs On or Off and a TVs key. TVs lists all seven, green while on. Each TV comes on showing its default |
| 44 | Sony BRAVIA TVs, maybe Samsung. The ATEM 4 M/E feeds each TV from its own output, and Companion switches the TV to that HDMI input, then the output's source. A button for everything on, later | Sony Professional Displays or Samsung commercial displays work dependably with Companion. Samsung home TVs don't. Each TV's Send block now turns it on or off, sets its ATEM output and its input. The ATEM's model, address, outputs and sources are still needed, and USB waits for a test on a real TV |
| 45, 46 | The ATEM is a 4 M/E Constellation HD. M/E 1 is the stream, input 20 announcements, input 19 custom. The TVs are BRAVIA 3 II. A sheet listing the TVs | The 24 outputs fit the TVs on 18 to 24, and the sources are set. The BRAVIA 3 II is controlled with Sony's Simple IP control, because newer Sony TVs need HTTPS for the other method, which Companion's Sony module can't do. No key is needed. USB stays on the remote. The TV sheet is `config/network/tvs.csv` |
| 47 | Keep USB and add another SDI option. The ATEM outputs are fine, the ATEM is always on, and its address can be a placeholder | Each TV page has a sixth choice, SDI, another ATEM source that starts as Black, and Back moves to the last key, with Home one press further on the TVs page. Outputs 18 to 24 are confirmed. The `atem` connection has the ATEM's factory address, 192.168.10.240, as a placeholder |
