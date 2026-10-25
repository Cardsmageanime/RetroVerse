# Milestone 12B — Franklin SD GPIO mapping investigation

**Status:** research-only; GPIO equivalence and electrical configuration **not verified**.
**Target:** Vayava TVBOX-GAME / Franklin, Amlogic G12A-family candidate.
**Safety:** DO NOT BOOT OR FLASH the experimental DTB, run legacy `aml_autoscript`, or change internal Android/eMMC.

## Evidence already collected
- Decompiled EmuELEC reference: `sd2@ffe05000` is enabled, uses a 4-bit bus and declares `gpio_cd = <0x27 0x30 0x00>`.
- Vendor GPIO phandle `0x27` resolves to the GPIO controller under `pinctrl@ff634480/banks@ff6346c0`, with `#gpio-cells = <2>`.
- Mainline G12A example boards (FBX8AM, Radxa Zero, SEI510, U200, X96 Max) commonly use `&sd_emmc_b`, `&sdcard_c_pins`, and `cd-gpios = <&gpio GPIOC_6 GPIO_ACTIVE_LOW>`, plus board-local `vddao_3v3` supply references.
- In the upstream G12A GPIO binding `GPIOC_6 = 47` and `GPIOC_7 = 48`. **Do not infer** that vendor's `0x30` (48) equals `GPIOC_7`; verify the vendor driver's GPIO index basis, bank offsets, flags and physical net.
- The copied vendor DTS showed a CPU PWM regulator; it has **not** established SD-card VMMC/VQMMC supply routing.
- Android-side SD CMD18 CRC errors were previously observed. Card detect and rail assumptions remain unverified.

## Next investigation: inspect offline, do not apply DT changes
From the RetroVerse checkout on Linux Mint:

```bash
cd ~/Downloads/RetroVerse-Development
REF="$HOME/Downloads/RetroVerse-Boot-Reference/emuelec-dtb.dts"
{
  echo '=== VENDOR SD PIN GROUPS ==='
  grep -n -A 100 'sd_all_pins {' "$REF" | head -115
  echo '=== VENDOR GPIO BANK CONTEXT ==='
  grep -n -B 18 -A 14 'phandle = <0x27>' "$REF"
  echo '=== MAINLINE G12A GPIO DEFINITIONS ==='
  grep -nE 'GPIOC_[0-7]' "$HOME/src/linux/include/dt-bindings/gpio/meson-g12a-gpio.h"
  echo '=== MAINLINE SD EXAMPLE ==='
  sed -n '/&sd_emmc_b {/,/^};/p' "$HOME/src/linux/arch/arm64/boot/dts/amlogic/meson-g12a-x96-max.dts"
} > "$HOME/Downloads/RetroVerse-GPIO-Mapping.txt"
```

Upload `~/Downloads/RetroVerse-GPIO-Mapping.txt` for review.

## Release gates still blocked
1. Silicon SKU identity independently proven — no.
2. Board-matched mainline DTB, pin polarity and SD power rails independently confirmed — no.
3. External U-Boot loading sequence and nonpersistent recovery path verified — no.
4. GameBox SD-link reliability confirmed — no.

This note is for review only; it is **not** permission to create a bootable SD image, select arbitrary U-Boot addresses, or flash any storage.
