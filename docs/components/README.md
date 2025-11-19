# React Components Documentation

This directory contains documentation for React components in the ClaudeTask Framework frontend application.

## Available Components

### Session Management

#### [ClaudeSessions](./ClaudeSessions.md)
Comprehensive interface for managing and monitoring embedded Claude Code task sessions.

**Features:**
- Browse sessions by project and task
- Enhanced message display with color-coded bubbles
- Active session monitoring with real-time updates
- Session detail views with tabs (Info, Messages, Tools, Timeline)
- Process termination and command execution capabilities

**Location:** `claudetask/frontend/src/pages/ClaudeSessions.tsx`

**Status:** Active, Recently Updated (v2.0.0)

#### [ClaudeCodeSessions](./ClaudeCodeSessions.md)
Advanced analytics and browsing interface for Claude Code native session files (.jsonl).

**Features:**
- Multi-project session discovery
- Advanced statistics and analytics
- Tool usage patterns and insights
- Error tracking and debugging
- Content-based session search
- Detailed message history inspection

**Location:** `claudetask/frontend/src/pages/ClaudeCodeSessions.tsx`

**Status:** Active, Full Analytics Suite

### Project Management

#### [FileBrowser](./FileBrowser.md)
GitHub-style file browser and code editor with comprehensive file management and refined UI/UX.

**Features:**
- Complete file management: create, read, save, rename, delete, copy
- File system navigation within project scope
- Monaco Editor integration with syntax highlighting
- Markdown preview mode with GitHub-flavored markdown
- Context menu for right-click operations
- Copy/paste with clipboard support
- Auto-generated unique names for paste operations (file.txt → file (1).txt → file (2).txt)
- Modal dialogs for file operations
- Compact single-line header with smart visibility toggles
- Stable layout with no button wrapping or disappearing
- Breadcrumb navigation with enhanced visibility (200px maxWidth)
- Editor panel with consistent layout (no full-width expansion on first open)
- Null-safe delete operations with automatic selection clearing
- Security with path traversal protection
- Support for 15+ programming languages
- Unsaved changes detection

**Location:** `claudetask/frontend/src/pages/FileBrowser.tsx`

**Status:** Active, Production Ready (v2.0.1 - Latest UI/UX Refinements)

### Framework Management

#### [Hooks](./Hooks.md)
Hooks management interface for configuring automated shell commands at workflow trigger points.

**Features:**
- Browse and enable default framework hooks
- Create custom project-specific hooks
- Category-based organization and filtering
- JSON hook configuration editor
- Dependency management
- Favorite hooks for quick access

**Location:** `claudetask/frontend/src/pages/Hooks.tsx`

**Status:** Active, Core Framework Feature

#### [Subagents](./Subagents.md)
Subagent management interface for specialized AI assistants with focused expertise.

**Features:**
- Browse default framework subagents by category
- Create custom project-specific subagents
- View subagent markdown definitions
- Enable/disable subagents per project
- Edit custom subagent instructions
- Mark favorites for task delegation

**Location:** `claudetask/frontend/src/pages/Subagents.tsx`

**Status:** Active, Agent Delegation System

#### [Skills](./Skills.md)
Skills management interface for creating and managing Claude Code skills.

**Features:**
- Browse available skills library
- Create new skills via skills-creator agent
- View skill implementation code
- Enable/disable skills for projects
- Update skill status and metadata
- Archive unused skills

**Location:** `claudetask/frontend/src/pages/Skills.tsx`

**Status:** Active, Extended Capabilities System

## Component Architecture

### Technology Stack
- **React** 18.x - UI library
- **TypeScript** - Type safety
- **Material-UI (MUI)** v5 - Component library
- **React Router** v6 - Navigation
- **Fetch API** - Backend communication

### Common Patterns

#### API Integration
All components follow consistent API integration pattern:

```tsx
const [data, setData] = useState<DataType[]>([]);
const [loading, setLoading] = useState(false);

useEffect(() => {
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/endpoint');
      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [dependencies]);
```

#### State Management
Components use React hooks for local state:
- `useState` - Local component state
- `useEffect` - Side effects and API calls
- `useContext` - Global state (when needed)

#### Styling Approach
All components use MUI's `sx` prop for styling:

```tsx
<Box sx={{
  padding: 2,
  borderRadius: 1,
  bgcolor: 'background.paper',
}}>
```

### Layout Structure

```
claudetask/frontend/src/
├── pages/                    # Page-level components
│   ├── ClaudeSessions.tsx
│   ├── Skills.tsx
│   ├── Hooks.tsx
│   └── ...
├── components/               # Reusable components
│   ├── common/              # Shared UI components
│   └── ...
└── App.tsx                  # Main app component
```

## Component Categories

### 1. Session & Process Management
Components for managing Claude Code sessions and processes:
- **ClaudeSessions** - Embedded task session management with real-time monitoring
- **ClaudeCodeSessions** - Native Claude Code session analytics and browsing

