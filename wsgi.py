"""WSGI entry point for debugging"""
from app import app

# This is the WSGI application
application = app

if __name__ == "__main__":
    app.run()
