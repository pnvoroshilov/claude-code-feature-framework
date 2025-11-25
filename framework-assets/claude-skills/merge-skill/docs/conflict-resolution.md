# Conflict Resolution - Comprehensive Techniques

## Understanding Conflict Markers

When Git cannot automatically merge changes, it inserts special markers to show conflicting sections.

### Basic Conflict Structure

```javascript
<<<<<<< HEAD (current branch - ours)
const API_URL = "https://api.production.com";
const TIMEOUT = 3000;
=======
const API_URL = "https://api.staging.com";
const TIMEOUT = 5000;
>>>>>>> feature/api-update (incoming branch - theirs)
```

conflict_marker_types[3]{marker,meaning}:
<<<<<<< HEAD,Start of current branch version (yours)
=======,Divider between your changes and incoming changes
>>>>>>> branch-name,End of incoming branch version (theirs)

### diff3 Conflict Style (Recommended)

Enable diff3 to see the common ancestor:

```bash
git config --global merge.conflictstyle diff3
```

Now conflicts show three sections:

```javascript
<<<<<<< HEAD (ours)
const TIMEOUT = 3000;
||||||| merged common ancestor
const TIMEOUT = 5000;
=======
const TIMEOUT = 10000;
>>>>>>> feature/timeout-increase (theirs)
```

This reveals:
- **Original value**: 5000
- **Our change**: 5000 → 3000 (decreased)
- **Their change**: 5000 → 10000 (increased)
- **Resolution needed**: Decide which direction makes sense

## Manual Resolution Workflow

resolution_steps[8]{step,action,command}:
1. Identify conflicts,Check which files have conflicts,git status
2. Understand context,View the conflicting changes,git diff
3. Open file,Edit in your preferred editor,code <file> or vim <file>
4. Choose resolution,Keep one both or create new solution,Manual editing
5. Remove markers,Delete all <<<<<<< ======= >>>>>>> lines,Manual editing
6. Test changes,Verify code still works,Run tests
7. Stage file,Mark conflict as resolved,git add <file>
8. Complete merge,Commit the merge,git commit or git merge --continue

### Step-by-Step Example

```bash
# 1. Identify conflicts
git merge feature/new-api
# Auto-merging src/config.js
# CONFLICT (content): Merge conflict in src/config.js
# Automatic merge failed; fix conflicts and then commit the result.

# 2. View conflicted files
git status
# Unmerged paths:
#   both modified:   src/config.js

# 3. View conflict details
git diff src/config.js

# 4. Open and resolve
vim src/config.js
# Edit file, remove markers, keep desired changes

# 5. Verify resolution
cat src/config.js
# Ensure no <<<<<<< markers remain

# 6. Test
npm test

# 7. Stage resolved file
git add src/config.js

# 8. Complete merge
git commit -m "Merge feature/new-api: resolved config conflicts"
```

## Resolution Strategies by Scenario

### Strategy 1: Accept One Side Completely

**Use when**: One version is clearly correct

```bash
# Accept current branch (ours)
git checkout --ours src/config.js
git add src/config.js

# Accept incoming branch (theirs)
git checkout --theirs src/config.js
git add src/config.js
```

### Strategy 2: Combine Both Changes

**Use when**: Both changes are needed

```javascript
// BEFORE (conflict)
<<<<<<< HEAD
function authenticate(user) {
    return validatePassword(user.password);
}
=======
async function authenticate(user) {
    return await validateToken(user.token);
}
>>>>>>> feature/token-auth

// AFTER (combined)
async function authenticate(user) {
    // Support both password and token authentication
    if (user.token) {
        return await validateToken(user.token);
    }
    return validatePassword(user.password);
}
```

### Strategy 3: Write New Solution

**Use when**: Neither version is ideal, need new approach

```python
# BEFORE (conflict)
<<<<<<< HEAD
def process_data(data):
    return data.upper()
=======
def process_data(data):
    return data.lower()
>>>>>>> feature/lowercase

# AFTER (new solution)
def process_data(data, format_type='upper'):
    """Process data with configurable formatting"""
    if format_type == 'upper':
        return data.upper()
    elif format_type == 'lower':
        return data.lower()
    return data
```

