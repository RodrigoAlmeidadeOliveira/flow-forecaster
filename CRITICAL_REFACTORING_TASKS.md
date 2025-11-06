# Flow Forecaster - Critical Refactoring Tasks Report

## Executive Summary

The Flow Forecaster application is a functional Python/Flask-based project forecasting tool with Monte Carlo simulations and ML capabilities. However, it exhibits significant architectural issues that impact maintainability, scalability, and testability. This report identifies critical refactoring tasks prioritized by business impact and technical debt.

---

## CRITICAL PRIORITY (Blocks Production Scaling)

### 1. **MONOLITHIC app.py - SPLIT INTO BLUEPRINTS** ⭐⭐⭐
**File:** `/home/user/flow-forecaster/app.py` (3,504 lines, 63 functions, 49 routes)

**Issues:**
- Single file contains entire application logic (routes, business logic, database queries)
- 24 functions exceed 50 lines (largest: `api_deadline_analysis` with 485 lines)
- Violates separation of concerns
- Impossible to test individual endpoints without full app initialization
- Code navigation and maintenance is extremely difficult

**Required Actions:**
```
app/
├── __init__.py              # App factory pattern
├── auth/
│   ├── __init__.py
│   ├── routes.py            # /register, /login, /logout
│   └── auth_helpers.py      # User loading, access control
├── api/
│   ├── __init__.py
│   ├── simulations.py       # /api/simulate, /api/ml-forecast, /api/deadline-analysis
│   ├── analysis.py          # /api/cost-analysis, /api/trend-analysis, /api/accuracy-analysis
│   ├── forecasts.py         # /api/forecast-how-many, /api/forecast-when
│   ├── dependencies.py      # /api/dependency-analysis
│   └── validation.py        # Input validation schemas
├── web/
│   ├── __init__.py
│   ├── routes.py            # HTML pages
│   └── templates_handler.py # Template rendering
├── models.py                # (move from root)
├── database.py              # (move from root)
└── middleware.py            # Error handling, logging
```

**Impact:** Enables parallel development, easier testing, better scalability
**Effort:** 4-5 days

---

### 2. **NO LOGGING FRAMEWORK - REPLACE print() WITH logging** ⭐⭐⭐
**Files:** Throughout codebase

**Issues:**
- 156+ `try/except` blocks but inconsistent error logging
- Print statements used instead of proper logging (50+ instances in app.py alone)
- No log levels (DEBUG, INFO, WARNING, ERROR)
- No structured logging for debugging production issues
- Impossible to disable debug output in production
- Cannot track error patterns across different modules

**Examples:**
```python
# CURRENT (BAD):
print(f"[INFO] Received {len(simulation_data['dependencies'])} dependencies", flush=True)
print(f"[WARNING] dependency_analysis NOT in result", flush=True)

# SHOULD BE:
logger.info(f"Received {len(simulation_data['dependencies'])} dependencies")
logger.warning(f"dependency_analysis NOT in result")
```

**Required Actions:**
1. Set up logging configuration with handlers
2. Replace all `print()` statements with `logger.debug/info/warning/error`
3. Add request/response logging middleware
4. Implement structured logging for JSON logs in production

**Impact:** Operational visibility, debugging production issues
**Effort:** 3 days

---

### 3. **NO INPUT VALIDATION - ADD Pydantic OR Marshmallow** ⭐⭐⭐
**Files:** `/home/user/flow-forecaster/app.py` (49 endpoints with manual validation)

**Issues:**
- Manual validation scattered across endpoints (lines 512-530, 1062-1074, etc.)
- No centralized validation schemas
- No request/response documentation
- Manual type checking: `request.json.get('field')`
- Inconsistent error responses:
  - Some return `{'error': str(e)}`
  - Some return `{'error': error_msg, 'trace': trace_msg}`
  - Some return `{'error': str(e), 'trace': traceback.format_exc()}`
- No validation for:
  - Field types
  - Required fields
  - Value ranges
  - String length limits

**Example Issues:**
```python
# Line 509: No validation that request.json is not None
simulation_data = request.json

# Line 1015: Hardcoded default values scattered everywhere
cost_per_person_week = data.get('costPerPersonWeek', 5000)

# Different error response formats across endpoints
return jsonify({'error': str(e)}), 400  # Line 513
return jsonify({'error': 'Need throughput samples'}), 400  # Line 514
```

