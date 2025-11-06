# Critical Refactoring - Code Examples

This document provides before/after code examples for the most critical refactoring tasks.

---

## 1. LOGGING - Replace print() with logging

### Before (Current - app.py lines 543-554)
```python
print(f"[INFO] Received {len(simulation_data['dependencies'])} dependencies", flush=True)
if simulation_data['dependencies']:
    print(f"[INFO] First dependency: {simulation_data['dependencies'][0]}", flush=True)

if 'dependency_analysis' in result:
    print(f"[INFO] dependency_analysis is in result with {result['dependency_analysis']['total_dependencies']} deps", flush=True)
else:
    print(f"[WARNING] dependency_analysis NOT in result. Result keys: {list(result.keys())}", flush=True)
```

### After (Recommended)
```python
# In a new logging_config.py:
import logging
import sys

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# In app.py or any module:
logger.info(f"Received {len(simulation_data['dependencies'])} dependencies")
if simulation_data['dependencies']:
    logger.debug(f"First dependency: {simulation_data['dependencies'][0]}")

if 'dependency_analysis' in result:
    logger.info(f"dependency_analysis with {result['dependency_analysis']['total_dependencies']} deps")
else:
    logger.warning(f"dependency_analysis NOT in result. Result keys: {list(result.keys())}")
```

---

## 2. INPUT VALIDATION - Add Pydantic schemas

### Before (Current - app.py lines 508-530)
```python
@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    try:
        simulation_data = request.json

        # Validation
        if not simulation_data.get('tpSamples') or not any(n >= 1 for n in simulation_data['tpSamples']):
            return jsonify({
                'error': 'Must have at least one weekly throughput sample greater than zero'
            }), 400

        split_rate_samples = simulation_data.get('splitRateSamples', [])
        if split_rate_samples and any(n > 10 or n < 0.2 for n in split_rate_samples):
            return jsonify({
                'error': 'Your split rates don\'t seem correct. For a 10% split rate, you should put \'1.1\'.'
            }), 400

        # Set defaults for optional fields
        simulation_data['minContributors'] = (simulation_data.get('minContributors') or
                                             simulation_data['totalContributors'])
```

### After (Recommended)
```python
# In app/api/validation.py:
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class SimulationRequest(BaseModel):
    """Validation schema for /api/simulate endpoint."""
    project_name: str = Field(..., min_length=1, max_length=200)
    number_of_simulations: int = Field(default=10000, ge=100, le=100000)
    tp_samples: List[float] = Field(..., min_items=1)
    lt_samples: Optional[List[float]] = Field(default=None)
    split_rate_samples: Optional[List[float]] = Field(default=None)
    backlog: int = Field(default=0, ge=0)
    number_of_tasks: int = Field(..., gt=0)
    total_contributors: int = Field(default=1, ge=1)
    min_contributors: Optional[int] = None
    max_contributors: Optional[int] = None
    s_curve_size: int = Field(default=0, ge=0)
    risks: Optional[List[dict]] = Field(default=None)
    team_focus: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)

    @validator('tp_samples')
    def validate_tp_samples(cls, v):
        if not any(n >= 1 for n in v):
            raise ValueError('Must have at least one weekly throughput sample >= 1')
        return v

    @validator('split_rate_samples')
    def validate_split_rates(cls, v):
        if v and any(n > 10 or n < 0.2 for n in v):
            raise ValueError('Split rates should be between 0.2 and 10')
        return v

    @validator('min_contributors', 'max_contributors', always=True)
    def validate_contributors(cls, v, values):
        if v is None and 'total_contributors' in values:
            return values['total_contributors']
        return v

    class Config:
        schema_extra = {
            "example": {
                "project_name": "My Project",
                "number_of_simulations": 10000,
                "tp_samples": [5, 6, 7, 5, 6],
                "backlog": 50,
                "number_of_tasks": 50,
                "total_contributors": 3,
            }
        }

# In app/api/simulations.py:
from flask import request, jsonify
from app.api.validation import SimulationRequest

@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    try:
        # Automatic validation and parsing
        data = SimulationRequest(**request.json)
        
        # Now data is guaranteed to be valid
        simulation_data = data.dict()
        
        result = run_monte_carlo_simulation(simulation_data)
        return jsonify(result)
        
    except ValidationError as e:
        return jsonify({
            'error': 'Invalid request',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.exception("Error in simulate endpoint")
        return jsonify({'error': 'Internal server error'}), 500
```

