@echo off

if "%1" == "" goto help
goto %~1

:help
echo.
echo commands:
echo upgrade-pip                    upgrades pip and setuptools to latest version
echo install-dependencies           installs dependencies
goto:eof

:upgrade-pip
python -m pip install -U pip

:install-dependencies
python -m pip install -r requirements.txt
goto:eof
