---
allowed-tools: [Task, AskUserQuestion]
argument-hint: [skill-name] [skill-description]
description: Create comprehensive multi-file Claude Code skill package with exhaustive documentation, examples, and templates
---

# Create Comprehensive Claude Code Skill Package

I'll create a comprehensive, multi-file skill package by delegating to the skills-creator specialist agent.

## Workflow

### Step 1: Gather Skill Requirements

**If arguments provided:**
- Argument 1: Skill name (e.g., "Python FastAPI Development")
- Argument 2: Skill description (e.g., "Comprehensive guide for building FastAPI applications")

**If no arguments provided:**
Ask user for:
1. Skill name
2. Brief description of what the skill should cover
3. Target domain/technology (optional)

### Step 2: Delegate to Skills Creator Agent

Once I have the skill information, I'll immediately delegate to the `skills-creator` agent with complete requirements:

```
Task tool with subagent_type=skills-creator:
"Create a COMPREHENSIVE, MULTI-FILE Claude Code skill package.

🎯 **SKILL DETAILS**:
- **Name**: [SKILL NAME]
- **Description**: [SKILL DESCRIPTION]
- **Domain**: [TECHNOLOGY/DOMAIN]

🔴 **YOUR TASK**:
Follow your complete autonomous creation workflow to build a production-ready skill package with:
- 20-30+ files organized in proper directory structure
- 2,000-5,000+ lines of comprehensive content
- SKILL.md + 6 docs/ files + 9+ examples + 3+ templates + 4+ resources
- All cross-references validated
- Complete working code examples
- Ready-to-use templates

Target location: .claude/skills/[skill-name-kebab-case]/

Follow ALL phases of your creation workflow and provide a completion report with statistics when done."
```

### Step 3: Monitor and Report

The skills-creator agent will:
1. Create complete directory structure
2. Write all 20-30+ files
3. Validate cross-references
4. Verify quality standards
5. Report completion with statistics

I'll relay the completion report to you when the agent finishes.

## What to Expect

The skills-creator agent will create:
- **Complete multi-file structure** with 20-30+ files
- **2,000-5,000+ lines** of exhaustive documentation
- **SKILL.md** as navigation hub (200-500 lines)
- **6+ docs/ files** with detailed documentation (600-1,800 lines)
- **9+ examples** at basic, intermediate, and advanced levels (900-1,800 lines)
- **3+ templates** ready to use (300-500 lines)
- **4+ resource files** with checklists, glossary, references, workflows (200-800 lines)

## Example Usage

**With arguments:**
```
/create-skill "Database Migration" "Comprehensive guide for database migrations with Alembic and SQLAlchemy"
```

**Without arguments (interactive):**
```
/create-skill
```
I'll ask you for the skill name and description, then delegate to the agent.

## Timeline

Skill creation typically takes 45-60 minutes for the agent to complete a comprehensive package. You'll receive a detailed completion report with file counts and statistics when done.

---

Let me gather the skill requirements and delegate to the skills-creator agent...
