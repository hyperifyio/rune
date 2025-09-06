import sys
import unittest
from unittest.mock import patch


class TestAssetsPrefixCLI(unittest.TestCase):
    def test_parser_exposes_assets_prefix_option(self):
        from hyperify_rune import __main__ as cli
        self.assertTrue(hasattr(cli, "create_parser"), "CLI should expose create_parser()")
        parser = cli.create_parser()
        help_text = parser.format_help()
        self.assertIn("--assets-prefix", help_text)

    def test_assets_prefix_propagates_to_config(self):
        from hyperify_rune import __main__ as cli
        with patch.object(cli, 'process_files', return_value=None) as _:
            with patch.object(sys, 'argv', ['rune', '--assets-prefix', '/prefix', 'some_dir', 'json']):
                from hyperify_rune import config as rune_config
                # Ensure clean state
                try:
                    rune_config.config.assetsPrefix = None
                except Exception:
                    pass
                cli.main()
                self.assertEqual(rune_config.config.assetsPrefix, '/prefix')

    def test_default_assets_prefix_is_none(self):
        from hyperify_rune import __main__ as cli
        with patch.object(cli, 'process_files', return_value=None) as _:
            with patch.object(sys, 'argv', ['rune', 'some_dir', 'json']):
                from hyperify_rune import config as rune_config
                try:
                    rune_config.config.assetsPrefix = 'should-be-cleared'
                except Exception:
                    pass
                cli.main()
                self.assertIsNone(rune_config.config.assetsPrefix)


if __name__ == '__main__':
    unittest.main()
