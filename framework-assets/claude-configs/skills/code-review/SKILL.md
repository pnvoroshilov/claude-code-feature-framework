---
name: code-review
description: Comprehensive code review with quality checks, best practices, and actionable feedback
version: 1.0.0
tags: [code-review, quality, best-practices, security, performance, maintainability]
---

# Code Review Skill

Expert-level comprehensive code review that evaluates code quality across multiple dimensions including correctness, security, performance, maintainability, testability, and adherence to best practices. Provides actionable feedback with specific recommendations and code examples.

## Quick Start

**Basic Review Request:**
```
Review this code:
[paste code]
```

**Focused Review:**
```
Review this authentication module focusing on security vulnerabilities:
[paste code]
```

**Pull Request Review:**
```
Review this PR for merge readiness:
- Focus on changes only (not existing code)
- Check adherence to project standards
- Verify test coverage
[provide git diff or changed files]
```

## Core Capabilities

This skill provides expert-level code review across 15+ quality dimensions:

### 1. **Code Correctness & Logic**
- Algorithm correctness verification
- Logic error detection
- Edge case identification
- Boundary condition validation
- Error-prone pattern detection
- Control flow analysis

### 2. **Security Analysis**
- Vulnerability detection (SQL injection, XSS, CSRF)
- Authentication/authorization flaws
- Input validation gaps
- Sensitive data exposure
- Cryptographic weaknesses
- Dependency vulnerabilities
- OWASP Top 10 compliance

### 3. **Performance Optimization**
- Algorithm complexity analysis (Big O)
- Database query optimization
- Memory leak detection
- Resource management issues
- Caching opportunities
- N+1 query problems
- Unnecessary computations

### 4. **Code Maintainability**
- Code complexity metrics (cyclomatic, cognitive)
- Naming convention adherence
- Code duplication detection
- Function/method length analysis
- Single Responsibility Principle
- DRY principle violations
- SOLID principles adherence

### 5. **Testing & Testability**
- Test coverage analysis
- Testability assessment
- Missing test cases identification
- Test quality evaluation
- Mock/stub usage review
- Integration test coverage

### 6. **Error Handling & Resilience**
- Exception handling completeness
- Error propagation patterns
- Logging adequacy
- Recovery mechanisms
- Circuit breaker patterns
- Retry logic evaluation

### 7. **Documentation Quality**
- Code comment adequacy
- API documentation completeness
- Function/method documentation
- Complex logic explanation
- README and setup guides
- Architecture documentation

### 8. **Design Patterns & Architecture**
- Design pattern usage appropriateness
- Architectural pattern adherence
- Separation of concerns
- Dependency management
- Interface design quality
- Abstraction levels

### 9. **Code Style & Consistency**
- Language idiom usage
- Style guide compliance
- Formatting consistency
- Import organization
- File structure adherence
- Naming patterns

### 10. **Database & Data Management**
- Schema design quality
- Query efficiency
- Index usage
- Transaction management
- Data validation
- Migration patterns

### 11. **API Design Quality**
- RESTful principles adherence
- Endpoint naming conventions
- HTTP method usage
- Status code appropriateness
- Request/response validation
- API versioning strategy

### 12. **Concurrency & Threading**
- Race condition detection
- Deadlock potential
- Thread safety analysis
- Synchronization patterns
- Async/await usage
- Parallel processing efficiency

### 13. **Frontend Specific**
- Component design quality
- State management patterns
- Rendering performance
- Accessibility compliance (WCAG)
- Browser compatibility
- Bundle size optimization
- User experience patterns

### 14. **DevOps & Deployment**
- Configuration management
- Environment handling
- Secret management
- Logging and monitoring
- Deployment safety
- Health check implementation

### 15. **Dependency Management**
- Dependency version pinning
- Security vulnerability scanning
- License compliance
- Package size optimization
- Update strategy
- Deprecation handling

## How to Use This Skill

### Basic Usage Pattern

**Step 1: Provide Context**
```
I need a code review for a user authentication module.
Language: Python/FastAPI
Focus areas: Security and error handling
```

**Step 2: Share Code**
- Paste code directly
- Provide file paths
- Share git diff for PR reviews
- Include related files for context

**Step 3: Specify Review Type**
- Quick review (high-level issues)
- Comprehensive review (all dimensions)
- Focused review (specific concerns)
- PR review (changes only)

### Review Output Format

Each review provides:

**1. Executive Summary**
- Overall quality assessment (1-10 scale)
- Critical issues count
- Blockers for deployment
- Approval recommendation

**2. Critical Issues (Must Fix)**
- Security vulnerabilities
- Correctness bugs
- Performance bottlenecks
- Breaking changes

**3. Important Issues (Should Fix)**
- Code quality problems
- Maintainability concerns
- Testing gaps
- Documentation needs

**4. Suggestions (Nice to Have)**
- Optimization opportunities
- Style improvements
- Refactoring recommendations
- Best practice adoption

