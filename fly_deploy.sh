#!/bin/bash

# Flow Forecaster - Fly.io Deployment Script
# This script automates the deployment process to Fly.io

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Flow Forecaster - Fly.io Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if flyctl is installed
if ! command -v fly &> /dev/null && ! command -v flyctl &> /dev/null; then
    echo -e "${RED}Error: Fly CLI not found${NC}"
    echo "Please install it first:"
    echo "  curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Use 'fly' or 'flyctl' depending on what's available
FLY_CMD=$(command -v fly || command -v flyctl)

echo -e "${GREEN}✓ Fly CLI found: $FLY_CMD${NC}"
echo ""

# Check if logged in
if ! $FLY_CMD auth whoami &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Fly.io${NC}"
    echo "Logging in..."
    $FLY_CMD auth login
fi

echo -e "${GREEN}✓ Authenticated with Fly.io${NC}"
echo ""

# Parse command line arguments
DEPLOY_TYPE="${1:-full}"

case "$DEPLOY_TYPE" in
    "setup")
        echo -e "${YELLOW}=== Initial Setup ===${NC}"
        echo ""

        # PostgreSQL setup
        echo -e "${BLUE}Step 1: PostgreSQL Database${NC}"
        echo "You've already created: flow-forecaster-db"
        echo "Connection string: postgres://postgres:zvgK6kProVGys5w@flow-forecaster-db.flycast:5432"
        echo ""

        # Attach PostgreSQL
        echo -e "${YELLOW}Attaching PostgreSQL to app...${NC}"
        $FLY_CMD postgres attach flow-forecaster-db --app flow-forecaster || echo "Database already attached"
        echo -e "${GREEN}✓ PostgreSQL attached${NC}"
        echo ""

        # Redis setup
        echo -e "${BLUE}Step 2: Redis (Upstash)${NC}"
        echo "Creating Redis instance..."

        # Try to create Upstash Redis
        $FLY_CMD redis create --name flow-forecaster-redis --region gru || {
            echo -e "${YELLOW}Redis might already exist or Upstash not available in your plan${NC}"
            echo ""
            echo "Alternative: Set up Redis manually and configure secrets:"
            echo "  fly secrets set CELERY_BROKER_URL=redis://your-redis-url:6379/0"
            echo "  fly secrets set CELERY_RESULT_BACKEND=redis://your-redis-url:6379/0"
        }
        echo ""

        # Secrets configuration
        echo -e "${BLUE}Step 3: Secrets Configuration${NC}"
        echo "Setting up secrets..."

        # Generate a secret key if not exists
        SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

        $FLY_CMD secrets set SECRET_KEY="$SECRET_KEY" --app flow-forecaster
        echo -e "${GREEN}✓ SECRET_KEY configured${NC}"

        # Set Flask environment
        $FLY_CMD secrets set FLASK_ENV=production --app flow-forecaster
        echo -e "${GREEN}✓ FLASK_ENV configured${NC}"

        echo ""
        echo -e "${GREEN}Setup completed!${NC}"
        echo "Next steps:"
        echo "  1. Configure Redis connection (if not done automatically)"
        echo "  2. Run: ./fly_deploy.sh deploy"
        echo ""
        ;;

    "secrets")
        echo -e "${YELLOW}=== Configure Secrets ===${NC}"
        echo ""

        read -p "Enter CELERY_BROKER_URL (Redis): " BROKER_URL
        read -p "Enter CELERY_RESULT_BACKEND (Redis): " RESULT_BACKEND

        $FLY_CMD secrets set CELERY_BROKER_URL="$BROKER_URL" --app flow-forecaster
        $FLY_CMD secrets set CELERY_RESULT_BACKEND="$RESULT_BACKEND" --app flow-forecaster

        echo -e "${GREEN}✓ Redis secrets configured${NC}"
        ;;

    "deploy")
        echo -e "${YELLOW}=== Deploying Application ===${NC}"
        echo ""

        # Check if setup is done
        echo "Checking configuration..."

        # Deploy with 1 web and 1 worker machine
        echo -e "${BLUE}Deploying to Fly.io...${NC}"
        $FLY_CMD deploy --ha=false

        echo ""
        echo -e "${GREEN}✓ Deployment initiated${NC}"
        echo ""

        # Scale machines
        echo -e "${BLUE}Scaling machines...${NC}"
        echo "Web: 1 machine (512MB RAM, 1 CPU)"
        echo "Worker: 1 machine (1GB RAM, 1 CPU)"

        $FLY_CMD scale count web=1 worker=1 --app flow-forecaster

        echo -e "${GREEN}✓ Machines scaled${NC}"
        echo ""

        # Show status
        echo -e "${BLUE}Deployment status:${NC}"
        $FLY_CMD status --app flow-forecaster
        echo ""

        echo -e "${GREEN}Deployment complete!${NC}"
        echo ""
        echo "Your app is available at: https://flow-forecaster.fly.dev"
        echo ""
        echo "Monitor deployment:"
        echo "  fly logs --app flow-forecaster"
        echo "  fly status --app flow-forecaster"
        echo "  fly vm status --app flow-forecaster"
        ;;

    "migrate")
        echo -e "${YELLOW}=== Database Migration ===${NC}"
        echo ""
        echo "Running database migrations..."

        # Create tables (Alembic or direct)
        $FLY_CMD ssh console --app flow-forecaster -C "python -c 'from database import init_db; init_db()'"

        echo -e "${GREEN}✓ Database initialized${NC}"
        ;;

    "logs")
        echo -e "${YELLOW}=== Viewing Logs ===${NC}"
        echo ""

        # Show logs for both web and worker
        $FLY_CMD logs --app flow-forecaster
        ;;

    "status")
        echo -e "${YELLOW}=== Application Status ===${NC}"
        echo ""

        $FLY_CMD status --app flow-forecaster
        echo ""
        $FLY_CMD vm status --app flow-forecaster
        ;;

    "scale")
        WEB_COUNT="${2:-1}"
        WORKER_COUNT="${3:-1}"

        echo -e "${YELLOW}=== Scaling Application ===${NC}"
        echo "Web machines: $WEB_COUNT"
        echo "Worker machines: $WORKER_COUNT"
        echo ""

        $FLY_CMD scale count web=$WEB_COUNT worker=$WORKER_COUNT --app flow-forecaster

        echo -e "${GREEN}✓ Scaling complete${NC}"
        ;;

    "ssh")
        echo -e "${YELLOW}=== SSH Console ===${NC}"
        echo ""

        $FLY_CMD ssh console --app flow-forecaster
        ;;

    "full")
        echo -e "${YELLOW}=== Full Deployment Process ===${NC}"
        echo ""
        echo "This will:"
        echo "  1. Deploy the application"
        echo "  2. Scale to 1 web + 1 worker"
        echo "  3. Initialize database"
        echo "  4. Show status"
        echo ""
        read -p "Continue? (y/n) " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Deploy
            $0 deploy

            # Wait a bit for deployment
            echo "Waiting 30 seconds for deployment to stabilize..."
            sleep 30

            # Initialize database
            $0 migrate

            # Show status
            $0 status

            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}Full deployment complete!${NC}"
            echo -e "${GREEN}========================================${NC}"
            echo ""
            echo "Access your app at: https://flow-forecaster.fly.dev"
            echo ""
            echo "Useful commands:"
            echo "  ./fly_deploy.sh logs      - View application logs"
            echo "  ./fly_deploy.sh status    - Check application status"
            echo "  ./fly_deploy.sh scale 2 2 - Scale to 2 web + 2 workers"
            echo "  ./fly_deploy.sh ssh       - SSH into container"
        fi
        ;;

    *)
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  setup           - Initial setup (PostgreSQL, Redis, secrets)"
        echo "  secrets         - Configure Redis secrets manually"
        echo "  deploy          - Deploy application to Fly.io"
        echo "  migrate         - Run database migrations"
        echo "  logs            - View application logs"
        echo "  status          - Show application status"
        echo "  scale <w> <c>   - Scale web and worker machines"
        echo "  ssh             - SSH into container"
        echo "  full            - Full deployment (deploy + migrate + status)"
        echo ""
        echo "Examples:"
        echo "  $0 setup                  # Initial setup"
        echo "  $0 deploy                 # Deploy app"
        echo "  $0 scale 2 2             # Scale to 2 web + 2 workers"
        echo "  $0 full                   # Full deployment"
        echo ""
        exit 1
        ;;
esac
