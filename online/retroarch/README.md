# RetroVerse → RetroArch native Netplay bridge

**Status:** Host/join/spectate *launcher integration committed*, not yet tested with two RetroArch installations or the Vayava GameBox.

RetroVerse delegates gameplay synchronization to **RetroArch's existing netplay implementation** instead of replacing it with the experimental Pong WebSocket server. Both players need compatible RetroArch versions, **the same core and the same game content**; not all cores or games support netplay. RetroArch generally uses TCP port **55435** for hosting.

Run in the repository root with your own installed RetroArch, libretro core and game file:

```sh
python3 online/retroarch/netplay_bridge.py host --core "/path/to/core.so" --content "/path/to/game.rom" --nick RetroVerse
python3 online/retroarch/netplay_bridge.py join --peer 192.168.1.20 --core "/path/to/core.so" --content "/path/to/game.rom"
python3 online/retroarch/netplay_bridge.py spectate --peer 192.168.1.20 --core "/path/to/core.so" --content "/path/to/game.rom"
```

For Windows use `py`, a Windows RetroArch executable via `--retroarch`, and your own installed DLL core.

Add `--dry-run` to validate and inspect the launch command without starting RetroArch. Commands use argument arrays, **not a shell**. This bridge only launches a fresh RetroArch process: it does not control an already running process or discover remote rooms. It doesn't transmit games, install cores, edit configuration, enable network interfaces, open firewall ports, or modify Android's internal storage.

**Security:** Avoid public hosting until you have appropriate router/network controls. For private sessions, configure RetroArch's own netplay password/relay settings through its menu; the bridge does not claim to implement account security. Start with two PCs on a trusted LAN. Spectating depends on RetroArch version/core support.

**Known limits:** This is native RetroArch *local-multiplayer synchronization*. It does not emulate console link cables or automatically add network play to games with no supported local multiplayer. Neither the RetroVerse browser lobby nor the physical ARM GameBox frontend is connected to this launcher yet.

References:
- https://docs.libretro.com/guides/netplay-getting-started/
- https://docs.libretro.com/guides/netplay-faq/
- https://manpages.ubuntu.com/manpages/noble/man6/retroarch.6.html
