# Lighting setup

Companion runs the lights. It keeps each look as a level for the linear house lights and one for each light area, and sends them as Art-Net to the ODE Mk3, which turns them into DMX on your one universe. There is no separate preset player.

Companion's own [Art-Net module](https://github.com/bitfocus/companion-module-generic-artnet) does the sending, so this is configuration, not code. [Stream Deck pages](14-stream-deck-pages.md#lighting-math) shows the exact math.

## What people control

| Control | What it does |
| --- | --- |
| Lights 1, 2 and 3 | Fade to that look over 2 seconds. Lights 1 is the dimmest |
| Lights Off | Fades everything out, and remembers the look |
| All Lights dial | Dims or brightens every light together, 5% a click, more when turned quickly. Turning it from off brings the look back. Push it to turn the lights off or on |
| Linear dial | Sets just the linear house lights, 5% a click, more when turned quickly. Push it to put them back to the look |
| Dimmer and Brighter, at the doors | Move every light 10% |
| Hold a Lights key on the rack for 3 seconds | Saves the lights as they are now into that key. The key turns green and says Saved |

## The dimmers

Every light in the lobby is a dimmer channel on one of three controllers, all on the one DMX universe. They take 20 channels.

| Controller | Channels | Outputs | How it dims | Limit per output |
| --- | --- | --- | --- | --- |
| [ETC UFMP8](https://www.etcconnect.com/Products/Architectural-Systems/Foundry/Mini-Panels/Features.aspx) Foundry Mini Panel | 1 to 8 | 8 zones, each a relay and a 0-10V output | The relay switches the circuit and 0-10V dims the drivers, one DMX channel a zone | See the relay rating in ETC's manual |
| [DLS PD804-DMX-120](https://www.digitallighting.com/animationfolder/pd804%20dmx%20dimmers.htm) | 9 to 16 | 8 line-voltage dimmers | Forward phase (leading edge) | 4 A, 480 W at 120 V. DLS also lists 500 W |
| [DLS PD408-DMX-120](https://www.digitallighting.com/animationfolder/pd408%20dmx%20dimmers.htm) | 17 to 20 | 4 line-voltage dimmers | Forward phase (leading edge) | 8 A, 960 W at 120 V. DLS also lists 1000 W |

The two DLS packs dim incandescent, MLV, ELV and LED loads, and any output can be set to switch only. LEDs on them must be TRIAC (forward phase) dimmable. Size each output to the lower wattage until DLS confirms it, and leave headroom for LED inrush. They set their start address on hex rotary switches, so check the DLS manual for how channel 9 and 17 are dialed in.

## The patch sheet

[config/network/dmx-patch.csv](../config/network/dmx-patch.csv) has one row for each thing being dimmed, which is one row a controller output. Open it in Excel and fill in each output as its circuit is assigned. Channels 481 to 512 are kept free for temporary lights.

| Column | What goes in it |
| --- | --- |
| ID | A short number for the row, to label the circuit |
| Controller, Output | The controller and which of its outputs this is |
| Start channel, Channels, End channel | The DMX channel. A dimmer output takes one, so all three match. A fixture with its own DMX, such as a temporary color light, takes a range |
| Dimming | 0-10V, or forward phase for the line-voltage packs |
| Light | What's on this output, such as Cafe pendants |
| Area | The control it follows: Linear, or a Light Control area (Cafe, Chandeliers, Entry Hall, Sconces, Soffit, Fireplace or Outside). None for lights only the iPad runs |
| Location | Where those lights are |
| Make and model | The fixtures on this output |
| Fixtures | How many fixtures are on this output |
| Load (W) | Their total wattage. Keep it under Max load |
| Max load (W) | The controller's limit for one output |
| Channel use | `Dimmer` for every output here. A fixture with its own DMX lists each channel in order, separated by semicolons |
| Status | Open until a light is assigned, then Assigned, then Confirmed once it's wired and tested |

In Channel use, a plain name such as `Dimmer` follows the area's level from 0 to 255. `Red up to 200` follows the level but tops out at 200, which sets a color mix that still dims. `Strobe = 0` holds a channel at that value. A dimmer output set to switch only can say `Switch`.

## Wire the DMX

1. Set the UFMP8's start address to 1, the PD804's to 9 and the PD408's to 17, and record any change on the [patch sheet](../config/network/dmx-patch.csv).
2. Run ODE Port 1 to the UFMP8, then on to the PD804 and the PD408, and terminate the end of the line. The DLS packs take DMX on RJ45 in and out connectors, with XLR as an order option, so match the connectors to the ODE and the UFMP8's DMX terminals.
3. Leave Port 2 free. It can become a second universe later.

## Set up the ODE Mk3

Steps follow the [ODE Mk3 manual](https://support.enttec.com/user-manuals/ode-mk3).

1. Connect the ODE alone and browse to its address. Without DHCP it falls back to 192.168.0.10.
2. On the Settings tab, turn off DHCP and set 192.168.50.31.
3. Set Port 1 to DMX OUT, Art-Net, universe 0, merge HTP.
4. Save, then record the settings in the repo.

## Set the patch in Companion

The imported file still has placeholder channels from before the controllers were chosen: the seven areas sit on channels 9 to 32, but only 9 to 20 exist. They line up once each output's Area is filled in on the patch sheet. Each group of channels follows one level.

| Channels | Follows | What they are |
| --- | --- | --- |
| 1 to 8 | The Linear dial and each look's linear level | Linear house lights, on the ETC UFMP8 0-10V zones |
| 9 to 12 | Cafe | Placeholder |
| 13 to 16 | Chandeliers | Placeholder |
| 17 to 20 | Entry Hall | Placeholder |
| 21 to 24 | Sconces | Placeholder |
| 25 to 28 | Soffit | Placeholder |
| 29 to 30 | Fireplace | Placeholder |
| 31 to 32 | Outside | Placeholder |

Each area has its own level, which the Area dial on Light Control sets and each look saves. All Lights scales every area and the linear lights together. When the fixtures are chosen, list on the patch sheet which ones belong to each area.

1. In Companion, open page 22, key `22/1/0` **Compute DMX**.
2. Edit the channel ranges in its expression to match the patch sheet. A range like `9-12` sets every channel in it.
3. If a fixture needs a channel held at a fixed value, such as a color mix or mode, add it to the end of the expression the same way, with a number instead of a level.
4. Press a Lights key and check each fixture.

Before the first import, it's easier to change `LIGHT_GROUPS` and `STATIC_CHANNELS` in [build.py](../config/stream-deck/build.py) and rebuild.

## Set the three looks

The file starts with Lights 1 at 35%, Lights 2 at 65% and Lights 3 at full. Set them in the real room:

1. Stand at the rack and press **Lights 2**.
2. Turn **All Lights** and **Linear**, and set single areas on **More**, then **Light Control**, until the room looks right.
3. Hold **Lights 2** for 3 seconds, until it turns green and says **Saved**.
4. Repeat for Lights 1 and 3.

Doors, the rack and the schedule all use the saved looks at once. Saving also writes the look into Companion's startup values, so exports and backups keep it.

## Connect the iPad

For Luminair, follow [ENTTEC's Wi-Fi guide](https://support.enttec.com/dmx/edmx-art-net-sacn-networking/edmx-art-net-sacn-sending-over-wifi):

1. Join the AV Wi-Fi.
2. Tap the status icon in the upper right and select Art-Net.
3. Confirm output is enabled and that universe and subnet are 0.
4. Open node settings and select the ODE at 192.168.50.31. This switches Luminair to unicast.

For your own app, send Art-Net to 192.168.50.31, universe 0, from one IP address.

## How the iPad override works

The ODE merges two sources, Companion and the iPad, and the highest level wins. Holding **iPad Mode** fades Companion's output to zero over 2 seconds, so the iPad's levels are the only ones left. Companion also locks every lighting key and dial. Leaving iPad Mode fades the last look back in.

- **One iPad at a time.** The ODE [ignores any third source](https://support.enttec.com/user-manuals/ode-mk3).
- **If the iPad drops.** The ODE discards a lost source after 4 seconds. What the lights do next is a bench test.
- **Plan B.** Switch Companion, the ODE and the iPad to sACN, with Companion at a lower priority. The iPad then wins automatically. Companion has a [sACN module](https://github.com/bitfocus/companion-module-generic-sacn) for this. Use it only if Luminair's sACN proves stable on your Wi-Fi.

## If Companion stops

Companion now sends the lights continuously, so the lights depend on it. The Art-Net module repeats the levels every second, and the startup trigger fades the last look back 5 seconds after Companion starts.

If the Companion host stops, the ODE stops hearing it. Whether the ODE holds the last look or goes dark after 4 seconds is [bench test 4](09-testing.md). Either way, the lighting iPad can run the lights straight through the ODE, with no Companion involved.

## Temporary lights

Put special-occasion fixtures on unused addresses at the end of the universe. The looks leave those channels alone, and the iPad controls them.

## Adding active looks later

Companion's looks are static levels. For moving or color-changing looks, run them from the iPad in iPad Mode. If they become part of everyday use, a dedicated controller can take over the lighting by changing only the lighting blocks on page 22. [DMX Core 100](https://dmxcore.com/dmx-core-100) and your own Lumen were both considered, and both can do it.
