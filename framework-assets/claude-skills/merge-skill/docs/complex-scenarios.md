# Complex Merge Scenarios - Advanced Resolution

## Scenario 1: Renamed/Moved Files with Conflicts

### The Problem

Git tracks file renames, but conflicts can occur when:
- File renamed in one branch, modified in another
- File moved to different directory in one branch, edited in another
- File renamed differently in both branches

### Detection

```bash
git status
# On branch main
# You have unmerged paths.
#
# Unmerged paths:
#   both modified:   src/auth/login.js
#   renamed:         src/auth/login.js -> src/authentication/user-login.js
```

### Resolution Strategy

```bash
# Git usually auto-merges into the renamed file
# Check if rename was detected
git log --follow --oneline src/authentication/user-login.js

# If conflicts in renamed file
vim src/authentication/user-login.js
# Resolve conflicts normally

# Ensure old file is removed
git rm src/auth/login.js  # if it still exists

# Stage the resolution
git add src/authentication/user-login.js
git commit
```

### Example: Both Branches Renamed Same File Differently

```bash
# Branch A: login.js -> user-auth.js
# Branch B: login.js -> authentication.js

git status
# both added:      src/user-auth.js
# both added:      src/authentication.js
# both deleted:    src/login.js

# Resolution: Choose one name, merge content
cat src/user-auth.js src/authentication.js > src/user-auth.js.combined
vim src/user-auth.js.combined  # Merge content manually

# Keep one naming convention
mv src/user-auth.js.combined src/user-auth.js
git rm src/authentication.js
git add src/user-auth.js
git commit -m "Merge: resolve rename conflict, use user-auth.js"
```

## Scenario 2: Deleted vs Modified Conflicts

### The Problem

conflict_types[3]{type,description}:
Deleted by us,Current branch deleted file that incoming branch modified
Deleted by them,Incoming branch deleted file that we modified
Both deleted,Both deleted but with different content changes

### Detection

```bash
git status
# deleted by us:   src/legacy-api.js
# deleted by them: src/config/old-settings.js
```

### Resolution Decision Tree

```
FILE DELETED vs MODIFIED:
│
├─> Was deletion intentional (deprecated/obsolete)?
│   └─> YES: Keep deletion (git rm <file>)
│   └─> NO: Continue
│
├─> Are modifications important?
│   └─> YES: Restore file with modifications (git add <file>)
│   └─> NO: Keep deletion
│
└─> Can modifications be migrated elsewhere?
    └─> YES: Delete file, apply changes to new location
    └─> NO: Restore file
```

### Examples

**Case 1: Keep deletion (file was deprecated)**

```bash
git status
# deleted by us:   src/legacy-module.js

# File was intentionally removed - keep deletion
git rm src/legacy-module.js
git commit -m "Merge: confirm removal of deprecated legacy-module"
```

**Case 2: Restore modifications (deletion was mistake)**

```bash
git status
# deleted by them: src/important-utils.js

# We need this file and its modifications
git checkout HEAD -- src/important-utils.js
git add src/important-utils.js
git commit -m "Merge: restore important-utils.js with modifications"
```

**Case 3: Migrate changes to new location**

```bash
# File deleted because functionality moved elsewhere
git show HEAD:src/legacy-api.js > /tmp/old-api.js

# Extract useful changes
vim /tmp/old-api.js  # Copy relevant changes

# Apply to new file
vim src/api/modern-endpoints.js  # Paste changes here

# Confirm deletion of old file
git rm src/legacy-api.js
git add src/api/modern-endpoints.js
git commit -m "Merge: migrate legacy API functionality to new endpoints"
```

## Scenario 3: Binary File Conflicts

### The Problem

Git cannot merge binary files (images, PDFs, compiled assets, etc.)

### Detection

```bash
git status
# both modified:   assets/logo.png
# both modified:   docs/manual.pdf
# both modified:   static/compiled.wasm
```

### Resolution Strategies

binary_resolution_strategies[4]{strategy,use_case,command}:
Accept ours,Keep current branch version,git checkout --ours <file>
Accept theirs,Take incoming branch version,git checkout --theirs <file>
Keep both,Rename and preserve both versions,Manual renaming
Manual merge,Combine using external tool,Use image/PDF editor

### Examples

**Strategy 1: Choose one version**

```bash
# Keep our version
git checkout --ours assets/logo.png
git add assets/logo.png

# Or keep their version
git checkout --theirs assets/logo.png
git add assets/logo.png
```

**Strategy 2: Keep both versions**

```bash
# Rename and keep both
git checkout --ours assets/logo.png
mv assets/logo.png assets/logo-v1.png

git checkout --theirs assets/logo.png
mv assets/logo.png assets/logo-v2.png

# Stage both
git add assets/logo-v1.png assets/logo-v2.png
git commit -m "Merge: keep both logo versions for review"
```

**Strategy 3: Manual merge for images**

```bash
# Export both versions
git show :2:assets/banner.png > banner-ours.png
git show :3:assets/banner.png > banner-theirs.png

# Open in image editor (GIMP, Photoshop, etc.)
gimp banner-ours.png banner-theirs.png

# Manually combine elements
# Save result as assets/banner.png

git add assets/banner.png
git commit -m "Merge: manually combined banner designs"
```

## Scenario 4: Package Lock File Conflicts

### The Problem

Lock files (`package-lock.json`, `Cargo.lock`, `poetry.lock`) frequently conflict because they're auto-generated and contain exact dependency versions.

### Why Lock Files Conflict

```
Branch A: Added dependency "axios@1.5.0"
Branch B: Added dependency "lodash@4.17.21"

Both modified package-lock.json in different ways
Git cannot auto-merge because structure is complex
```

### Resolution Strategy

