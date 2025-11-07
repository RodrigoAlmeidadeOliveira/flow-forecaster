"""
Centralized configuration for Flow Forecaster application.

This module contains all application constants, default values, and configuration
settings to avoid magic numbers and hardcoded values scattered throughout the codebase.
"""

import os
from enum import Enum


# ============================================================================
# Application Configuration
# ============================================================================

class Config:
    """Base configuration class with common settings."""

    # Flask settings
    SECRET_KEY = os.environ.get('FLOW_FORECASTER_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'change-me-in-production'

    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///forecaster.db')

    # Logging settings
    LOG_LEVEL = os.environ.get('FLOW_FORECASTER_LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('FLOW_FORECASTER_LOG_FILE')

    # Celery settings
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Compression settings
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'text/javascript'
    ]
    COMPRESS_LEVEL = 6  # Balance between speed and compression (1-9)
    COMPRESS_MIN_SIZE = 500  # Only compress responses > 500 bytes


# ============================================================================
# Simulation Defaults
# ============================================================================

class SimulationDefaults:
    """Default values for Monte Carlo simulations."""

    # Number of simulation iterations
    DEFAULT_SIMULATIONS = 10000
    MIN_SIMULATIONS = 100
    MAX_SIMULATIONS = 100000

    # Team focus defaults
    DEFAULT_TEAM_FOCUS = 1.0
    MIN_TEAM_FOCUS = 0.0
    MAX_TEAM_FOCUS = 1.0

    # Backlog defaults
    DEFAULT_BACKLOG = 0
    MIN_BACKLOG = 0

    # Throughput defaults
    MIN_THROUGHPUT_SAMPLES = 3  # Minimum samples required for simulation


# ============================================================================
# Percentiles and Statistical Thresholds
# ============================================================================

class Percentiles:
    """Standard percentiles used across the application."""

    P10 = 0.10
    P15 = 0.15
    P25 = 0.25
    P50 = 0.50  # Median
    P75 = 0.75
    P85 = 0.85
    P90 = 0.90
    P95 = 0.95
    P99 = 0.99

    # Default percentiles for forecasting
    DEFAULT_LOW = P15
    DEFAULT_MEDIUM = P50
    DEFAULT_HIGH = P85
    DEFAULT_VERY_HIGH = P95


# ============================================================================
# Cost Analysis Defaults
# ============================================================================

class CostDefaults:
    """Default values for cost analysis and estimation."""

    # Cost per person-week in BRL (Brazilian Real)
    DEFAULT_COST_PER_PERSON_WEEK = 5000
    MIN_COST_PER_PERSON_WEEK = 0

    # Team size defaults
    DEFAULT_TEAM_SIZE = 5
    MIN_TEAM_SIZE = 1
    MAX_TEAM_SIZE = 100

    # PERT Beta defaults for cost estimation
    PERT_BETA_ALPHA = 4  # Shape parameter for PERT distribution
    PERT_BETA_DEFAULT_MODE_WEIGHT = 4  # Weight for mode in (min + mode*4 + max)/6


# ============================================================================
# Pagination and Limits
# ============================================================================

class PaginationDefaults:
    """Default pagination limits for API responses."""

    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    MIN_PAGE_SIZE = 1

    # Default offset
    DEFAULT_OFFSET = 0


# ============================================================================
# Project Status Enums
# ============================================================================

class ProjectStatus(str, Enum):
    """Valid project status values."""
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ON_HOLD = 'on_hold'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'


class RiskLevel(str, Enum):
    """Valid risk level values."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Priority(int, Enum):
    """Valid priority values (1=highest, 5=lowest)."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    LOWEST = 5


class StrategicImportance(str, Enum):
    """Valid strategic importance values."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


# ============================================================================
# User Roles
# ============================================================================

class UserRole(str, Enum):
    """Valid user role values."""
    USER = 'user'
    ADMIN = 'admin'
    INSTRUCTOR = 'instructor'


# Admin roles set for quick access control
ADMIN_ROLES = {'admin', 'instructor'}


# ============================================================================
# Machine Learning Defaults
# ============================================================================

class MLDefaults:
    """Default values for ML forecasting."""

    # Cross-validation defaults
    DEFAULT_CV_FOLDS = 5
    MIN_CV_FOLDS = 2
    MAX_CV_FOLDS = 10

    # Training defaults
    DEFAULT_TRAIN_TEST_SPLIT = 0.8
    MIN_SAMPLES_FOR_ML = 10  # Minimum samples required to train ML model

    # Model parameters
    DEFAULT_RANDOM_STATE = 42

    # Forecast horizon defaults
    DEFAULT_FORECAST_DAYS = 30
    MIN_FORECAST_DAYS = 1
    MAX_FORECAST_DAYS = 365


# ============================================================================
# Cost of Delay (CoD) Defaults
# ============================================================================

class CoDDefaults:
    """Default values for Cost of Delay forecasting."""

    # Required columns for CoD training data
    REQUIRED_COLUMNS = {
        'budget_millions',
        'duration_weeks',
        'team_size',
        'num_stakeholders',
        'business_value',
        'complexity',
        'cod_weekly',
    }

    # Sample data generation defaults
    DEFAULT_SAMPLE_SIZE = 100
    MIN_SAMPLE_SIZE = 10


# ============================================================================
# Validation Constants
# ============================================================================

class ValidationLimits:
    """Validation limits for input data."""

    # String lengths
    MAX_PROJECT_NAME_LENGTH = 200
    MAX_OWNER_NAME_LENGTH = 200
    MAX_STAKEHOLDER_NAME_LENGTH = 200
    MAX_TAG_LENGTH = 50
    MAX_TAGS_PER_PROJECT = 20

    # Numeric ranges
    MAX_BUSINESS_VALUE = 100
    MIN_BUSINESS_VALUE = 0

    MAX_CAPACITY_ALLOCATED = 1.0
    MIN_CAPACITY_ALLOCATED = 0.0

    # Date formats
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# ============================================================================
# Database Connection Pool Settings
# ============================================================================

class DatabasePoolSettings:
    """Database connection pool configuration."""

    # PostgreSQL pool settings
    POSTGRESQL_POOL_SIZE = 20
    POSTGRESQL_MAX_OVERFLOW = 40
    POSTGRESQL_POOL_PRE_PING = True
    POSTGRESQL_POOL_RECYCLE = 3600  # 1 hour
    POSTGRESQL_POOL_TIMEOUT = 30  # seconds
    POSTGRESQL_CONNECT_TIMEOUT = 10  # seconds

    # SQLite settings
    SQLITE_CHECK_SAME_THREAD = False


# ============================================================================
# Task Timeout Settings
# ============================================================================

class TaskTimeouts:
    """Timeout settings for async tasks."""

    # Celery task timeouts (in seconds)
    SIMULATION_TIMEOUT = 600  # 10 minutes
    ML_FORECAST_TIMEOUT = 300  # 5 minutes
    BACKTEST_TIMEOUT = 900  # 15 minutes
    DEFAULT_TASK_TIMEOUT = 300  # 5 minutes


# ============================================================================
# Dependency Analysis Defaults
# ============================================================================

class DependencyDefaults:
    """Default values for dependency analysis."""

    # Risk multipliers based on dependency status
    BLOCKED_RISK_MULTIPLIER = 2.0
    AT_RISK_MULTIPLIER = 1.5
    ON_TRACK_MULTIPLIER = 1.0

    # Default dependency delay (in days)
    DEFAULT_DELAY_DAYS = 0
    MAX_DELAY_DAYS = 365


# ============================================================================
# Visualization Defaults
# ============================================================================

class VisualizationDefaults:
    """Default values for charts and visualizations."""

    # Chart dimensions
    DEFAULT_FIGURE_WIDTH = 10
    DEFAULT_FIGURE_HEIGHT = 6

    # Chart colors
    PRIMARY_COLOR = '#1f77b4'
    SUCCESS_COLOR = '#2ca02c'
    WARNING_COLOR = '#ff7f0e'
    DANGER_COLOR = '#d62728'

    # Histogram bins
    DEFAULT_HISTOGRAM_BINS = 50


# ============================================================================
# Security Settings
# ============================================================================

class SecuritySettings:
    """Security-related configuration."""

    # Password requirements
    MIN_PASSWORD_LENGTH = 8

    # Session settings
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    }


# ============================================================================
# Rate Limiting (for future implementation)
# ============================================================================

class RateLimitDefaults:
    """Rate limiting defaults for API endpoints."""

    # Requests per minute
    DEFAULT_RATE_LIMIT = 60
    SIMULATION_RATE_LIMIT = 10  # CPU-intensive operations
    AUTH_RATE_LIMIT = 5  # Login/register attempts


# ============================================================================
# Environment-Specific Configurations
# ============================================================================

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'


# ============================================================================
# Configuration Factory
# ============================================================================

def get_config(env: str = None) -> Config:
    """
    Get configuration based on environment.

    Args:
        env: Environment name ('development', 'production', 'testing')
             If not provided, uses FLASK_ENV or defaults to 'development'

    Returns:
        Configuration class instance
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }

    return config_map.get(env.lower(), DevelopmentConfig)
