# Audio setup

Speaker zones live in Wing Rack matrices, so no extra audio processor is needed. Each source has its own bus, and each zone picks one source by turning sends on and off. Companion only changes sends, mutes and faders, so the operator's mix stays untouched.

The [Wing Rack](https://thomannmusic.com/behringer_wing_rack.htm) has 8 matrices and 8 analog outputs. These zones use 7 outputs, which leaves 1 spare.

| Source | Comes in on | Wing channel | Feeds matrices from |
| --- | --- | --- | --- |
| Auditorium feed | Two line inputs | Aux 1 | Bus 14 |
| Playlist | Two line inputs | Aux 2 | Bus 15 |
| Bluetooth | Two line inputs | Aux 3 | Bus 16 |
| Lobby mix | Band and wireless mics | Normal channels | Main 1 |

| Zone | Matrix | Format | Wing output | Amp channel |
| --- | --- | --- | --- | --- |
| Mains | MX1 | Stereo | Local 1 and 2 | Own pair |
| Outdoor | MX2 | Stereo | Local 3 and 4 | Own pair |
| Soffit, 70V | MX3 | Mono | Local 5 | Own channel |
| Bathrooms | MX4 | Mono | Local 6 | Own channel |
| Vestibule | MX5 | Mono | Local 7 | Own channel |

Adjust the input numbers and buses to fit the band plan. Screen names below come from the [Wing manual](https://www.adorama.com/col/productManuals/BEHWINGCM.pdf) and may differ slightly on newer firmware.

## Bring in the auditorium feed

1. On the auditorium Wing, create a dedicated lobby feed on its own bus or matrix, so room mix changes don't move it.
2. Patch it to a pair of analog outputs and use the balanced run to the lobby.
3. Connect it to two Wing Rack inputs with phantom power off.
4. Set the trim from a real service, not a test tone.
5. If you hear hum, add a line isolation transformer at the Wing Rack end.

## Set up the playlist player

Settle music licensing before this goes live. See Open items.

1. Connect the WiiM to the AV switch and set it up in the WiiM Home app.
2. Sign in to the streaming account.
3. Run its RCA outputs to two Wing Rack inputs. Use a stereo DI if the unbalanced connection hums.
4. Save each playlist to a WiiM preset. Name them for how people use them, such as Morning or Christmas.
5. Test a preset from a browser: `http://192.168.50.40/httpapi.asp?command=MCUKeyShortClick:1`

The [WiiM HTTP API](https://www.wiimhome.com/pdf/HTTP%20API%20for%20WiiM%20Products.pdf) documents the URL format. The [preset command](https://forum.wiimhome.com/threads/possible-to-start-a-qobuz-playlist-and-or-wiim-preset-from-the-http-api.968/) comes from forum users, so it is on the bench test list. Try `https` if plain `http` fails.

Downloaded music needs no extra hardware. Play it from a phone or iPad over Bluetooth.

## Set up Bluetooth

1. Mount the receiver at the front of the rack, clear of metal doors. Its range is [listed at about 100 ft](https://www.markertek.com/product/dn-200br/denon-dn-200br-stereo-bluetooth-audio-receiver).
2. Run its XLR outputs to two Wing Rack inputs.
3. Pair devices at the rack.

No zone listens to Bluetooth by default, so a stray pairing plays nowhere.

## Configure the Wing Rack

1. Update to current firmware and record the version in the repo.
2. In SETUP, open NETWORK and set the IP to 192.168.50.20.
3. On the ROUTING screen, assign the three input pairs to Aux 1, 2 and 3 as stereo. Name them AUD FEED, PLAYLIST and BLUETOOTH.
4. Take Aux 1 to 3 out of Main 1. The operator's mix should not contain them.
5. Send Aux 1 to Bus 14, Aux 2 to Bus 15 and Aux 3 to Bus 16, each at 0 dB.
6. Name those buses SRC AUD, SRC MUSIC and SRC BT. Set their faders to 0 dB and take them out of Main 1.
7. Name Matrix 1 to 5 after the zones above. Set Matrix 3, 4 and 5 to mono.
8. On every zone matrix, set the sends from Bus 14, Bus 15, Bus 16 and Main 1 to 0 dB, then turn them off. That is 20 sends.
9. On the ROUTING screen, assign Local outputs 1 to 7 as listed above.
10. Add zone EQ, delay and a limiter on each matrix. Outdoor and soffit will need different tuning from the mains.
11. Play the Wing's oscillator as pink noise through each zone. With the matrix fader at 0 dB, set the amp gain to the loudest level you would ever accept.
12. Save this as a snapshot called Lobby Base, and keep a copy in the repo.

## Protect the zones from scene recalls

A snapshot recall can overwrite zone settings, so protect them on purpose.

1. Open [Global Safes](https://drewbrashler.com/?p=43975) and protect Matrix 1 to 5, Bus 14 to 16 and Aux 1 to 3.
2. Recall a band snapshot and confirm the zones didn't change.
3. Tell operators a full restore ignores safes.

It is not yet confirmed that Global Safes cover matrices. If they don't, set each band snapshot's scope to leave these parts out.

When nobody is mixing, try the Wing's surface lock. On the Wing Compact you hold HOME for about 1.5 seconds with buttons of your choice, which become the unlock code. Confirm the steps on the Rack. [Audio and remote control keep working](https://www.adorama.com/col/productManuals/BEHWINGCM.pdf), so Stream Decks are unaffected.