**5. Positive Highlights**
- Well-implemented patterns
- Good practices observed
- Excellent code sections

**6. Code Examples**
- Before/after comparisons
- Corrected implementations
- Alternative approaches

## Documentation

### Core Concepts
See [docs/core-concepts.md](docs/core-concepts.md)
- Code quality dimensions
- Review methodologies
- Quality metrics and standards
- Mental models for reviewers
- Technical debt assessment
- Risk evaluation frameworks

### Best Practices
See [docs/best-practices.md](docs/best-practices.md)
- Industry-standard review practices
- Language-specific best practices
- Security review guidelines
- Performance review techniques
- Maintainability principles
- Testing best practices
- Documentation standards

### Patterns & Anti-Patterns
See [docs/patterns.md](docs/patterns.md)
- Common code patterns (when to use)
- Anti-patterns to avoid
- Design pattern review
- Architectural patterns
- Testing patterns
- Error handling patterns
- Security patterns

### Advanced Topics
See [docs/advanced-topics.md](docs/advanced-topics.md)
- Automated code review tools
- Static analysis integration
- Linter configuration
- CI/CD quality gates
- Code metrics tracking
- Review automation strategies
- Pair programming techniques

### Troubleshooting
See [docs/troubleshooting.md](docs/troubleshooting.md)
- Handling disagreements on reviews
- False positive identification
- Context-dependent decisions
- Legacy code review strategies
- Large codebase review approaches
- Time-constrained reviews

### API Reference
See [docs/api-reference.md](docs/api-reference.md)
- Review command syntax
- Quality metrics definitions
- Severity level guidelines
- Review checklist templates
- Rating scale explanations
- Tool integration guides

## Examples

### Basic Examples

**1. Simple Function Review**
[Example 1: Function Code Review](examples/basic/example-1-function-review.md)
- Review single function for correctness
- Identify edge cases
- Suggest improvements
- Basic security checks

**2. Class Implementation Review**
[Example 2: Class Review](examples/basic/example-2-class-review.md)
- Object-oriented design review
- SOLID principles check
- Method organization
- Encapsulation validation

**3. Configuration File Review**
[Example 3: Configuration Review](examples/basic/example-3-config-review.md)
- Security configuration check
- Environment management
- Secret handling
- Best practices validation

### Intermediate Examples

**1. API Endpoint Review**
[Example 1: REST API Review](examples/intermediate/pattern-1-api-review.md)
- Complete endpoint analysis
- Security vulnerability scan
- Performance optimization
- Error handling validation
- Documentation check

**2. Database Query Optimization**
[Example 2: Database Review](examples/intermediate/pattern-2-database-review.md)
- Query performance analysis
- Index usage optimization
- N+1 problem detection
- Transaction management
- Data validation

**3. React Component Review**
[Example 3: Frontend Component Review](examples/intermediate/pattern-3-component-review.md)
- Component design evaluation
- State management review
- Performance optimization
- Accessibility compliance
- Testing coverage

### Advanced Examples

**1. Complete Pull Request Review**
[Example 1: PR Review Workflow](examples/advanced/advanced-pattern-1-pr-review.md)
- Comprehensive PR analysis
- Change impact assessment
- Test coverage validation
- Documentation updates
- Breaking change detection
- Deployment risk assessment

**2. Security Audit Review**
[Example 2: Security-Focused Review](examples/advanced/advanced-pattern-2-security-audit.md)
- OWASP Top 10 compliance
- Authentication/authorization audit
- Input validation review
- Cryptographic implementation
- Dependency vulnerability scan
- Security header validation

**3. Performance Critical Code Review**
[Example 3: Performance Optimization Review](examples/advanced/advanced-pattern-3-performance-review.md)
- Algorithm complexity analysis
- Memory usage optimization
- Database query performance
- Caching strategy review
- Profiling recommendations
- Load testing suggestions

## Templates

### Template 1: Standard Code Review
[Template: Standard Review Checklist](templates/template-1-standard-review.md)
- Complete review checklist
- Quality dimension scoring
- Issue categorization
- Actionable feedback format
- Approval criteria

### Template 2: Security-Focused Review
[Template: Security Review](templates/template-2-security-review.md)
- Security-specific checklist
- OWASP Top 10 validation
- Threat modeling
- Vulnerability assessment
- Security recommendations

### Template 3: Pull Request Review
[Template: PR Review](templates/template-3-pr-review.md)
- PR-specific checklist
- Change impact analysis
- Test coverage validation
- Documentation verification
- Merge readiness assessment

## Resources

### Quality Checklists
[Complete Review Checklists](resources/checklists.md)
- Pre-commit checklist
- Pre-PR checklist
- Merge readiness checklist
- Security audit checklist
- Performance review checklist
- Accessibility checklist

### Glossary
[Code Review Terminology](resources/glossary.md)
- Quality metrics definitions
- Technical terms
- Severity levels
- Review methodologies
- Industry terminology

