"""
Standardized error handling for Flow Forecaster API.

This module provides consistent error response formats and exception handlers
to replace scattered error handling throughout the application.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
import traceback
from typing import Optional, Dict, Any
from logger import get_logger

logger = get_logger('error_handlers')


# ============================================================================
# Custom Exception Classes
# ============================================================================

class APIError(Exception):
    """Base class for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class ValidationError(APIError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code='VALIDATION_ERROR',
            details=details
        )


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = 'Authentication required'):
        super().__init__(
            message=message,
            status_code=401,
            error_code='AUTHENTICATION_ERROR'
        )


class AuthorizationError(APIError):
    """Raised when user lacks permission."""

    def __init__(self, message: str = 'Permission denied'):
        super().__init__(
            message=message,
            status_code=403,
            error_code='AUTHORIZATION_ERROR'
        )


class ResourceNotFoundError(APIError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f'{resource} with id {resource_id} not found',
            status_code=404,
            error_code='RESOURCE_NOT_FOUND',
            details={'resource': resource, 'resource_id': str(resource_id)}
        )


class ResourceConflictError(APIError):
    """Raised when a resource conflict occurs (e.g., duplicate)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code='RESOURCE_CONFLICT',
            details=details
        )


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = 'Rate limit exceeded'):
        super().__init__(
            message=message,
            status_code=429,
            error_code='RATE_LIMIT_EXCEEDED'
        )


class SimulationError(APIError):
    """Raised when simulation execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code='SIMULATION_ERROR',
            details=details
        )


# ============================================================================
# Error Response Builders
# ============================================================================

def build_error_response(
    message: str,
    status_code: int = 500,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    include_trace: bool = False
) -> tuple:
    """
    Build a standardized error response.

    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Machine-readable error code
        details: Additional error details
        include_trace: Whether to include stack trace (only in development)

    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': False,
        'error': {
            'message': message,
            'code': error_code or HTTP_STATUS_CODES.get(status_code, 'UNKNOWN_ERROR'),
            'status': status_code
        }
    }

    if details:
        response['error']['details'] = details

    if include_trace:
        response['error']['trace'] = traceback.format_exc()

    return jsonify(response), status_code


def build_success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200
) -> tuple:
    """
    Build a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code (default: 200)

    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': True,
        'data': data
    }

    if message:
        response['message'] = message

    return jsonify(response), status_code


# ============================================================================
# Flask Error Handlers
# ============================================================================

def register_error_handlers(app):
    """
    Register error handlers with Flask application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors."""
        logger.error(f"API Error: {error.message}", extra={
            'error_code': error.error_code,
            'status_code': error.status_code,
            'details': error.details
        })

        return build_error_response(
            message=error.message,
            status_code=error.status_code,
            error_code=error.error_code,
            details=error.details,
            include_trace=app.config.get('DEBUG', False)
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(f"HTTP Exception: {error.code} - {error.description}")

        return build_error_response(
            message=error.description or HTTP_STATUS_CODES.get(error.code, 'Unknown error'),
            status_code=error.code,
            error_code=f'HTTP_{error.code}'
        )

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        """Handle ValueError exceptions."""
        logger.error(f"ValueError: {str(error)}")

        return build_error_response(
            message=str(error),
            status_code=400,
            error_code='INVALID_VALUE',
            include_trace=app.config.get('DEBUG', False)
        )

    @app.errorhandler(KeyError)
    def handle_key_error(error: KeyError):
        """Handle KeyError exceptions (missing required fields)."""
        logger.error(f"KeyError: {str(error)}")

        return build_error_response(
            message=f'Missing required field: {str(error)}',
            status_code=400,
            error_code='MISSING_FIELD',
            details={'field': str(error)}
        )

    @app.errorhandler(TypeError)
    def handle_type_error(error: TypeError):
        """Handle TypeError exceptions."""
        logger.error(f"TypeError: {str(error)}")

        return build_error_response(
            message='Invalid data type provided',
            status_code=400,
            error_code='INVALID_TYPE',
            details={'error': str(error)},
            include_trace=app.config.get('DEBUG', False)
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle all unhandled exceptions."""
        logger.exception(f"Unhandled exception: {str(error)}")

        # Never expose internal error details in production
        if app.config.get('DEBUG'):
            message = str(error)
            include_trace = True
        else:
            message = 'An internal server error occurred'
            include_trace = False

        return build_error_response(
            message=message,
            status_code=500,
            error_code='INTERNAL_SERVER_ERROR',
            include_trace=include_trace
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        logger.warning(f"404 Not Found: {error}")

        return build_error_response(
            message='The requested resource was not found',
            status_code=404,
            error_code='NOT_FOUND'
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        logger.warning(f"405 Method Not Allowed: {error}")

        return build_error_response(
            message='The HTTP method is not allowed for this endpoint',
            status_code=405,
            error_code='METHOD_NOT_ALLOWED'
        )

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 errors."""
        logger.exception(f"500 Internal Server Error: {error}")

        return build_error_response(
            message='An internal server error occurred',
            status_code=500,
            error_code='INTERNAL_SERVER_ERROR',
            include_trace=app.config.get('DEBUG', False)
        )

    logger.info("Error handlers registered successfully")


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_required_fields(data: dict, required_fields: list) -> None:
    """
    Validate that required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValidationError(
            message='Missing required fields',
            details={'missing_fields': missing_fields}
        )


def validate_field_type(data: dict, field: str, expected_type: type) -> None:
    """
    Validate that a field has the expected type.

    Args:
        data: Dictionary containing the field
        field: Field name
        expected_type: Expected Python type

    Raises:
        ValidationError: If field type doesn't match
    """
    if field in data and not isinstance(data[field], expected_type):
        raise ValidationError(
            message=f'Invalid type for field "{field}"',
            details={
                'field': field,
                'expected_type': expected_type.__name__,
                'actual_type': type(data[field]).__name__
            }
        )


def validate_numeric_range(
    value: float,
    field: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> None:
    """
    Validate that a numeric value is within a specified range.

    Args:
        value: Value to validate
        field: Field name
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Raises:
        ValidationError: If value is out of range
    """
    if min_value is not None and value < min_value:
        raise ValidationError(
            message=f'Field "{field}" must be at least {min_value}',
            details={'field': field, 'min_value': min_value, 'actual_value': value}
        )

    if max_value is not None and value > max_value:
        raise ValidationError(
            message=f'Field "{field}" must be at most {max_value}',
            details={'field': field, 'max_value': max_value, 'actual_value': value}
        )
