"""
Date parsing and manipulation utilities.

This module contains helper functions for parsing and handling dates
in various formats.
"""

from datetime import datetime
from typing import Optional


def parse_flexible_date(date_str: str) -> datetime:
    """
    Parse a date string in common day-month-year formats.

    Supported formats:
    - DD/MM/YY
    - DD/MM/YYYY
    - YYYY-MM-DD
    - DD-MM-YY
    - DD-MM-YYYY
    - YYYY/MM/DD
    - DD.MM.YYYY

    Args:
        date_str: Date string to parse

    Returns:
        datetime: Parsed datetime object

    Raises:
        ValueError: If the string doesn't match supported formats
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")

    value = date_str.strip()
    if not value:
        raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")

    formats = [
        '%d/%m/%y',
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%d-%m-%y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d.%m.%Y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(f"Date {date_str} doesn't match expected day-month-year formats")
