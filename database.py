"""
Database initialization and session management for Flow Forecaster
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
from models import Base, Project, Forecast, Actual, User

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///forecaster.db')

# Normalize legacy connection string prefix for compatibility with Fly.io/Heroku
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

is_postgresql = DATABASE_URL.startswith('postgresql://')
is_sqlite = DATABASE_URL.startswith('sqlite://')

if is_postgresql:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30,
        echo=False,
        connect_args={
            'connect_timeout': 10,
            'application_name': 'flow-forecaster',
        },
    )
    print("[DATABASE] PostgreSQL engine created with connection pooling")
    print("[DATABASE] Pool size: 20, Max overflow: 40")
elif is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        echo=False,
        connect_args={'check_same_thread': False},
    )
    print("[DATABASE] SQLite engine created (development mode)")
else:
    engine = create_engine(DATABASE_URL, echo=False)
    print(f"[DATABASE] Generic engine created for {DATABASE_URL}")

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

DB_PATH = DATABASE_URL  # Maintains backwards compatibility for existing code paths


def init_db():
    """Initialize database, create all tables."""
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DB_PATH}")


def ensure_schema():
    """Ensure existing databases include the latest columns."""
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

        if 'users' in table_names:
            existing_user_columns = {col['name'] for col in inspector.get_columns('users')}

            if is_postgresql:
                user_columns = [
                    (
                        'registration_date',
                        "ALTER TABLE users ADD COLUMN registration_date TIMESTAMP",
                        "UPDATE users SET registration_date = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE registration_date IS NULL",
                    ),
                    (
                        'access_expires_at',
                        "ALTER TABLE users ADD COLUMN access_expires_at TIMESTAMP",
                        (
                            "UPDATE users "
                            "SET access_expires_at = COALESCE(registration_date, created_at, CURRENT_TIMESTAMP) + INTERVAL '365 days' "
                            "WHERE access_expires_at IS NULL"
                        ),
                    ),
                ]
            else:
                user_columns = [
                    (
                        'registration_date',
                        "ALTER TABLE users ADD COLUMN registration_date DATETIME",
                        "UPDATE users SET registration_date = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE registration_date IS NULL",
                    ),
                    (
                        'access_expires_at',
                        "ALTER TABLE users ADD COLUMN access_expires_at DATETIME",
                        (
                            "UPDATE users "
                            "SET access_expires_at = DATETIME("
                            "COALESCE(registration_date, created_at, CURRENT_TIMESTAMP), '+365 days') "
                            "WHERE access_expires_at IS NULL"
                        ),
                    ),
                ]

            for column_name, ddl, hydration in user_columns:
                if column_name not in existing_user_columns:
                    connection.execute(text(ddl))
                    existing_user_columns.add(column_name)
                    if hydration:
                        connection.execute(text(hydration))


def get_session():
    """Get a new database session."""
    return Session()


def close_session():
    """Close the current session."""
    Session.remove()


def reset_db():
    """Drop all tables and recreate (WARNING: destroys all data)."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database reset complete")


if is_sqlite:
    db_file = DB_PATH.replace('sqlite:///', '').replace('sqlite:////', '/')
    if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        print(f"[DATABASE] Initializing new SQLite database at {db_file}")
        init_db()
    else:
        print(f"[DATABASE] Using existing SQLite database at {db_file}")

    try:
        ensure_schema()
    except Exception as exc:
        print(f"[DATABASE] SQLite schema update warning: {exc}")

elif is_postgresql:
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            print("[DATABASE] No tables found in PostgreSQL, creating initial schema")
            init_db()
        else:
            print(f"[DATABASE] Connected to PostgreSQL with {len(tables)} tables")
    except Exception as exc:
        print(f"[DATABASE] Warning: Could not inspect PostgreSQL database: {exc}")

    try:
        ensure_schema()
    except Exception as exc:
        print(f"[DATABASE] PostgreSQL schema update warning: {exc}")

else:
    print(f"[DATABASE] Initializing database at {DATABASE_URL}")
    init_db()
    try:
        ensure_schema()
    except Exception as exc:
        print(f"[DATABASE] Schema update warning for {DATABASE_URL}: {exc}")
