"""
Utility functions package.

This package contains helper functions for authentication, database queries,
date parsing, and general utilities.
"""

from .auth_helpers import (
    is_safe_redirect_url,
    current_user_is_admin,
    has_record_access
)
from .db_helpers import (
    scoped_project_query,
    scoped_forecast_query,
    scoped_actual_query
)
from .date_helpers import parse_flexible_date
from .helpers import convert_to_native_types, add_no_cache_headers

__all__ = [
    # Auth helpers
    'is_safe_redirect_url',
    'current_user_is_admin',
    'has_record_access',
    # DB helpers
    'scoped_project_query',
    'scoped_forecast_query',
    'scoped_actual_query',
    # Date helpers
    'parse_flexible_date',
    # General helpers
    'convert_to_native_types',
    'add_no_cache_headers',
]
