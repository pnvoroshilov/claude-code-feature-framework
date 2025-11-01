---
name: git-workflow
description: Comprehensive guidance for advanced Git workflow management with branching strategies, pull requests, merge strategies, and team collaboration patterns
version: 1.0.0
tags: [git, version-control, workflow, branching, collaboration]
---

# Git Workflow - Advanced Version Control Management

## Overview

This skill provides comprehensive guidance for advanced Git workflow management, covering everything from basic commits to complex branching strategies, pull requests, merge strategies, and team collaboration patterns. Master professional Git workflows used in production environments.

## What You'll Master

This skill covers the complete Git workflow lifecycle:
- **Professional commit practices** with semantic versioning and conventional commits
- **Branch management strategies** including GitFlow, GitHub Flow, and trunk-based development
- **Pull request workflows** with proper review processes and CI/CD integration
- **Advanced merge strategies** including rebasing, squashing, and conflict resolution
- **Repository maintenance** with history rewriting, cleanup, and optimization
- **Team collaboration patterns** with proper code review and approval workflows
- **Release management** with tagging, versioning, and changelog generation
- **Git hooks and automation** for enforcing standards and quality gates
- **Troubleshooting complex scenarios** including recovery from mistakes
- **Integration with CI/CD pipelines** and development workflows

## Quick Start

### Basic Commit Workflow
```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add user authentication feature"

# Push to remote
git push origin feature/user-auth
```

### Feature Branch Workflow
```bash
# Create feature branch
git checkout -b feature/new-dashboard main

# Work on feature
git add src/dashboard/
git commit -m "feat(dashboard): implement new analytics widget"

# Push and create PR
git push -u origin feature/new-dashboard
gh pr create --title "Add analytics dashboard" --body "Implements new dashboard with real-time analytics"
```

### Pull Request Review
```bash
# Fetch PR for local review
gh pr checkout 123

# Review changes
git diff main..HEAD

# Test locally
npm test

# Approve or request changes
gh pr review --approve
# OR
gh pr review --request-changes --body "Please add unit tests"
```

## Core Capabilities

### 1. Commit Management
- **Semantic commits** following Conventional Commits specification
- **Atomic commits** with single logical changes
- **Descriptive messages** with proper formatting and context
- **Commit amendment** for fixing recent commits
- **Interactive staging** for partial file commits
- **Commit signing** with GPG for security
- **Co-authorship** for pair programming
- **Commit templates** for consistency

### 2. Branch Management
- **Branch naming conventions** (feature/, bugfix/, hotfix/, release/)
- **GitFlow workflow** for structured releases
- **GitHub Flow** for continuous deployment
- **Trunk-based development** for rapid iteration
- **Branch protection rules** and policies
- **Long-running branches** vs ephemeral branches
- **Branch cleanup** and pruning strategies
- **Remote branch tracking** and synchronization

### 3. Pull Request Workflows
- **PR creation** with templates and descriptions
- **Draft PRs** for work-in-progress
- **PR review process** with approval requirements
- **Code review best practices** and etiquette
- **Review comments** and suggestions
- **PR status checks** with CI/CD integration
- **Auto-merge** with approval requirements
- **PR linking** to issues and projects

### 4. Merge Strategies
- **Merge commits** for preserving history
- **Squash merging** for clean history
- **Rebase merging** for linear history
- **Fast-forward merging** when possible
- **Merge conflict resolution** strategies
- **Three-way merges** understanding
- **Octopus merges** for multiple branches
- **Strategy selection** based on context

### 5. Rebasing and History Rewriting
- **Interactive rebase** for cleaning history
- **Commit squashing** to combine commits
- **Commit reordering** for logical flow
- **Commit splitting** for better granularity
- **Fixup and autosquash** workflows
- **Rebase vs merge** decision making
- **Force push safely** with lease protection
- **History rewriting risks** and best practices

### 6. Release Management
- **Semantic versioning** (MAJOR.MINOR.PATCH)
- **Release branches** for stabilization
- **Tag creation** for versions
- **Annotated tags** with metadata
- **Changelog generation** from commits
- **Release notes** automation
- **Hotfix workflows** for production issues
- **Version bumping** strategies

### 7. Code Review Practices
- **Review checklist** for consistency
- **Inline comments** with suggestions
- **Approval workflows** with CODEOWNERS
- **Review assignments** and notifications
- **Review etiquette** and communication
- **Addressing feedback** efficiently
- **Re-review requests** after changes
- **Review automation** with bots

### 8. Git Hooks and Automation
- **Pre-commit hooks** for linting and formatting
- **Commit-msg hooks** for message validation
- **Pre-push hooks** for testing
- **Post-merge hooks** for cleanup
- **Husky integration** for Node.js projects
- **Hook sharing** across team
- **Hook bypass** when necessary
- **Custom hook scripts** for workflows

### 9. Repository Maintenance
- **Branch pruning** to remove stale branches
- **Large file management** with Git LFS
- **History cleanup** to reduce repository size
- **Reflog usage** for recovery
- **Garbage collection** optimization
- **Repository compression** techniques
- **Submodule management** best practices
- **Monorepo strategies** with Git

