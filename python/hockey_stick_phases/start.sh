#!/bin/bash

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
    
    echo "Installing required dependencies (numpy, matplotlib)..."
    pip install numpy matplotlib
else
    echo "Virtual environment '$VENV_DIR' already exists."
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

echo "Starting the Development S-Curve Simulator..."
python3 generator.py
