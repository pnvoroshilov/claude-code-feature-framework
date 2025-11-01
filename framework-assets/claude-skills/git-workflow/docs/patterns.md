# Git Workflow Patterns

## Table of Contents

- [GitFlow Workflow](#gitflow-workflow)
- [GitHub Flow](#github-flow)
- [Trunk-Based Development](#trunk-based-development)
- [Feature Toggle Workflow](#feature-toggle-workflow)
- [Hotfix Workflow](#hotfix-workflow)
- [Release Train Model](#release-train-model)
- [Fork and Pull Request Pattern](#fork-and-pull-request-pattern)
- [Git Workflow Anti-Patterns](#git-workflow-anti-patterns)

## GitFlow Workflow

### What It Is

GitFlow is a branching model designed around project releases, with multiple long-lived branches for different purposes. Created by Vincent Driessen, it provides structure for managing features, releases, and hotfixes.

### Branch Structure

```
main (master)     - Production-ready code
  └── develop    - Integration branch
       ├── feature/* - New features
       ├── release/* - Release preparation
       └── hotfix/*  - Production fixes
```

**Branch purposes:**
- **main** - Always production-ready, deployed to production
- **develop** - Integration branch, contains latest development changes
- **feature/** - New feature development, branch from develop
- **release/** - Release preparation, branch from develop
- **hotfix/** - Emergency production fixes, branch from main

### When to Use

**GitFlow is ideal for:**
- ✅ Projects with scheduled releases (quarterly, monthly)
- ✅ Multiple versions in production simultaneously
- ✅ Need to support old versions with hotfixes
- ✅ Strict release management required
- ✅ Large teams with defined roles

**Not ideal for:**
- ❌ Continuous deployment environments
- ❌ Small teams wanting simplicity
- ❌ Projects with single production version
- ❌ Rapid iteration requirements

### Implementation

**1. Initialize GitFlow:**
```bash
# Create main and develop branches
git checkout -b develop main
git push -u origin develop

# Set up branch protections for both main and develop
```

**2. Feature development:**
```bash
# Start feature
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# Work on feature
git add .
git commit -m "feat(auth): implement JWT tokens"

# Keep up to date with develop
git fetch origin
git rebase origin/develop

# Finish feature
git checkout develop
git merge --no-ff feature/user-authentication
git push origin develop
git branch -d feature/user-authentication
```

**3. Release preparation:**
```bash
# Start release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Bump version in package.json, update changelog
npm version minor  # 1.1.0 -> 1.2.0
git add package.json CHANGELOG.md
git commit -m "chore(release): prepare v1.2.0"

# Bug fixes allowed on release branch
git commit -m "fix(release): resolve login issue"

# Finish release - merge to both main and develop
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# Delete release branch
git branch -d release/v1.2.0
```

**4. Hotfix workflow:**
```bash
# Critical bug in production!
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# Fix the bug
git commit -m "fix(security): patch SQL injection vulnerability"

# Merge to both main and develop
git checkout main
git merge --no-ff hotfix/security-patch
git tag -a v1.2.1 -m "Hotfix: security patch"
git push origin main --tags

git checkout develop
git merge --no-ff hotfix/security-patch
git push origin develop

# Delete hotfix branch
git branch -d hotfix/security-patch

# Deploy to production immediately
```

### Visualization

```
main:     A-----B-----F-----G-----H (tags: v1.0, v1.1, v1.2)
           \         /       \   /
develop:    C---D---E---I---J---K
             \     /     \
feature:      L---M       N---O

release:                P---Q

hotfix:                     R
```

### Best Practices

**Feature branches:**
- Branch from: `develop`
- Merge to: `develop`
- Naming: `feature/` or `feature/<issue>-<description>`
- Lifespan: Days to weeks
- Merge type: `--no-ff` (create merge commit)

**Release branches:**
- Branch from: `develop`
- Merge to: `main` AND `develop`
- Naming: `release/v<version>`
- Only bug fixes allowed, no new features
- Update version numbers
- Generate changelog
- Merge type: `--no-ff`

**Hotfix branches:**
- Branch from: `main`
- Merge to: `main` AND `develop` (or current release)
- Naming: `hotfix/<description>`
- For critical production issues only
- Tag on main after merge
- Deploy immediately

### Complete Example

**Scenario: Add payment feature, release v2.0.0, fix critical bug**

```bash
# === FEATURE DEVELOPMENT ===
git checkout develop
git checkout -b feature/stripe-payment

# Implement payment integration
git commit -m "feat(payment): add Stripe SDK integration"
git commit -m "feat(payment): create payment controller"
git commit -m "test(payment): add payment tests"

# Merge to develop
git checkout develop
git merge --no-ff feature/stripe-payment
git push origin develop
git branch -d feature/stripe-payment

# === RELEASE PREPARATION ===
git checkout -b release/v2.0.0

# Final preparations
npm version major  # 1.9.0 -> 2.0.0
npm run build
npm run test
git commit -m "chore(release): bump version to 2.0.0"

# Generate changelog
npm run changelog
git add CHANGELOG.md
git commit -m "docs(release): update changelog for v2.0.0"

# Merge release to main
git checkout main
git merge --no-ff release/v2.0.0
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v2.0.0
git push origin develop

# Deploy to production
git branch -d release/v2.0.0

# === HOTFIX (if needed) ===
# Production bug discovered!
git checkout main
git checkout -b hotfix/payment-error

# Fix bug
git commit -m "fix(payment): resolve payment confirmation issue"

# Merge to main
git checkout main
git merge --no-ff hotfix/payment-error
git tag -a v2.0.1 -m "Hotfix: payment confirmation"
git push origin main --tags

# Merge to develop
git checkout develop
git merge --no-ff hotfix/payment-error
git push origin develop

git branch -d hotfix/payment-error

# Deploy hotfix immediately
```

### Automation

**Automated GitFlow with tools:**

```bash
# Install git-flow
brew install git-flow  # macOS
apt-get install git-flow  # Linux

# Initialize
git flow init

# Use git-flow commands
git flow feature start user-authentication
git flow feature finish user-authentication

git flow release start 1.2.0
git flow release finish 1.2.0

git flow hotfix start security-patch
git flow hotfix finish security-patch
```

---

## GitHub Flow

### What It Is

GitHub Flow is a lightweight, branch-based workflow designed for teams practicing continuous deployment. It's simpler than GitFlow with only one long-lived branch (`main`).

### Branch Structure

```
main          - Always deployable
  ├── feature/user-auth
  ├── feature/dashboard
  └── bugfix/login-error
```

**Principles:**
1. Main branch is always deployable
2. Create descriptive branches from main
3. Commit and push regularly
4. Open PR when ready for feedback
5. Merge after review and CI passes
6. Deploy immediately after merge

### When to Use

**GitHub Flow is ideal for:**
- ✅ Continuous deployment environments
- ✅ Teams deploying multiple times per day
- ✅ Single production version
- ✅ Simple, fast-moving projects
- ✅ Small to medium teams

**Not ideal for:**
- ❌ Multiple versions in production
- ❌ Scheduled releases
- ❌ Complex release processes
- ❌ Support for old versions

### Implementation

**Complete workflow:**

```bash
# 1. Create branch from main
git checkout main
git pull origin main
git checkout -b feature/user-dashboard

# 2. Develop feature with regular commits
git add src/dashboard.tsx
git commit -m "feat(dashboard): add user dashboard component"

git add tests/dashboard.test.tsx
git commit -m "test(dashboard): add dashboard tests"

# 3. Push regularly
git push -u origin feature/user-dashboard

# 4. Open PR (even if not finished - draft PR)
gh pr create --draft --title "Add user dashboard"

# 5. Continue development
git commit -m "feat(dashboard): add analytics widget"
git push

# 6. Mark PR ready when complete
gh pr ready

# 7. Code review and discussion
# Reviewers leave comments
# You address feedback

# 8. CI/CD runs automatically
# - Tests
# - Linting
# - Security scans
# - Build verification

# 9. Merge after approval
gh pr merge --squash

# 10. Automatic deployment to production
# GitHub Actions deploys automatically

# 11. Delete branch
git branch -d feature/user-dashboard
git push origin --delete feature/user-dashboard
```

### Visualization

```
main:  A---B---E---F---H---I
            \     /     \   /
feature-1:   C---D       G

Every merge to main triggers deployment
```

### Best Practices

**Branch lifecycle:**
- Create from latest main
- Keep branches short-lived (hours to days)
- Push early and often
- Use draft PRs for early feedback
- Merge as soon as ready
- Delete after merge

**Pull request practices:**
- Open PR early (even if not ready)
- Use draft PRs to signal WIP
- Request review when ready
- Keep PRs small (200-400 lines)
- Ensure CI passes before merge
- Squash commits when merging

**Deployment practices:**
- Main is always deployable
- Deploy immediately after merge
- Use feature flags for incomplete features
- Monitor deployments closely
- Rollback if issues detected

### Complete Example

**Scenario: Implement new dashboard feature**

```bash
# Day 1: Start feature
git checkout main
git pull origin main
git checkout -b feature/analytics-dashboard

# Initial work
git commit -m "feat(dashboard): add dashboard skeleton"
git push -u origin feature/analytics-dashboard

# Open draft PR for visibility
gh pr create \
  --draft \
  --title "Add analytics dashboard" \
  --body "Work in progress - adding analytics dashboard

## TODO
- [ ] Implement chart components
- [ ] Add data fetching
- [ ] Add tests
- [ ] Update documentation"

# Continue development
git commit -m "feat(dashboard): implement chart components"
git commit -m "feat(dashboard): add data fetching hooks"
git push

# Day 2: Complete feature
git commit -m "test(dashboard): add comprehensive tests"
git commit -m "docs(dashboard): update documentation"
git push

# Mark PR as ready
gh pr ready

# Update PR description
gh pr edit --body "Implemented analytics dashboard with real-time charts

## Changes
- Added Chart.js integration
- Implemented real-time data updates
- Added comprehensive test coverage
- Updated documentation

## Testing
- All unit tests passing
- Manual testing on dev environment
- Performance testing completed

Closes #123"

# Reviewers review code
# CI runs and passes

# After approval, merge
gh pr merge --squash --delete-branch

# Automatic deployment to production via GitHub Actions
# Monitor deployment in real-time
```

### GitHub Actions Integration

**Automated deployment on merge:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: npm run deploy:prod
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployed to production'
```

### Feature Flags Pattern

**Deploy incomplete features safely:**

```javascript
// feature-flags.js
const featureFlags = {
  newDashboard: process.env.FEATURE_NEW_DASHBOARD === 'true',
  paymentV2: process.env.FEATURE_PAYMENT_V2 === 'true'
};

// Use in code
if (featureFlags.newDashboard) {
  return <NewDashboard />;
} else {
  return <OldDashboard />;
}

// Merge to main with flag off
// Enable in production when ready
// No need for long-lived feature branches
```

---

## Trunk-Based Development

### What It Is

Trunk-Based Development (TBD) is a branching model where developers collaborate on code in a single branch (trunk/main) with very short-lived feature branches (hours, not days).

### Key Characteristics

- **Single long-lived branch** (trunk/main)
- **Very short-lived feature branches** (< 1 day)
- **Frequent integration** (multiple times per day)
- **Small commits** directly to trunk (or via PR)
- **Feature flags** for incomplete features

### When to Use

**Trunk-based development is ideal for:**
- ✅ High-performing teams
- ✅ Continuous integration/continuous deployment
- ✅ Fast feedback loops required
- ✅ Teams comfortable with feature flags
- ✅ Strong automated testing

**Not ideal for:**
- ❌ Teams new to CI/CD
- ❌ Weak test coverage
- ❌ Long review processes
- ❌ Complex approval workflows

### Implementation

**Variant 1: Direct commits to trunk (small teams)**

```bash
# Pull latest
git checkout main
git pull origin main

# Make small change
git add src/user.js
git commit -m "feat(user): add email validation"

# Push directly to main
git push origin main

# CI/CD automatically tests and deploys
```

**Variant 2: Short-lived branches (larger teams)**

```bash
# Create short-lived branch
git checkout -b user-email-validation

# Make focused change (2-3 hours work max)
git commit -m "feat(user): add email validation"

# Push and create PR
git push -u origin user-email-validation
gh pr create --title "Add email validation"

# Quick review (< 2 hours)
# Merge immediately after approval
gh pr merge --squash

# Delete branch
git branch -d user-email-validation
```

### Visualization

```
main: A---B---C---D---E---F---G---H
       \   / \   /       /       /
        \ /   \ /       /       /
Short:   X     Y       Z       W  (hours old, not days)

Multiple merges per day from entire team
```

### Best Practices

**Commit frequency:**
- Commit at least once per day
- Preferably multiple times per day
- Every commit should build and pass tests
- Small, incremental changes

**Branch strategy:**
- Branches live for hours, not days
- 1-3 commits per branch maximum
- Merge before end of day
- No long-lived feature branches

**Feature flags:**
```javascript
// Incomplete feature hidden behind flag
if (featureFlags.newCheckout) {
  return <NewCheckoutFlow />;
}
return <OldCheckoutFlow />;

// Merge code even if not complete
// Enable flag when ready
```

**Testing requirements:**
- Comprehensive automated test suite
- Tests run on every commit
- Fast test execution (< 10 minutes)
- Prevent broken builds on main

### Complete Example

**Scenario: Add user profile feature over 2 days**

```bash
# === Day 1, Morning (2 hours) ===
git checkout main
git pull origin main
git checkout -b profile-model

# Create user profile model
git commit -m "feat(profile): add user profile model"
git commit -m "test(profile): add profile model tests"

# Push and merge
git push -u origin profile-model
gh pr create --title "Add user profile model"
# Quick review
gh pr merge --squash
git checkout main
git pull origin main

# === Day 1, Afternoon (3 hours) ===
git checkout -b profile-api

# Add API endpoints (behind feature flag)
git commit -m "feat(profile): add profile API endpoints"
git commit -m "test(profile): add API tests"

# Push and merge
git push -u origin profile-api
gh pr create --title "Add profile API"
# Quick review
gh pr merge --squash
git checkout main
git pull origin main

# === Day 2, Morning (3 hours) ===
git checkout -b profile-ui

# Add UI components (behind feature flag)
git commit -m "feat(profile): add profile UI components"
git commit -m "test(profile): add UI tests"

# Push and merge
git push -u origin profile-ui
gh pr create --title "Add profile UI"
# Quick review
gh pr merge --squash
git checkout main
git pull origin main

# === Day 2, Afternoon ===
# Enable feature flag in production
# Feature is live!
# No long-lived branches needed
```

### Feature Flag Management

```javascript
// feature-flags.service.js
class FeatureFlags {
  constructor() {
    this.flags = {
      userProfile: {
        enabled: process.env.FEATURE_USER_PROFILE === 'true',
        rollout: 0.1  // 10% of users
      }
    };
  }

  isEnabled(feature, userId) {
    const flag = this.flags[feature];
    if (!flag.enabled) return false;

    // Gradual rollout
    const hash = this.hashUserId(userId);
    return hash < flag.rollout;
  }
}

// Usage
if (featureFlags.isEnabled('userProfile', user.id)) {
  return <UserProfile user={user} />;
}
```

### Benefits and Challenges

**Benefits:**
- ✅ Fast integration of changes
- ✅ Reduces merge conflicts
- ✅ Encourages small, atomic commits
- ✅ Forces good CI/CD practices
- ✅ Faster feedback loops

**Challenges:**
- ⚠️ Requires excellent test coverage
- ⚠️ Needs fast CI/CD pipelines
- ⚠️ Feature flag management complexity
- ⚠️ Team discipline required
- ⚠️ Cultural shift for many teams

---

## Feature Toggle Workflow

### What It Is

Feature toggles (feature flags) allow you to merge code to production while keeping features disabled until ready. Enables continuous integration even for incomplete features.

### Types of Feature Toggles

**1. Release toggles** - Control feature rollout
```javascript
if (featureFlags.newPaymentFlow) {
  return <NewPaymentFlow />;
}
return <OldPaymentFlow />;
```

**2. Experiment toggles** - A/B testing
```javascript
if (experiment.variant === 'A') {
  return <VariantA />;
}
return <VariantB />;
```

**3. Ops toggles** - Operational control
```javascript
if (featureFlags.enableCaching) {
  return cacheService.get(key);
}
return database.query(key);
```

**4. Permission toggles** - User permissions
```javascript
if (user.hasFeature('advancedDashboard')) {
  return <AdvancedDashboard />;
}
return <BasicDashboard />;
```

### Implementation

**Simple feature flag system:**

```javascript
// config/feature-flags.js
module.exports = {
  features: {
    newDashboard: {
      enabled: process.env.FEATURE_NEW_DASHBOARD === 'true',
      description: 'New analytics dashboard',
      added: '2024-01-15',
      jira: 'PROJ-123'
    },
    paymentV2: {
      enabled: process.env.FEATURE_PAYMENT_V2 === 'true',
      description: 'New payment processing',
      added: '2024-01-20',
      jira: 'PROJ-456'
    }
  }
};

// services/feature-flag.service.js
class FeatureFlagService {
  isEnabled(featureName) {
    const feature = features[featureName];
    if (!feature) {
      console.warn(`Feature ${featureName} not found`);
      return false;
    }
    return feature.enabled;
  }
}

// Usage in React component
function Dashboard() {
  const featureFlags = useFeatureFlags();

  if (featureFlags.isEnabled('newDashboard')) {
    return <NewDashboard />;
  }

  return <OldDashboard />;
}

// Usage in backend
app.get('/api/payment', (req, res) => {
  if (featureFlags.isEnabled('paymentV2')) {
    return paymentServiceV2.process(req.body);
  }
  return paymentServiceV1.process(req.body);
});
```

### Workflow with Feature Toggles

```bash
# Day 1: Start feature with toggle OFF
git checkout -b feature/new-dashboard

# Implement feature behind toggle
cat > src/Dashboard.jsx << EOF
function Dashboard() {
  if (featureFlags.newDashboard) {
    return <NewDashboard />;  // New code
  }
  return <OldDashboard />;  // Existing code
}
EOF

git commit -m "feat(dashboard): add new dashboard behind feature flag"
git push -u origin feature/new-dashboard

# Merge to main with toggle OFF
gh pr create --title "Add new dashboard (behind feature flag)"
gh pr merge --squash

# Feature is in production but disabled
# No one sees it yet

# Day 2-3: Continue development
# Add more features
# All behind same toggle
# Merge incrementally

# Day 4: Enable in staging
# Update staging environment
FEATURE_NEW_DASHBOARD=true

# Test in staging

# Day 5: Gradual rollout
# 10% of users
featureFlags.newDashboard.rollout = 0.1

# Monitor metrics

# 50% of users
featureFlags.newDashboard.rollout = 0.5

# Monitor metrics

# 100% rollout
featureFlags.newDashboard.rollout = 1.0

# Week later: Remove toggle
# Once confident, remove flag code
git checkout -b remove-dashboard-toggle

# Remove toggle logic
cat > src/Dashboard.jsx << EOF
function Dashboard() {
  return <NewDashboard />;  // Now default
}
EOF

git commit -m "chore(dashboard): remove dashboard feature flag"
```

### Best Practices

**Toggle lifecycle:**
1. **Add toggle** - Wrap new feature
2. **Develop** - Build behind toggle
3. **Test** - Enable in test environments
4. **Roll out** - Gradual production rollout
5. **Monitor** - Watch metrics and errors
6. **Remove** - Delete toggle code after stabilization

**Toggle hygiene:**
- Document all toggles
- Set expiration dates
- Regular toggle cleanup
- Maximum toggle lifespan (e.g., 2 months)
- Alert on old toggles

**Monitoring:**
```javascript
// Log feature flag usage
logger.info('Feature flag accessed', {
  feature: 'newDashboard',
  enabled: flag.enabled,
  user: user.id
});

// Metrics
metrics.increment('feature_flag.new_dashboard.enabled');
```

---

## Hotfix Workflow

### What It Is

Hotfix workflow is a process for rapidly fixing critical production issues with minimal disruption and maximum safety.

### When to Use Hotfix

**Use hotfix workflow for:**
- 🔴 Critical production bugs
- 🔴 Security vulnerabilities
- 🔴 Data corruption issues
- 🔴 System down/unavailable
- 🔴 Significant revenue impact

**NOT for:**
- 🟡 Non-critical bugs
- 🟡 Feature requests
- 🟡 Performance improvements
- 🟡 Refactoring

### Hotfix Process (GitFlow Style)

```bash
# 1. ALERT: Critical bug in production!
# "Payment processing failing for all users"

# 2. Create hotfix branch from main (production)
git checkout main
git pull origin main
git checkout -b hotfix/payment-processing

# 3. Reproduce and fix
npm run test:integration
# Fix the bug
git commit -m "fix(payment): resolve Stripe API timeout issue

Critical bug causing payment failures for all users.
Issue: Stripe API calls timing out due to missing timeout config.
Fix: Add 30s timeout and retry logic.

Affects: All payment transactions since deploy at 14:00 UTC
Impact: ~$50k revenue lost
Root cause: Missing timeout in Stripe client initialization"

# 4. Test fix thoroughly
npm run test
npm run test:integration
npm run test:e2e

# 5. Fast-track review (still get review!)
git push -u origin hotfix/payment-processing
gh pr create \
  --label "hotfix" \
  --label "critical" \
  --reviewer @tech-lead \
  --title "HOTFIX: Fix payment processing failure" \
  --body "Critical production issue - payment processing failing

## Issue
Payment processing failing for 100% of users since 14:00 UTC

## Root Cause
Missing timeout configuration in Stripe client

## Fix
- Add 30s timeout to Stripe API calls
- Add retry logic with exponential backoff
- Add error logging

## Testing
- All unit tests pass
- Integration tests pass
- Manual testing completed

## Impact
- Fixes payment processing
- No breaking changes
- Safe to deploy immediately

Requires immediate deployment"

# 6. Expedited review (< 30 minutes)
# Tech lead reviews and approves

# 7. Merge to main
gh pr merge --squash

# 8. Tag hotfix version
git checkout main
git pull origin main
git tag -a v1.2.3 -m "Hotfix: Payment processing fix"
git push origin --tags

# 9. Deploy to production IMMEDIATELY
npm run deploy:prod

# 10. Monitor deployment
# Watch error rates
# Check payment success rates
# Verify fix is working

# 11. Merge back to develop (if using GitFlow)
git checkout develop
git merge main
git push origin develop

# 12. Post-incident
# Write incident report
# Identify preventive measures
# Update monitoring/alerts
```

### Hotfix Communication

**During hotfix:**
```
Slack/Teams message:
"🔴 CRITICAL: Payment processing down
- Issue: Stripe API timeouts
- Impact: All payments failing
- Status: Hotfix in progress
- ETA: 30 minutes
- Team: @tech-lead @devops working on it"

Every 15 minutes:
"Update: Hotfix PR created and under review"
"Update: Hotfix approved, deploying"
"Update: Hotfix deployed, monitoring"
"✅ RESOLVED: Payments processing normally"
```

**Post-incident report:**
```markdown
# Post-Incident Report: Payment Processing Failure

## Incident Summary
- Date: 2024-01-15
- Duration: 45 minutes (14:00-14:45 UTC)
- Severity: Critical
- Impact: 100% payment failures, ~$50k revenue

## Timeline
- 14:00 - Deploy v1.2.2 to production
- 14:05 - First payment failures reported
- 14:10 - Incident declared, hotfix team assembled
- 14:15 - Root cause identified
- 14:25 - Hotfix PR created
- 14:35 - PR approved
- 14:40 - Hotfix deployed
- 14:45 - Issue resolved, monitoring

## Root Cause
Missing timeout configuration in Stripe client initialization
caused indefinite hangs on API calls.

## Fix Applied
- Added 30s timeout to Stripe client
- Implemented retry logic with exponential backoff
- Enhanced error logging

## Preventive Measures
1. Add integration tests for payment timeouts
2. Implement circuit breaker pattern
3. Add monitoring for payment success rate
4. Review all external API clients for timeout config
5. Update deployment checklist

## Action Items
- [ ] Complete integration tests (Owner: @dev1, Due: 2024-01-18)
- [ ] Implement circuit breaker (Owner: @dev2, Due: 2024-01-22)
- [ ] Add monitoring alerts (Owner: @devops, Due: 2024-01-17)
```

### Hotfix Testing Checklist

```
Before deploying hotfix:
- [ ] Issue reproduced locally
- [ ] Fix verified to resolve issue
- [ ] No new errors introduced
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Code reviewed (expedited)
- [ ] Deployment plan confirmed
- [ ] Rollback plan ready
- [ ] Monitoring in place
```

---

## Release Train Model

### What It Is

Release train is a scheduled release pattern where releases happen on a fixed schedule (weekly, bi-weekly), like a train leaving the station at set times. Features ready in time make the train; others wait for next train.

### Key Characteristics

- **Fixed release schedule** (e.g., every Tuesday at 2 PM)
- **Features board the train when ready**
- **Train leaves on time regardless**
- **Predictable release rhythm**
- **Parallel development tracks**

### When to Use

**Release train is ideal for:**
- ✅ Large organizations with multiple teams
- ✅ Need predictable release schedule
- ✅ Many concurrent features in development
- ✅ Stakeholder communication requirements
- ✅ Coordinated marketing/sales efforts

### Implementation

**Weekly release train:**

```bash
# Week 1: Develop features
# Monday-Thursday: Development
git checkout -b feature/dashboard-widget
# ... development work ...
git commit -m "feat(dashboard): add analytics widget"

# Friday: Feature freeze for next Tuesday release
# Only features merged by Friday 5 PM make next release

# Week 2: Release week
# Monday: Final testing and bug fixes
# Tuesday 2 PM: Release train departs

# Release branch created Monday
git checkout main
git pull origin main
git checkout -b release/2024-01-15

# Only bug fixes merged to release branch
git commit -m "fix(dashboard): resolve chart rendering"

# Tuesday: Deploy release
git checkout main
git merge release/2024-01-15
git tag -a v1.15.0 -m "Release train 2024-01-15"
git push origin main --tags

# Deploy to production
npm run deploy:prod

# Features not ready wait for next train (next Tuesday)
```

### Visualization

```
       Train 1          Train 2          Train 3
         (Week 1)         (Week 2)         (Week 3)
          ↓                ↓                ↓
main: ----R1--------------R2--------------R3----
      /  |  \          /  |  \          /  |  \
F1: ----✓              |  |  |          |  |  |
F2: -------✓           |  |  |          |  |  |
F3: ----------X (miss) --✓  |          |  |  |
F4: ----------------X (miss) --✓       |  |  |
F5: ----------------------X (miss) --------|--✓

✓ = Made the train
X = Missed, wait for next train
```

### Best Practices

**Feature development:**
- Start features early in cycle
- Aim to complete 2-3 days before train
- Use feature flags if cutting it close
- Don't rush to make the train

**Cut-off times:**
- Feature complete: Friday before release
- Code freeze: Monday morning
- Release branch: Monday 9 AM
- Bug fixes only: Monday-Tuesday
- Release: Tuesday 2 PM

**Communication:**
```markdown
# Release Train Communication

## Release Train #45 - January 15, 2024

### Schedule
- Feature Cut-off: Friday, Jan 12, 5:00 PM
- Code Freeze: Monday, Jan 15, 9:00 AM
- Release: Tuesday, Jan 16, 2:00 PM

### Boarding This Train
✅ User Dashboard Widget (@dev1) - MERGED
✅ Payment Improvements (@dev2) - MERGED
✅ Search Optimization (@dev3) - MERGED

### Missing This Train (Next: Jan 23)
❌ Advanced Analytics (@dev4) - Not ready
❌ Mobile App Updates (@dev5) - Testing incomplete

### Risk Items
⚠️ Payment Improvements - Monitor closely after release
```

### Emergency Off-ramp

**If critical issue found:**
```bash
# Option 1: Remove feature from release train
git revert <feature-commit>
git push origin release/2024-01-15

# Option 2: Delay release train
# Communicate delay
# Fix issue
# Reschedule release

# Option 3: Release without problematic feature
# Use feature flag to disable
# Release train proceeds on schedule
```

---

## Fork and Pull Request Pattern

### What It Is

Fork and pull request pattern is used for open source projects where external contributors don't have write access to the main repository. Contributors fork the repository, make changes, and submit pull requests.

### Workflow

```bash
# 1. Fork repository on GitHub
# Click "Fork" button on github.com/original/repo

# 2. Clone your fork
git clone git@github.com:your-username/repo.git
cd repo

# 3. Add upstream remote (original repository)
git remote add upstream git@github.com:original/repo.git

# 4. Create feature branch
git checkout -b feature/add-documentation

# 5. Make changes
git add docs/
git commit -m "docs: improve installation guide"

# 6. Push to your fork
git push origin feature/add-documentation

# 7. Create pull request
# Go to GitHub and click "Create Pull Request"
# Base: original/repo:main
# Head: your-username/repo:feature/add-documentation

# 8. Address review feedback
git commit -m "docs: address review feedback"
git push origin feature/add-documentation

# 9. Keep your fork updated
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# 10. After PR merged, clean up
git branch -d feature/add-documentation
git push origin --delete feature/add-documentation
```

### Best Practices for Contributors

**Before contributing:**
- Read CONTRIBUTING.md
- Check existing issues and PRs
- Discuss large changes first
- Follow project conventions

**Pull request quality:**
- Clear description
- Reference related issues
- Include tests
- Follow coding standards
- Keep PRs focused and small

### Best Practices for Maintainers

**Repository setup:**
```markdown
# CONTRIBUTING.md

## How to Contribute

### 1. Fork and Clone
```bash
git clone git@github.com:your-username/project.git
cd project
git remote add upstream git@github.com:original/project.git
```

### 2. Create Branch
```bash
git checkout -b feature/your-feature
```

### 3. Make Changes
- Follow our [Code Style Guide](STYLE.md)
- Add tests for new features
- Update documentation

### 4. Submit PR
- Clear title and description
- Reference related issues
- Ensure CI passes

## Code Review Process
- PRs reviewed within 48 hours
- Address feedback promptly
- Squash commits before merge
```

---

## Git Workflow Anti-Patterns

### Anti-Pattern 1: Long-Lived Feature Branches

**Problem:**
```
main: A---B-------------------F
       \                     /
feature: C---D---E---G---H---I  (3 months old!)

# Massive merge conflicts
# Out of sync with main
# Hard to review
```

**Solution:**
- Keep branches short-lived (days, not weeks/months)
- Merge to main frequently
- Use feature flags for incomplete features
- Break large features into smaller increments

### Anti-Pattern 2: Merge Commits Everywhere

**Problem:**
```
main: A---M1---M2---M3---M4 (all merge commits, no actual work visible)
```

**Solution:**
- Use squash merging for PRs
- Or rebase before merging
- Keep history clean and linear

### Anti-Pattern 3: Committing to Main Directly

**Problem:**
```
# No code review
# No CI checks
# No discussion
# Mistakes go directly to production
```

**Solution:**
- Protect main branch
- Require PRs
- Require reviews
- Require CI passing

### Anti-Pattern 4: Giant Pull Requests

**Problem:**
```
PR #123: Implement entire user system
Files changed: 145
+15,234 lines
-2,156 lines
```

**Solution:**
- Break into smaller PRs
- 200-400 lines maximum
- Single responsibility
- Easier to review

### Anti-Pattern 5: Unclear Commit Messages

**Problem:**
```
❌ git commit -m "fix"
❌ git commit -m "updates"
❌ git commit -m "wip"
```

**Solution:**
```
✅ git commit -m "fix(auth): resolve JWT token expiration bug

Tokens were expiring after 1 hour instead of 24 hours.
Fixed by correcting the expiresIn configuration.

Closes #456"
```

### Anti-Pattern 6: No Branch Protection

**Problem:**
- Anyone can push to main
- No review required
- No CI checks
- Easy to break production

**Solution:**
- Enable branch protection
- Require PR reviews
- Require status checks
- Prevent force push

---

## Summary

Choose the right workflow for your team:

- **GitFlow** - Structured releases, multiple versions
- **GitHub Flow** - Continuous deployment, simplicity
- **Trunk-Based** - High-performing teams, fast iteration
- **Feature Toggles** - Continuous integration with control
- **Release Train** - Predictable schedule, large teams
- **Fork/PR** - Open source, external contributors

**Key Principles:**
1. Consistency within team
2. Clear branch purposes
3. Regular integration
4. Small, frequent merges
5. Always reviewable code
6. Automated testing
7. Fast feedback loops
8. Adapt to team needs

**Next Steps:**
- Choose workflow for your team
- Document team conventions
- Set up automation (CI/CD)
- Train team members
- Iterate and improve

See [../examples/](../examples/) for hands-on workflow implementations.
