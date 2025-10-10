# Migration Guide - Unified Monte Carlo Simulation

## Overview

This project has been successfully migrated from using separate JavaScript and Python Monte Carlo implementations to a **unified Python-only implementation** that combines the best features from:

1. **monte_carlo.js** (JavaScript) - Complete project forecasting with team dynamics
2. **monte_carlo.py** (Python) - Simple throughput forecasting
3. **Forecasting_MCS_ML_v4_full_ml.py** - Advanced Weibull-based simulation

## 🎯 Version 2.1: Weibull Unification

**IMPORTANT UPDATE (2025-10-10):** All simulation modes now use **Weibull distribution** for random throughput sampling, regardless of which mode you choose. This provides better statistical accuracy across all forecasts.

For detailed information about the Weibull unification, see **WEIBULL_UNIFICATION.md**.

## What Changed?

### ✅ New File: `monte_carlo_unified.py`

This is the new unified module that provides **THREE simulation modes**:

#### 1. **Simple Mode** (Formerly from `monte_carlo.py`)
- Single contributor
- No team dynamics
- Fast, straightforward throughput forecasting
- ✅ **Now uses Weibull distribution** for better accuracy (v2.1+)
- **Use case:** Quick estimates, simple projects

```python
from monte_carlo_unified import run_unified_simulation

result = run_unified_simulation(
    tp_samples=[5, 6, 7, 4, 8, 6, 5, 7],
    backlog=50,
    n_simulations=10000,
    mode='simple'
)
# P85: ~9 weeks
```

#### 2. **Weibull Mode** (From `Forecasting_MCS_ML_v4_full_ml.py`)
- ✅ **Alias for Simple Mode** - Both now use Weibull distribution (v2.1+)
- Single contributor with Weibull sampling
- **Use case:** Maintained for backward compatibility

```python
result = run_unified_simulation(
    tp_samples=[5, 6, 7, 4, 8, 6, 5, 7],
    backlog=50,
    n_simulations=10000,
    mode='weibull'
)
# P85: ~9 weeks (more statistically sound)
```

#### 3. **Complete Mode** (From `monte_carlo.js`)
- Full team dynamics with S-curve (ramp-up/ramp-down)
- Variable team sizes (min/max contributors)
- Lead-times, split rates, risks
- Calculates both **duration** AND **effort**
- ✅ **Now uses Weibull distribution** for throughput sampling (v2.1+)
- **Use case:** Real project forecasting with complexity

```python
result = run_unified_simulation(
    tp_samples=[5, 6, 7, 4, 8, 6, 5, 7],
    backlog=50,
    n_simulations=100000,
    mode='complete',
    team_size=10,
    min_contributors=2,
    max_contributors=5,
    s_curve_size=20,
    lt_samples=[],  # Optional
    split_rate_samples=[],  # Optional
    risks=[]  # Optional
)
# P85: ~23 weeks, 86 person-weeks
```

### 🔄 Modified Files

#### `app.py`
Updated imports to use the new unified module:

```python
# OLD
from monte_carlo import run_monte_carlo_simulation, simulate_throughput_forecast

# NEW
from monte_carlo_unified import (
    run_monte_carlo_simulation,
    simulate_throughput_forecast,
    run_unified_simulation
)
```

All existing API endpoints (`/api/simulate`, `/api/mc-throughput`, `/api/combined-forecast`) work **exactly the same** - no breaking changes!

### 🗄️ Backup Files

- `monte_carlo.js.backup` - Original JavaScript implementation
- `monte_carlo.py.backup` - Original simple Python implementation
- `monte_carlo.py` - Now a symbolic link to `monte_carlo_unified.py` for compatibility

## Why This Matters: Understanding the Two Different Results

### The Problem You Had

You were getting two different results:
1. **23 weeks** from the traditional simulation
2. **8.5 weeks** from the simplified simulation

### The Explanation

These are **NOT errors** - they're modeling different scenarios:

| Aspect | Simple/Weibull (8.5 weeks) | Complete (23 weeks) |
|--------|---------------------------|---------------------|
| **Team Model** | 10 people always working | 2-5 people (variable with S-curve) |
| **Throughput** | Full capacity always | Adjusted by active contributors |
| **Ramp-up** | None | 20% S-curve at start |
| **Ramp-down** | None | 20% S-curve at end |
| **Effort** | Not calculated | 86 person-weeks |
| **Sampling Algorithm** | ✅ Weibull distribution (v2.1+) | ✅ Weibull distribution (v2.1+) |

