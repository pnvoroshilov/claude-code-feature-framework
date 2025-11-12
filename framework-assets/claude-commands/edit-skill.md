---
allowed-tools: [Read, Edit, Bash, Grep]
argument-hint: [skill-name] [edit-instructions]
description: Edit and improve existing skill based on instructions using Claude's intelligent code editing
---

# Edit Skill with Claude

I'll read the existing skill configuration, apply your requested changes, and save the improved version. I will use subagent `skills-creator`

## Workflow

### Step 1: Parse Arguments

**If arguments provided:**
- Argument 1: Skill name (e.g., "react-developing" or "React Development")
- Argument 2: Edit instructions (e.g., "add React 19 server components examples")

**If no arguments provided:**
Ask user for:
1. Skill name to edit
2. What changes/improvements they want

### Step 2: Locate Skill File

I'll search for the skill file in `.claude/skills/`:
- Convert skill name to kebab-case if needed
- Find matching file (e.g., `react-developing.md`)
- If not found, list available skills

### Step 3: Read Current Content

I'll read the complete skill file to understand:
- Current purpose and description
- When to use this skill
- Core capabilities and features
- Usage examples and patterns
- Best practices and guidelines
- Common pitfalls and warnings

### Step 4: Apply Intelligent Edits

Based on your instructions, I'll:

**For content additions:**
- Add new use cases or scenarios
- Include additional examples
- Expand capability descriptions
- Add relevant best practices
- Include new patterns or approaches

**For content modifications:**
- Update examples with better practices
- Improve clarity of instructions
- Modernize recommendations
- Fix incorrect information
- Enhance existing examples

**For content removal:**
- Remove outdated patterns
- Clean up redundant examples
- Eliminate deprecated approaches
- Simplify overly complex explanations

**For structural improvements:**
- Better organize sections
- Add subsections for clarity
- Improve headings and formatting
- Enhance readability

### Step 5: Preserve Quality

I'll ensure the edited skill maintains:
- ✅ Clear purpose statement
- ✅ Actionable guidance
- ✅ Practical examples
- ✅ Consistent formatting
- ✅ Professional quality
- ✅ Relevant and current information

### Step 6: Save and Report

I'll:
1. Save the updated skill file
2. Report what was changed
3. Provide a summary of improvements
4. Confirm the skill is ready to use

## Example Usage

**With arguments:**
```
/edit-skill "react-developing" "add examples for React Server Components and Suspense boundaries"
```

**Without arguments (interactive):**
```
/edit-skill
```
I'll ask you which skill to edit and what changes you want.

## Edit Instructions Examples

**Adding features:**
- "add examples for Next.js App Router"
- "include testing strategies with React Testing Library"
- "add accessibility best practices"

**Improving content:**
- "make examples more detailed"
- "add error handling patterns"
- "expand state management section"

**Updating technology:**
- "update to React 19 features"
- "add TypeScript 5 examples"
- "include Vite configuration tips"

**Fixing issues:**
- "remove deprecated lifecycle methods"
- "fix incorrect hook usage"
- "update outdated API patterns"

**Restructuring:**
- "reorganize by use case"
- "split complex examples"
- "add quick reference section"

## What I'll Change

Based on your instructions, I'll intelligently modify:

### Content Updates
- Add new examples and use cases
- Update existing patterns
- Remove outdated information
- Expand brief sections
- Add missing scenarios

### Code Examples
- Add new code snippets
- Update existing examples
- Fix code errors
- Improve code comments
- Add TypeScript types

### Best Practices
- Add new recommendations
- Update guidelines
- Remove deprecated advice
- Include modern patterns
- Add performance tips

### Structural Changes
- Reorganize sections
- Add subsections
- Improve headings
- Consolidate content
- Enhance navigation

## Timeline

Skill editing typically takes 1-3 minutes depending on the complexity of changes. You'll receive a report showing what was modified.

## After Editing

The updated skill will be immediately available with your improvements:

```
Use the skill as before - all improvements will be automatically applied when Claude invokes it.
```

## Skill vs Agent

**Skills** are specialized knowledge modules that provide:
- Domain-specific guidance
- Code patterns and examples
- Best practices
- Common pitfalls

**Agents** are autonomous workers that:
- Execute multi-step tasks
- Use tools to complete work
- Follow structured workflows
- Deliver concrete results

Edit skills when you want to improve guidance and examples.
Edit agents when you want to change task execution capabilities.

---

Let me locate the skill and apply your requested changes...
