@echo off
cd /d "%~dp0.."
set PYTHONPATH=%CD%\src;%PYTHONPATH%
python -m agent.cli --repl
