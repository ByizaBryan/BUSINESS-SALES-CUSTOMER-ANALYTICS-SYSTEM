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

try:
    from app.app import app
except Exception as e:
    import traceback
    from flask import Flask, jsonify

    err_trace = traceback.format_exc()
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all_error(path):
        return jsonify({
            "error": "InsightMart Serverless Startup Failure",
            "message": str(e),
            "traceback": err_trace,
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }), 500

