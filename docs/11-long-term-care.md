# Long-term care

The git repo is the project's memory, and each kind of change has a clear owner. Content changes happen often and stay with lay people. Core changes should be rare, planned, and recorded.

| Change | Who | Where | How often |
| --- | --- | --- | --- |
| Songs in a playlist | Anyone trusted | Spotify | Any time |
| Which playlist a button plays | Trained volunteer | WiiM Home app | Occasionally |
| A light look | Trained volunteer | S-Play web page | Seasonally |
| Button labels and layouts | Technical person | Companion | Rarely |
| Zones and routing | Technical person | Wing Rack | Rarely |
| Network and addresses | Technical person | Switch | Rarely |
| Firmware and updates | Technical person | Each device | Planned |

## What belongs in the repo

| Path | Contents |
| --- | --- |
| `Initial Prompt.md` | Living brief, answers and decision log |
| `docs/` | These planning documents |
| `config/stream-deck/` | First importable Companion file, icons, and the script that builds them |
| `config/companion/` | Companion exports in YAML |
| `config/s-play/` | S-Play `.bak` backups |
| `config/wing/` | Wing snapshots and show files |
| `config/network/` | Addresses, patch sheets and ODE settings |

Keep passwords out of the repo. Store them in the church's password manager, including S-Play, Companion, AV Wi-Fi, the switch and music accounts.

## Routine

| When | Do this |
| --- | --- |
| After any core change | Export the configuration, commit it, and add a line to the decision log |
| After changing a light look | Download an S-Play backup and commit it |
| Every quarter | Test the schedule, wipe the door decks, and confirm backups exist |
| Every year | Run the commissioning checklist, including the power loss test |
| When someone leaves | Update owners, and change shared passwords |

## Updating safely

1. Never update in the week before a major event.
2. Update one thing at a time, and back up first.
3. Run the affected tests from the Testing section afterward.
4. Record the new version in the decision log.

Follow the [S-Play firmware steps](https://support.enttec.com/user-manuals/s-play-mini) exactly. ENTTEC says to back up and factory reset first, so restore your show afterward. `sudo companion-update` can also move Companion back to an earlier version.

## Planning for replacement

The design avoids depending on any one product. Companion only sends messages, so these parts can be swapped without rebuilding the system:

- **Presets.** Any player that accepts OSC can replace the S-Play.
- **Door buttons.** Companion supports other surfaces, including touch screens running its web buttons.
- **Music.** Any player with line outputs can feed Aux 2.

The Wing Rack is the exception. Zones live inside it, so replacing it means rebuilding the zones. Keep its show file safe.

## Handover

Name a primary and backup technical owner, and write them in the brief. Each new owner should run the commissioning checklist once with the previous owner.
