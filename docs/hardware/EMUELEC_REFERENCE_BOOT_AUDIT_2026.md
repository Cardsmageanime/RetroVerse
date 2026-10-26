# EmuELEC boot reference audit

Observed from user-inspected copies of files on the known EmuELEC FAT partition on 2026-10-23. The original card files were not modified or executed. This is reference evidence only.

## File inventory

| File | Bytes | SHA-256 | Inspection |
| --- | ---: | --- | --- |
| `aml_autoscript` | 1,466 | `ca11472e8367893740242e3570472154c4ff0fc5629007dfc70e079d418bc6a8` | U-Boot legacy uImage, script, uncompressed |
| `cfgload` | 1,938 | `195770793f0a6ba4f1dbc37c0bc7f726df6d154920cfa015445dcdf4890d36ff` | U-Boot legacy uImage, script, uncompressed |
| `config.ini` | 7,014 | `7082f75a3aa76c1a06abf80d3c1b45e43c791e6969d58ca3966e6ec5bbe86286` | Text configuration |
| `dtb.img` | 68,156 | `66f024a72e9e9c6efcf2e1e61ea6338afb29be12ff2b0da41d1b792b38d17966` | FDT v17; decompiled for read-only inspection |

## Reference DTB observations

- Root model: `Amlogic`
- Root compatible: `amlogic, g12a`
- `sd1@ffe05000`: disabled
- `sd2@ffe05000`: enabled; 4-bit bus; maximum frequency 100 MHz
- The two vendor nodes share register address `0xffe05000`. `dtc` reported a duplicate unit-address warning.
- These SD controller settings agree with the previously recorded Android vendor-tree observations. They corroborate the G12A family and identify the candidate SD controller in this EmuELEC DTB; they do not identify the exact PCB revision or establish compatibility with the RetroVerse mainline kernel.

## Script behavior observed in extracted strings

- `aml_autoscript` defines an SD-first, USB-second, eMMC-fallback flow using U-Boot device indices, then invokes vendor boot commands.
- The script includes `saveenv`. U-Boot documents this as saving the environment to persistent storage.
- `cfgload` imports optional configuration, loads `dtb.img` and `kernel.img`, then invokes `bootm`.
- These are executable bootloader scripts. Neither script was run. Do not execute or reuse them for RetroVerse without exact firmware matching and command-by-command review.

## Readiness status

This audit describes the EmuELEC reference files, not the installed device bootloader. It does not prove that the device accepts this external boot sequence, that its U-Boot MMC indices match the script, or that this DTB matches the RetroVerse kernel.

Keep these gates unchanged:

- `external_uboot_boot_path_verified = false`
- `board_dtb_matches_compiled_kernel = false`
- `external_sd_boot_verified = false`
- `can_flash = false`

Next hardware gate: verify the exact installed U-Boot boot path from a passive boot log or an exact matching vendor firmware/configuration. Do not use a generic recovery script or write to internal eMMC.
