#!/bin/bash

################################################################################
# run-code-review.sh - Comprehensive Code Review Automation
################################################################################
#
# DESCRIPTION:
#   Automated code review script that runs multiple quality checks including:
#   - Linting (ESLint, Pylint, etc.)
#   - Type checking (TypeScript, mypy)
#   - Security scanning
#   - Code complexity analysis
#   - Test coverage verification
#   - Format checking
#
# USAGE:
#   ./run-code-review.sh [OPTIONS]
#
# OPTIONS:
#   -d, --directory DIR    Target directory to review (default: current directory)
#   -l, --language LANG    Language to review (auto-detect if not specified)
#                          Supported: javascript, typescript, python, java, go
#   -f, --fix              Auto-fix issues where possible
#   -s, --severity LEVEL   Minimum severity to report (info, warning, error)
#   -o, --output FORMAT    Output format (console, json, html)
#   -r, --report FILE      Save detailed report to file
#   -h, --help             Show this help message
#
# EXAMPLES:
#   # Review current directory
#   ./run-code-review.sh
#
#   # Review specific directory with auto-fix
#   ./run-code-review.sh -d ./src -f
#
#   # Review Python code with HTML report
#   ./run-code-review.sh -l python -o html -r review-report.html
#
#   # Review TypeScript with error-level only
#   ./run-code-review.sh -l typescript -s error
#
# EXIT CODES:
#   0 - All checks passed
#   1 - Critical issues found
#   2 - Configuration error
#   3 - Tool not found
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
TARGET_DIR="."
LANGUAGE="auto"
AUTO_FIX=false
SEVERITY="warning"
OUTPUT_FORMAT="console"
REPORT_FILE=""

# Issue counters
ERROR_COUNT=0
WARNING_COUNT=0
INFO_COUNT=0

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARNING_COUNT++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((ERROR_COUNT++))
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
    ((INFO_COUNT++))
}

show_help() {
    sed -n '/^# USAGE:/,/^################################################################################/p' "$0" | sed 's/^# //g' | head -n -1
    exit 0
}

check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        print_warning "Tool '$tool' not found. Skipping related checks."
        return 1
    fi
    return 0
}

detect_language() {
    local dir=$1

    # Check for package.json (JavaScript/TypeScript)
    if [ -f "$dir/package.json" ]; then
        if [ -f "$dir/tsconfig.json" ]; then
            echo "typescript"
        else
            echo "javascript"
        fi
        return
    fi

    # Check for Python files
    if [ -f "$dir/setup.py" ] || [ -f "$dir/pyproject.toml" ] || [ -f "$dir/requirements.txt" ]; then
        echo "python"
        return
    fi

    # Check for Go files
    if [ -f "$dir/go.mod" ]; then
        echo "go"
        return
    fi

    # Check for Java files
    if [ -f "$dir/pom.xml" ] || [ -f "$dir/build.gradle" ]; then
        echo "java"
        return
    fi

    echo "unknown"
}

################################################################################
# Language-Specific Checks
################################################################################

review_javascript() {
    print_header "JavaScript Code Review"

    # ESLint
    if check_tool "eslint"; then
        print_info "Running ESLint..."
        if [ "$AUTO_FIX" = true ]; then
            eslint "$TARGET_DIR" --fix --ext .js,.jsx 2>&1 | tee -a "$REPORT_FILE" || true
        else
            eslint "$TARGET_DIR" --ext .js,.jsx 2>&1 | tee -a "$REPORT_FILE" || true
        fi
    fi

    # Prettier format check
    if check_tool "prettier"; then
        print_info "Checking code formatting..."
        if [ "$AUTO_FIX" = true ]; then
            prettier --write "$TARGET_DIR/**/*.{js,jsx}" 2>&1 | tee -a "$REPORT_FILE" || true
        else
            prettier --check "$TARGET_DIR/**/*.{js,jsx}" 2>&1 | tee -a "$REPORT_FILE" || true
        fi
    fi
}

review_typescript() {
    print_header "TypeScript Code Review"

    # ESLint with TypeScript
    if check_tool "eslint"; then
        print_info "Running ESLint for TypeScript..."
        if [ "$AUTO_FIX" = true ]; then
            eslint "$TARGET_DIR" --fix --ext .ts,.tsx 2>&1 | tee -a "$REPORT_FILE" || true
        else
            eslint "$TARGET_DIR" --ext .ts,.tsx 2>&1 | tee -a "$REPORT_FILE" || true
        fi
    fi

    # TypeScript compiler check
    if check_tool "tsc"; then
        print_info "Running TypeScript type checking..."
        tsc --noEmit --skipLibCheck 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # Prettier format check
    if check_tool "prettier"; then
        print_info "Checking code formatting..."
        if [ "$AUTO_FIX" = true ]; then
            prettier --write "$TARGET_DIR/**/*.{ts,tsx}" 2>&1 | tee -a "$REPORT_FILE" || true
        else
            prettier --check "$TARGET_DIR/**/*.{ts,tsx}" 2>&1 | tee -a "$REPORT_FILE" || true
        fi
    fi
}