### Strategy 4: Cherry-pick Changes

**Use when**: Want specific parts from each side

```css
/* BEFORE (conflict) */
<<<<<<< HEAD
.button {
    background-color: blue;
    padding: 10px;
    font-size: 14px;
}
=======
.button {
    background-color: #007bff;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
>>>>>>> feature/button-redesign

/* AFTER (cherry-picked best of both) */
.button {
    background-color: #007bff;  /* from theirs - better color */
    padding: 10px;              /* from ours - keep padding */
    font-size: 14px;            /* from ours - keep font size */
    border-radius: 4px;         /* from theirs - add radius */
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* from theirs - add shadow */
}
```

## Reading Complex Conflicts

### Multiple Conflict Blocks in One File

```javascript
// File: src/database.js

<<<<<<< HEAD
const DB_HOST = "localhost";
const DB_PORT = 5432;
=======
const DB_HOST = "db.example.com";
const DB_PORT = 3306;
>>>>>>> feature/mysql

// Auto-merged section (no conflict)
const DB_NAME = "production";
const DB_USER = "admin";

<<<<<<< HEAD
const CONNECTION_POOL = 10;
=======
const CONNECTION_POOL = 20;
const CONNECTION_TIMEOUT = 5000;
>>>>>>> feature/mysql
```

**Resolution approach**:
1. Resolve each conflict block independently
2. Consider context from auto-merged sections
3. Ensure consistency across all resolutions
4. Test entire file after resolution

### Conflicts with Multiple Files

```bash
# Systematic approach to multiple file conflicts
git status --short
# UU src/api/auth.js
# UU src/api/users.js
# UU src/config/database.js

# Resolve one file at a time
# 1. Start with core dependencies (database.js)
vim src/config/database.js
# resolve, test, stage

# 2. Then dependent files (auth.js, users.js)
vim src/api/auth.js
# resolve, test, stage

vim src/api/users.js
# resolve, test, stage

# 3. Run full test suite
npm test

# 4. Commit all resolutions together
git commit -m "Merge feature/mysql: migrate to MySQL

Conflicts resolved:
- database.js: Updated connection config for MySQL
- auth.js: Modified authentication queries for MySQL syntax
- users.js: Updated user management queries

All tests passing."
```

## Using Git Mergetool

Visual merge tools make conflict resolution easier:

### Configuring Mergetool

```bash
# VS Code
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait --merge $REMOTE $LOCAL $BASE $MERGED'

# Vim (built-in)
git config --global merge.tool vimdiff

# Meld (Linux)
git config --global merge.tool meld

# Beyond Compare
git config --global merge.tool bc
git config --global mergetool.bc.path "/usr/bin/bcompare"

# P4Merge (free from Perforce)
git config --global merge.tool p4merge
git config --global mergetool.p4merge.path "/Applications/p4merge.app/Contents/MacOS/p4merge"
```

### Using Mergetool

```bash
# During a conflict, launch mergetool
git mergetool

# This opens each conflicted file one by one
# Resolve in visual interface
# Save and close each file

# Git automatically stages resolved files
# Complete the merge
git commit
```

### Mergetool Layout

Most merge tools show 4-way view:

```
+-------------------+-------------------+
|      LOCAL        |      REMOTE       |
|   (your changes)  | (incoming changes)|
+-------------------+-------------------+
|               BASE                    |
|        (common ancestor)              |
+---------------------------------------+
|              MERGED                   |
|        (resolution result)            |
+---------------------------------------+
```

## Verification After Resolution

verification_checklist[6]{check,command}:
No conflict markers remain,grep -r "<<<<<<< " . (should be empty)
File syntax is valid,Run linter: eslint . or pylint .
Code still compiles,npm run build or cargo build
Tests pass,npm test or pytest or cargo test
No unintended changes,git diff --staged (review carefully)
All conflicts resolved,git status (no "Unmerged" files)

### Verification Commands

