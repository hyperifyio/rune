import os
import tempfile
import unittest

from hyperify_rune.path_utils import build_asset_url


class TestPathUtils(unittest.TestCase):
    def test_build_asset_url_with_prefix(self):
        url = build_asset_url(
            filename="logo.png",
            output_json_path="/tmp/out/data.json",
            assets_dir="/ignored",
            assets_prefix="/static",
        )
        self.assertEqual(url, "/static/logo.png")

    def test_build_asset_url_strips_trailing_slash_in_prefix(self):
        url = build_asset_url(
            filename="logo.png",
            output_json_path="/tmp/out/data.json",
            assets_dir="/ignored",
            assets_prefix="/static/",
        )
        self.assertEqual(url, "/static/logo.png")

    def test_build_asset_url_relative_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "build")
            assets_dir = os.path.join(tmp, "assets")
            os.makedirs(out_dir, exist_ok=True)
            os.makedirs(assets_dir, exist_ok=True)
            output_json_path = os.path.join(out_dir, "data.json")
            # Create a file path within assets dir
            filename = "images/logo.png"
            full_asset_path = os.path.join(assets_dir, filename)
            os.makedirs(os.path.dirname(full_asset_path), exist_ok=True)
            with open(full_asset_path, "wb") as f:
                f.write(b"fake")

            url = build_asset_url(
                filename=filename,
                output_json_path=output_json_path,
                assets_dir=assets_dir,
                assets_prefix=None,
            )

            # Relative path from out_dir to assets_dir/filename
            expected = os.path.relpath(full_asset_path, start=out_dir).replace("\\", "/")
            self.assertEqual(url, expected)

    def test_build_asset_url_requires_filename(self):
        with self.assertRaises(ValueError):
            build_asset_url(
                filename="",
                output_json_path="/tmp/out/data.json",
                assets_dir="/tmp/assets",
                assets_prefix=None,
            )


if __name__ == "__main__":
    unittest.main()
