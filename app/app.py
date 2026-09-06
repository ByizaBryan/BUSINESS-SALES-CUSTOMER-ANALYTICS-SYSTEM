"""
InsightMart Business Sales & Customer Analytics System
Module: app/app.py
Description: Flask application factory configuring security headers, route blueprints,
             error handlers, and production/development server parameters.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Load environment configuration
load_dotenv(ROOT_DIR / ".env")


def create_app():
    """Application factory initializing Flask app and extensions."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "insightmart-production-secret-key-default-2026")
    app.config["JSON_SORT_KEYS"] = False

    # Register Blueprints
    from app.routes.api_routes import api_bp
    from app.routes.view_routes import view_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(view_bp)

    # Security Headers Hook
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "API endpoint not found"}), 404
        return render_template("base.html", error_title="404 - Page Not Found",
                               error_msg="The page you requested does not exist."), 404

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Internal server error occurred"}), 500
        return render_template("base.html", error_title="500 - Server Error",
                               error_msg="A backend processing error occurred. Please try again."), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"Starting InsightMart Analytics Portal on http://127.0.0.1:{port} (Debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
