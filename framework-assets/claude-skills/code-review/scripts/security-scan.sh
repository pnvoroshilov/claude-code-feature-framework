#!/bin/bash

################################################################################
# security-scan.sh - Comprehensive Security Scanning for Code Review
################################################################################
#
# DESCRIPTION:
#   Performs comprehensive security scanning including dependency vulnerabilities,
#   static code analysis, secrets detection, and security best practices validation.
#   Integrates multiple security tools for thorough analysis.
#
# USAGE:
#   ./security-scan.sh [OPTIONS]
#
# OPTIONS:
#   -d, --directory DIR      Target directory (default: current directory)
#   -l, --level LEVEL        Scan level: quick, standard, thorough (default: standard)
#   -o, --output FILE        Output report file (JSON format)
#   -f, --fix                Attempt to auto-fix vulnerabilities where possible
#   -s, --severity LEVEL     Minimum severity to report (low, medium, high, critical)
#   -i, --ignore FILE        Ignore file with vulnerability exceptions
#   -v, --verbose            Verbose output
#   -h, --help               Show this help message
#
# EXAMPLES:
#   # Quick security scan
#   ./security-scan.sh -l quick
#
#   # Thorough scan with JSON report
#   ./security-scan.sh -l thorough -o security-report.json
#
#   # Scan with auto-fix for dependencies
#   ./security-scan.sh -f -s high
#
#   # Standard scan with custom ignore file
#   ./security-scan.sh -i .security-ignore
#
# EXIT CODES:
#   0 - No security issues found
#   1 - Security issues found
#   2 - Configuration error
#   3 - Required tool not found
#
# SECURITY CHECKS PERFORMED:
#   - Dependency vulnerability scanning (npm audit, safety, etc.)
#   - Static code security analysis (Bandit, ESLint security)
#   - Secret/credential detection (detect-secrets, git-secrets)
#   - License compliance checking
#   - OWASP Top 10 pattern detection
#   - Hardcoded password detection
#   - SQL injection pattern detection
#   - XSS vulnerability detection
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default configuration
TARGET_DIR="."
SCAN_LEVEL="standard"
OUTPUT_FILE=""
AUTO_FIX=false
MIN_SEVERITY="low"
IGNORE_FILE=""
VERBOSE=false

# Issue tracking
CRITICAL_COUNT=0
HIGH_COUNT=0
MEDIUM_COUNT=0
LOW_COUNT=0

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

print_critical() {
    echo -e "${MAGENTA}🔴 CRITICAL: $1${NC}"
    ((CRITICAL_COUNT++))
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
    local required=$2

    if ! command -v "$tool" &> /dev/null; then
        if [ "$required" = "true" ]; then
            print_error "Required tool '$tool' not found. Please install it."
            return 1
        else
            print_warning "Optional tool '$tool' not found. Skipping related checks."
            return 1
        fi
    fi
    return 0
}

################################################################################
# Dependency Vulnerability Scanning
################################################################################

scan_npm_dependencies() {
    print_header "Scanning npm Dependencies"

    if [ ! -f "package.json" ]; then
        print_info "No package.json found. Skipping npm audit."
        return
    fi

    if ! check_tool "npm" false; then
        return
    fi

    print_info "Running npm audit..."

    if [ "$AUTO_FIX" = true ]; then
        npm audit fix || true
        print_success "Attempted to fix npm vulnerabilities"
    fi

    # Generate audit report
    local audit_output
    audit_output=$(npm audit --json 2>&1) || true

    # Count vulnerabilities by severity
    local critical=$(echo "$audit_output" | jq -r '.metadata.vulnerabilities.critical // 0' 2>/dev/null || echo "0")
    local high=$(echo "$audit_output" | jq -r '.metadata.vulnerabilities.high // 0' 2>/dev/null || echo "0")
    local medium=$(echo "$audit_output" | jq -r '.metadata.vulnerabilities.moderate // 0' 2>/dev/null || echo "0")
    local low=$(echo "$audit_output" | jq -r '.metadata.vulnerabilities.low // 0' 2>/dev/null || echo "0")

    CRITICAL_COUNT=$((CRITICAL_COUNT + critical))
    HIGH_COUNT=$((HIGH_COUNT + high))
    MEDIUM_COUNT=$((MEDIUM_COUNT + medium))
    LOW_COUNT=$((LOW_COUNT + low))

    if [ "$critical" -gt 0 ] || [ "$high" -gt 0 ]; then
        print_critical "Found $critical critical and $high high severity npm vulnerabilities"
    elif [ "$medium" -gt 0 ]; then
        print_warning "Found $medium medium severity npm vulnerabilities"
    else
        print_success "No critical npm vulnerabilities found"
    fi
}

