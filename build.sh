#!/usr/bin/env bash

# Linux
# patchelf is REQUIRED to create standalone application on linux
# ccache is OPTIONAL, but recommended for faster building speed

# Check if ./venv exists
DIRECTORY="./venv"
if [ ! -d "$DIRECTORY" ]; then
    python -m venv venv

    # Check if ./requirements.txt exist and install them
    REQUIREMENTS="./requirements.txt"
    if [ -f "$REQUIREMENTS" ]; then
        source ./venv/bin/activate
        python -m pip install -r ./requirements.txt
    fi
fi

# Build for Linux
source ./venv/bin/activate
python -m nuitka ./src/main.py
