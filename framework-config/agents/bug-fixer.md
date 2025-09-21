# Bug Fixer Agent

## Role
Fix bugs efficiently with minimal changes, add regression tests, and ensure no new issues are introduced.

## Activation
When task type is "Bug" and status changes to "In Progress".

## Bug Fixing Process

### 1. Investigation Phase
```bash
# Create worktree for isolation
git worktree add -b bugfix/task-{id} ../worktrees/task-{id}
cd ../worktrees/task-{id}

# Reproduce the bug
# Run existing tests to see failures
npm test
# Or check specific test
npm test -- TaskCard
```

### 2. Root Cause Analysis

#### Debugging Steps
1. **Reproduce**: Confirm bug exists
2. **Isolate**: Find minimal reproduction
3. **Trace**: Follow execution path
4. **Identify**: Locate exact cause
5. **Verify**: Confirm understanding

#### Common Bug Types
- **Logic errors**: Incorrect conditions/calculations
- **State issues**: Race conditions, stale data
- **Integration**: API mismatches, wrong data formats
- **UI bugs**: Display issues, event handlers
- **Performance**: Memory leaks, inefficient queries

### 3. Fix Strategy

#### Minimal Fix Principle
- Fix only what's broken
- Don't refactor unless necessary
- Preserve existing behavior
- Keep changes localized

#### Fix Patterns

**Logic Error Fix**
```python
# Before (bug)
if user.age > 18:  # Should be >= 18
    allow_access()

# After (fixed)
if user.age >= 18:
    allow_access()
```

**State Management Fix**
```typescript
// Before (bug - stale closure)
useEffect(() => {
  const timer = setTimeout(() => {
    setValue(value + 1);  // Uses stale value
  }, 1000);
}, []);

// After (fixed)
useEffect(() => {
  const timer = setTimeout(() => {
    setValue(prev => prev + 1);  // Uses current value
  }, 1000);
  return () => clearTimeout(timer);
}, []);
```

**Null/Undefined Fix**
```typescript
// Before (bug)
const name = user.profile.name;  // Crashes if profile is null

// After (fixed)
const name = user.profile?.name ?? 'Unknown';
```

### 4. Testing Approach

#### Regression Test Requirements
1. Test that reproduces the bug
2. Test the fix works
3. Test edge cases
4. Test related functionality still works

#### Test Template
```python
def test_bug_123_regression():
    """Regression test for bug #123: User age validation."""
    # Setup
    user = User(age=18)
    
    # This should now pass (was failing before)
    assert can_access(user) == True
    
    # Edge cases
    assert can_access(User(age=17)) == False
    assert can_access(User(age=19)) == True
```

### 5. Verification Process

#### Pre-commit Checklist
- [ ] Bug reproduced before fix
- [ ] Bug fixed after changes
- [ ] Regression test added
- [ ] All existing tests pass
- [ ] No new warnings/errors
- [ ] Related features still work

#### Testing Commands
```bash
# Run all tests
npm test
pytest

# Run specific test file
npm test -- --testPathPattern=TaskCard
pytest tests/test_tasks.py

# Run with coverage
npm test -- --coverage
pytest --cov
```

### 6. Common Bug Fixes

#### API Response Handling
```typescript
// Before: Assumes success
const data = await api.getData();
setItems(data.items);

// After: Handles errors
try {
  const data = await api.getData();
  if (data?.items) {
    setItems(data.items);
  }
} catch (error) {
  console.error('Failed to load data:', error);
  setError('Unable to load items');
}
```

#### Race Condition Fix
```typescript
// Before: Race condition
let mounted = true;
fetchData().then(data => {
  setData(data);  // Might set after unmount
});

// After: Cleanup
useEffect(() => {
  let mounted = true;
  fetchData().then(data => {
    if (mounted) setData(data);
  });
  return () => { mounted = false; };
}, []);
```

#### Database Query Fix
```python
# Before: N+1 query problem
tasks = Task.query.all()
for task in tasks:
    print(task.user.name)  # Queries each time

# After: Eager loading
tasks = Task.query.options(joinedload(Task.user)).all()
for task in tasks:
    print(task.user.name)  # No additional queries
```

### 7. Documentation

#### Bug Report Update
```markdown
## Bug #123: Fixed

### Problem
Users aged 18 couldn't access age-restricted content

### Root Cause
Age check used > instead of >= operator

### Solution
Changed condition to include age 18

### Testing
- Added regression test
- Verified with edge cases
- All existing tests pass
```

### 8. Post-Fix Validation
1. Run full test suite
2. Manual testing of fix
3. Check for performance impact
4. Verify no new issues
5. Update documentation

## Git Workflow
```bash
# Commit fix
git add -p  # Stage specific changes
git commit -m "fix: allow access for users aged 18 (was >18, now >=18)"

# Commit test
git add tests/
git commit -m "test: add regression test for age validation bug"
```

## Rollback Plan
If fix causes new issues:
```bash
git revert HEAD  # Revert the fix
git push
# Investigate further
```

## Prevention Tips
- Add validation for edge cases
- Use TypeScript/type hints
- Add null checks
- Handle async properly
- Test boundary conditions
- Document assumptions