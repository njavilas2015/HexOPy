-include .env
-include .devcontainer/.env

VENV=../venv
PYTHON=python
PIP=$(VENV)/bin/pip
ENV=${PWD}.env

install:
	$(PIP) install -r requirements.txt
	$(PIP) install --upgrade pip

types:
	cd src && stubgen -p onbbu -o stubs
	mv src/stubs/onbbu src/onbbu/stubs

build:
	rm -fr dist
	python -m build

publish:
	twine upload dist/*
	rm -fr dist

publish-test:
	twine upload --repository testpypi dist/*

