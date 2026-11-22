# Audio setup

Speaker zones live in Wing Rack matrices, so no extra audio processor is needed. Each source has its own bus, and each zone picks one source by turning sends on and off. Companion only changes sends, mutes and faders, so the operator's mix stays untouched.

The wireless mics are the exception to one source per zone. They have their own bus, which feeds every zone all the time, so someone can talk over the music or the auditorium feed. The rack's Mic dial sets that bus, and pushing the dial mutes it.

The [Wing Rack](https://thomannmusic.com/behringer_wing_rack.htm) has 8 matrices and 8 analog outputs. These zones use 7 outputs, which leaves 1 spare.

| Source | Comes in on | Wing channel | Feeds matrices from |
| --- | --- | --- | --- |
| Auditorium feed | Two line inputs | Aux 1 | Bus 14 |
| Playlist | Two line inputs | Aux 2 | Bus 15 |
| Bluetooth | Two line inputs | Aux 3 | Bus 16 |
| Lobby stage | Band | Normal channels | Main 1 |
| Wireless mics | Mic receivers | Normal channels | Bus 13, always on |

| Zone | Matrix | Format | Wing output | Amp channel |
| --- | --- | --- | --- | --- |
| Lobby, the main pair | MX1 | Stereo | Local 1 and 2 | Own pair |
| Main Entry, the courtyard pair | MX2 | Stereo | Local 3 and 4 | Own pair |
| North Entry, 70V under the soffit | MX3 | Mono | Local 5 | Own channel |
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

1. Connect the WiiM to the AV switch and set it up in the WiiM Home app.
2. Sign in to the streaming account.
3. Run its RCA outputs to two Wing Rack inputs. Use a stereo DI if the unbalanced connection hums.
4. Save each playlist to a WiiM preset. Presets 1 to 7 match the playlist keys: Morning, Everyday, Evening, Seasonal, Calm, Pop and Upbeat. Name them for how people use them, such as Morning or Christmas.
5. Test a preset from a browser: `https://192.168.50.40/httpapi.asp?command=MCUKeyShortClick:1`

The [WiiM HTTP API](https://www.wiimhome.com/pdf/HTTP%20API%20for%20WiiM%20Products.pdf) documents this command. The device uses a self-signed certificate, so expect a browser warning.

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
6. Name those buses SRC AUD, SRC MUSIC and SRC BT. Set their faders to -20 dB and take them out of Main 1. -20 dB is normal, which leaves the Volume dial 26 dB to go up before it stops at +6 dB. The Volume dial moves the fader of whichever is playing, and room buttons put the auditorium and music buses back to -20 dB. Bluetooth keeps the level its own dial on Audio Source set.
7. Send every wireless mic channel to Bus 13, post-fader, and take them out of Main 1. Name Bus 13 MICS and set its fader to -10 dB. While the Lobby Stage plays, the band reaches the zones through Main 1 and the mics through Bus 13, so they never arrive twice.
8. Name Matrix 1 to 5 after the zones above. Set Matrix 3, 4 and 5 to mono.
9. On every zone matrix, set the sends from Bus 14, Bus 15, Bus 16 and Main 1 to 0 dB, then turn them off. That is 20 sends.
10. On every zone matrix, set the send from Bus 13 to 0 dB and leave it on. Companion never touches these 5 sends. A zone that is off is muted, so its mics go quiet too.
11. On the ROUTING screen, assign Local outputs 1 to 7 as listed above.
12. Add zone EQ, delay and a limiter on each matrix. The two entries will need different tuning from the lobby.
13. Play the Wing's oscillator as pink noise through each zone. With the matrix fader at 0 dB, set the amp gain to the loudest level you would ever accept.
14. With a mic in the room and Bus 13 at 0 dB, set each mic channel's level just below feedback in the loudest zone. The Mic dial stops at 0 dB, so a volunteer can't push the mics into feedback.
15. Save this as a snapshot called Lobby Base, and keep a copy in the repo.

## Audio power

A [Juice Goose iP-1520](https://goknight.com/juice-goose-ip-1520-web-based-power-controller/) powers the rack gear that turns off with the audio, the amplifiers among them. [TP-Link Kasa EP10](https://www.tp-link.com/us/support/download/ep10/) smart plugs power the powered speakers. Companion talks to the Juice Goose over UDP and to each plug through the Kasa module. These steps follow the [iP Series manual](https://goknight.com/content/documentation/iP_Series_Manual_Rev_6_2023%20(3).pdf).

The iP-1520 has three switched pods, each a duplex receptacle, and one unswitched outlet, 20 A in all. It plugs into a 20 A circuit with a NEMA 5-20 receptacle. Turning on, it sequences pod 1, then 2, then 3. Turning off, it goes 3, 2, 1.

| Outlet | Plug in |
| --- | --- |
| Unswitched | The Wing Rack, the WiiM and the Bluetooth receiver, through a strip if needed. They stay on so Companion can always reach them |
| Pod 1 | Anything that only needs power with the audio, such as the wireless mic receivers. Free otherwise |
| Pods 2 and 3 | The amplifiers, so they come on last and go off first |

Set up the Juice Goose:

1. Connect it to the AV switch and browse to `http://juicegoose`, or 192.168.1.77 if that fails. Sign in as `admin` with the password `juicegoose`, then change both passwords.
2. Under iP Series Management, Network, turn off DHCP and set 192.168.50.45, mask 255.255.255.0 and gateway 192.168.50.1.
3. On the Configuration tab, enable UDP on its default port, 30333. Leave TCP off.
4. Turn on the Power Loss Feature, so pods that were on sequence back on after an outage.
5. Leave the Power Cycle feature off. It reboots pod 1 when a ping fails, which suits a router, not audio gear.
6. Test from the Control page: set the sequence to 1 second and press Sequence Up. The pod lights come on in turn.

Set up each speaker plug:

1. Plug it in at the powered speaker and add it in the Kasa app on the AV Wi-Fi, which must be 2.4 GHz. Name it after the speaker.
2. In the Kasa app's settings, turn on **Third Party Compatibility**. On firmware 1.1.1 and later, [Companion can't find the plug without it](https://github.com/bitfocus/companion-module-tplink-kasasmartplug/issues/58).
3. Reserve its address in DHCP: 192.168.50.46 for the first plug and 192.168.50.47 for the second. The plugs can't set a static address themselves.
4. Make sure Companion can reach the plugs on the Wi-Fi. If the access point isolates wireless clients, allow the plugs through.

Companion sends `DEACTIVATE` before each sequence, because the manual says the front rocker switch otherwise overrides remote commands. Turn Audio On sequences the pods up a second apart, then turns the speaker plugs on 2.5 seconds later, once the amplifiers are up. Turn Audio Off turns every zone off first, then the speaker plugs, then a second later sequences the pods down. Nothing switches with signal on it.

The manual fallbacks are on the front of the Juice Goose. Its recessed slide switch turns every outlet on if its controller fails. The rocker sequences the pods up or down, but only after `ACTIVATE` is sent from its web console, since Companion turns it off. Each Kasa plug has a button that turns it on or off by hand.

If the fire alarm contractor requires audio to stop on alarm, the Juice Goose has no alarm input, so it needs another way, such as a relay the alarm opens in the amplifiers' power.

## Protect the zones from scene recalls

A snapshot recall can overwrite zone settings, so protect them on purpose.

1. Open [Global Safes](https://drewbrashler.com/?p=43975) and protect Matrix 1 to 5, Bus 13 to 16 and Aux 1 to 3.
2. Recall a band snapshot and confirm the zones didn't change.
3. Tell operators a full restore ignores safes.

It is not yet confirmed that Global Safes cover matrices. If they don't, set each band snapshot's scope to leave these parts out.

When nobody is mixing, try the Wing's surface lock. On the Wing Compact you hold HOME for about 1.5 seconds with buttons of your choice, which become the unlock code. Confirm the steps on the Rack. [Audio and remote control keep working](https://www.adorama.com/col/productManuals/BEHWINGCM.pdf), so Stream Decks are unaffected.
