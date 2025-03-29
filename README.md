# Rune

**Rune** is a tool that combines different types of content (like YAML, HTML,
[Markdown](https://github.com/hyperifyio/rune/issues/22), 
[TSX](https://github.com/hyperifyio/rune/issues/26), SVG, PNG, ZIP, JPG, and 
JSON) into one easy-to-use JSON format.

This output is designed to securely serve content through a REST API.

Rune is built for everyone on your team — developers, designers, and content 
creators. It simplifies collaboration by supporting familiar formats like HTML, 
YAML, Markdown, and TSX, making it easy to manage assets, translations, and 
views all in one place.

## Metaphor: Rune and the Basket of Fruits

Think of Rune as a master basket weaver, skillfully crafting a basket to hold 
different kinds of fruits, each familiar to a specific audience:

- **HTML files** are like apples — crisp, structured, and familiar to frontend 
  developers.
- **YAML files** are like oranges — layered, segmented, and a favorite of 
  backend developers and system architects.
- **JSON translation files** are like bananas—rich in meaning, easy to peel 
  apart, and familiar for localization experts.
- **Markdown files** are like grapes — small, simple, and versatile, perfect for 
  documentation writers. *Markdown is not yet implemented.* See
  [#22](https://github.com/hyperifyio/rune/issues/22).
- **Assets (images, downloadable content, etc.)** are like cherries — vibrant, 
  eye-catching, and ready to be included.

Rune carefully weaves a basket — a JSON file — that organizes and holds all
these fruits together in a portable and structured way. This basket isn't just 
static; it can be used as-is or handed to a backend, where more fruits 
(additional data or assets) can be added later to enrich its contents.

The result is an adaptable basket ready for any use case, whether it's for a 
simple picnic (a static web content) or a grand feast (a dynamic API-driven 
application).

## Key Features

### 1. **Dynamic Content Processing**

- Consolidates YAML (`*.yml`) and HTML (`*.html`) files into a single JSON 
  output, embedding any referenced assets as Base64-encoded data URLs.
- Supports reusable components, nested children, and parameterized elements.

### 2. **Multilingual Support**

- Integrates translations from `translations/*.LANG.json` files.
- Outputs a flat `i18n` structure compatible with popular localization 
  libraries.

### 3. **Embedded Assets**

- Automatically embeds image files and assets as Base64-encoded data URLs.
- Supports SVG and other image formats with MIME type detection.

### 4. **Portability**

- Outputs a self-contained JSON file that includes all views, translations, and 
  assets.
- Ideal for static or dynamic web applications.

### 5. **Extensibility**

- Supports custom components and nested structures.
- Allows easy addition of new file types, assets, or features.

---

## Getting Started

### Prerequisites

To use Rune, ensure you have the following installed:

- Python 3.6 or later
- Required Python libraries:
  ```bash
  pip install -r requirements.txt
  ```

---

### Installation

You can install Rune using pip:

```bash
pip install hyperify-rune
```

Or clone the repository for development:

```bash
git clone https://github.com/hyperifyio/rune.git
cd rune
```

---

### Usage

#### **1. Using the Command Line Tool**

After installing with pip, you can use the `rune` command directly:

```bash
rune <directory> <output_type>
```

For example:
```bash
rune views json
```

#### **2. Prepare Your Project Directory**

Structure your project directory as follows:

```
project/                 # Contains YAML and HTML files
├── translations/        # Contains translation JSON files
│   ├── HelloWorld.en.json
│   └── HelloWorld.fi.json
├── assets/              # May contain images or other assets (or anywhere else on your system)
└── Makefile             # Makefile for build automation. Optional, for easier rebuild.
```

#### **3. Add YAML or HTML Views**

Example YAML file (`views/HelloWorld.yml`):

```yaml
- type: "View"
  name: "HelloWorld"
  body:
  - type: div
    classes:
    - "hello-world-container"
    body:
    - type: h1
      body:
      - "app.title"
  - type: p
    body:
    - "app.content"
```

Example HTML file (`views/HelloWorld.html`):

```html
<View name="HelloWorld">
  <div class="hello-world-container">
    <h1>app.title</h1>
    <p>app.content</p>
  </div>
</View>
```

#### **4. Add Translations**

Create translation files in `translations/` (e.g., `HelloWorld.en.json`):

```json
{
  "app.title": "Hello, World!",
  "app.content": "Welcome to Rune!"
}
```

#### **5. Build the Project**

Run Rune to merge all YAML, HTML, and translation files into a single JSON:

```bash
python3 rune.py views json
```

The output will look like this:

```json
[
  {
    "type": "View",
    "name": "HelloWorld",
    "body": [
      {
        "type": "div",
        "classes": ["hello-world-container"],
        "body": [
          {"type": "h1", "body": ["app.title"]},
          {"type": "p", "body": ["app.content"]}
        ]
      }
    ]
  },
  {
    "type": "i18n",
    "data": {
      "en": {
        "app.title": "Hello, World!",
        "app.content": "Welcome to Rune!"
      }
    }
  }
]
```

---

## Advanced Features

### **Reusable Components**

Define components with parameters and children:

Example (`views/UsageCard.html`):
```html
<Component name="UsageCard">
  <div class="card">
    <UnfoldableCard title="usageCard.title">
      <Component.Children></Component.Children>
    </UnfoldableCard>
  </div>
</Component>
```

### **Embedded Assets**

Embed files directly into the JSON output:

Example YAML asset (`views/assets.yml`):
```yaml
- type: "Asset"
  name: "logo"
  body: "data:image/png;base64,xxxxx"
```

### **Image Handling**

Automatically embed images referenced in properties like `Image`, `src`, or custom attributes.

Example HTML (`views/Example.html`):
```html
<Foo heroImage="../assets/logo.png"></Foo>
```

---

## CLI Options

```bash
python3 rune.py <directory> <output_type>
```

- `<directory>`: The project directory containing `*.yml`, `*.html`, and `translations/`.
- `<output_type>`: Either `json` or `yml`.

---

## License

**Rune** is licensed under [./LICENSE.md](the Functional Source License, Version 1.1, MIT Future License).

---

## Contact

For questions, feedback, or commercial inquiries, contact us at [info@hyperify.io](mailto:info@hyperify.io).
