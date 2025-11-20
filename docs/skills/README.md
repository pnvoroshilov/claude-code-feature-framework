# Claude Code Skills Documentation

This directory documents the Claude Code skills available in the framework. Skills extend Claude's capabilities with specialized expertise in specific domains.

## What Are Skills?

**Skills** are packaged sets of instructions that give Claude expertise in specific areas. They activate automatically based on keywords or can be invoked explicitly.

### Key Concepts

- **Automatic Activation**: Skills detect relevant keywords and activate when needed
- **Manual Activation**: Use `Skill: "skill-name"` to explicitly activate
- **Packaged Expertise**: Each skill contains comprehensive knowledge in its domain
- **Composable**: Multiple skills can work together

## Available Skills

### Data Format Skills

#### [TOON Format](./toon-format.md)
Expert skill for Token-Oriented Object Notation - a compact data format for LLM applications.

**Key Features**:
- JSON ↔ TOON conversion with 30-60% token reduction
- Token optimization for LLM API calls
- Python and TypeScript implementation support
- Multi-agent communication patterns

**Auto-activates on**: "TOON format", "token optimization", "reduce tokens"

**Manual activation**: `Skill: "toon-format"`

**Location**: `framework-assets/claude-skills/toon-format/`

### Requirements Analysis Skills

#### [UseCase Writer](./usecase-writer.md)
Expert skill for creating comprehensive, standards-compliant UseCases from requirements.

**Key Features**:
- Actor identification and analysis
- Structured flow documentation (main + alternative paths)
- Complete documentation (preconditions, postconditions, business rules)
- Standards compliance (UML, Cockburn, IEEE 830, RUP)

**Auto-activates on**: "use case", "usecase", "user flow", "acceptance criteria"

**Manual activation**: `Skill: "usecase-writer"`

**Location**: `framework-assets/claude-skills/usecase-writer/`

## Skills Directory Structure

```
framework-assets/claude-skills/
├── toon-format/
│   ├── README.md          # Skill overview and quick start
│   ├── SKILL.md           # Main skill instruction file
│   ├── examples.md        # Detailed examples and use cases
│   └── reference.md       # Complete reference documentation
├── usecase-writer/
│   ├── README.md          # Skill overview
│   ├── SKILL.md           # Main skill instruction file
│   ├── reference.md       # Standards and templates reference
│   └── examples/
│       ├── basic.md       # Simple use case examples
│       ├── intermediate.md # Complex examples
│       └── advanced.md    # Enterprise-level examples
└── ... (other skills)
```

## Using Skills

### Automatic Activation

Skills activate automatically when you mention relevant keywords:

```
User: "I need to convert this JSON to a more token-efficient format"
→ TOON Format skill activates automatically
```

### Manual Activation

Explicitly activate a skill with the Skill command:

```
Skill: "toon-format"

Now convert this data to TOON format:
{ "users": [...] }
```

### Combining Skills

Multiple skills can work together:

```
Skill: "usecase-writer"
Skill: "toon-format"

Create a use case for the authentication system and format
the data models using TOON for token efficiency.
```

## Skills vs Other Framework Components

### Skills vs Subagents
- **Skills**: Knowledge and expertise (what Claude knows)
- **Subagents**: Specialized roles and workflows (how Claude works)

**Example**:
- **Skill**: TOON Format (knowledge of TOON syntax)
- **Subagent**: Backend Architect (role: design backend systems)

### Skills vs Hooks
- **Skills**: Extend Claude's capabilities
- **Hooks**: Automate actions at workflow trigger points

**Example**:
- **Skill**: UseCase Writer (create use cases from requirements)
- **Hook**: Post-merge documentation (trigger doc updates after merge)

## Creating Custom Skills

### Skill Structure

A complete skill includes:

1. **SKILL.md** - Main skill instruction file
   - Skill description and purpose
   - Automatic activation keywords
   - Core capabilities
   - Implementation guidelines

2. **README.md** - Quick start guide
   - Skill overview
   - Activation instructions
   - Basic usage examples

3. **examples.md** - Detailed examples
   - Real-world use cases
   - Before/after comparisons
   - Integration patterns

4. **reference.md** - Complete reference
   - API documentation
   - Standards and specifications
   - Best practices

### Skill Template

```markdown
# Skill Name

Brief description of what this skill does.

## Automatic Activation

activation_keywords[N]:
keyword1
keyword2
...

## Core Capabilities

capabilities[N]{capability,description}:
Capability Name,Description of what it does
...

## Usage Example

[Provide clear examples]

## When to Use

[Describe appropriate use cases]

## Related Skills

[Link to complementary skills]
```

