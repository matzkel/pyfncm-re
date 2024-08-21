Rem Check if ./venv exists
@echo off

set DIRECTORY=venv
if not exists DIRECTORY {
    python -m venv venv

    Rem Check if ./requirements.txt exist and install them
    set REQUIREMENTS=requirements.txt
    if exists REQUIREMENTS python -m pip install -r requirements.txt
}

Rem Start the application
call venv\Scripts\activate.bat
python src\main.py
