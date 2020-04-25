.PHONY: help install-conda install-python upgrade-pip install-dependencies

help:
	@echo ""
	@echo "commands:"
	@echo "install-conda                installs miniconda3"
	@echo "install-python               installs python 3.8 with conda"
	@echo "upgrade-pip                  upgrades pip and setuptools to latest version"
	@echo "install-dependencies         installs dependencies"

install-conda:
	@wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	@bash Miniconda3-latest-Linux-x86_64.sh
	@rm Miniconda3-latest-Linux-x86_64.sh

install-python:
	@conda install -c anaconda python=3.8

upgrade-pip:
	@python -m pip install -U pip

install-dependencies:
	@python -m pip install -r requirements.txt
