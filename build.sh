#!/usr/bin/env bash

# Before building use ./start.sh script atleast once

# Linux
# patchelf is REQUIRED to create standalone application on linux
# ccache is OPTIONAL, but recommended for faster building speed

# Build for Linux
source ./venv/bin/activate
python -m nuitka ./src/main.py
