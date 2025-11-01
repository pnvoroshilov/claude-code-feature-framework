# Core Concepts for Code Review

## Table of Contents

- [What is Code Review](#what-is-code-review)
- [The Purpose of Code Reviews](#the-purpose-of-code-reviews)
- [Quality Dimensions](#quality-dimensions)
- [Review Depth Levels](#review-depth-levels)
- [Code Quality Metrics](#code-quality-metrics)
- [Technical Debt](#technical-debt)
- [Risk Assessment](#risk-assessment)
- [Review Psychology](#review-psychology)
- [Feedback Classification](#feedback-classification)
- [Code Smells](#code-smells)
- [Security Mindset](#security-mindset)
- [Performance Thinking](#performance-thinking)
- [Maintainability Principles](#maintainability-principles)
- [Testing Philosophy](#testing-philosophy)

## What is Code Review

### Definition

Code review is a systematic examination of source code by one or more people (or AI) to find and fix mistakes overlooked in the initial development phase, improve overall code quality, and share knowledge across the team.

### Key Characteristics

**Systematic**: Follows a structured methodology, not ad-hoc inspection
**Objective**: Based on established standards and best practices
**Constructive**: Aims to improve code, not criticize the developer
**Educational**: Teaches both reviewer and reviewee
**Collaborative**: Involves discussion and shared understanding

### Types of Code Reviews

**1. Formal Inspection**
- Structured process with defined roles
- Multiple reviewers
- Documented findings
- Follow-up verification
- Typically for critical code

**2. Peer Review**
- Informal review by colleagues
- Flexible process
- Quick turnaround
- Most common in agile teams

**3. Tool-Assisted Review**
- Automated static analysis
- Linter enforcement
- Security scanners
- Metrics collection
- Continuous monitoring

**4. Pair Programming**
- Real-time review during development
- Two developers, one keyboard
- Immediate feedback
- Knowledge transfer built-in

## The Purpose of Code Reviews

### Primary Objectives

**1. Bug Detection**
Find defects before they reach production:
- Logic errors
- Edge cases missed
- Race conditions
- Memory leaks
- Resource management issues

**2. Quality Improvement**
Enhance overall code quality:
- Readability
- Maintainability
- Performance
- Security
- Testability

**3. Knowledge Sharing**
Spread knowledge across team:
- System architecture understanding
- Design pattern usage
- Language feature awareness
- Domain knowledge transfer
- Best practice dissemination

**4. Standard Enforcement**
Ensure consistency:
- Coding style adherence
- Architecture pattern compliance
- Documentation standards
- Testing requirements
- Security guidelines

**5. Risk Mitigation**
Reduce project risks:
- Security vulnerabilities
- Performance bottlenecks
- Scalability issues
- Technical debt accumulation
- Maintenance burden

### Secondary Benefits

**Team Building**: Fosters collaboration and shared ownership
**Mentoring**: Helps junior developers learn from seniors
**Quality Culture**: Establishes quality as a team value
**Documentation**: Creates knowledge base through discussions
**Confidence**: Increases team confidence in codebase

## Quality Dimensions

### 1. Correctness

**Definition**: Code does what it's supposed to do, correctly handles all cases, and produces expected outputs.

**Evaluation Criteria**:
- Algorithm correctness
- Business logic accuracy
- Edge case handling
- Boundary condition management
- Error scenario handling
- Input validation
- Output verification

**Common Issues**:
- Off-by-one errors
- Incorrect operators (&&/|| confusion)
- Missing null checks
- Unhandled edge cases
- Type coercion errors
- Float comparison issues

**Example - Incorrect**:
```python
def divide(a, b):
    return a / b  # Missing zero check
```

**Example - Correct**:
```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### 2. Security

**Definition**: Code protects against malicious attacks, prevents unauthorized access, and handles sensitive data safely.

**Evaluation Criteria**:
- Input sanitization
- Authentication strength
- Authorization checks
- Data encryption
- SQL injection prevention
- XSS prevention
- CSRF protection
- Secure configuration

**Common Issues**:
- SQL injection vulnerabilities
- Missing authentication
- Inadequate authorization
- Plaintext passwords
- Exposed API keys
- Insecure deserialization
- Missing rate limiting

**Example - Vulnerable**:
```python
# SQL Injection vulnerability
query = f"SELECT * FROM users WHERE username = '{username}'"
```

**Example - Secure**:
```python
# Parameterized query prevents SQL injection
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

### 3. Performance

**Definition**: Code executes efficiently, uses resources optimally, and scales appropriately with load.

**Evaluation Criteria**:
- Algorithm complexity (Big O)
- Database query efficiency
- Memory usage
- Network calls optimization
- Caching strategy
- Resource cleanup
- Concurrency handling

**Common Issues**:
- N+1 query problems
- Missing database indexes
- Memory leaks
- Inefficient algorithms
- Unnecessary computations
- Blocking operations
- Poor caching

**Example - Inefficient**:
```python
# N+1 query problem
users = User.query.all()
for user in users:
    print(user.profile.name)  # Separate query for each user
```

**Example - Optimized**:
```python
# Eager loading - single query with join
users = User.query.options(joinedload(User.profile)).all()
for user in users:
    print(user.profile.name)
```

### 4. Maintainability

**Definition**: Code is easy to understand, modify, and extend by current and future developers.

**Evaluation Criteria**:
- Code readability
- Naming clarity
- Function size
- Code duplication
- Complexity level
- Documentation quality
- Modularity
- Coupling and cohesion

**Common Issues**:
- God classes (too many responsibilities)
- Long functions (>50 lines)
- Poor naming (a, temp, data)
- Code duplication
- High cyclomatic complexity
- Tight coupling
- Missing documentation

**Example - Poor Maintainability**:
```python
def p(u, p):  # Unclear naming
    if len(p) < 8 or not any(c.isupper() for c in p):  # No extraction
        return False
    # ... 100 more lines
    return True
```

**Example - High Maintainability**:
```python
def validate_user_password(username: str, password: str) -> bool:
    """Validate password meets security requirements."""
    if not meets_length_requirement(password):
        return False
    if not has_uppercase_letter(password):
        return False
    return True

def meets_length_requirement(password: str) -> bool:
    """Check password is at least 8 characters."""
    return len(password) >= MIN_PASSWORD_LENGTH
```

### 5. Testability

**Definition**: Code is designed to be easily tested with automated tests, enabling confidence in changes.

**Evaluation Criteria**:
- Unit test coverage
- Integration test presence
- Mock/stub usage appropriateness
- Test data management
- Test independence
- Test clarity
- Assertion quality

**Common Issues**:
- Untestable code (tight coupling)
- Missing tests for critical paths
- Poor test coverage
- Flaky tests
- Tests that test nothing
- Over-mocking
- Missing edge case tests

**Example - Hard to Test**:
```python
def process_order():
    user = get_current_user()  # Global dependency
    db = connect_database()  # Hard-coded connection
    result = calculate_total()  # Hidden dependencies
    send_email()  # Side effect
    return result
```

**Example - Easy to Test**:
```python
def process_order(user: User, db: Database, email_service: EmailService) -> OrderResult:
    """Process order with injected dependencies."""
    total = calculate_total(user.cart_items)
    order = db.save_order(user, total)
    email_service.send_confirmation(user.email, order)
    return OrderResult(order_id=order.id, total=total)
```

## Review Depth Levels

### Level 1: Quick Scan (5-10 minutes)

**Focus**:
- Obvious bugs
- Security red flags
- Major performance issues
- Critical violations

**When to Use**:
- Hotfix reviews
- Quick sanity checks
- Pre-commit validation
- Small changes (<50 lines)

### Level 2: Standard Review (20-30 minutes)

**Focus**:
- Correctness
- Code quality
- Test coverage
- Documentation
- Common issues

**When to Use**:
- Regular PR reviews
- Feature implementations
- Medium changes (50-400 lines)
- Most daily reviews

### Level 3: Deep Dive (1-2 hours)

**Focus**:
- Architecture impact
- Performance analysis
- Security audit
- Edge case exploration
- Design pattern evaluation
- Long-term maintainability

**When to Use**:
- Critical features
- Security-sensitive code
- Performance-critical paths
- Architecture changes
- Large changes (>400 lines)

### Level 4: Comprehensive Audit (Multiple sessions)

**Focus**:
- Complete system review
- Security penetration testing
- Performance profiling
- Technical debt assessment
- Documentation completeness
- Team standard establishment

**When to Use**:
- Pre-release audits
- Acquisition due diligence
- Security certifications
- Major refactoring
- Legacy code assessment

## Code Quality Metrics

### Cyclomatic Complexity

**Definition**: Measures the number of independent paths through code.

**Calculation**: Number of decision points + 1

**Thresholds**:
- 1-10: Simple, low risk
- 11-20: Moderate complexity
- 21-50: Complex, high risk
- 50+: Untestable, refactor immediately

**Example**:
```python
def calculate_discount(price, customer_type, loyalty_years):  # Complexity: 4
    discount = 0
    if customer_type == "premium":  # +1
        discount = 0.15
    if loyalty_years > 5:  # +1
        discount += 0.05
    if price > 1000:  # +1
        discount += 0.02
    return price * (1 - discount)
```

### Cognitive Complexity

**Definition**: Measures how difficult code is to understand (not just test).

**Factors**:
- Nesting depth (each level adds)
- Control flow breaks
- Recursion
- Binary operators in conditions

**Better Metric Than**: Cyclomatic complexity for readability assessment

### Code Coverage

**Definition**: Percentage of code executed by tests.

**Types**:
- **Line Coverage**: % of lines executed
- **Branch Coverage**: % of decision branches taken
- **Path Coverage**: % of execution paths tested
- **Function Coverage**: % of functions called

**Targets**:
- Critical code: 90-100%
- Important code: 80-90%
- Utility code: 70-80%
- Total: 80%+

### Duplication Percentage

**Definition**: Amount of duplicated code in codebase.

**Target**: <3% duplication

**Detection**: Identify similar code blocks (>6 lines)

**Impact**: High duplication = high maintenance cost

### Maintainability Index

**Definition**: Combined metric of complexity, code volume, and documentation.

**Scale**: 0-100 (higher is better)

**Thresholds**:
- 80-100: Highly maintainable
- 60-79: Moderately maintainable
- 40-59: Needs attention
- 0-39: Difficult to maintain

## Technical Debt

### Definition

Technical debt is the implied cost of additional rework caused by choosing an easy (quick) solution now instead of using a better approach that would take longer.

### Types of Technical Debt

**1. Deliberate Debt**
- Conscious decision to ship faster
- Documented and tracked
- Planned payback timeline
- Example: "Skip optimization for MVP launch"

**2. Accidental Debt**
- Result of lack of knowledge
- Not intentional
- Discovered later
- Example: "Didn't know about connection pooling"

**3. Bit Rot Debt**
- Gradual degradation over time
- Dependencies become outdated
- Standards evolve
- Example: "Using deprecated APIs"

**4. Design Debt**
- Architectural problems
- Wrong abstractions
- Tight coupling
- Example: "Monolith should be microservices"

### Measuring Technical Debt

**Debt Ratio** = (Cost to Fix / Cost to Develop) × 100

**Targets**:
- <5%: Healthy codebase
- 5-10%: Acceptable
- 10-20%: Concerning
- 20%+: Critical, dedicate resources

### Debt Management Strategies

**1. Prevention**
- Code reviews
- Automated quality gates
- Design reviews
- Pair programming

**2. Tracking**
- TODO comments with tracking IDs
- Technical debt backlog
- Debt visibility in dashboards
- Regular debt review meetings

**3. Paydown**
- Boy Scout Rule (leave code better)
- Dedicated refactoring sprints
- 20% time for tech debt
- Architecture evolution roadmap

## Risk Assessment

### Risk Categories

**1. Security Risk**
- **Critical**: Authentication bypass, SQL injection
- **High**: Missing authorization, XSS vulnerabilities
- **Medium**: Weak passwords, missing CSRF
- **Low**: Information disclosure

**2. Correctness Risk**
- **Critical**: Data corruption, financial calculation errors
- **High**: Core business logic bugs
- **Medium**: Edge case handling
- **Low**: UI display issues

**3. Performance Risk**
- **Critical**: System unavailability, crashes
- **High**: Severe degradation (>10x slower)
- **Medium**: Noticeable slowdown (2-10x)
- **Low**: Minor inefficiency

**4. Maintainability Risk**
- **Critical**: Unmaintainable code (no one understands)
- **High**: Frequent bugs in area
- **Medium**: Slow to modify
- **Low**: Slightly unclear code

### Impact vs Probability Matrix

| Probability | Critical Impact | High Impact | Medium Impact | Low Impact |
|-------------|----------------|-------------|---------------|-----------|
| Very Likely | BLOCK | BLOCK | FIX NOW | FIX SOON |
| Likely | BLOCK | FIX NOW | FIX SOON | BACKLOG |
| Possible | FIX NOW | FIX SOON | BACKLOG | BACKLOG |
| Unlikely | FIX SOON | BACKLOG | BACKLOG | IGNORE |

**Actions**:
- **BLOCK**: Do not merge until fixed
- **FIX NOW**: Must fix before next release
- **FIX SOON**: Fix within 2 sprints
- **BACKLOG**: Track for future
- **IGNORE**: Not worth the effort

## Review Psychology

### Cognitive Biases in Code Review

**1. Confirmation Bias**
- Seeing what you expect to see
- Missing issues because "it looks right"
- **Mitigation**: Use checklists, assume bugs exist

**2. Authority Bias**
- Not questioning senior developers
- Assuming experienced developers don't make mistakes
- **Mitigation**: Review all code equally

**3. Anchoring Bias**
- First impression influences entire review
- Initial bug found colors perception
- **Mitigation**: Review in multiple passes

**4. Availability Bias**
- Recent bugs influence current review
- Over-focusing on familiar issues
- **Mitigation**: Use comprehensive checklist

### Psychological Safety

**Why It Matters**:
- Encourages learning and growth
- Enables honest feedback
- Reduces defensive reactions
- Improves code quality long-term

**How to Create It**:
1. **Criticize code, not people**: "This function is complex" not "You wrote complex code"
2. **Ask questions**: "Did you consider...?" not "This is wrong"
3. **Acknowledge good work**: Start with positives
4. **Be specific**: Vague feedback is frustrating
5. **Explain rationale**: Help them learn why

### Reviewer Fatigue

**Symptoms**:
- Missing obvious bugs
- Rushing through reviews
- Irritable feedback
- Skipping sections

**Prevention**:
- Limit review time to 60 minutes
- Review 200-400 lines per session
- Take breaks
- Distribute review load
- Use automated tools to reduce burden

## Feedback Classification

### Severity Levels

**CRITICAL** (Must Fix - Block Merge)
- Security vulnerabilities
- Data corruption risks
- System crashes
- Correctness bugs in critical paths

**HIGH** (Should Fix - Strong Recommendation)
- Performance issues
- Significant maintainability problems
- Missing error handling
- Test coverage gaps

**MEDIUM** (Consider Fixing - Suggestion)
- Code style violations
- Minor optimizations
- Documentation improvements
- Refactoring opportunities

**LOW** (Optional - Nice to Have)
- Naming suggestions
- Formatting preferences
- Alternative approaches
- Micro-optimizations

### Feedback Types

**1. Blocking**
Must be addressed before merge:
```
CRITICAL: SQL injection vulnerability on line 45
This allows attackers to execute arbitrary SQL.
Fix: Use parameterized queries instead.
```

**2. Non-Blocking**
Should be addressed, but not blocking:
```
SUGGESTION: Consider extracting this logic into a separate function
This would improve testability and reusability.
```

**3. Question**
Seeking clarification:
```
QUESTION: Why do we use setTimeout here instead of promises?
Understanding the rationale would help assess if this is the best approach.
```

**4. Praise**
Highlighting good work:
```
NICE: Excellent error handling with descriptive messages
This will make debugging much easier.
```

## Code Smells

### Definition

Code smells are indicators of potential problems in code. They don't always indicate bugs, but suggest areas that warrant closer inspection.

### Common Code Smells

**1. Long Method**
- Functions/methods >50 lines
- **Problem**: Hard to understand, test, reuse
- **Fix**: Extract smaller functions

**2. Large Class**
- Classes with too many responsibilities
- **Problem**: Violates Single Responsibility Principle
- **Fix**: Split into smaller, focused classes

**3. Long Parameter List**
- Functions with >4 parameters
- **Problem**: Hard to understand, easy to misuse
- **Fix**: Use parameter objects or builder pattern

**4. Duplicate Code**
- Same/similar code in multiple places
- **Problem**: Hard to maintain, bugs multiply
- **Fix**: Extract to reusable function/class

**5. Dead Code**
- Unused functions, variables, parameters
- **Problem**: Confusing, maintenance burden
- **Fix**: Remove it (version control keeps history)

**6. Magic Numbers**
- Literal numbers without explanation
- **Problem**: Unclear meaning
- **Fix**: Named constants

**7. Feature Envy**
- Class uses methods of another class extensively
- **Problem**: Poor encapsulation
- **Fix**: Move functionality to the envied class

**8. Primitive Obsession**
- Using primitives instead of small objects
- **Problem**: Lack of type safety, validation
- **Fix**: Create value objects

## Security Mindset

### Trust Nothing

**Principle**: Never trust input, always validate

**Examples**:
- User input: Validate, sanitize, escape
- API responses: Verify structure, handle errors
- File uploads: Check type, size, content
- Configuration: Validate against schema

### Defense in Depth

**Principle**: Multiple layers of security

**Layers**:
1. Input validation
2. Authentication
3. Authorization
4. Encryption in transit
5. Encryption at rest
6. Audit logging
7. Rate limiting
8. Monitoring

### Principle of Least Privilege

**Principle**: Grant minimal necessary permissions

**Applications**:
- Database users: Read-only where possible
- File permissions: Minimal access needed
- API tokens: Scoped to specific actions
- User roles: Granular permissions

### Security by Design

**Principle**: Security is not an afterthought

**Practices**:
- Threat modeling during design
- Security requirements in stories
- Security testing automated
- Regular security reviews
- Dependency vulnerability scanning

## Performance Thinking

### Premature Optimization is Evil

**Principle**: "Premature optimization is the root of all evil" - Donald Knuth

**Meaning**:
- Don't optimize before measuring
- Focus on correct, clean code first
- Identify bottlenecks with profiling
- Then optimize hot paths

**Exceptions**:
- Algorithm choice (O(n²) vs O(n log n))
- Database indexes
- Caching strategy
- Resource cleanup

### Performance Budget

**Concept**: Set measurable performance targets

**Examples**:
- Page load: <3 seconds
- API response: <200ms (95th percentile)
- Database query: <100ms
- Bundle size: <500KB

### Common Performance Pitfalls

**1. N+1 Queries**
```python
# BAD: N+1 queries
posts = Post.query.all()
for post in posts:
    print(post.author.name)  # Query per post

# GOOD: Eager loading
posts = Post.query.options(joinedload(Post.author)).all()
for post in posts:
    print(post.author.name)  # Single query with join
```

**2. Missing Indexes**
```sql
-- BAD: Full table scan
SELECT * FROM users WHERE email = 'user@example.com';

-- GOOD: With index
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
```

**3. Unnecessary Computations**
```python
# BAD: Recalculating in loop
for item in items:
    if len(items) > MAX_ITEMS:  # Calculated every iteration
        break

# GOOD: Calculate once
items_count = len(items)
for item in items:
    if items_count > MAX_ITEMS:
        break
```

## Maintainability Principles

### SOLID Principles

**S - Single Responsibility**
Each class/function should have one reason to change

**O - Open/Closed**
Open for extension, closed for modification

**L - Liskov Substitution**
Subtypes must be substitutable for base types

**I - Interface Segregation**
Many specific interfaces better than one general

**D - Dependency Inversion**
Depend on abstractions, not concretions

### DRY (Don't Repeat Yourself)

**Principle**: Every piece of knowledge should have a single, unambiguous representation

**Application**:
- Extract duplicate code to functions
- Use configuration over hard-coding
- Create reusable components
- Share common utilities

**Balance**: Don't DRY too early (wait for 3rd usage)

### KISS (Keep It Simple, Stupid)

**Principle**: Simplicity should be a key goal; unnecessary complexity should be avoided

**Application**:
- Use simple algorithms when sufficient
- Avoid clever tricks
- Prefer clarity over brevity
- Use standard patterns

### YAGNI (You Aren't Gonna Need It)

**Principle**: Don't add functionality until needed

**Application**:
- Don't build for hypothetical future
- Add features when needed, not speculated
- Refactor when requirements change
- Focus on current requirements

## Testing Philosophy

### Testing Pyramid

**Structure**:
```
     /\
    /E2\     <- Few (slow, expensive, brittle)
   /----\
  /INTEGR\   <- Some (medium speed/cost)
 /--------\
/   UNIT   \ <- Many (fast, cheap, stable)
```

**Unit Tests (70%)**:
- Test individual functions/methods
- Fast execution (<1ms each)
- Isolated (no external dependencies)
- Many tests, high coverage

**Integration Tests (20%)**:
- Test component interactions
- Medium execution (<100ms each)
- Real dependencies (database, API)
- Critical paths covered

**E2E Tests (10%)**:
- Test complete user flows
- Slow execution (seconds)
- Full system integration
- Happy paths and critical scenarios

### Test Qualities

**FIRST Principles**:

**Fast**: Tests should run quickly
**Independent**: No dependencies between tests
**Repeatable**: Same result every time
**Self-Validating**: Clear pass/fail
**Timely**: Written with code (TDD) or immediately after

### Test-Driven Development (TDD)

**Red-Green-Refactor Cycle**:

1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code quality

**Benefits**:
- Tests written for all code
- Better API design
- Confidence in changes
- Living documentation

**When to Use**:
- Well-understood requirements
- Critical business logic
- Library/API development
- Bug fixes (test first, then fix)

---

These core concepts form the foundation of effective code review. Understanding them enables consistent, comprehensive, and constructive reviews that improve code quality and team effectiveness.
