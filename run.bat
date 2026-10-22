@echo off
setlocal
cd /d "%~dp0"
py -3 main.py --interactive
if errorlevel 1 (
  python main.py --interactive
)
pause
