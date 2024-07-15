# rune

Rune -- Dynamic YML content builder

### Usage

Create a makefile named `Makefile` in your project's YML data directory:

```Makefile
all: build

build: update-rune app-en.json app-fi.json

rune:
	git clone https://github.com/hyperifyio/rune.git rune

update-rune: rune
	cd rune && git pull

app-en.json: *.en.yml rune rune/rune Makefile
	rune/rune . json en > app-en.json

app-fi.json: *.fi.yml rune rune/rune Makefile
	rune/rune . json fi > app-fi.json
```

Example YML:

```yml
- lang: "en"
  type: "View"
  name: "HelloWorld"
  body:
  - type: Layout
    Title: "Hello, World!"
    body:
    - type: p
      body:
      - "Welcome to the Hello World App. This is a simple example to demonstrate the schema."

- type: Component
  name: Layout
  params:
  - type: string
    name: Title
  - type: body
    name: Outlet
  body:
  - type: div
    classes:
    - "layout"
    body:
    - type: Header
      Title:
        type: Title
    - type: Content
      body:
      - type: Outlet
    - type: Footer

- type: "Component"
  name: "Content"
  params:
  - type: body
    name: Outlet
  body:
  - type: div
    classes:
    - "content"
    body:
    - type: Outlet

- type: "Component"
  name: "Header"
  params:
  - type: string
    name: Title
  body:
  - type: div
    classes:
    - "header"
    body:
    - type: h1
      body:
      - type: Title

- type: "Component"
  name: "Footer"
  body:
  - type: div
    classes:
    - "footer"
    body:
    - type: button
      onClick:
        navigate: "/app/start"
      classes:
      - "start-button"
```