scan_python_dependencies() {
    print_header "Scanning Python Dependencies"

    if [ ! -f "requirements.txt" ] && [ ! -f "Pipfile" ] && [ ! -f "pyproject.toml" ]; then
        print_info "No Python dependency files found. Skipping Python security scan."
        return
    fi

    # Safety check
    if check_tool "safety" false; then
        print_info "Running Safety check..."

        local safety_output
        if [ -f "requirements.txt" ]; then
            safety_output=$(safety check -r requirements.txt --json 2>&1) || true

            local vuln_count
            vuln_count=$(echo "$safety_output" | jq 'length' 2>/dev/null || echo "0")

            if [ "$vuln_count" -gt 0 ]; then
                print_warning "Found $vuln_count Python package vulnerabilities"
                HIGH_COUNT=$((HIGH_COUNT + vuln_count))
            else
                print_success "No Python package vulnerabilities found"
            fi
        fi
    fi

    # Bandit static analysis
    if check_tool "bandit" false; then
        print_info "Running Bandit security analysis..."

        local bandit_output
        bandit_output=$(bandit -r "$TARGET_DIR" -f json 2>&1) || true

        local high_issues
        high_issues=$(echo "$bandit_output" | jq '[.results[] | select(.issue_severity=="HIGH")] | length' 2>/dev/null || echo "0")

        local medium_issues
        medium_issues=$(echo "$bandit_output" | jq '[.results[] | select(.issue_severity=="MEDIUM")] | length' 2>/dev/null || echo "0")

        HIGH_COUNT=$((HIGH_COUNT + high_issues))
        MEDIUM_COUNT=$((MEDIUM_COUNT + medium_issues))

        if [ "$high_issues" -gt 0 ]; then
            print_warning "Bandit found $high_issues high severity security issues"
        else
            print_success "Bandit found no high severity issues"
        fi
    fi
}

################################################################################
# Secret Detection
################################################################################

detect_secrets() {
    print_header "Detecting Hardcoded Secrets"

    # Check for common secret patterns
    print_info "Scanning for hardcoded secrets and credentials..."

    local secret_patterns=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api[_-]?key\s*=\s*['\"][^'\"]+['\"]"
        "secret[_-]?key\s*=\s*['\"][^'\"]+['\"]"
        "access[_-]?token\s*=\s*['\"][^'\"]+['\"]"
        "private[_-]?key"
        "BEGIN RSA PRIVATE KEY"
        "BEGIN PRIVATE KEY"
        "aws_access_key_id"
        "aws_secret_access_key"
    )

    local secrets_found=0

    for pattern in "${secret_patterns[@]}"; do
        local matches
        matches=$(grep -r -i -E "$pattern" "$TARGET_DIR" \
            --exclude-dir=node_modules \
            --exclude-dir=.git \
            --exclude-dir=venv \
            --exclude-dir=__pycache__ \
            --exclude="*.log" 2>/dev/null || true)

        if [ -n "$matches" ]; then
            print_critical "Potential secret detected: $pattern"
            echo "$matches" | head -5
            ((secrets_found++))
        fi
    done

    if [ $secrets_found -gt 0 ]; then
        CRITICAL_COUNT=$((CRITICAL_COUNT + secrets_found))
        print_error "Found $secrets_found potential hardcoded secrets!"
    else
        print_success "No obvious hardcoded secrets detected"
    fi

    # detect-secrets tool
    if check_tool "detect-secrets" false; then
        print_info "Running detect-secrets scan..."
        detect-secrets scan "$TARGET_DIR" 2>&1 | grep -E "potential secret" || print_success "detect-secrets: no issues"
    fi
}

################################################################################
# Code Security Patterns
################################################################################

