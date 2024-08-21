Rem Before building run ./start.bat script atleast once

Rem Windows
Rem Sadly nuitka doesn't support cross-compilation so you have to 
Rem setup virtual machine, install python 3.12 and use it to compile the app

Rem mingw64 toolchain is REQUIRED to compile the application on Windows
Rem python is REQUIRED to be add to your system's PATH environment variable

Rem Build for Windows
call venv\Scripts\activate.bat
python -m nuitka src\main.py
