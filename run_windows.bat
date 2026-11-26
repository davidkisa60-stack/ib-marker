@echo off
setlocal EnableExtensions
title IB Marker
cd /d "%~dp0"

echo ==========================================
echo   IB Marker
echo ==========================================
echo.

rem ---- 0. Is this running from an extracted folder? -------------------------
set "HERE=%~dp0"
echo "%HERE%" | findstr /i /l /c:"Temp1_" /c:".zip" /c:"Rar$" /c:"7zO" >nul
if not errorlevel 1 (
    echo It looks like this file is being opened from INSIDE a zip file:
    echo   "%HERE%"
    echo.
    echo Windows cannot run the app from inside a zip. Please:
    echo   1. Go back to the downloaded zip file, right-click it and choose "Extract All..."
    echo   2. Open the extracted ib-marker folder
    echo   3. Double-click run_windows.bat there
    echo.
    pause
    exit /b 1
)
if not exist "app\main.py" (
    echo The app files were not found next to this script.
    echo run_windows.bat must stay inside the ib-marker folder, together with the
    echo "app" folder and requirements.txt. This script is currently in:
    echo   "%HERE%"
    echo.
    pause
    exit /b 1
)

rem ---- 1. Find a Python interpreter ----------------------------------------
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY=python"
)
if not defined PY (
    echo Python was not found on this computer.
    echo.
    echo   1. Open https://www.python.org/downloads/ and download Python 3.11 or newer.
    echo   2. Run the installer. On the FIRST screen tick the box
    echo      "Add python.exe to PATH", then click "Install Now".
    echo   3. Close this window and double-click run_windows.bat again.
    echo.
    echo If a Microsoft Store window opened just now, close it and use python.org instead.
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo Found %%v

rem ---- 2. Check the version is new enough ----------------------------------
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo This Python is older than 3.10. Please install a newer version from
    echo https://www.python.org/downloads/ and run this script again.
    pause
    exit /b 1
)

rem ---- 3. Create a private environment so nothing else on the PC is touched -
if not exist ".venv\Scripts\python.exe" (
    echo Creating a private Python environment in .venv ... please wait.
    %PY% -m venv .venv
    if errorlevel 1 (
        echo Could not create the environment. Try reinstalling Python from python.org.
        pause
        exit /b 1
    )
)
set "VPY=.venv\Scripts\python.exe"

rem ---- 4. Install the packages ---------------------------------------------
echo Installing required packages (takes a minute the first time)...
"%VPY%" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo Package installation failed. Check the internet connection and try again.
    echo If you are on a school network with a proxy, ask IT to allow pypi.org.
    pause
    exit /b 1
)

rem ---- 5. Choose a free port -----------------------------------------------
set "PORT=8000"
netstat -ano 2>nul | findstr /r /c:":8000 .*LISTENING" >nul
if not errorlevel 1 (
    echo.
    echo Port 8000 is already in use on this computer, so IB Marker will use port 8010.
    echo If another copy of IB Marker is already running, it is at http://localhost:8000
    set "PORT=8010"
)

rem ---- 6. Start the server and open the browser ----------------------------
echo.
echo Starting IB Marker. Keep this window open while you use the app.
echo It will open in your browser at http://localhost:%PORT%
echo If the browser says it cannot connect, wait a few seconds and refresh the page.
echo Press Ctrl+C in this window (or just close it) to stop.
echo.
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:%PORT%'"
"%VPY%" -m uvicorn app.main:app --host 0.0.0.0 --port %PORT%
echo.
echo IB Marker has stopped. If there is an error message above, copy it and send it for help.
pause