### 2. Project Management
Components for project file and configuration management:
- **FileBrowser** - GitHub-style file browser and code editor with Monaco Editor integration

### 3. Framework Management
Components for managing framework features:
- **Hooks** - Automated shell command configuration at workflow trigger points
- **Subagents** - Specialized AI assistant management and delegation
- **Skills** - Extended capability creation and management

### 4. Task Management
Components for task and project management:
- **Tasks** - Task board and details (to be documented)
- **Projects** - Project configuration (to be documented)

### 5. Shared Components
Reusable components used across the application:
- **CodeEditorDialog** - Markdown/code editing dialog
- **Common UI elements** - Buttons, cards, layouts
- **Forms and inputs** - Reusable form components

## Styling Guidelines

### Theme Integration
All components use the MUI theme for consistency:

```tsx
import { useTheme, alpha } from '@mui/material';

const theme = useTheme();

// Use theme colors
sx={{
  color: theme.palette.primary.main,
  bgcolor: alpha(theme.palette.success.main, 0.1),
}}
```

### Color Palette
- **Primary**: Blue - User-initiated actions, primary CTAs
- **Success**: Green - Claude/system responses, success states
- **Error**: Red - Errors and destructive actions
- **Warning**: Orange - Warnings and cautions
- **Info**: Light Blue - Informational messages

### Responsive Design
Components should be mobile-first and responsive:

```tsx
<Grid container spacing={2}>
  <Grid item xs={12} md={6}>
    {/* Full width on mobile, half on desktop */}
  </Grid>
</Grid>
```

## Best Practices

### 1. Type Safety
Always define TypeScript interfaces for props and state:

```tsx
interface ComponentProps {
  data: DataType[];
  onUpdate: (id: string) => void;
  isLoading?: boolean;
}

const Component: React.FC<ComponentProps> = ({ data, onUpdate, isLoading = false }) => {
  // Component implementation
};
```

### 2. Error Handling
Implement proper error handling for all API calls:

```tsx
try {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
  // Handle data
} catch (error) {
  console.error('Error:', error);
  // Show user-friendly error message
}
```

### 3. Loading States
Always show loading indicators for async operations:

```tsx
{loading ? (
  <CircularProgress />
) : (
  <DataDisplay data={data} />
)}
```

### 4. Accessibility
- Use semantic HTML elements
- Add ARIA labels for screen readers
- Ensure keyboard navigation works
- Maintain proper color contrast

### 5. Performance
- Avoid unnecessary re-renders with `React.memo`
- Use `useCallback` for function props
- Lazy load heavy components
- Implement virtual scrolling for large lists

## Testing Components

### Manual Testing Checklist
- [ ] Component renders without errors
- [ ] All interactive elements work
- [ ] Loading states display correctly
- [ ] Error states handled gracefully
- [ ] Responsive on mobile and desktop
- [ ] Keyboard navigation works
- [ ] No console errors

### API Testing
Test backend integration separately:

```bash
# Test endpoint before component integration
curl http://localhost:3333/api/endpoint
```

## Creating New Component Documentation

When creating documentation for a new component, include:

1. **Purpose** - What the component does
2. **Location** - File path in codebase
3. **Props** - All accepted props with types
4. **State** - Internal state management
5. **API Integration** - Endpoints used
6. **Usage Example** - Basic usage code
7. **Styling** - MUI theme usage
8. **Related Components** - Dependencies and relations
9. **Future Enhancements** - Planned improvements
10. **Troubleshooting** - Common issues and solutions

## Component Lifecycle

### Development Flow
1. Create component in `src/pages/` or `src/components/`
2. Implement with TypeScript and MUI
3. Integrate with backend API
4. Test functionality
5. Document in `docs/components/[ComponentName].md`
6. Update this README with component entry

### Update Flow
1. Make changes to component code
2. Update component documentation
3. Update screenshots/examples if UI changed
4. Commit with descriptive message

## Contributing

When adding or updating components:
- Follow existing patterns and conventions
- Use TypeScript for type safety
- Follow MUI styling guidelines
- Document all props and state
- Add error handling
- Test on multiple screen sizes
- Update component documentation

---

**Last Updated**: 2025-11-19
**Total Components Documented**: 6
**Documentation Status**: Active maintenance

## Component Documentation Index

| Component | Category | Status | Version | Documentation |
|-----------|----------|--------|---------|---------------|
| ClaudeSessions | Session Management | Active | v2.1 | [View](./ClaudeSessions.md) |
| ClaudeCodeSessions | Session Management | Active | v1.0 | [View](./ClaudeCodeSessions.md) |
| FileBrowser | Project Management | Production Ready | v2.0.1 | [View](./FileBrowser.md) |
| Hooks | Framework Management | Active | v1.0 | [View](./Hooks.md) |
| Subagents | Framework Management | Active | v1.0 | [View](./Subagents.md) |
| Skills | Framework Management | Active | v1.0 | [View](./Skills.md) |
| Tasks | Task Management | Pending | - | To be documented |
| Projects | Task Management | Pending | - | To be documented |
