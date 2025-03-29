#!/usr/bin/python3
# Rune Preprocessor Entry Point
# Copyright 2024-2025 HyperifyIO <info@hyperify.io>

import sys
import os
import argparse
from . import main

def run():
    parser = argparse.ArgumentParser(description="Merge all YAML files in a directory into a single array and print it as JSON or YAML.")
    parser.add_argument("directory", type=str, help="Directory containing the YAML files to merge.")
    parser.add_argument("output_type", type=str, choices=['json', 'yml'], help="Output format: 'json' or 'yml'.")
    parser.add_argument("--language-dir", type=str, help="Directory containing translation files. Defaults to 'translations' in the input directory.")
    
    args = parser.parse_args()
    
    # If language_dir is not provided, use the default path
    if not args.language_dir:
        args.language_dir = os.path.join(args.directory, "translations")
    
    main(args.directory, args.output_type, args.language_dir)

if __name__ == "__main__":
    run() 