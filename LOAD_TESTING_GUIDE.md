# Flow Forecaster - Load Testing Guide

Comprehensive guide for load testing the Flow Forecaster application with Locust.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Test Scenarios](#test-scenarios)
- [Running Tests](#running-tests)
- [Analyzing Results](#analyzing-results)
- [Performance Baselines](#performance-baselines)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

Load testing validates that the Flow Forecaster application can handle expected production traffic and identifies performance bottlenecks. This guide uses **Locust**, a modern load testing framework that allows you to write test scenarios in Python.

### What We Test

1. **Asynchronous Endpoints** - Celery-based background job processing
2. **Synchronous Endpoints** - Traditional request-response patterns
3. **Mixed Workloads** - Realistic combination of reads and writes
4. **System Limits** - Maximum capacity before degradation

### Key Metrics

- **Response Time** - How long requests take (p50, p95, p99)
- **Throughput** - Requests per second (RPS)
- **Error Rate** - Percentage of failed requests
- **Concurrent Users** - Number of simultaneous users supported
- **Resource Utilization** - CPU, memory, disk usage during load

## Prerequisites

### System Requirements

- Python 3.8+
- At least 4GB RAM available
- Running Flow Forecaster application
- Running Redis and Celery workers
- Optional: Running PostgreSQL (for production testing)

### Application Setup

**Before running load tests, ensure your application is running:**

```bash
# Option 1: Docker Compose (recommended)
docker-compose up -d

# Option 2: Local development
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery workers
celery -A celery_app worker --loglevel=info --concurrency=4

# Terminal 3: Start Flask app
python app.py
# or
gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4
```

**Verify services are running:**

```bash
# Check Flask app
curl http://localhost:8000/

# Check async endpoints
curl http://localhost:8000/api/async/health

# Check Celery
celery -A celery_app inspect active
```

## Installation

### Install Load Testing Dependencies

```bash
# Install Locust and dependencies
pip install -r requirements-loadtest.txt

# Verify installation
locust --version
```

### Make Script Executable

```bash
chmod +x run_load_tests.sh
```

## Test Scenarios

The load testing suite includes multiple predefined scenarios:

### 1. Smoke Test

**Purpose**: Quick validation that the application works under minimal load

**Configuration**:
- Users: 5
- Spawn rate: 1/sec
- Duration: 2 minutes
- User class: `AsyncSimulationUser`

**When to use**: After deployments, before running larger tests

```bash
./run_load_tests.sh smoke
```

### 2. Baseline Test

**Purpose**: Establish performance baseline under normal conditions

**Configuration**:
- Users: 10
- Spawn rate: 2/sec
- Duration: 5 minutes
- User class: `MixedWorkloadUser`

**When to use**: Regular performance monitoring, comparing versions

```bash
./run_load_tests.sh baseline
```

### 3. Load Test

**Purpose**: Validate performance under expected production load

**Configuration**:
- Users: 50
- Spawn rate: 5/sec
- Duration: 10 minutes
- User class: `MixedWorkloadUser`

**When to use**: Pre-production validation, capacity planning

```bash
./run_load_tests.sh load
```

### 4. Stress Test

**Purpose**: Find the breaking point and identify limits

**Configuration**:
- Users: 100
- Spawn rate: 10/sec
- Duration: 10 minutes
- User class: `StressTestUser`

**When to use**: Capacity planning, finding bottlenecks

```bash
./run_load_tests.sh stress
```

### 5. Spike Test

**Purpose**: Test behavior under sudden traffic spikes

**Configuration**:
- Phase 1: 10 users for 3 minutes (baseline)
- Phase 2: 100 users for 3 minutes (spike)
- Phase 3: 10 users for 3 minutes (recovery)

**When to use**: Testing auto-scaling, cache warmup

```bash
./run_load_tests.sh spike
```

### 6. Endurance Test

**Purpose**: Detect memory leaks and performance degradation over time

**Configuration**:
- Users: 30
- Spawn rate: 3/sec
- Duration: 30 minutes
- User class: `MixedWorkloadUser`

**When to use**: Stability testing, memory leak detection

```bash
./run_load_tests.sh endurance
```

### 7. Async Test

**Purpose**: Focus on asynchronous endpoint performance

**Configuration**:
- Users: 50
- Spawn rate: 5/sec
- Duration: 10 minutes
- User class: `AsyncSimulationUser`

**When to use**: Testing Celery worker capacity

```bash
./run_load_tests.sh async
```

### 8. Sync Test

**Purpose**: Focus on synchronous endpoint performance

**Configuration**:
- Users: 20
- Spawn rate: 2/sec
- Duration: 10 minutes
- User class: `SyncSimulationUser`

**When to use**: Comparing sync vs async performance

```bash
./run_load_tests.sh sync
```

### 9. Full Test Suite

**Purpose**: Run all tests sequentially

```bash
./run_load_tests.sh full
```

### 10. Custom Test

**Purpose**: Run custom test with specific parameters

```bash
# Usage: ./run_load_tests.sh custom <users> <spawn_rate> <run_time> [user_class]

# Example: 25 users, 5/sec spawn rate, 10 minutes
./run_load_tests.sh custom 25 5 10m MixedWorkloadUser

# Example: High-stress test
./run_load_tests.sh custom 200 20 5m StressTestUser
```

## Running Tests

### Interactive Web UI Mode

Best for exploratory testing and monitoring:

```bash
# Start Locust web UI
./run_load_tests.sh web

# or
locust --host=http://localhost:8000

# Then open http://localhost:8089 in your browser
```

**Web UI Features**:
- Real-time charts of RPS, response times, errors
- Start/stop tests on demand
- Adjust user count while test is running
- Download detailed statistics

### Headless Mode

Best for CI/CD and automated testing:

```bash
# Run predefined scenario
./run_load_tests.sh load

# Run custom headless test
locust --host=http://localhost:8000 \
       --users 50 \
       --spawn-rate 5 \
       --run-time 10m \
       --headless \
       --only-summary \
       --csv load_test_results/my_test \
       --html load_test_results/my_test.html
```

### Distributed Load Testing

For very high load, run Locust in distributed mode:

```bash
# Terminal 1: Start master
locust --host=http://localhost:8000 --master

# Terminal 2-N: Start workers (on same or different machines)
locust --host=http://localhost:8000 --worker --master-host=localhost

# Run test with 1000 users across all workers
# Access web UI at http://localhost:8089
```

### Testing Against Different Environments

```bash
# Test local development
HOST=http://localhost:8000 ./run_load_tests.sh load

# Test staging
HOST=https://staging.flow-forecaster.com ./run_load_tests.sh load

# Test production (use with caution!)
HOST=https://flow-forecaster.com ./run_load_tests.sh smoke
```

## Analyzing Results

### Understanding Locust Output

#### Console Output

```
Type     Name                                                           # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
--------|----------------------------------------------------------|-------|-------|-------|-------|-------|-------|--------|-----------
POST     /api/async/simulate (submit)                                      245     0(0.00%)  |     125      85     450     120  |    4.08    0.00
GET      /api/tasks/{task_id} (poll)                                      2450     0(0.00%)  |      45      12     220      40  |   40.83    0.00
GET      /api/async/health                                                 4900     0(0.00%)  |      15       5      85      12  |   81.67    0.00
--------|----------------------------------------------------------|-------|-------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                        7595     0(0.00%)  |      38       5     450      15  |  126.58    0.00

Response time percentiles (approximated)
Type     Name                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|------|------|------|------|------|------|------|------|------|------|------
POST     /api/async/simulate (submit)                                          120    140    160    180    220    280    350    400    450    450    450    245
GET      /api/tasks/{task_id} (poll)                                            40     48     55     60     75     95    140    180    220    220    220   2450
GET      /api/async/health                                                       12     14     16     18     22     28     40     55     85     85     85   4900
--------|--------------------------------------------------------------------------------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                              15     20     28     38     75    120    180    220    350    450    450   7595
```

**Key Metrics Explained**:

- **# reqs**: Total number of requests made
- **# fails**: Number of failed requests
- **Avg/Min/Max**: Average, minimum, maximum response times (ms)
- **Median**: 50th percentile response time
- **req/s**: Requests per second (throughput)
- **Percentiles**: Response time distribution (50%, 95%, 99%)

#### CSV Results

Results are saved to `load_test_results/<test_name>_<timestamp>_stats.csv`:

```csv
Type,Name,Request Count,Failure Count,Median Response Time,Average Response Time,Min Response Time,Max Response Time,Average Content Size,Requests/s,Failures/s,50%,66%,75%,80%,90%,95%,98%,99%,99.9%,99.99%,100%
POST,/api/async/simulate,245,0,120,125,85,450,512,4.08,0.00,120,140,160,180,220,280,350,400,450,450,450
GET,/api/tasks/{task_id},2450,0,40,45,12,220,256,40.83,0.00,40,48,55,60,75,95,140,180,220,220,220
```

#### HTML Report

Interactive HTML report at `load_test_results/<test_name>_<timestamp>.html` includes:

- Charts of response times over time
- Charts of throughput (RPS) over time
- Distribution of response times
- Failures table
- Exceptions details

### Performance Baselines

#### Expected Results - Async Architecture

Based on async architecture with Celery + PostgreSQL + Redis:

**Smoke Test (5 users)**:
```
Endpoint                          Avg (ms)  p95 (ms)  p99 (ms)  RPS    Error Rate
/api/async/simulate (submit)      120       200       280       0.8    0%
/api/tasks/{task_id} (poll)       40        80        120       8.0    0%
/api/async/health                 12        25        35        16.0   0%
```

**Load Test (50 users)**:
```
Endpoint                          Avg (ms)  p95 (ms)  p99 (ms)  RPS    Error Rate
/api/async/simulate (submit)      180       350       500       8.0    0%
/api/tasks/{task_id} (poll)       55        120       180       80.0   0%
/api/async/health                 15        30        45        160.0  0%
/api/forecasts (list)             25        55        85        40.0   0%
```

**Stress Test (100 users)**:
```
Endpoint                          Avg (ms)  p95 (ms)  p99 (ms)  RPS    Error Rate
/api/async/simulate (submit)      280       600       850       15.0   <1%
/api/tasks/{task_id} (poll)       85        200       350       150.0  <1%
/api/async/health                 22        50        80        300.0  0%
```

#### Expected Results - Sync Architecture (Legacy)

**Load Test (20 users)** - Note: Lower concurrent users due to blocking:
```
Endpoint                          Avg (ms)  p95 (ms)  p99 (ms)  RPS    Error Rate
/monte_carlo (sync)               2500      4500      6000      3.0    0%
/throughput (sync)                2200      4000      5500      3.5    0%
/ (dashboard)                     45        95        150       20.0   0%
```

### Performance Criteria

**Acceptable Performance**:
- ✅ p95 response time < 500ms for async task submission
- ✅ p95 response time < 100ms for task status polling
- ✅ p95 response time < 50ms for health checks
- ✅ Error rate < 1%
- ✅ Throughput > 100 RPS total

**Warning Signs**:
- ⚠️ p95 response time > 1000ms
- ⚠️ Error rate 1-5%
- ⚠️ Response times increasing over time (memory leak)
- ⚠️ High variance in response times

**Critical Issues**:
- ❌ p95 response time > 5000ms
- ❌ Error rate > 5%
- ❌ Timeouts or connection errors
- ❌ Application crashes
- ❌ Database connection pool exhausted

### Monitoring During Load Tests

While tests are running, monitor system resources:

**1. Application Metrics (Prometheus + Grafana)**:
```bash
# Open Grafana dashboards
open http://localhost:3000

# Watch metrics in real-time:
# - Application Overview dashboard
# - Celery Workers dashboard
# - Infrastructure dashboard
```

**2. System Resources**:
```bash
# CPU and Memory
htop

# or
watch -n 1 'ps aux | grep -E "(python|celery|redis|postgres)" | grep -v grep'

# Disk I/O
iostat -x 2

# Network
iftop
```

**3. Celery Workers**:
```bash
# Watch Flower UI
open http://localhost:5555

# Or use CLI
watch -n 1 'celery -A celery_app inspect active'
```

**4. Database Connections**:
```bash
# PostgreSQL connections
docker exec forecaster_postgres psql -U forecaster -c "SELECT count(*) FROM pg_stat_activity WHERE datname='forecaster';"

# Redis info
redis-cli info clients
```

## Troubleshooting

### High Error Rates

**Symptoms**: Error rate > 5%, many failed requests

**Possible Causes**:
1. **Application overload** - Too many concurrent requests
2. **Database connection pool exhausted** - All connections in use
3. **Celery workers overloaded** - Task queue backup
4. **Redis connection limit** - Too many clients

**Solutions**:

```bash
# 1. Check application logs
docker-compose logs web --tail=100

# 2. Check database connections
docker exec forecaster_postgres psql -U forecaster -c "
SELECT state, count(*)
FROM pg_stat_activity
WHERE datname='forecaster'
GROUP BY state;"

# 3. Increase database pool size
# Edit database.py:
pool_size=20 → pool_size=40
max_overflow=40 → max_overflow=80

# 4. Scale Celery workers
docker-compose up -d --scale celery_worker=4

# 5. Check Redis memory
redis-cli info memory

# 6. Reduce test load
./run_load_tests.sh custom 20 2 5m
```

### Slow Response Times

**Symptoms**: p95 > 1000ms, increasing over time

**Possible Causes**:
1. **Database slow queries** - Missing indexes, complex queries
2. **Memory pressure** - Swapping to disk
3. **CPU saturation** - All cores at 100%
4. **Network latency** - Slow connections

**Solutions**:

```bash
# 1. Check slow queries (PostgreSQL)
docker exec forecaster_postgres psql -U forecaster -d forecaster -c "
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 seconds';"

# 2. Check system resources
free -h         # Memory
top             # CPU
vmstat 1 5      # Virtual memory stats

# 3. Enable query logging
# Edit postgresql.conf:
log_min_duration_statement = 1000  # Log queries > 1s

# 4. Add database indexes
# Analyze query plans:
EXPLAIN ANALYZE SELECT ...;

# 5. Optimize N+1 queries
# Use SQLAlchemy joinedload/selectinload
```

### Connection Errors

**Symptoms**: "Connection refused", "Max retries exceeded"

**Possible Causes**:
1. **Application not running** - Service down
2. **Port mismatch** - Wrong port number
3. **Firewall blocking** - Network restrictions
4. **Too many open connections** - System limits

**Solutions**:

```bash
# 1. Verify services running
docker-compose ps

# 2. Check ports
netstat -tlnp | grep -E "(8000|6379|5432)"

# 3. Test connectivity
curl -v http://localhost:8000/api/async/health

# 4. Check system limits
ulimit -n     # File descriptors
sysctl net.core.somaxconn  # Connection backlog

# 5. Increase limits (Linux)
# /etc/security/limits.conf:
* soft nofile 65536
* hard nofile 65536

# /etc/sysctl.conf:
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
```

### Memory Leaks

**Symptoms**: Memory usage increasing over time, eventual crash

**Possible Causes**:
1. **Unclosed database connections** - Sessions not closed
2. **Task results not cleaned** - Celery result accumulation
3. **Cache growth** - No TTL on cached data
4. **Large objects in memory** - Holding references

**Solutions**:

```bash
# 1. Monitor memory over time
watch -n 5 'free -h'

# 2. Profile Python memory
pip install memory_profiler
python -m memory_profiler app.py

# 3. Clean Celery results
celery -A celery_app purge

# 4. Set result expiry
# celery_app.py:
result_expires=3600  # 1 hour

# 5. Use context managers for sessions
with get_db_session() as session:
    # queries here
    pass  # session automatically closed

# 6. Monitor with Prometheus
# Check: node_memory_MemAvailable_bytes
```

### Database Deadlocks

**Symptoms**: "Deadlock detected", transactions failing

**Possible Causes**:
1. **Lock contention** - Multiple transactions on same rows
2. **Long transactions** - Holding locks too long
3. **Lock ordering issues** - Inconsistent lock acquisition

**Solutions**:

```bash
# 1. Check for deadlocks
docker exec forecaster_postgres psql -U forecaster -d forecaster -c "
SELECT * FROM pg_stat_activity WHERE wait_event_type = 'Lock';"

# 2. Enable deadlock logging
# postgresql.conf:
log_lock_waits = on
deadlock_timeout = 1s

# 3. Optimize transactions
# Keep transactions short
# Use appropriate isolation levels
# Order lock acquisition consistently

# 4. Add retries
# app_async_endpoints.py:
@retry(max_retries=3, default_retry_delay=1)
def save_forecast(...):
    # database operations
```

## Best Practices

### 1. Test Environment

- **Use dedicated test environment** - Don't test on production
- **Match production configuration** - Same database, cache, workers
- **Isolate from other services** - Avoid noisy neighbors
- **Use production-like data** - Representative data volumes

### 2. Test Execution

- **Start small** - Run smoke test first
- **Ramp up gradually** - Increase load incrementally
- **Monitor throughout** - Watch metrics during test
- **Run multiple times** - Average results, account for variance
- **Test at different times** - Consider time of day effects

### 3. Result Interpretation

- **Focus on percentiles** - p95/p99 more important than average
- **Look for trends** - Increasing response times indicate issues
- **Compare against baseline** - Track changes over time
- **Consider user experience** - What's acceptable for users?
- **Document findings** - Keep records of results

### 4. Performance Optimization

- **Fix one thing at a time** - Isolate variables
- **Measure before and after** - Verify improvements
- **Profile before optimizing** - Find actual bottlenecks
- **Consider trade-offs** - Speed vs complexity vs cost

### 5. CI/CD Integration

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  schedule:
    - cron: '0 2 * * *'  # Run nightly
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-loadtest.txt

      - name: Start services
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to be ready

      - name: Run smoke test
        run: |
          ./run_load_tests.sh smoke

      - name: Check results
        run: |
          python scripts/check_performance.py load_test_results/

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: load_test_results/
```

### 6. Performance Budgets

Set and enforce performance budgets:

```python
# scripts/check_performance.py
PERFORMANCE_BUDGETS = {
    '/api/async/simulate': {
        'p95_ms': 500,
        'p99_ms': 1000,
        'error_rate': 0.01,  # 1%
    },
    '/api/tasks/{task_id}': {
        'p95_ms': 100,
        'p99_ms': 200,
        'error_rate': 0.01,
    },
}

def check_results(csv_file):
    results = parse_csv(csv_file)
    failures = []

    for endpoint, metrics in results.items():
        budget = PERFORMANCE_BUDGETS.get(endpoint)
        if not budget:
            continue

        if metrics['p95'] > budget['p95_ms']:
            failures.append(f"{endpoint} p95: {metrics['p95']}ms > {budget['p95_ms']}ms")

        if metrics['error_rate'] > budget['error_rate']:
            failures.append(f"{endpoint} error rate: {metrics['error_rate']} > {budget['error_rate']}")

    if failures:
        print("PERFORMANCE BUDGET FAILURES:")
        for failure in failures:
            print(f"  ❌ {failure}")
        sys.exit(1)
    else:
        print("✅ All performance budgets met")
```

## Sample Results

### Baseline Test Results

**Configuration**: 10 users, 5 minutes, MixedWorkloadUser

**Results**:
```
Total Requests: 12,450
Total Failures: 0 (0%)
Average Response Time: 42ms
Median Response Time: 28ms
95th Percentile: 120ms
99th Percentile: 280ms
Requests/sec: 41.5
```

**Breakdown by Endpoint**:
```
Endpoint                          Requests  RPS    Avg    p50    p95    p99    Errors
/api/async/simulate                  450   1.5    185     165    320    450    0%
/api/tasks/{task_id}                4,500  15.0    45      38     92    155    0%
/api/async/health                   4,900  16.3    12       9     22     35    0%
/api/forecasts (list)                 900   3.0    35      28     68    105    0%
/api/forecasts/{id}                 1,200   4.0    28      22     58     95    0%
/ (dashboard)                         500   1.7    55      45    115    175    0%
```

**Resource Usage**:
- CPU: 45% average, 72% peak
- Memory: 1.2GB used (60%)
- Database connections: 12/60 used
- Redis memory: 45MB
- Celery queue: 0-5 pending tasks

**Conclusion**: ✅ Excellent performance, well within acceptable limits

### Load Test Results

**Configuration**: 50 users, 10 minutes, MixedWorkloadUser

**Results**:
```
Total Requests: 78,920
Total Failures: 12 (0.015%)
Average Response Time: 125ms
Median Response Time: 68ms
95th Percentile: 420ms
99th Percentile: 850ms
Requests/sec: 131.5
```

**Resource Usage**:
- CPU: 78% average, 95% peak
- Memory: 1.8GB used (90%)
- Database connections: 35/60 used
- Redis memory: 125MB
- Celery queue: 5-25 pending tasks

**Conclusion**: ✅ Good performance under expected production load. Minor optimization opportunities.

## Recommendations

Based on load testing results:

### Short Term (Quick Wins)

1. **Enable HTTP caching** for static content
2. **Add database indexes** on frequently queried columns
3. **Increase Celery worker count** to 8 workers
4. **Enable Redis persistence** for reliability

### Medium Term (Next Sprint)

1. **Implement API rate limiting** to prevent abuse
2. **Add response compression** (gzip)
3. **Optimize database queries** (fix N+1, add eager loading)
4. **Add caching layer** for frequently accessed data

### Long Term (Scalability)

1. **Implement horizontal scaling** (load balancer + multiple app instances)
2. **Use CDN** for static assets
3. **Add database read replicas** for read-heavy operations
4. **Consider sharding** for very large datasets

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [Load Testing Best Practices](https://grafana.com/blog/2024/01/30/load-testing-best-practices/)
- [Performance Testing Guide](https://www.nginx.com/blog/performance-testing-guidelines/)
- [Database Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