**Required Actions:**
1. Create Pydantic models for each endpoint:
   ```python
   class SimulationRequest(BaseModel):
       project_name: str
       number_of_simulations: int = 10000
       tp_samples: List[float]
       backlog: int
       deadline_date: str
       start_date: str
       # ... other fields
   ```
2. Use `@validate_json` decorator on endpoints
3. Standardize error responses with consistent format
4. Generate OpenAPI documentation from schemas

**Impact:** Security, reliability, API documentation
**Effort:** 3-4 days

---

### 4. **MISSING UNIT/INTEGRATION TESTS** ⭐⭐⭐
**Current State:** 17 test files but mostly integration tests, minimal unit tests

**Issues:**
- No `conftest.py` or pytest configuration
- `test_app.py` is just a stub (18 lines)
- No mocking of dependencies
- Tests import and run full simulations (slow, unreliable)
- No CI/CD test execution (only `fly-deploy.yml` exists)
- Test coverage likely < 30% for critical paths
- Database tests lack cleanup/teardown

**Test Coverage Gaps:**
- [ ] API endpoint validation tests
- [ ] Authentication/authorization tests
- [ ] Database transaction tests
- [ ] Error handling tests
- [ ] Edge cases (empty data, negative numbers, etc.)

**Required Actions:**
1. Create `conftest.py` with:
   - Flask test client fixture
   - Database session fixtures
   - User authentication fixtures
2. Create unit tests for:
   - `database.py` (session management)
   - `models.py` (to_dict() methods)
   - Validation functions
3. Create integration tests for each API endpoint
4. Set up pytest.ini with coverage thresholds
5. Add GitHub Actions workflow for test execution

**Impact:** Quality, confidence in refactoring, catch regressions
**Effort:** 5-7 days

---

## HIGH PRIORITY (Critical For Production)

### 5. **INCONSISTENT DATABASE SESSION MANAGEMENT** ⭐⭐
**Files:** `/home/user/flow-forecaster/app.py`, `/home/user/flow-forecaster/tasks/simulation_tasks.py`

**Issues:**
- Manual session management patterns:
  ```python
  # Pattern 1: Manual try/finally
  session = get_session()
  try:
      # operations
  finally:
      session.close()
  
  # Pattern 2: No cleanup (potential leaks)
  session = get_session()
  project = session.query(Project)...
  ```
- No context manager pattern
- Potential session leaks in error paths
- Inconsistent between web endpoints and async tasks

**Problematic Patterns Found:**
- Line 104-111: Manual get/close pattern in `load_user()`
- Line 317-344: Try/finally without guaranteed cleanup
- Multiple places missing `finally` blocks

**Required Actions:**
1. Create context manager:
   ```python
   @contextmanager
   def db_session():
       session = get_session()
       try:
           yield session
           session.commit()
       except Exception:
           session.rollback()
           raise
       finally:
           session.close()
   ```
2. Replace all manual session management with context manager
3. Use dependency injection for session in routes
4. Add session cleanup tests

**Impact:** Prevents database connection exhaustion, memory leaks
**Effort:** 2-3 days

---

### 6. **HARDCODED VALUES & MAGIC NUMBERS** ⭐⭐
**Files:** Throughout codebase

**Issues:**
- Hardcoded percentiles: `0.85`, `0.5`, `0.95` (scattered)
- Status constants: `'active'`, `'completed'`, `'medium'` (not enums)
- Default values scattered: `5000` (cost), `10000` (simulations), `100` (limit)
- Configuration mixed with code
- No centralized defaults

**Examples:**
- Line 1015: `cost_per_person_week = data.get('costPerPersonWeek', 5000)`
- Line 2481: `limit = request.args.get('limit', type=int, default=100)`
- Models.py line 76: `status = Column(String(50), default='active')`
- Multiple files: percentile defaults

**Required Actions:**
1. Create `config.py`:
   ```python
   class Config:
       DEFAULT_COST_PER_PERSON_WEEK = 5000  # BRL
       DEFAULT_SIMULATIONS = 10000
       DEFAULT_PAGE_LIMIT = 100
       PERCENTILE_P50 = 0.50
       PERCENTILE_P85 = 0.85
       PERCENTILE_P95 = 0.95
       
       PROJECT_STATUS = Enum('active', 'completed', 'on_hold', 'cancelled')
       RISK_LEVELS = Enum('low', 'medium', 'high', 'critical')
   ```
