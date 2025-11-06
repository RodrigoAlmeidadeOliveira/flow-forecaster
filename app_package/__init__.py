"""
Flow Forecaster Application Package.

This package implements the Application Factory pattern, organizing the monolithic
app.py into modular blueprints for better maintainability and testability.

Structure:
- auth/: Authentication routes (register, login, logout)
- web/: Web page routes (index, docs, etc.)
- api/: API endpoints organized by functionality
- utils/: Shared utility functions
"""

import os
import re
from pathlib import Path
from flask import Flask
from flask_compress import Compress
from flask_login import LoginManager

from database import init_db, close_session
from models import User
from logger import get_logger, setup_logger
from error_handlers import register_error_handlers
from config import Config, ADMIN_ROLES

logger = get_logger('app_factory')


def create_app(config_object=None):
    """
    Application factory function.

    Creates and configures the Flask application with all blueprints,
    extensions, and middleware.

    Args:
        config_object: Configuration class (defaults to Config from config.py)

    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Load configuration
    if config_object is None:
        config_object = Config
    app.config.from_object(config_object)

    # Set up logging
    setup_logger(
        level=app.config.get('LOG_LEVEL', 'INFO'),
        log_file=app.config.get('LOG_FILE')
    )

    logger.info("=" * 60)
    logger.info("Creating Flask application")
    logger.info(f"App name: {app.name}")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info("=" * 60)

    # Initialize database
    init_db()

    # Configure Flask-Compress for better performance
    app.config['COMPRESS_MIMETYPES'] = config_object.COMPRESS_MIMETYPES
    app.config['COMPRESS_LEVEL'] = config_object.COMPRESS_LEVEL
    app.config['COMPRESS_MIN_SIZE'] = config_object.COMPRESS_MIN_SIZE
    Compress(app)

    # Configure Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login session management."""
        if not user_id:
            return None

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None

        from database import get_session
        session = get_session()
        try:
            user = session.get(User, user_id)
            if user:
                session.expunge(user)
            return user
        finally:
            session.close()

    # Register teardown handler
    @app.teardown_appcontext
    def remove_session(exception=None):
        """Ensure scoped sessions are properly removed at request end."""
        close_session()

    # Register security headers middleware
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        from config import SecuritySettings
        for header, value in SecuritySettings.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

    # Register context processor for templates
    @app.context_processor
    def inject_auth_context():
        """Expose auth helpers to Jinja templates."""
        from app_package.utils import current_user_is_admin
        return {
            'is_admin_user': current_user_is_admin(),
            'ADMIN_ROLES': ADMIN_ROLES
        }

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    register_blueprints(app)

    # Register async endpoints if available
    try:
        from app_async_endpoints import register_async_endpoints
        register_async_endpoints(app)
        logger.info("Async endpoints registered successfully")
    except ImportError as e:
        logger.warning(f"Celery/Async endpoints not available: {e}")
        logger.warning("Application will run in synchronous mode only")

    # Log registered routes
    logger.info("=" * 60)
    logger.info(f"Total routes registered: {len(list(app.url_map.iter_rules()))}")
    logger.debug("Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.debug(f"  {rule.endpoint:30s} {rule.rule}")
    logger.info("=" * 60)

    return app


def register_blueprints(app):
    """
    Register all application blueprints.

    Args:
        app: Flask application instance
    """
    # Auth blueprint
    from app_package.auth import auth_bp
    app.register_blueprint(auth_bp)
    logger.info("Registered auth blueprint")

    # Web blueprint
    from app_package.web import web_bp
    app.register_blueprint(web_bp)
    logger.info("Registered web blueprint")

    # API blueprints will be registered here as they're created
    # TODO: Register API blueprints once they're implemented
    # from app_package.api import simulations_bp, analysis_bp, etc.
    # app.register_blueprint(simulations_bp, url_prefix='/api')
    # app.register_blueprint(analysis_bp, url_prefix='/api')
    # ...

    logger.info("All blueprints registered successfully")
