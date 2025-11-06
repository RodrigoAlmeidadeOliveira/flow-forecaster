#!/bin/bash

# Quick Migration Script for Fly.io
# Migrates SQLite → PostgreSQL on Fly.io

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SQLite → PostgreSQL Migration (Fly.io)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
if ! command -v fly &> /dev/null; then
    echo -e "${RED}Error: Fly CLI not found${NC}"
    echo "Install it: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)

# PostgreSQL credentials (update with yours)
PG_USER="postgres"
PG_PASS="zvgK6kProVGys5w"
PG_DB="flow_forecaster"
PG_APP="flow-forecaster-db"
LOCAL_PORT="15432"

# SQLite file
SQLITE_FILE="${1:-forecaster.db}"

if [ ! -f "$SQLITE_FILE" ]; then
    echo -e "${RED}Error: SQLite file not found: $SQLITE_FILE${NC}"
    echo "Usage: $0 [sqlite_file]"
    exit 1
fi

echo -e "${YELLOW}Step 1: Backup SQLite${NC}"
BACKUP_FILE="${SQLITE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$SQLITE_FILE" "$BACKUP_FILE"
echo -e "  ${GREEN}✓${NC} Backup created: $BACKUP_FILE"
echo ""

echo -e "${YELLOW}Step 2: Start Fly Proxy${NC}"
echo "  Starting proxy on port $LOCAL_PORT..."
echo "  ${YELLOW}Note: Proxy will run in background${NC}"

# Kill existing proxy if running
pkill -f "fly proxy.*$PG_APP" 2>/dev/null || true
sleep 1

# Start proxy in background
fly proxy $LOCAL_PORT:5432 -a $PG_APP > /tmp/fly_proxy.log 2>&1 &
PROXY_PID=$!
sleep 3

# Check if proxy is running
if ! ps -p $PROXY_PID > /dev/null; then
    echo -e "${RED}  ✗ Proxy failed to start${NC}"
    echo "  Check logs: cat /tmp/fly_proxy.log"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} Proxy started (PID: $PROXY_PID)"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping proxy...${NC}"
    kill $PROXY_PID 2>/dev/null || true
    echo -e "${GREEN}Done${NC}"
}

trap cleanup EXIT

echo -e "${YELLOW}Step 3: Run Migration${NC}"
echo ""

# Set DATABASE_URL
export DATABASE_URL="postgresql://$PG_USER:$PG_PASS@localhost:$LOCAL_PORT/$PG_DB?sslmode=disable"

# Run migration
$PYTHON_CMD migrate_to_postgres.py --sqlite "$SQLITE_FILE"

MIGRATION_STATUS=$?

if [ $MIGRATION_STATUS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Migration Successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Verify data: fly postgres connect -a $PG_APP"
    echo "  2. Deploy app: fly deploy"
    echo "  3. Test: https://flow-forecaster.fly.dev"
    echo ""
    echo "Backup saved at: $BACKUP_FILE"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Migration Failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Your data is safe. Backup: $BACKUP_FILE"
    echo "Check logs and try again"
    exit 1
fi
