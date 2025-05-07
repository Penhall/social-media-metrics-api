#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment setup completed"