2. Replace hardcoded values with config constants
3. Use Enums for status/risk values instead of strings

**Impact:** Maintainability, consistency, single source of truth
**Effort:** 2 days

---

### 7. **MISSING ERROR HANDLING & WEAK RESPONSES** ⭐⭐
**Files:** `/home/user/flow-forecaster/app.py`

**Issues:**
- Inconsistent error response formats
- Some endpoints include traceback (security risk in production)
- No validation of required fields
- Generic 500 errors without context
- No rate limiting despite being a CPU-heavy simulation app

**Examples:**
- Line 732: `return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500` (exposes internals)
- Line 867: Same issue
- Line 962: Same issue
- Lines 1069-1073: Manual validation with generic errors

**Missing Validations:**
```python
# No checks for:
- null/None values that break simulations
- array/list emptiness checks
- date format validation before use
- numeric range validation
- array length validation
```

**Required Actions:**
1. Create error handler middleware:
   ```python
   @app.errorhandler(Exception)
   def handle_error(error):
       logger.exception("Unhandled exception")
       return jsonify({'error': 'Internal server error'}), 500
   ```
2. Never expose traceback in production
3. Create custom exceptions for different error types
4. Add validation decorator for all endpoints
5. Implement rate limiting on CPU-heavy endpoints

**Impact:** Security, user experience, stability
**Effort:** 2 days

---

### 8. **ARCHITECTURAL ISSUES IN ML & MONTE CARLO MODULES** ⭐⭐
**Files:** 
- `monte_carlo_unified.py` (1,474 lines)
- `ml_forecaster.py` (894 lines)
- `monte_carlo.py` (1,243 lines)

**Issues:**
- Duplicate implementations: monte_carlo.py AND monte_carlo_unified.py (both 1000+ lines)
- All logic in functions, no classes/interfaces for reuse
- Functions with 50-100+ lines of logic
- No separation between algorithms and infrastructure
- Hard to test individual simulation algorithms
- Dependency analyzer optional (try/except import) - brittle pattern

**Example Duplication:**
```python
# Both files define:
- percentile() - same implementation
- random_integer() - same implementation
- analyze_deadline() - similar logic
- forecast_how_many() - similar logic
- forecast_when() - similar logic
```

**Required Actions:**
1. Remove monte_carlo.py (consolidate into monte_carlo_unified.py)
2. Extract core simulation logic into classes:
   ```python
   class MonteCarloSimulator:
       def __init__(self, throughput_data: List[float])
       def run(self, backlog: int, num_simulations: int) -> Dict
   
   class WeibullSimulator:
       def __init__(self, throughput_data: List[float])
       def sample(self, size: int) -> np.ndarray
   ```
3. Extract ML algorithms into service classes
4. Add interfaces/abstract base classes for swappable implementations
5. Move dependency analysis to optional service

**Impact:** Reduces code duplication, improves testability, reduces maintenance
**Effort:** 4-5 days

---

## MEDIUM PRIORITY (Improves Maintainability)

### 9. **NO REPOSITORY PATTERN - DIRECT ORM ACCESS** ⭐
**Files:** `/home/user/flow-forecaster/app.py` (12 direct `.query()` calls)

**Issues:**
- Database access logic scattered in routes
- `scoped_*_query()` helpers exist but not consistently used
- Complex queries embedded in endpoints
- Impossible to swap database backends
- Duplicate query logic

**Examples of Direct Access:**
```python
# Line 2019: Direct query in route
projects = scoped_project_query(session).order_by(Project.created_at.desc()).all()

# Line 2059: Another direct query
project = scoped_project_query(session).filter(Project.id == project_id).one_or_none()
```

**Required Actions:**
1. Create repository classes:
   ```python
   class ProjectRepository:
       def get_by_id(self, project_id: int) -> Project
       def get_user_projects(self, user_id: int) -> List[Project]
       def create(self, data: ProjectCreateDTO) -> Project
       def update(self, project_id: int, data: Dict) -> Project
       def delete(self, project_id: int) -> bool
   
   class ForecastRepository:
       # Similar methods
   ```
2. Inject repositories into routes
3. Move all queries into repositories
4. Add query caching layer

**Impact:** Better separation of concerns, easier to test, swappable storage
**Effort:** 3-4 days

---

### 10. **MISSING SERVICE LAYER PATTERN** ⭐
**Files:** `/home/user/flow-forecaster/app.py`

