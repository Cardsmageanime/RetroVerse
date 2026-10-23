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
