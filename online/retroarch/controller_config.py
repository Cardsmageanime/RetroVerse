#!/usr/bin/env python3
"""Generate an opt-in RetroArch controller *snippet* for Player 1 and Player 2.

Never touches retroarch.cfg, Android, or connected controllers. Indices in
RetroArch may differ from browser Gamepad API indices. Verify in RetroArch.
"""
import argparse
import json
from pathlib import Path

BUTTONS = ("a", "b", "x", "y", "start", "select", "l", "r",
           "up", "down", "left", "right", "l2", "r2", "l3", "r3")
DEFAULTS = {"a": 1, "b": 0, "x": 3, "y": 2, "start": 9, "select": 8,
            "l": 4, "r": 5, "l2": 6, "r2": 7, "l3": 10, "r3": 11,
            "up": 12, "down": 13, "left": 14, "right": 15}

def validate_player(config):
    if not isinstance(config, dict):
        raise ValueError("Player configuration must be an object")
    if set(config) - {"joypad_index", "buttons"}:
        raise ValueError("Unknown player fields")
    index = config.get("joypad_index")
    if type(index) is not int or not 0 <= index <= 15:
        raise ValueError("joypad_index must be integer 0..15")
    buttons = config.get("buttons", {})
    if not isinstance(buttons, dict) or set(buttons) - set(BUTTONS):
        raise ValueError("Invalid button assignments")
    for key, value in buttons.items():
        if type(value) is not int or not 0 <= value <= 63:
            raise ValueError("Invalid button index for " + key)
    return index, buttons

def generate(players):
    if not isinstance(players, list) or len(players) != 2:
        raise ValueError("Exactly two player configurations required")
    parsed = [validate_player(p) for p in players]
    if parsed[0][0] == parsed[1][0]:
        raise ValueError("Players must use different joypad indices")
    lines = ["# RetroVerse generated controller bindings; review before use.",
             "# Standalone snippet only. Does NOT change existing RetroArch settings.",
             "# Joypad indices may differ from browser Gamepad API indices."]
    for player, (index, buttons) in enumerate(parsed, 1):
        lines += ["", f"input_player{player}_joypad_index = \"{index}\""]
        for name in BUTTONS:
            if name in buttons:
                lines.append(f"input_player{player}_{name}_btn = \"{buttons[name]}\"")
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--players", required=True, type=Path, help="JSON containing a 'players' array")
    parser.add_argument("--output", required=True, type=Path, help="New snippet path (must not exist)")
    args = parser.parse_args()
    if args.players.resolve() == args.output.resolve():
        parser.error("Input and output files must be different")
    try:
        data = json.loads(args.players.read_text(encoding="utf-8"))
        text = generate(data["players"])
        with args.output.open("x", encoding="utf-8") as target:
            target.write(text)
    except (KeyError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("Generated review-only RetroArch controller snippet:", args.output)

if __name__ == "__main__":
    main()
