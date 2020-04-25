.PHONY: help install-python upgrade-pip install-dependencies

help:
	@echo ""
	@echo "commands:"
	@echo "install-python"              installs python 3.8 in $HOME/python38 (updates PATH in .bashrc)"
	@echo "upgrade-pip                  intalls latest version of pip and setuptools"
	@echo "install-dependencies         installs dependencies"

install-python:
	mkdir $HOME/python38 && cd $HOME/python38
	wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
	tar zxfv Python-3.8.2.tgz && rm Python-3.8.2.tgz && mv Python-3.8.2 python && cd python
	./configure --prefix=$HOME/python38 --enable-optimizations
	make && make install
	printf "\nexport PATH=$HOME/python38/python/:$PATH" >> .bashrc
	printf "export PYTHONPATH=$HOME/python38/python/" >> .bashrc
	source $HOME/.bashrc && cd $HOME
	echo "Python 3.8 successfully installed in $HOME/python38"
	echo "Python path was appended to PATH in the .bashrc file"

upgrade-pip:
	python -m pip install -U pip

install-dependencies:
	python -m pip install -r requirements.txt
