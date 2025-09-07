import os
import base64
import unittest
import tempfile
from hyperify_rune.assets import extract_data_url_to_assets_dir


# 1x1 transparent PNG
PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)
DATA_URL = f"data:image/png;base64,{PNG_BASE64}"


class TestAssetExtraction(unittest.TestCase):
    def test_extracts_png_and_names_by_sha256_with_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = extract_data_url_to_assets_dir(DATA_URL, tmpdir, "logo.png")
            self.assertTrue(os.path.isfile(path))
            # Verify filename structure: <sha256>.png
            expected_bytes = base64.b64decode(PNG_BASE64)
            import hashlib

            expected_hash = hashlib.sha256(expected_bytes).hexdigest()
            basename = os.path.basename(path)
            self.assertTrue(basename.endswith(".png"))
            self.assertTrue(basename.startswith(expected_hash))

            # Idempotency: second call returns same path and does not error
            path2 = extract_data_url_to_assets_dir(DATA_URL, tmpdir, "logo.png")
            self.assertEqual(path2, path)

    def test_invalid_input_raises(self):
        with self.assertRaises(ValueError):
            extract_data_url_to_assets_dir("not-a-data-url", "/tmp")


if __name__ == "__main__":
    unittest.main()
