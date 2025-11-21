---
name: requirements-analysis
description: Document formats and templates for User Stories, Use Cases, and Definition of Done
tags: [requirements, analysis, user-stories, use-cases, dod]
version: 1.0.0
---

# Requirements Analysis Skill

This skill provides document formats, templates, and examples for creating business requirements documentation following industry best practices.

## Document Formats

### 1. User Stories

Format each user story as:

```markdown
## User Story: [Story Name]

**As a** [type of user]
**I want** [goal/desire]
**So that** [benefit/value]

### Acceptance Criteria
- [ ] [Specific, measurable, testable criterion]
- [ ] [Another criterion]
- [ ] [Another criterion]

### Priority
[High/Medium/Low]

### Effort Estimate
[Story points or time estimate]
```

### 2. Use Cases

Format each use case as:

```markdown
## Use Case: [UC Name]

### Actors
- [Primary actor]
- [Secondary actors]

### Preconditions
- [Condition 1]
- [Condition 2]

### Main Flow
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Alternative Flows
**Alternative 1: [Name]**
1. [Step 1]
2. [Step 2]

### Exception Flows
**Exception 1: [Name]**
1. [What went wrong]
2. [How to handle]

### Postconditions
- [Result 1]
- [Result 2]
```

### 3. Definition of Done (DoD)

```markdown
## Definition of Done

### Functional Completeness
- [ ] All user stories implemented
- [ ] All acceptance criteria met
- [ ] All use cases covered

### Code Quality
- [ ] Code reviewed
- [ ] No critical bugs
- [ ] Follows coding standards
- [ ] No code smells

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] E2E tests for critical paths
- [ ] Test coverage > [X%]

### Documentation
- [ ] Code documented
- [ ] API documentation updated
- [ ] User documentation updated

### Performance
- [ ] Meets performance requirements
- [ ] No performance regressions

### Security
- [ ] Security review completed
- [ ] No security vulnerabilities
- [ ] Authentication/authorization implemented

### Deployment
- [ ] Can be deployed to staging
- [ ] Can be deployed to production
- [ ] Rollback plan exists
```

## Best Practices for Document Quality

### User Stories Best Practices
- ✅ Focus on user value (not technical implementation)
- ✅ Keep stories independent and atomic
- ✅ Make acceptance criteria specific and testable
- ✅ Use "As a... I want... So that..." format consistently
- ✅ Avoid technical jargon in user-facing stories

### Use Cases Best Practices
- ✅ Cover all flows: main, alternative, and exception
- ✅ Be specific and detailed in steps
- ✅ Include all actors (primary and secondary)
- ✅ Define clear preconditions and postconditions
- ✅ Number steps for clarity

### Definition of Done Best Practices
- ✅ Make criteria measurable and verifiable
- ✅ Include all quality gates (code, tests, docs, security)
- ✅ Align with project/team standards
- ✅ Ensure criteria are realistic and achievable
