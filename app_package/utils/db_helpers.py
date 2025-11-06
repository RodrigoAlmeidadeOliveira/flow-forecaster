"""
Database helper functions for scoped queries.

This module contains utility functions for creating database queries
that are automatically scoped based on user permissions.
"""

from flask_login import current_user
from sqlalchemy import or_
from models import Project, Forecast, Actual
from .auth_helpers import current_user_is_admin


def scoped_project_query(session):
    """
    Return a Project query scoped to the current user when needed.

    Args:
        session: Database session

    Returns:
        Query: SQLAlchemy query for projects
    """
    query = session.query(Project)
    if current_user_is_admin():
        return query
    return query.filter(Project.user_id == current_user.id)


def scoped_forecast_query(session):
    """
    Return a Forecast query scoped to the current user when needed.

    Args:
        session: Database session

    Returns:
        Query: SQLAlchemy query for forecasts
    """
    query = session.query(Forecast).outerjoin(Project, Forecast.project_id == Project.id)
    if current_user_is_admin():
        return query

    user_id = getattr(current_user, 'id', None)
    user_email = getattr(current_user, 'email', None)

    filters = []
    if user_id is not None:
        filters.append(Forecast.user_id == user_id)
        filters.append(Project.user_id == user_id)

    if user_email:
        filters.append(Forecast.created_by == user_email)

    if not filters:
        # No authenticated user context; return no records
        return query.filter(Forecast.id == -1)

    return query.filter(or_(*filters))


def scoped_actual_query(session):
    """
    Return an Actual query scoped to the current user.

    Args:
        session: Database session

    Returns:
        Query: SQLAlchemy query for actuals
    """
    query = session.query(Actual)
    if current_user_is_admin():
        return query
    return query.join(Forecast).filter(Forecast.user_id == current_user.id)
