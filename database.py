"""
Database initialization and session management for Flow Forecaster
"""
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Project, Forecast, Actual, User

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


def ensure_schema():
    """Ensure existing databases include the latest columns"""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if 'projects' not in table_names:
        return

    existing_project_columns = {col['name'] for col in inspector.get_columns('projects')}

    project_columns = [
        ('status', "ALTER TABLE projects ADD COLUMN status VARCHAR(50) DEFAULT 'active'", "UPDATE projects SET status = 'active' WHERE status IS NULL"),
        ('priority', "ALTER TABLE projects ADD COLUMN priority INTEGER DEFAULT 3", "UPDATE projects SET priority = 3 WHERE priority IS NULL"),
        ('business_value', "ALTER TABLE projects ADD COLUMN business_value INTEGER DEFAULT 50", "UPDATE projects SET business_value = 50 WHERE business_value IS NULL"),
        ('risk_level', "ALTER TABLE projects ADD COLUMN risk_level VARCHAR(20) DEFAULT 'medium'", "UPDATE projects SET risk_level = 'medium' WHERE risk_level IS NULL"),
        ('capacity_allocated', "ALTER TABLE projects ADD COLUMN capacity_allocated FLOAT DEFAULT 1.0", "UPDATE projects SET capacity_allocated = 1.0 WHERE capacity_allocated IS NULL"),
        ('strategic_importance', "ALTER TABLE projects ADD COLUMN strategic_importance VARCHAR(20) DEFAULT 'medium'", "UPDATE projects SET strategic_importance = 'medium' WHERE strategic_importance IS NULL"),
        ('start_date', "ALTER TABLE projects ADD COLUMN start_date VARCHAR(20)", None),
        ('target_end_date', "ALTER TABLE projects ADD COLUMN target_end_date VARCHAR(20)", None),
        ('owner', "ALTER TABLE projects ADD COLUMN owner VARCHAR(200)", None),
        ('stakeholder', "ALTER TABLE projects ADD COLUMN stakeholder VARCHAR(200)", None),
        ('tags', "ALTER TABLE projects ADD COLUMN tags TEXT", "UPDATE projects SET tags = '[]' WHERE tags IS NULL"),
        ('user_id', "ALTER TABLE projects ADD COLUMN user_id INTEGER", None),
    ]

    with engine.begin() as connection:
        for column_name, ddl, hydration in project_columns:
            if column_name not in existing_project_columns:
                connection.execute(text(ddl))
                existing_project_columns.add(column_name)
                if hydration:
                    connection.execute(text(hydration))

        if 'forecasts' in table_names:
            existing_forecast_columns = {col['name'] for col in inspector.get_columns('forecasts')}
            forecast_columns = [
                ('user_id', "ALTER TABLE forecasts ADD COLUMN user_id INTEGER", None),
            ]
            for column_name, ddl, hydration in forecast_columns:
                if column_name not in existing_forecast_columns:
                    connection.execute(text(ddl))
                    existing_forecast_columns.add(column_name)
                    if hydration:
                        connection.execute(text(hydration))


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
db_file = DB_PATH.replace('sqlite:///', '').replace('sqlite:////', '/')
if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
    # Ensure directory exists
    db_dir = os.path.dirname(db_file)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    init_db()

ensure_schema()
