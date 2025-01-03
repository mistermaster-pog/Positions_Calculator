@echo off
cd /d "%~dp0"
pyinstaller --onefile --icon="%~dp0images\icon.ico" --noconsole --distpath "%~dp0release\dist" --workpath "%~dp0release\build" --specpath "%~dp0release\spec" editor.py
pause