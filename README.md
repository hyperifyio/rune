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

Example app YML (not using reusable components yet):

```
- lang: "en"
  type: "View"
  name: "HelloWorld"
  body:
  - type: div
    classes:
    - "hello-world-container"
    body:
    - type: div
      classes:
      - "header"
      body:
      - type: h1
        body:
        - "Hello, World!"
    - type: div
      classes:
      - "content"
      body:
      - type: p
        body:
        - "Welcome to the Hello World App. This is a simple example to demonstrate the schema."
    - type: div
      classes:
      - "footer"
      body:
      - type: button
        onClick:
          navigate: "/app/start"
        classes:
        - "start-button"
        body:
        - "Get Started"
```
