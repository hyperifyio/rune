import sys
import unittest
from unittest.mock import patch


class TestAssetsDirCLI(unittest.TestCase):
    def test_parser_exposes_assets_dir_option(self):
        from hyperify_rune import __main__ as cli
        self.assertTrue(hasattr(cli, "create_parser"), "CLI should expose create_parser()")
        parser = cli.create_parser()
        help_text = parser.format_help()
        self.assertIn("--assets-dir", help_text)

    def test_assets_dir_propagates_to_config(self):
        from hyperify_rune import __main__ as cli
        with patch.object(cli, 'process_files', return_value=None) as _:
            with patch.object(sys, 'argv', ['rune', '--assets-dir', 'out/assets', 'some_dir', 'json']):
                from hyperify_rune import config as rune_config
                # Ensure clean state
                try:
                    rune_config.config.assetsDir = None
                except Exception:
                    pass
                cli.main()
                self.assertEqual(rune_config.config.assetsDir, 'out/assets')

    def test_default_assets_dir_is_none(self):
        from hyperify_rune import __main__ as cli
        with patch.object(cli, 'process_files', return_value=None) as _:
            with patch.object(sys, 'argv', ['rune', 'some_dir', 'json']):
                from hyperify_rune import config as rune_config
                try:
                    rune_config.config.assetsDir = 'should-be-cleared'
                except Exception:
                    pass
                cli.main()
                self.assertIsNone(rune_config.config.assetsDir)

    def test_cli_overrides_existing_config_value(self):
        from hyperify_rune import __main__ as cli
        with patch.object(cli, 'process_files', return_value=None) as _:
            with patch.object(sys, 'argv', ['rune', '--assets-dir', '/override', 'some_dir', 'json']):
                from hyperify_rune import config as rune_config
                # Pre-set a different value to ensure CLI wins
                try:
                    rune_config.config.assetsDir = '/preset'
                except Exception:
                    pass
                cli.main()
                self.assertEqual(rune_config.config.assetsDir, '/override')


if __name__ == '__main__':
    unittest.main()
