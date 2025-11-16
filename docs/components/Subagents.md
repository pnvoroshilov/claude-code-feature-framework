# Subagents Component

React component for managing Claude Code subagents - specialized AI assistants with focused expertise and specific tool access.

## Location

`claudetask/frontend/src/pages/Subagents.tsx`

## Purpose

Provides a comprehensive interface for:
- Browsing and enabling default framework subagents
- Creating custom project-specific subagents
- Managing subagent configurations and capabilities
- Viewing subagent markdown definitions
- Toggling subagent activation for different projects

## Features

### 1. Subagent Categories

**Predefined Categories:**
- **Development** - Frontend, backend, and fullstack developers
- **Analysis** - Business analysts, requirements analysts, context analyzers
- **Testing** - Quality engineers, test automation, web testers
- **Architecture** - System architects, backend/frontend architects
- **DevOps** - Infrastructure, deployment, CI/CD specialists
- **Security** - Security engineers, vulnerability assessment
- **Documentation** - Technical writers, docs generators
- **Quality** - Code reviewers, refactoring experts
- **Performance** - Performance engineers, optimization specialists
- **Custom** - User-defined subagents

### 2. Filter and Search

**Filter Options:**
- **All**: Show all subagents (default + custom + enabled)
- **Default**: Framework-provided subagents only
- **Custom**: User-created project-specific subagents
- **Favorite**: Starred subagents for quick access
- **Enabled**: Currently active subagents only

**Search:**
- Real-time search across subagent names and descriptions
- Case-insensitive matching
- Filters displayed subagents dynamically

### 3. Subagent Display Cards

**Visual Design:**
- Material-UI Card components with professional layout
- Category badges with color coding
- Favorite star icon (toggle on/off)
- Enable/disable switch
- Quick action buttons (View, Edit, Archive)

**Card Information:**
- Subagent name and description
- Category and subagent type
- Tools available (if specified)
- Recommended use cases
- Creator information (for custom subagents)
- Enable/disable toggle switch

### 4. Subagent Management Actions

#### Enable/Disable Subagent
```tsx
const handleEnableSubagent = async (
  subagentId: number,
  subagentKind: 'default' | 'custom'
) => {
  await axios.post(
    `/api/projects/${projectId}/subagents/enable/${subagentId}?subagent_kind=${subagentKind}`
  );
};

const handleDisableSubagent = async (subagentId: number) => {
  await axios.post(`/api/projects/${projectId}/subagents/disable/${subagentId}`);
};
```

#### Mark as Favorite
```tsx
const handleToggleFavorite = async (
  subagentId: number,
  subagentKind: 'default' | 'custom',
  currentState: boolean
) => {
  const endpoint = currentState ? 'unfavorite' : 'favorite';
  await axios.post(
    `/api/projects/${projectId}/subagents/${endpoint}/${subagentId}?subagent_kind=${subagentKind}`
  );
};
```

#### Archive Custom Subagent
```tsx
const handleArchiveSubagent = async (subagentId: number) => {
  await axios.post(`/api/projects/${projectId}/subagents/archive/${subagentId}`);
};
```

### 5. Create Custom Subagent Dialog

**Form Fields:**
- **Name**: Subagent identifier (required)
  - Auto-sanitized: lowercase, hyphens replace spaces
  - Example: "React Expert" → "react-expert"
- **Description**: Subagent purpose and expertise (required)

**Subagent Creation Process:**
1. User enters name and description
2. Frontend sanitizes name (lowercase, hyphenated)
3. Backend creates `/claude-agents/{name}.md` file via skills-creator agent
4. Markdown file contains instructions and capabilities
5. Subagent registered in database
6. Automatically enabled for current project

**Example Creation Request:**
```json
{
  "name": "React Performance Expert",
  "description": "Specialist in React performance optimization, memoization, and rendering strategies"
}
```

**Generated File:** `framework-assets/claude-agents/react-performance-expert.md`

### 6. View Subagent Definition Dialog

