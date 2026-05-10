#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Terminate script on any error
set -e

# Directory for the virtual environment
VENV_DIR="venv"

echo "Checking for virtual environment..."

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    echo "Upgrading pip..."
    pip install --upgrade pip
else
    echo "Virtual environment '$VENV_DIR' already exists."
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

echo "Verifying required dependencies (numpy, matplotlib, PyQt5)..."
pip install numpy matplotlib PyQt5

echo "Starting the Development S-Curve Simulator..."
python3 generator.py
