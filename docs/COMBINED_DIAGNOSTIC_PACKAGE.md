# Combined ARM64 diagnostic boot package

A manually triggered GitHub Actions workflow combines the **successful, pinned** kernel build run `39717680785` and diagnostic initramfs build run `39745766212`.

It downloads their artifacts via the repository Actions API, locates the compiled `Image`, a **reference-only** G12A DTB, and the gzip initramfs, then runs the existing staging and structural validation tools. It creates a downloadable diagnostic artifact, **not** a bootable SD image.

The reference DTB is explicitly not verified for the Vayava GameBox. Success means the pieces have plausible formats and valid checksums; it does not mean the bootloader, root filesystem, display, storage, or device hardware works.

To start, open GitHub Actions → **RetroVerse Combined Diagnostic Boot Package** → **Run workflow**.

Do not flash the produced ZIP. No internal Android or eMMC modification is intended.
