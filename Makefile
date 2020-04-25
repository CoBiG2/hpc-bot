.PHONY: help install-conda-python upgrade-pip install-dependencies

help:
	@echo ""
	@echo "commands:"
	@echo "install-conda-python         installs miniconda3 and python 3.8"
	@echo "upgrade-pip                  upgrades pip and setuptools to latest version"
	@echo "install-dependencies         installs dependencies"

install-conda-python:
	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash Miniconda3-latest-Linux-x86_64.sh
	rm Miniconda3-latest-Linux-x86_64.sh
	conda install -c anaconda python=3.8
	@echo "Miniconda3 and Python 3.8 successfully installed"

upgrade-pip:
	python -m pip install -U pip

install-dependencies:
	python -m pip install -r requirements.txt
