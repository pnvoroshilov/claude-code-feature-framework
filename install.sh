#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${CYAN}======================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}======================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check version
check_version() {
    local cmd=$1
    local min_version=$2
    local current_version=$($cmd 2>&1 | head -n1 | grep -oE '[0-9]+\.[0-9]+' | head -n1)

    if [[ -z "$current_version" ]]; then
        return 1
    fi

    # Simple version comparison
    if awk "BEGIN {exit !($current_version >= $min_version)}"; then
        return 0
    else
        return 1
    fi
}

# Install Python on macOS
install_python_mac() {
    print_status "Installing Python via Homebrew..."

    if ! command_exists brew; then
        print_status "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    brew install python@3.11
    print_success "Python installed"
}

# Install Python on Linux
install_python_linux() {
    print_status "Installing Python..."

    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip
    elif command_exists dnf; then
        sudo dnf install -y python3 python3-pip
    else
        print_error "Cannot detect package manager. Please install Python 3.8+ manually."
        exit 1
    fi

    print_success "Python installed"
}

# Install Node.js on macOS
install_node_mac() {
    print_status "Installing Node.js via Homebrew..."

    if ! command_exists brew; then
        print_status "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    brew install node
    print_success "Node.js installed"
}

# Install Node.js on Linux
install_node_linux() {
    print_status "Installing Node.js..."

    if command_exists apt-get; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command_exists yum; then
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs
    elif command_exists dnf; then
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo dnf install -y nodejs
    else
        print_error "Cannot detect package manager. Please install Node.js 16+ manually."
        exit 1
    fi

    print_success "Node.js installed"
}

# Check and install prerequisites
check_and_install_prerequisites() {
    print_header "Checking Prerequisites"

    local missing_deps=0

    # Check Python
    if ! command_exists python3; then
        print_warning "Python 3 is not installed"

        read -p "Install Python 3 automatically? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [[ "$OS" == "mac" ]]; then
                install_python_mac
            elif [[ "$OS" == "linux" ]]; then
                install_python_linux
            else
                print_error "Automatic installation not supported on $OS"
                print_error "Please install Python 3.8+ manually from https://www.python.org/"
                exit 1
            fi
        else
            print_error "Python 3 is required. Install from https://www.python.org/"
            exit 1
        fi
    else
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python $PYTHON_VERSION found"
    fi

    # Check pip
    if ! command_exists pip3 && ! python3 -m pip --version >/dev/null 2>&1; then
        print_status "Installing pip..."
        if [[ "$OS" == "mac" ]]; then
            python3 -m ensurepip --upgrade
        elif [[ "$OS" == "linux" ]]; then
            if command_exists apt-get; then
                sudo apt-get install -y python3-pip
            elif command_exists yum; then
                sudo yum install -y python3-pip
            fi
        fi
        print_success "pip installed"
    else
        print_success "pip found"
    fi

    # Check Node.js
    if ! command_exists node; then
        print_warning "Node.js is not installed"

        read -p "Install Node.js automatically? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [[ "$OS" == "mac" ]]; then
                install_node_mac
            elif [[ "$OS" == "linux" ]]; then
                install_node_linux
            else
                print_error "Automatic installation not supported on $OS"
                print_error "Please install Node.js 16+ manually from https://nodejs.org/"
                exit 1
            fi
        else
            print_error "Node.js 16+ is required. Install from https://nodejs.org/"
            exit 1
        fi
    else
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $NODE_VERSION -lt 16 ]]; then
            print_error "Node.js version $NODE_VERSION is too old. Requires 16+"
            exit 1
        fi
        print_success "Node.js v$(node --version | cut -d'v' -f2) found"
    fi

    # Check npm
    if ! command_exists npm; then
        print_error "npm is not installed (should come with Node.js)"
        exit 1
    else
        print_success "npm v$(npm --version) found"
    fi

    # Check Git
    if ! command_exists git; then
        print_warning "Git is not installed"

        read -p "Install Git automatically? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [[ "$OS" == "mac" ]]; then
                brew install git
            elif [[ "$OS" == "linux" ]]; then
                if command_exists apt-get; then
                    sudo apt-get install -y git
                elif command_exists yum; then
                    sudo yum install -y git
                elif command_exists dnf; then
                    sudo dnf install -y git
                fi
            fi
            print_success "Git installed"
        else
            print_error "Git is required. Install from https://git-scm.com/"
            exit 1
        fi
    else
        print_success "Git v$(git --version | cut -d' ' -f3) found"
    fi

    echo
    print_success "All prerequisites satisfied!"
    echo
}

