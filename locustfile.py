"""
Flow Forecaster Load Testing with Locust

This file contains load testing scenarios for the Flow Forecaster application.

Usage:
    # Web UI mode (recommended)
    locust --host=http://localhost:8000

    # Headless mode (automated)
    locust --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 5m --headless

    # Specific scenario
    locust --host=http://localhost:8000 -f locustfile.py AsyncSimulationUser
"""

import json
import random
import time
from locust import HttpUser, task, between, tag, events
from locust.contrib.fasthttp import FastHttpUser


class BaseFlowForecasterUser(HttpUser):
    """Base user with common setup for Flow Forecaster testing"""

    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts"""
        # Login or get session token
        self.login()

        # Store test data
        self.test_project_id = None
        self.test_forecast_ids = []

    def login(self):
        """Simulate user login"""
        # For now, create a test user or use existing one
        # In production, you'd login with credentials
        response = self.client.post("/register", data={
            "username": f"loadtest_user_{random.randint(1000, 9999)}",
            "password": "testpass123"
        }, catch_response=True)

        if response.status_code == 200 or response.status_code == 302:
            response.success()
        else:
            # User might already exist, try login
            self.client.post("/login", data={
                "username": "testuser",
                "password": "testpass123"
            })

    def create_test_project(self):
        """Create a test project for simulations"""
        response = self.client.post("/api/projects", json={
            "name": f"Load Test Project {random.randint(1000, 9999)}",
            "description": "Automated load testing project"
        }, catch_response=True)

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            self.test_project_id = data.get("id") or data.get("project_id")
            response.success()
        return response


class SyncSimulationUser(BaseFlowForecasterUser):
    """User that runs synchronous simulations (legacy endpoints)"""

    @tag('sync', 'monte_carlo')
    @task(3)
    def run_monte_carlo_sync(self):
        """Run synchronous Monte Carlo simulation"""
        simulation_data = {
            "targetOutcome": 100,
            "pBest": 10,
            "pWorst": 50,
            "pLikely": 25,
            "sCurveSize": 3,
            "nSimulations": 1000,
            "confidence": 0.85
        }

        with self.client.post(
            "/monte_carlo",
            json=simulation_data,
            catch_response=True,
            name="/monte_carlo (sync)"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "distribution" in result or "simulations" in result:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Status code: {response.status_code}")

    @tag('sync', 'throughput')
    @task(2)
    def run_throughput_sync(self):
        """Run synchronous throughput analysis"""
        simulation_data = {
            "targetOutcome": 100,
            "pBest": 10,
            "pWorst": 50,
            "pLikely": 25,
            "sCurveSize": 3,
            "nSimulations": 1000,
            "confidence": 0.85,
            "daysPerWeek": 5
        }

        with self.client.post(
            "/throughput",
            json=simulation_data,
            catch_response=True,
            name="/throughput (sync)"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @tag('sync', 'read')
    @task(5)
    def view_dashboard(self):
        """Load main dashboard"""
        with self.client.get("/", catch_response=True, name="/ (dashboard)") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class AsyncSimulationUser(BaseFlowForecasterUser):
    """User that runs asynchronous simulations (Celery-based)"""

    @tag('async', 'monte_carlo')
    @task(5)
    def run_monte_carlo_async(self):
        """Run asynchronous Monte Carlo simulation"""
        simulation_data = {
            "targetOutcome": 100,
            "pBest": 10,
            "pWorst": 50,
            "pLikely": 25,
            "sCurveSize": 3,
            "nSimulations": 1000,
            "confidence": 0.85,
            "save_forecast": False
        }

        # Submit task
        with self.client.post(
            "/api/async/simulate",
            json=simulation_data,
            catch_response=True,
            name="/api/async/simulate (submit)"
        ) as response:
            if response.status_code == 202:
                task_data = response.json()
                task_id = task_data.get("task_id")

                if task_id:
                    response.success()
                    # Poll for result
                    self.poll_task_result(task_id)
                else:
                    response.failure("No task_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")

    @tag('async', 'backtest')
    @task(2)
    def run_backtest_async(self):
        """Run asynchronous backtest"""
        backtest_data = {
            "historicalData": [
                {"date": f"2025-01-{i:02d}", "itemsCompleted": random.randint(5, 15)}
                for i in range(1, 31)
            ],
            "targetOutcome": 100,
            "pBest": 10,
            "pWorst": 50,
            "pLikely": 25,
            "sCurveSize": 3,
            "nSimulations": 500,
            "confidence": 0.85,
            "fold_size": 7,
            "fold_stride": 1
        }

        with self.client.post(
            "/api/async/backtest",
            json=backtest_data,
            catch_response=True,
            name="/api/async/backtest (submit)"
        ) as response:
            if response.status_code == 202:
                task_data = response.json()
                task_id = task_data.get("task_id")

                if task_id:
                    response.success()
                    # Don't wait for backtest (takes longer)
                else:
                    response.failure("No task_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")

    def poll_task_result(self, task_id, max_attempts=30):
        """Poll for async task result"""
        for attempt in range(max_attempts):
            time.sleep(1)  # Wait 1 second between polls

            with self.client.get(
                f"/api/tasks/{task_id}",
                catch_response=True,
                name="/api/tasks/{task_id} (poll)"
            ) as response:
                if response.status_code == 200:
                    task_status = response.json()
                    state = task_status.get("state")

                    if state == "SUCCESS":
                        response.success()
                        return True
                    elif state == "FAILURE":
                        response.failure(f"Task failed: {task_status.get('error')}")
                        return False
                    elif state in ["PENDING", "PROGRESS"]:
                        # Still processing, continue polling
                        response.success()
                    else:
                        response.failure(f"Unknown state: {state}")
                        return False
                else:
                    response.failure(f"Status code: {response.status_code}")
                    return False

        # Timeout
        return False

    @tag('async', 'read')
    @task(10)
    def check_health(self):
        """Check system health"""
        with self.client.get(
            "/api/async/health",
            catch_response=True,
            name="/api/async/health"
        ) as response:
            if response.status_code == 200:
                health = response.json()
                if health.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy: {health}")
            else:
                response.failure(f"Status code: {response.status_code}")


class MixedWorkloadUser(BaseFlowForecasterUser):
    """User that performs a mix of read and write operations"""

    @tag('mixed', 'read')
    @task(20)
    def browse_forecasts(self):
        """Browse existing forecasts"""
        with self.client.get(
            "/api/forecasts",
            catch_response=True,
            name="/api/forecasts (list)"
        ) as response:
            if response.status_code == 200:
                forecasts = response.json()
                if isinstance(forecasts, list):
                    response.success()

                    # Store some forecast IDs for later operations
                    if forecasts and len(self.test_forecast_ids) < 5:
                        self.test_forecast_ids.extend([f.get("id") for f in forecasts[:5]])
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Status code: {response.status_code}")

    @tag('mixed', 'read')
    @task(15)
    def view_forecast_detail(self):
        """View a specific forecast"""
        if self.test_forecast_ids:
            forecast_id = random.choice(self.test_forecast_ids)

            with self.client.get(
                f"/api/forecasts/{forecast_id}",
                catch_response=True,
                name="/api/forecasts/{id} (detail)"
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 404:
                    # Forecast might have been deleted
                    self.test_forecast_ids.remove(forecast_id)
                    response.success()
                else:
                    response.failure(f"Status code: {response.status_code}")

    @tag('mixed', 'write')
    @task(5)
    def create_simulation(self):
        """Create a new simulation (async)"""
        simulation_data = {
            "targetOutcome": random.randint(50, 200),
            "pBest": random.randint(5, 15),
            "pWorst": random.randint(30, 60),
            "pLikely": random.randint(15, 35),
            "sCurveSize": random.choice([2, 3, 4]),
            "nSimulations": random.choice([500, 1000, 2000]),
            "confidence": random.choice([0.75, 0.85, 0.95]),
            "save_forecast": random.choice([True, False])
        }

        with self.client.post(
            "/api/async/simulate",
            json=simulation_data,
            catch_response=True,
            name="/api/async/simulate (create)"
        ) as response:
            if response.status_code == 202:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @tag('mixed', 'read')
    @task(10)
    def view_static_page(self):
        """Load a static page"""
        pages = ["/", "/dashboard", "/about"]
        page = random.choice(pages)

        with self.client.get(page, catch_response=True, name=f"{page} (static)") as response:
            if response.status_code == 200 or response.status_code == 404:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class StressTestUser(FastHttpUser):
    """
    High-performance user for stress testing using FastHttpUser
    This user generates maximum load with minimal overhead
    """
    wait_time = between(0.1, 0.5)  # Very short wait times

    @task(10)
    def quick_health_check(self):
        """Rapid health check requests"""
        self.client.get("/api/async/health")

    @task(5)
    def quick_simulation(self):
        """Rapid simulation submissions"""
        self.client.post("/api/async/simulate", json={
            "targetOutcome": 100,
            "pBest": 10,
            "pWorst": 50,
            "pLikely": 25,
            "sCurveSize": 3,
            "nSimulations": 500,
            "confidence": 0.85,
            "save_forecast": False
        })


# Custom event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("\n" + "="*80)
    print("Flow Forecaster Load Test Started")
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.user_count if hasattr(environment.runner, 'user_count') else 'N/A'}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("\n" + "="*80)
    print("Flow Forecaster Load Test Completed")
    print("="*80 + "\n")


# Custom stats tracking
request_success_count = 0
request_failure_count = 0


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track request statistics"""
    global request_success_count, request_failure_count

    if exception:
        request_failure_count += 1
    else:
        request_success_count += 1
