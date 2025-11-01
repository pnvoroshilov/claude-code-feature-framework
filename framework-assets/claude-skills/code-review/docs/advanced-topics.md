# Advanced Code Review Topics

## Table of Contents

- [Automated Code Review Tools](#automated-code-review-tools)
- [Static Analysis Integration](#static-analysis-integration)
- [Code Metrics and Quality Gates](#code-metrics-and-quality-gates)
- [AI-Assisted Code Review](#ai-assisted-code-review)
- [Performance Profiling](#performance-profiling)
- [Security Scanning](#security-scanning)
- [Architecture Review](#architecture-review)
- [Technical Debt Management](#technical-debt-management)
- [Code Review Automation](#code-review-automation)
- [Pair Programming as Review](#pair-programming-as-review)

## Automated Code Review Tools

### Linters and Formatters

**Purpose**: Enforce code style and catch common errors automatically

**Python Tools**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203']

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile', 'black']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**JavaScript/TypeScript Tools**:
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react/prop-types": "off",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### Static Analysis Tools

**SonarQube Integration**:
```yaml
# sonar-project.properties
sonar.projectKey=myproject
sonar.projectName=My Project
sonar.sources=src
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Quality gates
sonar.qualitygate.wait=true
sonar.coverage.exclusions=**/*test*.py,**/*.spec.ts
```

**Benefits**:
- Automated quality metrics
- Historical trend tracking
- Team-wide quality dashboard
- CI/CD integration
- Configurable quality gates

## Static Analysis Integration

### Type Checking

**Python with mypy**:
```python
# mypy.ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_calls = True
strict_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
```

**TypeScript Strict Mode**:
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Complexity Analysis

**Calculate Cyclomatic Complexity**:
```python
# Using radon
from radon.complexity import cc_visit

def analyze_complexity(filepath: str) -> List[ComplexityResult]:
    with open(filepath) as f:
        code = f.read()
    
    results = cc_visit(code)
    high_complexity = [r for r in results if r.complexity > 10]
    
    return high_complexity

# CI Integration
def check_complexity_threshold(files: List[str], max_complexity: int = 10) -> bool:
    violations = []
    
    for filepath in files:
        results = analyze_complexity(filepath)
        for result in results:
            if result.complexity > max_complexity:
                violations.append(f"{filepath}:{result.lineno} - {result.name} (complexity: {result.complexity})")
    
    if violations:
        print("Complexity violations found:")
        for v in violations:
            print(f"  {v}")
        return False
    
    return True
```

## Code Metrics and Quality Gates

### Coverage Requirements

**pytest with coverage**:
```ini
# pytest.ini
[pytest]
addopts = 
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80

[coverage:run]
branch = True
source = src

[coverage:report]
precision = 2
skip_empty = True
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

**Jest configuration**:
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  coverageReporters: ['text', 'lcov', 'html'],
};
```

### CI/CD Quality Gates

**GitHub Actions Example**:
```yaml
name: Code Quality

on: [pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run linters
        run: |
          black --check .
          flake8 .
          mypy src/
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-fail-under=80
      
      - name: Check complexity
        run: |
          radon cc src/ -a -nb
      
      - name: Security scan
        run: |
          bandit -r src/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

## Security Scanning

### Dependency Vulnerability Scanning

**Python (Safety)**:
```bash
# Check for known security vulnerabilities
safety check --json

# In requirements-dev.txt
safety==2.3.5

# CI integration
safety check --exit-code 1  # Fail on vulnerabilities
```

**JavaScript (npm audit)**:
```bash
# Check for vulnerabilities
npm audit

# Fix automatically if possible
npm audit fix

# CI integration
npm audit --audit-level=high  # Fail on high/critical
```

**Snyk Integration**:
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [pull_request]

jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

### SAST (Static Application Security Testing)

**Bandit for Python**:
```yaml
# .bandit
[bandit]
exclude_dirs = ['/test', '/tests']
skips = ['B101']  # Skip assert_used test

# Run in CI
- name: Security scan with Bandit
  run: bandit -r src/ -f json -o bandit-report.json
```

**SemGrep**:
```yaml
# .semgrep.yml
rules:
  - id: sql-injection
    patterns:
      - pattern: cursor.execute(f"... {$VAR} ...")
    message: Potential SQL injection vulnerability
    severity: ERROR
    languages: [python]
  
  - id: hardcoded-password
    patterns:
      - pattern: password = "..."
    message: Hardcoded password detected
    severity: WARNING
    languages: [python, javascript]
```

## Performance Profiling

### Python Profiling

**cProfile Integration**:
```python
import cProfile
import pstats
from pstats import SortKey

def profile_function(func):
    """Decorator to profile function performance."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats(SortKey.CUMULATIVE)
        stats.print_stats(20)  # Top 20 functions
        
        return result
    return wrapper

@profile_function
def expensive_operation():
    # Code to profile
    pass
```

**Memory Profiling**:
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Profile memory usage line-by-line."""
    large_list = [i for i in range(1000000)]
    result = process_data(large_list)
    return result

# Run with: python -m memory_profiler script.py
```

### JavaScript/Node.js Profiling

**Chrome DevTools**:
```javascript
// Add profiling markers
console.time('expensive-operation');
expensiveOperation();
console.timeEnd('expensive-operation');

// Heap snapshot
if (global.gc) {
  global.gc();  // Force garbage collection
}
const usage = process.memoryUsage();
console.log(`Memory usage: ${usage.heapUsed / 1024 / 1024} MB`);
```

**Lighthouse CI**:
```yaml
# lighthouserc.js
module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run serve',
      url: ['http://localhost:3000/'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', {minScore: 0.9}],
        'categories:accessibility': ['error', {minScore: 0.9}],
        'categories:best-practices': ['error', {minScore: 0.9}],
        'categories:seo': ['error', {minScore: 0.9}],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

## Architecture Review

### Dependency Analysis

**Python (pydeps)**:
```bash
# Generate dependency graph
pydeps src/ --max-bacon=2 -o dependency-graph.svg

# Check for circular dependencies
pydeps src/ --show-cycles
```

**JavaScript (Madge)**:
```bash
# Circular dependency detection
madge --circular src/

# Generate dependency graph
madge --image dependency-graph.svg src/
```

### Architecture Fitness Functions

**ArchUnit for Python**:
```python
from archunit import RuleBuilder, ArchitectureTest

class ArchitectureTests(ArchitectureTest):
    
    @staticmethod
    def test_services_dont_depend_on_controllers():
        """Business logic shouldn't depend on presentation layer."""
        rule = (
            RuleBuilder()
            .classes_in_package('..services..')
            .should_not_depend_on('..controllers..')
        )
        rule.check()
    
    @staticmethod
    def test_repositories_only_accessed_by_services():
        """Data access layer should be encapsulated."""
        rule = (
            RuleBuilder()
            .classes_in_package('..repositories..')
            .should_only_be_accessed_by('..services..')
        )
        rule.check()
```

## Technical Debt Management

### Tracking Technical Debt

**TODO Comments with Tracking**:
```python
# TODO(TECH-123): Refactor this function - too complex (complexity: 15)
# FIXME(TECH-124): Memory leak in connection pool - investigate
# DEBT(TECH-125): Should use repository pattern instead of direct DB access
# HACK(TECH-126): Temporary workaround for API rate limiting

def detect_technical_debt(filepath: str) -> List[DebtItem]:
    """Extract technical debt markers from code."""
    debt_markers = ['TODO', 'FIXME', 'HACK', 'DEBT', 'XXX']
    debt_items = []
    
    with open(filepath) as f:
        for line_no, line in enumerate(f, 1):
            for marker in debt_markers:
                if marker in line:
                    debt_items.append(DebtItem(
                        file=filepath,
                        line=line_no,
                        marker=marker,
                        description=line.strip()
                    ))
    
    return debt_items
```

**SonarQube Technical Debt**:
```python
# SonarQube provides automatic technical debt estimation
# Based on time required to fix issues

def calculate_technical_debt_ratio(project_key: str) -> float:
    """Calculate technical debt ratio from SonarQube."""
    measures = sonar_api.get_measures(
        project_key,
        metrics=['sqale_debt_ratio']
    )
    return float(measures['sqale_debt_ratio'])
```

## Code Review Automation

### Automated PR Checks

**Danger JS**:
```javascript
// dangerfile.js
import { danger, warn, fail, message } from 'danger';

// Check PR size
const bigPRThreshold = 400;
if (danger.github.pr.additions + danger.github.pr.deletions > bigPRThreshold) {
  warn('⚠️ Big PR! Consider breaking this into smaller PRs for easier review.');
}

// Require tests for new code
const hasAppChanges = danger.git.modified_files.some(f => f.startsWith('src/'));
const hasTestChanges = danger.git.modified_files.some(f => f.startsWith('tests/'));

if (hasAppChanges && !hasTestChanges) {
  warn('⚠️ No test files were changed. Did you forget to add tests?');
}

// Check for TODO comments in new code
const todos = danger.git.diff.split('\n')
  .filter(line => line.startsWith('+') && line.includes('TODO'));

if (todos.length > 0) {
  message('💡 TODO comments found. Consider creating tickets for these:');
  todos.forEach(todo => message(todo));
}

// Require description
if (danger.github.pr.body.length < 50) {
  fail('❌ Please add a detailed PR description.');
}
```

### Code Review Bots

**GitHub Actions Bot**:
```yaml
name: Review Bot

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for diff
      
      - name: Check for large files
        run: |
          git diff --name-only origin/main...HEAD | while read file; do
            size=$(wc -c < "$file")
            if [ $size -gt 100000 ]; then
              echo "::warning file=$file::Large file detected ($size bytes)"
            fi
          done
      
      - name: Check for console.log
        run: |
          if git diff origin/main...HEAD | grep -E '^\+.*console\.log'; then
            echo "::error::console.log statements found in new code"
            exit 1
          fi
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Automated checks passed!'
            })
```

## Pair Programming as Review

### Benefits of Pair Programming

**Real-time Review**:
- Immediate feedback
- Knowledge sharing built-in
- Fewer defects reach code review
- Better design decisions

**Roles**:
- **Driver**: Writes code, tactical focus
- **Navigator**: Reviews code, strategic focus

**When to Use**:
- Complex features
- Critical business logic
- New team member onboarding
- Unfamiliar technology

### Remote Pair Programming Tools

**VS Code Live Share**:
```json
// .vscode/settings.json
{
  "liveshare.presence": true,
  "liveshare.focusBehavior": "accept",
  "liveshare.audio.startCallOnShare": true
}
```

**Mob Programming**:
- Rotate driver every 10-15 minutes
- Multiple people navigate
- Excellent for complex problems
- Great for team learning

---

These advanced topics enable sophisticated, automated code review processes that scale with team growth while maintaining high quality standards.