# Setup Backend
setup_backend() {
    print_header "Setting Up Backend"

    cd claudetask/backend

    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip

    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt

    print_success "Backend setup complete"

    cd ../..
}

# Setup Frontend
setup_frontend() {
    print_header "Setting Up Frontend"

    cd claudetask/frontend

    # Install dependencies
    print_status "Installing frontend dependencies (this may take a few minutes)..."
    npm install

    print_success "Frontend setup complete"

    cd ../..
}

# Setup MCP Server
setup_mcp_server() {
    print_header "Setting Up MCP Server"

    # Create MCP directory
    MCP_DIR="$HOME/.claudetask_mcp"
    print_status "Installing MCP server to $MCP_DIR..."

    mkdir -p "$MCP_DIR"

    # Copy MCP server files
    cp -r claudetask/mcp_server/* "$MCP_DIR/"

    # Install MCP dependencies
    cd "$MCP_DIR"
    print_status "Installing MCP server dependencies..."
    pip3 install -r requirements.txt

    # Make executable
    chmod +x native_stdio_server.py
    chmod +x claudetask_mcp_bridge.py

    cd - > /dev/null

    print_success "MCP server installed to $MCP_DIR"
}

# Create startup scripts
create_startup_scripts() {
    print_header "Creating Startup Scripts"

    # Backend startup script
    cat > start-backend.sh << 'EOF'
#!/bin/bash

echo "Starting ClaudeTask Backend..."

cd claudetask/backend

# Activate virtual environment
source venv/bin/activate

# Start backend
echo "Backend starting at http://localhost:3333"
echo "API Docs: http://localhost:3333/docs"
echo "Press Ctrl+C to stop"
echo

python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
EOF

    chmod +x start-backend.sh
    print_success "Created start-backend.sh"

    # Frontend startup script
    cat > start-frontend.sh << 'EOF'
#!/bin/bash

echo "Starting ClaudeTask Frontend..."

cd claudetask/frontend

# Start frontend
echo "Frontend starting at http://localhost:3000"
echo "Press Ctrl+C to stop"
echo

REACT_APP_API_URL=http://localhost:3333/api PORT=3000 npm start
EOF

    chmod +x start-frontend.sh
    print_success "Created start-frontend.sh"

    # Combined startup script
    cat > start-claudetask.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Starting ClaudeTask"
echo "=========================================="
echo

# Check if tmux is available
if command -v tmux >/dev/null 2>&1; then
    echo "Starting services in tmux session..."
    echo

    # Create tmux session with 2 panes
    tmux new-session -d -s claudetask
    tmux split-window -h -t claudetask

    # Start backend in first pane
    tmux send-keys -t claudetask:0.0 './start-backend.sh' C-m

    # Start frontend in second pane
    tmux send-keys -t claudetask:0.1 './start-frontend.sh' C-m

    echo "✓ Backend starting at http://localhost:3333"
    echo "✓ Frontend starting at http://localhost:3000"
    echo
    echo "To view services:"
    echo "  tmux attach -t claudetask"
    echo
    echo "To stop services:"
    echo "  ./stop-claudetask.sh"
    echo
else
    echo "tmux not found. Starting services in background..."
    echo

    # Start backend in background
    ./start-backend.sh > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid

    # Wait for backend to start
    sleep 3

    # Start frontend in background
    ./start-frontend.sh > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > .frontend.pid

    echo "✓ Backend started (PID: $BACKEND_PID)"
    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    echo
    echo "Backend: http://localhost:3333"
    echo "Frontend: http://localhost:3000"
    echo
    echo "Logs:"
    echo "  Backend: tail -f backend.log"
    echo "  Frontend: tail -f frontend.log"
    echo
    echo "To stop:"
    echo "  ./stop-claudetask.sh"
    echo
fi
EOF

    chmod +x start-claudetask.sh
    print_success "Created start-claudetask.sh"

    # Stop script
    cat > stop-claudetask.sh << 'EOF'
#!/bin/bash

echo "Stopping ClaudeTask..."

# Check if tmux session exists
if command -v tmux >/dev/null 2>&1 && tmux has-session -t claudetask 2>/dev/null; then
    tmux kill-session -t claudetask
    echo "✓ Stopped tmux session"
else
    # Stop processes by PID
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null && echo "✓ Stopped backend (PID: $BACKEND_PID)"
        rm .backend.pid
    fi

    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null && echo "✓ Stopped frontend (PID: $FRONTEND_PID)"
        rm .frontend.pid
    fi

    # Fallback: kill by port
    lsof -ti:3333 | xargs kill -9 2>/dev/null && echo "✓ Killed process on port 3333"
    lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✓ Killed process on port 3000"
fi

echo "ClaudeTask stopped."
EOF

    chmod +x stop-claudetask.sh
    print_success "Created stop-claudetask.sh"
}

# Test services
test_services() {
    print_header "Testing Services"

    # Start backend in background
    print_status "Starting backend..."
    cd claudetask/backend
    source venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 &
    BACKEND_PID=$!
    cd ../..

    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -f http://localhost:3333/health >/dev/null 2>&1; then
            print_success "Backend is responding"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start"
            kill $BACKEND_PID 2>/dev/null
            exit 1
        fi
        sleep 1
    done

    # Stop backend
    kill $BACKEND_PID 2>/dev/null
    sleep 2

    print_success "Services test passed"
}

# Print final instructions
print_final_instructions() {
    echo
    print_header "Installation Complete!"
    echo
    echo -e "${GREEN}✓ Backend installed${NC} (claudetask/backend)"
    echo -e "${GREEN}✓ Frontend installed${NC} (claudetask/frontend)"
    echo -e "${GREEN}✓ MCP Server installed${NC} (~/.claudetask_mcp)"
    echo
    echo -e "${CYAN}Next Steps:${NC}"
    echo
    echo "1. Start ClaudeTask:"
    echo -e "   ${YELLOW}./start-claudetask.sh${NC}"
    echo
    echo "2. Open in browser:"
    echo -e "   Frontend: ${YELLOW}http://localhost:3000${NC}"
    echo -e "   API Docs: ${YELLOW}http://localhost:3333/docs${NC}"
    echo
    echo "3. Initialize your first project:"
    echo "   - Click on 'Project Setup' in the sidebar"
    echo "   - Enter your project name and path"
    echo "   - Click 'Initialize Project'"
    echo
    echo "4. Configure Claude Code:"
    echo "   - Restart Claude Code in your project directory"
    echo "   - MCP tools will be available automatically"
    echo
    echo -e "${CYAN}Commands:${NC}"
    echo -e "  Start all:  ${YELLOW}./start-claudetask.sh${NC}"
    echo -e "  Stop all:   ${YELLOW}./stop-claudetask.sh${NC}"
    echo -e "  Backend:    ${YELLOW}./start-backend.sh${NC}"
    echo -e "  Frontend:   ${YELLOW}./start-frontend.sh${NC}"
    echo
    echo -e "${CYAN}Documentation:${NC}"
    echo "  README: https://github.com/pnvoroshilov/claude-code-feature-framework"
    echo
}

# Main installation function
main() {
    print_header "ClaudeTask Installation"
    echo
    echo "This script will:"
    echo "  1. Check and install prerequisites (Python, Node.js, Git)"
    echo "  2. Setup backend with Python virtual environment"
    echo "  3. Setup frontend with npm"
    echo "  4. Install MCP server globally"
    echo "  5. Create startup scripts"
    echo

    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi

    echo

    # Run installation steps
    check_and_install_prerequisites
    setup_backend
    setup_frontend
    setup_mcp_server
    create_startup_scripts
    test_services

    print_final_instructions
}

# Run main function
main "$@"
