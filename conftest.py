"""
Pytest configuration and shared fixtures for Flow Forecaster tests.

This module provides common test fixtures for database sessions, Flask app instances,
authenticated users, and other testing utilities.
"""

import pytest
import os
from datetime import datetime

# Set testing environment before importing app
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLOW_FORECASTER_LOG_LEVEL'] = 'ERROR'  # Reduce noise in tests

from app import app as flask_app
from database import engine, Base, get_session, Session
from models import User, Project, Forecast, Actual
from werkzeug.security import generate_password_hash


# ============================================================================
# Application Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def app():
    """
    Create Flask application for testing.

    This fixture creates the app once per test session.
    """
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'LOGIN_DISABLED': False,
    })

    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    """
    Create Flask test client.

    This fixture creates a new test client for each test function.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create Flask CLI test runner.

    This fixture creates a CLI runner for testing CLI commands.
    """
    return app.test_cli_runner()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def _db_setup():
    """
    Set up test database schema (once per session).

    This fixture creates all tables before tests run and drops them after.
    """
    # Create all tables
    Base.metadata.create_all(engine)

    yield

    # Drop all tables after tests
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def db_session(_db_setup):
    """
    Provide a database session for testing with automatic rollback.

    This fixture provides a clean database session for each test.
    All changes are rolled back after the test completes.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = get_session()

    yield session

    # Rollback changes and close
    session.close()
    Session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def clean_db(db_session):
    """
    Provide a completely clean database for testing.

    This fixture clears all data from tables before each test.
    """
    # Delete all records from tables
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

    yield db_session


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def test_user(db_session):
    """
    Create a test user.

    Returns:
        User: A test user with credentials (email: test@example.com, password: password123)
    """
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123'),
        role='user'
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def admin_user(db_session):
    """
    Create an admin test user.

    Returns:
        User: An admin user with credentials (email: admin@example.com, password: admin123)
    """
    user = User(
        username='adminuser',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Create an authenticated test client.

    This fixture logs in the test_user and returns the authenticated client.
    """
    # Login the test user
    client.post('/login', data={
        'email': test_user.email,
        'password': 'password123'
    }, follow_redirects=True)

    yield client

    # Logout after test
    client.get('/logout', follow_redirects=True)


@pytest.fixture
def admin_client(client, admin_user):
    """
    Create an authenticated admin test client.

    This fixture logs in the admin_user and returns the authenticated client.
    """
    # Login the admin user
    client.post('/login', data={
        'email': admin_user.email,
        'password': 'admin123'
    }, follow_redirects=True)

    yield client

    # Logout after test
    client.get('/logout', follow_redirects=True)


# ============================================================================
# Project Fixtures
# ============================================================================

@pytest.fixture
def test_project(db_session, test_user):
    """
    Create a test project.

    Returns:
        Project: A test project owned by test_user
    """
    project = Project(
        name='Test Project',
        description='A test project for testing',
        user_id=test_user.id,
        status='active',
        priority=3,
        business_value=50,
        risk_level='medium'
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    return project


@pytest.fixture
def test_projects(db_session, test_user):
    """
    Create multiple test projects.

    Returns:
        list[Project]: A list of 3 test projects
    """
    projects = []
    for i in range(3):
        project = Project(
            name=f'Test Project {i+1}',
            description=f'Test project number {i+1}',
            user_id=test_user.id,
            status='active',
            priority=i+1,
            business_value=50 + i*10
        )
        db_session.add(project)
        projects.append(project)

    db_session.commit()

    for project in projects:
        db_session.refresh(project)

    return projects


# ============================================================================
# Forecast Fixtures
# ============================================================================

@pytest.fixture
def test_forecast(db_session, test_user, test_project):
    """
    Create a test forecast.

    Returns:
        Forecast: A test forecast associated with test_project
    """
    forecast = Forecast(
        name='Test Forecast',
        project_id=test_project.id,
        user_id=test_user.id,
        forecast_date=datetime.now().date().isoformat(),
        p50=10,
        p85=15,
        p95=20,
        completion_date='2024-12-31',
        methodology='monte_carlo'
    )
    db_session.add(forecast)
    db_session.commit()
    db_session.refresh(forecast)

    return forecast


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_throughput_data():
    """
    Provide sample throughput data for simulations.

    Returns:
        list[float]: Sample throughput values
    """
    return [5.0, 6.0, 4.5, 7.0, 5.5, 6.5, 5.0, 6.0, 7.5, 5.5]


@pytest.fixture
def sample_simulation_data(sample_throughput_data):
    """
    Provide sample simulation request data.

    Returns:
        dict: Complete simulation request data
    """
    return {
        'projectName': 'Test Simulation',
        'numberOfSimulations': 1000,
        'tpSamples': sample_throughput_data,
        'backlog': 50,
        'deadlineDate': '2024-12-31',
        'startDate': '2024-01-01',
        'teamFocus': 1.0,
        'dependencies': []
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_monte_carlo_result():
    """
    Provide a mock Monte Carlo simulation result.

    Returns:
        dict: Mock simulation result
    """
    return {
        'p50': 10,
        'p85': 15,
        'p95': 20,
        'mean': 12.5,
        'std': 3.2,
        'completion_dates': ['2024-03-15', '2024-03-30', '2024-04-10'],
        'probabilities': [0.50, 0.85, 0.95]
    }


# ============================================================================
# Utility Functions
# ============================================================================

def create_user(session, username='user', email='user@example.com', password='password', role='user'):
    """
    Helper function to create a user.

    Args:
        session: Database session
        username: Username
        email: Email address
        password: Plain text password
        role: User role

    Returns:
        User: Created user instance
    """
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_project(session, user_id, name='Test Project', **kwargs):
    """
    Helper function to create a project.

    Args:
        session: Database session
        user_id: Owner user ID
        name: Project name
        **kwargs: Additional project fields

    Returns:
        Project: Created project instance
    """
    project = Project(
        name=name,
        user_id=user_id,
        **kwargs
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project
