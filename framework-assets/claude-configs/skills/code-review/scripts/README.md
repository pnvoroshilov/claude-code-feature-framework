# Code Review Scripts

This directory contains automation scripts for comprehensive code review workflows. These scripts help automate quality checks, security scanning, coverage analysis, and complexity measurement.

## Available Scripts

### 1. `run-code-review.sh` - Comprehensive Code Review Automation

**Purpose**: Automated code review script that runs multiple quality checks.

**Features**:
- Multi-language support (JavaScript, TypeScript, Python, Go, Java)
- Linting (ESLint, Pylint, Flake8, etc.)
- Type checking (TypeScript, mypy)
- Security scanning
- Code complexity analysis
- Format checking (Prettier, Black)
- Auto-fix capabilities

**Usage**:
```bash
# Basic review
./run-code-review.sh

# Review specific directory with auto-fix
./run-code-review.sh -d ./src -f

# Review Python code with HTML report
./run-code-review.sh -l python -o html -r review-report.html

# Review TypeScript with errors only
./run-code-review.sh -l typescript -s error
```

**Options**:
- `-d, --directory DIR` - Target directory (default: current)
- `-l, --language LANG` - Language to review (auto-detect if not specified)
- `-f, --fix` - Auto-fix issues where possible
- `-s, --severity LEVEL` - Minimum severity (info, warning, error)
- `-o, --output FORMAT` - Output format (console, json, html)
- `-r, --report FILE` - Save report to file

**Exit Codes**:
- `0` - All checks passed
- `1` - Critical issues found
- `2` - Configuration error
- `3` - Tool not found

---

### 2. `generate-review-report.py` - Generate Comprehensive Reports

**Purpose**: Generates detailed HTML/JSON/Markdown reports from code review results.

**Features**:
- Aggregates data from multiple linting tools
- Beautiful HTML reports with visualizations
- JSON format for CI/CD integration
- Markdown summaries
- Executive summary generation
- Actionable recommendations

**Usage**:
```bash
# Generate HTML report
python generate-review-report.py -i ./review-results -o report.html

# Generate JSON for CI/CD
python generate-review-report.py -i ./review-results -f json -o report.json

# Generate markdown summary
python generate-review-report.py -i ./review-results -f markdown -s -o summary.md
```

**Options**:
- `-i, --input DIR` - Input directory with review results
- `-o, --output FILE` - Output report file
- `-f, --format FORMAT` - Report format (html, json, markdown)
- `-s, --summary` - Generate executive summary only
- `-v, --verbose` - Verbose output

**Requirements**:
- Python 3.7+
- `jinja2` (optional, for enhanced HTML reports)
- `markdown` (optional, for markdown processing)

**Exit Codes**:
- `0` - Report generated successfully
- `1` - Error during generation
- `2` - Invalid arguments

---

### 3. `check-coverage.sh` - Test Coverage Validation

**Purpose**: Validates test coverage and enforces coverage thresholds.

**Features**:
- Multi-framework support (Jest, pytest, Go, Maven, Gradle)
- Coverage threshold enforcement
- Critical path coverage validation
- HTML/JSON/LCOV report generation
- Coverage gap identification

**Usage**:
```bash
# Check with default 80% threshold
./check-coverage.sh

# Check with 90% threshold and HTML report
./check-coverage.sh -t 90 -r html

# Check critical paths with higher coverage
./check-coverage.sh -c "src/auth,src/payment" -t 95 -s

# Run for Python project
./check-coverage.sh -f pytest -t 85 -r html -o ./coverage-report
```

**Options**:
- `-d, --directory DIR` - Target directory
- `-t, --threshold PCT` - Minimum coverage threshold (default: 80)
- `-f, --framework FRAMEWORK` - Testing framework (jest, pytest, go, auto)
- `-r, --report FORMAT` - Report format (html, json, lcov, text)
- `-o, --output DIR` - Output directory for reports
- `-s, --strict` - Fail on any coverage below threshold
- `-c, --critical PATHS` - Critical paths requiring higher coverage
- `-v, --verbose` - Verbose output

**Exit Codes**:
- `0` - Coverage meets threshold
- `1` - Coverage below threshold
- `2` - Configuration error
- `3` - Framework not found

---

### 4. `security-scan.sh` - Comprehensive Security Scanning

**Purpose**: Performs comprehensive security scanning for code review.

**Features**:
- Dependency vulnerability scanning (npm audit, safety, etc.)
- Static code security analysis (Bandit, ESLint security)
- Secret/credential detection
- License compliance checking
- OWASP Top 10 pattern detection
- SQL injection detection
- XSS vulnerability detection
- Insecure deserialization detection

**Usage**:
```bash
# Quick security scan
./security-scan.sh -l quick

# Thorough scan with JSON report
./security-scan.sh -l thorough -o security-report.json

# Scan with auto-fix for dependencies
./security-scan.sh -f -s high

# Standard scan with custom ignore file
./security-scan.sh -i .security-ignore
```

**Options**:
- `-d, --directory DIR` - Target directory
- `-l, --level LEVEL` - Scan level (quick, standard, thorough)
- `-o, --output FILE` - Output report file (JSON)
- `-f, --fix` - Auto-fix vulnerabilities where possible
- `-s, --severity LEVEL` - Minimum severity (low, medium, high, critical)
- `-i, --ignore FILE` - Ignore file with exceptions
- `-v, --verbose` - Verbose output

**Security Checks**:
- Dependency vulnerabilities
- Hardcoded secrets
- SQL injection patterns
- XSS vulnerabilities
- Insecure deserialization
- License compliance

**Exit Codes**:
- `0` - No security issues
- `1` - Security issues found
- `2` - Configuration error
- `3` - Required tool not found

---

