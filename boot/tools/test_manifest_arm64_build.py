import tempfile
import unittest
from pathlib import Path
from manifest_arm64_build import manifest

class BuildManifestTests(unittest.TestCase):
    def test_reject_missing_image(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                manifest(folder,"test")
    def test_collect_image_and_dtb(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            image=root/"arch/arm64/boot/Image"
            dtb=root/"arch/arm64/boot/dts/amlogic/example.dtb"
            image.parent.mkdir(parents=True)
            dtb.parent.mkdir(parents=True)
            image.write_bytes(b"image")
            dtb.write_bytes(b"dtb")
            data=manifest(folder,"fixture")
            self.assertTrue(data["build_verified"])
            self.assertFalse(data["boot_tested"])
            self.assertFalse(data["gamebox_compatible"])
            self.assertEqual(data["kernel_image"]["bytes"],5)
            self.assertEqual(len(data["device_trees"]),1)
    def test_reject_missing_dtbs(self):
        with tempfile.TemporaryDirectory() as folder:
            image=Path(folder)/"arch/arm64/boot/Image"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image")
            with self.assertRaises(ValueError):
                manifest(folder,"test")
if __name__=="__main__":unittest.main()
