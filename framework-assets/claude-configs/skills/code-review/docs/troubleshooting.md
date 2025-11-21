# Code Review Troubleshooting

## Table of Contents

- [Common Review Challenges](#common-review-challenges)
- [Handling Disagreements](#handling-disagreements)
- [False Positives](#false-positives)
- [Context-Dependent Decisions](#context-dependent-decisions)
- [Legacy Code Reviews](#legacy-code-reviews)
- [Large Codebase Reviews](#large-codebase-reviews)
- [Time-Constrained Reviews](#time-constrained-reviews)
- [Review Bottlenecks](#review-bottlenecks)
- [Cultural Challenges](#cultural-challenges)
- [Tool Issues](#tool-issues)

## Common Review Challenges

### Challenge: Reviewer Doesn't Understand the Code

**Symptoms**:
- Unable to provide meaningful feedback
- Superficial comments only
- Approving without understanding

**Solutions**:

1. **Ask Questions**:
```markdown
QUESTION: Can you explain the rationale behind using a queue here instead of direct processing?

QUESTION: What's the expected behavior when the API returns a 429 status?
```

2. **Request Documentation**:
```markdown
SUGGESTION: This algorithm is complex. Could you add a docstring explaining:
- What problem it solves
- Input/output expectations
- Time complexity

This will help reviewers and future maintainers.
```

3. **Pair Review Session**:
- Schedule 30-minute walkthrough
- Developer explains changes live
- Ask clarifying questions
- Document insights in PR comments

### Challenge: Code Works But Violates Standards

**Symptoms**:
- Code functions correctly
- Tests pass
- But doesn't follow team conventions

**Solutions**:

1. **Link to Standards**:
```markdown
NOTE: This works, but deviates from our error handling standard.

See: docs/standards/error-handling.md

Please update to use our ErrorResponse class:
- Consistent error format
- Proper HTTP status codes
- Structured error details
```

2. **Explain Why Standards Exist**:
```markdown
SUGGESTION: Consider using async/await instead of promise chains.

Why: Our team standard for readability and debugging:
- Easier to follow control flow
- Simpler error handling
- Better stack traces
- Consistent with rest of codebase (95% uses async/await)
```

3. **Offer to Help**:
```markdown
SUGGESTION: This could be refactored to match our repository pattern.

I'm happy to pair on this if you're unfamiliar with the pattern.
Or see examples in: src/repositories/user_repository.py
```

## Handling Disagreements

### Disagreement: Style Preferences

**Scenario**: Reviewer and author disagree on code style

**Resolution**:

1. **Check Automated Tools First**:
```bash
# If linter passes, accept it
black . && flake8 . && mypy .

# Don't argue about what tools already enforce
```

2. **Defer to Team Standards**:
```markdown
Per our team style guide (docs/style-guide.md), we use:
- Single quotes for strings
- 4 spaces for indentation
- Max line length: 88 characters

Let's follow the documented standard.
```

3. **If No Standard Exists**:
```markdown
This is a reasonable approach. I prefer [alternative], but either works.

Let's discuss in our next team meeting whether we want to standardize this.
For now, let's merge as-is since it's consistent internally.
```

### Disagreement: Technical Approach

**Scenario**: Two valid approaches, different opinions

**Resolution Framework**:

1. **Identify Trade-offs**:
```markdown
Your approach (REST API):
✅ Simpler implementation
✅ Widely understood
❌ More network calls

Alternative (GraphQL):
✅ Single endpoint
✅ Flexible queries
❌ Steeper learning curve
❌ More complex backend

Given our team's experience and project timeline, REST seems more appropriate here.
```

2. **Use Data**:
```markdown
I suggested using a hash map (O(1) lookup) instead of linear search (O(n)).

For our expected data size (10-100 items), the performance difference is negligible.
Your implementation is simpler and more readable.

Let's keep it unless we expect data growth. We can optimize later if needed.
```

3. **Escalate If Needed**:
```markdown
We have different views on the caching strategy. Both have merit.

@tech-lead Could you weigh in on:
1. Cache-aside pattern (author's proposal)
2. Write-through cache (my suggestion)

Considering our consistency requirements and traffic patterns?
```

## False Positives

### Linter False Positives

**Problem**: Automated tools report issues that are intentional

**Solution**: Disable with comments
```python
# Intentional dynamic attribute access
result = getattr(obj, dynamic_attribute)  # noqa: B009

# Type is actually correct, mypy confused
user: User = get_current_user()  # type: ignore[assignment]

# Complexity is acceptable for this specific case
def complex_business_rule():  # noqa: C901
    # Complex but correct business logic
    pass
```

**Best Practice**:
- Always add explanation when disabling
- Keep disabled scope minimal
- Document why it's a false positive

### Security Scanner False Positives

**Problem**: Security tools flag safe code

**Solution**: Document and whitelist
```python
# Safe usage - input is validated and sanitized before this point
# nosec B608 (SQL injection)
query = f"SELECT * FROM {validated_table_name} WHERE id = %s"
cursor.execute(query, (user_id,))
```

**Documentation**:
```markdown
## Security Scanner Exceptions

### B608: SQL injection in reports.py line 45

**Why Safe**: 
- Table name validated against whitelist
- Only admin users can call this function
- User input doesn't reach SQL
- Query parameters still use placeholders

**Verified**: 2025-01-31 by @security-team
**Re-review**: 2025-07-31
```

## Context-Dependent Decisions

### Performance vs Readability

**Context Matters**:

**Case 1: Startup MVP**
```python
# Readable but not optimized
users = User.query.all()
active_users = [u for u in users if u.is_active]

# Verdict: ACCEPT
# Rationale: Readability more important now. Optimize if it becomes a bottleneck.
```

**Case 2: High-Traffic Production System**
```python
# Same code in different context
users = User.query.all()
active_users = [u for u in users if u.is_active]

# Verdict: REQUIRES CHANGE
# Rationale: This runs on every page load (1000 req/sec). Filter in database:
# active_users = User.query.filter_by(is_active=True).all()
```

### Quick Fix vs Proper Solution

**Hotfix Context**:
```python
# Quick fix for production issue
if user_id == "broken-user-123":
    return default_value

# Verdict: ACCEPT for hotfix branch
# Action: Create ticket TECH-456 for proper fix
# Timeline: Address in next sprint
```

**Regular Feature**:
```python
# Same code in feature branch
if user_id == "broken-user-123":
    return default_value

# Verdict: REQUIRES CHANGE
# Rationale: Not a hotfix - take time to fix root cause
# Why is this user ID broken? Fix the underlying issue.
```

## Legacy Code Reviews

### Challenge: Reviewing Changes in Poor Quality Legacy Code

**Problem**: New code touches legacy code that doesn't meet standards

**Approaches**:

**1. Boy Scout Rule** (Leave it better):
```markdown
SUGGESTION: While you're here, could you also:
- Add type hints to this function
- Extract the complex conditional to a named function
- Add a docstring

This makes the legacy code slightly better with minimal effort.
```

**2. Focused Review** (Don't let legacy block progress):
```markdown
NOTE: This function you're modifying has several issues (complexity, lack of tests, unclear naming).

For THIS PR, let's focus on:
✅ Your changes are correct
✅ Your changes have tests
✅ You didn't make existing issues worse

We should refactor this whole module, but that's out of scope for this PR.
Created ticket TECH-789 to track refactoring.
```

**3. Gradual Improvement**:
```markdown
SUGGESTION: Let's improve this incrementally:

Phase 1 (this PR): Add tests for your new functionality
Phase 2 (next PR): Add tests for existing functionality
Phase 3 (future PR): Refactor with test coverage safety net

This is safer than big-bang refactoring and shows immediate value.
```

## Large Codebase Reviews

### Challenge: PR Has 2000+ Line Changes

**Problem**: Too large to review effectively

**Solutions**:

**1. Request Split**:
```markdown
REQUEST: This PR is too large for effective review (2,347 lines).

Could you split into smaller PRs:
1. Database schema changes
2. API layer changes
3. Frontend changes
4. Test updates

This makes review more thorough and reduces risk.
```

**2. Staged Review** (if can't split):
```markdown
APPROACH: I'll review this in stages:

✅ Day 1: Database and model changes (300 lines) - COMPLETE
🔄 Day 2: Business logic (800 lines) - IN PROGRESS
📅 Day 3: API endpoints (600 lines)
📅 Day 4: Frontend and tests (647 lines)

Will provide feedback incrementally rather than one massive review.
```

**3. Focus on High-Risk Areas**:
```markdown
PRIORITIZED REVIEW:

🔴 HIGH PRIORITY (reviewed thoroughly):
- Authentication changes (security critical)
- Payment processing (correctness critical)
- Database migrations (irreversible)

🟡 MEDIUM PRIORITY (standard review):
- API endpoints
- Business logic

🟢 LOW PRIORITY (quick scan):
- Test data fixtures
- Generated code
- Documentation updates
```

## Time-Constrained Reviews

### Challenge: Need Quick Review for Deployment

**Problem**: Production issue needs immediate fix

**Approach**:

**Hotfix Review Checklist** (5-10 minutes):
```markdown
QUICK REVIEW CHECKLIST:

✅ Does it fix the reported issue?
✅ Are there obvious security issues?
✅ Could this break something else?
✅ Is there a rollback plan?
✅ Are monitoring/alerts in place?

SKIPPING (follow-up required):
- Comprehensive test coverage (add later)
- Code style perfection (fix later)
- Optimal performance (good enough for now)

VERDICT: APPROVED for hotfix
FOLLOW-UP: Created TECH-890 for proper solution
```

**Risk Mitigation**:
```markdown
DEPLOYMENT PLAN:

1. Deploy to staging first
2. Run smoke tests
3. Deploy to 10% of production (canary)
4. Monitor for 30 minutes
5. Full rollout if no issues
6. Have rollback ready (previous deployment artifact)

MONITORING:
- Error rate dashboard
- Response time metrics
- Alert if errors spike >1%
```

## Review Bottlenecks

### Challenge: Reviews Taking Too Long

**Symptoms**:
- PRs sit for days without review
- Developers blocked waiting
- Frustration and deadline pressure

**Solutions**:

**1. Review Rotation**:
```markdown
TEAM PRACTICE: Review rotation

Week 1: Alice (primary), Bob (secondary)
Week 2: Bob (primary), Charlie (secondary)
Week 3: Charlie (primary), Alice (secondary)

- Primary reviewer: Within 4 hours
- Secondary reviewer: Within 24 hours
- Blocks removed by end of business day
```

**2. Review Size Limits**:
```markdown
TEAM STANDARD: PR size limits

- Small (<200 lines): Review within 2 hours
- Medium (200-400 lines): Review within 4 hours
- Large (>400 lines): Must split or schedule dedicated review time

Large PRs require prior discussion with reviewer to schedule time.
```

**3. Async + Sync Hybrid**:
```markdown
REVIEW PROCESS:

1. Async review: Reviewer leaves comments (within 4 hours)
2. If >5 significant issues: Schedule 30-min sync discussion
3. Developer addresses feedback
4. Quick re-review (within 1 hour)
5. Merge if approved

Sync discussion resolves ambiguity faster than comment ping-pong.
```

## Cultural Challenges

### Challenge: Defensive Developers

**Problem**: Developer takes feedback personally

**Solutions**:

**1. Frame as Learning**:
```markdown
LEARNING OPPORTUNITY: Did you know about Python's `pathlib`?

Instead of:
path = os.path.join(dir, "file.txt")

You can use:
path = Path(dir) / "file.txt"

Benefits: Cross-platform, more readable, better errors

Not a problem with your code - just sharing a useful pattern!
```

**2. Acknowledge Good Work First**:
```markdown
EXCELLENT:
- ✅ Comprehensive test coverage
- ✅ Clear variable names
- ✅ Good error handling
- ✅ Helpful comments

SUGGESTIONS:
- Consider extracting validation logic to separate function
- Could simplify the nested conditionals

Great work overall! Minor suggestions to make good code even better.
```

**3. Be Specific and Kind**:
```markdown
❌ BAD: "This code is messy and hard to read"

✅ GOOD: "This function has 3 responsibilities. Could we split it into:
- validate_input()
- process_data()
- format_output()

This would make each piece easier to understand and test independently."
```

## Tool Issues

### Challenge: Automated Tools Disagreeing

**Problem**: Different tools give conflicting advice

**Solution: Establish Tool Hierarchy**:
```yaml
# .editorconfig - Universal
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true

# Black (formatter) - Highest priority
# Line length: 88

# Flake8 (linter) - Must match Black
[flake8]
max-line-length = 88
extend-ignore = E203  # Black handles this

# MyPy (type checker) - Compatible config
[mypy]
python_version = 3.9

# Pylint - Disabled if conflicts with Black
# We prefer Black's formatting decisions
```

**Resolution Process**:
1. Formatter (Black, Prettier) - Automates style
2. Linter (Flake8, ESLint) - Configured to match formatter
3. Type Checker (MyPy, TypeScript) - Independent analysis
4. Security Scanner (Bandit, Snyk) - Manual review of findings

---

When facing review challenges, prioritize communication, context-awareness, and pragmatic decision-making over rigid rule enforcement.