### 5. `complexity-analyzer.py` - Code Complexity Analysis

**Purpose**: Analyzes code complexity and maintainability metrics.

**Features**:
- Cyclomatic complexity calculation
- Cognitive complexity measurement
- Maintainability index scoring
- Code smell detection
- Lines of code metrics
- Function parameter counting
- Nesting depth analysis
- HTML/JSON/text reports

**Usage**:
```bash
# Analyze Python code
python complexity-analyzer.py -d ./src -l python -t 15

# Generate HTML report
python complexity-analyzer.py -d ./src -f html -o complexity-report.html

# Analyze JavaScript and sort by complexity
python complexity-analyzer.py -d ./app -l javascript -s complexity
```

**Options**:
- `-d, --directory DIR` - Target directory
- `-l, --language LANG` - Language (python, javascript, typescript, auto)
- `-t, --threshold NUM` - Complexity threshold (default: 10)
- `-o, --output FILE` - Output report file
- `-f, --format FORMAT` - Output format (json, html, text)
- `-v, --verbose` - Verbose output

**Metrics Analyzed**:
- **Cyclomatic Complexity**: Number of independent paths
- **Cognitive Complexity**: Mental effort to understand
- **Lines of Code**: Physical and logical lines
- **Maintainability Index**: Overall maintainability (0-100)
- **Code Smells**: Long functions, deep nesting, etc.

**Exit Codes**:
- `0` - Analysis completed
- `1` - Complexity exceeds threshold
- `2` - Configuration error

---

## Installation & Setup

### Prerequisites

Install the required tools for your language:

**JavaScript/TypeScript**:
```bash
npm install -g eslint prettier
npm install -g license-checker
```

**Python**:
```bash
pip install pylint flake8 black isort mypy
pip install bandit safety radon
pip install pytest pytest-cov
```

**Go**:
```bash
go install honnef.co/go/tools/cmd/staticcheck@latest
go install golang.org/x/lint/golint@latest
```

**Optional Tools**:
```bash
# Security scanning
npm install -g snyk

# Secret detection
pip install detect-secrets

# Report generation (for Python scripts)
pip install jinja2
```

### Make Scripts Executable

```bash
chmod +x run-code-review.sh
chmod +x check-coverage.sh
chmod +x security-scan.sh
chmod +x complexity-analyzer.py
chmod +x generate-review-report.py
```

---

## Integration Examples

### CI/CD Integration (GitHub Actions)

```yaml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Code Review
        run: ./scripts/run-code-review.sh -d ./src -r report.html

      - name: Security Scan
        run: ./scripts/security-scan.sh -l thorough -o security.json

      - name: Check Coverage
        run: ./scripts/check-coverage.sh -t 80 -s

      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: review-reports
          path: |
            report.html
            security.json
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running code review checks..."

# Quick review
./scripts/run-code-review.sh -d . -s error || exit 1

# Security scan
./scripts/security-scan.sh -l quick -s high || exit 1

echo "All checks passed!"
```

### NPM Scripts Integration

```json
{
  "scripts": {
    "review": "./scripts/run-code-review.sh -d ./src",
    "review:fix": "./scripts/run-code-review.sh -d ./src -f",
    "review:report": "./scripts/run-code-review.sh -d ./src -o html -r review.html",
    "security": "./scripts/security-scan.sh -l standard",
    "coverage": "./scripts/check-coverage.sh -t 80",
    "complexity": "python ./scripts/complexity-analyzer.py -d ./src -f html -o complexity.html"
  }
}
```

---

## Workflow Examples

### Complete Code Review Workflow

```bash
# 1. Run comprehensive code review
./run-code-review.sh -d ./src -r review-raw.txt

# 2. Generate formatted report
python generate-review-report.py -i ./review-results -o review-report.html

# 3. Run security scan
./security-scan.sh -l thorough -o security-report.json

# 4. Check test coverage
./check-coverage.sh -t 80 -r html -o ./coverage

# 5. Analyze code complexity
python complexity-analyzer.py -d ./src -f html -o complexity-report.html

# 6. Review all reports
open review-report.html
open security-report.json
open coverage/index.html
open complexity-report.html
```

### Quick Pre-PR Check

```bash
# Fast checks before creating PR
./run-code-review.sh -s error -f  # Auto-fix errors
./security-scan.sh -l quick       # Quick security check
./check-coverage.sh -t 70         # Basic coverage check
```

### Release Quality Gate

```bash
# Strict checks before release
./run-code-review.sh -s warning -o html -r release-review.html
./security-scan.sh -l thorough -s high -o release-security.json
./check-coverage.sh -t 90 -s  # Strict mode
python complexity-analyzer.py -d ./src -t 8  # Lower complexity threshold
```

---

## Troubleshooting

### Common Issues

**"Tool not found" errors**:
- Install the required tool for your language
- Check if tool is in PATH: `which <tool-name>`
- Use verbose mode to see which tools are being checked

**Permission denied**:
```bash
chmod +x *.sh *.py
```

**Python script issues**:
```bash
# Ensure Python 3.7+
python --version

# Install dependencies
pip install -r requirements.txt  # if available
```

**Coverage not detected**:
- Ensure test framework is installed
- Run tests manually first to verify setup
- Use `-v` verbose flag to see detection process

### Getting Help

Run any script with `-h` or `--help` flag:
```bash
./run-code-review.sh --help
python complexity-analyzer.py --help
```

---

## Contributing

To add new scripts or improve existing ones:

1. Follow the existing script structure
2. Include comprehensive help documentation
3. Add examples in this README
4. Test with multiple languages/frameworks
5. Handle errors gracefully
6. Provide verbose logging options

---

## License

These scripts are part of the Code Review skill package and follow the same license as the parent project.
