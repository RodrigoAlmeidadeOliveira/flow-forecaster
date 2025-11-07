# Flow Forecaster - Blueprint Refactoring Guide

## Overview

This document describes the refactoring of the monolithic `app.py` (3,504 lines) into a modular blueprint-based architecture.

## ✅ Completed (Phase 1)

### 1. **Utility Modules Created**

All helper functions have been extracted to reusable modules:

```
app_package/utils/
├── __init__.py           # Exports all utilities
├── auth_helpers.py       # Authentication/authorization helpers
├── db_helpers.py         # Database query scoping functions
├── date_helpers.py       # Date parsing utilities
└── helpers.py            # General utilities (type conversion, etc.)
```

**Functions moved:**
- `is_safe_redirect_url()` → `auth_helpers.py`
- `current_user_is_admin()` → `auth_helpers.py`
- `has_record_access()` → `auth_helpers.py`
- `scoped_project_query()` → `db_helpers.py`
- `scoped_forecast_query()` → `db_helpers.py`
- `scoped_actual_query()` → `db_helpers.py`
- `parse_flexible_date()` → `date_helpers.py`
- `convert_to_native_types()` → `helpers.py`
- `add_no_cache_headers()` → `helpers.py`

### 2. **Authentication Blueprint Created**

```
app_package/auth/
├── __init__.py           # Exports auth_bp
└── routes.py             # Authentication routes
```

**Routes (3):**
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /logout` - User logout

**Features:**
- Email validation with regex
- Password strength requirements (min 8 chars)
- First user becomes admin automatically
- Session management with remember me
- Account expiration checking
- Logging for security events

### 3. **Web Pages Blueprint Created**

```
app_package/web/
├── __init__.py           # Exports web_bp
└── routes.py             # Web page routes
```

**Routes (8):**
- `GET /` - Main dashboard (login required)
- `GET /health` - Health check endpoint
- `GET /advanced` - Advanced forecasting (redirects to /#advanced-forecast)
- `GET /dependency-analysis` - Dependency analysis page
- `GET /documentacao` - Documentation page
- `GET /docs` - Redirects to /documentacao
- `GET /deadline-analysis` - Deadline analysis page
- `GET /forecast-vs-actual` - Forecast vs actual page (login required)

**Features:**
- Error handling with fallback HTML
- Logging for template errors
- Login protection where needed

### 4. **Application Factory Pattern Implemented**

```
app_package/__init__.py   # Application factory
```

**Function:** `create_app(config_object=None)`

**Features:**
- Configurable via Config classes
- Initializes database
- Configures Flask-Compress
- Sets up Flask-Login
- Registers security headers middleware
- Registers error handlers
- Registers all blueprints
- Optional async endpoints
- Comprehensive logging

**Entry Point:** `app_new.py`

## 📊 Progress Summary

### Completed: 11 of 49 Routes (22%)

| Category | Routes | Status |
|----------|--------|--------|
| **Auth** | 3 | ✅ Complete |
| **Web Pages** | 8 | ✅ Complete |
| **API - Simulations** | 7 | 🔄 Pending |
| **API - Analysis** | 8 | 🔄 Pending |
| **API - Forecasts** | 7 | 🔄 Pending |
| **API - Actuals** | 5 | 🔄 Pending |
| **API - Backtesting** | 1 | 🔄 Pending |
| **API - Portfolio** | 4 | 🔄 Pending |
| **API - Cost of Delay** | 6 | 🔄 Pending |

### Files Created: 15

- 5 utility modules
- 2 blueprints (auth + web)
- 1 application factory
- 1 new entry point
- 6 `__init__.py` files

### Lines of Code: ~700 lines (well-organized)

Previously in monolithic `app.py`: 3,504 lines

## 🎯 Next Steps (Phase 2)

### 1. **API Simulations Blueprint**

Create `app_package/api/simulations.py` with routes:
- `POST /api/simulate` - Monte Carlo simulation
- `POST /api/ml-forecast` - ML forecasting
- `POST /api/mc-throughput` - MC throughput forecast
- `POST /api/combined-forecast` - Combined MC + ML
- `POST /api/demand/forecast` - Demand forecasting
- `POST /api/encode` - Data encoding
- `POST /api/decode` - Data decoding

### 2. **API Analysis Blueprint**

Create `app_package/api/analysis.py` with routes:
- `POST /api/deadline-analysis` - Deadline analysis
- `POST /api/forecast-how-many` - Items forecast
- `POST /api/forecast-when` - Date forecast
- `POST /api/cost-analysis` - Cost analysis
- `POST /api/dependency-analysis` - Dependency analysis
- `POST /api/visualize-dependencies` - Dependency visualization
- `POST /api/risk-summary` - Risk summary
- `POST /api/trend-analysis` - Trend analysis

### 3. **API Forecasts/Projects Blueprint**

Create `app_package/api/forecasts.py` and `app_package/api/projects.py`

### 4. **API Portfolio & CoD Blueprints**

Create remaining API blueprints

### 5. **Update wsgi.py**

Update production entry point to use `app_new.py`

### 6. **Testing**

Test all endpoints work correctly with new structure

### 7. **Deprecate app.py**

Once fully tested, rename:
- `app.py` → `app_legacy.py` (archive)
- `app_new.py` → `app.py` (new main)

## 🔧 Usage

### Development

**Option 1: Use refactored version (recommended for new development)**
```bash
python app_new.py
```

**Option 2: Use original version (for compatibility)**
```bash
python app.py
```

### Production

Update `wsgi.py`:
```python
# Old (monolithic)
from app import app

