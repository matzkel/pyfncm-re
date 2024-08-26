Rem Windows
Rem Sadly nuitka doesn't support cross-compilation so you have to 
Rem setup virtual machine, install python 3.12 and use it to compile the app

Rem mingw64 toolchain is REQUIRED to compile the application on Windows
Rem python is REQUIRED to be added to your system's PATH environment variable
@echo off

Rem Check if ./venv exists
set DIRECTORY=venv
if not exists %DIRECTORY% (
    python -m venv venv

    Rem Check if ./requirements.txt exist and install them
    set REQUIREMENTS=requirements.txt
    if exists %REQUIREMENTS% (
        call venv\Scripts\activate.bat
        python -m pip install -r requirements.txt
    )
)

Rem Build for Windows
call venv\Scripts\activate.bat
python -m nuitka src\main.py
