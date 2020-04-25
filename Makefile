.PHONY: help install-python upgrade-pip install-dependencies

help:
	@echo ""
	@echo "commands:"
	@echo "install-python               installs python 3.8 in ${HOME}/python38 (updates PATH in .bashrc)"
	@echo "upgrade-pip                  intalls latest version of pip and setuptools"
	@echo "install-dependencies         installs dependencies"

install-python:
	wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz -P ${HOME}/python38
	cd ${HOME}/python38 && tar zxfv Python-3.8.2.tgz && rm Python-3.8.2.tgz && mv Python-3.8.2 python
	cd ${HOME}/python38/python && ./configure --prefix=${HOME}/python38 --enable-optimizations && make && make install
	printf "\n\nexport PATH=${HOME}/python38/python/:$PATH" >> ${HOME}/.bashrc
	printf "\nexport PYTHONPATH=${HOME}/python38/python/\n" >> ${HOME}/.bashrc
	echo "Python 3.8 successfully installed in ${HOME}/python38"
	echo "Python path was appended to PATH in the .bashrc file"
	echo "Restart your environment for the new PATH to take effect"

upgrade-pip:
	python -m pip install -U pip

install-dependencies:
	python -m pip install -r requirements.txt
