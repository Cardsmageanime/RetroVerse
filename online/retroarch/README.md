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

## Visual menu integration (Windows, Linux, macOS)

The RetroVerse **Online Lobby** now links to a local, opt-in RetroArch Netplay control panel. To start it from the repository root:

```powershell
py online/retroarch/netplay_ui_server.py
```

On Linux or macOS, use `python3` instead of `py`. Open `http://127.0.0.1:8768/netplay`, or run the original Neon Showcase and click **RetroArch: Host / Join / Spectate** in **Online Lobby**. The local service also serves the showcase at `http://127.0.0.1:8768/`.

Select Host, Join, or Spectate; enter the **locally installed** libretro core path, the game file path, and a peer address for Join/Spectate. **Validate & Preview** checks the paths and constructs a RetroArch command without running anything. **Launch RetroArch** requires a separate confirmation checkbox and starts the locally installed RetroArch process.

The server listens only on `127.0.0.1`, checks HTTP origin/host and a per-process request token, and has no cross-origin API access. Do not bypass these restrictions or run the service exposed on a public network. It does not install RetroArch, locate game files automatically, find online strangers, forward router ports, or authenticate players. Game content and cores are never uploaded by this service.

Use two properly configured devices with compatible RetroArch cores and legally obtained matching game files to verify real netplay. Note that spectating support and flags can vary by RetroArch/core versions and host settings. Verification of the UI controller code is **not proof of successful two-device gameplay**.
