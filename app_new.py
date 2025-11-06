"""
Flow Forecaster Application - Refactored with Application Factory Pattern.

This is the new entry point for the refactored application using blueprints.
The original app.py remains untouched for backward compatibility during migration.

To use this refactored version:
- Development: python app_new.py
- Production: Update your WSGI file to import from app_new instead of app
"""

from app_package import create_app

# Create application using factory
app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
