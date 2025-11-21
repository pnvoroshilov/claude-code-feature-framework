# Refactoring Best Practices

Industry-standard guidelines, workflows, and principles for safe and effective code refactoring.

## Table of Contents

- [Pre-Refactoring Checklist](#pre-refactoring-checklist)
- [Safe Refactoring Workflow](#safe-refactoring-workflow)
- [Testing Best Practices](#testing-best-practices)
- [Commit Strategies](#commit-strategies)
- [Code Review Guidelines](#code-review-guidelines)
- [Naming Conventions](#naming-conventions)
- [Architecture Best Practices](#architecture-best-practices)
- [Performance Considerations](#performance-considerations)
- [Team Collaboration](#team-collaboration)
- [Documentation Practices](#documentation-practices)
- [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
- [Refactoring at Scale](#refactoring-at-scale)

## Pre-Refactoring Checklist

Before starting any refactoring, ensure:

```markdown
Pre-Refactoring Checklist:
- [ ] Comprehensive test coverage exists (80%+)
- [ ] All tests currently pass
- [ ] Version control: working directory clean
- [ ] Understand what code does
- [ ] Know why refactoring is needed
- [ ] Have clear goal for improvement
- [ ] Allocated sufficient time
- [ ] Team is aware (for significant refactoring)
- [ ] Backup/branch created
- [ ] IDE refactoring tools configured
```

### Understanding the Code

**Don't refactor what you don't understand.**

Steps to gain understanding:
1. **Read the code** - Trace execution paths
2. **Add logging** - See runtime behavior
3. **Write tests** - Document expected behavior
4. **Talk to authors** - Get context and history
5. **Review git history** - Understand evolution
6. **Document findings** - Create knowledge

### Coverage Requirements

Minimum test coverage before refactoring:

| Risk Level | Coverage Required |
|------------|-------------------|
| Low (simple functions) | 70%+ |
| Medium (business logic) | 85%+ |
| High (critical paths) | 95%+ |
| Mission Critical | 100% |

### Time Allocation

Budget time conservatively:

- **Simple refactoring**: 2x estimated time
- **Medium complexity**: 3x estimated time
- **Complex/legacy**: 5x estimated time

Why? Testing, unexpected issues, learning.

## Safe Refactoring Workflow

### The Basic Cycle

```
1. GREEN: Ensure all tests pass
2. REFACTOR: Make small, focused change
3. GREEN: Run tests immediately
4. COMMIT: Save working code
5. REPEAT: Next small change
```

### Detailed Workflow

#### Step 1: Prepare

```markdown
Preparation:
- [ ] Checkout new branch: `git checkout -b refactor/improve-user-service`
- [ ] Run full test suite: `npm test` or `pytest`
- [ ] Verify all tests pass
- [ ] Note current metrics (lines, complexity, coverage)
```

#### Step 2: Identify Target

```markdown
Identify:
- [ ] What code smells exist?
- [ ] What specific improvement to make?
- [ ] What is the goal? (readability, performance, testability)
- [ ] How to measure success?
```

#### Step 3: Plan Small Steps

Break large refactoring into incremental steps.

**Example**: Decompose god class

```markdown
Steps:
1. Extract user validation to UserValidator class
2. Tests pass → Commit
3. Extract email logic to EmailService class
4. Tests pass → Commit
5. Extract database logic to UserRepository class
6. Tests pass → Commit
7. Simplify remaining UserService class
8. Tests pass → Commit
```

#### Step 4: Execute One Step

Make **one small change**:
- Extract method
- Rename variable
- Move method
- Simplify conditional

#### Step 5: Test Immediately

```bash
# Run affected tests
npm test -- src/users/

# Run full suite periodically
npm test
```

If tests fail:
- **Don't proceed** - Fix or revert
- **Understand why** - Bug in code or tests?
- **Try again** - Smaller step or different approach

#### Step 6: Commit Working Code

```bash
git add .
git commit -m "refactor: Extract user validation to separate class"
```

Commit often - every successful refactoring step.

#### Step 7: Evaluate and Continue

```markdown
Evaluate:
- [ ] Tests passing?
- [ ] Code improved?
- [ ] Ready for next step?
- [ ] Or done with this refactoring?
```

### Emergency Rollback

If things go wrong:

```bash
# Undo uncommitted changes
git reset --hard HEAD

# Undo last commit (keep changes)
git reset HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Return to last known good state
git checkout main
```

## Testing Best Practices

### Types of Tests for Refactoring

#### 1. Unit Tests

Test individual functions in isolation.

```python
# Unit test
def test_calculate_discount():
    assert calculate_discount(100, 'GOLD') == 10
    assert calculate_discount(100, 'SILVER') == 5
    assert calculate_discount(100, 'BRONZE') == 0
```

**When**: Before refactoring any function

#### 2. Integration Tests

Test components working together.

```python
# Integration test
def test_order_processing_flow():
    order = create_order(items=[item1, item2])
    result = order_service.process(order)

    assert result.status == 'COMPLETED'
    assert_database_has_order(order.id)
    assert_email_sent_to(order.customer.email)
```

**When**: Before refactoring service interactions

#### 3. Characterization Tests

Document existing behavior of legacy code.

```python
# Characterization test
def test_legacy_calculation_current_behavior():
    """
    Documents current behavior of legacy system.
    TODO: This behavior seems wrong but is currently expected.
    """
    result = legacy_calculate_price(item_price=100, quantity=2)
    assert result == 195  # Why 195 and not 200? Bug or feature?
```

**When**: Before refactoring legacy code you don't understand

#### 4. Regression Tests

Verify refactoring didn't break anything.

```python
# Regression test suite
@pytest.mark.regression
class TestOrderServiceRegression:
    def test_all_order_types_still_work(self):
        # Test each order type
        pass

    def test_edge_cases_still_handled(self):
        # Test boundary conditions
        pass
```

**When**: Run after each refactoring cycle

### Test-First Refactoring

When tests are missing:

```
1. Write characterization tests (document current behavior)
2. Ensure tests pass
3. Refactor code
4. Ensure tests still pass
5. Update tests if behavior should change
```

### Test Coverage Goals

Track coverage during refactoring:

```bash
# Python
pytest --cov=src --cov-report=html

# JavaScript
npm test -- --coverage

# Java
mvn test jacoco:report
```

Aim for:
- **Line coverage**: 85%+
- **Branch coverage**: 80%+
- **Function coverage**: 90%+

### Fast Test Suite

Keep tests fast for rapid feedback:

| Test Type | Target Time | Max Acceptable |
|-----------|-------------|----------------|
| Unit Tests | < 5 seconds | 15 seconds |
| Integration Tests | < 30 seconds | 1 minute |
| Full Suite | < 2 minutes | 5 minutes |

**Slow tests?** Refactor tests too:
- Mock external dependencies
- Use in-memory databases
- Parallelize test execution
- Split into fast/slow suites

## Commit Strategies

### Commit Frequency

**Commit early, commit often** during refactoring.

Ideal frequency:
- After each passing refactoring step (every 5-15 minutes)
- After each complete pattern application
- When reaching a stable state
- Before taking a break

### Commit Message Format

Use conventional commits:

```
refactor(scope): description

- Detailed explanation
- Why this refactoring
- What improved
```

**Examples**:

```bash
# Good commit messages
refactor(user-service): Extract validation to separate class
refactor(order): Replace magic numbers with named constants
refactor(auth): Simplify token validation logic
refactor(api): Remove duplicate error handling code

# Bad commit messages
refactor: changes
refactor: fix stuff
refactor: improvements
Update code
```

### Atomic Commits

Each commit should be:
- **Self-contained**: One logical change
- **Reversible**: Can be reverted independently
- **Testable**: Tests pass at this commit
- **Reviewable**: Easy to understand change

**Example**: Extracting a class

```bash
# Commit 1
refactor(user): Extract UserValidator interface

# Commit 2
refactor(user): Implement BasicUserValidator

# Commit 3
refactor(user): Integrate UserValidator into UserService

# Commit 4
refactor(user): Remove old validation code from UserService
```

Each commit is working code with passing tests.

### Branch Strategy

```bash
# Feature branches for refactoring
git checkout -b refactor/improve-user-validation

# Complete refactoring
# ...

# Merge to main
git checkout main
git merge refactor/improve-user-validation
```

For large refactorings:
```bash
# Create epic branch
git checkout -b refactor/user-service-overhaul

# Create sub-branches
git checkout -b refactor/user-service-validation
# Work, merge back to epic branch

git checkout refactor/user-service-overhaul
git checkout -b refactor/user-service-repository
# Work, merge back to epic branch

# Finally merge epic to main
```

## Code Review Guidelines

### Refactoring Pull Requests

#### PR Description Template

```markdown
## Refactoring Summary

**Goal**: Improve testability of OrderService

**Motivation**: Current code tightly couples business logic with database
access, making unit testing difficult.

**Approach**: Extract Repository pattern

**Changes**:
- Created OrderRepository interface
- Implemented PostgresOrderRepository
- Injected repository into OrderService
- Updated tests to use mock repository

**Metrics**:
- Before: 127 lines, complexity 18, 45% coverage
- After: 89 lines, complexity 8, 92% coverage

**Tests**: All existing tests pass + 15 new tests added

**Risk**: Low - behavior unchanged, comprehensive tests
```

#### Review Checklist

```markdown
Reviewer Checklist:
- [ ] Tests pass in CI
- [ ] Code behavior unchanged
- [ ] Complexity reduced (measured)
- [ ] Readability improved
- [ ] No performance degradation
- [ ] Naming conventions followed
- [ ] Documentation updated
- [ ] No mixed refactoring + features
- [ ] Commits are atomic
- [ ] Ready to merge
```

### Review Focus Areas

#### 1. Behavioral Preservation

**Verify**: External behavior unchanged

```python
# Before refactoring
def calculate(x, y):
    return x * y + 10

# After refactoring
def calculate_with_fee(price, quantity):
    total = price * quantity
    fee = get_processing_fee()
    return total + fee

# Reviewer checks: get_processing_fee() returns 10?
```

#### 2. Test Coverage

**Verify**: Tests cover refactored code

```bash
# Check coverage diff
git diff main..refactor/branch --coverage
```

#### 3. Complexity Reduction

**Verify**: Metrics improved

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines | 450 | 320 | -29% ✓ |
| Cyclomatic | 24 | 12 | -50% ✓ |
| Methods | 18 | 22 | +22% (OK - extracted) |

#### 4. No Hidden Changes

**Verify**: No sneaky bug fixes or features

```diff
# Red flag - behavior change hidden in refactoring
- def calculate_tax(amount):
-     return amount * 0.07
+ def calculate_tax(amount):
+     return amount * 0.08  # Tax rate changed!
```

### Giving Good Feedback

#### Constructive Comments

✅ **Good feedback**:
```
"Consider extracting this 15-line validation into a separate method
for better testability and reuse. Something like `validate_user_input()`."
```

❌ **Poor feedback**:
```
"This is messy."
```

#### Praise Improvements

```
"Excellent refactoring! The extracted methods make the flow much clearer,
and the naming really helps understand the business logic."
```

## Naming Conventions

### Intention-Revealing Names

Names should reveal **intention**, not implementation.

```python
# Bad names (implementation-focused)
def calc(x, y):
    return x * y * 1.08

# Good names (intention-focused)
def calculate_total_with_tax(price, quantity):
    subtotal = price * quantity
    total = apply_sales_tax(subtotal)
    return total
```

### Naming Principles

#### 1. Use Domain Language

```javascript
// Bad - technical jargon
function processUserDataStructure(ud) { }

// Good - domain language
function registerNewCustomer(customerInfo) { }
```

#### 2. Avoid Abbreviations

```java
// Bad
public void updUsrPrf(Usr u) { }

// Good
public void updateUserProfile(User user) { }
```

Exception: Well-known abbreviations (HTML, API, URL)

#### 3. Be Specific

```python
# Bad - vague
def get_data():
    return data

# Good - specific
def get_active_users_from_database():
    return database.query(User).filter_by(active=True).all()
```

#### 4. Use Consistent Vocabulary

```ruby
# Bad - inconsistent
def fetch_user
def retrieve_order
def get_product
def load_invoice

# Good - consistent
def get_user
def get_order
def get_product
def get_invoice
```

### Naming Patterns

#### Boolean Variables

Use `is`, `has`, `can`, `should`:

```typescript
// Good
const isActive = user.status === 'active';
const hasPermission = user.roles.includes('admin');
const canEdit = hasPermission && isActive;
const shouldNotify = user.preferences.notifications;
```

#### Collections

Use plural names:

```python
# Good
users = get_all_users()
active_orders = filter_active(orders)
pending_items = [item for item in items if item.pending]
```

#### Functions

Use verbs:

```javascript
// Good - verbs indicate actions
function calculateTotal() { }
function validateInput() { }
function sendEmail() { }
function transformData() { }
```

### Refactoring Naming

When refactoring, rename systematically:

```
1. Identify poorly named element
2. Understand its true purpose
3. Choose intention-revealing name
4. Use IDE rename refactoring (updates all references)
5. Run tests
6. Commit
```

## Architecture Best Practices

### SOLID Principles

#### Single Responsibility Principle

Each class/module should have one reason to change.

```python
# Bad - multiple responsibilities
class UserManager:
    def save_user(self, user):
        db.save(user)

    def send_welcome_email(self, user):
        email.send(user.email, "Welcome!")

    def log_activity(self, action):
        logger.write(action)

# Good - single responsibilities
class UserRepository:
    def save(self, user):
        db.save(user)

class EmailService:
    def send_welcome_email(self, user):
        email.send(user.email, "Welcome!")

class ActivityLogger:
    def log(self, action):
        logger.write(action)
```

#### Open/Closed Principle

Open for extension, closed for modification.

```javascript
// Bad - must modify for new types
function calculateArea(shape) {
    if (shape.type === 'circle') {
        return Math.PI * shape.radius ** 2;
    } else if (shape.type === 'square') {
        return shape.side ** 2;
    }
    // Must modify function to add triangle
}

// Good - extend without modification
class Shape {
    calculateArea() { throw new Error('Must implement'); }
}

class Circle extends Shape {
    calculateArea() { return Math.PI * this.radius ** 2; }
}

class Square extends Shape {
    calculateArea() { return this.side ** 2; }
}

// Add Triangle without modifying existing code
class Triangle extends Shape {
    calculateArea() { return 0.5 * this.base * this.height; }
}
```

#### Dependency Inversion Principle

Depend on abstractions, not concretions.

```python
# Bad - depends on concrete implementation
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Tightly coupled

# Good - depends on abstraction
class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository  # Loosely coupled

# Can inject any implementation
service = OrderService(PostgresOrderRepository())
# or
service = OrderService(MongoOrderRepository())
# or
service = OrderService(MockOrderRepository())  # For testing
```

### Layered Architecture

Organize code in layers:

```
Presentation Layer (UI/API)
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (Repositories)
    ↓
Database
```

**Rules**:
- Layer can depend on layer below
- Layer cannot depend on layer above
- Skip layers only with good reason

### Modularity

Create cohesive, loosely coupled modules:

```
src/
├── users/
│   ├── user.model.ts
│   ├── user.repository.ts
│   ├── user.service.ts
│   └── user.controller.ts
├── orders/
│   ├── order.model.ts
│   ├── order.repository.ts
│   ├── order.service.ts
│   └── order.controller.ts
└── shared/
    ├── database.ts
    ├── logger.ts
    └── validator.ts
```

## Performance Considerations

### Measure Before Optimizing

**Never assume** - always profile:

```bash
# Python profiling
python -m cProfile -o profile.stats script.py

# Node.js profiling
node --prof app.js

# Browser profiling
# Use Chrome DevTools Performance tab
```

### Refactoring vs Optimization

**Refactoring**: Improve structure, preserve performance
**Optimization**: Improve performance, may compromise structure

**Do both**, but separately:
1. First refactor for clarity
2. Then optimize hot paths
3. Keep optimized code well-documented

### Performance-Safe Refactorings

These typically don't hurt performance:
- Extract method (inline by compiler)
- Rename variables
- Move method to better class
- Extract constant
- Simplify conditionals

### Performance-Risky Refactorings

These might hurt performance:
- Adding abstraction layers
- Introducing polymorphism
- Moving from iteration to recursion
- Adding indirection

**Solution**: Measure before and after.

### Example: Performance-Aware Refactoring

```python
# Original - fast but unclear
def process(items):
    return [i*2 for i in items if i > 10]

# Refactored - clearer
def process(items):
    filtered = filter_large_items(items)
    doubled = double_values(filtered)
    return doubled

def filter_large_items(items):
    return [i for i in items if i > THRESHOLD]

def double_values(items):
    return [i * MULTIPLIER for i in items]

# Performance check: measure both
import timeit
timeit.timeit(lambda: original_process(data), number=10000)
timeit.timeit(lambda: refactored_process(data), number=10000)
# If refactored is significantly slower, optimize
```

## Team Collaboration

### Communicating Refactoring Plans

For significant refactorings:

```markdown
# Refactoring Proposal

## What
Refactor OrderService to extract repository pattern

## Why
- Current code tightly couples business logic with SQL
- Unit testing requires database (slow tests)
- Adding new database type requires changing OrderService

## Approach
1. Create OrderRepository interface
2. Extract database code to PostgresOrderRepository
3. Update OrderService to use repository
4. Update tests

## Impact
- Files affected: 8
- Time estimate: 2 days
- Risk: Low (comprehensive tests exist)

## Timeline
- Day 1: Extract repository, update tests
- Day 2: Review, merge, verify production

## Questions?
Discuss in #engineering channel
```

### Pair Refactoring

Two developers, one keyboard:
- **Driver**: Types code
- **Navigator**: Reviews, suggests, thinks ahead

**Benefits**:
- Knowledge sharing
- Fewer mistakes
- Better solutions
- Real-time review

### Mob Refactoring

Whole team refactors together:

**When**:
- Complex legacy code
- Architectural changes
- Learning opportunity
- Cross-team dependencies

### Refactoring Backlog

Track refactoring opportunities:

```markdown
# Tech Debt Backlog

## High Priority
- [ ] OrderService: Extract repository pattern
- [ ] PaymentService: Remove duplicate validation logic
- [ ] UserController: Simplify 200-line action method

## Medium Priority
- [ ] Replace string error codes with enums
- [ ] Add type hints to Python codebase
- [ ] Extract shared utilities to library

## Low Priority
- [ ] Rename variables in ReportGenerator
- [ ] Update old-style JavaScript to ES6
- [ ] Improve logging consistency
```

## Documentation Practices

### When to Update Documentation

Update documentation when refactoring changes:
- **Public APIs**: Method signatures, parameters, return types
- **Architecture**: Component relationships, dependencies
- **Setup**: Installation, configuration
- **Usage Examples**: If code structure changes

### Don't Document What's Obvious

```python
# Bad - redundant documentation
def get_user_by_id(user_id):
    """Gets a user by ID."""  # Obvious from name
    return db.query(User).get(user_id)

# Good - document non-obvious aspects
def get_user_by_id(user_id):
    """
    Retrieves user from database by ID.

    Returns None if user not found (doesn't raise exception).
    Includes related profile data via eager loading for performance.
    """
    return db.query(User).options(joinedload(User.profile)).get(user_id)
```

### Architecture Decision Records

Document significant refactoring decisions:

```markdown
# ADR-015: Extract Repository Pattern from OrderService

## Context
OrderService directly executes SQL queries, making testing difficult
and coupling business logic to database implementation.

## Decision
Extract repository pattern with interface-based design.

## Consequences
**Positive**:
- Unit tests no longer need database
- Can swap database implementations
- Clearer separation of concerns

**Negative**:
- Additional abstraction layer
- More files to maintain
- Learning curve for team

## Alternatives Considered
- Active Record pattern: Too much coupling
- Query builders: Still couples to SQL
```

## Common Pitfalls to Avoid

### 1. Refactoring Without Tests

**Pitfall**: "I'll just quickly refactor this..."
**Result**: Broke something, don't know what
**Solution**: Write tests first, always

### 2. Too Big Steps

**Pitfall**: Refactor 10 things at once
**Result**: Tests fail, can't identify cause
**Solution**: One small change at a time

### 3. Mixing Concerns

**Pitfall**: Refactor + fix bug + add feature
**Result**: Impossible to review or debug
**Solution**: Separate commits for each concern

### 4. Premature Abstraction

**Pitfall**: Extract for every duplication
**Result**: Over-engineered, harder to understand
**Solution**: Rule of three - abstract on third occurrence

### 5. Ignoring Performance

**Pitfall**: "Premature optimization is evil"
**Result**: 10x slower code
**Solution**: Measure before and after

### 6. Refactoring Under Pressure

**Pitfall**: Refactor with tight deadline
**Result**: Rushed, broken, or abandoned
**Solution**: Note debt, schedule proper time

### 7. Perfectionism

**Pitfall**: Must make code perfect
**Result**: Endless refactoring, never done
**Solution**: Good enough is good enough; iterate

### 8. Not Getting Buy-In

**Pitfall**: Surprise team with big refactoring
**Result**: Merge conflicts, confusion
**Solution**: Communicate plans early

## Refactoring at Scale

### Large Codebase Strategies

#### Strangler Fig Pattern

Gradually replace old system:

```
1. Identify subsystem to replace
2. Create new implementation alongside old
3. Route new requests to new system
4. Gradually migrate old data/users
5. Remove old system when unused
```

#### Branch by Abstraction

Refactor without breaking main branch:

```
1. Create abstraction over current implementation
2. Switch all callers to use abstraction
3. Create new implementation
4. Switch abstraction to use new implementation
5. Remove old implementation
```

### Coordinating Team Refactoring

#### Communication Plan

```markdown
Team Refactoring Plan:

## What's Changing
UserService → UserRepository pattern

## Who's Affected
- Backend team (primary)
- API team (consumers)
- QA team (tests)

## Timeline
- Week 1: Create repository interface
- Week 2: Migrate UserService
- Week 3: Migrate AdminService
- Week 4: Remove old code

## Migration Guide
[Link to document]

## Questions
#refactoring-userservice Slack channel
```

#### Incremental Rollout

1. **Feature flag**: New code behind flag
2. **Canary**: Test with 5% traffic
3. **Gradual increase**: 25%, 50%, 100%
4. **Monitor**: Watch metrics closely
5. **Rollback plan**: Quick revert if issues

## Summary

### Key Best Practices

1. **Test first** - Comprehensive coverage before refactoring
2. **Small steps** - Incremental changes with frequent testing
3. **Commit often** - Each successful step committed
4. **Separate hats** - Never mix refactoring with features
5. **Measure** - Track metrics to verify improvement
6. **Communicate** - Keep team informed of plans
7. **Review** - Get feedback on significant refactorings
8. **Document** - Update docs when structure changes
9. **Iterate** - Good enough now, perfect later
10. **Sustainable pace** - Don't refactor under pressure

### Next Steps

- Study [Refactoring Patterns](patterns.md) for specific techniques
- Practice with [Examples](../examples/)
- Use [Checklists](../resources/checklists.md) during work
- Review [Troubleshooting](troubleshooting.md) for common issues
