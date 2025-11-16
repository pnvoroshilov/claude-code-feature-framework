# React Components Documentation

This directory contains documentation for React components in the ClaudeTask Framework frontend application.

## Available Components

### Session Management

#### [ClaudeSessions](./ClaudeSessions.md)
Comprehensive interface for managing and monitoring Claude Code sessions.

**Features:**
- Browse sessions by project
- Enhanced message display with color-coded bubbles
- Active session monitoring
- Session detail views with tabs (Info, Messages, Tools, Timeline)
- Process termination capabilities

**Location:** `claudetask/frontend/src/pages/ClaudeSessions.tsx`

**Status:** Active, Recently Updated (v2.0.0)

### Task Management

#### [Skills](./Skills.md)
Skills management interface for creating and managing Claude Code skills.

**Features:**
- Browse available skills
- Create new skills via dedicated agent
- View skill details and implementation
- Enable/disable skills for projects

**Location:** `claudetask/frontend/src/pages/Skills.tsx`

**Status:** Active

### Other Components

Additional component documentation will be added as components are created or updated.

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
- ClaudeSessions - Session browsing and monitoring
- ClaudeCodeSessions - Alternative session view

### 2. Framework Management
Components for managing framework features:
- Skills - Skill creation and management
- Hooks - Hook configuration
- Subagents - Subagent management

### 3. Task Management
Components for task and project management:
- Tasks - Task board and details
- Projects - Project configuration

### 4. Shared Components
Reusable components used across the application:
- Common UI elements
- Forms and inputs
- Layout components

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

**Last Updated**: 2025-11-16
**Total Components Documented**: 2
**Documentation Status**: Active maintenance
