@echo off

if "%1" == "" goto help
goto %~1

:help
echo.
echo commands:
echo install-dependencies           installs dependencies
goto:eof

:install-dependencies
python -m pip install -r requirements.txt
goto:eof
