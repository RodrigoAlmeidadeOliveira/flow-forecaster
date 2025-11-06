#!/bin/bash

# Flow Forecaster Load Testing Script
# This script provides predefined load testing scenarios

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default host
HOST="${HOST:-http://localhost:8000}"

# Create results directory
RESULTS_DIR="load_test_results"
mkdir -p "$RESULTS_DIR"

# Timestamp for results
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Flow Forecaster Load Testing${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to run a test scenario
run_test() {
    local test_name="$1"
    local users="$2"
    local spawn_rate="$3"
    local run_time="$4"
    local user_class="${5:-AsyncSimulationUser}"

    echo -e "${YELLOW}Running test: $test_name${NC}"
    echo "  Users: $users"
    echo "  Spawn rate: $spawn_rate/sec"
    echo "  Duration: $run_time"
    echo "  User class: $user_class"
    echo ""

    locust \
        --host="$HOST" \
        --users "$users" \
        --spawn-rate "$spawn_rate" \
        --run-time "$run_time" \
        --headless \
        --only-summary \
        --csv "$RESULTS_DIR/${test_name}_${TIMESTAMP}" \
        --html "$RESULTS_DIR/${test_name}_${TIMESTAMP}.html" \
        "$user_class"

    echo -e "${GREEN}Test completed: $test_name${NC}"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    "smoke")
        echo "Smoke Test - Quick validation with minimal load"
        run_test "smoke_test" 5 1 "2m" "AsyncSimulationUser"
        ;;

    "baseline")
        echo "Baseline Test - Normal load conditions"
        run_test "baseline_test" 10 2 "5m" "MixedWorkloadUser"
        ;;

    "load")
        echo "Load Test - Expected production load"
        run_test "load_test" 50 5 "10m" "MixedWorkloadUser"
        ;;

    "stress")
        echo "Stress Test - High load to find limits"
        run_test "stress_test" 100 10 "10m" "StressTestUser"
        ;;

    "spike")
        echo "Spike Test - Sudden load increase"
        echo -e "${YELLOW}Phase 1: Baseline (10 users)${NC}"
        run_test "spike_test_baseline" 10 2 "3m" "MixedWorkloadUser"

        echo -e "${YELLOW}Phase 2: Spike (100 users)${NC}"
        run_test "spike_test_spike" 100 50 "3m" "MixedWorkloadUser"

        echo -e "${YELLOW}Phase 3: Recovery (10 users)${NC}"
        run_test "spike_test_recovery" 10 2 "3m" "MixedWorkloadUser"
        ;;

    "endurance")
        echo "Endurance Test - Sustained load over time"
        run_test "endurance_test" 30 3 "30m" "MixedWorkloadUser"
        ;;

    "async")
        echo "Async Test - Focus on asynchronous endpoints"
        run_test "async_test" 50 5 "10m" "AsyncSimulationUser"
        ;;

    "sync")
        echo "Sync Test - Focus on synchronous endpoints"
        run_test "sync_test" 20 2 "10m" "SyncSimulationUser"
        ;;

    "full")
        echo "Full Test Suite - Run all tests"
        run_test "01_smoke" 5 1 "2m" "AsyncSimulationUser"
        run_test "02_baseline" 10 2 "5m" "MixedWorkloadUser"
        run_test "03_load" 50 5 "10m" "MixedWorkloadUser"
        run_test "04_stress" 100 10 "10m" "StressTestUser"
        run_test "05_async" 50 5 "10m" "AsyncSimulationUser"
        run_test "06_sync" 20 2 "10m" "SyncSimulationUser"
        ;;

    "custom")
        # Custom test with user-provided parameters
        echo "Custom Test"
        USERS="${2:-10}"
        SPAWN_RATE="${3:-2}"
        RUN_TIME="${4:-5m}"
        USER_CLASS="${5:-MixedWorkloadUser}"

        run_test "custom_test" "$USERS" "$SPAWN_RATE" "$RUN_TIME" "$USER_CLASS"
        ;;

    "web")
        echo "Starting Locust Web UI"
        echo "Access the web interface at: http://localhost:8089"
        echo "Host is set to: $HOST"
        echo ""
        locust --host="$HOST"
        ;;

    *)
        echo "Usage: $0 <test_type> [options]"
        echo ""
        echo "Test types:"
        echo "  smoke      - Quick validation with 5 users for 2 minutes"
        echo "  baseline   - Normal load with 10 users for 5 minutes"
        echo "  load       - Production load with 50 users for 10 minutes"
        echo "  stress     - High load with 100 users for 10 minutes"
        echo "  spike      - Sudden load increase (10→100→10 users)"
        echo "  endurance  - Sustained load with 30 users for 30 minutes"
        echo "  async      - Focus on async endpoints (50 users, 10 min)"
        echo "  sync       - Focus on sync endpoints (20 users, 10 min)"
        echo "  full       - Run all tests sequentially"
        echo "  web        - Start Locust web UI (interactive mode)"
        echo "  custom     - Custom test (requires: users spawn_rate run_time [user_class])"
        echo ""
        echo "Examples:"
        echo "  $0 smoke"
        echo "  $0 load"
        echo "  $0 custom 25 5 10m AsyncSimulationUser"
        echo "  $0 web"
        echo ""
        echo "Environment variables:"
        echo "  HOST       - Application host (default: http://localhost:8000)"
        echo ""
        exit 1
        ;;
esac

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo -e "${GREEN}Results saved to: $RESULTS_DIR${NC}"
echo -e "${GREEN}========================================${NC}"
