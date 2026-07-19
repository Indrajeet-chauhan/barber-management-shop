# routes/reports.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from services.report_service import ReportService
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/analytics', methods=['GET'])
@login_required
def analytics():
    """Renders aggregated analytical business intelligence summaries."""
    # Run data calculation query matrix pipelines
    report_data = ReportService.generate_management_dashboard_matrix()
    return render_template('reports/analytics.html', data=report_data)