### 10. Team Collaboration
- **Collaborative workflows** with multiple developers
- **Fork and pull request** model
- **Shared repository** model
- **Protected branches** and permissions
- **Code ownership** with CODEOWNERS file
- **Conflict prevention** strategies
- **Synchronization practices** with remote
- **Communication protocols** around Git

## Documentation

### Core Concepts
**[docs/core-concepts.md](docs/core-concepts.md)** - Fundamental Git workflow concepts including:
- Distributed version control model
- Working directory, staging area, and repository
- Commits, trees, and blobs
- Branches and references
- Remote repositories and tracking
- The Git object model
- HEAD and detached HEAD states
- Merge base and common ancestors

### Best Practices
**[docs/best-practices.md](docs/best-practices.md)** - Industry-standard Git practices including:
- Commit message conventions
- Branch naming standards
- Pull request guidelines
- Code review principles
- Merge strategy selection
- History maintenance
- Security and signing
- Team collaboration protocols

### Common Patterns
**[docs/patterns.md](docs/patterns.md)** - Git workflow patterns including:
- GitFlow pattern for releases
- GitHub Flow for continuous deployment
- Trunk-based development
- Feature toggles workflow
- Hotfix workflow
- Release train model
- Fork and pull request pattern
- Anti-patterns to avoid

### Advanced Topics
**[docs/advanced-topics.md](docs/advanced-topics.md)** - Expert-level Git features including:
- Interactive rebase mastery
- Cherry-picking strategies
- Bisect for debugging
- Reflog for recovery
- Worktrees for parallel work
- Sparse checkout for large repos
- Shallow clones for speed
- Git internals and plumbing commands

### Troubleshooting
**[docs/troubleshooting.md](docs/troubleshooting.md)** - Solutions for common Git issues:
- Merge conflict resolution
- Recovering lost commits
- Undoing changes safely
- Fixing commit mistakes
- Resolving detached HEAD
- Cleaning up messy history
- Dealing with large files
- Fixing remote synchronization issues

### API Reference
**[docs/api-reference.md](docs/api-reference.md)** - Complete Git command reference:
- git commit - Create commits
- git branch - Manage branches
- git merge - Merge branches
- git rebase - Rebase branches
- git pull/push - Synchronize with remote
- git reset - Reset state
- git revert - Revert commits
- gh pr - GitHub PR commands

## Examples

### Basic Examples
Learn fundamental Git workflows:

- **[Example 1: Feature Branch Workflow](examples/basic/feature-branch-workflow.md)** - Complete feature development workflow from branch creation to merge
- **[Example 2: Conventional Commits](examples/basic/conventional-commits.md)** - Writing standardized commit messages for automated changelog generation
- **[Example 3: Pull Request Creation](examples/basic/pull-request-creation.md)** - Creating and managing pull requests with proper descriptions and links

### Intermediate Examples
Master common Git patterns:

- **[Pattern 1: Squash and Merge](examples/intermediate/squash-and-merge.md)** - Combining multiple commits into one for clean history
- **[Pattern 2: Rebase Workflow](examples/intermediate/rebase-workflow.md)** - Using rebase to maintain linear history and resolve conflicts
- **[Pattern 3: Hotfix Process](examples/intermediate/hotfix-process.md)** - Emergency bug fix workflow for production issues
- **[Pattern 4: Release Management](examples/intermediate/release-management.md)** - Creating releases with tags, versioning, and changelogs

### Advanced Examples
Expert-level Git workflows:

- **[Advanced 1: Interactive Rebase Mastery](examples/advanced/interactive-rebase.md)** - Advanced history rewriting with rebase for perfect commit history
- **[Advanced 2: Complex Merge Conflicts](examples/advanced/complex-merge-conflicts.md)** - Resolving multi-file merge conflicts with strategic approaches
- **[Advanced 3: Git Hooks Automation](examples/advanced/git-hooks-automation.md)** - Implementing pre-commit hooks with Husky for quality gates
- **[Advanced 4: Monorepo Workflow](examples/advanced/monorepo-workflow.md)** - Managing large monorepos with path-based workflows

## Templates

### Ready-to-Use Workflow Templates

- **[Template 1: Basic Feature Development](templates/basic-feature-template.md)** - Step-by-step template for standard feature development workflow
- **[Template 2: GitFlow Release Process](templates/gitflow-release-template.md)** - Complete GitFlow workflow with release and hotfix branches
- **[Template 3: Production Hotfix](templates/production-hotfix-template.md)** - Emergency production fix workflow with fast-track process
- **[Template 4: Code Review Workflow](templates/code-review-template.md)** - Comprehensive code review process with checklists

## Resources

### Additional Reference Materials

- **[Quality Checklists](resources/checklists.md)** - Pre-commit, pre-merge, and release checklists for quality assurance
- **[Git Glossary](resources/glossary.md)** - Complete terminology reference for Git concepts and commands
- **[External References](resources/references.md)** - Official documentation, tutorials, and community resources
- **[Workflow Diagrams](resources/workflows.md)** - Visual workflow diagrams and decision trees for common scenarios

