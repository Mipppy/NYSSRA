@echo off
setlocal enabledelayedexpansion
title Checking for updates...

echo Reading local version...
if not exist version.txt (
    echo 0.0 > version.txt
)
set /p local_ver=<version.txt
echo Local version: %local_ver%

echo Fetching remote version...
powershell -command "(Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Mipppy/NYSSRA/main/LIVETIMING/python/version.txt' -UseBasicParsing).Content" > remote_version.txt

set /p remote_ver=<remote_version.txt
echo Remote version: %remote_ver%

if "%local_ver%" == "%remote_ver%" (
    echo Up to date.
    del remote_version.txt
    goto start_app
)

echo New version found! Updating...

echo Downloading latest ZIP...
powershell -command "Invoke-WebRequest 'https://github.com/Mipppy/NYSSRA/archive/refs/heads/main.zip' -OutFile 'update.zip' -UseBasicParsing"

echo Extracting update...
powershell -command "Expand-Archive -Force 'update.zip' 'update_tmp'"

echo Finding extracted folder...
for /d %%D in (update_tmp\*) do set extracted=%%D

echo Copying updated program files from LIVETIMING\python...
xcopy "%extracted%\LIVETIMING\python\*" ".\" /E /Y /I >nul

echo Cleaning up...
del /f /q update.zip
del /f /q remote_version.txt
rmdir /s /q update_tmp

echo Update complete!

:start_app
echo Launching application...
start "" run.bat
exit
