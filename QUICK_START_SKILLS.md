# Quick Start: Creating Claude Code Skills

## TL;DR

**What:** Skills are modular instruction packages that give Claude specialized capabilities
**Format:** Markdown files with frontmatter metadata and structured sections
**Location:** `.claude/skills/` directory
**Structure:** Follow official Anthropic format (see examples below)

## Created Files

### 1. Skills Creator Agent
**File:** `.claude/agents/skills-creator.md` (635 lines)

**Use this agent when:** Creating new skills for the framework

**How to use:**
```
"Use the skills-creator agent to create a skill for [topic]"
```

### 2. Business Requirements Analysis Skill
**File:** `.claude/skills/business-requirements-analysis.md` (433 lines)

**Use this as:** The gold-standard example for creating other skills

**What it demonstrates:**
- Proper frontmatter format
- All required sections
- Multiple usage examples
- Best practices integration
- Troubleshooting guidance
- Related skills references

### 3. Research Summary
**File:** `SKILLS_RESEARCH_SUMMARY.md` (649 lines)

**Contains:**
- Official documentation findings
- Best practices from Anthropic
- Real examples from cookbooks
- Quality checklists
- Guidelines for creating remaining skills

## Minimum Viable Skill Structure

```markdown
---
name: skill-name-kebab-case
description: Clear one-sentence description under 150 characters
---

# Skill Display Name

Brief overview paragraph.

## Capabilities
- **Feature 1**: What it does
- **Feature 2**: When to use it
- **Feature 3**: Key benefits

## How to Use
1. First step
2. Second step
3. Third step

## Input Format
- **Data Type**: CSV, JSON, text
- **Required Fields**: field1, field2
- **Example**: [show example]

## Output Format
- **Output Type**: Report, file, data
- **Format**: Structure description
- **Example**: [show example]

## Example Usage
> "Natural language example request"

Expected output: [describe what happens]

## Best Practices
1. Practice 1: Why it matters
2. Practice 2: Common pitfall
3. Practice 3: Optimization tip

## Limitations
- Cannot do X because Y
- Edge case Z not supported
- Requires dependency A

## Related Skills
- `related-skill-1`: How they work together
```

## Essential Rules

### DO ✅
- Use **kebab-case** for skill names
- Keep description under **150 characters**
- Include **3-5 usage examples**
- Document **limitations** honestly
- Use **active voice** in instructions
- Reference **related skills**

### DON'T ❌
- Use generic names (helper, tool1)
- Write vague descriptions
- Skip input/output formats
- Ignore edge cases
- Embed everything in SKILL.md
- Duplicate existing skills

## 9 Recommended Skills to Create

1. **technical-specification** - Business requirements → technical specs
2. **code-review-checklist** - Code quality and review standards
3. **git-workflow-automation** - Version control best practices
4. **test-case-generation** - Create test scenarios from requirements
5. **documentation-writer** - Technical documentation standards
6. **api-endpoint-designer** - RESTful API design guidelines
7. **database-schema-design** - Data modeling and migrations
8. **performance-optimization** - Performance analysis and improvements
9. **security-audit** - Security best practices and vulnerability checks

## Creation Workflow

### Step 1: Plan
```
- Define skill purpose
- Identify capabilities
- List use cases
- Determine structure (single/multi-file)
```

### Step 2: Create
```
- Use skills-creator agent
- Start with frontmatter
- Add all standard sections
- Include 3-5 examples
- Document limitations
```

### Step 3: Validate
```
- Run quality checklist
- Test discoverability
- Verify completeness
- Check formatting
- Test examples
```

### Step 4: Integrate
```
- Reference related skills
- Define input/output contracts
- Enable workflow composition
- Update documentation
```

## Quality Checklist (Short Version)

- [ ] Name is kebab-case and descriptive
- [ ] Description under 150 characters
- [ ] All standard sections present
- [ ] Input/output formats specified
- [ ] 3-5 usage examples included
- [ ] Limitations documented
- [ ] Related skills referenced
- [ ] Markdown properly formatted
- [ ] Tested with example queries