```bash
# Check for remaining conflict markers
grep -rn "<<<<<<< " .
grep -rn "=======" .
grep -rn ">>>>>>> " .

# Better: check all at once
git diff --check

# Verify file is staged
git status

# Review what you're about to commit
git diff --staged

# Run tests
npm test  # or appropriate test command

# If all good, commit
git commit
```

## Common Mistakes and Fixes

common_resolution_mistakes[6]{mistake,consequence,fix}:
Forgot to remove markers,Conflict markers in committed code,grep -r "<<<<<<< " . then fix
Staged wrong version,Committed incorrect resolution,git reset HEAD <file> then re-resolve
Didn't test after resolve,Broken code merged to main,git revert <merge-commit> then fix properly
Mixed up ours vs theirs,Wrong version chosen,git checkout <file> git merge --abort then retry
Incomplete resolution,File doesn't work,git checkout MERGE_HEAD -- <file> to restart
Committed with conflicts,Conflict markers in history,git reset --soft HEAD~1 fix then recommit

### Fixing Committed Conflict Markers

```bash
# Discovered conflict markers in committed code
grep -rn "<<<<<<< " .
# src/config.js:42:<<<<<<< HEAD

# Fix it
vim src/config.js  # Remove markers, resolve properly

# Amend the commit (if not pushed)
git add src/config.js
git commit --amend --no-edit

# Or create new commit (if already pushed)
git add src/config.js
git commit -m "fix: remove conflict markers from config.js"
```

## Advanced Conflict Resolution

### Using Patience Algorithm

Git's default merge algorithm can be improved:

```bash
# Use patience diff algorithm (better for large conflicts)
git merge -X patience feature/refactor

# Or set as default
git config --global merge.algorithm patience
```

### Resolving with grep and sed

For repetitive conflicts across many files:

```bash
# Find all files with specific conflict pattern
git grep -l "<<<<<<< HEAD"

# Example: Always keep "theirs" for specific file type
for file in $(git diff --name-only --diff-filter=U | grep '\.json$'); do
    git checkout --theirs "$file"
    git add "$file"
done
```

### Conflict Resolution Hooks

Automate verification with pre-commit hook:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for conflict markers
if git diff --cached | grep -E "^(\+|-)<<<<<<< |^(\+|-)=======$|^(\+|-)>>>>>>> "; then
    echo "Error: Conflict markers detected in staged files"
    exit 1
fi

# Check for debug statements
if git diff --cached | grep -E "console\.log|debugger|pdb\.set_trace"; then
    echo "Warning: Debug statements found"
    echo "Continue anyway? (y/n)"
    read answer
    if [ "$answer" != "y" ]; then
        exit 1
    fi
fi

exit 0
```

## Interactive Conflict Resolution

### Using git add --patch

Stage only parts of conflicted file:

```bash
# After resolving conflicts, stage interactively
git add --patch src/config.js

# Review each hunk
# y = yes, stage this hunk
# n = no, don't stage
# s = split hunk into smaller pieces
# e = manually edit hunk
```

### Using git checkout --patch

Cherry-pick conflict resolution from one side:

```bash
# Apply some changes from theirs, interactively
git checkout --patch --theirs src/config.js

# Select which hunks to accept from their version
```

## Tips for Preventing Conflicts

prevention_strategies[8]{strategy,explanation}:
Frequent merges,Merge main into feature daily to stay current
Small changes,Smaller PRs = fewer conflicts
Communicate,Tell team about large refactors
Feature flags,Hide incomplete features avoid blocking others
Code ownership,Coordinate on shared files
Linting consistency,Same formatting rules prevent style conflicts
Automated formatting,Use prettier/black to normalize formatting
Lock file commits,Commit lock files separately easier to resolve

## Summary

Conflict resolution is a skill that improves with practice:
1. **Understand** what each side changed and why
2. **Decide** which approach is correct (or combine both)
3. **Verify** resolution works correctly
4. **Test** before committing
5. **Document** complex resolutions in commit message

When in doubt, abort and ask for help: `git merge --abort`
