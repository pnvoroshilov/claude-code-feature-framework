# Code Review API Reference

## Review Request Syntax

### Basic Review Request

```
Review this code:
[paste code or provide file path]
```

### Focused Review Request

```
Review this [component type] focusing on [aspects]:
[code]

Component types: function, class, module, API endpoint, component, service
Aspects: security, performance, correctness, maintainability, testing
```

### Pull Request Review

```
Review this PR for merge readiness:
- PR #: [number]
- Focus: [changes only / full context]
- Critical areas: [list]
[provide git diff or changed files]
```

## Severity Levels

### CRITICAL - Must Fix Before Merge

**Definition**: Issues that will cause:
- Security vulnerabilities
- Data loss or corruption
- System crashes
- Incorrect business logic
- Breaking changes without migration

**Example Output**:
```
CRITICAL: SQL Injection Vulnerability (Line 45)
Severity: CRITICAL
Category: Security
Impact: Attackers can execute arbitrary SQL queries

Issue:
query = f"SELECT * FROM users WHERE id = '{user_id}'"

Fix:
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

Priority: BLOCK MERGE
```

### HIGH - Should Fix

**Definition**: Issues that significantly impact:
- Performance (>2x degradation)
- Maintainability
- Test coverage (<80% for new code)
- Error handling gaps

**Example Output**:
```
HIGH: N+1 Query Problem (Lines 78-82)
Severity: HIGH
Category: Performance
Impact: Database query per iteration (potential 1000+ queries)

Current Implementation:
users = User.query.all()
for user in users:
    print(user.profile.name)  # Separate query each time

Suggested Fix:
users = User.query.options(joinedload(User.profile)).all()
for user in users:
    print(user.profile.name)  # Single query with join

Performance Impact: 1000x improvement for 1000 users
Priority: Fix before release
```

### MEDIUM - Consider Fixing

**Definition**: Issues that:
- Violate style guidelines
- Have minor performance impacts
- Could be more maintainable
- Have documentation gaps

**Example Output**:
```
MEDIUM: Function Complexity (Line 100)
Severity: MEDIUM
Category: Maintainability
Complexity: 15 (threshold: 10)

Suggestion: Extract nested conditionals into separate functions:
- validate_permissions()
- check_business_rules()
- format_response()

This would improve testability and readability.

Priority: Address in current sprint
```

### LOW - Optional

**Definition**: Nice-to-have improvements:
- Naming suggestions
- Alternative approaches
- Micro-optimizations
- Formatting preferences

**Example Output**:
```
LOW: Variable Naming Suggestion (Line 45)
Severity: LOW
Category: Style

Current: data
Suggested: user_registration_data

Rationale: More descriptive name improves code clarity

Priority: Optional
```

## Quality Metrics

### Overall Quality Score

**Scale**: 1-10 (10 being perfect)

**Calculation**:
```python
score = base_score  # Start at 10
score -= critical_issues * 2.0  # -2 per critical
score -= high_issues * 0.5      # -0.5 per high
score -= medium_issues * 0.2    # -0.2 per medium
score -= low_issues * 0.1       # -0.1 per low
score = max(score, 1)           # Minimum 1
```

**Interpretation**:
- 9-10: Excellent quality
- 7-8: Good quality, minor improvements
- 5-6: Acceptable, several improvements needed
- 3-4: Poor quality, significant rework required
- 1-2: Unacceptable, major issues

### Code Coverage Metrics

**Types**:
- Line Coverage: % of lines executed by tests
- Branch Coverage: % of decision branches taken
- Function Coverage: % of functions called
- Path Coverage: % of execution paths tested

**Thresholds**:
```python
COVERAGE_THRESHOLDS = {
    'critical_code': 0.95,    # 95% minimum
    'business_logic': 0.85,   # 85% minimum
    'utility_code': 0.75,     # 75% minimum
    'overall': 0.80           # 80% minimum
}
```

### Complexity Metrics

**Cyclomatic Complexity**:
```python
COMPLEXITY_LEVELS = {
    'simple': (1, 10),        # Low risk
    'moderate': (11, 20),     # Medium risk
    'complex': (21, 50),      # High risk
    'very_complex': (51, float('inf'))  # Unacceptable
}
```

**Cognitive Complexity**:
- Measures how difficult code is to understand
- Accounts for nesting, breaks, and recursion
- Target: <15 per function

## Review Checklists

### Pre-Commit Checklist

```markdown
Code Quality Pre-Commit Checklist:

Correctness:
- [ ] Code compiles/runs without errors
- [ ] Handles edge cases and null/undefined
- [ ] Input validation implemented
- [ ] Business logic is correct

Testing:
- [ ] New code has tests
- [ ] Tests pass locally
- [ ] Coverage meets threshold (80%+)
- [ ] Edge cases tested

Code Quality:
- [ ] Functions <50 lines
- [ ] Complexity <10 per function
- [ ] No code duplication
- [ ] Meaningful variable names
- [ ] Comments for complex logic only

Security:
- [ ] No sensitive data in code
- [ ] Input sanitized
- [ ] Authentication/authorization checked
- [ ] Dependencies up to date

Performance:
- [ ] No N+1 queries
- [ ] Appropriate indexes
- [ ] Reasonable algorithm complexity
- [ ] Resources properly cleaned up

Documentation:
- [ ] Public APIs documented
- [ ] README updated if needed
- [ ] CHANGELOG updated
- [ ] Complex logic explained
```

