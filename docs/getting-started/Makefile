
all: build

build: getting-started.json

update: update-rune build

update-rune:
	git pull

clean:
	rm -f getting-started.json

getting-started.json: src/**/*.html src/**/*.json ../../rune.py Makefile
	../../rune.py . json > $@
