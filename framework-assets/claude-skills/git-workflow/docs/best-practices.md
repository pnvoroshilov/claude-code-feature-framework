# Best Practices - Professional Git Standards

## Table of Contents

- [Commit Message Conventions](#commit-message-conventions)
- [Branch Naming Standards](#branch-naming-standards)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Code Review Principles](#code-review-principles)
- [Merge Strategy Selection](#merge-strategy-selection)
- [History Maintenance](#history-maintenance)
- [Security and Signing](#security-and-signing)
- [Team Collaboration Protocols](#team-collaboration-protocols)
- [Repository Hygiene](#repository-hygiene)
- [Commit Frequency and Size](#commit-frequency-and-size)

## Commit Message Conventions

### Principle

Commit messages should be **clear, consistent, and informative**. They serve as documentation for your project's evolution and help team members understand changes without reading code.

### Why It Matters

Good commit messages:
- Enable quick understanding of changes
- Support automated changelog generation
- Facilitate code reviews
- Aid in debugging and bisecting
- Document decision-making process

### Conventional Commits Format

Use the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, tooling, dependencies
- `ci`: CI/CD changes
- `revert`: Reverting previous commit

### Good Examples

**Simple feature:**
```
feat(auth): add JWT token validation

Implement middleware to validate JWT tokens on protected routes.
Adds token expiration checking and signature verification.
```

**Bug fix with context:**
```
fix(dashboard): resolve memory leak in chart component

The chart component was not properly cleaning up WebSocket
connections when unmounted. This caused memory to accumulate
during navigation.

- Add cleanup in useEffect return
- Close WebSocket connections on unmount
- Add tests to verify cleanup

Closes #456
```

**Breaking change:**
```
feat(api)!: change response format for user endpoints

BREAKING CHANGE: User API now returns camelCase instead of snake_case

Migration guide:
- Update API clients to use camelCase
- Run migration script: npm run migrate:users

Closes #789
Reviewed-by: Jane Smith
```

### Bad Examples

**Too vague:**
```
❌ fix: bug fix
❌ update: changes
❌ wip: stuff
```

**Missing context:**
```
❌ fix login
// What was wrong? How did you fix it?

✅ fix(auth): prevent session timeout during active use

Reset session timer on user activity to prevent unexpected
logouts during form completion.
```

**Too much in one commit:**
```
❌ feat: add user dashboard, refactor API, update docs, fix bugs

// Should be 4+ separate commits
```

### Subject Line Best Practices

**DO:**
- ✅ Use imperative mood ("add" not "added" or "adds")
- ✅ Capitalize first letter
- ✅ Limit to 50-72 characters
- ✅ Be specific about what changed
- ✅ Omit trailing period

**DON'T:**
- ❌ Use past tense ("added feature")
- ❌ Be vague ("fix stuff")
- ❌ Write novels (use body for details)
- ❌ Include issue numbers in subject (use footer)

### Body Best Practices

**Include:**
- Why the change was made
- What problem it solves
- Alternative approaches considered
- Side effects or implications
- Testing approach

**Format:**
- Wrap at 72 characters
- Leave blank line after subject
- Use bullet points for multiple items
- Reference related issues/PRs

### Footer Best Practices

**Include:**
- Issue references: `Closes #123`, `Fixes #456`
- Breaking changes: `BREAKING CHANGE: description`
- Co-authors: `Co-authored-by: Name <email>`
- Reviewers: `Reviewed-by: Name <email>`

### Examples by Scenario

**Feature with tests:**
```
feat(payment): add Stripe payment integration

Integrate Stripe payment processing for checkout flow.

- Add Stripe SDK initialization
- Implement payment intent creation
- Add webhook handler for payment events
- Include error handling for failed payments
- Add comprehensive test suite

Technical decisions:
- Use payment intents instead of charges (Stripe recommendation)
- Store payment IDs in database for reconciliation
- Implement idempotency for webhook handling

Closes #234
Tested-by: QA Team
```

**Refactoring:**
```
refactor(auth): extract authentication logic to separate service

Move authentication logic from controllers to dedicated service.
This improves testability and allows reuse across API versions.

Changes:
- Create AuthService class
- Move JWT generation to service
- Move password hashing to service
- Update controllers to use service
- Add service unit tests

No functional changes - all tests pass.
```

**Documentation:**
```
docs(api): add examples for user authentication endpoints

Add code examples for:
- Login with email/password
- OAuth authentication flow
- Token refresh process
- Logout and session termination

Examples include curl commands and JavaScript fetch examples.
```

### Commit Message Template

Create a template file and configure Git to use it:

```bash
# Create template
cat > ~/.gitmessage << EOF
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
#
# Types: feat, fix, docs, style, refactor, perf, test, chore, ci, revert
# Scope: Component or module affected
# Subject: Imperative mood, lowercase, no period, <50 chars
# Body: Wrap at 72 chars, explain what and why vs how
# Footer: Issue references, breaking changes, co-authors
EOF

# Configure Git to use template
git config --global commit.template ~/.gitmessage
```

### Automated Validation

Use commit hooks to enforce standards:

```bash
# .husky/commit-msg
#!/bin/sh
npx --no-install commitlint --edit "$1"
```

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'chore', 'ci', 'revert'
    ]],
    'subject-case': [2, 'always', 'sentence-case'],
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100]
  }
};
```

---

## Branch Naming Standards

### Principle

Branch names should be **descriptive, consistent, and organized** using a clear naming convention that indicates purpose and ownership.

### Standard Format

```
<type>/<issue-number>-<description>

Examples:
feature/123-user-authentication
bugfix/456-memory-leak
hotfix/789-security-patch
release/v1.2.0
```

### Branch Type Prefixes

**feature/** - New features
```
feature/user-dashboard
feature/123-payment-integration
feature/oauth-login
```

**bugfix/** or **fix/** - Bug fixes
```
bugfix/login-error
fix/456-memory-leak
bugfix/chart-rendering
```

**hotfix/** - Emergency production fixes
```
hotfix/security-vulnerability
hotfix/789-payment-processing
hotfix/critical-api-error
```

**release/** - Release preparation
```
release/v1.2.0
release/2024-Q1
release/sprint-23
```

**experiment/** or **spike/** - Experimental work
```
experiment/new-architecture
spike/performance-testing
experiment/ml-integration
```

**docs/** - Documentation updates
```
docs/api-reference
docs/user-guide
docs/architecture-diagram
```

**refactor/** - Code refactoring
```
refactor/auth-service
refactor/database-layer
refactor/legacy-code
```

### Naming Best Practices

**DO:**
- ✅ Use lowercase
- ✅ Use hyphens for spaces
- ✅ Include issue number when applicable
- ✅ Be descriptive but concise
- ✅ Use consistent prefixes

**DON'T:**
- ❌ Use spaces (use hyphens)
- ❌ Use special characters
- ❌ Make names too long (>50 chars)
- ❌ Use ambiguous names
- ❌ Include personal names

### Examples by Scenario

**With issue tracking:**
```
feature/PROJ-123-user-authentication
bugfix/JIRA-456-fix-memory-leak
hotfix/ISSUE-789-security-patch
```

**Without issue tracking:**
```
feature/user-authentication
bugfix/memory-leak-in-charts
hotfix/production-api-error
```

**Personal/team branches:**
```
username/feature/experimental-ui
team-alpha/feature/new-dashboard
poc/blockchain-integration
```

### Branch Organization

**Short-lived branches:**
- Feature branches: 1-2 weeks maximum
- Bugfix branches: 1-3 days
- Hotfix branches: Hours to 1 day

**Long-lived branches:**
- `main` (or `master`): Production-ready code
- `develop`: Integration branch (GitFlow)
- `staging`: Pre-production testing
- `release/*`: Active release preparation

### Branch Lifecycle

```bash
# 1. Create branch from main
git checkout main
git pull origin main
git checkout -b feature/123-user-auth

# 2. Work on feature
git commit -m "feat(auth): implement login"
git commit -m "test(auth): add login tests"

# 3. Keep updated with main
git fetch origin
git rebase origin/main

# 4. Push for review
git push -u origin feature/123-user-auth

# 5. Create PR and merge
gh pr create
# ... review and approval ...
git checkout main
git pull origin main

# 6. Delete branch after merge
git branch -d feature/123-user-auth
git push origin --delete feature/123-user-auth
```

---

## Pull Request Guidelines

### Principle

Pull requests should be **reviewable, well-documented, and properly sized** to facilitate effective code review and maintain high quality.

### PR Size Best Practices

**Optimal PR size:**
- 200-400 lines of changes (excluding tests)
- Single logical change or feature
- Reviewable in 30-60 minutes

**When to split PRs:**
- PR exceeds 500-1000 lines
- Multiple unrelated changes
- Mix of refactoring and new features
- Different reviewers needed

### PR Title Format

Follow commit message conventions:
```
feat(auth): implement JWT authentication
fix(dashboard): resolve chart rendering bug
docs(api): update authentication endpoints
```

### PR Description Template

```markdown
## Summary
Brief description of what this PR does (2-3 sentences)

## Type of Change
- [ ] Feature (new functionality)
- [ ] Bug fix (fixes an issue)
- [ ] Refactoring (no functional changes)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test coverage improvement

## Related Issues
Closes #123
Related to #456

## Changes Made
- Implemented JWT token generation
- Added token validation middleware
- Created authentication service
- Updated API documentation

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

Test coverage: 85% → 92%

## Screenshots/Videos
(If UI changes, include before/after screenshots)

## Deployment Notes
- Requires new environment variable: `JWT_SECRET`
- Run migration: `npm run migrate`
- Update configuration in production

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console logs or debug code
- [ ] Tests added and passing
- [ ] Branch up to date with base branch
```

### Draft PRs

Use draft PRs for work in progress:
```bash
# Create draft PR
gh pr create --draft --title "WIP: User authentication"

# Mark ready for review when done
gh pr ready
```

**When to use draft PRs:**
- Want early feedback on approach
- Need help with technical decision
- Working on large feature over multiple days
- Want to show progress to team

### PR Review Request Best Practices

**DO:**
- ✅ Request review from relevant experts
- ✅ Assign specific reviewers
- ✅ Respond promptly to feedback
- ✅ Mark conversations as resolved
- ✅ Update PR when base branch changes

**DON'T:**
- ❌ Request review before PR is ready
- ❌ Request review from entire team
- ❌ Ignore reviewer feedback
- ❌ Force push without warning
- ❌ Merge without required approvals

### Self-Review Checklist

Before requesting review:
```
Code Quality:
- [ ] No debug code or console.logs
- [ ] No commented-out code
- [ ] No hardcoded values that should be config
- [ ] Error handling implemented
- [ ] Edge cases handled

Testing:
- [ ] Unit tests added for new code
- [ ] Integration tests updated
- [ ] All tests passing
- [ ] Test coverage maintained/improved

Documentation:
- [ ] Code comments where needed
- [ ] API docs updated
- [ ] README updated if needed
- [ ] CHANGELOG updated

Git Hygiene:
- [ ] Commits are atomic and well-described
- [ ] No merge commits (rebased on base branch)
- [ ] No WIP or temp commits
- [ ] Branch name follows convention
```

---

## Code Review Principles

### Principle

Code reviews should be **constructive, thorough, and respectful** - focusing on code quality while maintaining positive team relationships.

### Review Goals

**Primary objectives:**
1. **Correctness** - Code does what it's supposed to
2. **Quality** - Code is maintainable and follows standards
3. **Knowledge sharing** - Team learns from each other
4. **Bug prevention** - Catch issues before production

**Secondary objectives:**
5. **Documentation** - Changes are well-documented
6. **Testing** - Adequate test coverage
7. **Performance** - No obvious performance issues
8. **Security** - No security vulnerabilities

### Reviewer Responsibilities

**MUST review:**
- ✅ Logic correctness
- ✅ Error handling
- ✅ Security implications
- ✅ Test coverage
- ✅ Code style consistency

**SHOULD review:**
- ✅ Performance implications
- ✅ Documentation quality
- ✅ API design decisions
- ✅ Database schema changes
- ✅ Breaking changes

**AVOID nitpicking:**
- ❌ Personal style preferences
- ❌ Minor formatting (use linters)
- ❌ Variable naming (unless confusing)
- ❌ Bikeshedding

### Feedback Best Practices

**Constructive feedback structure:**
```
❌ Bad: "This is wrong."
✅ Good: "This might cause issue X. Consider approach Y instead."

❌ Bad: "Why did you do it this way?"
✅ Good: "Could we use pattern X here? It might be more maintainable because Y."

❌ Bad: "This is terrible."
✅ Good: "This could be improved by X. Here's an example: [code]"
```

**Feedback categories:**
- **MUST FIX** - Blocking issues (bugs, security)
- **SHOULD FIX** - Important improvements (performance, maintainability)
- **COULD FIX** - Nice-to-have suggestions
- **QUESTION** - Seeking understanding
- **PRAISE** - Acknowledge good work

### Review Comment Examples

**Bug/correctness:**
```
🔴 MUST FIX: Potential null pointer exception

This could crash if `user` is null. Suggest adding:

```javascript
if (!user) {
  throw new Error('User not found');
}
```
```

**Security:**
```
🔴 MUST FIX: SQL injection vulnerability

Direct string interpolation is unsafe. Use parameterized queries:

```javascript
// Instead of:
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Use:
const query = 'SELECT * FROM users WHERE id = ?';
const result = await db.query(query, [userId]);
```
```

**Performance:**
```
🟡 SHOULD FIX: Potential N+1 query

This loops through users and makes a query for each. Consider using a join or batch query.
```

**Suggestion:**
```
💡 COULD FIX: Consider extracting to helper function

This validation logic appears in multiple places. Extracting to a helper would improve maintainability.
```

**Question:**
```
❓ QUESTION: Why use approach X instead of Y?

Just trying to understand the reasoning - both seem viable.
```

**Praise:**
```
✅ PRAISE: Excellent error handling!

Great job covering edge cases and providing helpful error messages.
```

### Review Turnaround Time

**Target response times:**
- Critical hotfix: < 2 hours
- Standard PR: < 24 hours
- Large PR: < 48 hours

**If you can't review promptly:**
- Notify author of delay
- Suggest alternative reviewer
- Set expectation for when you'll review

### Author Responsibilities

**Responding to feedback:**
- Read all comments carefully
- Ask questions if unclear
- Address all feedback (fix or explain why not)
- Mark conversations as resolved
- Thank reviewers

**Handling disagreements:**
```
🤝 Professional disagreement:
"I appreciate your feedback. I chose approach X because of Y. However, I'm open to approach Z if you think it's better. What do you think?"

Instead of:
"No, my way is correct."
```

### Review Checklist

```
Functionality:
- [ ] Code does what PR description says
- [ ] No logical errors
- [ ] Edge cases handled
- [ ] Error handling appropriate

Code Quality:
- [ ] Code is readable and maintainable
- [ ] No unnecessary complexity
- [ ] Follows project conventions
- [ ] No code duplication

Testing:
- [ ] New code has tests
- [ ] Tests cover edge cases
- [ ] Tests are meaningful (not just coverage)
- [ ] All tests pass

Documentation:
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] README updated if needed
- [ ] Breaking changes noted

Security:
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS prevented

Performance:
- [ ] No obvious performance issues
- [ ] Database queries efficient
- [ ] No N+1 queries
- [ ] Appropriate caching

Git:
- [ ] Commit messages follow conventions
- [ ] No merge commits
- [ ] Branch up to date
- [ ] Clean commit history
```

---

## Merge Strategy Selection

### Principle

Choose the **appropriate merge strategy** based on your workflow, team size, and history preferences. Each strategy has trade-offs.

### Three Main Strategies

**1. Merge Commit** (default)
- Preserves complete history
- Shows branch structure
- Cluttered history graph

**2. Squash and Merge**
- Clean linear history
- One commit per PR
- Loses detailed commit history

**3. Rebase and Merge**
- Linear history
- Preserves individual commits
- Requires careful handling

### When to Use Each Strategy

**Merge Commit - Use when:**
- ✅ Want to preserve feature branch history
- ✅ Multiple developers worked on branch
- ✅ Want to see branching structure
- ✅ Need to easily revert entire feature

**Squash and Merge - Use when:**
- ✅ Want clean, linear history
- ✅ PR has many WIP commits
- ✅ Individual commits not meaningful
- ✅ Simplify changelog generation

**Rebase and Merge - Use when:**
- ✅ Want linear history with preserved commits
- ✅ Each commit is meaningful and atomic
- ✅ Commits follow conventions
- ✅ Team understands rebase workflow

### Comparison Table

| Aspect | Merge Commit | Squash Merge | Rebase Merge |
|--------|-------------|--------------|--------------|
| History | Branched | Linear | Linear |
| PR commits | All preserved | Combined | All preserved |
| Revert ease | Easy (one commit) | Easy (one commit) | Harder (multiple commits) |
| Bisect friendly | Less | More | Most |
| Graph complexity | High | Low | Low |
| Best for | Large features | Any PR | Clean PRs |

### Implementation Examples

**Merge commit:**
```bash
git checkout main
git merge --no-ff feature/user-auth
# Creates merge commit even if fast-forward possible
```

**Squash and merge:**
```bash
git checkout main
git merge --squash feature/user-auth
git commit -m "feat(auth): implement user authentication

Summary of all changes from feature branch:
- Add login endpoint
- Implement JWT tokens
- Add password hashing
- Create user tests"
```

**Rebase and merge:**
```bash
git checkout feature/user-auth
git rebase main  # Rebase feature on main first
git checkout main
git merge --ff-only feature/user-auth
# Fast-forward merge (linear history)
```

### GitHub/GitLab Configuration

**GitHub repository settings:**
```
Settings → Branches → Branch protection rules

Configure allowed merge types:
☑ Allow merge commits
☑ Allow squash merging
☑ Allow rebase merging

Choose default:
● Squash (recommended for most teams)
```

### Handling Merge Conflicts

**During merge commit:**
```bash
git merge feature
# CONFLICT!
# Fix conflicts in files
git add resolved-files
git commit  # Complete merge
```

**During rebase:**
```bash
git rebase main
# CONFLICT!
# Fix conflicts in files
git add resolved-files
git rebase --continue
# Repeat for each commit with conflicts
```

**Best practices:**
- Communicate before complex merges
- Keep branches short-lived to minimize conflicts
- Rebase frequently on base branch
- Use visual merge tools (VS Code, GitKraken, etc.)

---

## History Maintenance

### Principle

Maintain a **clean, readable Git history** that tells the story of your project's evolution. History is documentation.

### Why Clean History Matters

- **Easier debugging** - Bisect works better with clean commits
- **Better understanding** - Future developers understand evolution
- **Simpler reverts** - Atomic commits are easy to revert
- **Professional appearance** - Shows care and attention

### Interactive Rebase for Cleanup

**Before pushing to shared branch:**
```bash
# Clean up last 5 commits
git rebase -i HEAD~5

# In editor, you'll see:
pick c7f8a9 feat: add user login
pick b4d6e8 wip: testing
pick a1b2c3 fix typo
pick d4e6f2 feat: add user logout
pick f8g9h1 refactor: improve code

# Change to:
pick c7f8a9 feat: add user login
fixup b4d6e8 wip: testing        # Squash into previous
fixup a1b2c3 fix typo            # Squash into previous
pick d4e6f2 feat: add user logout
fixup f8g9h1 refactor: improve code  # Squash into previous

# Result: 2 clean commits instead of 5 messy ones
```

**Interactive rebase commands:**
- `pick` - Keep commit as-is
- `reword` - Keep commit, but edit message
- `edit` - Keep commit, but stop to amend
- `squash` - Combine with previous, keep both messages
- `fixup` - Combine with previous, discard this message
- `drop` - Remove commit entirely

### Amending Commits

**Fix the last commit:**
```bash
# Forgot to add file
git add forgotten-file.js
git commit --amend --no-edit

# Fix commit message
git commit --amend -m "feat(auth): correct commit message"
```

**Autosquash workflow:**
```bash
# Make commit that fixes earlier commit
git commit --fixup=c7f8a9  # Creates "fixup! original message"

# Later, squash all fixup commits
git rebase -i --autosquash HEAD~10
# Automatically arranges fixup commits after targets
```

### History Rewriting Rules

**SAFE to rewrite:**
- ✅ Commits only on your local branch
- ✅ Commits not yet pushed
- ✅ Your personal feature branch (warn team first)

**DANGEROUS to rewrite:**
- ❌ Commits on main/master
- ❌ Commits other people are building on
- ❌ Pushed commits on shared branches
- ❌ Published release tags

**Force push safely:**
```bash
# After rewriting history, need to force push
# Use --force-with-lease to prevent overwriting others' work
git push --force-with-lease origin feature

# If rejected, someone else pushed - fetch and review first
git fetch
git log origin/feature
# Decide whether to keep their work or proceed with force
```

### Commit Splitting

**Split one commit into multiple:**
```bash
git rebase -i HEAD~3
# Mark commit with 'edit'

# Reset to before the commit
git reset HEAD^

# Stage and commit in pieces
git add src/auth.js
git commit -m "feat(auth): add authentication"

git add tests/auth.test.js
git commit -m "test(auth): add authentication tests"

# Continue rebase
git rebase --continue
```

### Commit Reordering

**Reorder commits logically:**
```bash
git rebase -i HEAD~5

# Reorder lines in editor:
pick d4e6f2 docs: update README
pick c7f8a9 feat: add feature
pick b4d6e8 test: add tests
pick a1b2c3 fix: fix bug in feature

# Changes to logical order:
pick c7f8a9 feat: add feature
pick b4d6e8 test: add tests
pick a1b2c3 fix: fix bug in feature
pick d4e6f2 docs: update README
```

### Cherry-Picking

**Apply specific commits from another branch:**
```bash
# Apply single commit
git cherry-pick c7f8a9

# Apply range of commits
git cherry-pick c7f8a9..d4e6f2

# Cherry-pick without committing (to modify)
git cherry-pick -n c7f8a9
# Make changes
git commit
```

---

## Security and Signing

### Principle

**Verify commit authenticity** and **protect sensitive data** to maintain repository security and integrity.

### GPG Commit Signing

**Why sign commits:**
- Proves commits came from you
- Prevents impersonation
- Required by some organizations
- Shows "Verified" badge on GitHub

**Setup GPG signing:**
```bash
# Generate GPG key
gpg --full-generate-key
# Choose RSA and RSA, 4096 bits

# List keys
gpg --list-secret-keys --keyid-format=long

# Configure Git
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Export public key for GitHub
gpg --armor --export <KEY_ID>
# Add to GitHub Settings → SSH and GPG keys
```

**Signing commits:**
```bash
# Sign individual commit
git commit -S -m "feat: add feature"

# With auto-sign enabled, just commit normally
git commit -m "feat: add feature"
# Automatically signed

# Sign tags
git tag -s v1.0.0 -m "Release v1.0.0"
```

**Verify signatures:**
```bash
# Verify specific commit
git verify-commit HEAD

# Show signature info
git log --show-signature

# Verify tag
git verify-tag v1.0.0
```

### Protecting Sensitive Data

**Never commit:**
- ❌ API keys and secrets
- ❌ Passwords
- ❌ Private keys
- ❌ Environment files (.env)
- ❌ Database credentials
- ❌ OAuth tokens

**Use .gitignore:**
```bash
# .gitignore
.env
.env.local
.env.*.local
secrets.json
*.key
*.pem
config/credentials.yml
```

**If you accidentally committed secrets:**
```bash
# Remove from latest commit
git rm --cached .env
git commit --amend --no-edit
git push --force-with-lease

# Remove from history (if already pushed)
# Use BFG Repo Cleaner or git-filter-repo
git filter-repo --path .env --invert-paths

# Rotate the compromised secrets IMMEDIATELY!
```

**Use environment variables:**
```javascript
// ❌ Bad
const apiKey = "sk_live_abc123";

// ✅ Good
const apiKey = process.env.API_KEY;
```

**Use secret management:**
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- GitHub Secrets (for CI/CD)

### Branch Protection

**Protect critical branches:**
```
GitHub Settings → Branches → Add rule

Branch name pattern: main

Protections:
☑ Require pull request before merging
  ☑ Require approvals: 1-2
  ☑ Dismiss stale approvals
☑ Require status checks to pass
  ☑ Tests
  ☑ Linting
  ☑ Security scan
☑ Require conversation resolution
☑ Require signed commits
☑ Include administrators
☑ Restrict who can push
☑ Prevent force push
☑ Prevent deletion
```

### Security Scanning

**Pre-commit hooks:**
```bash
# .husky/pre-commit
#!/bin/sh

# Scan for secrets
npm run secrets-scan

# Scan for vulnerabilities
npm audit --audit-level=high

# Run security linter
npm run security-lint
```

**Tools:**
- **git-secrets** - Prevents committing secrets
- **truffleHog** - Scans history for secrets
- **GitLeaks** - Detects hardcoded secrets
- **Dependabot** - Automated dependency updates
- **Snyk** - Vulnerability scanning

---

## Team Collaboration Protocols

### Principle

Establish **clear communication protocols** and **consistent workflows** to enable efficient team collaboration.

### Communication Best Practices

**When to communicate:**
- ✅ Before starting large features
- ✅ When changing shared code
- ✅ When blocked on review
- ✅ When force-pushing shared branch
- ✅ When reverting others' commits

**Communication channels:**
- **PRs** - Technical discussion, code-specific
- **Issues** - Planning, requirements, bugs
- **Slack/Teams** - Quick questions, status updates
- **Meetings** - Complex decisions, design reviews

### Synchronization Practices

**Daily workflow:**
```bash
# Morning: sync with remote
git checkout main
git pull origin main

# Create/update feature branch
git checkout feature/my-feature
git rebase main

# Evening: push progress
git push origin feature/my-feature
```

**Before lunch/end of day:**
```bash
# Push work even if not done
git add .
git commit -m "wip: partial implementation"
git push

# Prevents losing work, enables collaboration
```

### Conflict Prevention

**Strategies:**
1. **Communicate** - Let team know what you're working on
2. **Small PRs** - Merge frequently to avoid drift
3. **Rebase regularly** - Stay current with main
4. **Modular code** - Reduce overlapping changes
5. **Feature toggles** - Deploy incomplete features safely

**When conflicts occur:**
```bash
# 1. Communicate
"Hey, I'm getting conflicts with your recent merge.
Let me know when you're available to pair on resolution."

# 2. Understand both changes
git diff main...feature

# 3. Resolve collaboratively
# Screen share or pair program

# 4. Test thoroughly after resolution
npm test
npm run integration-test
```

### Code Ownership (CODEOWNERS)

**CODEOWNERS file:**
```
# .github/CODEOWNERS

# Default owners for everything
* @team-leads

# Frontend code
/src/frontend/ @frontend-team
*.tsx @frontend-team
*.css @frontend-team

# Backend code
/src/backend/ @backend-team
*.py @backend-team

# Infrastructure
/infrastructure/ @devops-team
Dockerfile @devops-team
*.yml @devops-team

# Documentation
/docs/ @tech-writers
*.md @tech-writers

# Security-sensitive
/src/auth/ @security-team
/src/payments/ @security-team
```

**Benefits:**
- Automatic reviewer assignment
- Clear responsibility
- Prevent unauthorized changes
- Knowledge distribution

### PR Review Rotation

**Fair review distribution:**
- Use round-robin assignment
- Track review load per person
- Don't always ask the same reviewer
- New team members should review too

**Review SLA:**
- Standard PR: 24 hours
- Urgent PR: 4 hours
- Blocking PR: 2 hours
- Escalate if not reviewed in time

### Handling Emergencies

**Hotfix protocol:**
```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix and test
# ... fix ...
npm test

# 3. Fast-track review (still get review!)
gh pr create --label "urgent" --reviewer @team-lead

# 4. Merge immediately after approval
gh pr merge --squash

# 5. Deploy to production
npm run deploy:prod

# 6. Communicate to team
"Hotfix deployed: [description] - [PR link]"

# 7. Backport to active release branches if needed
git checkout release/v1.2
git cherry-pick <hotfix-commit>
```

---

## Repository Hygiene

### Principle

Keep repository **clean, organized, and performant** through regular maintenance.

### Branch Cleanup

**Delete merged branches:**
```bash
# Local branches
git branch --merged main | grep -v "main" | xargs git branch -d

# Remote branches
git remote prune origin

# Or configure automatic pruning
git config --global fetch.prune true
```

**GitHub auto-delete:**
```
Settings → General → Pull Requests
☑ Automatically delete head branches
```

### Repository Size Management

**Check repository size:**
```bash
# See repository size
git count-objects -vH

# Find large files
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '/^blob/ {print substr($0,6)}' \
  | sort --numeric-sort --key=2 \
  | tail -20
```

**Remove large files from history:**
```bash
# Use git-filter-repo (recommended)
git filter-repo --path-glob '*.zip' --invert-paths

# Or BFG Repo-Cleaner
bfg --delete-files '*.zip'
bfg --strip-blobs-bigger-than 50M
```

**Use Git LFS for large files:**
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "*.mp4"
git lfs track "*.zip"

# Add .gitattributes
git add .gitattributes

# Large files now stored in LFS, not Git
```

### Regular Maintenance

**Weekly tasks:**
```bash
# Fetch and prune
git fetch --prune --all

# Delete merged branches
git branch --merged | grep -v "main" | xargs git branch -d

# Clean up reflog
git reflog expire --expire=30.days --all

# Garbage collection
git gc --auto
```

**Monthly tasks:**
```bash
# Aggressive garbage collection
git gc --aggressive --prune=now

# Verify repository integrity
git fsck --full

# Optimize repository
git repack -ad
```

### .gitignore Best Practices

**Comprehensive .gitignore:**
```bash
# Operating System
.DS_Store
Thumbs.db
*.swp

# IDEs
.idea/
.vscode/
*.sublime-workspace

# Dependencies
node_modules/
vendor/
venv/

# Build outputs
dist/
build/
*.pyc
*.class

# Environment
.env
.env.local
secrets.json

# Logs
*.log
logs/

# Test coverage
coverage/
.nyc_output/

# Temporary files
tmp/
temp/
*.tmp
```

**Global gitignore:**
```bash
# Create global ignore file
cat > ~/.gitignore_global << EOF
.DS_Store
.idea/
*.swp
EOF

# Configure Git to use it
git config --global core.excludesfile ~/.gitignore_global
```

---

## Commit Frequency and Size

### Principle

Commit **frequently with focused changes** to create a meaningful, navigable history.

### Optimal Commit Frequency

**Good rhythm:**
- Commit every 30-60 minutes
- Commit after each logical unit of work
- Commit before risky changes
- Commit before taking breaks

**Too infrequent:**
- ❌ One commit per day
- ❌ Massive commits with many changes
- ❌ Lost work if something goes wrong

**Too frequent:**
- ❌ Commit every line change
- ❌ Commits like "a", "b", "c"
- ❌ Cluttered history

### Optimal Commit Size

**Good commit:**
- 50-200 lines of production code
- Single logical change
- Includes related tests
- Leaves project in working state

**Too large:**
- ❌ 1000+ lines in one commit
- ❌ Multiple unrelated changes
- ❌ Entire feature in one commit

**Too small:**
- ❌ One line per commit
- ❌ Separate commits for typos
- ❌ Fragmented logical changes

### Atomic Commits

**What makes a commit atomic:**
- ✅ Single logical change
- ✅ Independently understandable
- ✅ Can be reverted safely
- ✅ Leaves project buildable
- ✅ Tests pass

**Example atomic commits:**
```bash
# Bad: Too much in one commit
git commit -m "Add user auth, refactor database, update docs, fix bugs"

# Good: Atomic commits
git commit -m "feat(auth): add JWT token generation"
git commit -m "test(auth): add token generation tests"
git commit -m "feat(auth): add token validation middleware"
git commit -m "test(auth): add token validation tests"
git commit -m "docs(auth): document authentication flow"
```

### Commit Granularity Examples

**Feature development:**
```bash
# Good granularity
feat(user): add User model
feat(user): add user repository
feat(user): add user service
feat(user): add user controller
test(user): add comprehensive user tests
docs(user): document user API endpoints

# Bad: One huge commit
feat(user): implement complete user system
```

**Refactoring:**
```bash
# Good: Step by step
refactor(auth): extract validation to separate function
refactor(auth): move constants to config file
refactor(auth): rename variables for clarity
test(auth): update tests for refactored code

# Bad: All at once
refactor(auth): major refactoring
```

---

## Summary

Following these best practices ensures:
- **Readable history** - Future developers understand evolution
- **Easy collaboration** - Team works smoothly together
- **Quality code** - Fewer bugs, better maintainability
- **Professional workflow** - Industry-standard practices

**Key Takeaways:**
1. Write clear, conventional commit messages
2. Use consistent branch naming
3. Create focused, reviewable PRs
4. Conduct thorough, respectful code reviews
5. Choose appropriate merge strategies
6. Maintain clean Git history
7. Sign commits for security
8. Communicate with your team
9. Keep repository clean and organized
10. Commit frequently with atomic changes

**Next Steps:**
- Implement commit message template
- Set up branch protection rules
- Configure pre-commit hooks
- Establish team Git guidelines
- Explore [patterns.md](patterns.md) for workflow implementations
