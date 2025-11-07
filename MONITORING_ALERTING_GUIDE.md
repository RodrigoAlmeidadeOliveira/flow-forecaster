# Flow Forecaster - Monitoring and Alerting Guide

Comprehensive guide for monitoring the Flow Forecaster application with Prometheus, Grafana, and Alertmanager.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Components](#components)
- [Dashboards](#dashboards)
- [Alerts](#alerts)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The Flow Forecaster monitoring stack provides:

- **Metrics Collection**: Prometheus scrapes metrics from all application components
- **Visualization**: Grafana dashboards for application, workers, and infrastructure
- **Alerting**: Alertmanager routes critical and warning alerts to multiple channels
- **Exporters**: Specialized exporters for PostgreSQL, Redis, and system metrics

### Key Features

- Real-time application performance monitoring
- Celery task queue and worker metrics
- Infrastructure resource utilization (CPU, memory, disk, network)
- Database and cache health monitoring
- Customizable alerts with email, Slack, and PagerDuty integration
- 30-day metric retention

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Monitoring Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Flask   │───▶│Prometheus│───▶│ Grafana  │    │Alertmgr  │  │
│  │   App    │    │          │    │Dashboards│    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                         │                               │         │
│  ┌──────────┐          │                               │         │
│  │  Celery  │──────────┤                               │         │
│  │  Flower  │          │                               │         │
│  └──────────┘          │                               ▼         │
│                         │                          ┌──────────┐  │
│  ┌──────────┐          │                          │  Email   │  │
│  │   Node   │──────────┤                          │  Slack   │  │
│  │ Exporter │          │                          │PagerDuty │  │
│  └──────────┘          │                          └──────────┘  │
│                         │                                        │
│  ┌──────────┐          │                                        │
│  │  Redis   │──────────┤                                        │
│  │ Exporter │          │                                        │
│  └──────────┘          │                                        │
│                         │                                        │
│  ┌──────────┐          │                                        │
│  │Postgres  │──────────┘                                        │
│  │ Exporter │                                                    │
│  └──────────┘                                                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start main application first
docker-compose up -d

# Start monitoring services
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Verify all services are running
docker-compose ps
```

### 2. Access Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | None |
| Alertmanager | http://localhost:9093 | None |
| Flower (Celery) | http://localhost:5555 | None |

### 3. View Dashboards

1. Open Grafana at http://localhost:3000
2. Login with `admin` / `admin` (change password on first login)
3. Navigate to **Dashboards** → **Browse**
4. Select one of the pre-configured dashboards:
   - **Application Overview** - Request rates, errors, response times
   - **Celery Workers** - Task metrics, queue status, worker health
   - **Infrastructure** - CPU, memory, disk, network, database

## Components

### Prometheus

**Purpose**: Metrics collection and storage

**Configuration**: `monitoring/prometheus.yml`

**Scrape Targets**:
- `prometheus:9090` - Prometheus itself
- `node_exporter:9100` - System metrics
- `redis_exporter:9121` - Redis metrics
- `postgres_exporter:9187` - PostgreSQL metrics
- `web:8000/metrics` - Flask application metrics
- `flower:5555/metrics` - Celery worker metrics

**Retention**: 30 days

**Accessing Prometheus**:
```bash
# Open in browser
open http://localhost:9090

# Example queries
up                                    # Service availability
rate(flask_http_request_total[5m])   # Request rate
celery_tasks_total{state="PENDING"}  # Pending tasks
```

### Grafana

**Purpose**: Visualization and dashboards

**Configuration**: `monitoring/grafana/provisioning/`

**Pre-configured Datasources**:
- Prometheus (default)
- PostgreSQL
- Redis

**Dashboards**:

#### 1. Application Overview (`application-overview.json`)

Monitors HTTP request metrics:
- Request rate by endpoint
- Error rate (5xx responses)
- Response time percentiles (p50, p95, p99)
- Status code distribution
- Active requests
- Total requests and errors (1h)
- Application health status

**Key Metrics**:
```promql
# Request rate
rate(flask_http_request_total[5m])

# Error rate
rate(flask_http_request_total{status=~"5.."}[5m]) / rate(flask_http_request_total[5m])

# Response time p95
histogram_quantile(0.95, rate(flask_http_request_duration_seconds_bucket[5m]))
```

#### 2. Celery Workers (`celery-workers.json`)

Monitors background task processing:
- Task completion rate (success/failure)
- Task failure rate
- Task duration percentiles
- Queue status (pending, active, retry)
- Pending/active/failed task counts
- Worker health status
- Task distribution by type
- Task throughput

**Key Metrics**:
```promql
# Task success rate
rate(celery_tasks_total{state="SUCCESS"}[5m])

# Task failure rate
rate(celery_tasks_total{state="FAILURE"}[10m]) / rate(celery_tasks_total[10m])

# Pending tasks
celery_tasks_total{state="PENDING"}
```

#### 3. Infrastructure (`infrastructure.json`)

Monitors system resources:
- CPU usage (percentage and timeline)
- Memory usage (percentage and bytes)
- Disk usage
- Network I/O (receive/transmit)
- PostgreSQL status and connections
- Redis status and connections
- Redis memory usage
- PostgreSQL transaction rate

**Key Metrics**:
```promql
# CPU usage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# Disk usage
100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100)
```

### Alertmanager

**Purpose**: Alert routing and notifications

**Configuration**: `monitoring/alertmanager.yml`

**Notification Channels**:
1. **Email (SMTP)**
   - Default team alerts
   - Critical on-call alerts
   - Warning team alerts

2. **Slack** (optional)
   - Critical: `#alerts-critical`
   - Warning: `#alerts-warning`

3. **PagerDuty** (optional)
   - Critical alerts only

**Routing Rules**:
- Critical alerts → Email (on-call + team) + Slack + PagerDuty
- Warning alerts → Email (team) + Slack
- Default → Email (team)

**Inhibition Rules**:
- Critical alerts suppress warning alerts for the same service

### Exporters

#### Node Exporter
- **Port**: 9100
- **Metrics**: CPU, memory, disk, network, filesystem
- **Image**: `prom/node-exporter:latest`

#### Redis Exporter
- **Port**: 9121
- **Metrics**: Memory, connections, commands, keys
- **Image**: `oliver006/redis_exporter:latest`

#### PostgreSQL Exporter
- **Port**: 9187
- **Metrics**: Connections, transactions, queries, locks
- **Image**: `prometheuscommunity/postgres-exporter:latest`

## Alerts

### Alert Rules

Configuration: `monitoring/alert.rules.yml`

| Alert | Severity | Threshold | Duration | Description |
|-------|----------|-----------|----------|-------------|
| **HighErrorRate** | critical | >5% | 5m | HTTP 5xx error rate exceeds threshold |
| **HighResponseTime** | warning | >2s | 5m | p95 response time exceeds threshold |
| **CeleryWorkersDown** | critical | 0 workers | 2m | No Celery workers responding |
| **HighMemoryUsage** | warning | >85% | 5m | System memory usage high |
| **HighCPUUsage** | warning | >80% | 10m | System CPU usage high |
| **RedisDown** | critical | down | 1m | Redis server not responding |
| **PostgreSQLDown** | critical | down | 1m | PostgreSQL database not responding |
| **DiskSpaceLow** | warning | <15% | 5m | Available disk space low |
| **TooManyPendingTasks** | warning | >100 | 10m | Celery queue backlog |
| **HighTaskFailureRate** | critical | >10% | 5m | Task failure rate high |

### Alert Examples

#### HighErrorRate
```yaml
alert: HighErrorRate
expr: rate(flask_http_request_total{status=~"5.."}[5m]) > 0.05
for: 5m
labels:
  severity: critical
annotations:
  summary: "High error rate detected"
  description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
```

#### CeleryWorkersDown
```yaml
alert: CeleryWorkersDown
expr: up{job="celery_flower"} == 0
for: 2m
labels:
  severity: critical
annotations:
  summary: "Celery workers are down"
  description: "No Celery workers are responding"
```

### Testing Alerts

```bash
# Trigger a test alert
curl -X POST http://localhost:9093/api/v1/alerts -d '[{
  "labels": {
    "alertname": "TestAlert",
    "severity": "warning"
  },
  "annotations": {
    "summary": "Test alert from manual trigger"
  }
}]'

# Check alert status
curl http://localhost:9093/api/v1/alerts | jq

# Silence an alert
curl -X POST http://localhost:9093/api/v1/silences -d '{
  "matchers": [
    {
      "name": "alertname",
      "value": "HighMemoryUsage",
      "isRegex": false
    }
  ],
  "startsAt": "2025-01-01T00:00:00Z",
  "endsAt": "2025-01-01T12:00:00Z",
  "comment": "Planned maintenance",
  "createdBy": "admin"
}'
```

## Configuration

### Email Notifications

Edit `monitoring/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@your-domain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'  # Use app-specific password
  smtp_require_tls: true
```

**Gmail Setup**:
1. Enable 2FA on your Google account
2. Generate an app-specific password
3. Use the app password in `smtp_auth_password`

### Slack Notifications

1. Create a Slack webhook:
   - Go to https://api.slack.com/apps
   - Create new app → Incoming Webhooks
   - Activate webhooks and add to workspace
   - Copy webhook URL

2. Edit `monitoring/alertmanager.yml`:
```yaml
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts-critical'
    title: '🚨 Critical Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}\n{{ end }}'
    send_resolved: true
```

### PagerDuty Integration

1. Create PagerDuty service integration key

2. Edit `monitoring/alertmanager.yml`:
```yaml
pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

### Custom Metrics

Add custom metrics to your Flask app:

```python
from prometheus_client import Counter, Histogram, Gauge

# Counter example
simulation_counter = Counter(
    'simulation_total',
    'Total simulations run',
    ['simulation_type']
)

# Histogram example
simulation_duration = Histogram(
    'simulation_duration_seconds',
    'Simulation execution time',
    ['simulation_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

# Gauge example
active_simulations = Gauge(
    'simulation_active',
    'Currently running simulations'
)

# Usage
@app.route('/api/simulate')
def simulate():
    simulation_counter.labels(simulation_type='monte_carlo').inc()

    with simulation_duration.labels(simulation_type='monte_carlo').time():
        # Run simulation
        result = run_simulation()

    return result
```

### Custom Alerts

Add new alerts to `monitoring/alert.rules.yml`:

```yaml
- alert: CustomAlert
  expr: your_custom_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom alert description"
    description: "Value is {{ $value }}"
```

Reload Prometheus configuration:
```bash
curl -X POST http://localhost:9090/-/reload
```

## Troubleshooting

### Services Not Starting

```bash
# Check service logs
docker-compose logs prometheus
docker-compose logs grafana
docker-compose logs alertmanager

# Check service health
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:9093/-/healthy  # Alertmanager
curl http://localhost:3000/api/health # Grafana
```

### No Metrics in Grafana

1. **Check Prometheus targets**:
   - Open http://localhost:9090/targets
   - All targets should show "UP"
   - If down, check network and service health

2. **Check Grafana datasource**:
   - Go to Configuration → Data Sources → Prometheus
   - Click "Test" button
   - Should show "Data source is working"

3. **Check metric names**:
   ```bash
   # List all metrics
   curl http://localhost:9090/api/v1/label/__name__/values | jq

   # Query specific metric
   curl 'http://localhost:9090/api/v1/query?query=up' | jq
   ```

### Alerts Not Firing

1. **Check alert rules**:
   ```bash
   # View active alerts
   curl http://localhost:9090/api/v1/alerts | jq

   # Check rule evaluation
   curl http://localhost:9090/api/v1/rules | jq
   ```

2. **Test alert expression**:
   - Open http://localhost:9090/graph
   - Enter alert expression
   - Check if it returns data

3. **Check Alertmanager**:
   ```bash
   # View active alerts in Alertmanager
   curl http://localhost:9093/api/v1/alerts | jq

   # Check configuration
   curl http://localhost:9093/api/v1/status | jq
   ```

### Email Alerts Not Sending

1. **Check SMTP credentials**:
   - Verify `smtp_auth_username` and `smtp_auth_password`
   - For Gmail, use app-specific password (not account password)

2. **Check Alertmanager logs**:
   ```bash
   docker-compose logs alertmanager | grep -i smtp
   ```

3. **Test email manually**:
   ```bash
   # Trigger test alert
   curl -X POST http://localhost:9093/api/v1/alerts -d '[{
     "labels": {"alertname": "TestEmail", "severity": "warning"},
     "annotations": {"summary": "Test email"}
   }]'
   ```

### High Memory Usage

1. **Reduce Prometheus retention**:
   Edit `docker-compose.monitoring.yml`:
   ```yaml
   - '--storage.tsdb.retention.time=7d'  # Reduce from 30d
   ```

2. **Increase scrape interval**:
   Edit `monitoring/prometheus.yml`:
   ```yaml
   global:
     scrape_interval: 30s  # Increase from 15s
   ```

3. **Limit metric cardinality**:
   - Avoid high-cardinality labels (e.g., user IDs, timestamps)
   - Use aggregation and recording rules

### Dashboard Not Loading

1. **Check provisioning**:
   ```bash
   docker exec forecaster_grafana ls -la /etc/grafana/provisioning/dashboards
   docker exec forecaster_grafana ls -la /var/lib/grafana/dashboards
   ```

2. **Check Grafana logs**:
   ```bash
   docker-compose logs grafana | grep -i error
   ```

3. **Manually import dashboard**:
   - Go to Dashboards → Import
   - Upload JSON file from `monitoring/grafana/dashboards/`

## Best Practices

### 1. Alert Fatigue

- Set appropriate thresholds to avoid false positives
- Use `for` duration to prevent flapping alerts
- Implement inhibition rules to suppress redundant alerts
- Regularly review and tune alert rules

### 2. Metric Collection

- Use consistent naming conventions (`<namespace>_<metric>_<unit>`)
- Keep label cardinality low
- Use histograms for timing metrics
- Use counters for events, gauges for states

### 3. Dashboard Design

- Group related metrics together
- Use appropriate visualization types
- Include context (thresholds, baselines)
- Add descriptions and units

### 4. Security

- Change default Grafana password immediately
- Use HTTPS in production (reverse proxy)
- Restrict network access to monitoring ports
- Use secrets management for credentials
- Enable authentication for Prometheus and Alertmanager

### 5. Maintenance

- Regularly review and update dashboards
- Archive old metrics data
- Test alert routing periodically
- Document custom metrics and alerts
- Keep exporters and images updated

## Production Considerations

### Scaling

For high-traffic production environments:

1. **Use external Prometheus storage**:
   - Thanos for long-term storage
   - Cortex for multi-tenant setup
   - Victoria Metrics for performance

2. **Deploy multiple Prometheus instances**:
   - Shard by service or region
   - Use federation for aggregation

3. **Use Grafana Enterprise**:
   - RBAC and team permissions
   - Advanced alerting features
   - Enhanced authentication

### High Availability

1. **Run multiple Alertmanager instances**:
   ```yaml
   alertmanager:
     replicas: 3
   ```

2. **Use external PostgreSQL/Redis**:
   - Managed database services
   - Replication and backups

3. **Load balance Grafana**:
   - Multiple Grafana instances
   - Shared database backend

### Backup and Recovery

```bash
# Backup Prometheus data
docker run --rm -v prometheus_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data

# Backup Grafana data
docker run --rm -v grafana_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz /data

# Restore
docker run --rm -v prometheus_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/prometheus-backup.tar.gz -C /
```

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
