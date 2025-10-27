"""
Database initialization and session management for Flow Forecaster
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Project, Forecast, Actual

# Database configuration
DB_PATH = os.environ.get('DATABASE_URL', 'sqlite:///forecaster.db')
engine = create_engine(DB_PATH, echo=False)

# Session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """Initialize database, create all tables"""
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DB_PATH}")


def get_session():
    """Get a new database session"""
    return Session()


def close_session():
    """Close the current session"""
    Session.remove()


def reset_db():
    """Drop all tables and recreate (WARNING: destroys all data)"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database reset complete")


# Initialize database on import
if not os.path.exists('forecaster.db') or os.path.getsize('forecaster.db') == 0:
    init_db()
