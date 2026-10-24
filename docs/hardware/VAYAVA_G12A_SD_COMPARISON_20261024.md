# Vayava Franklin — G12A SD interface comparison (2026-10-24)

Status: **reference comparison only; no bootable board DTB selected**.

## Evidence supplied from local device tree analysis

Legacy decompiled EmuELEC tree (`RetroVerse-Boot-Reference/emuelec-dtb.dts`):
- root model `Amlogic`, `coreelec-dt-id = "g12a_s905x2_2g"`
- `sd2@ffe05000`: enabled, size `0x800`, GIC SPI 190, bus width 4
- declared maximum frequency 100 MHz; nested `sd` settings show 50 MHz
- nested card detect `gpio_cd = <0x27 0x30 0x00>`; phandle and GPIO index **not resolved**
- vendor-specific controller compatible string and pinctrl definitions; do not copy into mainline

Linux 7.3 `meson-g12-common.dtsi`:
- `sd_emmc_b: mmc@ffe05000` size `0x800`, GIC SPI 190, default disabled
- upstream `amlogic,meson-axg-mmc` driver binding
- SD pinctrl candidates `sdcard_c_pins` / `sdcard_clk_gate_c_pins`

Linux 7.3 reference boards:
- U200: enables `sd_emmc_b`, 4-bit, 50 MHz, GPIOC_6 active-low CD, `vddao_3v3` supplies
- X96 Max: same pinctrl and GPIOC_6, maximum 100 MHz, `vddao_3v3` supplies
- regulator labels and GPIO selections **belong to those boards**; they are NOT Vayava confirmations.

## Blockers before selecting a mainline DTB

1. Resolve legacy `phandle = <0x27>` to its GPIO controller and interpret `0x30` within vendor GPIO numbering.
2. Verify real card-detect polarity and SD pin mapping, not just controller register address.
3. Confirm supply rails/regulator ownership from Vayava board evidence.
4. Reconcile SD CMD18 CRC errors; consider conservative <=25 MHz for initial *diagnostic* tests only, not a validated operating rate.
5. Compare bootloader external kernel handoff, boot arguments, root filesystem, and on-device observations.
6. Keep `sd_emmc_c` / eMMC and Android storage unchanged. **Do not flash**.

Kernel baseline: Linux 7.3.0, source commit `17bb0e2f6c8043f70a693a5f3797471cbed354c8`.
No validated board-matched kernel/DTB, bootable SD image, or hardware RetroVerse boot currently exists.

## Follow-up: legacy GPIO phandle resolution

User's decompiled EmuELEC DTS has `pinctrl@ff634480/banks@ff6346c0` with `gpio-controller`, `#gpio-cells = <2>`, and `phandle = <0x27>`. The SD node's `gpio_cd = <0x27 0x30 0x00>` therefore refers to this peripheral GPIO provider, index `0x30` (48), and raw flags cell zero. This **does not yet prove** the equivalent Linux 7.3 named GPIO, electrical polarity, or detection behavior. Vendor `gpio_cd` semantics are not interchangeable with upstream `cd-gpios` without validation.

Suggested next read-only check: compare `include/dt-bindings/gpio/meson-g12a-gpio.h` constants and upstream pinctrl driver ranges with the vendor DTS GPIO bank/pinmux mapping. Do not replace the upstream candidate's card-detect GPIO based on the raw numeric index alone.

## Additional pinctrl evidence (user-observed)

Legacy `sd_all_pins` uses `sdcard_d0_c` through `sdcard_d3_c`, `sdcard_cmd_c`, and `sdcard_clk_c`, matching mainline G12A group names. Electrical configuration may differ.

Linux 7.3 `meson-g12a-gpio.h` reports `GPIOC_6 = 47`, `GPIOC_7 = 48`. Legacy `gpio_cd = <0x27 0x30 0x00>` uses numeric index 48 under the peripheral GPIO provider. **It is not established that the legacy and upstream numbering match.** Neither `GPIOC_6` nor `GPIOC_7` has been verified as the Franklin card-detect GPIO; polarity is also unverified. Keep this as a blocker, not a candidate board setting.

## Linux 7.3 GPIO bank mapping follow-up

User-observed `include/dt-bindings/gpio/meson-g12a-gpio.h` defines `GPIOC_6 = 47`, `GPIOC_7 = 48`; `pinctrl-meson-g12a.c` includes the C bank `GPIOC_0` through `GPIOC_7`. The legacy SD card-detect tuple `<0x27 0x30 0x00>` is a GPIO reference to the peripheral bank provider with numeric offset 48. **Tentative inference:** if vendor offsets are identical to upstream, the reference corresponds to GPIOC_7, not GPIOC_6. This needs cross-check against vendor pin numbering and observed card insertion/removal, including polarity. Do not infer that raw flags cell 0 means an active-high card detect under the vendor binding.

Next evidence requested: inspect G12A pinctrl provider in the legacy DTB, find vendor GPIO bank numbering definitions (if available), and gather read-only card-detect behavior from the running known-working operating system. No device tree may be marked board-matched based solely on this inference.
