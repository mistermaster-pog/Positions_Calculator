@echo off
cd /d "%~dp0"

:: Pełna ścieżka do Pythona
set PYTHON_PATH=C:\Users\karol\AppData\Local\Programs\Python\Python313\python.exe

:: Debugowanie: Sprawdzanie wersji Python i lokalizacji
echo Checking Python version and location...
"%PYTHON_PATH%" --version
echo Python path: %PYTHON_PATH%
pause

:: Sprawdzenie, czy Python jest zainstalowany
"%PYTHON_PATH%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

:: Sprawdzenie, czy PyInstaller jest zainstalowany
"%PYTHON_PATH%" -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing PyInstaller...
    "%PYTHON_PATH%" -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller. Please check your Python and pip installation.
        pause
        exit /b
    )
)

:: Lista wymaganych bibliotek
set "requirements=tkinter pillow pyperclip matplotlib numpy scipy perlin-noise re"

:: Sprawdzanie i instalowanie brakujących bibliotek
for %%i in (%requirements%) do (
    "%PYTHON_PATH%" -m pip show %%i >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installing missing library: %%i...
        "%PYTHON_PATH%" -m pip install %%i
        if %errorlevel% neq 0 (
            echo Failed to install %%i. Please check your Python and pip installation.
            pause
            exit /b
        )
    )
)

:: Sprawdzanie, czy folder 'release' istnieje, jeśli nie to go tworzymy
if not exist "release" (
    mkdir "release"
)

:: Uruchomienie PyInstaller z odpowiednimi opcjami
"%PYTHON_PATH%" -m PyInstaller ^
    --onefile ^
    --icon="%~dp0images\icon.ico" ^
    --noconsole ^
    --distpath "%~dp0release\dist" ^
    --workpath "%~dp0release\build" ^
    --specpath "%~dp0release\spec" ^
    editor.py

:: Powiadomienie o zakończeniu
echo Export complete. The .exe file is in the release\dist folder.
pause
