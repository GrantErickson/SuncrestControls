# TVs

The seven TVs are planned as Sony BRAVIA 3 II. The production ATEM, a 4 M/E Constellation HD, feeds each TV from its own output, over SDI to a converter behind the TV, which feeds the TV's HDMI 1. Companion turns each TV on or off and picks its input over the network, using Sony's Simple IP control. For now the Main Lobby TV is a Samsung home TV on test instead: see [Trying a Samsung home TV](#trying-a-samsung-home-tv). For Stream, Announcements, Custom and SDI, it also picks the source on that TV's ATEM output.

[Stream Deck pages](14-stream-deck-pages.md#tvs) has every key and block, and [Everyday use](10-everyday-use.md#the-tvs) has the volunteer version. The TV sheet, [config/network/tvs.csv](../config/network/tvs.csv), lists each TV's address, ATEM output, model, serial and MAC address. Fill it in as the TVs go up.

## What the deck does

- **More** has **Turn TVs On** and **Turn TVs Off**, which switch every TV at once, and **TVs**, which opens the list of TVs.
- **TVs** has a key for each TV. It's green while that TV is on, with what it shows above its name, and red while it's off. Tapping one opens that TV's page.
- **Each TV's page** has a switch that names the TV and turns it on or off, then a key for each of the six things it can show, then **Back** to the list of TVs, whose last key is **Home**. Choosing one turns the TV on if it's off.
- The night schedule turns every TV off with the lights and the audio. Five seconds after Companion starts, it sends every TV its state again.

A TV that comes on shows its default, not what it showed last, so it's always predictable. A single button that turns on everything, lights, audio and TVs, is planned for later.

## The TVs

The ATEM outputs are confirmed. The defaults are proposals, so confirm or change them.

| TV | Page | Address | ATEM output | Shows when it comes on | Why |
| --- | --- | --- | --- | --- | --- |
| Main Lobby | 8 | 192.168.50.81. For now, 192.168.0.126, a Samsung on test | 18 | Announcements | Where most people wait |
| Right Lobby | 9 | 192.168.50.82 | 19 | Announcements | Same |
| Cafe | 10 | 192.168.50.83 | 20 | Announcements | Same |
| Entry Hall | 11 | 192.168.50.84 | 21 | Announcements | First thing people see coming in |
| Kitchen | 12 | 192.168.50.85 | 22 | Stream | Volunteers working through the service can follow it |
| Meeting Room | 13 | 192.168.50.86 | 23 | Announcements | A meeting picks Local HDMI for a laptop. Announcements avoids a blank "No signal" screen in the morning |
| Back Stage | 14 | 192.168.50.87 | 24 | Stream | The team waiting to go on can see where the service is |

The outputs are the last seven of the Constellation's 24, which leaves the low numbers to production. To change a default after import, edit that TV's On block in the Library, the second block on its first row on pages 25 to 28, and point it at another Show block on its second row. Before the first import, change `TVS` in [build.py](../config/stream-deck/build.py). Keep the TV sheet the same as `build.py`, because `build.py` doesn't read it.

## The six things a TV shows

| Key | What it is | The ATEM | The TV |
| --- | --- | --- | --- |
| Stream | The live stream of the service | The TV's output takes M/E 1 Program, source 10010, from `atem_stream` | HDMI 1 |
| Announcements | The announcement slides | The TV's output takes input 20, from `atem_announcements` | HDMI 1 |
| Custom | A custom signal for every TV, such as an event's graphics | The TV's output takes input 19, from `atem_custom` | HDMI 1 |
| SDI | Another ATEM source, to be chosen | The TV's output takes the source in `atem_sdi`: Black until its input is chosen | HDMI 1 |
| USB | Whatever is on a USB stick in the TV | Nothing | Nothing. See [USB](#usb) |
| Local HDMI | A laptop or player plugged in at the TV | Nothing | HDMI 2, from an HDMI wall plate beside it |

The four source numbers are custom variables, so a technician changes them on Companion's Variables page and every TV follows. An ATEM numbers its inputs from 1. 10010 is M/E 1 Program, 10020 is M/E 2 Program, and so on. ATEM Software Control shows each source's name, and the ATEM connection's dropdowns show the numbers.

## How Companion talks to the TVs

Each `tv` connection holds a TCP connection to its TV's Simple IP control port, 20060, through Companion's generic TCP/UDP module, the same one the Juice Goose uses. Every message is 24 bytes: `*S`, `C` for a command, four letters, sixteen digits and a line feed.

| Message | Does |
| --- | --- |
| `*SCPOWR0000000000000001` | Turns the TV on |
| `*SCPOWR0000000000000000` | Turns the TV off |
| `*SCINPT0000000100000001` | HDMI 1, the ATEM |
| `*SCINPT0000000100000002` | HDMI 2, the wall plate |

Companion's Sony Bravia module isn't used. It sends Sony's REST API over plain HTTP only. Sony requires HTTPS on TVs released since August 1, 2025 to meet Europe's radio rules, and owners of newer models report the module's kind of HTTP control failing. It isn't clear whether US models are affected, and the BRAVIA 3 II is newer than that date. Simple IP control works either way and needs no key, so there's nothing secret to keep out of the repo. The cost is that anything on the control network can command the TVs, so keep them on it and off the guest Wi-Fi, as [Network plan](04-network-plan.md) already does.

A `tv` connection is green once its TCP connection is open. That shows the TV is reachable, not that it obeyed. The TV's last reply shows on Companion's Variables page as `$(tv1:tcp_response)` for TV 1, and so on: `*SA` and sixteen zeros means it obeyed, `*SA` and sixteen F's means it refused, and `*SN` is the TV reporting a change, such as `*SNPOWR0000000000000001` when it comes on. If the TV drops the connection, the module opens it again by itself.

## Which TVs work reliably

| TV | With Companion | Why |
| --- | --- | --- |
| Sony BRAVIA Professional Display, such as the BZ30P, BZ35P or BZ40P | Yes. The most dependable | Sony documents its control for these displays. Pro mode locks the menus, they're built for long hours, and their BRAVIA Signage app plays a USB stick |
| Sony BRAVIA home TV, such as the BRAVIA 3 II | Yes, with the settings below | The same Simple IP control. Home firmware can bring update prompts, sign-in screens and changed settings, and Sony documents Simple IP control for its professional displays, so try it on the first TV before ordering the rest |
| Samsung commercial display, such as the QB, QM or QH series | Yes | Companion's Samsung Display module uses Samsung's MDC protocol on TCP port 1515, with power, input and status. It can pick the USB player directly |
| Samsung home TV | No, until the test says otherwise | Its Companion module can only send remote-control key presses. It needs a pop-up on the TV accepted to pair, turns on by Wake-on-LAN, and firmware updates have broken it before. One is on test as the Main Lobby TV: see [Trying a Samsung home TV](#trying-a-samsung-home-tv) |

## Setting up each BRAVIA 3 II

Sony moves these menus between firmware versions, so the names may differ a little.

1. **Setup.** When Google TV asks, choosing **Basic TV** skips the Google account and the apps, which leaves fewer prompts on screen. Check on the first TV that the network settings below still work that way.
2. **Address.** Reserve its address from the table above in DHCP, by its MAC address, and write both in the TV sheet.
3. **Remote start.** Under **Network & Internet**, turn **Remote start** on, so Companion can turn the TV on over the network. On newer firmware it's **Remote device settings**, **Control remotely**. It uses a little more power in standby.
4. **Simple IP control.** Under **Network & Internet**, **IP control**, turn **Simple IP control** on. Some firmware puts IP control under **Home network** or **Local network**. Sony also recommends it to keep a TV answering in deep standby.
5. **Staying on.** Under **Power and energy**, turn off **Idle TV standby** and anything else that turns the TV off by itself, such as after a while with no signal. Companion turns the TVs off at night.
6. **HDMI-CEC.** Turn **BRAVIA Sync** off, so a laptop on the wall plate can't switch the TV or turn it off.
7. **Record it.** Put the serial number and firmware version in the TV sheet.

Then turn the TV off and on from the deck, and try each input.

## Trying a Samsung home TV

For now the Main Lobby TV, `tv1`, is a Samsung home TV on test: a 50" UN50U8000FDXZA, a 2025 Crystal UHD U8000F on Tizen. It's wired, at 192.168.0.126 on the same network as the Wing, and calls itself Office TV. The other six stay on Sony's Simple IP control. The test shows whether a Samsung home TV is good enough for the lobby, against the "No" in the table above.

The TV answers Samsung's home-TV remote API on ports 8001 and 8002 and asks for a pairing token. Port 1515 is closed, so it doesn't speak MDC like Samsung's commercial displays. `tv1` uses Companion's [Samsung Smart TV module](https://github.com/bitfocus/companion-module-samsung-smarttv), samsung-smarttv 1.0.0, on port 8002 with **Limit TLS to 1.2** on, and MAC address b0:f2:f6:38:9b:73 for Wake-on-LAN.

| The deck asks for | The module does |
| --- | --- |
| On | Nothing if the TV is on. Presses Power if it's in standby. Sends Wake-on-LAN if it's fully off, then waits up to 30 seconds for the TV to answer |
| Off | Presses Power, only if the TV is on, since Power toggles |
| HDMI 1, the ATEM | Presses the remote's `KEY_HDMI1` |
| HDMI 2, the wall plate | Presses `KEY_HDMI2` |

A Samsung that was fully off takes longer to wake, so its Send block sends the picture again after 8 seconds, not 3. USB only turns it on, as on the Sonys.

### On the TV first

Samsung moves these menus between years, so the names may differ a little.

1. **Pairing prompt.** Under **Settings**, **All Settings**, **Connection**, **External Device Manager**, **Device Connect Manager**, set **Access Notification** to **First Time Only**. With **Always Ask**, the TV asks every time Companion connects.
2. **Turning on over the network.** Under **Connection**, **Network**, **Expert Settings**, turn **Power On with Mobile** on. Turn **IP Remote** on too, if the menu has it.
3. **Staying on.** Under **General & Privacy**, **Power and Energy Saving**, turn off **Auto Power Off** and anything else that turns the TV off by itself.
4. **Address.** Reserve 192.168.0.126 in DHCP by its MAC address.

### Pairing

1. Import [lobby.companionconfig](../config/stream-deck/lobby.companionconfig). If `tv1` says its module is missing, install **Samsung: Smart TV** on Companion's Modules page.
2. With the TV on, it shows a pop-up asking to allow **Bitfocus Connection**. Choose **Allow** within about 30 seconds.
3. The module saves the TV's token in `tv1`'s **Pairing Token**, so the TV won't ask again. The token isn't in the repo. To pair again, clear that field and save.

If the TV keeps asking, check **Limit TLS to 1.2** is on in `tv1`. `$(tv1:power_state)` on the Variables page reads on, standby, or off when the TV doesn't answer at all.

### The test

On the deck, open **TVs**, then **Main Lobby**:

1. With the TV on, choose **Local HDMI**, then **Stream**. The TV should go straight to HDMI 2, then HDMI 1.
2. Turn it off with its switch, wait a minute, then choose **Announcements**. It should come on and go to HDMI 1.
3. Leave it off for half an hour, so it's fully asleep, then turn it on from the deck. That's Wake-on-LAN.
4. Unplug it for a minute, plug it back in, and turn it on from the deck.

Watch `tv1`'s log on the Connections page. Write what happened in the [TV sheet](../config/network/tvs.csv)'s Status and Notes. The open questions are whether `KEY_HDMI1` and `KEY_HDMI2` go straight to those inputs on this model (some Samsungs only step through inputs with the Source key), whether it wakes from fully off, and whether firmware updates bring prompts.

To put the Main Lobby TV back on Sony's Simple IP, take TV 1 out of `SAMSUNG_TVS` in [build.py](../config/stream-deck/build.py) and build again.

## The ATEM

- **The model.** It's a 4 M/E Constellation HD, which has 24 outputs, so the seven TVs fit with 17 to spare. The `atem` connection is set to that model, so its dropdowns show every output before it connects.
- **The outputs belong to the TVs.** Production shouldn't route them, and the lobby keys never touch any other output. Name them in ATEM Software Control, such as "TV Cafe". The TV sheet has a name for each.
- **The ATEM is always on.** Stream, Announcements, Custom and SDI come from it, so if it's ever off, those TVs go black. Local HDMI and USB still work.
- **Companion must reach it.** The ATEM sits on the production network. The control network needs a route or firewall rule to the ATEM's address, UDP port 9910. The `atem` connection has a placeholder, 192.168.10.240, the address every ATEM ships with. Replace it with the real address, in Companion or as `ATEM_IP` in `build.py`. Until then the connection stays red and the TVs' ATEM outputs don't change.
- **Connections are limited.** An ATEM takes only a few control connections at once. Users report about five on some models. Companion takes one, beside ATEM Software Control and any panels or other Companions production uses.
- **Each TV needs its cable and converter.** That's an SDI cable from its ATEM output and a powered SDI to HDMI converter behind the TV. The Constellation HD works in HD, so a 3G-SDI converter is enough, and the TV scales 1080p up to its 4K screen.

## How the Send block works

Each TV has two rows in the Library, two TVs to a page on pages 25 to 28. The first row holds its Send, On and Off blocks, and the second a Show block for each thing it can show. The Send block is the first on the first row. Every key, the night schedule and the startup trigger set the TV's variable, `tv1_src` to `tv7_src`, then run it. It's the only block that talks to the TV or the ATEM.

1. If the variable says Off, it turns the TV off. Nothing else.
2. Otherwise it turns the TV on. Sending on to a TV that's already on does nothing.
3. For Stream, Announcements, Custom or SDI, it sets the TV's ATEM output to that source, then the TV to HDMI 1. For Local HDMI, it sets the TV to HDMI 2.
4. Three seconds later it does step 3 again, because a TV that was off may ignore an input change while it wakes. If the TV was turned off meanwhile, it sends nothing.

[Bench test 16](09-testing.md) checks it.

## USB

USB is the one key that doesn't reach the TV. It turns the TV on and lights the key, and someone picks the USB stick with the TV's remote. Simple IP control can choose HDMI inputs but not the USB player, and the BRAVIA 3 II has no signage app to start playback by itself.

The key stays. For content that has to start without the remote, the SDI key brings in another ATEM source.

The Samsung on test is no different. Its Companion module can only press remote keys, the remote has no USB key, and the TV has no command to open a folder or start a slideshow. A run of key presses that walks the Source menu to the stick might work, but it breaks whenever the menu or the TV's state differs. Samsung's home TVs also don't start a USB slideshow when they turn on. A slideshow that a key can start needs a player that starts one by itself, feeding the TV's HDMI 2, so the key is Local HDMI, or slides fed through the ATEM, so the key is Announcements, Custom or SDI.

### Putting photos on a stick

For a slideshow started with the TV's remote, on the Samsung or any TV:

1. **Format.** exFAT, or FAT32 for the widest support. Samsung's recent TVs also read NTFS. Plug the stick straight into the TV, not through a hub.
2. **Images.** JPEG, 16:9, at 3840 x 2160 for a 4K TV or 1920 x 1080. PNG and BMP work too. Slides from PowerPoint, Keynote or Canva export straight to JPEG at that size.
3. **One folder.** Put them all in one folder at the top of the stick, such as `Slides`, with nothing else in it and no folders inside. Samsung's TVs show up to 1,000 files in a folder.
4. **Order.** Number the names with leading zeros, such as `01 Welcome.jpg`, `02 Events.jpg`, and sort by name on the TV. A Mac leaves hidden `._` files on a stick, which can show up as blank photos, so eject it properly.
5. **On the TV.** Choose the stick from **Source**, open the folder, open the first photo, and start the slideshow from the controls on screen. Set the speed, and turn **Repeat** on so it loops. It stops when the TV turns off.

## Still to decide

These are in [Open items](12-open-items.md):

- The ATEM's real address, and the route to it from the control network
- Which ATEM source SDI shows, and whether to give the key a friendlier name
- The default for each TV
- Whether the morning schedules turn the TVs on
- Later: one button that turns everything on

## Sources

- [Sony's Simple IP control protocol](https://pro-bravia.sony.net/remote-display-control/simple-ip-control/) and [Sony's IP control changes for Europe's radio rules](https://pro-bravia.sony.net/setup/device-settings/red-da/)
- [A BRAVIA 3 owner's thread on the HTTPS change, Home Assistant forum](https://community.home-assistant.io/t/unable-to-add-bravia-k-55s30-to-bravia-tv-integration/919669)
- [The Sony Bravia module's HTTP-only client](https://github.com/bitfocus/companion-module-sony-bravia/blob/master/src/api.js), the [generic TCP/UDP module](https://github.com/bitfocus/companion-module-generic-tcp-udp) and the [ATEM module](https://github.com/bitfocus/companion-module-bmd-atem)
- [Samsung Display module](https://github.com/bitfocus/companion-module-samsung-display) and [Samsung Smart TV module](https://github.com/bitfocus/companion-module-samsung-smarttv)
- [ATEM connection limits on the Blackmagic forum](https://forum.blackmagicdesign.com/viewtopic.php?p=777096)
