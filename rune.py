#!/usr/bin/python3
# Rune Preprocessor
# Copyright 2024-2025 HyperifyIO <info@hyperify.io>

import os
import sys
import yaml
import base64
import argparse
import json
from typing import List, Dict, Any
from collections import defaultdict
from bs4 import BeautifulSoup
import mistune
import esprima


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
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translation_data = json.load(f)

                    if isinstance(translation_data, dict):
                        translations_by_language[language_code].update(translation_data)
                    else:
                        raise ValueError(f"does not contain a dictionary at the root level.")
                except Exception as e:
                    raise ValueError(f"Error processing JSON file '{file_path}': {e}")

    if not translations_by_language:
        print(f"No .json translation files found in the language directory: {language_dir}", file=sys.stderr)

    return translations_by_language


def parse_html_element(element):
    """
    Recursively parses an HTML element into a structured dictionary.
    :param element: A BeautifulSoup Tag or NavigableString.
    :return: A dictionary representing the element or raw text if it's a string.
    """
    try:
        if isinstance(element, str):  # Handle plain strings
            text = element.strip()
            return text if text else None

        if not hasattr(element, 'name'):  # Handle cases where element has no tag name
            raise ValueError("Invalid HTML element: Missing 'name' attribute.")

        result = {"type": element.name}

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
                parsed_child = parse_html_element(child)
                if parsed_child:
                    children.append(parsed_child)

        if children:
            result["body"] = children

        return result
    except Exception as e:
        raise ValueError(f"Error parsing HTML element: {element}. Error: {e}")


def html_to_data_structure(html_content):
    wrapped_html = f"<root>{html_content}</root>"
    soup = BeautifulSoup(wrapped_html, 'lxml-xml')
    root_elements = soup.root.find_all(recursive=False)
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


def parse_markdown (text: str) -> str:
    return mistune.html(text)

# Parse Markdown file into data structure
def markdown_to_data_structure(file_path: str, is_component: bool) -> Dict[str, Any]:
    """
    Converts Markdown content into structured data for Rune with enhanced error reporting.
    :param file_path: The path to the Markdown file.
    :param is_component: If True, treats the Markdown as a component.
    :return: A structured dictionary for Rune.
    """
    try:
        with open(file_path, 'r') as f:
            markdown_content = f.read()

        html_content = parse_markdown(markdown_content)
        wrapped_html = f"<root>{html_content}</root>"
        soup = BeautifulSoup(wrapped_html, 'lxml-xml')

        # Extract the name from the file name
        file_name = os.path.basename(file_path)
        name = file_name.replace(".Component.md", "").replace(".md", "")

        result = {
            "type": "Component" if is_component else "View",
            "name": name,
            "body": []
        }

        root_elements = soup.root.find_all(recursive=False)
        data_structure = [parse_html_element(el) for el in root_elements]

        for element in data_structure:
            if element:
                result["body"].append(element)

        return result
    except Exception as e:
        raise ValueError(f"Error processing Markdown file '{file_path}': {e}")


# Process Markdown files
def merge_markdown_files(markdown_files: List[str]) -> List[Dict[str, Any]]:
    merged_data = []
    for file in markdown_files:
        try:
            is_component = file.endswith(".Component.md")
            data = markdown_to_data_structure(file, is_component)
            merged_data.append(data)
        except Exception as e:
            print(f"Error: Failed to process Markdown file '{file}': {e}", file=sys.stderr)
    return merged_data


