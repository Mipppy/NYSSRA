@echo off
setlocal enabledelayedexpansion
title Installing Timing System...

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This installer requires administrator privileges!
    echo Requesting elevation...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
    exit /b
)

echo Downloading Python 3.13 (32-bit)...
set PYTHON_URL=https://www.python.org/ftp/python/3.13.0/python-3.13.0.exe
set PYTHON_INSTALLER=python_installer.exe
powershell -Command "Invoke-WebRequest '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing"

if not exist %PYTHON_INSTALLER% (
    echo Failed to download Python!
    pause
    exit /b 1
)

echo Installing Python silently...
%PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 /log python_install.log

py -3.13-32 --version >nul 2>&1
if errorlevel 1 (
    echo Python installation failed! Check python_install.log
    pause
    exit /b 1
)
set PYTHON_CMD=py
set PYTHON_VER_ARG=-3.13-32

del /q %PYTHON_INSTALLER%


echo Creating temporary requirements.txt...
set REQ_FILE=%TEMP%\TimingSystem_requirements.txt
(
echo annotated-types==0.7.0
echo anyio==4.10.0
echo cffi==1.17.1
echo click==8.2.1
echo colorama==0.4.6
echo comtypes==1.4.11
echo et_xmlfile==2.0.0
echo fastapi==0.116.1
echo future==1.0.0
echo gevent==25.5.1
echo greenlet==3.2.3
echo h11==0.16.0
echo httptools==0.6.4
echo idna==3.10
echo iso8601==2.1.0
echo openpyxl==3.1.5
echo pycparser==2.22
echo pydantic==2.11.7
echo pydantic_core==2.33.2
echo pypiwin32==223
echo PyQt5==5.15.11
echo PyQt5-Qt5==5.15.2
echo PyQt5_sip==12.17.0
echo PyQtWebEngine==5.15.7
echo PyQtWebEngine-Qt5==5.15.2
echo pyserial==3.5
echo python-dotenv==1.1.1
echo python-multipart==0.0.20
echo pyttsx3==2.99
echo pywin32==311
echo PyYAML==6.0.2
echo qasync==0.27.1
echo serial==0.0.97
echo setuptools==80.9.0
echo sniffio==1.3.1
echo starlette==0.47.2
echo typing-inspection==0.4.1
echo typing_extensions==4.14.1
echo tzdata==2025.2
echo uvicorn==0.35.0
echo watchfiles==1.1.0
echo websocket==0.2.1
echo websocket-client==1.8.0
echo websockets==15.0.1
echo zope.event==5.1.1
echo zope.interface==7.2
) > %REQ_FILE%

echo Installing Python packages...
%PYTHON_CMD% %PYTHON_VER_ARG% -m pip install --upgrade pip
%PYTHON_CMD% %PYTHON_VER_ARG% -m pip install -r %REQ_FILE%
if errorlevel 1 (
    echo ERROR: pip install failed!
    pause
    exit /b 1
)

echo Creating program directory...
set TARGET_DIR=%USERPROFILE%\Documents\TimingSystem
mkdir "%TARGET_DIR%" 2>nul


echo Downloading Timing System application...
set ZIP_URL=https://github.com/Mipppy/NYSSRA/archive/refs/heads/main.zip
set ZIP_FILE=program.zip
powershell -Command "Invoke-WebRequest '%ZIP_URL%' -OutFile '%ZIP_FILE%'"

if not exist %ZIP_FILE% (
    echo Failed to download program ZIP!
    pause
    exit /b 1
)


echo Extracting program files...
powershell -Command "Expand-Archive -Force '%ZIP_FILE%' '%TARGET_DIR%\tmp_extract'"

for /d %%D in ("%TARGET_DIR%\tmp_extract\*") do set EXTRACTED=%%D
xcopy "%EXTRACTED%\LIVETIMING\python\*" "%TARGET_DIR%\" /E /Y /I >nul
rmdir /s /q "%TARGET_DIR%\tmp_extract"


echo Cleaning up...
del /q %ZIP_FILE%
del /q %REQ_FILE%


cd /d "%TARGET_DIR%"

echo Running Timing System...
%PYTHON_CMD% %PYTHON_VER_ARG% main.py
echo Program exited. Press any key to close...

pause >nul
exit /b 0