---

## 3. DATABASE SESSIONS - Add context manager

### Before (Current - multiple patterns)
```python
# Pattern 1: app.py lines 104-111
session = get_session()
try:
    user = session.get(User, user_id)
except (TypeError, ValueError):
    return None
finally:
    session.close()

# Pattern 2: app.py lines 317-344
session = None
try:
    session = get_session()
    # ... operations ...
finally:
    if session:
        session.close()
```

### After (Recommended)
```python
# In database.py:
from contextlib import contextmanager
from typing import Generator

@contextmanager
def db_session() -> Generator:
    """
    Context manager for database sessions.
    Handles commit/rollback automatically.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage in app.py:
from database import db_session

def load_user(user_id):
    """Load user for Flask-Login session management."""
    if not user_id:
        return None
    
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    
    with db_session() as session:
        user = session.get(User, user_id)
        if user:
            session.expunge(user)  # Detach from session
        return user

# In route handlers:
@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    """Fetch all projects for current user."""
    with db_session() as session:
        projects = scoped_project_query(session).order_by(Project.created_at.desc()).all()
        return jsonify([p.to_dict() for p in projects])
```

---

## 4. SERVICE LAYER - Separate business logic from routes

### Before (Current - app.py lines 482-610)
```python
@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    """Execute Monte Carlo simulation (131 lines of business logic)"""
    try:
        simulation_data = request.json
        
        # Validation mixed with logic
        if not simulation_data.get('tpSamples'):
            return jsonify({'error': '...'}), 400
        
        # Business logic in route
        result = run_monte_carlo_simulation(simulation_data)
        
        # Saving logic in route
        if save_to_db:
            session = get_session()
            try:
                forecast = Forecast(...)
                session.add(forecast)
                session.commit()
            finally:
                session.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### After (Recommended)
```python
# In services/simulation_service.py:
from app.api.validation import SimulationRequest
from monte_carlo_unified import run_monte_carlo_simulation
from database import db_session

class SimulationService:
    """Service for running simulations."""
    
    def run_monte_carlo(self, 
                       params: SimulationRequest,
                       user_id: int,
                       save_forecast: bool = False) -> dict:
        """
        Run Monte Carlo simulation.
        
        Args:
            params: Validated simulation parameters
            user_id: ID of user running simulation
            save_forecast: Whether to save results to database
            
        Returns:
            Dictionary with simulation results
        """
        logger.info(f"Running MC simulation for user {user_id}: {params.project_name}")
        
        try:
            # Run simulation
            simulation_data = params.dict()
            result = run_monte_carlo_simulation(simulation_data)
            
            # Optionally save to database
            if save_forecast:
                forecast_id = self._save_forecast(params, result, user_id)
                result['forecast_id'] = forecast_id
                logger.info(f"Forecast saved with ID: {forecast_id}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in MC simulation for user {user_id}")
            raise
    
    def _save_forecast(self, params, result, user_id) -> int:
        """Save forecast results to database."""
        with db_session() as session:
            project = session.query(Project).filter(
                Project.id == params.project_id,
                Project.user_id == user_id
            ).one_or_none()
            
            if not project:
                project = Project(
                    name=params.project_name,
                    user_id=user_id,
                    team_size=params.total_contributors
                )
                session.add(project)
                session.flush()
            
            forecast = Forecast(
                project_id=project.id,
                user_id=user_id,
                name=f"Monte Carlo - {params.project_name}",
                forecast_type='monte_carlo',
                forecast_data=json.dumps(result),
                input_data=json.dumps(params.dict()),
                backlog=params.number_of_tasks
            )
            session.add(forecast)
            session.commit()
            
            return forecast.id

# In app/api/simulations.py:
from services.simulation_service import SimulationService
from app.api.validation import SimulationRequest

simulation_service = SimulationService()