**Features:**
- Full markdown content display of subagent instructions
- Syntax highlighting for code blocks
- Read-only view
- Copy-to-clipboard functionality
- Scrollable content area

**Subagent Markdown Structure:**
```markdown
# {Subagent Name}

{Role and expertise description}

## Capabilities
- Capability 1
- Capability 2
- Capability 3

## Tools Available
- Tool 1: Purpose
- Tool 2: Purpose

## Best Practices
- Guideline 1
- Guideline 2

## Example Usage
{Usage examples and patterns}
```

### 7. Edit Custom Subagent

**Editable via Code Editor:**
- Opens CodeEditorDialog component
- Full markdown editing capabilities
- Syntax highlighting
- Save updates to subagent file
- Cannot edit default subagents (only custom)

**Editor Features:**
- Monaco-based code editor
- Markdown syntax support
- Line numbers and formatting
- Auto-save on close
- Validation before saving

## Props

This is a page component and doesn't accept props. It uses:
- `ProjectContext` for current project selection
- Internal state management for subagent data

## State Management

```tsx
const [activeFilter, setActiveFilter] = useState<FilterType>('all');
const [searchQuery, setSearchQuery] = useState('');
const [subagents, setSubagents] = useState<SubagentsResponse>({
  enabled: [],
  available_default: [],
  custom: [],
  favorites: [],
});
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [selectedSubagent, setSelectedSubagent] = useState<Subagent | null>(null);
const [createDialogOpen, setCreateDialogOpen] = useState(false);
const [viewSubagentDialogOpen, setViewSubagentDialogOpen] = useState(false);
```

## API Integration

### Endpoints Used

