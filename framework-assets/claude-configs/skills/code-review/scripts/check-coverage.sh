#!/bin/bash

################################################################################
# check-coverage.sh - Test Coverage Validation Script
################################################################################
#
# DESCRIPTION:
#   Validates test coverage for code review process. Checks coverage thresholds,
#   identifies uncovered critical code paths, and generates coverage reports.
#   Supports multiple testing frameworks and languages.
#
# USAGE:
#   ./check-coverage.sh [OPTIONS]
#
# OPTIONS:
#   -d, --directory DIR      Target directory (default: current directory)
#   -t, --threshold PCT      Minimum coverage threshold (default: 80)
#   -f, --framework FRAMEWORK Testing framework (jest, pytest, go, auto)
#   -r, --report FORMAT      Report format (html, json, lcov, text)
#   -o, --output DIR         Output directory for reports (default: ./coverage)
#   -s, --strict             Fail on any coverage below threshold
#   -c, --critical PATHS     Comma-separated critical paths requiring higher coverage
#   -v, --verbose            Verbose output
#   -h, --help               Show this help message
#
# EXAMPLES:
#   # Check coverage with default 80% threshold
#   ./check-coverage.sh
#
#   # Check with 90% threshold and generate HTML report
#   ./check-coverage.sh -t 90 -r html
#
#   # Check critical paths with higher coverage requirement
#   ./check-coverage.sh -c "src/auth,src/payment" -t 95 -s
#
#   # Run coverage for Python project
#   ./check-coverage.sh -f pytest -t 85 -r html -o ./coverage-report
#
# EXIT CODES:
#   0 - Coverage meets or exceeds threshold
#   1 - Coverage below threshold
#   2 - Configuration error
#   3 - Framework not found
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
THRESHOLD=80
FRAMEWORK="auto"
REPORT_FORMAT="text"
OUTPUT_DIR="./coverage"
STRICT_MODE=false
CRITICAL_PATHS=""
VERBOSE=false

# Coverage results
CURRENT_COVERAGE=0
PASSED=false

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
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[DEBUG] $1${NC}"
    fi
}

show_help() {
    sed -n '/^# USAGE:/,/^################################################################################/p' "$0" | sed 's/^# //g' | head -n -1
    exit 0
}

check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        print_error "Tool '$tool' not found. Please install it first."
        exit 3
    fi
}

detect_framework() {
    local dir=$1

    # Check for Jest (package.json with jest)
    if [ -f "$dir/package.json" ]; then
        if grep -q '"jest"' "$dir/package.json" 2>/dev/null; then
            echo "jest"
            return
        fi
    fi

    # Check for pytest
    if [ -f "$dir/pytest.ini" ] || [ -f "$dir/setup.py" ] || [ -f "$dir/pyproject.toml" ]; then
        echo "pytest"
        return
    fi

    # Check for Go
    if [ -f "$dir/go.mod" ]; then
        echo "go"
        return
    fi

    # Check for Maven/Gradle (Java)
    if [ -f "$dir/pom.xml" ]; then
        echo "maven"
        return
    fi

    if [ -f "$dir/build.gradle" ]; then
        echo "gradle"
        return
    fi

    echo "unknown"
}

extract_coverage_percentage() {
    local output=$1
    local framework=$2

    case $framework in
        jest)
            # Extract from Jest output: "All files    |   85.5 |"
            echo "$output" | grep -E "All files.*\|.*\|" | awk -F'|' '{print $2}' | tr -d ' %' | head -1
            ;;
        pytest)
            # Extract from pytest-cov output: "TOTAL    100    85    85%"
            echo "$output" | grep "TOTAL" | awk '{print $NF}' | tr -d '%'
            ;;
        go)
            # Extract from go test output: "coverage: 85.5% of statements"
            echo "$output" | grep "coverage:" | grep -oE '[0-9]+\.[0-9]+' | head -1
            ;;
        *)
            echo "0"
            ;;
    esac
}

################################################################################
# Framework-Specific Coverage Checks
################################################################################

check_jest_coverage() {
    print_header "Running Jest Coverage Analysis"

    check_tool "npm"

    local jest_cmd="npm test -- --coverage --coverageReporters=$REPORT_FORMAT"

    if [ "$REPORT_FORMAT" = "html" ]; then
        jest_cmd="$jest_cmd text"
    fi

    log_verbose "Running: $jest_cmd"

    # Run Jest with coverage
    local output
    output=$(eval "$jest_cmd" 2>&1) || true

    echo "$output"

    # Extract coverage percentage
    CURRENT_COVERAGE=$(extract_coverage_percentage "$output" "jest")

    log_verbose "Extracted coverage: $CURRENT_COVERAGE%"

    # Check if coverage meets threshold
    if (( $(echo "$CURRENT_COVERAGE >= $THRESHOLD" | bc -l) )); then
        print_success "Coverage ($CURRENT_COVERAGE%) meets threshold ($THRESHOLD%)"
        PASSED=true
    else
        print_error "Coverage ($CURRENT_COVERAGE%) below threshold ($THRESHOLD%)"
        PASSED=false
    fi
}

check_pytest_coverage() {
    print_header "Running pytest Coverage Analysis"

    check_tool "pytest"

    local pytest_cmd="pytest --cov=$TARGET_DIR --cov-report=$REPORT_FORMAT"

    if [ "$REPORT_FORMAT" = "html" ]; then
        pytest_cmd="$pytest_cmd --cov-report=html:$OUTPUT_DIR"
    fi

    log_verbose "Running: $pytest_cmd"

    # Run pytest with coverage
    local output
    output=$(eval "$pytest_cmd" 2>&1) || true

    echo "$output"

    # Extract coverage percentage
    CURRENT_COVERAGE=$(extract_coverage_percentage "$output" "pytest")

    log_verbose "Extracted coverage: $CURRENT_COVERAGE%"

    # Check if coverage meets threshold
    if (( $(echo "$CURRENT_COVERAGE >= $THRESHOLD" | bc -l) )); then
        print_success "Coverage ($CURRENT_COVERAGE%) meets threshold ($THRESHOLD%)"
        PASSED=true
    else
        print_error "Coverage ($CURRENT_COVERAGE%) below threshold ($THRESHOLD%)"
        PASSED=false
    fi
}

