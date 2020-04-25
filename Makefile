.PHONY: help install-dependencies

help:
	@echo ""
	@echo "commands:"
	@echo "install-dependencies         installs dependencies"

install-dependencies:
	python3 -m pip install -r requirements.txt