1. **GET /api/projects/{project_id}/subagents/**
   - Fetches all subagents (enabled, default, custom, favorites)
   - Returns structured SubagentsResponse object

2. **POST /api/projects/{project_id}/subagents/enable/{subagent_id}**
   - Enables a subagent for the project
   - Query param: `subagent_kind` (default or custom)

3. **POST /api/projects/{project_id}/subagents/disable/{subagent_id}**
   - Disables an active subagent

4. **POST /api/projects/{project_id}/subagents/favorite/{subagent_id}**
   - Marks subagent as favorite
   - Query param: `subagent_kind`

5. **POST /api/projects/{project_id}/subagents/unfavorite/{subagent_id}**
   - Removes favorite status

6. **POST /api/projects/{project_id}/subagents/**
   - Creates new custom subagent
   - Uses skills-creator agent to generate markdown file
   - Request body: `{ name, description }`

7. **PUT /api/projects/{project_id}/subagents/{subagent_id}**
   - Updates existing custom subagent markdown content
   - Cannot edit default subagents

8. **POST /api/projects/{project_id}/subagents/archive/{subagent_id}**
   - Archives (soft delete) custom subagent
   - Sets status to 'archived'
   - Cannot archive default subagents

9. **GET /api/projects/{project_id}/subagents/{subagent_id}/content**
   - Fetches raw markdown content of subagent definition
   - Used for viewing and editing

## Default Framework Subagents

### Development Specialists
- **frontend-developer** - React/TypeScript UI development
- **backend-architect** - FastAPI/Python backend design
- **python-expert** - Python coding and best practices
- **mobile-react-expert** - Mobile-first React development
- **python-api-expert** - RESTful API design and implementation
- **fullstack-developer** - End-to-end feature development

### Analysis Specialists
- **business-analyst** - Requirements gathering and analysis
- **requirements-analyst** - Technical specification creation
- **context-analyzer** - Codebase understanding and analysis
- **root-cause-analyst** - Bug investigation and debugging
- **systems-analyst** - System design and architecture planning

### Architecture Specialists
- **system-architect** - High-level system design
- **backend-architect** - Backend infrastructure planning
- **frontend-architect** - Frontend application structure
- **devops-architect** - Infrastructure and deployment design

### Testing & Quality
- **quality-engineer** - Test strategy and quality assurance
- **web-tester** - Web application testing
- **background-tester** - Service and integration testing
- **fullstack-code-reviewer** - Comprehensive code review

### Specialized Roles
- **security-engineer** - Security analysis and hardening
- **performance-engineer** - Performance optimization
- **technical-writer** - Documentation creation
- **refactoring-expert** - Code quality improvement
- **devops-engineer** - CI/CD and deployment automation

## Subagent File Structure

**Location:** `framework-assets/claude-agents/{subagent-name}.md`

**Default Subagents:** Pre-created in framework
**Custom Subagents:** Generated dynamically via skills-creator agent

**File Naming:**
- Lowercase with hyphens
- Examples: `frontend-developer.md`, `react-performance-expert.md`

**Content Format:**
```markdown
# {Subagent Name}

{Brief role description}

## Responsibilities
- Primary responsibility 1
- Primary responsibility 2

## Capabilities
- What the subagent can do
- Tools and techniques available

## Approach
- How the subagent works
- Decision-making process

## Tools
- Available MCP tools
- Framework utilities

## Example Interactions
{Sample conversations and workflows}
```

## Common Use Cases

### 1. Creating a Domain-Specific Expert

**Use Case**: Need an expert for GraphQL API development

**Steps:**
1. Click "Create Custom Subagent"
2. Name: "GraphQL API Expert"
3. Description: "Specialist in GraphQL schema design, resolvers, and query optimization"
4. Save → skills-creator agent generates markdown file
5. Enable for project
6. Use in Task delegation or direct commands

### 2. Enabling Framework Specialists

**Use Case**: Working on React frontend task

**Steps:**
1. Filter by "Development" category
2. Find "frontend-developer" and "mobile-react-expert"
3. Enable both subagents
4. Mark as favorites for quick access
5. Delegate React tasks to these specialists

### 3. Customizing Existing Patterns

**Use Case**: Modify security-engineer for project-specific security policies

**Steps:**
1. Create custom "Security Auditor" subagent
2. View framework's security-engineer.md for reference
3. Edit custom subagent with project security requirements
4. Add company-specific security tools and policies
5. Enable and use for security reviews

## UI Improvements (v2.0)

**Recent Enhancements:**
- Professional card-based layout with consistent design
- Color-coded category badges
- Improved filtering and search UX
- Better mobile responsiveness
- Enhanced dialog layouts with tabs
- Loading states and error handling
- Empty state messaging for filter results
- Integration with CodeEditorDialog for markdown editing

**Design System:**
- Material-UI theme consistency
- Smooth hover effects and transitions
- Professional SaaS-style aesthetics
- Accessible color contrasts

## Integration with Task System

Subagents are used by the Task Coordinator for delegation:

**Delegation Pattern:**
```markdown
Task tool with frontend-developer:
"Create a responsive navigation menu component.

Requirements:
- Mobile-first design
- Accessibility support
- Material-UI components

Please implement in src/components/Navigation.tsx"
```

**Agent Selection:**
- Coordinator analyzes task type
- Selects appropriate enabled subagent
- Provides task context and requirements
- Agent executes with specialized knowledge

## Error Handling

**User-Facing Errors:**
- Failed to fetch subagents
- Failed to enable/disable subagent
- Failed to create custom subagent
- Subagent file not found
- Invalid markdown content

**Error Display:**
- Alert banner at top of page
- Inline validation errors in dialogs
- Toast notifications for quick actions
- Detailed error messages in console

## Performance Considerations

**Optimization Strategies:**
- Fetch subagents only when project changes
- Debounced search input
- Memoized filtered subagent lists
- Lazy loading of markdown content
- Efficient state updates

## Accessibility

- Keyboard navigation support
- ARIA labels on interactive elements
- Screen reader-friendly descriptions
- Focus management in dialogs
- Color contrast compliance (WCAG AA)

## Related Documentation

- [Skills Component](./Skills.md) - Related skill management UI
- [Task Coordinator](../architecture/task-coordination.md) - Agent delegation system
- [Subagent Creation API](../api/endpoints/subagents.md) - Backend API documentation
