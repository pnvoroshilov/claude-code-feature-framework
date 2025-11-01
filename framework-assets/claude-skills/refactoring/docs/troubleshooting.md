# Refactoring Troubleshooting Guide

Common problems encountered during refactoring and their solutions.

## Table of Contents

- [Tests Breaking](#tests-breaking)
- [Performance Degradation](#performance-degradation)
- [Merge Conflicts](#merge-conflicts)
- [Scope Creep](#scope-creep)
- [Team Resistance](#team-resistance)
- [Lost in Complexity](#lost-in-complexity)
- [Incomplete Refactoring](#incomplete-refactoring)
- [Production Issues](#production-issues)

## Tests Breaking

### Problem: Tests Fail After Refactoring

**Symptoms**:
- Previously passing tests now fail
- Unclear which change caused failure
- Multiple tests failing at once

**Root Causes**:
1. Changed behavior unintentionally
2. Tests coupled to implementation
3. Steps too large
4. Forgot to update test expectations

### Solution 1: Revert and Take Smaller Steps

```bash
# Undo your changes
git reset --hard HEAD

# Start over with smaller steps
git commit -m "refactor: Extract validation method (step 1 of 5)"
# Tests pass

git commit -m "refactor: Move validation to validator class (step 2 of 5)"
# Tests pass

# Continue incrementally
```

### Solution 2: Fix Tests, Not Code

Sometimes tests need updating:

```python
# Test coupled to implementation
def test_process_order():
    order = Order()
    assert order._internal_state == 'PENDING'  # Testing private state

# Better: Test behavior, not implementation
def test_process_order():
    order = Order()
    assert order.is_pending()  # Test public behavior
```

### Solution 3: Isolate the Breaking Change

```bash
# Binary search through commits
git bisect start
git bisect bad HEAD
git bisect good HEAD~10

# Git will checkout commits - run tests at each
npm test

git bisect good  # If tests pass
git bisect bad   # If tests fail

# Git identifies exact breaking commit
```

### Prevention

- ✅ Run tests after EVERY change
- ✅ Commit after each passing step
- ✅ Keep changes small
- ✅ Test behavior, not implementation

## Performance Degradation

### Problem: Refactored Code is Slower

**Symptoms**:
- API endpoints timing out
- Page load times increased
- Background jobs taking longer
- Database queries slower

**Root Causes**:
1. Added unnecessary abstraction layers
2. Introduced N+1 queries
3. Removed caching
4. Changed algorithm complexity

### Solution 1: Profile and Compare

```python
import cProfile
import time

# Before refactoring
def original_implementation():
    # ...

# After refactoring
def refactored_implementation():
    # ...

# Compare
start = time.time()
original_implementation()
print(f"Original: {time.time() - start}s")

start = time.time()
refactored_implementation()
print(f"Refactored: {time.time() - start}s")
```

### Solution 2: Check for N+1 Queries

**Problem**:
```python
# Refactored to use relationships - introduced N+1!
users = User.query.all()
for user in users:
    print(user.profile.bio)  # Separate query for each user
```

**Fix**:
```python
# Eager load relationships
users = User.query.options(joinedload(User.profile)).all()
for user in users:
    print(user.profile.bio)  # No additional queries
```

### Solution 3: Add Caching Back

```python
# Refactored version lost caching
def get_user_recommendations(user_id):
    return expensive_calculation(user_id)

# Add caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_recommendations(user_id):
    return expensive_calculation(user_id)
```

### Solution 4: Optimize Hot Paths

Keep hot paths optimized even if less "clean":

```python
# Refactored version (clean but slow)
def calculate_total(items):
    return sum([self.calculate_item_price(item) for item in items])

def calculate_item_price(self, item):
    return item.price * item.quantity

# Optimized (less DRY but faster for hot path)
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity  # Inline for performance
    return total
```

### Prevention

- ✅ Profile before refactoring (baseline)
- ✅ Profile after refactoring (comparison)
- ✅ Load test critical paths
- ✅ Monitor production metrics

## Merge Conflicts

### Problem: Massive Merge Conflicts

**Symptoms**:
- Hundreds of conflicting lines
- Other team members blocked
- Conflicts in unexpected files
- Can't merge to main

**Root Causes**:
1. Long-running branch
2. Didn't sync with main regularly
3. Refactoring overlapped with feature work
4. Too many files changed at once

### Solution 1: Rebase Regularly

```bash
# While working on refactoring branch
git checkout refactor/my-branch

# Pull latest main
git fetch origin main

# Rebase onto main (resolve conflicts incrementally)
git rebase origin/main

# Resolve conflicts as they appear
git add .
git rebase --continue
```

### Solution 2: Break into Smaller PRs

```bash
# Instead of one large PR
git checkout -b refactor/extract-validation
# Extract validation only
git push origin refactor/extract-validation
# Create PR, merge

git checkout main
git pull

git checkout -b refactor/extract-repository
# Extract repository only
git push origin refactor/extract-repository
# Create PR, merge

# Smaller PRs = smaller conflicts
```

### Solution 3: Coordinate with Team

```markdown
# Post in team channel
"Planning to refactor UserService over next 2 weeks.
Files affected:
- src/services/user_service.py
- src/repositories/user_repository.py
- tests/services/test_user_service.py

Please coordinate if working in these areas.
Slack: #refactoring-coordination"
```

### Prevention

- ✅ Sync with main daily
- ✅ Keep branches short-lived (< 2 days)
- ✅ Communicate plans early
- ✅ Use feature flags for parallel work

## Scope Creep

### Problem: Refactoring Never Finishes

**Symptoms**:
- "Just one more thing..."
- Branch grows to 100+ files
- Timeline keeps extending
- Original goal unclear

**Root Causes**:
1. Perfectionism
2. No clear scope definition
3. Finding more issues while refactoring
4. Trying to fix everything at once

### Solution 1: Define Clear Scope

```markdown
# Refactoring Scope Document

## Goal
Extract repository pattern from UserService

## In Scope
- Create UserRepository interface
- Implement PostgresUserRepository
- Update UserService to use repository
- Update tests

## Out of Scope
- Refactoring OrderService (separate task)
- Adding new features (separate task)
- Improving performance (separate task)
- Rewriting tests (separate task)

## Done When
- [ ] UserService has no SQL queries
- [ ] All tests pass
- [ ] Code review approved
- [ ] Deployed to production
```

### Solution 2: Track Technical Debt Separately

```python
# While refactoring, don't fix everything
def process_order(order):
    validate_order(order)

    # TODO: This error handling is messy (create separate ticket)
    try:
        save_order(order)
    except Exception as e:
        log.error(e)
        return False

    return True
```

Create tickets for additional issues:
```markdown
Tech Debt Backlog:
- [ ] #1234: Improve error handling in process_order
- [ ] #1235: Add logging to OrderService
- [ ] #1236: Extract email service from OrderService
```

### Solution 3: Time-Box Refactoring

```markdown
Refactoring Time Budget:
- Week 1: Extract repository
- Week 2: Update tests and review
- Week 3: Deploy

If not done by Week 3, reassess scope.
```

### Prevention

- ✅ Document scope before starting
- ✅ Track additional issues separately
- ✅ Set time limits
- ✅ Review progress daily

## Team Resistance

### Problem: Team Doesn't Support Refactoring

**Symptoms**:
- "We don't have time for this"
- "It works fine as is"
- "Focus on features"
- PRs sit unreviewed

**Root Causes**:
1. Value not communicated
2. Previous failed refactoring
3. Deadline pressure
4. Team doesn't see pain

### Solution 1: Quantify the Problem

```markdown
# Refactoring Business Case

## Current Pain Points
- Bug fix in UserService takes 2 days (tight coupling)
- 45% of bugs in last quarter from UserService
- New developers take 2 weeks to understand code
- Feature velocity down 30% in this area

## Proposed Solution
Extract repository pattern from UserService

## Expected Benefits
- Bug fixes: 2 days → 4 hours (75% faster)
- Bug rate: Reduce by 50%
- Onboarding: 2 weeks → 3 days
- Velocity: Increase by 25%

## Investment
- 2 developers for 2 weeks
- Low risk (comprehensive tests exist)

## ROI
Break-even in 1 month, ongoing benefits
```

### Solution 2: Start Small, Show Results

```markdown
# Pilot Refactoring

Week 1: Extract one method
Result: Tests run 30% faster

Week 2: Extract validation class
Result: Found 3 bugs during extraction

Week 3: Add tests to increase coverage
Result: Caught regression that would have hit production

Team sees value → Support grows
```

### Solution 3: Align with Features

```markdown
# Feature-Driven Refactoring

Product: "We need to add social login"
Dev: "Current auth code is tangled. Let's:
  1. Refactor auth to be extensible (2 days)
  2. Add social login (1 day)

Total: 3 days

Without refactoring:
  - Hack in social login (3 days)
  - Create tech debt
  - Next auth feature even harder"
```

### Prevention

- ✅ Show business value
- ✅ Start with quick wins
- ✅ Align refactoring with features
- ✅ Share success stories

## Lost in Complexity

### Problem: Can't Figure Out How to Refactor

**Symptoms**:
- Code is too complex to understand
- Don't know where to start
- Every change breaks something
- Overwhelmed by dependencies

**Root Causes**:
1. Lack of understanding
2. No tests to verify behavior
3. Too many responsibilities tangled together
4. Trying to fix everything at once

### Solution 1: Map the Code

```python
# Create understanding through documentation

"""
UserService Responsibilities (TOO MANY!):
1. Validation (lines 50-120)
2. Database access (lines 121-200)
3. Email sending (lines 201-250)
4. Logging (lines 251-280)
5. Caching (lines 281-320)

Dependencies:
- PostgreSQL database
- SMTP email server
- Redis cache
- Logging service

Called By:
- UserController (main path)
- AdminController (admin path)
- BackgroundJobService (batch processing)
"""
```

### Solution 2: Add Tests First

```python
# Characterization tests to understand behavior

def test_create_user_happy_path():
    """Document normal user creation"""
    user = service.create_user("test@example.com", "password")
    assert user.email == "test@example.com"
    # Email sent? Check email service
    # Database updated? Check DB
    # Cached? Check cache

def test_create_user_duplicate_email():
    """Document error handling"""
    service.create_user("test@example.com", "password")
    with pytest.raises(DuplicateEmailError):
        service.create_user("test@example.com", "password2")
```

### Solution 3: Extract One Thing at a Time

```python
# Don't refactor everything - extract one responsibility

# Step 1: Extract validation (easiest)
class UserValidator:
    def validate_email(self, email):
        if '@' not in email:
            raise InvalidEmailError()

# Step 2: Use in service
class UserService:
    def __init__(self):
        self.validator = UserValidator()

    def create_user(self, email, password):
        self.validator.validate_email(email)  # Extracted
        # ... rest of complex code unchanged
```

### Solution 4: Ask for Help

```markdown
# Code Review Request

"I'm refactoring UserService but it's very complex.
Looking for input on approach:

Option 1: Extract validation first (safest)
Option 2: Extract repository first (most value)
Option 3: Add tests first (slowest but safest)

Which would you recommend?"
```

### Prevention

- ✅ Document code structure before refactoring
- ✅ Add tests to understand behavior
- ✅ Extract one responsibility at a time
- ✅ Collaborate with team

## Incomplete Refactoring

### Problem: Refactoring Left Half-Done

**Symptoms**:
- Two ways to do the same thing
- Mix of old and new patterns
- TODO comments everywhere
- Tech debt increased, not decreased

**Root Causes**:
1. Lost interest/motivation
2. Got pulled to other work
3. Harder than expected
4. No clear completion criteria

### Solution 1: Define "Done"

```markdown
# Refactoring Done Criteria

## Must Have
- [ ] All UserService methods use repository
- [ ] No SQL queries in UserService
- [ ] All tests passing
- [ ] Code review approved
- [ ] Merged to main

## Nice to Have (separate tickets)
- [ ] Extract email service
- [ ] Add caching layer
- [ ] Improve logging
```

### Solution 2: Complete or Revert

```bash
# Option 1: Complete the refactoring
# Commit next 2 days to finishing

# Option 2: Revert and defer
git revert abc123..def456
# Create ticket for future: "Refactor UserService - extract repository"
```

### Solution 3: Feature Flag Incomplete Work

```python
# Allow gradual completion

class UserService:
    def __init__(self, use_new_repository=False):
        self.use_new = use_new_repository

    def get_user(self, user_id):
        if self.use_new:
            return self.repository.find(user_id)  # New way
        else:
            return self.db.query("SELECT * ...")  # Old way

# Finish migration when time permits
```

### Prevention

- ✅ Define "done" before starting
- ✅ Allocate sufficient time
- ✅ Protect time from interruptions
- ✅ Complete what you start

## Production Issues

### Problem: Refactoring Broke Production

**Symptoms**:
- 500 errors in production
- Data corruption
- Performance degradation
- User complaints

**Root Causes**:
1. Insufficient testing
2. Behavior changed unintentionally
3. Environment differences
4. Race conditions in concurrent code

### Solution 1: Immediate Rollback

```bash
# Quick rollback
git revert <refactoring-commits>
git push origin main

# Or roll back deployment
kubectl rollout undo deployment/my-app

# Investigate after service restored
```

### Solution 2: Feature Flag Rollback

```python
# Toggle off new code without redeploying
class FeatureFlags:
    def use_refactored_user_service(self):
        return os.getenv('USE_REFACTORED_USER_SERVICE', 'false') == 'true'

# In production: set USE_REFACTORED_USER_SERVICE=false
```

### Solution 3: Gradual Rollout

```python
# Canary deployment: test with small % of traffic

class UserService:
    def get_user(self, user_id):
        if should_use_new_implementation(user_id):
            return self.new_get_user(user_id)
        else:
            return self.old_get_user(user_id)

def should_use_new_implementation(user_id):
    # Start with 1%, gradually increase
    return hash(user_id) % 100 < ROLLOUT_PERCENTAGE
```

### Post-Incident Review

```markdown
# Refactoring Incident Postmortem

## What Happened
Refactored UserService broke user login (500 errors)

## Root Cause
Changed error handling behavior:
- Old: returned None on invalid user
- New: raised UserNotFoundError

Frontend expected None, got exception.

## Why Not Caught
- Unit tests mocked error cases
- Integration tests used only valid users
- Staging environment had no invalid user attempts

## Fixes
1. Immediate: Rolled back deployment
2. Short-term: Added error handling compatibility
3. Long-term: Improved integration tests

## Prevention
- Add integration tests for error cases
- Deploy to staging with production data copy
- Canary deployments for refactorings
```

### Prevention

- ✅ Comprehensive testing (unit, integration, E2E)
- ✅ Test with production-like data
- ✅ Canary/gradual rollouts
- ✅ Monitor metrics during rollout
- ✅ Have rollback plan ready

## Quick Reference

### Troubleshooting Checklist

When things go wrong:

```markdown
- [ ] Can I revert immediately? (git reset/revert)
- [ ] Do tests identify the problem?
- [ ] Was my last step too large?
- [ ] Did I document what I was doing?
- [ ] Have I asked team for help?
- [ ] Should I take a break and come back fresh?
```

### Getting Unstuck

1. **Revert to last working state**
2. **Take smaller steps**
3. **Add more tests**
4. **Ask for help**
5. **Document the problem**
6. **Take a break**

## Summary

### Most Common Issues

1. **Tests breaking** → Smaller steps, commit often
2. **Performance regression** → Profile before/after
3. **Merge conflicts** → Sync regularly, smaller PRs
4. **Scope creep** → Define clear boundaries
5. **Team resistance** → Show value, start small
6. **Lost in complexity** → Document, test, extract one thing
7. **Incomplete refactoring** → Define "done", protect time
8. **Production issues** → Test thoroughly, rollout gradually

### Next Steps

- Review [Best Practices](best-practices.md) for prevention strategies
- Use [Checklists](../resources/checklists.md) to avoid issues
- Study [Examples](../examples/) for patterns that work
