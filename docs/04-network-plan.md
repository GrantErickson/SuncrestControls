# Network plan

Everything sits on its own AV VLAN, separate from guest Wi-Fi. OSC and Art-Net have no login, so anyone who can reach this network can control the room. Companion sends Art-Net unicast to the ODE, not broadcast. These addresses are examples, except the Wing's, so change the subnet if it collides with the building network.

| Device | Address | Connection | Power |
| --- | --- | --- | --- |
| Gateway for the AV VLAN | 192.168.50.1 | Building network | Building network |
| Companion host | 192.168.50.10 | Switch | UPS |
| Wing Rack | 192.168.0.30, its real address, outside this plan's 192.168.50 | Switch | Always-on rack power |
| ODE Mk3 | 192.168.50.31 | Switch | PoE or UPS |
| WiiM Pro Plus | 192.168.50.40 | Switch, needs internet | Always-on rack power |
| Rack power, Juice Goose iP-1520 | 192.168.50.45 | Switch | 20 A circuit |
| Speaker plug 1, Kasa EP10 | 192.168.50.46, reserved in DHCP | AV Wi-Fi, 2.4 GHz | At the speaker |
| Speaker plug 2, Kasa EP10 | 192.168.50.47, reserved in DHCP | AV Wi-Fi, 2.4 GHz | At the speaker |
| Door 1 Network Dock | 192.168.50.51 | Cat6 to switch | PoE |
| Door 2 Network Dock | 192.168.50.52 | Cat6 to switch | PoE |
| Door 3 Network Dock | 192.168.50.53 | Cat6 to switch | PoE |
| AV Wi-Fi access point | 192.168.50.60 | Switch | PoE |
| Lighting iPad | 192.168.50.70 | AV Wi-Fi | Battery |
| Wing app iPad | 192.168.50.71 | AV Wi-Fi | Battery |
| TVs 1 to 7, Sony BRAVIA 3 II, in the order on the TVs page. The [TV sheet](../config/network/tvs.csv) has each one | 192.168.50.81 to .87, proposed. For now TV 1 is a Samsung on test at 192.168.0.126 | Cat6 to switch | At each TV |
| Production ATEM 4 M/E Constellation HD, always on | On the production network. 192.168.10.240, its factory address, is a placeholder in Companion | Routed, UDP 9910 from the Companion host only | Production rack |

1. Create the AV VLAN on the managed switch and give it one untagged port per device above.
2. Make every door run a home run back to the switch. The docks use [802.3af PoE](https://www.elgato.com/explorer/products/stream-deck/how-to-set-up-stream-deck-network-dock/).
3. Create a password-protected AV Wi-Fi network on this VLAN only. Keep it off the guest and staff networks. Give it a 2.4 GHz band for the Kasa plugs, make sure it reaches the powered speakers, and let wired devices reach its clients.
4. Allow internet access for the WiiM, and for the Kasa plugs while they're set up in the Kasa app. Give the Companion host internet only during planned updates.
5. Set static addresses on the devices themselves, or reserve them in DHCP. ENTTEC [advises against unicast to DHCP-assigned addresses](https://support.enttec.com/user-manuals/ode-mk3) in long-term installs.
6. Put the switch, Companion host and ODE Mk3 on the UPS. Companion sends the lights, so all three carry them. The Juice Goose remembers which pods were on and sequences them back after an outage.
7. Keep the Wing Rack, the WiiM and the Bluetooth receiver on power that is never switched, such as the Juice Goose's unswitched outlet. Only gear that turns off with the audio goes on its pods.
8. Let the Companion host reach the production ATEM, and nothing else on this network. Route UDP 9910 from the Companion host to the ATEM's address. Video reaches the TVs over SDI, not this network.
9. Let the Companion host and the Wing app iPad reach the Wing at 192.168.0.30, on UDP port 2223. It's outside 192.168.50, so either put this VLAN on 192.168.0 and move the other addresses to match, or route UDP 2223 to the Wing, as for the ATEM.
10. Set up a new ODE on its own. It falls back to 192.168.0.10 without DHCP, which can clash with other new devices.

[ENTTEC recommends wired connections where possible](https://support.enttec.com/dmx/edmx-art-net-sacn-networking/edmx-art-net-sacn-sending-over-wifi). For important events, consider a USB-C Ethernet adapter on the lighting iPad instead of Wi-Fi.
