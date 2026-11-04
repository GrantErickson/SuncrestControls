# Door stations

Start with the front screen and a sensible height, and add covers only if real use shows a need. Both are free, and each door's front screen can be changed later without touching the wall.

| Protection | Stops | Cost | Downside |
| --- | --- | --- | --- |
| Front screen, hold to open | Casual taps and children | Free | A determined person still gets in |
| Mounting toward the top of the reach range | Small children | Free | Check accessibility rules first |
| [Companion PIN lockout](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md) | Anyone without the code | Free | Slower for volunteers |
| Lockable clear cover | Everyone without a key | Low | Someone has to find the key |

US accessibility rules commonly cap controls at about 48 inches above the floor. Ask your architect what applies before mounting higher.

## Choose the deck

I found no Elgato wall mount for the MK.2 or the Stream Deck +. There are two practical routes, and the Stream Deck Module is the better fit for a public wall.

| Option | Size | Mounting | Good for | Watch for |
| --- | --- | --- | --- | --- |
| [Stream Deck Module 15 Keys](https://www.elgato.com/ww/en/p/stream-deck-module-15-keys) | 107 x 70 x 20 mm | Behind a faceplate, using Elgato's CAD files | Flush, unbranded wall stations | Price and mounting points need confirming |
| Stream Deck MK.2 in a custom plate | 118 x 84 x 25 mm | Plate clamps the edges | Using the budgeted part | Bulkier, and made for desks |
| [TechShieldz steel holder](https://www.indooroutdoors.co.uk/a/s/products/techshieldz-stream-deck-wall-mount-holder) for the MK.2 | 120 x 85 x 31 mm | Two screws, sits on the wall | Staff areas and the rack | The deck sits in a holder and can be lifted out |

The Module has the same 15 keys at the same 72 pixels, so the [configuration](14-stream-deck-pages.md) works unchanged. Elgato [lists Module 15 as supported](https://www.elgato.com/explorer/products/stream-deck/stream-deck-network-dock-overview/) on the Network Dock.

Module prices vary by seller, about [C$189](https://hotrodcameras.com/en-ca/collections/post-sound/products/elgato-stream-deck-module-15-keys) in Canada and [€107 before VAT](https://www.streamingvalley.nl/product/elgato-stream-deck-module-15-keys/) in the Netherlands. I couldn't confirm a US price, so get a quote before changing the budget. Elgato's page doesn't state its mounting points or where the USB-C port sits, so check the CAD files first.

A [flush enclosure for the Module](https://makerworld.com/en/models/2552178-stream-deck-module-15-keys-wall-mount-enclosure) is shared on MakerWorld as a starting point. It's listed at 20 mm deep, or 14 mm with a hole in the wall for the USB-C plug. It's a hobby design that I could only see through search results, so treat it as a sketch for a tamper-resistant plate.

The rack station is different. I found no wall mount for the Stream Deck +, and it needs clearance for its dials, so plan on a shelf or custom plate at the rack.

## Mounting

Elgato's overview doesn't list the dock's size, so measure one first. The dock [comes with a mounting bracket](https://www.elgato.com/explorer/products/stream-deck/stream-deck-network-dock-overview/) and a 15 cm USB-C cable.

1. Buy one deck and one dock before the walls close, and test-fit them in the box you plan to use.
2. Terminate the Cat6 inside the box, with room for the dock and a USB-C loop.
3. Make a laser-cut or 3D-printed faceplate that clamps the deck by its edges and hides the USB-C cable.
4. Use tamper-resistant screws, because a surface-mounted deck unplugs with one tug.
5. Leave air around the dock.
6. Label each plate with its door number, so support calls are easy.

Dim the door decks in Companion with **Surface: Set to brightness**. You can drop brightness overnight once the schedule is running.
