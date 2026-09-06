"""
InsightMart Business Sales & Customer Analytics System
Module: app/routes/api_routes.py
Description: REST API Blueprint exposing analytical endpoints with JSON serialization,
             parameter validation, and error handling.
"""

from flask import Blueprint, request, jsonify
from app.services.analytics_service import AnalyticsService
from src.analysis import generate_automated_business_insights

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _extract_filters(req) -> dict:
    """Extracts and sanitizes query parameter filters from the request."""
    return {
        "start_date": req.args.get("start_date", "").strip() or None,
        "end_date": req.args.get("end_date", "").strip() or None,
        "store_id": req.args.get("store_id", "").strip() or None,
        "region": req.args.get("region", "").strip() or None,
        "category_id": req.args.get("category_id", "").strip() or None,
        "sales_channel": req.args.get("sales_channel", "").strip() or None,
        "payment_method": req.args.get("payment_method", "").strip() or None,
        "customer_segment": req.args.get("customer_segment", "").strip() or None
    }


@api_bp.route("/dashboard/kpis", methods=["GET"])
def get_kpis():
    """Returns top-level executive KPIs (Revenue, Profit, Orders, Units, AOV, Margin)."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_dashboard_kpis(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/dashboard/revenue-trend", methods=["GET"])
def get_revenue_trend():
    """Returns monthly progression of revenue and profit."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_revenue_trend(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/dashboard/category-performance", methods=["GET"])
def get_category_performance():
    """Returns merchandise category volume and margins."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_category_performance(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/dashboard/store-performance", methods=["GET"])
def get_store_performance():
    """Returns retail store performance benchmarks."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_store_performance(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/dashboard/sales-channels", methods=["GET"])
def get_sales_channels():
    """Returns sales channel distribution."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_sales_channel_breakdown(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/dashboard/payment-methods", methods=["GET"])
def get_payment_methods():
    """Returns payment methods breakdown."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_payment_methods_breakdown(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/products/top", methods=["GET"])
def get_top_products():
    """Returns top products ranked by revenue."""
    try:
        limit = int(request.args.get("limit", 10))
        filters = _extract_filters(request)
        data = AnalyticsService.get_top_products(limit=limit, filters=filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/products/underperforming", methods=["GET"])
def get_underperforming_products():
    """Returns underperforming products."""
    try:
        limit = int(request.args.get("limit", 10))
        filters = _extract_filters(request)
        data = AnalyticsService.get_underperforming_products(limit=limit, filters=filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/products/catalog", methods=["GET"])
def get_products_catalog():
    """Returns comprehensive product catalog matrix."""
    try:
        data = AnalyticsService.get_all_products_catalog()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/customers/segments", methods=["GET"])
def get_customer_segments():
    """Returns customer segment distribution and spend profile."""
    try:
        data = AnalyticsService.get_customer_segments()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/customers/top", methods=["GET"])
def get_top_customers():
    """Returns highest spend customers."""
    try:
        limit = int(request.args.get("limit", 15))
        data = AnalyticsService.get_top_customers(limit=limit)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/stores/performance", methods=["GET"])
def get_all_stores():
    """Returns detailed store performance ranking."""
    try:
        filters = _extract_filters(request)
        data = AnalyticsService.get_store_performance(filters)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/sales/transactions", methods=["GET"])
def get_sales_transactions():
    """Returns paginated, searchable transaction table data."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(100, int(request.args.get("per_page", 15)))
        search = request.args.get("search", "").strip()
        filters = _extract_filters(request)

        data = AnalyticsService.get_transactions_paginated(
            page=page, per_page=per_page, search=search, filters=filters
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/insights", methods=["GET"])
def get_insights():
    """Returns data-driven business insights and recommendations."""
    try:
        data = generate_automated_business_insights()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/filters/options", methods=["GET"])
def get_filter_options():
    """Returns dropdown options for filter controls."""
    try:
        data = AnalyticsService.get_filter_options()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
