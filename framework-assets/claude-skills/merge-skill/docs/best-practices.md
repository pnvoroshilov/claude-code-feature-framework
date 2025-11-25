# Best Practices for Git Merging

## Team Collaboration

### Communication is Key

communication_practices[5]{practice,benefit}:
Announce large refactors,Prevents simultaneous conflicting work
Coordinate on shared files,Reduces merge conflicts
Use draft PRs early,Gets feedback before conflicts occur
Document merge decisions,Helps future developers understand choices
Quick conflict resolution,Don't let conflicts accumulate

### Team Communication Examples

```bash
# Before starting large refactor
# Post in team chat:
"Starting refactor of auth system (src/auth/*).
 Will be working on this for next 2 days.
 Please coordinate if you need to touch these files.
 See issue #456 for details."

# During merge conflict
# In PR comments:
"Resolved conflict in database.js:
 - Kept our connection pooling changes
 - Integrated their timeout configuration
 - Tested both changes work together
 See commit abc123 for resolution details"
```

## Branch Management

### Branch Hygiene

branch_best_practices[8]{practice,explanation}:
Keep branches small,Target 1-3 days of work maximum
Delete merged branches,Clean up after PR merged
Use descriptive names,feature/user-auth not feature/stuff
One feature per branch,Easier to review and merge
Branch from latest main,Always start from current main
Sync frequently,Merge main into feature daily
Avoid long-lived branches,More than 1 week increases conflict risk
Use branch protection,Prevent force push protect history

### Branch Naming Convention

```
Type/description pattern:

Feature branches:    feature/user-authentication
Bug fixes:          bugfix/login-error
Hotfixes:          hotfix/security-patch
Releases:          release/v1.2.0
Experiments:       experiment/new-algorithm

Examples:
feature/add-payment-integration
bugfix/fix-memory-leak
hotfix/patch-xss-vulnerability
release/v2.0.0-beta
```

### Branch Lifecycle

```bash
# 1. Create from latest main
git checkout main
git pull origin main
git checkout -b feature/user-profile

# 2. Work and commit frequently
git commit -m "feat: add profile model"
git commit -m "feat: add profile API endpoint"
git commit -m "test: add profile tests"

# 3. Keep synchronized with main
git fetch origin
git rebase origin/main  # or merge if branch is shared

# 4. Create PR when ready
gh pr create --title "Add user profile management" \
  --body "Implements user profile CRUD operations"

# 5. After merge, cleanup
git checkout main
git pull origin main
git branch -d feature/user-profile
```

## Merge Commit Messages

### Convention Template

```
Type: Brief summary (50 chars)

More detailed explanation if needed. Explain WHY the
changes were made, not WHAT was changed (git diff shows that).

If there were conflicts, explain how they were resolved:
- file.js: Chose approach X because Y
- config.json: Combined both settings

Resolves: #issue-number
Reviewed-by: @reviewer-username
```

### Real Examples

**Good merge commit:**
```
Merge: Add OAuth2 authentication

Implements GitHub and Google OAuth2 providers with JWT
token management and session handling.

Conflicts resolved in:
- src/auth/config.js: Combined OAuth settings with existing
  email auth configuration
- package-lock.json: Regenerated after merging package.json

Resolves: #234
Reviewed-by: @senior-dev
Tested: Manual testing on staging environment
```

**Bad merge commit:**
```
Merge branch 'feature/stuff'

merged some things
fixed conflicts
```

### Commit Message Types

commit_types[8]{type,when_to_use}:
Merge,Merging branches (automatic or manual)
feat,New feature added
fix,Bug fix
refactor,Code restructuring no behavior change
docs,Documentation changes
test,Adding or updating tests
chore,Build process or tooling changes
perf,Performance improvements

## Pre-merge Validation

### Automated Pre-merge Checklist

