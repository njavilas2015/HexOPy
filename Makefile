-include .env
-include .devcontainer/.env

VENV=../venv
PYTHON=python
PIP=$(VENV)/bin/pip
ENV=${PWD}.env

install:
	$(PIP) install -r requirements.txt
	$(PIP) install --upgrade pip

lint:
	cd src && stubgen -p onbbu --output .

build:
	rm -fr dist
	python -m build

publish:
	twine upload dist/*
	rm -fr dist

publish-test:
	twine upload --repository testpypi dist/*

