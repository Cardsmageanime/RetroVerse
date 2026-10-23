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

## Visual two-player Netplay controller panel

The local Netplay panel at `http://127.0.0.1:8768/netplay` now includes an **optional** Player 1 / Player 2 assignment section. Enable it and choose distinct RetroArch joypad indices, plus each player's A-button index. Use **Validate & Preview** to inspect the generated controller overlay before approving **Launch RetroArch**.

The local server keeps this overlay in a unique temporary directory until the RetroArch subprocess exits, then removes the directory. No `retroarch.cfg` file is overwritten by this implementation. RetroArch itself can have separate settings that save on exit, so turn off its **Save Configuration on Exit** option when testing and back up its settings.

This first visual integration sets controller indices and A-button bindings only; the standalone JSON exporter still supports the wider set of RetroArch button mappings. The displayed Xbox, PlayStation, and Switch choices are **browser-standard suggestions**, not detected native RetroArch autoconfig hardware mappings. The operator must confirm indices in the actual RetroArch Input settings.

No real gamepad compatibility or physical GameBox test has yet been demonstrated.

## Full visual digital-button editor

The Netplay menu now offers editable indices for all 16 digital RetroPad inputs for **each of two players**: A/B/X/Y, Start/Select, D-pad, L/R, L2/R2, and L3/R3. Use **Reset to standard mapping** to restore sample assignments, then **Validate & Preview** to see the generated overlay. RetroArch joypad button indices and browser Gamepad API button indices are not always the same.

**Scope:** This milestone does *not* yet remap analog-stick axes in RetroArch, automatically detect native joypad indices, or verify physical controllers. Testing remains required for each actual platform and driver. These assignments are optional and only used when controller overrides are enabled.

## Analog stick milestone

The RetroVerse Netplay panel now includes independent left/right X/Y axis assignments for Player 1 and Player 2. An optional controller overlay produces `input_playerN_l_x_plus_axis` and corresponding minus bindings (and similarly for Y and right stick). Indices must match the *native RetroArch* joypad driver; browser mappings are not authoritative. Axis direction uses RetroArch's native plus/minus convention, and the form resets to 0/1/2/3 for each player.

RetroArch's `input_analog_deadzone` is a **global setting**, not a per-player option. This change deliberately leaves it unchanged rather than pretending to support per-controller deadzones. Physical hardware detection, driver-specific mappings, real netplay playtests, and booting on the ARM GameBox remain unverified.

The Console Edition remains separate and is on hold.

## Physical controller identification milestone

The local RetroVerse Netplay menu now has **Scan connected controllers**. It uses the browser's read-only Gamepad API to show browser controller index, reported name/family (PlayStation, Xbox, Nintendo or generic), standard mapping state, button count, pressed button numbers, and current axis values. This is intended for verifying that a physical USB/Bluetooth gamepad is visible in the *browser*. It does not install device drivers, access firmware, pair Bluetooth devices, or prove that RetroArch sees the same device.

**Important:** Browser Gamepad API device indices are not guaranteed to correspond to RetroArch native joypad indices or button numbers. The diagnostic never silently assigns RetroArch joypad indices; users must verify these through RetroArch's Input settings. Some browsers require a button press and browser focus before a gamepad appears.

The local service serves its diagnostic script only on loopback and runs no network upload. Xbox/PlayStation/Nintendo labels are best-effort guesses from device-reported IDs, not hardware authentication. CI tests exercise synthetic gamepad data; **physical hardware/netplay compatibility remains untested**.