## Common Patterns

### Analysis Skills
Focus: Data → Insights → Recommendations
```
Input: Raw data (CSV, JSON)
Process: Analysis, calculations
Output: Reports, metrics, insights
```

### Workflow Skills
Focus: Step-by-step automation
```
Input: Task description
Process: Sequential actions
Output: Completed workflow
```

### Development Skills
Focus: Code generation and standards
```
Input: Requirements, context
Process: Code generation, validation
Output: Code files, documentation
```

### Integration Skills
Focus: System connections
```
Input: Configuration, data
Process: API calls, transformations
Output: Integrated results
```

## Example: Creating Your First Skill

Let's create `technical-specification.md`:

```markdown
---
name: technical-specification
description: Converts business requirements into detailed technical specifications with architecture and implementation details
version: 1.0.0
tags: [technical, specification, architecture, design]
---

# Technical Specification Skill

Transforms business requirements into implementable technical specifications.

## Capabilities
- **Architecture Design**: Define system components and interactions
- **API Specifications**: Detail endpoints, methods, parameters
- **Data Models**: Design database schemas and relationships
- **Technology Stack**: Recommend appropriate technologies
- **Implementation Plan**: Break down into development tasks

## How to Use
1. Provide business requirements document or user stories
2. Specify target technology stack (if known)
3. Request technical specification generation
4. Review and refine specifications

## Input Format
- **Business Requirements**: User stories, BRD, or PRD
- **Context**: Existing system architecture (if applicable)
- **Constraints**: Technology, budget, timeline limitations
- **Format**: Text, markdown, or document upload

## Output Format
- **Technical Specification Document** including:
  - System Architecture Diagram
  - Component Specifications
  - API Definitions (OpenAPI/Swagger format)
  - Database Schema (ERD)
  - Security Considerations
  - Performance Requirements
  - Deployment Strategy

## Example Usage

**Example 1: From User Story**
> "Convert this user story into a technical specification: As a user,
> I want to see a Continue button on task cards so I can resume work"

Output: Technical spec with:
- Frontend component changes
- State management updates
- API endpoints (if needed)
- Database changes (if needed)
- Testing requirements

**Example 2: Full Feature**
> "Create technical specifications for the invoice processing feature
> described in this requirements document"

Output: Complete technical design with:
- System architecture
- Component breakdown
- API specifications
- Database schema
- Integration points
- Implementation phases

## Best Practices
1. **Start High-Level**: System architecture before details
2. **Be Specific**: Exact technologies, versions, configurations
3. **Consider Non-Functionals**: Performance, security, scalability
4. **Plan for Testing**: Unit, integration, E2E test requirements
5. **Document Assumptions**: Make technical assumptions explicit

## Limitations
- Cannot make final technology decisions (provides recommendations)
- Requires clear business requirements as input
- May need refinement based on technical feasibility
- Does not include actual implementation code

## Related Skills
- `business-requirements-analysis`: Provides input requirements
- `api-endpoint-designer`: Detailed API design
- `database-schema-design`: Detailed database design
- `test-case-generation`: Create tests from specs

## Version History
- **1.0.0** (2025-01-30): Initial release
```

Save as: `.claude/skills/technical-specification.md`

## Resources

### Official Docs
- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

### Examples
- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- Business Requirements Analysis skill (this repo)

### Tools
- Skills Creator agent (this repo)
- Quality checklist (in research summary)

## Next Steps

1. **Study the example skill** - `business-requirements-analysis.md`
2. **Use the Skills Creator agent** - For creating new skills
3. **Create remaining 9 skills** - Following the pattern
4. **Test each skill** - Validate with real use cases
5. **Iterate and improve** - Based on usage feedback

---

**Questions?** Review the detailed `SKILLS_RESEARCH_SUMMARY.md`

**Ready to create?** Use: "skills-creator agent, create a skill for [topic]"
