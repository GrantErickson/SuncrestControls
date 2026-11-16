# Long-term care

The git repo is the project's memory, and each kind of change has a clear owner. Content changes happen often and stay with lay people. Core changes should be rare, planned, and recorded.

| Change | Who | Where | How often |
| --- | --- | --- | --- |
| Songs in a playlist | Anyone trusted | Spotify | Any time |
| Which playlist a button plays | Trained volunteer | WiiM Home app | Occasionally |
| A light look | Anyone trusted | Any station, hold the key to save | Seasonally |
| Button labels, layouts and the DMX patch | Technical person | Companion | Rarely |
| Zones and routing | Technical person | Wing Rack | Rarely |
| Network and addresses | Technical person | Switch | Rarely |
| Firmware and updates | Technical person | Each device | Planned |

## What belongs in the repo

| Path | Contents |
| --- | --- |
| `Initial Prompt.md` | Living brief, answers and decision log |
| `docs/` | These planning documents |
| `config/stream-deck/` | First importable Companion file, its artwork, and the script that builds them |
| `config/companion/` | Companion exports in YAML |
| `config/wing/` | Wing snapshots and show files |
| `config/network/` | Addresses, patch sheets and ODE settings |

Keep passwords out of the repo. Store them in the church's password manager, including Companion, the ODE, AV Wi-Fi, the switch and music accounts.

## Routine

| When | Do this |
| --- | --- |
| After any core change | Export the configuration, commit it, and add a line to the decision log |
| After saving a light look | Export the Companion configuration and commit it |
| Every quarter | Test the schedule, wipe the door decks, and confirm backups exist |
| Every year | Run the commissioning checklist, including the power loss test |
| When someone leaves | Update owners, and change shared passwords |

## Updating safely

1. Never update in the week before a major event.
2. Update one thing at a time, and back up first.
3. Run the affected tests from the Testing section afterward.
4. Record the new version in the decision log.

Record the ODE's settings before a firmware update, and check them afterward. `sudo companion-update` can also move Companion back to an earlier version. After a Companion update, run bench tests 3, 12 and 13, because they cover the lights and the dials.

## Planning for replacement

The design avoids depending on any one product. Companion only sends messages, so these parts can be swapped without rebuilding the system:

- **Lighting.** Companion sends plain Art-Net. A dedicated controller such as DMX Core 100, or your own Lumen once it takes commands from Companion, can take over by changing only the lighting blocks on page 22.
- **Door buttons.** Companion supports other surfaces, including touch screens running its web buttons.
- **Music.** Any player with line outputs can feed Aux 2.

The Wing Rack is the exception. Zones live inside it, so replacing it means rebuilding the zones. Keep its show file safe.

## Handover

Name a primary and backup technical owner, and write them in the brief. Each new owner should run the commissioning checklist once with the previous owner.
