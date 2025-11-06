"""
Authentication and authorization helper functions.

This module contains utility functions for user authentication, authorization,
and access control checks.
"""

from typing import Optional
from flask import request
from flask_login import current_user
from urllib.parse import urlparse, urljoin
from config import ADMIN_ROLES


def is_safe_redirect_url(target: Optional[str]) -> bool:
    """
    Ensure redirect targets stay within the same host to avoid open redirects.

    Args:
        target: URL to redirect to

    Returns:
        bool: True if the URL is safe to redirect to
    """
    if not target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https') and
        ref_url.netloc == test_url.netloc
    )


def current_user_is_admin() -> bool:
    """
    Determine if the logged-in user has elevated privileges.

    Returns:
        bool: True if user is admin or instructor
    """
    if not getattr(current_user, 'is_authenticated', False):
        return False

    role = getattr(current_user, 'role', None)
    return isinstance(role, str) and role.lower() in ADMIN_ROLES


def has_record_access(record, attr='user_id') -> bool:
    """
    Check whether the logged-in user can access the given record.

    Args:
        record: Database record to check access for
        attr: Attribute name to check against user ID (default: 'user_id')

    Returns:
        bool: True if user has access to the record
    """
    if record is None:
        return False
    if current_user_is_admin():
        return True
    return getattr(record, attr, None) == current_user.id
