# Parts list and budget

The control electronics come to about $2,230 for three door stations. About $1,640 comes from retail listings and about $595 is an assumption. Check prices before ordering.

| Item | Qty | Each (USD) | Total (USD) | Job | Price basis |
| --- | --- | --- | --- | --- | --- |
| [Stream Deck +](https://www.bhphotovideo.com/c/product/1972608-REG/elgato_stream_deck_with.html/overview) | 4 | 180 | 720 | Every station: three doors and the rack, 8 keys and 4 dials each | Listed, older listings show $200 |
| [Elgato Network Dock](https://www.thomannmusic.com/elgato_stream_deck_network_dock.htm) | 3 | 83 | 249 | Puts each door deck on PoE Cat6 | Listed |
| [ENTTEC ODE Mk3](https://www.sweetwater.com/store/detail/ODEmk3--enttec-ode-mk3-two-universe-bidirectional-dmx-ethernet-gateway) | 1 | 319 | 319 | Turns Companion's Art-Net into DMX, and merges the iPad | Listed |
| [WiiM Pro Plus](https://www.whathifi.com/hi-fi/music-streamers/wiim-ultra-vs-wiim-pro-plus-which-five-star-music-streamer-is-the-best-option-for-you) | 1 | 219 | 219 | Playlist player | Review price, confirm |
| [Denon DN-200BR](https://www.markertek.com/product/dn-200br/denon-dn-200br-stereo-bluetooth-audio-receiver) | 1 | 129 | 129 | Bluetooth receiver with XLR outputs | Listed, some retailers show it discontinued |
| Fanless mini PC with SSD | 1 | 250 | 250 | Runs Companion, which now also sends the lights | Assumed |
| Managed PoE switch, 8 or more ports | 1 | 170 | 170 | AV network | Assumed |
| UPS | 1 | 150 | 150 | Keeps controls up through power blips | Assumed |
| [Kasa Smart Plug Mini EP10, 2-pack](https://www.amazon.com/Kasa-Smart-Required-Certified-EP10P2/dp/B091FXQQMQ) | 1 | 25 | 25 | Lets Companion switch the powered speakers | Assumed |

This excludes door faceplates, cables, labor, and an access point if the building doesn't already have one for the AV network. The Wing Rack, amps and speakers are already planned separately. The TVs aren't here either: seven Sony BRAVIA 3 II, and for each one an SDI cable from the production ATEM, a 3G-SDI to HDMI converter behind it, and an HDMI wall plate beside it for Local HDMI. The [TV sheet](../config/network/tvs.csv) lists them. [TVs](15-tvs.md) has what they need.

The [Juice Goose iP-1520](https://goknight.com/juice-goose-ip-1520-web-based-power-controller/) that sequences the rack's power is $659.99 at Knight, against an $870 list price. It belongs with the amps, so it isn't in the total. It's rated 20 A for everything plugged into it.

On 2026-11-21 the Juice Goose replaced the Furman CN-1800S sequencer, about $725, and the Shelly Pro 1 relay that switched it, $70. Companion now sends it commands directly.

Plan on one spare Stream Deck + and one spare dock once the design is proven. They are the parts most exposed to the public, and because every station uses the same deck, one spare covers them all.

The ENTTEC S-Play Mini ($380) left the list on 2026-11-15. It can't dim live, which the rack's light dials need, so Companion sends the lights instead.

On 2026-11-15 the doors changed from 15-key Stream Deck MK.2 decks, $150 each, to the Stream Deck +, so every station works the same. That adds about $90.
