"""
InsightMart Business Sales & Customer Analytics System
File: api/index.py
Description: Production Serverless entrypoint for Vercel deployment.
"""

import sys
import os
from pathlib import Path

# Resolve repository root directory and register exclusively on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
root_str = str(ROOT_DIR)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Ensure subfolder paths do not shadow the root package names
for sub in [str(ROOT_DIR / "app"), str(ROOT_DIR / "src")]:
    while sub in sys.path:
        sys.path.remove(sub)

# Declare serverless environment flag
os.environ["VERCEL"] = "1"

try:
    from app.app import app
except Exception as startup_err:
    import traceback
    from flask import Flask, jsonify

    err_trace = traceback.format_exc()
    err_msg = str(startup_err)
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def diagnostic_fallback(path):
        return jsonify({
            "status": "error",
            "error_type": "ServerlessInitializationError",
            "message": err_msg,
            "traceback": err_trace,
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }), 500

# Expose both app and handler for complete Vercel WSGI / ASGI compatibility
handler = app
