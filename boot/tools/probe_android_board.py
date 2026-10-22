#!/usr/bin/env python3
"""Read-only Android hardware survey over ADB; no rooting, flashing, or rebooting."""
import argparse, json, shutil, subprocess, sys
from datetime import datetime, timezone

FIELDS = {
    "soc_platform": "getprop ro.board.platform",
    "hardware": "getprop ro.hardware",
    "product_board": "getprop ro.product.board",
    "bootloader_version": "getprop ro.bootloader",
    "device_tree_model": "if [ -r /proc/device-tree/model ]; then tr '\\000' ' ' </proc/device-tree/model; fi",
    "device_tree_compatible": "if [ -r /proc/device-tree/compatible ]; then tr '\\000' ' ' </proc/device-tree/compatible; fi",
    "kernel_release": "uname -r",
    "mmc_hosts": "ls /sys/class/mmc_host 2>/dev/null",
}
def survey(adb="adb"):
    rows={}
    for key,command in FIELDS.items():
        result=subprocess.run([adb,"shell","sh","-c",command],capture_output=True,text=True,timeout=15,check=False)
        rows[key]={"ok":result.returncode==0,"value":result.stdout.strip()[:1024] if result.returncode==0 else ""}
    return rows
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",help="New local JSON output path (never overwrites)")
    a=p.parse_args()
    if shutil.which("adb") is None:p.error("Install Android platform-tools (adb) first")
    d=subprocess.run(["adb","devices"],capture_output=True,text=True,timeout=15,check=True).stdout
    connected=[x for x in d.splitlines()[1:] if x.strip().endswith("\tdevice")]
    if len(connected)!=1:p.error("Exactly one ADB-authorized device must be connected")
    report={"project":"RetroVerse","survey_type":"read-only-android-board-probe","survey_utc":datetime.now(timezone.utc).isoformat(),"results":survey(),
     "caution":"This is not proof of U-Boot SD boot support. Does not report serial number, MAC, accounts or other personal data.","board_boot_verified":False}
    rendered=json.dumps(report,indent=2)+"\n"
    if a.output:
        from pathlib import Path
        target=Path(a.output)
        with target.open("x",encoding="utf-8") as f:f.write(rendered)
        print("Survey written to",target)
    else:print(rendered)
    return 0
if __name__=="__main__":sys.exit(main())
