# Framework Assets

This directory contains all framework components that are deployed to user projects when they use ClaudeTask.

## Structure

```
framework-assets/
├── claude-agents/             # Specialized Claude Code agents
│   ├── ai-implementation-expert.md
│   ├── api-validator.md
│   ├── backend-architect.md
│   ├── background-tester.md
│   ├── context-analyzer.md
│   ├── data-formatter.md
│   ├── devops-engineer.md
│   ├── docs-generator.md
│   ├── frontend-developer.md
│   ├── fullstack-code-reviewer.md
│   ├── mcp-engineer.md
│   ├── memory-sync.md
│   ├── mobile-react-expert.md
│   ├── python-api-expert.md
│   ├── skills-creator.md      # Skill creation specialist
│   ├── ux-ui-researcher.md
│   └── web-tester.md
├── claude-commands/           # Default slash commands
├── claude-configs/            # CLAUDE.md templates and configurations
│   └── CLAUDE.md             # Default framework instructions
├── claude-hooks/              # Default hooks for automation
├── claude-skills/             # Default skills for Claude Code
│   ├── api-development/       # API design and implementation
│   ├── api-integration/       # Frontend-backend integration
│   ├── code-review/           # Code review automation
│   ├── database-migration/    # Database schema management
│   ├── debug-helper/          # Debugging assistance
│   ├── deployment-helper/     # Deployment automation
│   ├── documentation-writer/  # Technical documentation
│   ├── git-workflow/          # Git operations and PR management
│   ├── refactoring/           # Code refactoring
│   ├── test-runner/           # Test execution and coverage
│   ├── toon-format/           # 🆕 TOON format expertise
│   ├── ui-component/          # React component creation
│   ├── usecase-writer/        # 🆕 UseCase creation expertise
│   └── pdf-creator/           # PDF generation
└── mcp-configs/              # MCP server configurations
```

## Deployment

When a user initializes or updates a ClaudeTask project, these assets are deployed as follows:

1. **Agents** → `.claude/agents/` in the user's project
2. **Commands** → `.claude/commands/` in the user's project
3. **Hooks** → `.claude/hooks/` in the user's project
4. **Skills** → `.claude/skills/` in the user's project
5. **CLAUDE.md** → Root of the user's project (customized with project details)
6. **MCP Configs** → MCP server configurations

## Agent Categories

### Core Development
- `backend-architect` - Backend architecture and design
- `frontend-developer` - React and UI development
- `python-api-expert` - FastAPI and Python backend
- `fullstack-code-reviewer` - Comprehensive code review

### Testing & Quality
- `background-tester` - Automated testing in background
- `web-tester` - E2E and browser testing
- `api-validator` - API validation and testing
- `ux-ui-researcher` - UX/UI analysis and research

### Specialized
- `ai-implementation-expert` - AI/ML functionality
- `mobile-react-expert` - React Native development
- `devops-engineer` - Docker and deployment
- `mcp-engineer` - MCP protocol implementation

### Support
- `context-analyzer` - Code context analysis
- `data-formatter` - Data transformation
- `docs-generator` - Documentation generation
- `memory-sync` - Memory and state management

### Meta
- `skills-creator` - Creates new Claude Code skills with proper structure

## Default Skills

### Documentation & Requirements
- **usecase-writer** 🆕 - Creates comprehensive UseCases from requirements
  - Follows UML, Cockburn, and IEEE 830 standards
  - Generates actors, flows, preconditions, postconditions
  - Includes basic, intermediate, and advanced examples

- **toon-format** 🆕 - TOON format expertise for token-efficient documentation
  - ~40% token reduction vs JSON
  - Human-readable structured data
  - Complete syntax reference and examples

### Development
- **api-development** - RESTful and GraphQL API design
- **api-integration** - Frontend-backend integration patterns
- **database-migration** - Alembic and SQLAlchemy migrations
- **ui-component** - React TypeScript component creation

### Code Quality
- **code-review** - Comprehensive code review automation
- **debug-helper** - Systematic debugging assistance
- **refactoring** - Code quality improvement patterns

### DevOps
- **deployment-helper** - Docker, CI/CD, cloud deployments
- **git-workflow** - Git operations and PR management
- **test-runner** - Test execution and coverage

### Utilities
- **documentation-writer** - Technical documentation generation
- **pdf-creator** - PDF generation and conversion

## Usage

These assets are automatically managed by the ClaudeTask framework:
- Updated via `framework_update_service.py`
- Deployed during project initialization
- Synchronized when framework updates are available

### Adding New Skills to Framework

To add a new default skill:
1. Create the skill in `.claude/skills/` using `/create-skill` command
2. Test the skill thoroughly
3. Copy to `framework-assets/claude-skills/`
4. Update this README with skill description
5. Skills will be deployed to all new projects automatically