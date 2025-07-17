#!/bin/bash
# SmartHQ Add-on Run Script
set -e
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default settings."
    echo "Copy .env.template to .env and configure your settings."
fi
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application..."
python main.py