**Issues:**
- Business logic mixed with HTTP handling
- Complex calculations in endpoints (lines 482-610 for simulate())
- Duplication of forecast-saving logic across multiple endpoints
- Impossible to reuse logic without a web request
- Hard to test business rules independently

**Required Actions:**
1. Create service classes:
   ```python
   class SimulationService:
       def run_monte_carlo(self, params: SimulationRequest) -> Dict
       def run_ml_forecast(self, params: MLForecastRequest) -> Dict
   
   class ForecastService:
       def create_forecast(self, data: Dict, user_id: int) -> Forecast
       def get_user_forecasts(self, user_id: int) -> List[Forecast]
       def delete_forecast(self, forecast_id: int, user_id: int) -> bool
   ```
2. Move business logic from routes to services
3. Inject services into route handlers
4. Keep routes thin (validation + service call + response)

**Impact:** Separation of concerns, code reuse, testability
**Effort:** 4-5 days

---

### 11. **NO API DOCUMENTATION - ADD Swagger/OpenAPI** ⭐
**Files:** `/home/user/flow-forecaster/app.py` (49 endpoints)

**Issues:**
- No API documentation for 49 endpoints
- No request/response examples
- No parameter documentation
- Hard to understand what each endpoint expects
- No auto-generated client code
- No error code documentation

**Current State:**
- Comments exist (lines 487-506) but scattered
- No machine-readable format
- No interactive API explorer

**Required Actions:**
1. Add Flask-RESTX or Flasgger
2. Document all endpoints with:
   - Request schema
   - Response schema
   - Error responses
   - Example payloads
3. Generate OpenAPI spec
4. Host Swagger UI at `/api/docs`

**Impact:** Developer experience, easier API consumption, integration
**Effort:** 2-3 days

---

### 12. **WEAK AUTHENTICATION & AUTHORIZATION** ⭐
**Files:** `/home/user/flow-forecaster/app.py`

**Issues:**
- 11 endpoints without `@login_required` protection
- Routes checked: `/`, `/advanced`, `/docs`, `/documentacao`, `/health`, etc.
- Manual authorization checks scattered (`has_record_access()` called only in some places)
- No role-based access control (RBAC) - role field exists but unused
- No API key support for integrations
- No session timeout configuration

**Unprotected Endpoints:**
```
/register, /login, /logout        # OK
/health                           # OK (for monitoring)
/                                 # NEEDS LOGIN
/advanced                         # NEEDS LOGIN
/docs, /documentacao              # NEEDS LOGIN
/deadline-analysis                # NEEDS LOGIN
```

**Missing Authorization Checks:**
- User can access other users' forecasts if they guess the ID
- Admin role field exists but never checked

**Required Actions:**
1. Add `@login_required` to all non-auth endpoints
2. Create RBAC decorator:
   ```python
   @require_role(['admin', 'instructor'])
   def restricted_endpoint():
       pass
   ```
3. Add authorization checks to all data access
4. Implement API key authentication for task workers
5. Add session timeout

**Impact:** Security, data isolation, compliance
**Effort:** 2-3 days

---

### 13. **NO MONITORING/METRICS - ADD Prometheus/OpenTelemetry** ⭐
**Files:** Monitoring infrastructure exists but not integrated

**Issues:**
- Monitoring config exists (`monitoring/prometheus.yml`, `alertmanager.yml`)
- Not integrated into application code
- No metrics for:
  - Request count/latency
  - Database query performance
  - Simulation execution time
  - Error rates
  - Worker health
- No distributed tracing
- No custom business metrics

**Current State:**
- Prometheus config exists but app doesn't export metrics
- No instrument any endpoints
- Celery health check task exists but not used

**Required Actions:**
1. Add prometheus_client
2. Instrument endpoints:
   ```python
   REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
   REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency')
   ```
3. Add database query metrics
4. Add `/metrics` endpoint
5. Create dashboards in Grafana

**Impact:** Operational visibility, performance tuning, proactive issue detection
**Effort:** 2-3 days

---

## LOWER PRIORITY (Code Quality)

### 14. **LARGE FUNCTIONS - EXTRACT HELPER METHODS** ⭐
**Files:** `/home/user/flow-forecaster/app.py`

**Issues:**
- `api_deadline_analysis()`: 485 lines
- `accuracy_analysis()`: 134 lines
- `api_trend_analysis()`: 133 lines
- `simulate()`: 131 lines
- 24 functions exceed 50 lines (should be max 30)

