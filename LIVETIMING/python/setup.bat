@echo off

set PYTHON_VERSION=3.11.8
set PYTHON_INSTALLER=python-%PYTHON_VERSION%-embed-win32.zip
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-win32.zip

echo Downloading 32-bit Python %PYTHON_VERSION%...
powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile %PYTHON_INSTALLER%"

echo Extracting Python...
powershell -Command "Expand-Archive -Path %PYTHON_INSTALLER% -DestinationPath SkiTiming\python"

set PYTHON_DIR=%CD%\SkiTiming\python
set PATH=%PYTHON_DIR%;%PATH%

echo Downloading LIVETIMING/python from GitHub...
if not exist SkiTiming mkdir SkiTiming
cd SkiTiming
git clone --depth 1 --filter=blob:none --sparse https://github.com/Mipppy/NYSSRA.git
cd NYSSRA
git sparse-checkout set LIVETIMING/python
cd ../..
xcopy /E /I /Y SkiTiming\NYSSRA\LIVETIMING\python SkiTiming\python
rmdir /S /Q SkiTiming\NYSSRA

echo Installing required Python modules...
echo pyqt5> SkiTiming\python\requirements.txt
echo pyqtwebengine>> SkiTiming\python\requirements.txt
echo pyserial>> SkiTiming\python\requirements.txt

%PYTHON_DIR%\python.exe -m ensurepip
%PYTHON_DIR%\python.exe -m pip install --upgrade pip
%PYTHON_DIR%\python.exe -m pip install -r SkiTiming\python\requirements.txt

echo Setup complete!
pause