### Pull Request Checklist

```markdown
PR Review Checklist:

General:
- [ ] PR description clear and complete
- [ ] Linked to issue/ticket
- [ ] Reasonable size (<400 lines)
- [ ] No merge conflicts

Code Review:
- [ ] Code changes reviewed
- [ ] Tests reviewed
- [ ] Documentation reviewed
- [ ] No obvious bugs

Testing:
- [ ] All tests pass
- [ ] New functionality tested
- [ ] Regression tests added if fixing bug
- [ ] Manual testing completed

Quality Gates:
- [ ] Linter passes
- [ ] Type checker passes (if applicable)
- [ ] Code coverage meets threshold
- [ ] Security scan passes

Deployment:
- [ ] Database migrations included if needed
- [ ] Configuration changes documented
- [ ] Rollback plan identified
- [ ] Feature flags used if appropriate

Approval:
- [ ] At least one approval from team member
- [ ] All conversations resolved
- [ ] CI/CD pipeline green
- [ ] Ready to merge
```

### Security Review Checklist

```markdown
Security Review Checklist:

Input Validation:
- [ ] All user input validated
- [ ] Type checking implemented
- [ ] Length limits enforced
- [ ] Whitelist validation used
- [ ] Encoded/escaped for context (HTML, SQL, URL)

Authentication & Authorization:
- [ ] Authentication required
- [ ] Authorization checked
- [ ] Session management secure
- [ ] Password handling secure (hashed, salted)
- [ ] MFA supported where appropriate

Data Protection:
- [ ] Sensitive data encrypted in transit (HTTPS)
- [ ] Sensitive data encrypted at rest
- [ ] PII handling compliant
- [ ] Secrets not in code
- [ ] Logging doesn't expose sensitive data

Common Vulnerabilities:
- [ ] No SQL injection
- [ ] No XSS vulnerabilities
- [ ] No CSRF vulnerabilities
- [ ] No insecure deserialization
- [ ] No path traversal
- [ ] No command injection

Security Headers:
- [ ] CSP (Content Security Policy)
- [ ] HSTS (Strict Transport Security)
- [ ] X-Frame-Options
- [ ] X-Content-Type-Options
- [ ] Referrer-Policy

Dependencies:
- [ ] No known vulnerabilities (npm audit / safety check)
- [ ] Versions pinned
- [ ] Regular updates planned
- [ ] License compliance checked

Monitoring:
- [ ] Security events logged
- [ ] Failed auth attempts tracked
- [ ] Rate limiting implemented
- [ ] Anomaly detection in place
```

## Rating Scale Explanations

### Code Quality Rating (1-10)

**10 - Exceptional**:
- Zero issues found
- Exemplary best practices
- Comprehensive tests
- Excellent documentation
- Could be used as example

**9 - Excellent**:
- Minor LOW severity issues only
- Strong adherence to best practices
- Good test coverage
- Well documented

**8 - Very Good**:
- Few MEDIUM issues
- Generally follows best practices
- Adequate test coverage
- Basic documentation

**7 - Good**:
- Some MEDIUM issues
- Mostly follows best practices
- Acceptable test coverage
- Documentation present

**6 - Acceptable**:
- Multiple MEDIUM issues or few HIGH
- Inconsistent best practices
- Test coverage below ideal
- Documentation gaps

**5 - Fair**:
- Several HIGH issues
- Many best practice violations
- Significant test gaps
- Poor documentation

**4 - Poor**:
- HIGH issues and possibly CRITICAL
- Frequent violations
- Major test gaps
- Minimal documentation

**3 - Very Poor**:
- Multiple CRITICAL issues
- Systematic violations
- Insufficient testing
- No documentation

**2 - Unacceptable**:
- Severe CRITICAL issues
- Complete disregard for standards
- No testing
- No documentation

**1 - Dangerous**:
- Critical security vulnerabilities
- Will cause production failures
- Cannot be safely deployed

## Tool Integration Guides

### GitHub Actions Integration

```yaml
name: Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Run linters
        run: |
          black --check .
          flake8 .
          mypy src/

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml

      - name: Check coverage
        run: |
          coverage report --fail-under=80

      - name: Security scan
        run: |
          bandit -r src/
          safety check
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
```

### SonarQube Configuration

```properties
# sonar-project.properties
sonar.projectKey=myproject
sonar.projectName=My Project
sonar.projectVersion=1.0

# Source and test directories
sonar.sources=src
sonar.tests=tests

# Coverage reports
sonar.python.coverage.reportPaths=coverage.xml
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Quality gate conditions
sonar.qualitygate.wait=true

# Exclusions
sonar.coverage.exclusions=**/*test*.py,**/*.spec.ts
sonar.cpd.exclusions=**/*test*.py

# Thresholds
sonar.coverage.minLines=80
sonar.duplications.minBlocks=10
```

---

This API reference provides structured guidelines for requesting reviews, interpreting results, and integrating code review into development workflows.