```bash
#!/bin/bash
# .git/hooks/pre-merge-commit
# Runs before creating merge commit

echo "Running pre-merge validation..."

# 1. Check for conflict markers
if git diff --cached | grep -E "^(\+|-)<<<<<<< |^(\+|-)=======$|^(\+|-)>>>>>>> "; then
    echo "❌ Error: Conflict markers detected!"
    exit 1
fi

# 2. Check for debug statements
if git diff --cached | grep -E "console\.log|debugger|TODO|FIXME"; then
    echo "⚠️  Warning: Debug statements or TODOs found"
    echo "Continue anyway? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
        exit 1
    fi
fi

# 3. Run linter
echo "Running linter..."
npm run lint || exit 1

# 4. Run tests
echo "Running tests..."
npm test || exit 1

echo "✅ Pre-merge validation passed!"
```

### Manual Checklist

pre_merge_manual_checks[10]{check,command}:
All tests pass,npm test / pytest / cargo test
Linting passes,npm run lint / pylint . / cargo clippy
No conflict markers,grep -r "<<<<<<< " .
Changes reviewed,git diff --staged
Commit message clear,Review in editor
Branch is current,git fetch && git status
CI/CD passes,Check GitHub Actions / GitLab CI
Documentation updated,Ensure README etc. current
Breaking changes noted,Mark in commit message
Team notified,Post in chat/PR comments

## Conflict Prevention Strategies

### Strategy 1: Frequent Integration

```bash
# Daily workflow
# Morning: update feature branch with latest main
git checkout feature/my-work
git fetch origin
git rebase origin/main  # or merge if branch is shared

# Work during the day...
git commit -m "feat: add feature X"

# Evening: push changes
git push origin feature/my-work

# This keeps branch current, prevents massive conflicts
```

### Strategy 2: Small, Focused Changes

```
❌ Bad: Mega PR
- Refactor entire codebase
- Add new feature
- Fix unrelated bugs
- Update dependencies
→ High conflict risk, hard to review

✅ Good: Small PRs
PR 1: Update critical dependency
PR 2: Fix login bug
PR 3: Add user avatar feature
PR 4: Refactor auth module
→ Low conflict risk, easy to review
```

### Strategy 3: Feature Flags

```javascript
// Instead of long-lived branch, use feature flag
const ENABLE_NEW_DASHBOARD = process.env.FEATURE_NEW_DASHBOARD === 'true';

function renderDashboard() {
    if (ENABLE_NEW_DASHBOARD) {
        return <NewDashboard />;
    }
    return <OldDashboard />;
}

// Benefits:
// - Merge to main even if incomplete
// - No long-lived branches
// - Enable for testing, disable for production
```

### Strategy 4: Code Ownership

```
# CODEOWNERS file
# Prevents conflicts by coordinating changes

# Core team owns auth system
/src/auth/ @auth-team

# Frontend team owns UI
/src/components/ @frontend-team

# DevOps owns infrastructure
/.github/ @devops-team
/docker/ @devops-team

# Changes to owned areas require team approval
```

## CI/CD Integration

### Automated Merge Checks

```yaml
# .github/workflows/pr-checks.yml
name: PR Validation

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check for merge conflicts
        run: |
          if git diff --check; then
            echo "✅ No merge conflicts"
          else
            echo "❌ Merge conflicts detected"
            exit 1
          fi

      - name: Run tests
        run: npm test

      - name: Run linter
        run: npm run lint

      - name: Check commit message
        run: |
          # Enforce conventional commits
          npx commitlint --from ${{ github.event.pull_request.base.sha }}
```

### Required Status Checks

```yaml
# Branch protection rules (GitHub UI or API)
required_status_checks:
  - "test"
  - "lint"
  - "build"
  - "security-scan"

require_branches_to_be_up_to_date: true
require_code_owner_reviews: true
required_approving_review_count: 2
```

## Merge Strategy Selection

### By Project Type

project_merge_strategy[6]{project_type,strategy,reason}:
Open source library,Squash merge,Clean history attribution
Microservices,3-way merge,Preserve feature context
Monorepo,3-way merge,Track changes across modules
Solo project,Rebase merge,Perfect linear history
Enterprise app,Squash merge,One commit per feature
Continuous deployment,Squash merge,Easy rollback

