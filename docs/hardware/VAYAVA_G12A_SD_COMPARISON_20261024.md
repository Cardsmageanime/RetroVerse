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
