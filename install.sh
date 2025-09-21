#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check for Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check for Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check for Python (for MCP server)
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check for pip
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    print_success "All prerequisites are available"
}

# Install MCP server globally
install_mcp_server() {
    print_status "Installing ClaudeTask MCP server..."
    
    # Create MCP server directory
    MCP_DIR="$HOME/.claudetask_mcp"
    mkdir -p "$MCP_DIR"
    
    # Copy MCP server files
    cp -r claudetask/mcp_server/* "$MCP_DIR/"
    
    # Install dependencies
    cd "$MCP_DIR"
    pip3 install -r requirements.txt
    
    # Make executable
    chmod +x claudetask_mcp_bridge.py
    
    # Create symlink in PATH
    sudo ln -sf "$MCP_DIR/claudetask_mcp_bridge.py" /usr/local/bin/claudetask-mcp
    
    print_success "MCP server installed successfully"
}

# Setup Docker environment
setup_docker() {
    print_status "Setting up Docker environment..."
    
    # Create data directory
    mkdir -p ./data
    
    # Build and start services
    if command_exists docker-compose; then
        docker-compose build
        docker-compose up -d
    else
        docker compose build
        docker compose up -d
    fi
    
    print_success "Docker services started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    for i in {1..30}; do
        if curl -f http://localhost:3333/health >/dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Wait for frontend
    for i in {1..30}; do
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Frontend failed to start"
            exit 1
        fi
        sleep 2
    done
}

# Create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    cat > start-claudetask.sh << 'EOF'
#!/bin/bash

echo "Starting ClaudeTask..."

# Start Docker services
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose up -d
else
    docker compose up -d
fi

echo "ClaudeTask is starting..."
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:3333"
echo ""
echo "To stop ClaudeTask, run: ./stop-claudetask.sh"
EOF

    chmod +x start-claudetask.sh
    
    # Create stop script
    cat > stop-claudetask.sh << 'EOF'
#!/bin/bash

echo "Stopping ClaudeTask..."

if command -v docker-compose >/dev/null 2>&1; then
    docker-compose down
else
    docker compose down
fi

echo "ClaudeTask stopped."
EOF

    chmod +x stop-claudetask.sh
    
    print_success "Startup scripts created"
}

# Main installation function
main() {
    echo "======================================"
    echo "ClaudeTask Installation Script"
    echo "======================================"
    echo ""
    
    check_prerequisites
    install_mcp_server
    setup_docker
    wait_for_services
    create_startup_script
    
    echo ""
    echo "======================================"
    print_success "ClaudeTask installation completed!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Initialize your first project using the Project Setup page"
    echo "3. Restart Claude Code to load the MCP configuration"
    echo ""
    echo "Commands:"
    echo "  Start:  ./start-claudetask.sh"
    echo "  Stop:   ./stop-claudetask.sh"
    echo ""
    echo "For more information, see the README.md file."
}

# Run main function
main "$@"