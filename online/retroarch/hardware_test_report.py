"""Offline, privacy-conscious checklist for two-controller RetroArch hardware trials.

This tool records *manual observations*, not hardware detection or proof of
netplay. Nothing is transmitted; it writes only a user-selected new JSON file.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CHECKS = (
    "two_gamepads_visible_in_browser",
    "both_gamepads_visible_in_retroarch",
    "player_1_controls_only_player_1",
    "player_2_controls_only_player_2",
    "analog_and_buttons_respond",
    "two_device_netplay_connects",
    "two_device_netplay_playable",
)

def make_report(observations, platform="unspecified", notes=""):
    if not isinstance(observations, dict) or set(observations) != set(CHECKS):
        raise ValueError("Each required check must be supplied exactly once")
    if any(type(v) is not bool and v is not None for v in observations.values()):
        raise ValueError("Check values must be true, false or null (not tested)")
    if not isinstance(platform, str) or not 1 <= len(platform) <= 80:
        raise ValueError("Invalid platform label")
    if not isinstance(notes, str) or len(notes) > 1000:
        raise ValueError("Notes must be at most 1000 characters")
    return {"schema_version": 1, "platform": platform, "checks": observations,
            "notes": notes,
            "result": "passed" if all(v is True for v in observations.values())
            else "failed" if any(v is False for v in observations.values())
            else "incomplete"}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New local report filename")
    parser.add_argument("--platform", default="unspecified")
    parser.add_argument("--notes", default="")
    parser.add_argument("--answers", type=Path, help="Optional local JSON object of manual check answers")
    args = parser.parse_args(argv)
    try:
        answers = json.loads(args.answers.read_text(encoding="utf-8")) if args.answers else {k: None for k in CHECKS}
        report = make_report(answers, args.platform, args.notes)
        report["created_utc"] = datetime.now(timezone.utc).isoformat()
        with args.output.open("x", encoding="utf-8") as file:
            json.dump(report, file, indent=2)
            file.write("\n")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(report["result"], args.output)

if __name__ == "__main__":
    main()
