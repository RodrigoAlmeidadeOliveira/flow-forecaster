"""
General utility functions.

This module contains miscellaneous helper functions used across the application.
"""

import math
import numpy as np
from flask import make_response


def convert_to_native_types(obj):
    """
    Convert numpy types to native Python types for JSON serialization.

    Args:
        obj: Object to convert (can be numpy array, dict, list, etc.)

    Returns:
        Native Python types suitable for JSON serialization
    """
    if isinstance(obj, np.ndarray):
        return [convert_to_native_types(item) for item in obj.tolist()]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        value = float(obj)
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    else:
        return obj


def add_no_cache_headers(response):
    """
    Add headers to prevent caching of response.

    Args:
        response: Flask response object

    Returns:
        Response with no-cache headers added
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
