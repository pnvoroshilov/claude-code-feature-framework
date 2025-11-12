---
allowed-tools: [Read, Edit, Bash, Grep]
argument-hint: [agent-name] [edit-instructions]
description: Edit and improve existing agent based on instructions using Claude's intelligent code editing
---

# Edit Agent with Claude

I'll read the existing agent configuration, apply your requested changes, and save the improved version. I will use subagent `agent-creator`

## Workflow

### Step 1: Parse Arguments

**If arguments provided:**
- Argument 1: Agent name (e.g., "frontend-developer" or "Frontend Developer")
- Argument 2: Edit instructions (e.g., "add TypeScript strict mode recommendations")

**If no arguments provided:**
Ask user for:
1. Agent name to edit
2. What changes/improvements they want

### Step 2: Locate Agent File

I'll search for the agent file in `.claude/agents/`:
- Convert agent name to kebab-case if needed
- Find matching file (e.g., `frontend-developer.md`)
- If not found, list available agents

### Step 3: Read Current Content

I'll read the complete agent file to understand:
- Current YAML frontmatter (name, description, tools)
- Role and expertise section
- Core capabilities
- Workflow and responsibilities
- Best practices and guidelines

### Step 4: Apply Intelligent Edits

Based on your instructions, I'll:

**For content additions:**
- Add new capabilities to the appropriate section
- Integrate new workflow steps logically
- Add relevant best practices or examples
- Maintain consistent formatting and tone

**For content modifications:**
- Update specific sections based on instructions
- Improve clarity or expand explanations
- Modernize recommendations
- Fix any issues or inconsistencies

**For content removal:**
- Remove outdated or irrelevant sections
- Consolidate redundant information
- Streamline verbose explanations

**For tool changes:**
- Update YAML frontmatter tools list
- Add tool usage guidelines in content
- Remove references to tools no longer needed

### Step 5: Preserve Structure

I'll ensure the edited agent maintains:
- ✅ Valid YAML frontmatter format
- ✅ Clear section organization
- ✅ Consistent markdown formatting
- ✅ Professional tone and style
- ✅ Production-ready quality

### Step 6: Save and Report

I'll:
1. Save the updated agent file
2. Report what was changed
3. Provide a summary of improvements
4. Confirm the agent is ready to use

## Example Usage

**With arguments:**
```
/edit-agent "frontend-developer" "add recommendations for React 19 features and server components"
```

**Without arguments (interactive):**
```
/edit-agent
```
I'll ask you which agent to edit and what changes you want.

## Edit Instructions Examples

**Adding features:**
- "add TypeScript strict mode best practices"
- "include guidelines for testing with Vitest"
- "add section on accessibility standards"

**Improving content:**
- "make the workflow steps more detailed"
- "add more specific examples for API integration"
- "expand the error handling guidelines"

**Updating technology:**
- "update to React 19 recommendations"
- "add modern CSS-in-JS approaches"
- "include Bun runtime support"

**Fixing issues:**
- "remove outdated jQuery references"
- "fix incorrect ESLint configuration"
- "update deprecated API usage"

**Restructuring:**
- "reorganize capabilities by priority"
- "split long sections into subsections"
- "combine redundant best practices"

## What I'll Change

Based on your instructions, I'll intelligently modify:

### Content Updates
- Add new sections, capabilities, or guidelines
- Update existing content with improvements
- Remove outdated or incorrect information
- Expand brief explanations with more detail

### Tool Updates
- Add tools to YAML frontmatter if needed
- Remove tools that are no longer required
- Update tool usage examples

### Quality Improvements
- Fix typos or grammar issues
- Improve clarity and readability
- Add missing examples or use cases
- Ensure consistent formatting

### Structural Changes
- Reorganize sections for better flow
- Add subsections for complex topics
- Consolidate redundant content
- Improve section headers

## Timeline

Agent editing typically takes 1-3 minutes depending on the complexity of changes. You'll receive a report showing what was modified.

## After Editing

The updated agent will be immediately available with your improvements:

```
Task tool with subagent_type="your-agent-name":
"Your task with improved agent capabilities"
```

---

Let me locate the agent and apply your requested changes...
