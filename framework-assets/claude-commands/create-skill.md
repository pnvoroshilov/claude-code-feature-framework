---
allowed-tools: [Task, Read, Write, Bash, Glob]
argument-hint: [skill-name] [skill-description]
description: Create comprehensive multi-file Claude Code skill package with exhaustive documentation, examples, and templates
---

# Create Comprehensive Claude Code Skill Package

I'll create a **comprehensive, multi-file skill package** with exhaustive documentation, abundant examples, templates, and reference materials - following the react-developing skill structure.

## Core Philosophy

**CRITICAL**: Every skill will be a complete knowledge package with:
- ✅ **Multi-file structure** - 20-30+ files organized in folders
- ✅ **Exhaustive documentation** - 2,000-5,000+ lines total
- ✅ **Abundant examples** - 9+ examples at different complexity levels
- ✅ **Ready-to-use templates** - 3+ complete templates
- ✅ **Comprehensive resources** - Checklists, glossary, workflows
- ❌ **NEVER single-file skills** - always full packages

## Mandatory Directory Structure

Every skill will include:

```
skill-name/
├── SKILL.md                    # Main entry (200-500 lines)
├── docs/                       # 6+ files (100-300 lines each)
│   ├── core-concepts.md
│   ├── best-practices.md
│   ├── patterns.md
│   ├── advanced-topics.md
│   ├── troubleshooting.md
│   └── api-reference.md
├── examples/                   # 9+ examples
│   ├── basic/                  # 3+ examples
│   ├── intermediate/           # 3+ examples
│   └── advanced/               # 3+ examples
├── templates/                  # 3+ templates
├── resources/                  # 4+ files
│   ├── checklists.md
│   ├── glossary.md
│   ├── references.md
│   └── workflows.md
└── scripts/                    # Optional utility scripts
```

## Workflow

### Step 1: Gather Skill Requirements

**Required Information:**
- **Skill Name**: Descriptive name (e.g., "Python FastAPI Development")
- **Skill Description**: What it covers and when to use
- **Domain/Technology**: What technology/domain this skill addresses

**If arguments provided**: Use them directly
**If no arguments**: Ask user for the information

### Step 2: Delegate to Skills Creator Agent

**IMPORTANT**: Provide EXTREMELY detailed instructions to the skills-creator agent:

```
Task tool with skills-creator:
"Create a COMPREHENSIVE, MULTI-FILE Claude Code skill package for: [SKILL NAME]

Description: [SKILL DESCRIPTION]

🔴 CRITICAL REQUIREMENTS:

1. **DIRECTORY STRUCTURE** (MANDATORY):
   Create the following structure in .claude/skills/[skill-name-kebab-case]/:
   ```
   skill-name/
   ├── SKILL.md (200-500 lines)
   ├── docs/
   │   ├── core-concepts.md (100-300 lines)
   │   ├── best-practices.md (100-300 lines)
   │   ├── patterns.md (100-300 lines)
   │   ├── advanced-topics.md (100-300 lines)
   │   ├── troubleshooting.md (100-300 lines)
   │   └── api-reference.md (100-300 lines)
   ├── examples/
   │   ├── basic/
   │   │   ├── example-1.md
   │   │   ├── example-2.md
   │   │   └── example-3.md
   │   ├── intermediate/
   │   │   ├── pattern-1.md
   │   │   ├── pattern-2.md
   │   │   └── pattern-3.md
   │   └── advanced/
   │       ├── advanced-pattern-1.md
   │       ├── advanced-pattern-2.md
   │       └── advanced-pattern-3.md
   ├── templates/
   │   ├── template-1.md
   │   ├── template-2.md
   │   └── template-3.md
   └── resources/
       ├── checklists.md
       ├── glossary.md
       ├── references.md
       └── workflows.md
   ```

2. **CONTENT REQUIREMENTS**:

   **SKILL.md** (200-500 lines):
   - Comprehensive overview
   - 10-20+ capabilities listed
   - Quick start guide
   - 5-10 usage examples
   - Navigation links to ALL docs/examples
   - Progressive disclosure structure

   **Each docs/ file** (100-300 lines):
   - Table of contents
   - 10+ major topics/concepts
   - 3-5 code examples per topic
   - Best practices and anti-patterns
   - Cross-references to other files

   **Each example** (100-200 lines with explanations):
   - Problem statement (50+ words)
   - Complete working code (50-150 lines)
   - Line-by-line explanation
   - 2-3 variations
   - Common pitfalls
   - Testing approach

   **Each template** (100-150 lines):
   - Complete working template
   - Heavily commented
   - Usage instructions
   - Customization points

   **Each resource file** (50-200 lines):
   - checklists.md: Quality checklists
   - glossary.md: Complete terminology
   - references.md: External resources
   - workflows.md: Step-by-step procedures

3. **QUALITY STANDARDS**:
   - Total package: 2,000-5,000+ lines minimum
   - Code examples for EVERY concept
   - Multiple approaches for each pattern
   - Real-world use cases explained
   - Troubleshooting with solutions
   - Consistent terminology throughout

4. **DELIVERY**:
   - Create ALL files using Write tool
   - Provide complete file contents
   - Validate all cross-references work
   - Confirm directory structure created

🎯 **GOAL**: Create a production-ready, exhaustively detailed skill package that leaves NOTHING to assumptions. Think react-developing skill level of detail."
```

