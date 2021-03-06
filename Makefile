.PHONY: help install-conda install-python upgrade-pip install-dependencies lint update

help:
	@echo ""
	@echo "commands:"
	@echo "install-conda                installs miniconda3"
	@echo "install-python               installs python 3.8 with conda"
	@echo "upgrade-pip                  upgrades pip and setuptools to latest version"
	@echo "install-dependencies         installs dependencies (including dev)"
	@echo "lint                         check code style (lint)"
	@echo "update                       installs current code with pip and restarts systemd service"

install-conda:
	@wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	@bash Miniconda3-latest-Linux-x86_64.sh
	@rm Miniconda3-latest-Linux-x86_64.sh

install-python:
	@conda install -c anaconda python=3.8

upgrade-pip:
	@python -m pip install -U pip

install-dependencies:
	@python -m pip install -r requirements.txt -r requirements-dev.txt

lint:
	@python -m pylint hpc_bot setup.py

update:
	@systemctl --user stop hpc-bot.service
	@python -m pip install . --user --upgrade
	@systemctl --user daemon-reload
	@systemctl --user start hpc-bot.service
