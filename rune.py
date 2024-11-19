#!/usr/bin/python3
# Rune YML Builder
# Copyright 2024 HyperifyIO <info@hyperify.io>

import os
import sys
import yaml
import base64
import argparse
import json
from typing import List, Dict, Any
from collections import defaultdict
from bs4 import BeautifulSoup


# Load the translation file
def load_translation(language_code):
    with open(f"{language_code}.json", "r") as f:
        return json.load(f)


# Translate key
def translate(key, translations):
    return translations.get(key, f"[{key} not found]")


# Merge YAML files to single list
def merge_yaml_files(yaml_files: List[str]) -> List[Dict[str, Any]]:
    merged_data = []
    for file in yaml_files:
        with open(file, 'r') as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                raise ValueError(f"YAML file {file} does not contain a list at the root level.")
    return merged_data


# Merge JSON files to single list
def merge_json_files(yaml_files: List[str]) -> List[Dict[str, Any]]:
    merged_data = []
    for file in yaml_files:
        with open(file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                raise ValueError(f"JSON file {file} does not contain a list at the root level.")
    return merged_data


# Embed images mentioned in the YAML
def embed_images(data: List[Dict[str, Any]], base_dir: str) -> List[Dict[str, Any]]:
    def embed_image_property(item: Dict[str, Any]):
        for key, value in item.items():
            if isinstance(value, dict):
                embed_image_property(value)
            elif isinstance(value, list):
                for sub_item in value:
                    if isinstance(sub_item, dict):
                        embed_image_property(sub_item)
            elif (key == 'image' or key.endswith('Image') or key.startswith('Image') or key == 'src' ) and isinstance(value, str) and (not value.startswith('Component.Param.')):
                image_path = os.path.join(base_dir, value)
                if os.path.isfile(image_path):
                    with open(image_path, 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        mime_type = get_data_url_mime_type(os.path.splitext(image_path)[1][1:])
                        data_url = f"data:{mime_type};base64,{encoded_string}"
                        item[key] = data_url
                else:
                    raise FileNotFoundError(f"Image file not found: {image_path}")

    for obj in data:
        embed_image_property(obj)

    return data


def get_data_url_mime_type (type: str) -> str:
    if type.startswith("svg"):
        return "image/svg+xml"
    return "image/" + type


def get_all_translations(language_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Get all translation files in the given directory, grouped by language code, and merge them into dictionaries.

    :param language_dir: Directory containing translation files
    :return: Dictionary where keys are language codes and values are merged dictionaries of translations
    """
    translations_by_language = defaultdict(dict)

    # Loop through all files in the language directory
    for file in os.listdir(language_dir):
        if file.endswith(".json"):
            file_parts = file.rsplit('.', 3)
            if len(file_parts) >= 3:
                language_code = file_parts[-2]
                file_path = os.path.join(language_dir, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    translation_data = json.load(f)

                if isinstance(translation_data, dict):
                    translations_by_language[language_code].update(translation_data)
                else:
                    raise ValueError(f"JSON file {file_path} does not contain a dictionary at the root level.")

    if not translations_by_language:
        print(f"No .json translation files found in the language directory: {language_dir}", file=sys.stderr)

    return translations_by_language


def parse_html_element(element):
    result = {}
    result['type'] = element.name

    # Handle attributes
    if element.attrs:
        for attr, value in element.attrs.items():
            if attr == 'class':
                if isinstance(value, list):
                    result['classes'] = value
                elif isinstance(value, str):
                    if value.startswith('[') and value.endswith(']'):
                        result['classes'] = json.loads(value)
                    else:
                        result['classes'] = value.split()
            elif attr == 'onClick':
                # Assuming onClick attribute contains JSON string
                try:
                    result['onClick'] = json.loads(value)
                except json.JSONDecodeError:
                    result['onClick'] = value
            else:
                result[attr] = value

    # Handle children
    children = []
    for child in element.contents:
        if isinstance(child, str):
            text = child.strip()
            if text:
                children.append(text)
        else:
            children.append(parse_html_element(child))
    if children:
        result['body'] = children

    return result


def html_to_data_structure(html_content):
    soup = BeautifulSoup(html_content, 'lxml-xml')
    root_elements = soup.find_all(recursive=False)
    data_structure = [parse_html_element(el) for el in root_elements]
    return data_structure


def merge_html_files(html_files: List[str]) -> List[Dict[str, Any]]:
    merged_data = []
    for file in html_files:
        with open(file, 'r') as f:
            html_content = f.read()
            data = html_to_data_structure(html_content)
            merged_data.extend(data)
    return merged_data


# Merge all YAML files in a directory into a single array and print it as JSON or YAML
def main(directory: str, output_type: str, language_dir: str):

    # Get all .yml files in the directory
    yaml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.yml')]

    # Get all .html files in the directory
    html_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.html')]

    if not yaml_files and not html_files:
        print(f"No .yml or .html files found in the directory: {directory}", file=sys.stderr)
        return

    try:

        translations = get_all_translations(language_dir)

        # Merge YAML and HTML data
        merged_data = []
        if yaml_files:
            yaml_data = merge_yaml_files(yaml_files)
            merged_data.extend(yaml_data)

        if html_files:
            html_data = merge_html_files(html_files)
            merged_data.extend(html_data)

        embedded_data = embed_images(merged_data, directory)

        # Structure the output in the desired format
        i18n_data = {
            "type": "i18n",
            "data": translations
        }

        embedded_data.append(i18n_data)

        if output_type == 'json':
            print(json.dumps(embedded_data, indent=2))
        elif output_type == 'yml':
            print(yaml.dump(embedded_data, default_flow_style=False))
        else:
            print(f"Unsupported output type: '{output_type}'. Please use 'json' or 'yml'.", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Merge all YAML files in a directory into a single array and print it as JSON or YAML.")
    parser.add_argument("directory", type=str, help="Directory containing the YAML files to merge.")
    parser.add_argument("output_type", type=str, choices=['json', 'yml'], help="Output format: 'json' or 'yml'.")
    args = parser.parse_args()
    
    main(args.directory, args.output_type, os.path.join(args.directory, "translations"))
