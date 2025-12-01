#!/bin/bash
set -e

if [ -z "$VIRTUAL_ENV" ]; then
    echo "No active virtual environment detected."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "Virtual environment 'venv' created."
    fi
    source venv/bin/activate
else
    echo "Detected active virtual environment, using it."
fi
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi
python main.py
