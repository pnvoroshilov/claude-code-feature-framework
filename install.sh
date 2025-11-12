#!/bin/bash

###############################################################################
# ClaudeTask Framework - One-Command Installer
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  🚀 ClaudeTask Framework Installer                       ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_requirements() {
    log_info "Checking system requirements..."
    
    command -v python3 >/dev/null 2>&1 && log_success "Python 3 found" || { log_error "Python 3 not found"; exit 1; }
    command -v node >/dev/null 2>&1 && log_success "Node.js found" || { log_error "Node.js not found"; exit 1; }
    command -v npm >/dev/null 2>&1 && log_success "npm found" || { log_error "npm not found"; exit 1; }
    
    log_success "All requirements satisfied!"
}

install_backend() {
    log_info "Installing backend..."
    cd claudetask/backend
    
    [ ! -d "venv" ] && python3 -m venv venv && log_success "Venv created"
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    log_success "Backend installed"
    
    python migrations/migrate_add_custom_instructions.py 2>/dev/null || true
    deactivate
    cd ../..
}

install_mcp_server() {
    log_info "Installing MCP server..."
    cd claudetask/mcp_server
    
    [ ! -d "venv" ] && python3 -m venv venv && log_success "MCP venv created"
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -e . > /dev/null 2>&1
    log_success "MCP server installed"
    
    deactivate
    cd ../..
}

install_frontend() {
    log_info "Installing frontend..."
    cd claudetask/frontend
    npm install > /dev/null 2>&1
    log_success "Frontend installed"
    cd ../..
}

create_scripts() {
    log_info "Creating scripts..."
    
    mkdir -p logs
    
    # Start script
    cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ClaudeTask Framework..."

cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID $MCP_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

cd claudetask/backend && source venv/bin/activate && python -m uvicorn app.main:app --port 3333 > ../../logs/backend.log 2>&1 & BACKEND_PID=$!
cd ../..
sleep 2

cd claudetask/mcp_server && source venv/bin/activate && python -m claudetask_mcp.server > ../../logs/mcp.log 2>&1 & MCP_PID=$!
cd ../..
sleep 2

cd claudetask/frontend && PORT=3334 npm start > ../../logs/frontend.log 2>&1 & FRONTEND_PID=$!
cd ../..

echo ""
echo "✓ Running!"
echo "  📊 Frontend:  http://localhost:3334"
echo "  🔌 Backend:   http://localhost:3333"
echo ""
echo "Press Ctrl+C to stop"
wait
EOF
    
    # Stop script
    cat > stop.sh << 'EOF'
#!/bin/bash
echo "Stopping ClaudeTask Framework..."
lsof -ti:3333 | xargs kill -9 2>/dev/null && echo "✓ Backend stopped"
lsof -ti:3334 | xargs kill -9 2>/dev/null && echo "✓ Frontend stopped"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✓ MCP stopped"
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "claudetask_mcp" 2>/dev/null
echo "All services stopped"
EOF
    
    chmod +x start.sh stop.sh
    log_success "Scripts created"
}

main() {
    print_header
    
    [ ! -d "claudetask" ] && { log_error "Run from framework root directory"; exit 1; }
    
    check_requirements
    echo ""
    
    install_backend
    echo ""
    
    install_mcp_server
    echo ""
    
    install_frontend
    echo ""
    
    create_scripts
    echo ""
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ✓ Installation Complete!                                 ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🚀 Quick Start:"
    echo "  ./start.sh     - Start all services"
    echo "  ./stop.sh      - Stop all services"
    echo ""
}

main
