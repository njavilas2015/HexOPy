-include .env
-include .devcontainer/.env

VENV=../venv
PYTHON=python
PIP=$(VENV)/bin/pip
ENV=${PWD}.env

install:
	$(PIP) install -r requirements.txt
	$(PIP) install --upgrade pip

build:
	python -m build

publish:
	twine upload dist/*

publish-test:
	twine upload --repository testpypi dist/*

