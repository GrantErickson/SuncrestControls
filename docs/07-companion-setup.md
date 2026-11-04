# Companion setup

Companion holds the button layouts and logic, but no lighting looks or audio mixes. Its whole setup exports to one backup file. Nothing here needs custom code.

## Install it

1. Install Debian or Ubuntu Server on the mini PC.
2. In the BIOS, set the PC to power on after AC power returns.
3. Set its static address to 192.168.50.10.
4. As root, run the [official headless install script](https://github.com/bitfocus/companion-pi): `curl https://raw.githubusercontent.com/bitfocus/companion-pi/main/install.sh | bash`
5. Run `sudo companion-update` and choose the current stable release. That was v5.1.1 on 2026-11-04.
6. Browse to `http://192.168.50.10:8000`.
7. Turn on the [Admin UI Password](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md). It only stops casual browsing, which is why the VLAN matters.
8. On the Protocols page, turn off remote protocols you aren't using.

## Add the connections

| Connection | Module | Settings |
| --- | --- | --- |
| Wing Rack | [behringer-wing](https://github.com/bitfocus/companion-module-behringer-wing) | Desk IP 192.168.50.20, desk type Rack |
| S-Play Mini | [generic-osc](https://github.com/bitfocus/companion-module-generic-osc) | Target 192.168.50.30, port 8000 |
| WiiM | [generic-http](https://github.com/bitfocus/companion-module-generic-http) | Base URL `http://192.168.50.40` |

If the WiiM needs `https`, set Unauthorized Certificates to Accept in that connection.

## Add the surfaces

1. Plug the rack Stream Deck + into the Companion host by USB. The install script handles Linux USB permissions.
2. Power each door dock over PoE, then give it its static address on the dock itself.
3. In Companion, open [Surfaces, then Remote Surfaces](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/surfaces.md). Add each dock by name and address, such as Door 1. [Elgato's guide](https://www.elgato.com/explorer/products/stream-deck/how-to-set-up-stream-deck-network-dock/) shows the same steps.
4. Turn off Use Last Page At Startup. Set Startup Page to 1 for doors and 4 for the rack.
5. Use Page Permissions to limit doors to pages 1 to 3 and the rack to pages 4 to 12.

## Create the custom variables

Turn on Persist value for all of these, so state survives a restart.

| Variable | Holds |
| --- | --- |
| `light_mode` | `presets` or `ipad` |
| `light_preset` | Name of the active preset |
| `light_preset_n` | Number of the active preset |
| `z1_src` to `z5_src` | Source name for each zone, or Off |

## Lay out the pages

| Page | Name | Used by |
| --- | --- | --- |
| 1 | Door Front | Doors |
| 2 | Door Lights | Doors |
| 3 | Door iPad | Doors |
| 4 | Rack Home | Rack |
| 5 | Rack Music | Rack |
| 6 and 7 | Rack Lights A and B | Rack |
| 8 to 12 | One page per zone | Rack |
| 20 | Library, the shared building blocks | No surface |

**Door Lights** on a 15-key MK.2:

| Sunday Morning | Everyday | Bright | Evening | Event |
| --- | --- | --- | --- | --- |
| Walkthrough | Seasonal | Night |  |  |
| All Off |  |  | Audio, added later | Back |

**Rack Home** on the Stream Deck +:

| Sunday Feed | Music | Lobby Event | Bluetooth |
| --- | --- | --- | --- |
| All Audio Off | Zones | Lights | iPad Mode |
| Dial: Mains | Dial: Outdoor | Dial: Soffit | Dial: Vestibule |

**Rack Music** holds up to four playlist keys, Inside, Everywhere and Home. Each zone page has the four sources, Zone Off, previous and next zone, and Home, with a volume dial.

## Build the Library page

The Library is why this stays maintainable. Each real button calls these blocks with **Button: Trigger press and release**, so a change happens in one place.

Create five buttons per zone: Auditorium, Playlist, Bluetooth, Lobby Mix and Off. Here is `Z1 Auditorium`:

1. Wing **Set Send Mute**: Bus 14 to MX1, unmuted.
2. Wing **Set Send Mute**: Bus 15 to MX1, muted.
3. Wing **Set Send Mute**: Bus 16 to MX1, muted.
4. Wing **Set Send Mute**: Main 1 to MX1, muted.
5. Wing **Set Mute**: MX1, unmuted.
6. Set custom variable `z1_src` to Auditorium.

The Off button only mutes the matrix and sets the variable to Off. Create one more Library button per lighting preset. It sends the OSC address and sets `light_preset` and `light_preset_n`.

## Build the whole-room buttons

Each button calls one Library button per zone and sets each matrix fader to its default. Because they set every zone, pressing any of them resets the room. These zone choices are starting points.

| Button | Mains | Outdoor | Soffit | Bathrooms | Vestibule |
| --- | --- | --- | --- | --- | --- |
| Sunday Feed | Auditorium | Off | Off | Auditorium | Auditorium |
| Music, Inside | Playlist | Off | Off | Playlist | Playlist |
| Music, Everywhere | Playlist | Playlist | Playlist | Playlist | Playlist |
| Lobby Event | Lobby Mix | Off | Off | Lobby Mix | Lobby Mix |
| Bluetooth | Bluetooth | Off | Off | Bluetooth | Bluetooth |
| All Audio Off | Off | Off | Off | Off | Off |

## Build the door behavior

1. On Door Front, show the logo and `$(custom:light_preset)`.
2. Add one key labeled **Hold for lights**. Add a [duration group](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/buttons/creating/actions.md) of 1,500 ms, set to run while held, with **Surface: Set to page** 2 on the current surface.
3. In the same group, add **internal: Wait** of 30 seconds, then a **Logic: If statement**. If `light_mode` is `presets`, return the surface to page 1.
4. Each preset key calls its Library button, waits 5 seconds, then returns to page 1.
5. Color the active preset with a variable check feedback on `light_preset`.
6. On Door iPad, show only the message **iPad in control**. No key does anything.

## Build iPad Mode

Use a **Logic: If statement** on `light_mode`.

**Entering iPad Mode:**

1. Send OSC `/lobby/off` to stop the S-Play.
2. Set `light_mode` to `ipad`.
3. Set Door 1, 2 and 3 to page 3.

**Leaving iPad Mode:**

1. Set `light_mode` to `presets`.
2. Send OSC `/lobby/preset/$(custom:light_preset_n)` to restore the last preset.
3. Set Door 1, 2 and 3 to page 1.

Only the rack station can leave iPad Mode. That matches your rule that the iPad overrides the doors. Tell the iPad operator to close the lighting app first.

## Set the dials

On each dial button, turn on [Rotary actions](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/buttons/creating/index.md). Add Wing **Adjust Level** for that matrix at -1 dB on Rotate left and +1 dB on Rotate right. Use a **Logic: If statement** to stop at 0 dB, the level set at the amps.

## Add the startup trigger

The preset can't also be a power-up playlist, because the manual describes one Start Trigger per playlist. Companion handles recovery instead.

1. Create a [trigger](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/triggers.md) on the startup event.
2. Add **internal: Wait** of 60 seconds, so other devices finish booting.
3. If `light_mode` is `presets`, resend `/lobby/preset/$(custom:light_preset_n)`.
4. Set doors to page 1, or page 3 if `light_mode` is `ipad`.

## Add the schedule after launch

Use time-of-day trigger events, which support chosen days of the week. Check `light_mode` first, so a schedule never interrupts an iPad event.

| When | Action |
| --- | --- |
| Sunday, before first arrivals | Sunday Morning lights and Sunday Feed |
| Weekday opening time | Everyday lights and Music, Inside |
| Every night | All Off and All Audio Off |

Add a Night trigger that also leaves iPad Mode after the last possible event. That way a forgotten iPad Mode can't lock the doors for days.

## Set up backups

In Settings, open [Backups](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/settings.md) and add a weekly backup rule. After any planned change, also [export the configuration](https://github.com/bitfocus/companion/blob/main/docs/user-guide/3_config/import-export.md) as YAML and commit it to the repo.
