"""
InsightMart Business Sales & Customer Analytics System
Module: app/routes/view_routes.py
Description: Web views blueprint rendering multi-page Jinja2 templates.
"""

from flask import Blueprint, render_template

view_bp = Blueprint("views", __name__)


@view_bp.route("/")
@view_bp.route("/dashboard")
def dashboard():
    """Renders Executive Dashboard page."""
    return render_template("dashboard.html", active_page="dashboard")


@view_bp.route("/sales")
def sales():
    """Renders Sales Analytics & Transactions page."""
    return render_template("sales.html", active_page="sales")


@view_bp.route("/products")
def products():
    """Renders Product & Merchandise Analytics page."""
    return render_template("products.html", active_page="products")


@view_bp.route("/customers")
def customers():
    """Renders Customer Segmentation & Loyalty page."""
    return render_template("customers.html", active_page="customers")


@view_bp.route("/stores")
def stores():
    """Renders Retail Stores & Regional Benchmarking page."""
    return render_template("stores.html", active_page="stores")


@view_bp.route("/insights")
def insights():
    """Renders Business Insights & Recommendations page."""
    return render_template("insights.html", active_page="insights")


@view_bp.route("/about")
def about():
    """Renders Information Systems Portfolio & Architecture page."""
    return render_template("about.html", active_page="about")
