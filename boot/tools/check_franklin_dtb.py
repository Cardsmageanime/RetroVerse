#!/usr/bin/env python3
"""Compile and inspect the research-only Franklin DTB. Never flash/boot it."""
import argparse
import pathlib
import shutil
import subprocess
import sys


def run(*args, stdout=None):
    return subprocess.run(args, check=True, text=True, stdout=stdout, capture_output=(stdout is None))


def find_node(dtb, name):
    queue = ["/"]
    while queue:
        node = queue.pop(0)
        children = run("fdtget", "-l", str(dtb), node).stdout.splitlines()
        for child in children:
            path = (node.rstrip("/") + "/" + child.strip())
            if child.strip() == name:
                return path
            queue.append(path)
    raise RuntimeError(f"Missing required node: {name}")


def property_value(dtb, node, prop):
    return run("fdtget", "-t", "s", str(dtb), node, prop).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", type=pathlib.Path, required=True, help="Linux 7.3 source tree")
    parser.add_argument("--output", type=pathlib.Path, required=True, help="Output directory")
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[2]
    source = root / "hardware/dts/meson-g12a-vayava-franklin-experimental.dts"
    for command in ("cpp", "dtc", "fdtget"):
        if shutil.which(command) is None:
            parser.error(f"Missing required command: {command}")
    if not source.is_file():
        parser.error(f"Missing DTS: {source}")
    include_dir = args.kernel / "arch/arm64/boot/dts/amlogic"
    if not (include_dir / "meson-g12a.dtsi").is_file():
        parser.error(f"Missing G12A kernel source: {include_dir}")
    args.output.mkdir(parents=True, exist_ok=True)
    preprocessed = args.output / "franklin.preprocessed.dts"
    dtb = args.output / "franklin-experimental.dtb"
    with preprocessed.open("w", encoding="utf-8") as fh:
        run("cpp", "-nostdinc", "-undef", "-D__DTS__", "-x", "assembler-with-cpp",
            "-I", str(include_dir), "-I", str(args.kernel / "include"), str(source), stdout=fh)
    run("dtc", "-I", "dts", "-O", "dtb", "-o", str(dtb), str(preprocessed))
    model = property_value(dtb, "/", "model")
    compatibles = property_value(dtb, "/", "compatible")
    if "experimental" not in model.lower() or "retroverse,vayava-franklin-experimental" not in compatibles:
        raise RuntimeError("Unexpected model/compatible in generated DTB")
    for node_name in ("mmc@ffe05000", "mmc@ffe07000"):
        path = find_node(dtb, node_name)
        status = property_value(dtb, path, "status")
        if status != "disabled":
            raise RuntimeError(f"SAFETY FAILURE: {path} status is {status!r}, expected disabled")
        print(f"PASS {path}: disabled")
    print(f"PASS Research-only DTB validated: {dtb}")
    print("NOT BOOT VERIFIED. DO NOT FLASH OR BOOT THIS DTB.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (subprocess.CalledProcessError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