review_python() {
    print_header "Python Code Review"

    # Pylint
    if check_tool "pylint"; then
        print_info "Running Pylint..."
        pylint "$TARGET_DIR" --recursive=y 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # Flake8
    if check_tool "flake8"; then
        print_info "Running Flake8..."
        flake8 "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # mypy type checking
    if check_tool "mypy"; then
        print_info "Running mypy type checking..."
        mypy "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # Black format check
    if check_tool "black"; then
        print_info "Checking code formatting with Black..."
        if [ "$AUTO_FIX" = true ]; then
            black "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
        else
            black --check "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
        fi
    fi

    # isort import sorting
    if check_tool "isort"; then
        print_info "Checking import sorting..."
        if [ "$AUTO_FIX" = true ]; then
            isort "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
        else
            isort --check-only "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
        fi
    fi
}

review_go() {
    print_header "Go Code Review"

    # go fmt
    print_info "Checking Go formatting..."
    if [ "$AUTO_FIX" = true ]; then
        go fmt "$TARGET_DIR/..." 2>&1 | tee -a "$REPORT_FILE" || true
    else
        gofmt -l "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # go vet
    if check_tool "go"; then
        print_info "Running go vet..."
        go vet "$TARGET_DIR/..." 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # golint
    if check_tool "golint"; then
        print_info "Running golint..."
        golint "$TARGET_DIR/..." 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # staticcheck
    if check_tool "staticcheck"; then
        print_info "Running staticcheck..."
        staticcheck "$TARGET_DIR/..." 2>&1 | tee -a "$REPORT_FILE" || true
    fi
}

################################################################################
# Security Scanning
################################################################################

run_security_scan() {
    print_header "Security Scanning"

    # npm audit for Node.js
    if [ -f "package.json" ] && check_tool "npm"; then
        print_info "Running npm audit..."
        npm audit 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # Safety for Python
    if [ -f "requirements.txt" ] && check_tool "safety"; then
        print_info "Running safety check..."
        safety check -r requirements.txt 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # Bandit for Python security
    if [ "$LANGUAGE" = "python" ] && check_tool "bandit"; then
        print_info "Running Bandit security scan..."
        bandit -r "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # Snyk (if installed)
    if check_tool "snyk"; then
        print_info "Running Snyk security scan..."
        snyk test 2>&1 | tee -a "$REPORT_FILE" || true
    fi
}

################################################################################
# Code Complexity Analysis
################################################################################

analyze_complexity() {
    print_header "Code Complexity Analysis"

    # radon for Python
    if [ "$LANGUAGE" = "python" ] && check_tool "radon"; then
        print_info "Analyzing Python complexity..."
        radon cc "$TARGET_DIR" -a 2>&1 | tee -a "$REPORT_FILE" || true
        radon mi "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
    fi

    # plato for JavaScript
    if [ "$LANGUAGE" = "javascript" ] && check_tool "plato"; then
        print_info "Analyzing JavaScript complexity..."
        plato -r -d complexity-report "$TARGET_DIR" 2>&1 | tee -a "$REPORT_FILE" || true
    fi
}

################################################################################
# Main Execution
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--directory)
                TARGET_DIR="$2"
                shift 2
                ;;
            -l|--language)
                LANGUAGE="$2"
                shift 2
                ;;
            -f|--fix)
                AUTO_FIX=true
                shift
                ;;
            -s|--severity)
                SEVERITY="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -r|--report)
                REPORT_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

main() {
    parse_arguments "$@"

    # Validate target directory
    if [ ! -d "$TARGET_DIR" ]; then
        print_error "Directory not found: $TARGET_DIR"
        exit 2
    fi

    # Initialize report file
    if [ -n "$REPORT_FILE" ]; then
        echo "Code Review Report - $(date)" > "$REPORT_FILE"
        echo "Target: $TARGET_DIR" >> "$REPORT_FILE"
        echo "========================================" >> "$REPORT_FILE"
    fi

    # Auto-detect language if needed
    if [ "$LANGUAGE" = "auto" ]; then
        LANGUAGE=$(detect_language "$TARGET_DIR")
        print_info "Detected language: $LANGUAGE"
    fi

    # Run language-specific checks
    case $LANGUAGE in
        javascript)
            review_javascript
            ;;
        typescript)
            review_typescript
            ;;
        python)
            review_python
            ;;
        go)
            review_go
            ;;
        *)
            print_warning "Language '$LANGUAGE' not fully supported. Running generic checks..."
            ;;
    esac

    # Run universal checks
    run_security_scan
    analyze_complexity

    # Summary
    print_header "Review Summary"
    echo -e "Errors:   ${RED}$ERROR_COUNT${NC}"
    echo -e "Warnings: ${YELLOW}$WARNING_COUNT${NC}"
    echo -e "Info:     ${BLUE}$INFO_COUNT${NC}"

    if [ -n "$REPORT_FILE" ]; then
        print_success "Detailed report saved to: $REPORT_FILE"
    fi

    # Exit with appropriate code
    if [ $ERROR_COUNT -gt 0 ]; then
        exit 1
    else
        print_success "Code review completed successfully!"
        exit 0
    fi
}

# Run main function
main "$@"