### By Team Size

```
Small team (1-5):
→ Flexible, can use rebase for clean history

Medium team (5-20):
→ 3-way merge or squash, coordinate on shared files

Large team (20+):
→ Squash merge, strict branch protection, CODEOWNERS
```

## Documentation Practices

### Document Complex Resolutions

```bash
# In merge commit message
git commit -m "Merge: Integrate payment system with inventory

Conflicts resolved:
- src/checkout.js:
  * Combined new payment flow with existing inventory check
  * Kept transaction handling from payment branch
  * Preserved inventory locking from main branch
  * Added integration tests for combined behavior

- src/api/orders.js:
  * Merged payment webhook handler with order creation
  * Updated order status enum to include payment states
  * Refactored to handle both sync and async payment flows

Technical decisions:
- Used pessimistic locking for inventory during payment
- Added payment timeout of 15 minutes (configurable)
- Maintained backward compatibility with existing orders

Testing:
- All unit tests pass
- Integration tests added for payment + inventory
- Manual testing on staging environment
- Load testing completed (500 concurrent checkouts)

Resolves: #789, #790
Reviewed-by: @tech-lead, @payment-expert"
```

### Maintain Merge Log

Keep a team wiki page documenting tricky merges:

```markdown
# Complex Merge Resolutions

## 2024-11-25: Payment + Inventory Integration

**PR**: #789
**Merge Commit**: abc123
**Complexity**: High (15 files, 3 hours to resolve)

**Conflicts**:
- checkout.js: Payment flow vs inventory check timing
- orders.js: Status enum conflicts

**Resolution**:
- Combined both flows with transaction wrapper
- Extended status enum to support both systems

**Lessons Learned**:
- Should have coordinated earlier
- Feature flags would have helped
- Need better test coverage in checkout flow

**Team Members**: @dev1, @dev2, @tech-lead
```

## Tooling Recommendations

recommended_tools[8]{tool,purpose}:
GitHub CLI (gh),Manage PRs from command line
GitKraken,Visual Git client
Meld,Visual diff and merge tool
diff-so-fancy,Better git diff output
tig,Terminal Git repository browser
git-extras,Additional Git utilities
commitizen,Enforce commit message format
husky,Git hooks management

### Git Configuration

```bash
# Recommended Git settings

# Better diff algorithm
git config --global merge.algorithm patience

# Show conflict markers with common ancestor
git config --global merge.conflictstyle diff3

# Automatically reuse conflict resolutions
git config --global rerere.enabled true

# Better merge commit formatting
git config --global commit.cleanup scissors

# Prune deleted remote branches automatically
git config --global fetch.prune true

# Use main as default branch
git config --global init.defaultBranch main
```

## Summary of Best Practices

top_10_practices[10]{practice,impact}:
Small frequent merges,Prevents massive conflicts
Communicate early,Coordinates team work
Test before merging,Catches integration issues
Use branch protection,Enforces quality standards
Document resolutions,Helps future developers
Keep branches current,Reduces conflict scope
Feature flags over long branches,Enables continuous integration
Meaningful commit messages,Improves code archaeology
Automate validation,Consistent quality checks
Clean up merged branches,Maintains repository hygiene

## Anti-patterns to Avoid

merge_antipatterns[8]{antipattern,why_bad}:
Long-lived feature branches,Massive conflicts impossible to resolve
Force push to shared branches,Destroys team's work
Ignoring conflicts,Broken code in production
"Works on my machine",Insufficient testing
Mega PRs,Too complex to review properly
No commit message,Lost context for future
Skip CI checks,Quality issues slip through
Never delete branches,Repository becomes cluttered

## Final Advice

1. **Prevention > Resolution** - Avoid conflicts rather than resolve them
2. **Communicate** - Talk to your team about changes
3. **Test thoroughly** - Automated and manual testing
4. **Document decisions** - Future you will thank you
5. **Keep learning** - Git is powerful, master it gradually

Remember: The best merge is one that happens smoothly because you prevented conflicts through good practices.
