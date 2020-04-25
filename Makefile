.PHONY: help install-python upgrade-pip install-dependencies

help:
	@echo ""
	@echo "commands:"
	@echo "install-python               installs python 3.8 in ~/python38 (updates PATH in .bashrc)"
	@echo "upgrade-pip                  intalls latest version of pip and setuptools"
	@echo "install-dependencies         installs dependencies"

install-python:
	mkdir ~/python38 && cd ~/python38
	wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
	tar zxfv Python-3.8.2.tgz && rm Python-3.8.2.tgz && mv Python-3.8.2 python && cd python
	./configure --prefix=~/python38 --enable-optimizations
	make && make install
	printf "\nexport PATH=~/python38/python/:$PATH" >> .bashrc
	printf "export PYTHONPATH=~/python38/python/" >> .bashrc
	source ~/.bashrc && cd ~
	echo "Python 3.8 successfully installed in ~/python38"
	echo "Python path was appended to PATH in the .bashrc file"

upgrade-pip:
	python -m pip install -U pip

install-dependencies:
	python -m pip install -r requirements.txt
