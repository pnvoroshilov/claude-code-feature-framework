# Example 2: Resolving Text Conflicts

## Scenario

Two developers worked on the same file simultaneously:
- **Developer A**: Updated API endpoint configuration
- **Developer B**: Added new API endpoints

Git cannot auto-merge - manual resolution needed.

## The Conflict

### Setup

```bash
# Main branch state
git checkout main
cat src/api/config.js
```

```javascript
// src/api/config.js (main branch)
const API_CONFIG = {
    baseURL: "https://api.example.com",
    timeout: 5000,
    endpoints: {
        users: "/users",
        posts: "/posts"
    }
};
```

### Branch A: Update Configuration

```javascript
// Developer A's changes (branch: feature/update-config)
const API_CONFIG = {
    baseURL: "https://api.production.com",  // Changed
    timeout: 10000,                         // Changed
    retries: 3,                             // Added
    endpoints: {
        users: "/users",
        posts: "/posts"
    }
};
```

### Branch B: Add Endpoints

```javascript
// Developer B's changes (branch: feature/new-endpoints)
const API_CONFIG = {
    baseURL: "https://api.example.com",
    timeout: 5000,
    endpoints: {
        users: "/users",
        posts: "/posts",
        comments: "/comments",              // Added
        likes: "/likes"                     // Added
    }
};
```

## Merging Process

### Step 1: Merge First Branch (Success)

```bash
# Merge branch A first
git checkout main
git merge feature/update-config
# Updating abc123..def456
# Fast-forward
#  src/api/config.js | 3 ++-
#  1 file changed, 2 insertions(+), 1 deletion(-)

# Push
git push origin main
```

### Step 2: Merge Second Branch (Conflict!)

```bash
# Try to merge branch B
git merge feature/new-endpoints
# Auto-merging src/api/config.js
# CONFLICT (content): Merge conflict in src/api/config.js
# Automatic merge failed; fix conflicts and then commit the result.
```

### Step 3: Examine the Conflict

```bash
# See conflict status
git status
# On branch main
# You have unmerged paths.
#
# Unmerged paths:
#   both modified:   src/api/config.js

# View the conflicted file
cat src/api/config.js
```

```javascript
const API_CONFIG = {
<<<<<<< HEAD (current main - includes branch A changes)
    baseURL: "https://api.production.com",
    timeout: 10000,
    retries: 3,
=======
    baseURL: "https://api.example.com",
    timeout: 5000,
>>>>>>> feature/new-endpoints
    endpoints: {
        users: "/users",
        posts: "/posts",
<<<<<<< HEAD
=======
        comments: "/comments",
        likes: "/likes"
>>>>>>> feature/new-endpoints
    }
};
```

### Step 4: Analyze the Conflict

**What happened:**
1. **HEAD (ours)** = main branch with branch A merged
   - baseURL changed to production
   - timeout increased to 10000
   - retries added
2. **feature/new-endpoints (theirs)** = branch B
   - baseURL still example.com (old)
   - timeout still 5000 (old)
   - Added new endpoints

**Decision:**
- Keep branch A's config updates (production URL, higher timeout, retries)
- Add branch B's new endpoints

### Step 5: Resolve the Conflict

Edit `src/api/config.js`:

```javascript
// REMOVE conflict markers and combine changes
const API_CONFIG = {
    baseURL: "https://api.production.com",  // From branch A
    timeout: 10000,                         // From branch A
    retries: 3,                             // From branch A
    endpoints: {
        users: "/users",
        posts: "/posts",
        comments: "/comments",              // From branch B
        likes: "/likes"                     // From branch B
    }
};
```

### Step 6: Verify Resolution

```bash
# Check for remaining conflict markers
grep -n "<<<<<<< " src/api/config.js
grep -n "=======" src/api/config.js
grep -n ">>>>>>> " src/api/config.js
# (Should return nothing)

# Verify syntax is valid
node -c src/api/config.js
# (No output = valid syntax)

# Run linter
npm run lint src/api/config.js
```

### Step 7: Test the Resolution

```bash
# Run tests
npm test

# If tests pass, continue
# If tests fail, fix issues before committing
```

### Step 8: Complete the Merge

```bash
# Stage the resolved file
git add src/api/config.js

# Verify what's staged
git diff --staged

# Complete the merge
git commit -m "Merge feature/new-endpoints into main

Added new API endpoints (comments and likes).

Conflicts resolved in src/api/config.js:
- Kept production configuration from feature/update-config
  (production URL, 10s timeout, retry logic)
- Integrated new endpoints from feature/new-endpoints
  (comments and likes endpoints)
- Verified all tests pass
- Confirmed configuration works in staging environment

Resolves: #789"

# Push
git push origin main
```

## Alternative Resolution Scenarios

### Scenario A: Accept One Side Completely