# New (refactored)
from app_new import app
```

### Testing

The refactored structure is test-friendly:

```python
from app_package import create_app
from config import TestingConfig

app = create_app(TestingConfig)
client = app.test_client()

# Test authentication
response = client.post('/register', data={...})
assert response.status_code == 200
```

## 📁 Final Structure (Target)

```
flow-forecaster/
├── app.py (legacy - to be replaced)
├── app_new.py (refactored entry point)
├── app_package/
│   ├── __init__.py (application factory)
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── web/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── simulations.py
│   │   ├── analysis.py
│   │   ├── forecasts.py
│   │   ├── projects.py
│   │   ├── actuals.py
│   │   ├── portfolio.py
│   │   └── cod.py
│   └── utils/
│       ├── __init__.py
│       ├── auth_helpers.py
│       ├── db_helpers.py
│       ├── date_helpers.py
│       └── helpers.py
├── config.py
├── logger.py
├── error_handlers.py
├── database.py
├── models.py
└── [other modules...]
```

## 🎉 Benefits

### 1. **Maintainability**
- Each blueprint is <300 lines
- Clear separation of concerns
- Easy to find and modify code

### 2. **Testability**
- Can test blueprints independently
- Application factory allows different configs
- Easier to mock dependencies

### 3. **Scalability**
- Can assign different teams to different blueprints
- Parallel development possible
- Easy to add new features

### 4. **Code Reuse**
- Utility functions in central location
- No duplicate code
- Consistent patterns across app

### 5. **Team Collaboration**
- Reduced merge conflicts
- Clear ownership of modules
- Better code organization

## 📝 Migration Checklist

- [x] Extract utility functions
- [x] Create auth blueprint
- [x] Create web blueprint
- [x] Implement application factory
- [x] Create new entry point
- [ ] Create API simulations blueprint
- [ ] Create API analysis blueprint
- [ ] Create API forecasts blueprint
- [ ] Create API projects blueprint
- [ ] Create API actuals blueprint
- [ ] Create API portfolio blueprint
- [ ] Create API CoD blueprint
- [ ] Update tests to use new structure
- [ ] Update deployment scripts
- [ ] Full integration testing
- [ ] Replace app.py with app_new.py

## 🚀 Estimated Completion

**Phase 1 (Completed):** 1 day
- Utility modules
- Auth & web blueprints
- Application factory

**Phase 2 (Remaining):** 3-4 days
- API blueprints (7 files)
- Testing and validation
- Documentation updates
- Deployment updates

**Total:** 4-5 days (as estimated)

## 📖 Related Documents

- `CRITICAL_REFACTORING_TASKS.md` - Full refactoring analysis
- `REFACTORING_CODE_EXAMPLES.md` - Code examples
- `config.py` - Configuration constants
- `logger.py` - Logging framework
- `error_handlers.py` - Error handling