### Mathematical Difference

**Simple Mode:**
```
Average throughput = 6.25 tasks/week
50 tasks ÷ 6.25 = 8 weeks
```

**Complete Mode with S-curve:**
```
Week 1-4: Ramp-up (2-3 contributors) → Low throughput
Week 5-18: Full capacity (5 contributors) → 50% of max throughput
Week 19-23: Ramp-down (5-2 contributors) → Low throughput

Adjusted throughput = randomTp × (contributorsThisWeek / totalContributors)
Example: 6 tasks/week × (2/10) = 1.2 tasks/week

Result: ~23 weeks with 86 person-weeks effort
```

## When to Use Each Mode?

### Use **Simple Mode** when:
- ✅ You need quick estimates
- ✅ Team size is constant
- ✅ No ramp-up/down periods
- ✅ Simple throughput forecasting

### Use **Weibull Mode** when:
- ✅ Backward compatibility with older code
- ✅ Same as Simple mode (both use Weibull now in v2.1+)
- 💡 **Note:** In v2.1+, Simple and Weibull modes are functionally identical

### Use **Complete Mode** when:
- ✅ Real project with team dynamics
- ✅ Team ramps up at start
- ✅ Team ramps down at end
- ✅ You need effort estimates (person-weeks)
- ✅ You have risks, lead-times, or split rates
- ✅ Accurate project forecasting

## Testing

Run the integration tests to verify everything works:

```bash
cd project-forecaster-py
python test_integration.py
```

Expected output:
```
✓ SIMPLE mode: PASSED (P85: ~9 weeks)
✓ WEIBULL mode: PASSED (P85: ~9 weeks)
✓ COMPLETE mode: PASSED (P85: ~23 weeks, 86 person-weeks)
✓ ALL TESTS PASSED
```

## API Compatibility

All existing API endpoints remain **100% compatible**:

- `/api/simulate` - Uses `run_monte_carlo_simulation()` (complete mode)
- `/api/mc-throughput` - Uses `simulate_throughput_forecast()` (simple mode)
- `/api/combined-forecast` - Uses both ML and Monte Carlo

No changes needed to your frontend or API clients!

## Benefits of Unification

1. ✅ **Single source of truth** - One Python module instead of JS + Python
2. ✅ **Three simulation modes** - Choose the right tool for your needs
3. ✅ **Better maintainability** - Pure Python, no JS dependencies
4. ✅ **Enhanced features** - Weibull distribution from advanced ML module
5. ✅ **Consistent API** - Same interface for all modes
6. ✅ **Backward compatible** - All existing code works as-is
7. ✅ **Weibull everywhere (v2.1)** - All modes use same statistical foundation

## Migration Checklist

### Version 2.0 - Unification
- [x] Created `monte_carlo_unified.py` with all three modes
- [x] Updated `app.py` to import from unified module
- [x] Created symbolic link for backward compatibility
- [x] Backed up original files (`.backup` extension)
- [x] Created integration tests
- [x] Verified all three modes work correctly
- [x] Documented the differences between modes
- [x] Explained why results differ (not a bug!)

### Version 2.1 - Weibull Unification
- [x] Modified `simulate_burn_down()` to use Weibull distribution
- [x] Updated `simulate_throughput_forecast()` documentation
- [x] Unified 'simple' and 'weibull' modes to same implementation
- [x] Created `WEIBULL_UNIFICATION.md` documentation
- [x] Validated all tests pass with Weibull
- [x] Updated `MIGRATION_GUIDE.md` to reflect v2.1 changes

## Future Enhancements

Possible additions to `monte_carlo_unified.py`:

1. ~~**Hybrid mode** - Combine Weibull sampling with S-curve dynamics~~ ✅ **DONE in v2.1**
2. **Custom distributions** - Support Gamma, LogNormal, etc.
3. **Parallel execution** - Speed up large simulations with multiprocessing
4. **Caching** - Cache S-curve distributions for repeated simulations
5. **Validation** - Built-in parameter validation and warnings

## Questions?

If you have questions about:
- Which mode to use: See "When to Use Each Mode?" section
- Why results differ: See "The Explanation" section
- How to migrate code: All existing code works without changes
- Adding new features: The unified module is designed to be extensible
- Weibull unification: See `WEIBULL_UNIFICATION.md` for technical details

---

**Migration Date (v2.0):** 2025-10-10
**Weibull Unification (v2.1):** 2025-10-10
**Status:** ✅ Complete and tested
**Breaking Changes:** None - fully backward compatible
