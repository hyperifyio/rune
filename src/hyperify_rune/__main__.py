#!/usr/bin/python3
# Rune Preprocessor Entry Point
# Copyright 2024-2025 HyperifyIO <info@hyperify.io>

import sys
import os
import argparse
from . import process_files

def main():
    try:
        parser = argparse.ArgumentParser(description="Merge all YAML files in a directory into a single array and print it as JSON or YAML.")
        parser.add_argument("directory", type=str, help="Directory containing the YAML files to merge.")
        parser.add_argument("output_type", type=str, choices=['json', 'yml'], help="Output format: 'json' or 'yml'.")
        args = parser.parse_args()
        
        process_files(args.directory, args.output_type, os.path.join(args.directory, "translations"))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