def parse_tsx_to_html(tsx_code: str) -> str:
    """
    Parse TSX code into HTML. Elements that cannot be rendered directly are wrapped in HTML comments.
    """
    ast = esprima.parseScript(tsx_code, jsx=True)

    def transform_node(node):
        if not node:
            return ""

        if node.type == "Program":
            return "".join(transform_node(child) for child in node.body)

        elif node.type == "ExpressionStatement":
            return transform_node(node.expression)

        elif node.type == "JSXElement":
            opening_tag = transform_node(node.openingElement)
            children = "".join(transform_node(child) for child in node.children)
            closing_tag = transform_node(node.closingElement) if node.closingElement else ""
            return f"{opening_tag}{children}{closing_tag}"

        elif node.type == "JSXOpeningElement":
            attributes = " ".join(transform_node(attr) for attr in node.attributes)
            tag_name = node.name.name if node.name.type == "JSXIdentifier" else "unknown_JSXOpeningElement"
            return f"<{tag_name} {attributes}>".strip()

        elif node.type == "JSXClosingElement":
            tag_name = node.name.name if node.name.type == "JSXIdentifier" else "unknown_JSXClosingElement"
            return f"</{tag_name}>"

        elif node.type == "JSXText":
            return node.value.strip()

        elif node.type == "Literal":
            return str(node.value)

        elif node.type == "JSXExpressionContainer":
            expression = transform_node(node.expression)
            return f"<!-- JSX Expression: {expression} -->"

        elif node.type == "JSXAttribute":
            name = node.name.name
            value = transform_node(node.value) if node.value else ""
            return f"{name}={value}"

        elif node.type == "JSXSpreadAttribute":
            return "<!-- Spread attributes are not supported: {...props} -->"

        elif node.type == "JSXFragment":
            children = "".join(transform_node(child) for child in node.children)
            return f"<!-- Fragment start -->{children}<!-- Fragment end -->"

        elif node.type == "Identifier":
            return node.name

        elif node.type == "JSXIdentifier":
            return node.name

        elif node.type == "BinaryExpression":
            left = transform_node(node.left)
            right = transform_node(node.right)
            operator = node.operator
            return f"({left} {operator} {right})"

        elif node.type == "CallExpression":
            callee = transform_node(node.callee)
            args = ", ".join(transform_node(arg) for arg in node.arguments)
            return f"<!-- Function call: {callee}({args}) -->"

        elif node.type == "VariableDeclaration":
            return "<!-- Variable declaration: Not rendered in HTML -->"

        elif node.type == "FunctionDeclaration":
            return "<!-- Function declaration: Not rendered in HTML -->"

        elif node.type == "ImportDeclaration":
            return f"<!-- Import: {transform_node(node.source)} -->"

        # Add more node types here as needed
        else:
            return f"<!-- Unsupported node type: {node.type} -->"

    return transform_node(ast)


def merge_tsx_files(tsx_files: List[str]) -> List[Dict[str, Any]]:
    """
    Parse TSX files and convert them to a structured data format for components or views.
    """
    merged_data = []
    for file in tsx_files:
        try:
            with open(file, 'r') as f:
                tsx_code = f.read()
                html_content = parse_tsx_to_html(tsx_code)
                wrapped_html = f"<root>{html_content}</root>"
                soup = BeautifulSoup(wrapped_html, 'lxml-xml')

                # Extract the name from the file name
                file_name = os.path.basename(file)
                name = file_name.replace(".Component.tsx", "").replace(".tsx", "")
                is_component = file_name.endswith(".Component.tsx")

                result = {
                    "type": "Component" if is_component else "View",
                    "name": name,
                    "body": []
                }

                # Parse the root elements
                root_elements = soup.root.find_all(recursive=False)
                data_structure = [parse_html_element(el) for el in root_elements]

                for element in data_structure:
                    if element:
                        result["body"].append(element)

                merged_data.append(result)
        except Exception as e:
            print(f"Error: Failed to process TSX file '{file}': {e}", file=sys.stderr)
    return merged_data


# Merge all YAML files in a directory into a single array and print it as JSON or YAML
def main(directory: str, output_type: str, language_dir: str):

    # Get all .yml files in the directory
    yaml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.yml')]

    # Get all .html files in the directory
    html_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.html')]

    # Get all .md files in the directory
    markdown_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.md')]

    # Get all .tsx files in the directory
    tsx_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.tsx')]

    if not yaml_files and not html_files and not markdown_files and not tsx_files:
        print(f"No .yml, .html, .md, or .tsx files found in the directory: {directory}", file=sys.stderr)
        return

    try:

        if os.path.isdir(language_dir):
            translations = get_all_translations(language_dir)
        else:
            # print(f"Translation directory '{language_dir}' does not exist. Skipping translations.", file=sys.stderr)
            translations = {}

        # Merge YAML and HTML data
        merged_data = []
        if yaml_files:
            yaml_data = merge_yaml_files(yaml_files)
            merged_data.extend(yaml_data)

        if html_files:
            html_data = merge_html_files(html_files)
            merged_data.extend(html_data)

        if markdown_files:
            markdown_data = merge_markdown_files(markdown_files)
            merged_data.extend(markdown_data)

        if tsx_files:
            tsx_data = merge_tsx_files(tsx_files)
            merged_data.extend(tsx_data)

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