```bash
# If branch A's changes are clearly correct
git checkout --ours src/api/config.js
git add src/api/config.js

# Or if branch B's changes are correct
git checkout --theirs src/api/config.js
git add src/api/config.js

# Then commit
git commit
```

### Scenario B: Use Mergetool

```bash
# Launch visual merge tool
git mergetool

# Configure VS Code as mergetool (one-time)
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd \
  'code --wait --merge $REMOTE $LOCAL $BASE $MERGED'

# Then
git mergetool
# VS Code opens with 4-pane view
# Make changes in bottom pane
# Save and close
```

### Scenario C: Complex Multi-section Conflict

```javascript
// More complex conflict with multiple sections
const API_CONFIG = {
<<<<<<< HEAD
    baseURL: "https://api.production.com",
    timeout: 10000,
||||||| merged common ancestor
    baseURL: "https://api.example.com",
    timeout: 5000,
=======
    baseURL: "https://api.staging.com",
    timeout: 7500,
>>>>>>> feature/staging-config

    endpoints: {
<<<<<<< HEAD
        users: "/v2/users",
        posts: "/v2/posts"
=======
        users: "/users",
        posts: "/posts",
        analytics: "/analytics"
>>>>>>> feature/staging-config
    }
};
```

**Resolution with diff3 style:**
- Original: api.example.com, timeout 5000
- HEAD: Changed to production.com, timeout 10000
- Theirs: Changed to staging.com, timeout 7500
- **Decision**: Production for production branch, keep both endpoint versions

```javascript
const API_CONFIG = {
    baseURL: "https://api.production.com",  // Production is correct
    timeout: 10000,                         // Higher timeout needed

    endpoints: {
        users: "/v2/users",                 // Keep v2 from HEAD
        posts: "/v2/posts",                 // Keep v2 from HEAD
        analytics: "/analytics"             // Add from theirs
    }
};
```

## Common Mistakes and Fixes

### Mistake 1: Forgot to Remove Conflict Markers

```bash
# Accidentally committed with markers
git commit -m "Merge feature branch"
git push origin main

# Discover the mistake
grep -r "<<<<<<< " .
# src/api/config.js:5:<<<<<<< HEAD

# Fix it
vim src/api/config.js  # Remove markers properly
git add src/api/config.js

# Amend commit (if not yet pushed)
git commit --amend --no-edit

# Or create fix commit (if already pushed)
git commit -m "fix: remove conflict markers from config"
git push origin main
```

### Mistake 2: Resolved Wrong Way

```bash
# Merged but kept wrong version
git log -1
# a1b2c3d Merge feature/new-endpoints

# Tests fail!
npm test
# FAIL: API endpoints not working

# Fix: Revert merge and redo
git revert -m 1 a1b2c3d
git push origin main

# Now merge again properly
git merge feature/new-endpoints
# Resolve correctly this time
```

### Mistake 3: Staged Wrong File

```bash
# Resolved conflict but staged different file by mistake
git add src/api/wrong-file.js

git status
# Changes to be committed:
#   modified:   src/api/wrong-file.js
# Unmerged paths:
#   both modified:   src/api/config.js

# Fix: Unstage wrong file, stage correct one
git reset HEAD src/api/wrong-file.js
git add src/api/config.js
git commit
```

## Best Practices for Text Conflicts

conflict_resolution_practices[8]{practice,explanation}:
Understand both changes,Read what each developer was trying to do
Preserve intent,Keep the intention of both changes if possible
Test thoroughly,Run all tests after resolution
Use diff3,Enable diff3 to see original version
Communicate,Ask developers if resolution unclear
Document decision,Explain resolution in commit message
Use tools,Visual merge tools help for complex conflicts
Verify syntax,Ensure code is syntactically correct

## Verification Checklist

After resolving text conflicts:

```bash
# ✓ No conflict markers remain
git diff --check

# ✓ File is syntactically valid
node -c src/api/config.js       # For JavaScript
python -m py_compile file.py    # For Python
cargo check                     # For Rust

# ✓ Linting passes
npm run lint

# ✓ Tests pass
npm test

# ✓ Manual testing done
# Test the actual functionality

# ✓ Commit message is descriptive
git log -1
```

## Key Takeaways

1. **Understand before resolving** - Know what each side changed and why
2. **Combine thoughtfully** - Don't just pick one side arbitrarily
3. **Test everything** - Ensure resolution actually works
4. **Document your reasoning** - Future developers will thank you
5. **When in doubt, ask** - Consult the developers who made the changes

## Next Steps

- [Example 3: Pre-merge Validation](pre-merge-checks.md) - Automated checks
- [Example 4: Binary File Conflicts](binary-conflicts.md) - Non-text files
- [docs/conflict-resolution.md](../docs/conflict-resolution.md) - Complete guide
