# Core Refactoring Concepts

Fundamental principles, definitions, and mental models for effective code refactoring.

## Table of Contents

- [What is Refactoring](#what-is-refactoring)
- [Why Refactor](#why-refactor)
- [When to Refactor](#when-to-refactor)
- [When NOT to Refactor](#when-not-to-refactor)
- [The Refactoring Mindset](#the-refactoring-mindset)
- [Code Smells](#code-smells)
- [The Testing Safety Net](#the-testing-safety-net)
- [Small Steps Philosophy](#small-steps-philosophy)
- [Technical Debt](#technical-debt)
- [Refactoring Economics](#refactoring-economics)
- [The Two Hats Principle](#the-two-hats-principle)
- [Coupling and Cohesion](#coupling-and-cohesion)

## What is Refactoring

### Definition

**Refactoring** is a disciplined technique for restructuring existing code, altering its internal structure without changing its external behavior.

Key characteristics:
- **Behavior Preserving**: External functionality remains unchanged
- **Internal Improvement**: Code quality increases
- **Incremental**: Small, safe steps
- **Testable**: Verified at each step

### What Refactoring Is NOT

❌ **Not debugging**: Fixing bugs changes behavior
❌ **Not optimization**: Performance tuning may change behavior
❌ **Not rewriting**: Starting from scratch is different
❌ **Not adding features**: New functionality is separate
❌ **Not cleanup**: Reformatting alone isn't refactoring

### Example: Refactoring vs Not Refactoring

**Refactoring** (behavior preserved):
```python
# Before
def calc(x, y):
    return x * y + 10

# After - better naming, same behavior
def calculate_total_with_fee(price, quantity):
    return price * quantity + PROCESSING_FEE
```

**Not Refactoring** (behavior changed):
```python
# Before
def calc(x, y):
    return x * y + 10

# After - changed fee calculation (bug fix or feature)
def calculate_total_with_fee(price, quantity):
    fee = PROCESSING_FEE if price > 100 else 0
    return price * quantity + fee
```

## Why Refactor

### Primary Benefits

#### 1. Improved Readability
Code is read 10x more than written. Clear code saves time.

```python
# Hard to read
def p(d):
    t = 0
    for i in d:
        if i['s'] == 'A':
            t += i['p'] * 0.9
        else:
            t += i['p']
    return t

# Easy to read
def calculate_order_total(items):
    total = 0
    for item in items:
        if item['status'] == 'ACTIVE':
            total += item['price'] * ACTIVE_DISCOUNT
        else:
            total += item['price']
    return total
```

#### 2. Enhanced Maintainability
Changes are easier and safer in clean code.

**Before** (hard to maintain):
```javascript
function processUser(u) {
    if(u.age >= 18 && u.country === 'US' && u.verified) {
        // 50 lines of processing
    }
}
```

**After** (easy to maintain):
```javascript
function processUser(user) {
    if (!isEligibleUser(user)) return;

    performUserProcessing(user);
}

function isEligibleUser(user) {
    return user.age >= ADULT_AGE
        && user.country === SUPPORTED_COUNTRY
        && user.verified;
}
```

#### 3. Reduced Bugs
Simpler code has fewer hiding places for bugs.

#### 4. Faster Development
Clean code accelerates feature development by 2-3x.

#### 5. Better Testability
Refactored code is easier to test.

```python
# Hard to test (database coupled)
def get_user_score(user_id):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    score = (user.purchases * 10) + (user.reviews * 5)
    return score

# Easy to test (pure function)
def calculate_user_score(purchases, reviews):
    return (purchases * PURCHASE_WEIGHT) + (reviews * REVIEW_WEIGHT)

def get_user_score(user_id):
    user = db.get_user(user_id)
    return calculate_user_score(user.purchases, user.reviews)
```

### Secondary Benefits

- **Knowledge Transfer**: Clear code teaches new developers
- **Lower Cognitive Load**: Less mental overhead to understand
- **Team Morale**: Developers enjoy working with clean code
- **Risk Reduction**: Easier to spot and fix issues
- **Flexibility**: Easier to adapt to changing requirements

## When to Refactor

### The Rule of Three

First occurrence: write it
Second occurrence: notice duplication
Third occurrence: **refactor**

### Opportunistic Refactoring

Refactor when you touch code:
- **Preparatory Refactoring**: Before adding feature - "Make change easy, then make easy change"
- **Comprehension Refactoring**: When reading code - improve understanding
- **Litter-Pickup Refactoring**: Small improvements while passing through

### Planned Refactoring

Dedicate time to refactoring:
- **Technical Debt Sprints**: Scheduled cleanup work
- **Before Major Features**: Clean up area of planned changes
- **After Learning**: Apply new insights to existing code
- **Performance Refactoring**: Optimize based on profiling

### Signals It's Time to Refactor

- **Adding Feature is Hard**: Code structure resists changes
- **Understanding Takes Too Long**: Need to trace many levels
- **Testing is Difficult**: Can't isolate behavior
- **Bugs Keep Appearing**: Same area has repeated issues
- **Code Review Takes Forever**: Reviewers can't follow logic
- **You're Afraid to Touch It**: Fear indicates poor structure

## When NOT to Refactor

### Don't Refactor If:

#### 1. No Tests Exist
**Why**: Can't verify behavior preservation
**Instead**: Write characterization tests first

#### 2. Code Works and Never Changes
**Why**: Cost outweighs benefit
**Instead**: Leave it alone

#### 3. Rewrite Would Be Faster
**Why**: Complete mess beyond repair
**Instead**: Rewrite with tests

#### 4. You Don't Understand the Code
**Why**: Risk of breaking things
**Instead**: Study and document first

#### 5. Under Tight Deadline
**Why**: Refactoring needs time to do safely
**Instead**: Note technical debt, fix later

#### 6. External Behavior Must Change
**Why**: That's feature work or bug fixing
**Instead**: Fix bug or add feature first, then refactor

## The Refactoring Mindset

### Separate Hats

**Feature Hat**: Adding new behavior
**Refactoring Hat**: Improving structure

Never wear both simultaneously!

### Example Workflow

```
1. [Feature Hat] Write failing test for new feature
2. [Feature Hat] Make test pass (messy code OK)
3. [Refactoring Hat] Clean up code
4. [Refactoring Hat] Run tests
5. Commit
6. Repeat
```

### Incremental Improvement

Think compound interest: small daily improvements accumulate dramatically.

**Day 1**: 1% better
**Day 100**: 2.7x better
**Day 365**: 37x better

## Code Smells

Code smells are indicators that something might be wrong. They're not bugs, but signs of deeper problems.

### Common Code Smells

#### Long Method
**Smell**: Method > 50 lines
**Problem**: Does too many things
**Fix**: Extract Method

```python
# Smell: 80 line method
def process_order(order):
    # validation (20 lines)
    # calculation (20 lines)
    # persistence (20 lines)
    # notification (20 lines)
    pass

# Fixed: 4 focused methods
def process_order(order):
    validate_order(order)
    total = calculate_order_total(order)
    save_order(order)
    notify_customer(order)
```

#### Large Class
**Smell**: Class > 300 lines or > 20 methods
**Problem**: Too many responsibilities
**Fix**: Extract Class

#### Duplicate Code
**Smell**: Same code in multiple places
**Problem**: Changes require editing many places
**Fix**: Extract Method/Class

#### Long Parameter List
**Smell**: > 3-4 parameters
**Problem**: Hard to understand and use
**Fix**: Introduce Parameter Object

```java
// Smell: 6 parameters
public void createUser(String name, String email, int age,
                       String address, String phone, String city) {
    // ...
}

// Fixed: Parameter object
public void createUser(UserInfo userInfo) {
    // ...
}
```

#### Divergent Change
**Smell**: One class changes for multiple reasons
**Problem**: Violates Single Responsibility Principle
**Fix**: Extract Class

#### Shotgun Surgery
**Smell**: One change requires many small edits in many classes
**Problem**: Related code is scattered
**Fix**: Move Method, Inline Class

#### Feature Envy
**Smell**: Method uses another class more than its own
**Problem**: Wrong location
**Fix**: Move Method

```python
# Smell: feature envy
class Order:
    def calculate_shipping(self):
        cost = self.customer.address.state.tax_rate
        cost += self.customer.address.city.shipping_rate
        cost *= self.customer.shipping_preference.multiplier
        return cost

# Fixed: move to Customer
class Customer:
    def calculate_shipping_cost(self, order):
        cost = self.address.base_shipping_cost()
        cost *= self.shipping_preference.multiplier
        return cost
```

## The Testing Safety Net

### Why Tests Are Critical

Refactoring without tests is **rewriting**, not refactoring. Tests provide:
- **Confidence**: Know immediately if something breaks
- **Documentation**: Show expected behavior
- **Safety**: Enable bold improvements
- **Speed**: Automated verification

### Types of Tests for Refactoring

#### Unit Tests
Test individual functions/methods in isolation.

```python
def test_calculate_discount():
    assert calculate_discount(100) == 5
    assert calculate_discount(1000) == 50
    assert calculate_discount(50) == 0
```

#### Integration Tests
Test components working together.

```python
def test_order_processing():
    order = create_test_order()
    result = process_order(order)
    assert_order_saved(order.id)
    assert_email_sent(order.customer)
```

#### Characterization Tests
Document existing behavior before refactoring legacy code.

```python
def test_legacy_calculation_behavior():
    # Document what it does, even if not what it should do
    result = legacy_calculate(10, 5)
    assert result == 47  # Weird, but this is current behavior
```

### Test-Driven Refactoring

```
1. Ensure tests exist and pass (GREEN)
2. Refactor code (keeping tests green)
3. Run tests continuously
4. Commit when tests pass
```

## Small Steps Philosophy

### Why Small Steps

- **Safety**: Easy to undo
- **Speed**: Fast feedback loop
- **Confidence**: Know exactly what changed
- **Debugging**: Narrow scope when something breaks

### Example: Extracting Method in Steps

**Step 1**: Select code to extract
```python
def process():
    # ... other code ...
    x = calculate_something()
    y = calculate_other()
    result = x + y
    # ... more code ...
```

**Step 2**: Extract to new method (copy-paste)
```python
def extracted_calculation():
    x = calculate_something()
    y = calculate_other()
    result = x + y
    return result

def process():
    # ... other code ...
    x = calculate_something()
    y = calculate_other()
    result = x + y
    # ... more code ...
```

**Step 3**: Replace with call
```python
def process():
    # ... other code ...
    result = extracted_calculation()
    # ... more code ...
```

**Step 4**: Run tests → PASS → Commit

**Step 5**: Improve naming
```python
def calculate_total():
    x = calculate_something()
    y = calculate_other()
    result = x + y
    return result
```

**Step 6**: Run tests → PASS → Commit

### Frequency of Testing

Run tests:
- After each refactoring step (every 2-5 minutes)
- Before committing
- Before taking a break
- When in doubt

## Technical Debt

### What is Technical Debt

**Technical Debt**: Shortcuts taken during development that make future changes harder.

Like financial debt:
- **Principal**: Initial time saved
- **Interest**: Extra time each change takes
- **Bankruptcy**: Code becomes unmaintainable

### Types of Technical Debt

#### Deliberate Debt
Conscious decision to move fast now, pay later.

**Example**: "Ship MVP with known code issues, refactor after validating market"

#### Accidental Debt
Unintentional - didn't know better at the time.

**Example**: "Didn't know design patterns, created tightly coupled code"

#### Bit Rot
Code becomes outdated as technology evolves.

**Example**: "Written in 2015, uses deprecated APIs"

### Managing Technical Debt

#### Track It
Document debt items:
- Location in codebase
- Why it exists
- Impact on development
- Estimated cost to fix

#### Prioritize It
**High Priority** (fix soon):
- Code changed frequently
- Slows feature development
- Causes bugs

**Low Priority** (defer):
- Code rarely changes
- Isolated impact
- Working adequately

#### Pay It Down
- **Boy Scout Rule**: Leave code cleaner than found
- **Dedicated Time**: 20% time for technical debt
- **Before Features**: Refactor area before adding feature

## Refactoring Economics

### Cost-Benefit Analysis

#### Costs
- Time to refactor
- Risk of breaking something
- Testing effort

#### Benefits
- Faster future development
- Fewer bugs
- Lower maintenance cost
- Better team morale

### When Benefits Outweigh Costs

- **High-Change Areas**: Code modified frequently
- **Complex Logic**: Hard to understand code
- **Bug-Prone Code**: Repeated issues
- **Blocking Features**: Structure prevents new features
- **Onboarding Friction**: New developers struggle

### When Costs Outweigh Benefits

- **Low-Change Areas**: Code rarely touched
- **Working Adequately**: No pain points
- **Near End-of-Life**: Code being replaced soon
- **Stable Legacy**: Works, documented, understood

## The Two Hats Principle

### Feature Hat

**Goal**: Add new functionality
**Mindset**: Make it work
**Tests**: Add new tests
**Commits**: Feature changes

### Refactoring Hat

**Goal**: Improve structure
**Mindset**: Make it better
**Tests**: Keep existing tests passing
**Commits**: Refactoring changes

### Why Separate Hats

**Mixing hats leads to**:
- Harder code review
- Difficult debugging
- Unclear commits
- Risky changes

**Separate hats provides**:
- Clear intention
- Easy review
- Simple rollback
- Safe changes

### Example Git History

```
✅ Good (separate hats):
feat: Add user authentication
refactor: Extract auth validation
refactor: Simplify auth middleware
test: Add auth edge cases

❌ Bad (mixed hats):
feat: Add auth, refactor validators, fix bug in user service
```

## Coupling and Cohesion

### Coupling

**Definition**: Degree of interdependence between modules.

**Goal**: **Low coupling** - modules can change independently.

#### High Coupling (Bad)
```python
class Order:
    def save(self):
        conn = psycopg2.connect("dbname=prod")
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO orders VALUES ({self.id})")
        conn.commit()

        email = smtplib.SMTP('smtp.gmail.com')
        email.send(f"Order {self.id} confirmed")
```
Order class tightly coupled to database and email implementation.

#### Low Coupling (Good)
```python
class Order:
    def save(self):
        self.repository.save(self)
        self.notifier.send_confirmation(self)
```
Order class depends on abstractions, not implementations.

### Cohesion

**Definition**: Degree to which elements of a module belong together.

**Goal**: **High cohesion** - each module has single, well-defined purpose.

#### Low Cohesion (Bad)
```python
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def log_to_file(self): ...
    def calculate_tax(self): ...
    def generate_report(self): ...
```
Unrelated responsibilities mixed together.

#### High Cohesion (Good)
```python
class UserManager:
    def create_user(self): ...
    def update_user(self): ...
    def delete_user(self): ...
    def find_user(self): ...
```
All methods relate to user management.

### Ideal: Low Coupling + High Cohesion

```python
# High cohesion within each class
class UserRepository:
    def save(self, user): ...
    def find(self, id): ...
    def delete(self, id): ...

class EmailNotifier:
    def send_welcome(self, user): ...
    def send_confirmation(self, user): ...

class UserService:
    def __init__(self, repo, notifier):  # Low coupling via DI
        self.repo = repo
        self.notifier = notifier

    def register_user(self, user):
        self.repo.save(user)
        self.notifier.send_welcome(user)
```

## Summary

### Key Takeaways

1. **Refactoring preserves behavior** while improving structure
2. **Tests are mandatory** - they enable safe refactoring
3. **Small steps are faster** - incremental changes reduce risk
4. **Two hats principle** - separate feature work from refactoring
5. **Technical debt is real** - manage it proactively
6. **Low coupling + high cohesion** - architectural goal
7. **Refactor opportunistically** - little and often
8. **Economics matter** - balance costs and benefits

### Next Steps

- Read [Best Practices](best-practices.md) for safe refactoring workflows
- Study [Refactoring Patterns](patterns.md) for specific techniques
- Practice with [Basic Examples](../examples/basic/)
- Use [Checklists](../resources/checklists.md) during refactoring
