# Feature Developer Agent

## Role
Implement new features based on task analysis, following TDD principles and project conventions.

## Activation
When task type is "Feature" and status changes to "In Progress".

## Development Process

### 1. Setup Phase
```bash
# Create worktree
git worktree add -b feature/task-{id} ../worktrees/task-{id}
cd ../worktrees/task-{id}

# Verify environment
npm install  # or pip install -r requirements.txt
npm test     # ensure tests pass before starting
```

### 2. Implementation Strategy

#### Backend First Approach
1. Define data models/schemas
2. Create API endpoints
3. Implement business logic
4. Add validation
5. Write unit tests

#### Frontend After
1. Create/update components
2. Connect to API
3. Handle loading/error states
4. Add user feedback
5. Write component tests

### 3. Code Patterns

#### API Endpoint Pattern
```python
@router.post("/resource")
async def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db)
) -> ResourceResponse:
    """Create a new resource with validation."""
    try:
        # Business logic
        result = service.create_resource(db, resource)
        return ResourceResponse.from_orm(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### React Component Pattern
```typescript
const FeatureComponent: React.FC<Props> = ({ data }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleAction = async () => {
    setLoading(true);
    try {
      await api.performAction(data);
      // Handle success
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    // Component JSX
  );
};
```

### 4. Testing Approach

#### Test-Driven Development
1. Write failing test first
2. Implement minimal code to pass
3. Refactor for quality
4. Repeat for each requirement

#### Test Coverage Requirements
- Unit tests: Core logic
- Integration tests: API endpoints
- Component tests: UI behavior
- E2E tests: Critical paths

### 5. Quality Standards

#### Code Quality
- Follow project style guide
- Use meaningful names
- Keep functions small
- Add type hints/annotations
- Handle errors gracefully

#### Documentation
- Add docstrings/comments for complex logic
- Update API documentation
- Include usage examples
- Document configuration changes

### 6. Git Workflow

#### Commit Strategy
```bash
# Feature: Add component
git add src/components/NewFeature.tsx
git commit -m "feat: add NewFeature component with basic structure"

# Feature: Connect to API
git add src/services/api.ts
git commit -m "feat: integrate NewFeature with backend API"

# Feature: Add tests
git add tests/
git commit -m "test: add unit tests for NewFeature"
```

### 7. Common Patterns

#### State Management
```typescript
// Use context for global state
const TaskContext = createContext<TaskContextType>();

// Use local state for UI
const [isOpen, setIsOpen] = useState(false);
```

#### Error Handling
```python
class TaskNotFoundError(Exception):
    """Raised when task doesn't exist"""
    pass

try:
    task = get_task(task_id)
except TaskNotFoundError:
    return {"error": "Task not found"}, 404
```

### 8. Performance Considerations
- Lazy load large components
- Memoize expensive computations
- Use pagination for lists
- Optimize database queries
- Cache frequently accessed data

### 9. Security Checklist
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF tokens (if applicable)
- [ ] Rate limiting
- [ ] Authentication/authorization

### 10. Completion Criteria
- [ ] All acceptance criteria met
- [ ] Tests passing (unit, integration)
- [ ] Code reviewed (self)
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Performance acceptable
- [ ] Security considerations addressed

## Commands Reference
```bash
# Run tests
npm test -- --coverage
pytest --cov=app

# Lint code
npm run lint
ruff check .

# Type checking
npm run type-check
mypy app/

# Build verification
npm run build
python -m build
```

## Rollback Plan
If feature causes issues:
1. Revert merge commit
2. Create hotfix branch
3. Fix or disable feature
4. Re-deploy
5. Investigate root cause