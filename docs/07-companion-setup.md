# Companion setup

Companion holds the button layouts and logic, but no lighting looks or audio mixes. Every page, icon and action comes from one file you import, so nothing runs custom code at the church.

[Stream Deck pages](14-stream-deck-pages.md) lists every key and what runs behind it.

## Install it

1. Install Debian or Ubuntu Server on the mini PC.
2. In the BIOS, set the PC to power on after AC power returns.
3. Set its static address to 192.168.50.10.
4. As root, run the [official headless install script](https://github.com/bitfocus/companion-pi): `curl https://raw.githubusercontent.com/bitfocus/companion-pi/main/install.sh | bash`
5. Run `sudo companion-update` and choose the current stable release. That was v5.1.2 on 2026-11-04.
6. Browse to `http://192.168.50.10:8000`.
7. Turn on the [Admin UI Password](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md). It only stops casual browsing, which is why the VLAN matters.
8. On the Protocols page, turn off remote protocols you aren't using.

## Import the configuration

1. Open [Import/Export](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/import-export.md) and choose [lobby.companionconfig](../config/stream-deck/lobby.companionconfig).
2. On the **Full import** tab, leave every available category selected and choose **Full Reset then Import**. Only do this on a new install, because it replaces what is there.
3. Open Connections and confirm the three below. Companion uses the newest installed version of each module, so if one reports a missing module, install it from the Modules page.
4. Run [bench test 13](09-testing.md).

| Connection | Module | Settings in the file |
| --- | --- | --- |
| `wing` | [behringer-wing](https://github.com/bitfocus/companion-module-behringer-wing) | Desk IP 192.168.50.20, desk type Wing Rack |
| `splay` | [generic-osc](https://github.com/bitfocus/companion-module-generic-osc) | Target 192.168.50.30, port 8000, UDP |
| `wiim` | [generic-http](https://github.com/bitfocus/companion-module-generic-http) | Base URL `https://192.168.50.40/`, unauthorized certificates accepted |

The WiiM uses a self-signed certificate, which is why the file accepts it. The file holds pages, variables, triggers and connections. It doesn't hold surfaces or passwords, so add those next.

## Add the surfaces

1. Plug the rack Stream Deck + into the Companion host by USB. The install script handles Linux USB permissions.
2. Power each door dock over PoE, then give it its static address on the dock itself.
3. In Companion, open [Surfaces, then Remote Surfaces](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/surfaces.md). Add each dock by name and address, such as Door 1. [Elgato's guide](https://www.elgato.com/explorer/products/stream-deck/how-to-set-up-stream-deck-network-dock/) shows the same steps.
4. Turn off Use Last Page At Startup. Set Startup Page to 1 for doors and 4 for the rack.
5. Use Page Permissions to limit doors to pages 1 to 3 and the rack to pages 4 to 12.

## How the pages are arranged

| Page | Name | Used by |
| --- | --- | --- |
| 1 | Door Front | Doors |
| 2 | Door Lights | Doors |
| 3 | Door Audio | Doors |
| 4 | Rack Home | Rack |
| 5 | Rack Music | Rack |
| 6 and 7 | Rack Lights A and B | Rack |
| 8 to 12 | One page per zone | Rack |
| 20 and 21 | Library, the shared building blocks | No surface |

The Library is why this stays maintainable. Each real key runs a Library block with **Button: Trigger press and release**, so a change happens in one place. Pages 13 to 19 are empty.

## The whole-room buttons

Each one runs one Library block per zone and resets every matrix fader to its default. Because they set every zone, pressing any of them resets the room. These zone choices are starting points, and you change one by editing its block on page 21.

| Button | Mains | Outdoor | Soffit | Bathrooms | Vestibule |
| --- | --- | --- | --- | --- | --- |
| Sunday Feed | Auditorium | Off | Off | Auditorium | Auditorium |
| Music, Inside | Playlist | Off | Off | Playlist | Playlist |
| Music, Everywhere | Playlist | Playlist | Playlist | Playlist | Playlist |
| Lobby Event | Lobby Mix | Off | Off | Lobby Mix | Lobby Mix |
| Bluetooth | Bluetooth | Off | Off | Bluetooth | Bluetooth |
| All Audio Off | Off | Off | Off | Off | Off |

The player follows the zones. It starts when the first zone goes to Playlist, and it stops when the last zone leaves. Pressing a playlist in a silent room also runs Music, Inside, so a volunteer always hears a result.

## Door behavior

1. The front screen shows artwork and the current look.
2. Holding **Hold for lights** for 1.5 seconds opens Door Lights. After 30 seconds the door returns to the front screen on its own.
3. Pressing a preset runs it, and the door returns to the front screen 5 seconds later.
4. **Audio** on Door Lights opens Door Audio, with the room buttons people need at a door. To leave audio off the doors, clear key `2/2/3`.

## iPad Mode

Hold **iPad Mode** on the rack station for 1 second. The hold stops a stray press from blacking out the lobby.

**Entering iPad Mode** stops the S-Play with `/lobby/off` and sets `light_mode` to `ipad`.

**Leaving iPad Mode** sets `light_mode` to `presets` and resends the last preset, unless the lights were off.

Every lighting key checks `light_mode` before it acts, and the check lives in the Library. In iPad Mode the front key stops opening the lights, presets and All Off do nothing, and the door shows **iPad in control**. A door that restarts during an event locks too, because nothing is stored on the door.

Only the rack station can leave iPad Mode. That matches your rule that the iPad overrides the doors. Tell the iPad operator to close the lighting app first.

## The dials

On the Stream Deck +, Companion treats the dials as row 3 and the touch strip as row 2. Each dial changes its matrix by 1 dB a click, and stops at 0 dB, the level set at the amps, and at -60 dB. Pressing a dial opens that zone's page. Bathrooms has no Home dial, so use its zone page.

## The startup trigger

The preset can't also be a power-up playlist, because the manual describes one Start Trigger per playlist. Companion handles recovery instead. Sixty seconds after Companion starts, the **Startup recovery** trigger replays the last preset, unless iPad Mode is on.

## Turn on the schedule after launch

The file includes three time-of-day triggers, turned off. Set their times, then turn them on. The first two skip themselves during iPad Mode, so a schedule never interrupts an event.

| When | Action |
| --- | --- |
| Sunday, before first arrivals | Sunday Morning lights and Sunday Feed |
| Weekday opening time | Everyday lights and Music, Inside |
| Every night | Leaves iPad Mode, then All Off and All Audio Off |

The night trigger leaves iPad Mode first, so a forgotten iPad Mode can't lock the doors for days.

## Set up backups

In Settings, open [Backups](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md) and add a weekly backup rule. After any planned change, also [export the configuration](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/import-export.md) as YAML and commit it to the repo. From then on, that export is the live record.