## Usage in Claude Code

This skill is automatically loaded when working with Git operations in Claude Code. It enhances:

1. **Commit Message Generation** - Suggests properly formatted commit messages
2. **Branch Strategy Recommendations** - Advises on appropriate branching approaches
3. **Merge Strategy Selection** - Helps choose the right merge strategy
4. **Conflict Resolution Guidance** - Provides step-by-step conflict resolution help
5. **PR Review Assistance** - Guides through code review best practices
6. **Release Planning** - Assists with version management and releases

## Getting Started

1. **Start with SKILL.md** (this file) for a complete overview
2. **Read [docs/core-concepts.md](docs/core-concepts.md)** to understand Git fundamentals
3. **Review [docs/best-practices.md](docs/best-practices.md)** for professional standards
4. **Explore [examples/](examples/)** for practical, working code examples
5. **Use [templates/](templates/)** for quick-start workflows
6. **Reference [resources/](resources/)** for checklists and additional materials

## Integration with Development Workflow

### Daily Development Flow
```bash
# Morning: Update your branch
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main

# During development: Commit frequently
git add src/component.tsx
git commit -m "feat(component): add loading state"

# Before push: Clean up commits
git rebase -i HEAD~3  # Interactive rebase last 3 commits

# Push and create PR
git push -f origin feature/my-feature
gh pr create --web
```

### CI/CD Integration
- Automated testing on PR creation
- Status checks before merge
- Automated changelog generation
- Version bumping on merge to main
- Automated deployment on tag creation

## Common Workflows Covered

1. **Feature Development** - From branch creation to merged PR
2. **Bug Fixes** - Quick fixes with proper testing
3. **Hotfixes** - Emergency production fixes
4. **Releases** - Version management and deployment
5. **Code Reviews** - Professional review process
6. **Conflict Resolution** - Handling merge conflicts
7. **History Cleanup** - Maintaining clean commit history
8. **Repository Maintenance** - Keeping repos healthy

## Key Principles

### Clean History
Maintain a clear, readable Git history that tells the story of your project's evolution.

### Atomic Commits
Each commit should represent one logical change that can be easily understood and reverted if needed.

### Meaningful Messages
Commit messages should explain why a change was made, not just what was changed.

### Protected Main Branch
Never commit directly to main/master - always use feature branches and pull requests.

### Review Everything
All code should be reviewed by at least one other developer before merging.

### Test Before Merge
All tests must pass before merging to main branch.

## Advanced Features

### Git Worktrees
Work on multiple branches simultaneously without switching:
```bash
git worktree add ../project-feature feature/new-feature
cd ../project-feature
# Work on feature while main project stays on different branch
```

### Git Bisect
Binary search to find bug-introducing commit:
```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git checks out middle commit, you test and mark good/bad
```

### Git Hooks
Automate quality checks:
```bash
# .husky/pre-commit
npm run lint
npm run test
npm run type-check
```

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Merge conflicts | See [docs/troubleshooting.md](docs/troubleshooting.md#merge-conflicts) |
| Lost commits | Use `git reflog` - see [examples/advanced/recovery.md](docs/troubleshooting.md#lost-commits) |
| Wrong commit message | `git commit --amend` for last commit |
| Committed to wrong branch | `git cherry-pick` to move commits |
| Need to undo changes | `git reset` or `git revert` depending on context |
| Detached HEAD | `git checkout -b new-branch` to save work |

## Team Collaboration Best Practices

1. **Communicate Early** - Open draft PRs for feedback
2. **Small PRs** - Easier to review and merge
3. **Frequent Pulls** - Stay synchronized with team
4. **Clear Messages** - Help future developers understand
5. **Respectful Reviews** - Constructive feedback only
6. **Quick Reviews** - Don't block teammates
7. **Fix Forward** - Prefer new commits over force push
8. **Document Decisions** - Use PR descriptions for context

## Configuration Recommendations

### Global Git Config
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "code --wait"
git config --global pull.rebase true
git config --global fetch.prune true
git config --global rerere.enabled true
```

### Repository Config
```bash
git config branch.autoSetupRebase always
git config merge.conflictstyle diff3
git config push.default simple
git config push.followTags true
```

## Next Steps

After mastering this skill:
1. Implement Git workflows in your team
2. Customize templates for your organization
3. Set up automated hooks and CI/CD
4. Train team members on best practices
5. Establish code review culture
6. Document team-specific conventions
7. Continuously improve processes

## Skill Maintenance

This skill is regularly updated with:
- New Git features and commands
- Emerging workflow patterns
- Community best practices
- Tool integrations (GitHub CLI, GitLab, etc.)
- Real-world examples from production use

---

**Ready to master Git workflows?** Start with [docs/core-concepts.md](docs/core-concepts.md) to build a solid foundation, then explore the examples and templates to see these concepts in action.
