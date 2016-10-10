all: dependencies build

dependencies:
	npm install

build: dependencies
	webpack --progress --colors

watch:
	webpack --progress --colors --watch

run:
	python application.py
