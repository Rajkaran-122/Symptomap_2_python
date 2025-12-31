#!/bin/bash

#################################
# SymptoMap Doctor Station
# Quick Start Script (Mac/Linux)
#################################

echo "🚀 Starting SymptoMap Doctor Station..."
echo ""

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3.8 or higher"
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "Please install Node.js 16 or higher"
    echo "Download from: https://nodejs.org/"
    exit 1
fi

# Print versions
echo -e "${BLUE}📦 System Check:${NC}"
echo "  Python: $(python3 --version)"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo ""

# Create necessary directories
mkdir -p backups
mkdir -p export
mkdir -p logs

# Backend setup and start
echo -e "${BLUE}📦 Starting Backend...${NC}"
cd backend-python

# Create virtual environment if doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Start backend in background
echo "  Launching FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Wait for backend to start
echo "  Waiting for backend to initialize..."
sleep 4

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}  ✅ Backend started successfully${NC}"
else
    echo -e "${YELLOW}  ⚠️  Backend may still be starting...${NC}"
fi

# Frontend setup and start
echo ""
echo -e "${BLUE}🎨 Starting Frontend...${NC}"
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "  Installing Node.js dependencies..."
    npm install --silent
fi

# Start frontend in background
echo "  Launching React development server..."
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to start
echo "  Waiting for frontend to initialize..."
sleep 5

# Final status
echo ""
echo -e "${GREEN}✅ Doctor Station Started Successfully!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo""
echo -e "${BLUE}📍 Access URLs:${NC}"
echo "  🏥 Doctor Portal:  http://localhost:3000/doctor"
echo "  📊 Dashboard:      http://localhost:3000/dashboard"
echo "  📚 API Docs:       http://localhost:8000/api/docs"
echo ""
echo -e "${BLUE}🔑 Login Credentials:${NC}"
echo "  Password: Doctor@SymptoMap2025"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  • Backend logs: tail -f logs/backend.log"
echo "  • Frontend logs: tail -f logs/frontend.log"
echo "  • Stop services: Press Ctrl+C"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Save PIDs to file for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    # Kill backend
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    # Kill frontend
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    # Extra cleanup
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running
wait