## Default Framework Skills

The framework includes these skills by default:

1. **toon-format** - Token-efficient data format expertise
2. **usecase-writer** - Requirements analysis and use case creation

Additional skills can be added via:
- Framework assets directory
- Project-specific skills directory
- Skills management UI

## Skills Management UI

Access the Skills management interface at:
```
/projects/{project_id}/skills
```

**Features**:
- Browse available skills
- Enable/disable skills per project
- View skill documentation
- Create custom skills
- Update skill metadata

See [Skills Component Documentation](../components/Skills.md) for UI details.

## Skill Activation Keywords

### TOON Format Skill
```
toon-format, toon, token-oriented object notation, reduce tokens,
token optimization, token efficiency, compact format, llm data format
```

### UseCase Writer Skill
```
use case, usecase, write use case, create use case, user flow,
user scenario, acceptance criteria, actors and preconditions,
main flow, alternative flow, extension flow, use case diagram,
requirements analysis, business requirements, functional specification
```

## Best Practices

### 1. Use Automatic Activation
Let skills activate naturally by mentioning relevant concepts:
```
"How can I reduce token usage in my API calls?"
→ TOON Format skill activates automatically
```

### 2. Explicit Activation for Clarity
Use manual activation when you want to ensure a skill is active:
```
Skill: "usecase-writer"

Write a use case for the login feature.
```

### 3. Check Skill Documentation
Each skill has comprehensive documentation with examples:
- `README.md` - Quick start
- `SKILL.md` - Full capabilities
- `examples.md` - Real-world examples
- `reference.md` - Complete reference

### 4. Combine Skills When Needed
Multiple skills can work together for complex tasks:
```
Skill: "usecase-writer"
Skill: "toon-format"

Document the authentication flow as a use case and
format all data models in TOON for token efficiency.
```

## Performance Considerations

### Token Usage
- Skills add context to Claude's prompt
- Only activated skills consume tokens
- Automatic activation is efficient - only activates when needed

### Skill Combinations
- Multiple skills can be active simultaneously
- Each skill adds its context to the prompt
- Be mindful of context window limits with many skills

## Troubleshooting

### Skill Not Activating
**Issue**: Expected skill doesn't activate automatically.

**Solution**:
- Check activation keywords in skill's SKILL.md
- Use explicit activation: `Skill: "skill-name"`
- Verify skill is enabled for the project

### Skill Conflicts
**Issue**: Multiple skills provide overlapping capabilities.

**Solution**:
- Use explicit activation to choose specific skill
- Check skill priority and activation order
- Disable conflicting skills if not needed

### Outdated Skill Documentation
**Issue**: Skill documentation doesn't match current implementation.

**Solution**:
- Check skill version in SKILL.md
- Review recent updates in skill directory
- Update skill via Skills management UI

## Contributing Skills

### Adding Skills to Framework

1. Create skill directory in `framework-assets/claude-skills/`
2. Include all required files (SKILL.md, README.md, etc.)
3. Define clear activation keywords
4. Provide comprehensive examples
5. Test skill activation and functionality

### Skill Quality Standards

**Required**:
- Clear purpose and scope
- Automatic activation keywords
- Usage examples
- Reference documentation

**Recommended**:
- Multiple example scenarios
- Integration patterns
- Best practices guide
- Troubleshooting section

## Related Documentation

- [Skills Component](../components/Skills.md) - Skills management UI
- [Subagents Documentation](../components/Subagents.md) - Specialized AI roles
- [Hooks Documentation](../components/Hooks.md) - Workflow automation
- [Framework Assets](../../framework-assets/README.md) - All framework resources

## Future Skills

**Planned Skills**:
- **API Design** - REST API design best practices
- **Database Schema** - Database design and optimization
- **Security Analysis** - Security vulnerability assessment
- **Performance Optimization** - Code and system performance tuning
- **Test Strategy** - Test planning and coverage analysis

## Skill Metrics

**Current Statistics**:
- Total Skills: 2 (TOON Format, UseCase Writer)
- Skill Categories: Data Formats (1), Requirements Analysis (1)
- Total Documentation Files: 9
- Average Activation Keywords: 8-15 per skill

---

**Last Updated**: 2025-11-20
**Documentation Status**: Active
**Total Skills Documented**: 2
**Framework Version**: 1.0
