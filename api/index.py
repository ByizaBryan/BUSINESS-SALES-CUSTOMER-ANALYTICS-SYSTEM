"""
InsightMart Analytics System
File: api/index.py
Description: Vercel Serverless Function entrypoint for Flask.
"""

import sys
import os
from pathlib import Path

# Ensure root directory is on sys.path so app and src modules resolve
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Set Vercel serverless environment flag
os.environ["VERCEL"] = "1"

from app.app import app

# Vercel WSGI entrypoint exports 'app'
if __name__ == "__main__":
    app.run()