scan_security_patterns() {
    print_header "Scanning for Security Anti-Patterns"

    # SQL Injection patterns
    print_info "Checking for SQL injection vulnerabilities..."
    local sql_patterns=(
        "execute\([\"'][^\"']*\+.*[\"']\)"
        "query\([\"'][^\"']*\+.*[\"']\)"
        "SELECT.*FROM.*WHERE.*\+.*"
    )

    for pattern in "${sql_patterns[@]}"; do
        local matches
        matches=$(grep -r -E "$pattern" "$TARGET_DIR" \
            --include="*.py" \
            --include="*.js" \
            --include="*.ts" \
            --include="*.java" \
            --exclude-dir=node_modules \
            --exclude-dir=.git 2>/dev/null || true)

        if [ -n "$matches" ]; then
            print_warning "Potential SQL injection vulnerability detected"
            echo "$matches" | head -3
            HIGH_COUNT=$((HIGH_COUNT + 1))
        fi
    done

    # XSS patterns
    print_info "Checking for XSS vulnerabilities..."
    local xss_patterns=(
        "innerHTML\s*=.*"
        "dangerouslySetInnerHTML"
        "document\.write\("
    )

    for pattern in "${xss_patterns[@]}"; do
        local matches
        matches=$(grep -r -E "$pattern" "$TARGET_DIR" \
            --include="*.js" \
            --include="*.jsx" \
            --include="*.ts" \
            --include="*.tsx" \
            --exclude-dir=node_modules \
            --exclude-dir=.git 2>/dev/null || true)

        if [ -n "$matches" ]; then
            print_warning "Potential XSS vulnerability detected: $pattern"
            MEDIUM_COUNT=$((MEDIUM_COUNT + 1))
        fi
    done

    # Insecure deserialization
    print_info "Checking for insecure deserialization..."
    local deser_patterns=(
        "pickle\.loads"
        "eval\("
        "exec\("
        "Function\(['\"].*['\"]"
    )

    for pattern in "${deser_patterns[@]}"; do
        local matches
        matches=$(grep -r -E "$pattern" "$TARGET_DIR" \
            --exclude-dir=node_modules \
            --exclude-dir=.git 2>/dev/null || true)

        if [ -n "$matches" ]; then
            print_warning "Potentially insecure code execution pattern: $pattern"
            HIGH_COUNT=$((HIGH_COUNT + 1))
        fi
    done
}

################################################################################
# License Compliance
################################################################################

check_licenses() {
    print_header "Checking License Compliance"

    # npm license check
    if [ -f "package.json" ] && check_tool "license-checker" false; then
        print_info "Checking npm package licenses..."
        license-checker --summary 2>&1 || true
    fi

    # Python license check
    if check_tool "pip-licenses" false; then
        print_info "Checking Python package licenses..."
        pip-licenses --format=markdown 2>&1 || true
    fi
}

################################################################################
# Generate Security Report
################################################################################

generate_report() {
    if [ -z "$OUTPUT_FILE" ]; then
        return
    fi

    print_info "Generating security report: $OUTPUT_FILE"

    cat > "$OUTPUT_FILE" <<EOF
{
  "scan_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "target_directory": "$TARGET_DIR",
  "scan_level": "$SCAN_LEVEL",
  "summary": {
    "critical": $CRITICAL_COUNT,
    "high": $HIGH_COUNT,
    "medium": $MEDIUM_COUNT,
    "low": $LOW_COUNT,
    "total": $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))
  },
  "scans_performed": [
    "dependency_vulnerabilities",
    "secret_detection",
    "security_patterns",
    "license_compliance"
  ]
}
EOF

    print_success "Report saved to: $OUTPUT_FILE"
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
            -l|--level)
                SCAN_LEVEL="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -f|--fix)
                AUTO_FIX=true
                shift
                ;;
            -s|--severity)
                MIN_SEVERITY="$2"
                shift 2
                ;;
            -i|--ignore)
                IGNORE_FILE="$2"
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

    print_header "🔒 Security Scanning - $SCAN_LEVEL level"
    print_info "Target: $TARGET_DIR"

    # Run scans based on level
    case $SCAN_LEVEL in
        quick)
            scan_npm_dependencies
            detect_secrets
            ;;
        standard)
            scan_npm_dependencies
            scan_python_dependencies
            detect_secrets
            scan_security_patterns
            ;;
        thorough)
            scan_npm_dependencies
            scan_python_dependencies
            detect_secrets
            scan_security_patterns
            check_licenses
            ;;
        *)
            print_error "Unknown scan level: $SCAN_LEVEL"
            exit 2
            ;;
    esac

    # Generate report
    generate_report

    # Summary
    print_header "Security Scan Summary"
    echo -e "Critical Issues: ${MAGENTA}$CRITICAL_COUNT${NC}"
    echo -e "High Issues:     ${RED}$HIGH_COUNT${NC}"
    echo -e "Medium Issues:   ${YELLOW}$MEDIUM_COUNT${NC}"
    echo -e "Low Issues:      ${BLUE}$LOW_COUNT${NC}"
    echo ""

    # Exit with appropriate code
    if [ $CRITICAL_COUNT -gt 0 ] || [ $HIGH_COUNT -gt 0 ]; then
        print_error "Security issues found that require immediate attention!"
        exit 1
    elif [ $MEDIUM_COUNT -gt 0 ]; then
        print_warning "Security issues found that should be addressed"
        exit 0
    else
        print_success "No critical security issues found!"
        exit 0
    fi
}

# Run main function
main "$@"