**Required Actions:**
1. Break large functions into smaller chunks
2. Extract calculations into helper functions
3. Create step-by-step processing functions
4. Add unit tests for extracted functions

**Impact:** Code readability, maintainability, testability
**Effort:** 3-4 days

---

### 15. **INCONSISTENT NAMING & CONVENTIONS**
**Files:** Throughout codebase

**Issues:**
- Mixed naming: `tpSamples` (camelCase) vs `tp_samples` (snake_case)
- Models use underscores, API uses camelCase
- Parameter names don't match column names
- Class methods mix naming conventions

**Examples:**
```python
# API uses camelCase
data.get('deadlineDate')
data.get('teamFocus')
simulation_data.get('numberOfSimulations')

# Python uses snake_case
deadline_date = ...
team_focus = ...
n_simulations = ...
```

**Required Actions:**
1. Standardize on snake_case for Python, camelCase for API
2. Create DTO classes with automatic conversion
3. Use Pydantic's `ConfigDict(alias_generator=to_camel)`
4. Add validation that prevents naming mismatches

**Impact:** Consistency, reduced bugs from typos
**Effort:** 2 days

---

### 16. **ENVIRONMENT CONFIGURATION ISSUES**
**Files:** `database.py`, `celery_app.py`, `app.py`

**Issues:**
- Scattered environment variable reads throughout codebase
- No centralized config management
- No validation of required env vars
- Default values mixed in code
- No config file support

**Examples:**
```python
# database.py line 11
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///forecaster.db')

# celery_app.py line 9
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# app.py line 71
app.config['SECRET_KEY'] = os.environ.get('FLOW_FORECASTER_SECRET_KEY') or ...
```

**Required Actions:**
1. Create `config.py` with Config classes:
   ```python
   class DevelopmentConfig:
       DATABASE_URL = 'sqlite:///forecaster.db'
       CELERY_BROKER_URL = 'redis://localhost:6379/0'
   
   class ProductionConfig:
       DATABASE_URL = os.environ.get('DATABASE_URL')
       CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
   ```
2. Use python-dotenv for local development
3. Validate required env vars on startup
4. Use `flask config from_object()`

**Impact:** Cleaner code, easier deployment, configuration management
**Effort:** 1 day

---

### 17. **MISSING DEPENDENCY INJECTION**
**Files:** `/home/user/flow-forecaster/app.py`

**Issues:**
- Dependencies created manually in functions
- Hard to test with mocked dependencies
- Coupling between components
- No dependency container

**Examples:**
```python
session = get_session()  # Direct dependency
visualizer = ForecastVisualizer()  # Hard-coded instantiation
forecaster = MLForecaster()  # No way to inject mock
```

**Required Actions:**
1. Use dependency_injector or similar library
2. Create application container with all dependencies
3. Inject services into route handlers
4. Use context variables for request-scoped dependencies

**Impact:** Testability, flexibility, loose coupling
**Effort:** 2-3 days

---

### 18. **SECURITY - POTENTIAL VULNERABILITIES**
**Files:** `/home/user/flow-forecaster/app.py`

**Issues:**
1. **XSS Risk**: User input in JSON responses not escaped
2. **Information Disclosure**: Traceback exposed in responses (lines 732, 867, 962)
3. **CSRF**: No CSRF tokens in forms (not critical for API-first, but forms exist)
4. **SQL Injection**: Using SQLAlchemy correctly, but raw SQL uses text() (safe)
5. **Missing Security Headers**: No HSTS, X-Frame-Options, etc.
6. **Data Validation**: User input not validated before use in simulations

**Required Actions:**
1. Add security headers middleware:
   ```python
   app.after_request
   response.headers['X-Content-Type-Options'] = 'nosniff'
   response.headers['X-Frame-Options'] = 'DENY'
   response.headers['Strict-Transport-Security'] = 'max-age=31536000'
   ```
2. Never expose tracebacks in production
3. Validate all user input
4. Add CSRF tokens to forms
5. Run security scan with bandit

**Impact:** Security, compliance, data protection
**Effort:** 1-2 days

---

### 19. **DATABASE MIGRATIONS - USE Alembic**
**Files:** `/home/user/flow-forecaster/database.py`

