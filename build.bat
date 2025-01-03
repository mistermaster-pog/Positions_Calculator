@echo off
cd /d "%~dp0"
:: Sprawdzanie, czy folder 'release' istnieje, jeśli nie to go tworzymy
if not exist "release" (
    mkdir "release"
)

:: Uruchomienie PyInstaller z odpowiednimi opcjami
pyinstaller --onefile --icon="%~dp0images\icon.ico" --noconsole --distpath "%~dp0release\dist" --workpath "%~dp0release\build" --specpath "%~dp0release\spec" editor.py

:: Powiadomienie o zakończeniu
echo Export complete. The .exe file is in the release\dist folder.
pause