#!/usr/bin/env bash

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

# Start the application
source ./venv/bin/activate
python ./src/main.py
