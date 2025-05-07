#!/bin/bash

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Start FastAPI server
uvicorn app.main:app --reload

# For production:
# uvicorn app.main:app --host 0.0.0.0 --port 8000