lock_file_resolution[5]{file_type,resolution_approach}:
package-lock.json,Regenerate with npm install
yarn.lock,Regenerate with yarn install
Cargo.lock,Regenerate with cargo update
poetry.lock,Regenerate with poetry lock --no-update
Pipfile.lock,Regenerate with pipenv lock

### Examples

**npm package-lock.json**

```bash
git status
# both modified:   package-lock.json

# Strategy 1: Merge package.json first, regenerate lock
git checkout --theirs package.json  # or merge manually
rm package-lock.json
npm install  # Regenerates lock file with both dependencies
git add package-lock.json package.json
```

**Cargo.lock**

```bash
git status
# both modified:   Cargo.lock

# Merge Cargo.toml first
git checkout --theirs Cargo.toml  # or merge manually

# Regenerate lock
rm Cargo.lock
cargo update  # or cargo build
git add Cargo.lock Cargo.toml
```

**poetry.lock**

```bash
git status
# both modified:   poetry.lock

# Merge pyproject.toml first
vim pyproject.toml  # Resolve conflicts

# Regenerate lock without updating dependencies
rm poetry.lock
poetry lock --no-update
git add poetry.lock pyproject.toml
```

## Scenario 5: Large-scale Refactoring Conflicts

### The Problem

Major code restructuring in one branch conflicts with feature development in another:
- Files moved to new directory structure
- Code split into multiple modules
- Namespaces/imports changed

### Example Scenario

```
Branch A (refactor):
- Moved src/utils/ → src/common/utils/
- Split monolithic file into modules
- Changed import paths

Branch B (feature):
- Modified files in src/utils/
- Added new functions to utils
```

### Resolution Strategy

refactoring_resolution_steps[6]{step,action}:
1. Accept structure,Choose refactored structure as base
2. Identify changes,Extract feature changes from old structure
3. Apply to new location,Manually apply changes to refactored files
4. Update imports,Fix all import statements
5. Run tests,Verify everything works
6. Clean up,Remove old file locations

### Step-by-Step Resolution

```bash
# 1. Accept refactored structure
git checkout --theirs src/

# 2. Extract feature changes
git show feature-branch:src/utils/helpers.js > /tmp/feature-helpers.js

# 3. Manually merge into new structure
# Compare old and new
diff /tmp/feature-helpers.js src/common/utils/helpers.js

# Apply feature additions
vim src/common/utils/helpers.js
# Copy new functions from /tmp/feature-helpers.js

# 4. Update imports across codebase
# Find all old imports
grep -r "from 'src/utils/helpers'" .

# Update to new path
sed -i "s|src/utils/helpers|src/common/utils/helpers|g" src/**/*.js

# 5. Test
npm test

# 6. Commit
git add .
git commit -m "Merge: apply feature changes to refactored structure

- Migrated new helper functions to src/common/utils/
- Updated all import paths
- All tests passing"
```

### Using Git Rerere for Refactoring

```bash
# Enable rerere (reuse recorded resolution)
git config --global rerere.enabled true

# First time resolving refactoring conflict
# Manually resolve as shown above
git commit

# Next time similar conflict occurs (e.g., during rebase)
git rebase main
# Git automatically applies your previous resolution!
```

## Scenario 6: Submodule Conflicts

### The Problem

```bash
git status
# both modified:   vendor/library (submodule)
```

Different commits checked out in submodule.

### Resolution

```bash
# See submodule status
git diff vendor/library

# Option 1: Accept their version
cd vendor/library
git checkout <their-commit-hash>
cd ../..
git add vendor/library

# Option 2: Update to latest
cd vendor/library
git pull origin main
cd ../..
git add vendor/library

# Option 3: Keep our version
git add vendor/library  # No changes, keeps our commit
```

## Scenario 7: Conflicting Configuration Files

### The Problem

Environment-specific configs conflict (`.env`, `config.yml`, etc.)

### Resolution Strategy

```bash
# Example: .env file conflict
<<<<<<< HEAD
API_URL=https://api.production.com
DEBUG=false
=======
API_URL=https://api.staging.com
DEBUG=true
>>>>>>> feature/testing

# Resolution: Use environment variables for differences
# Create .env.example with placeholders
API_URL=${API_URL:-https://api.production.com}
DEBUG=${DEBUG:-false}

# Document in README which env vars are needed
```

## Advanced: Handling Merge Conflicts in Multiple Commits

### Scenario: Rebase with Many Conflicts

```bash
git rebase main
# Conflict in commit 1 of 10

# Resolve first conflict
vim conflicted-file.js
git add conflicted-file.js
git rebase --continue

# Conflict in commit 2 of 10
# ... resolve ...
git rebase --continue

# If too many conflicts, abort and use merge instead
git rebase --abort
git merge main
```

## Tools for Complex Conflicts

useful_merge_tools[6]{tool,best_for}:
meld,Side-by-side GUI diff
vimdiff,Terminal-based three-way merge
Beyond Compare,Commercial powerful comparison
P4Merge,Free visual merge tool
KDiff3,Cross-platform three-way merge
VS Code,Built-in merge editor

### Example: Using Meld

```bash
git config --global merge.tool meld
git mergetool

# Meld opens showing:
# - Your version (left)
# - Merged result (center)
# - Their version (right)

# Click sections to choose which version
# Edit center pane for final result
# Save and close
```

## Summary

Complex scenarios require:
1. **Understanding** - Know what each branch changed
2. **Strategy** - Choose appropriate resolution approach
3. **Testing** - Verify resolution works
4. **Documentation** - Explain complex resolutions in commit message

When conflicts are too complex, consider:
- Breaking up the merge into smaller steps
- Coordinating with other developers
- Using `git merge --abort` and rethinking the approach