**Issues:**
- Using `create_all()` instead of migrations
- `ensure_schema()` function is brittle (manual ALTER TABLE)
- No version control for schema changes
- Can't rollback changes
- Hard to manage multiple environments

**Current Approach:**
```python
# Line 57: Just creates tables
Base.metadata.create_all(engine)

# Lines 61-153: Manual schema updates with raw SQL
```

**Required Actions:**
1. Set up Alembic:
   ```bash
   alembic init migrations
   ```
2. Create initial migration from current schema
3. Use `alembic upgrade` instead of `create_all()`
4. Version all schema changes
5. Document migration strategy

**Impact:** Schema management, rollback capability, version control
**Effort:** 2-3 days

---

### 20. **PERFORMANCE OPTIMIZATIONS**
**Files:** Various

**Issues:**
- N+1 queries in some endpoints
- No query result caching
- No pagination optimization (no limit/offset guidance)
- Simulations run synchronously in some paths
- No async I/O for external requests

**Examples:**
- `api_deadline_analysis()` runs full simulation on each request
- No memoization for repeated calculations
- Loading all user data instead of paginating

**Required Actions:**
1. Add query result caching (Redis)
2. Use `select(Project).where(...).limit(100).offset(0)`
3. Add query performance monitoring
4. Consider async processing for CPU-heavy tasks
5. Add result streaming for large simulations

**Impact:** Performance, scalability, reduced load
**Effort:** 3-4 days

---

## SUMMARY TABLE

| Priority | Task | Effort | Impact | Files |
|----------|------|--------|--------|-------|
| **CRITICAL** | Split app.py into blueprints | 4-5d | Scalability, testability | app.py |
| **CRITICAL** | Add logging framework | 3d | Debugging, operations | All |
| **CRITICAL** | Add input validation (Pydantic) | 3-4d | Security, reliability | app.py |
| **CRITICAL** | Add unit/integration tests | 5-7d | Quality, confidence | All test files |
| **HIGH** | Fix session management | 2-3d | Stability, memory leaks | app.py, tasks/ |
| **HIGH** | Extract hardcoded values | 2d | Maintainability | All |
| **HIGH** | Improve error handling | 2d | Security, UX | app.py |
| **HIGH** | Refactor ML/MC modules | 4-5d | Maintainability | monte_carlo*, ml_* |
| **HIGH** | Add Repository pattern | 3-4d | Testability | app.py |
| **HIGH** | Add Service layer | 4-5d | Reusability | app.py |
| **MED** | Add API documentation | 2-3d | Developer experience | app.py |
| **MED** | Fix auth/authorization | 2-3d | Security | app.py |
| **MED** | Add monitoring/metrics | 2-3d | Operations | app.py |
| **LOW** | Extract large functions | 3-4d | Readability | app.py |
| **LOW** | Standardize naming | 2d | Consistency | All |
| **LOW** | Centralize config | 1d | Cleanliness | config files |
| **LOW** | Add dependency injection | 2-3d | Testability | app.py |
| **LOW** | Security hardening | 1-2d | Security | app.py |
| **LOW** | Setup Alembic migrations | 2-3d | Schema management | database.py |
| **LOW** | Performance optimizations | 3-4d | Performance | Various |

**Total Estimated Effort:** 60-75 days for full refactoring
**Recommended Approach:** Phase refactoring, start with CRITICAL items

---

## PHASED REFACTORING ROADMAP

### Phase 1 (Weeks 1-2): Foundation
- Split app.py (4-5d)
- Add logging (3d)
- Add tests infrastructure (2d)

### Phase 2 (Weeks 3-4): Architecture
- Add validation (3-4d)
- Add service layer (4-5d)
- Fix session management (2-3d)

### Phase 3 (Weeks 5-6): Integration
- Add repositories (3-4d)
- Refactor MC/ML modules (4-5d)
- Add API documentation (2-3d)

### Phase 4 (Weeks 7-8): Production Readiness
- Auth/authorization hardening (2-3d)
- Security improvements (1-2d)
- Add monitoring (2-3d)
- Performance optimization (3-4d)

---

## QUICK WINS (Can Do Immediately)

1. **Add logging** - 3 days - High impact, starts debugging immediately
2. **Hardcoded values to config** - 2 days - Easy, improves maintainability
3. **Input validation decorator** - 3 days - Security improvement
4. **Test setup** - 1-2 days - Foundation for other work
5. **Security headers middleware** - Few hours - Easy security win

