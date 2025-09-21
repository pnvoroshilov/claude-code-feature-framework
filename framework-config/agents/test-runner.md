# Test Runner Agent

## Role
Execute comprehensive testing when tasks move to "Testing" status, ensure quality and catch regressions.

## Activation
Triggered when task status changes to "Testing".

## Testing Strategy

### 1. Test Preparation
```bash
# Navigate to worktree
cd ../worktrees/task-{id}

# Update dependencies
npm install
pip install -r requirements.txt

# Clean test cache
npm test -- --clearCache
pytest --cache-clear
```

### 2. Test Execution Order

#### Progressive Testing
1. **Unit Tests** - Fast, isolated
2. **Integration Tests** - Component interactions  
3. **E2E Tests** - Full workflows
4. **Performance Tests** - If applicable
5. **Security Tests** - If applicable

### 3. Test Commands

#### Frontend Testing
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage --watchAll=false

# Run specific test suite
npm test -- TaskCard

# Run in CI mode
CI=true npm test

# Run E2E tests
npm run test:e2e
```

#### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_tasks.py::test_create_task

# Run by marker
pytest -m "not slow"

# Parallel execution
pytest -n auto
```

### 4. Test Categories

#### Unit Tests
- Test individual functions/methods
- Mock external dependencies
- Fast execution (<100ms each)
- High coverage target (>80%)

#### Integration Tests
- Test component interactions
- Use test database
- Test API endpoints
- Verify data flow

#### E2E Tests
- Test complete user workflows
- Run in browser environment
- Test critical paths only
- Accept slower execution

### 5. Test Quality Checks

#### Coverage Requirements
```yaml
minimum_coverage:
  statements: 80%
  branches: 75%
  functions: 80%
  lines: 80%
```

#### Coverage Analysis
```bash
# Generate coverage report
npm test -- --coverage --watchAll=false

# View HTML report
open coverage/lcov-report/index.html

# Python coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### 6. Common Test Scenarios

#### Task Creation Test
```typescript
describe('Task Creation', () => {
  it('should create task with all fields', async () => {
    const task = {
      title: 'Test Task',
      description: 'Description',
      type: 'Feature',
      priority: 'High'
    };
    
    const result = await createTask(task);
    
    expect(result).toMatchObject(task);
    expect(result.id).toBeDefined();
    expect(result.status).toBe('Backlog');
  });
  
  it('should validate required fields', async () => {
    const task = { description: 'No title' };
    
    await expect(createTask(task))
      .rejects.toThrow('Title is required');
  });
});
```

#### API Endpoint Test
```python
def test_update_task_status(client, sample_task):
    """Test status update endpoint."""
    response = client.put(
        f"/api/tasks/{sample_task.id}/status",
        json={"status": "In Progress"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    
    # Verify in database
    task = Task.query.get(sample_task.id)
    assert task.status == "In Progress"
```

### 7. Test Failure Handling

#### When Tests Fail
1. Identify failing test
2. Check if it's related to current task
3. If related: Fix and re-test
4. If unrelated: Document and create bug task
5. Never ignore failing tests

#### Debugging Failed Tests
```bash
# Run single test with debugging
npm test -- --runInBand --verbose TaskCard

# Python debugging
pytest -vv --pdb tests/test_tasks.py::test_name

# Check test logs
tail -f test.log
```

### 8. Performance Testing

#### Load Testing (if applicable)
```python
import locust

class TaskUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_task(self):
        self.client.post("/api/tasks", json={
            "title": f"Task {time.time()}",
            "type": "Feature",
            "priority": "Medium"
        })
    
    @task(3)
    def view_tasks(self):
        self.client.get("/api/tasks")
```

### 9. Test Report Generation

#### Test Summary Format
```markdown
## Test Report - Task #123

### Test Execution Summary
- **Total Tests**: 245
- **Passed**: 243 ✅
- **Failed**: 2 ❌
- **Skipped**: 0
- **Duration**: 45.3s

### Coverage Report
- **Statements**: 85.2%
- **Branches**: 78.9%
- **Functions**: 87.1%
- **Lines**: 84.8%

### Failed Tests
1. `test_edge_case_null_priority` - Fixed in commit abc123
2. `test_concurrent_update` - Known flaky test, re-ran successfully

### New Tests Added
- `test_task_priority_display`
- `test_priority_filter`
- `test_priority_validation`

### Performance
- API response time: <200ms ✅
- Frontend render: <100ms ✅
- Database queries: Optimized ✅

### Recommendation
Ready for code review ✅
```

### 10. Continuous Testing

#### Watch Mode Development
```bash
# Frontend - auto-run on changes
npm test -- --watch

# Backend - auto-run on changes
pytest-watch
```

#### Pre-push Testing
```bash
#!/bin/bash
# .git/hooks/pre-push
npm test -- --watchAll=false
pytest
if [ $? -ne 0 ]; then
  echo "Tests failed. Push aborted."
  exit 1
fi
```

## Success Criteria
- All tests pass
- Coverage meets thresholds
- No performance regressions
- No security vulnerabilities
- Documentation updated

## Failure Actions
- Fix related issues
- Document unrelated failures
- Create bug tasks if needed
- Update task status accordingly
- Never proceed with failing tests