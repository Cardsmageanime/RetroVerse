# RetroVerse controller-to-RetroArch configuration (preview)

RetroVerse can now **generate a two-player controller configuration snippet** with explicit Player 1 / Player 2 joypad indices and button mappings. It never writes to RetroArch's installed config, changes firmware, or accesses controllers. This allows a safe inspection step before applying settings.

Example `players.json`:
```json
{
  "players": [
    {"joypad_index": 0, "buttons": {"a": 1, "b": 0, "up": 12, "down": 13, "start": 9}},
    {"joypad_index": 1, "buttons": {"a": 1, "b": 0, "up": 12, "down": 13, "start": 9}}
  ]
}
```

Generate a *new* snippet file from the repository root:
```powershell
py online/retroarch/controller_config.py --players players.json --output retroverse-controller-preview.cfg
```

Use a different output filename if it already exists; the exporter deliberately refuses to overwrite it. Inspect its values, then use the RetroArch Input menu to configure the correct physical devices and buttons. The RetroArch controller IDs and button numbers may **differ from the browser Gamepad API**, especially across Windows, ARM Linux, and Bluetooth/USB drivers. These are not RetroArch autoconfig device-identification profiles, and the exporter is **not** yet linked to the browser's saved profile UI or the RetroArch launcher. Its output is only a review artifact; applying configurations safely will require separate verified work.

Official RetroArch configuration reference: https://github.com/libretro/RetroArch/blob/master/retroarch.cfg


## Opt-in launch integration

The **CLI Netplay bridge** can now load the same two-player JSON file into an ephemeral RetroArch configuration overlay using RetroArch's documented `--appendconfig` argument:

```powershell
py online/retroarch/netplay_bridge.py host --retroarch retroarch --core "C:\\RetroArch\\cores\\your_core.dll" --content "C:\\Games\\your_game.rom" --controller-profiles players.json
```

Use `--dry-run` first. The bridge validates both player configurations before launching, creates a temporary overlay only for this RetroArch session, and deletes it when RetroArch exits normally. **It does not edit your regular retroarch.cfg.** Avoid running multiple sessions from one shared config until tested, and leave RetroArch's `Save Configuration on Exit` disabled if you want no persistent changes. The launcher is a blocking CLI process; the local web Netplay panel is not yet wired to this controller-profile option.

Note: **The JSON joypad indices and button indices must correspond to RetroArch on the target device, not automatically to browser Gamepad API indices.** PlayStation/Xbox/Switch browser presets have not been translated into confirmed native RetroArch device-specific mappings. Real controller behavior needs verification.
