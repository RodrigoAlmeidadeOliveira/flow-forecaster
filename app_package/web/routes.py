"""
Web pages routes blueprint.

This module contains routes for serving HTML pages.
"""

from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required
from logger import get_logger

logger = get_logger('web')

# Create blueprint
web_bp = Blueprint('web', __name__)


@web_bp.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "ok", "routes": len(list(current_app.url_map.iter_rules()))}


@web_bp.route('/')
@login_required
def index():
    """Render the main page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {e}")
        # Fallback if template rendering fails
        return f"""
        <html>
        <head><title>Flow Forecasting - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading template: {str(e)}</p>
            <p>Template path: {current_app.template_folder}</p>
        </body>
        </html>
        """, 500


@web_bp.route('/advanced')
@login_required
def advanced():
    """Redirect to the unified advanced forecasting section."""
    return redirect(url_for('web.index') + '#advanced-forecast')


@web_bp.route('/dependency-analysis')
@login_required
def dependency_analysis_page():
    """Render the dependency analysis page."""
    try:
        return render_template('dependency_analysis.html')
    except Exception as e:
        logger.error(f"Error rendering dependency analysis template: {e}")
        return f"""
        <html>
        <head><title>Dependency Analysis - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading dependency analysis template: {str(e)}</p>
        </body>
        </html>
        """, 500


@web_bp.route('/documentacao')
def documentation():
    """Render the user manual/documentation page."""
    try:
        return render_template('documentacao.html')
    except Exception as e:
        logger.error(f"Error rendering documentation template: {e}")
        return f"""
        <html>
        <head><title>Documentação - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading documentation template: {str(e)}</p>
        </body>
        </html>
        """, 500


@web_bp.route('/docs')
def docs_redirect():
    """Redirect /docs to /documentacao."""
    return redirect(url_for('web.documentation'))


@web_bp.route('/deadline-analysis')
def deadline_analysis_page():
    """Render the deadline analysis page."""
    try:
        return render_template('deadline_analysis.html')
    except Exception as e:
        logger.error(f"Error rendering deadline analysis template: {e}")
        return f"""
        <html>
        <head><title>Deadline Analysis - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading deadline analysis template: {str(e)}</p>
        </body>
        </html>
        """, 500


@web_bp.route('/forecast-vs-actual')
@login_required
def forecast_vs_actual_page():
    """Render the forecast vs actual analysis page."""
    try:
        return render_template('forecast_vs_actual.html')
    except Exception as e:
        logger.error(f"Error rendering forecast vs actual template: {e}")
        return f"""
        <html>
        <head><title>Forecast vs Actual - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading forecast vs actual template: {str(e)}</p>
        </body>
        </html>
        """, 500
