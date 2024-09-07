# rune

Rune -- Dynamic YML content builder

### Usage

Create a makefile named `Makefile` in your project's YML data directory:

```Makefile
all: build

build: update-rune app.json

rune:
	git clone https://github.com/hyperifyio/rune.git rune

update-rune: rune
	cd rune && git pull

app.json: *.yml ./translations/*.json rune rune/rune.py Makefile
	rune/rune.py . json > $@
```

Create a directory `./translations` and files for each translation named like 
`HelloWorld.en.json` and `HelloWorld.fi.json`:

```json
{
  "app.title": "Hello, World!",
  "app.content": "Welcome to the Hello World App. This is a simple example to demonstrate the schema.",
  "app.startButton.label": "Get Started"
}
```

Then create files like `HelloWorld.yml`:

```
- type: "View"
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
        - "app.title"
    - type: div
      classes:
      - "content"
      body:
      - type: p
        body:
        - "app.content"
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
        - "app.startButton.label"
```

Then run `make build` and you'll get single `app.json` with all the data.