### External References
[Recommended Resources](resources/references.md)
- Official documentation
- Industry standards
- Security resources (OWASP)
- Performance guidelines
- Testing resources
- Style guides by language

### Workflows
[Step-by-Step Review Workflows](resources/workflows.md)
- Standard review workflow
- Security review workflow
- Performance review workflow
- PR review workflow
- Legacy code review workflow

## Review Process Recommendations

### For Individual Developers

**Before Requesting Review:**
1. Self-review your code first
2. Run automated checks (linters, tests)
3. Ensure code compiles/runs
4. Update documentation
5. Add/update tests
6. Check for sensitive data

**Responding to Reviews:**
1. Read feedback thoroughly
2. Ask clarifying questions
3. Fix critical issues immediately
4. Discuss disagreements respectfully
5. Thank reviewers for their time

### For Code Reviewers

**Review Best Practices:**
1. Review within 24 hours
2. Start with positive feedback
3. Be specific and actionable
4. Provide code examples
5. Explain the "why" behind suggestions
6. Use constructive tone
7. Distinguish between must-fix and suggestions

**Time Management:**
1. Limit review sessions to 60 minutes
2. Review 200-400 lines at a time
3. Take breaks between reviews
4. Don't rush critical sections
5. Request help for unfamiliar areas

### For Teams

**Establish Review Standards:**
1. Define approval criteria
2. Set response time expectations
3. Assign review responsibilities
4. Track review metrics
5. Share review learnings
6. Conduct review calibration sessions

## Integration with Development Workflow

### Git Workflow Integration

**Pre-Commit:**
```bash
# Run automated checks
npm run lint
npm run test
npm run type-check

# Self-review with this skill
# Request review of critical sections
```

**Pre-PR:**
```bash
# Ensure branch is up to date
git pull origin main

# Review your own diff
git diff main...feature-branch

# Use this skill for self-review
# Address obvious issues before PR
```

**PR Review:**
```
1. Use PR template
2. Request skill-based review
3. Address feedback iteratively
4. Get approval from reviewers
5. Merge when all checks pass
```

### CI/CD Integration

**Automated Quality Gates:**
- Linter checks (ESLint, Pylint, etc.)
- Test coverage thresholds
- Security scanning (Snyk, Dependabot)
- Performance benchmarks
- Code complexity metrics
- Documentation coverage

**Manual Review Triggers:**
- High-risk areas (auth, payment)
- Public API changes
- Database migrations
- Security-sensitive code
- Performance-critical paths

## Language-Specific Guidance

### Python
- PEP 8 compliance
- Type hints usage
- Virtual environment setup
- Dependency management (requirements.txt)
- Testing with pytest
- Documentation with docstrings

### JavaScript/TypeScript
- ESLint configuration
- TypeScript strict mode
- Modern ES6+ syntax
- Async/await patterns
- Testing with Jest
- Bundle size optimization

### React
- Component composition
- Hook usage patterns
- State management (Context/Redux)
- Performance optimization (memo, useMemo)
- Accessibility (ARIA, semantic HTML)
- Testing (React Testing Library)

### FastAPI/Python
- Pydantic validation
- Dependency injection
- Async route handlers
- Error handling middleware
- OpenAPI documentation
- Testing with TestClient

### SQL/Databases
- Index optimization
- Query performance
- Transaction management
- Migration safety
- Connection pooling
- Data validation

## Limitations & Scope

### What This Skill Does
✅ Comprehensive code quality analysis
✅ Security vulnerability detection
✅ Performance optimization suggestions
✅ Best practice recommendations
✅ Actionable feedback with examples
✅ Multi-dimensional quality assessment

### What This Skill Does NOT Do
❌ Execute or run code
❌ Access live systems or databases
❌ Perform penetration testing
❌ Make final merge decisions
❌ Replace human judgment
❌ Guarantee bug-free code

### Best Used For
- Code review before commits
- Pull request reviews
- Security audits
- Performance optimization
- Refactoring guidance
- Onboarding new developers
- Establishing code standards

### Not Suitable For
- Real-time debugging
- Production incident response
- Business logic validation
- Requirements gathering
- UI/UX design review
- Infrastructure configuration (DevOps focused)

## Success Metrics

Track review effectiveness:

**Quality Metrics:**
- Bugs caught in review vs production
- Security vulnerabilities prevented
- Performance issues identified
- Code maintainability trends

**Process Metrics:**
- Review turnaround time
- Feedback implementation rate
- Review cycle iterations
- Developer satisfaction scores

**Team Metrics:**
- Knowledge sharing effectiveness
- Code standard adherence
- Technical debt reduction
- Team skill development

## Version History

- **1.0.0** (2025-01-31): Initial comprehensive release
  - Multi-dimensional quality analysis
  - Security vulnerability detection
  - Performance optimization guidance
  - 15+ review capability areas
  - Language-specific guidelines
  - Complete documentation and examples
  - Templates and checklists
  - Workflow integration guides