### Step 3: Monitor Creation Progress

During creation, the agent will:
1. Create directory structure using Bash (mkdir -p)
2. Write all files using Write tool
3. Verify cross-references
4. Report completion with file counts

### Step 4: Validate and Report

After skills-creator completes:
1. **Verify directory structure** using `ls -R .claude/skills/[skill-name]/`
2. **Count files created** using `find .claude/skills/[skill-name] -type f | wc -l`
3. **Count total lines** using `find .claude/skills/[skill-name] -name "*.md" -exec wc -l {} + | tail -1`
4. **List all files** to confirm completeness

### Step 5: Provide Usage Instructions

Report to user:
```
✅ Comprehensive skill package created successfully!

📦 **Skill**: [Skill Name]
📁 **Location**: .claude/skills/[skill-name-kebab-case]/
📊 **Statistics**:
   - Total files: [COUNT]
   - Total lines: [COUNT]
   - Documentation files: [COUNT]
   - Examples: [COUNT]
   - Templates: [COUNT]

📂 **Structure**:
   ├── SKILL.md ([LINES] lines)
   ├── docs/ ([COUNT] files, [LINES] lines total)
   ├── examples/ ([COUNT] examples)
   ├── templates/ ([COUNT] templates)
   └── resources/ ([COUNT] resource files)

🎯 **How to Use**:
   - Skill is automatically available (no restart needed)
   - Start with SKILL.md for overview
   - Explore docs/ for deep understanding
   - Use examples/ for code patterns
   - Use templates/ for quick starts

📖 **Main Entry**: Open .claude/skills/[skill-name]/SKILL.md
```

## Key Principles

### 1. ALWAYS Multi-File Structure
❌ **NEVER** create single-file skills
✅ **ALWAYS** create comprehensive packages with 20-30+ files

### 2. Exhaustive Documentation
- Each topic covered in extreme detail
- Multiple examples for every concept
- All edge cases documented
- Complete troubleshooting guide

### 3. Progressive Disclosure
- SKILL.md = navigation hub
- docs/ = detailed documentation
- examples/ = working code
- templates/ = ready-to-use starters
- resources/ = supplementary materials

### 4. Quality Over Speed
- Better to take time and create comprehensive content
- 2,000-5,000+ lines total is the target
- Every file should be substantial

## Example Usage

### Example 1: With Arguments
```
User: /create-skill "Database Migration" "Comprehensive guide for database migrations with Alembic and SQLAlchemy"

Agent:
1. Parse arguments
2. Delegate to skills-creator with full requirements
3. Monitor creation of 25+ files
4. Verify structure and content
5. Report completion with statistics
```

### Example 2: Interactive Mode
```
User: /create-skill

Agent: What is the name of the skill you want to create?
User: API Testing
Agent: What domain/technology should this skill cover?
User: Python pytest for API testing with FastAPI
Agent: Creating comprehensive skill package...
[Creates 25+ files with 3,000+ lines of content]
```

## Success Criteria

A skill is successfully created when:
- ✅ Directory structure matches template (all folders created)
- ✅ Minimum 20 files created
- ✅ SKILL.md is 200+ lines
- ✅ All 6 docs/ files created (600-1,800 lines total)
- ✅ All 9 examples created (900-1,800 lines total)
- ✅ All 3 templates created (300-500 lines total)
- ✅ All 4 resource files created (200-800 lines total)
- ✅ Total package is 2,000-5,000+ lines
- ✅ All cross-references work
- ✅ Skill is immediately usable

## Anti-Patterns to Avoid

❌ Creating single SKILL.md file
❌ Brief/minimal documentation
❌ Missing examples or templates
❌ No directory structure
❌ Skills under 2,000 lines
❌ Assuming Claude knows details
❌ Skipping resources or docs

✅ Always create full multi-file packages
✅ Exhaustive detail in every file
✅ Abundant examples at all levels
✅ Complete templates ready to use
✅ Comprehensive resources
✅ 2,000-5,000+ lines total

## Troubleshooting

**Issue**: Skill seems incomplete
**Solution**: Check line counts. If under 2,000 total, ask agent to expand

**Issue**: Missing directories
**Solution**: Verify agent created full structure with mkdir -p

**Issue**: Broken cross-references
**Solution**: Ask agent to validate and fix all links

**Issue**: Examples too brief
**Solution**: Each example should be 100-200 lines with full explanations

Let me start by gathering skill requirements...
