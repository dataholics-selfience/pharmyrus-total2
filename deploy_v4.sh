#!/bin/bash

# Pharmyrus v4.0 - Automated Deployment Script
# Usage: ./deploy_v4.sh [local|railway|rollback]

set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "main_v4.py" ]; then
    print_error "main_v4.py not found! Are you in the right directory?"
    exit 1
fi

MODE=${1:-local}

case $MODE in
    local)
        print_header "DEPLOYING v4.0 LOCALLY"
        
        # Backup v3
        if [ -f "main.py" ] && [ ! -f "main_v3_backup.py" ]; then
            print_info "Backing up v3..."
            cp main.py main_v3_backup.py
            cp requirements.txt requirements_v3_backup.txt
            print_success "v3 backed up"
        fi
        
        # Deploy v4
        print_info "Deploying v4..."
        cp main_v4.py main.py
        cp requirements_v4.txt requirements.txt
        print_success "v4 deployed"
        
        # Install dependencies
        print_info "Installing dependencies..."
        pip install -r requirements.txt --quiet
        print_success "Dependencies installed"
        
        # Start server
        print_header "STARTING SERVER"
        print_info "API will be available at: http://localhost:8000"
        print_info "Press Ctrl+C to stop"
        python main.py
        ;;
    
    railway)
        print_header "DEPLOYING v4.0 TO RAILWAY"
        
        # Check git status
        if ! git diff --quiet; then
            print_warning "You have uncommitted changes"
            read -p "Continue? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_error "Deployment cancelled"
                exit 1
            fi
        fi
        
        # Backup v3
        if [ -f "main.py" ] && [ ! -f "main_v3_backup.py" ]; then
            print_info "Backing up v3..."
            cp main.py main_v3_backup.py
            cp requirements.txt requirements_v3_backup.txt
            git add main_v3_backup.py requirements_v3_backup.txt
            print_success "v3 backed up"
        fi
        
        # Deploy v4
        print_info "Deploying v4..."
        cp main_v4.py main.py
        cp requirements_v4.txt requirements.txt
        print_success "v4 files ready"
        
        # Git operations
        print_info "Committing changes..."
        git add main.py requirements.txt
        git commit -m "Deploy v4.0 - Multi-strategy crawling with full debug and stats"
        print_success "Changes committed"
        
        # Push
        print_info "Pushing to Railway..."
        git push origin main
        print_success "Pushed to Railway"
        
        print_header "DEPLOYMENT COMPLETE"
        print_info "Railway will auto-deploy in ~2 minutes"
        print_info "Monitor at: https://railway.app/project/YOUR_PROJECT"
        print_warning "Test the API before rolling back!"
        ;;
    
    rollback)
        print_header "ROLLING BACK TO v3.0"
        
        if [ ! -f "main_v3_backup.py" ]; then
            print_error "No v3 backup found! Cannot rollback."
            exit 1
        fi
        
        print_warning "This will restore v3.0"
        read -p "Are you sure? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Rollback cancelled"
            exit 1
        fi
        
        # Restore v3
        print_info "Restoring v3..."
        cp main_v3_backup.py main.py
        cp requirements_v3_backup.txt requirements.txt
        print_success "v3 restored"
        
        # Git operations (if railway)
        read -p "Push to Railway? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Committing rollback..."
            git add main.py requirements.txt
            git commit -m "Rollback to v3.0"
            
            print_info "Pushing to Railway..."
            git push origin main
            print_success "Rollback deployed"
        fi
        
        print_header "ROLLBACK COMPLETE"
        print_info "v3.0 is now active"
        ;;
    
    test)
        print_header "RUNNING AUTOMATED TESTS"
        
        if [ ! -f "main.py" ]; then
            print_error "main.py not found! Deploy first."
            exit 1
        fi
        
        # Check if API is running
        print_info "Checking if API is running..."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "API is running"
        else
            print_warning "API is not running. Starting..."
            python main.py &
            API_PID=$!
            sleep 5
        fi
        
        # Run tests
        print_info "Running test suite..."
        python3 test_api.py
        
        # Stop API if we started it
        if [ ! -z "$API_PID" ]; then
            kill $API_PID
        fi
        ;;
    
    compare)
        print_header "COMPARING v3 vs v4 RESPONSES"
        
        MOLECULE=${2:-Darolutamide}
        
        # Start v3
        print_info "Testing v3..."
        if [ -f "main_v3_backup.py" ]; then
            cp main_v3_backup.py main.py
            python main.py &
            V3_PID=$!
            sleep 3
            
            curl -s "http://localhost:8000/api/v1/search?molecule_name=$MOLECULE" | jq '.' > v3_result.json
            kill $V3_PID
            print_success "v3 tested"
        else
            print_warning "No v3 backup, skipping"
        fi
        
        # Start v4
        print_info "Testing v4..."
        cp main_v4.py main.py
        python main.py &
        V4_PID=$!
        sleep 3
        
        curl -s "http://localhost:8000/api/v1/search?molecule_name=$MOLECULE" | jq '.' > v4_result.json
        kill $V4_PID
        print_success "v4 tested"
        
        # Compare
        print_header "COMPARISON RESULTS"
        
        if [ -f "v3_result.json" ]; then
            V3_BRS=$(jq -r '.search_result.total_br_from_epo // 0' v3_result.json)
            print_info "v3 BRs found: $V3_BRS"
        fi
        
        V4_BRS=$(jq -r '.br_patents.total // 0' v4_result.json)
        V4_MATCH=$(jq -r '.comparison.match_rate // "0%"' v4_result.json)
        V4_STATUS=$(jq -r '.comparison.status // "unknown"' v4_result.json)
        
        print_info "v4 BRs found: $V4_BRS"
        print_info "v4 Match rate: $V4_MATCH"
        print_info "v4 Status: $V4_STATUS"
        
        print_success "Results saved to v3_result.json and v4_result.json"
        ;;
    
    *)
        print_error "Unknown mode: $MODE"
        echo ""
        echo "Usage: $0 [local|railway|rollback|test|compare]"
        echo ""
        echo "Modes:"
        echo "  local     - Deploy v4 locally and start server"
        echo "  railway   - Deploy v4 to Railway (git push)"
        echo "  rollback  - Restore v3 from backup"
        echo "  test      - Run automated test suite"
        echo "  compare   - Compare v3 vs v4 results"
        echo ""
        exit 1
        ;;
esac
