# Network plan

Everything sits on its own AV VLAN, separate from guest Wi-Fi. OSC and Art-Net have no login, so anyone who can reach this network can control the room. Companion sends Art-Net unicast to the ODE, not broadcast. These addresses are examples, so change the subnet if it collides with the building network.

| Device | Address | Connection | Power |
| --- | --- | --- | --- |
| Gateway for the AV VLAN | 192.168.50.1 | Building network | Building network |
| Companion host | 192.168.50.10 | Switch | UPS |
| Wing Rack | 192.168.50.20 | Switch | Rack power |
| ODE Mk3 | 192.168.50.31 | Switch | PoE or UPS |
| WiiM Pro Plus | 192.168.50.40 | Switch, needs internet | Rack power |
| Door 1 Network Dock | 192.168.50.51 | Cat6 to switch | PoE |
| Door 2 Network Dock | 192.168.50.52 | Cat6 to switch | PoE |
| Door 3 Network Dock | 192.168.50.53 | Cat6 to switch | PoE |
| AV Wi-Fi access point | 192.168.50.60 | Switch | PoE |
| Lighting iPad | 192.168.50.70 | AV Wi-Fi | Battery |
| Wing app iPad | 192.168.50.71 | AV Wi-Fi | Battery |

1. Create the AV VLAN on the managed switch and give it one untagged port per device above.
2. Make every door run a home run back to the switch. The docks use [802.3af PoE](https://www.elgato.com/explorer/products/stream-deck/how-to-set-up-stream-deck-network-dock/).
3. Create a password-protected AV Wi-Fi network on this VLAN only. Keep it off the guest and staff networks.
4. Allow internet access for the WiiM only. Give the Companion host internet only during planned updates.
5. Set static addresses on the devices themselves, or reserve them in DHCP. ENTTEC [advises against unicast to DHCP-assigned addresses](https://support.enttec.com/user-manuals/ode-mk3) in long-term installs.
6. Put the switch, Companion host and ODE Mk3 on the UPS. Companion sends the lights, so all three carry them.
7. Set up a new ODE on its own. It falls back to 192.168.0.10 without DHCP, which can clash with other new devices.

[ENTTEC recommends wired connections where possible](https://support.enttec.com/dmx/edmx-art-net-sacn-networking/edmx-art-net-sacn-sending-over-wifi). For important events, consider a USB-C Ethernet adapter on the lighting iPad instead of Wi-Fi.
