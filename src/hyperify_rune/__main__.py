#!/usr/bin/python3
# Rune Preprocessor Entry Point
# Copyright 2024-2025 HyperifyIO <info@hyperify.io>

import sys
import os
import argparse
from . import process_files
from .config import config as rune_config


def create_parser() -> argparse.ArgumentParser:
    """Create and return the CLI argument parser for Rune."""
    parser = argparse.ArgumentParser(
        description=(
            "Merge all YAML/HTML/Markdown/TSX files in a directory into a single array "
            "and print it as JSON or YAML."
        )
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing the source files to process.",
    )
    parser.add_argument(
        "output_type",
        type=str,
        choices=["json", "yml"],
        help="Output format: 'json' or 'yml'.",
    )
    
    parser.add_argument(
        "--assets-dir",
        dest="assets_dir",
        type=str,
        default=None,
        help="Directory to write extracted assets; default embeds as data URLs.",
    )
    parser.add_argument(
        "--assets-prefix",
        dest="assets_prefix",
        type=str,
        default=None,
        help="Prefix to add to emitted asset URLs (e.g. /static).",
    )
    return parser


def main():
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Update global configuration from CLI flags
        rune_config.assetsPrefix = args.assets_prefix if args.assets_prefix else None
        rune_config.assetsDir = args.assets_dir if getattr(args, "assets_dir", None) else None

        process_files(
            args.directory,
            args.output_type,
            os.path.join(args.directory, "translations"),
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