@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    """Execute Monte Carlo simulation."""
    try:
        # Validate input
        params = SimulationRequest(**request.json)
        
        # Call service (thin route handler)
        result = simulation_service.run_monte_carlo(
            params=params,
            user_id=current_user.id,
            save_forecast=request.json.get('save_forecast', False)
        )
        
        return jsonify(result), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Invalid request', 'details': e.errors()}), 400
    except Exception as e:
        logger.exception("Error in simulate endpoint")
        return jsonify({'error': 'Internal server error'}), 500
```

---

## 5. REPOSITORY PATTERN - Centralize data access

### Before (Current - app.py, direct queries)
```python
# Line 2019:
projects = scoped_project_query(session).order_by(Project.created_at.desc()).all()

# Line 2059:
project = scoped_project_query(session).filter(Project.id == project_id).one_or_none()

# Line 2121:
query = scoped_forecast_query(session).order_by(Forecast.created_at.desc())
```

### After (Recommended)
```python
# In repositories/project_repository.py:
from sqlalchemy.orm import Session
from models import Project
from typing import List, Optional

class ProjectRepository:
    """Repository for Project entity."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return self.session.query(Project).filter(Project.id == project_id).one_or_none()
    
    def get_user_projects(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Project]:
        """Get all projects for a user."""
        return self.session.query(Project).filter(
            Project.user_id == user_id
        ).order_by(
            Project.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    def create(self, user_id: int, name: str, description: str = None) -> Project:
        """Create a new project."""
        project = Project(
            user_id=user_id,
            name=name,
            description=description
        )
        self.session.add(project)
        self.session.flush()
        return project
    
    def update(self, project_id: int, data: dict) -> Optional[Project]:
        """Update project."""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        self.session.flush()
        return project
    
    def delete(self, project_id: int) -> bool:
        """Delete project."""
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        self.session.delete(project)
        self.session.flush()
        return True

# In repositories/__init__.py:
from repositories.project_repository import ProjectRepository
from repositories.forecast_repository import ForecastRepository

# Usage in services or routes:
@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    """Get user's projects."""
    with db_session() as session:
        repo = ProjectRepository(session)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        projects = repo.get_user_projects(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        return jsonify([p.to_dict() for p in projects])
```

---

## 6. CONFIGURATION - Centralize hardcoded values

### Before (Current - scattered throughout code)
```python
# app.py line 1015
cost_per_person_week = data.get('costPerPersonWeek', 5000)

# app.py line 2481
limit = request.args.get('limit', type=int, default=100)

# models.py line 76
status = Column(String(50), default='active')

# Multiple percentile usages
percentile_p85 = 0.85
percentile_p50 = 0.50
percentile_p95 = 0.95
```

### After (Recommended)
```python
# In config/constants.py:
from enum import Enum
from typing import Final

# Financial constants
DEFAULT_COST_PER_PERSON_WEEK: Final[float] = 5000.0  # BRL
MIN_COST_PER_PERSON_WEEK: Final[float] = 100.0
MAX_COST_PER_PERSON_WEEK: Final[float] = 50000.0

# Pagination
DEFAULT_PAGE_SIZE: Final[int] = 100
MAX_PAGE_SIZE: Final[int] = 1000
MIN_PAGE_SIZE: Final[int] = 1

# Simulation defaults
DEFAULT_SIMULATIONS: Final[int] = 10000
MIN_SIMULATIONS: Final[int] = 100
MAX_SIMULATIONS: Final[int] = 100000

# Percentiles
class Percentiles(Enum):
    """Common percentile thresholds."""
    P50 = 0.50
    P85 = 0.85
    P95 = 0.95
    P99 = 0.99

# Status enums
class ProjectStatus(str, Enum):
    """Project status values."""
    ACTIVE = 'active'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class RiskLevel(str, Enum):
    """Risk level values."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class UserRole(str, Enum):
    """User role values."""
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'

# Usage in code:
from config.constants import (
    DEFAULT_COST_PER_PERSON_WEEK,
    DEFAULT_PAGE_SIZE,
    ProjectStatus,
    Percentiles
)

# In routes:
@app.route('/api/projects', methods=['GET'])
def get_projects():
    limit = request.args.get('limit', DEFAULT_PAGE_SIZE, type=int)
    
# In models:
class Project(Base):
    status = Column(String(20), default=ProjectStatus.ACTIVE.value)
    
# In code:
if project.status == ProjectStatus.ACTIVE.value:
    # Process active project
```

---

## 7. ERROR HANDLING - Standardize error responses

### Before (Current - inconsistent responses)
```python
# Line 513
return jsonify({'error': str(e)}), 400

# Line 732
return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

# Line 1444
return jsonify({'error': error_msg, 'trace': trace_msg, 'error_type': 'ValueError'}), 400
```

### After (Recommended)
```python
# In app/middleware.py:
from flask import jsonify
from pydantic import ValidationError
from typing import Tuple, Dict, Any

class APIError(Exception):
    """Base API error."""
    def __init__(self, message: str, status_code: int = 400, details: Dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(APIError):
    """Validation error (400)."""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message, 400, details)

class NotFoundError(APIError):
    """Resource not found (404)."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class UnauthorizedError(APIError):
    """Unauthorized access (401)."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)

def format_error_response(error: APIError) -> Tuple[Dict[str, Any], int]:
    """Format error response consistently."""
    response = {
        'error': error.message,
        'status_code': error.status_code
    }
    if error.details:
        response['details'] = error.details
    return response, error.status_code

def register_error_handlers(app):
    """Register error handlers for the app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return format_error_response(error)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning(f"Validation error: {error.message}")
        return format_error_response(error)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return format_error_response(NotFoundError("Endpoint not found")), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        logger.exception("Unhandled server error")
        return format_error_response(
            APIError("Internal server error", 500)
        ), 500

# Usage in routes:
@app.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    try:
        with db_session() as session:
            repo = ProjectRepository(session)
            project = repo.get_by_id(project_id)
            
            if not project:
                raise NotFoundError(f"Project {project_id} not found")
            
            # Authorization check
            if project.user_id != current_user.id and not current_user_is_admin():
                raise UnauthorizedError("Cannot access this project")
            
            return jsonify(project.to_dict())
    
    except APIError:
        raise  # Re-raise API errors
    except Exception as e:
        logger.exception(f"Error fetching project {project_id}")
        raise APIError("Internal server error", 500)
```

---

## 8. FLASK BLUEPRINTS - Split app.py structure

### Before (Current)
```
app.py (3,504 lines with all routes and logic)
```

### After (Recommended)
```python
# In app/__init__.py:
from flask import Flask
from flask_login import LoginManager
from flask_compress import Compress
from database import init_db

def create_app(config_name='development'):
    """Application factory."""
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'production':
        from config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Extensions
    init_db()
    Compress(app)
    
    # Login manager
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.auth.auth_helpers import load_user_from_db
        return load_user_from_db(user_id)
    
    # Blueprints
    from app.auth.routes import auth_bp
    from app.api.simulations import simulations_bp
    from app.api.analysis import analysis_bp
    from app.web.routes import web_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(simulations_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    # Error handlers
    from app.middleware import register_error_handlers
    register_error_handlers(app)
    
    return app

# In app/auth/routes.py:
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # ... registration logic ...
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # ... login logic ...
    pass

@auth_bp.route('/logout')
@login_required
def logout():
    # ... logout logic ...
    pass

# In app/api/simulations.py:
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.simulation_service import SimulationService
from app.api.validation import SimulationRequest

simulations_bp = Blueprint('simulations', __name__)
simulation_service = SimulationService()

@simulations_bp.route('/simulate', methods=['POST'])
@login_required
def simulate():
    try:
        params = SimulationRequest(**request.json)
        result = simulation_service.run_monte_carlo(params, current_user.id)
        return jsonify(result)
    except ValidationError as e:
        return jsonify({'error': 'Invalid request', 'details': e.errors()}), 400

# In app/web/routes.py:
from flask import Blueprint, render_template
from flask_login import login_required

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@login_required
def index():
    return render_template('index.html')

# In wsgi.py or run.py:
from app import create_app

app = create_app(config_name='production')

if __name__ == '__main__':
    app.run(debug=False)
```

---

These examples show the recommended patterns for refactoring. Each can be implemented incrementally without breaking existing functionality if proper testing is in place first.