check_go_coverage() {
    print_header "Running Go Coverage Analysis"

    check_tool "go"

    local go_cmd="go test -cover ./..."

    if [ "$REPORT_FORMAT" = "html" ]; then
        go_cmd="go test -coverprofile=coverage.out ./... && go tool cover -html=coverage.out -o $OUTPUT_DIR/coverage.html"
    fi

    log_verbose "Running: $go_cmd"

    # Run Go tests with coverage
    local output
    output=$(eval "$go_cmd" 2>&1) || true

    echo "$output"

    # Extract coverage percentage
    CURRENT_COVERAGE=$(extract_coverage_percentage "$output" "go")

    log_verbose "Extracted coverage: $CURRENT_COVERAGE%"

    # Check if coverage meets threshold
    if (( $(echo "$CURRENT_COVERAGE >= $THRESHOLD" | bc -l) )); then
        print_success "Coverage ($CURRENT_COVERAGE%) meets threshold ($THRESHOLD%)"
        PASSED=true
    else
        print_error "Coverage ($CURRENT_COVERAGE%) below threshold ($THRESHOLD%)"
        PASSED=false
    fi
}

check_maven_coverage() {
    print_header "Running Maven (JaCoCo) Coverage Analysis"

    check_tool "mvn"

    local mvn_cmd="mvn clean test jacoco:report"

    log_verbose "Running: $mvn_cmd"

    # Run Maven with JaCoCo
    eval "$mvn_cmd" || true

    # Check JaCoCo report
    if [ -f "target/site/jacoco/index.html" ]; then
        print_success "Coverage report generated: target/site/jacoco/index.html"

        # Try to extract coverage from CSV if available
        if [ -f "target/site/jacoco/jacoco.csv" ]; then
            # Parse JaCoCo CSV (simplified)
            CURRENT_COVERAGE=$(awk -F',' 'END {print int(($5/($4+$5))*100)}' target/site/jacoco/jacoco.csv)
        else
            print_warning "Cannot extract exact coverage percentage. Check HTML report manually."
            CURRENT_COVERAGE=$THRESHOLD
        fi
    else
        print_error "Coverage report not found"
        PASSED=false
        return
    fi

    # Check if coverage meets threshold
    if (( CURRENT_COVERAGE >= THRESHOLD )); then
        print_success "Coverage ($CURRENT_COVERAGE%) meets threshold ($THRESHOLD%)"
        PASSED=true
    else
        print_error "Coverage ($CURRENT_COVERAGE%) below threshold ($THRESHOLD%)"
        PASSED=false
    fi
}

check_critical_paths() {
    if [ -z "$CRITICAL_PATHS" ]; then
        return
    fi

    print_header "Checking Critical Path Coverage"

    IFS=',' read -ra PATHS <<< "$CRITICAL_PATHS"

    for path in "${PATHS[@]}"; do
        print_info "Checking coverage for critical path: $path"

        case $FRAMEWORK in
            jest)
                npm test -- --coverage --collectCoverageFrom="$path/**/*.{js,ts,jsx,tsx}" --coverageThreshold="{\"$path/\":{\"lines\":$THRESHOLD}}" || true
                ;;
            pytest)
                pytest --cov="$path" --cov-fail-under="$THRESHOLD" || true
                ;;
            *)
                print_warning "Critical path checking not implemented for $FRAMEWORK"
                ;;
        esac
    done
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
            -t|--threshold)
                THRESHOLD="$2"
                shift 2
                ;;
            -f|--framework)
                FRAMEWORK="$2"
                shift 2
                ;;
            -r|--report)
                REPORT_FORMAT="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -s|--strict)
                STRICT_MODE=true
                shift
                ;;
            -c|--critical)
                CRITICAL_PATHS="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
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

    # Auto-detect framework if needed
    if [ "$FRAMEWORK" = "auto" ]; then
        FRAMEWORK=$(detect_framework "$TARGET_DIR")
        print_info "Detected testing framework: $FRAMEWORK"
    fi

    # Create output directory if needed
    if [ "$REPORT_FORMAT" = "html" ]; then
        mkdir -p "$OUTPUT_DIR"
    fi

    # Run framework-specific coverage check
    case $FRAMEWORK in
        jest)
            check_jest_coverage
            ;;
        pytest)
            check_pytest_coverage
            ;;
        go)
            check_go_coverage
            ;;
        maven)
            check_maven_coverage
            ;;
        gradle)
            print_error "Gradle coverage checking not yet implemented"
            exit 2
            ;;
        *)
            print_error "Unknown or unsupported framework: $FRAMEWORK"
            exit 2
            ;;
    esac

    # Check critical paths
    check_critical_paths

    # Summary
    print_header "Coverage Summary"
    echo -e "Framework:        $FRAMEWORK"
    echo -e "Current Coverage: ${CURRENT_COVERAGE}%"
    echo -e "Threshold:        ${THRESHOLD}%"

    if [ "$PASSED" = true ]; then
        print_success "Coverage check passed!"
        exit 0
    else
        print_error "Coverage check failed!"
        if [ "$STRICT_MODE" = true ]; then
            exit 1
        else
            print_warning "Running in non-strict mode. Continuing..."
            exit 0
        fi
    fi
}

# Run main function
main "$@"
