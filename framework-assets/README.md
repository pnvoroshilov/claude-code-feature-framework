# Framework Assets

This directory contains all framework components that are deployed to user projects when they use ClaudeTask.

## Structure

```
framework-assets/
├── agents/                    # Specialized Claude Code agents
│   └── development/           # Development-focused agents
│       ├── ai-implementation-expert.md
│       ├── api-validator.md
│       ├── backend-architect.md
│       ├── background-tester.md
│       ├── context-analyzer.md
│       ├── data-formatter.md
│       ├── devops-engineer.md
│       ├── docs-generator.md
│       ├── frontend-developer.md
│       ├── fullstack-code-reviewer.md
│       ├── mcp-engineer.md
│       ├── memory-sync.md
│       ├── mobile-react-expert.md
│       ├── python-api-expert.md
│       ├── ux-ui-researcher.md
│       └── web-tester.md
├── claude-configs/            # CLAUDE.md templates and configurations
│   └── CLAUDE.md             # Default framework instructions
└── templates/                # Project templates and boilerplates
```

## Deployment

When a user initializes or updates a ClaudeTask project, these assets are deployed as follows:

1. **Agents** → `.claude/agents/` in the user's project
2. **CLAUDE.md** → Root of the user's project (customized with project details)
3. **Templates** → Used during project initialization

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

## Usage

These assets are automatically managed by the ClaudeTask framework:
- Updated via `framework_update_service.py`
- Deployed during project initialization
- Synchronized when framework updates are available