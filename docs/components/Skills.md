# Skills Page Component

## Purpose

The Skills page provides a modern, professional interface for managing Claude Code skills across projects. It allows users to view, enable, create, edit, and organize both default and custom skills with a focus on excellent user experience and visual aesthetics.

## Location

`claudetask/frontend/src/pages/Skills.tsx`

## Key Features

### 1. Modern SaaS Design
- Professional, clean interface inspired by leading SaaS products
- Glass morphism effects and gradient backgrounds
- Smooth animations and transitions
- Responsive grid layout (1-3 columns based on viewport)

### 2. Skill Management
- **Enable/Disable Skills**: Toggle skills per project
- **Favorite System**: Mark frequently-used skills as favorites (cross-project)
- **Custom Skills**: Create custom skills with Claude integration
- **Edit Skills**: Edit custom skill content via Monaco editor
- **Delete Skills**: Remove custom skills (with confirmation)

### 3. Organization
- **Tabs**: Separate views for All, Enabled, Custom, and Favorites
- **Categorization**: Skills organized by category (Project, Managed, Development, Testing, Documentation)
- **Badge System**: Visual indicators for custom skills and favorites

## Component Structure

### Props

None - uses React Context for project selection

### State Management

```typescript
interface Skill {
  id: number;
  name: string;
  description: string;
  skill_type: 'default' | 'custom';
  category: string;
  file_path?: string;
  is_enabled: boolean;
  is_favorite: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface SkillsResponse {
  enabled: Skill[];
  available_default: Skill[];
  custom: Skill[];
  favorites: Skill[];
}
```

**State Variables:**
- `activeTab`: Current tab index (0-3)
- `skills`: SkillsResponse object with categorized skills
- `loading`: Loading state during API calls
- `error`: Error message display
- `createDialogOpen`: Create new skill dialog visibility
- `newSkillName`: Name for new skill
- `newSkillDescription`: Description for new skill
- `creating`: Creation in progress state
- `editDialogOpen`: Edit skill dialog visibility
- `editingSkill`: Currently editing skill object

### Context Dependencies

- `ProjectContext`: Accesses `selectedProject` for project-specific operations

## Design System

### Color Palette

#### Category Colors
- **Project**: Primary blue (`theme.palette.primary.main`)
- **Managed**: Secondary purple (`theme.palette.secondary.main`)
- **Development**: Info blue (`theme.palette.info.main`)
- **Testing**: Success green (`theme.palette.success.main`)
- **Documentation**: Warning yellow (`theme.palette.warning.main`)

#### Gradients
- **Primary Gradient**: `linear-gradient(135deg, primary.main, primary.dark)`
- **Category Gradient**: `linear-gradient(135deg, alpha(color, 0.15), alpha(color, 0.05))`
- **Tab Indicator**: `linear-gradient(90deg, primary.main, secondary.main)`
- **Background**: Multi-layer radial and linear gradients

#### Shadows
- **Card Default**: `0 4px 16px rgba(0,0,0,0.04)`
- **Card Hover**: `0 12px 40px rgba(primary, 0.15)`
- **Button**: `0 6px 20px rgba(primary, 0.4)`
- **Favorite Badge**: Enhanced shadow with warning color

### Typography

- **Skill Name**: 1.25rem, weight 700, letter-spacing -0.02em
- **Category**: 0.75rem, weight 600, uppercase
- **Description**: 0.95rem, line-height 1.8
- **Header Title**: 2.5rem (h3 variant)
- **Tab Labels**: 1rem, weight 700

### Spacing

- **Card Border Radius**: 16px (4)
- **Card Padding**: 24px (3)
- **Grid Spacing**: 24px (3)
- **Section Margins**: 32px (4)

## Animations

### Card Hover Effect
```css
transform: translateY(-8px) scale(1.01)
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)
box-shadow: 0 12px 40px rgba(primary, 0.15)
```

### Enter Animation (fadeInUp)
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
animation: fadeInUp 0.4s ease-out
```

### Interactive Elements
- **Icon Buttons**: `scale(1.1) rotate(5deg)` on hover
- **Tabs**: Background highlight + lift effect
- **Chips**: Scale effect on hover
- **Favorite Badge**: Pulse animation

## API Integration

### Endpoints Used

#### Get Skills
```typescript
GET /api/projects/{projectId}/skills/
Response: SkillsResponse
```

#### Enable Skill
```typescript
POST /api/projects/{projectId}/skills/enable/{skillId}
Response: { message: string }
```

#### Disable Skill
```typescript
POST /api/projects/{projectId}/skills/disable/{skillId}
Response: { message: string }
```

#### Toggle Favorite
```typescript
POST /api/projects/{projectId}/skills/toggle-favorite/{skillId}
Response: { message: string }
```

#### Create Custom Skill
```typescript
POST /api/projects/{projectId}/skills/custom
Body: { name: string, description: string }
Response: Skill
```

#### Delete Skill
```typescript
DELETE /api/projects/{projectId}/skills/{skillId}
Response: { message: string }
```

#### Get Skill Content
```typescript
GET /api/editor/skill-content/{projectId}?skill_name={name}
Response: string (Markdown content)
```

#### Update Skill Content
```typescript
PUT /api/editor/skill-content/{projectId}
Body: { skill_name: string, content: string }
Response: { message: string }
```

## Usage Example

```tsx
import Skills from './pages/Skills';

// In App.tsx or Router
<Route path="/skills" element={<Skills />} />
```

The component automatically:
1. Fetches skills when project is selected
2. Categorizes skills into tabs
3. Handles all skill operations (enable, favorite, create, edit, delete)
4. Updates UI optimistically with API confirmation

## Key Functions

### fetchSkills()
Retrieves all skills for the selected project and categorizes them.

### handleToggleSkill(skillId, isEnabled)
Enables or disables a skill for the project.

### handleToggleFavorite(skillId)
Toggles favorite status for a skill (cross-project).

### handleCreateSkill()
Creates a new custom skill via Claude integration.

### handleDeleteSkill(skillId)
Deletes a custom skill with confirmation.

### handleEditSkill(skill)
Opens Monaco editor dialog to edit custom skill content.

### handleTabChange(newValue)
Switches between tabs (All, Enabled, Custom, Favorites).

## Accessibility

- High contrast ratios (WCAG AA compliant)
- Keyboard navigation support
- Proper ARIA labels in tooltips
- Screen reader friendly structure
- Focus indicators on interactive elements
- Minimum touch target size: 36x36px

## Responsive Design

### Breakpoints
- **Mobile (xs)**: Single column, full-width cards
- **Tablet (md)**: 2-column grid
- **Desktop (lg+)**: 3-column grid

### Adaptive Features
- Fluid typography scales with viewport
- Spacing adjusts for smaller screens
- Touch-optimized for mobile devices
- Stacked dialogs on mobile

## Empty States

Each tab has custom empty state messaging:

- **All/Enabled**: "No skills available" with info about creating custom skills
- **Custom**: "No custom skills yet" with call-to-action to create
- **Favorites**: "No favorites yet" with instructions to star skills

## Loading State

Custom loading indicator with:
- Circular progress spinner
- Branded color scheme
- "Loading Skills..." text
- Centered layout

## Error Handling

- API errors displayed in Alert component
- Non-intrusive error messages
- Auto-retry on network failures
- Graceful fallbacks

## Performance Optimizations

- GPU-accelerated CSS animations
- Optimized React re-renders
- Efficient gradient rendering
- Smooth 60fps transitions
- Backdrop blur with hardware acceleration

## Browser Compatibility

- Chrome/Edge (latest) ✓
- Firefox (latest) ✓
- Safari (latest) ✓
- WebKit background support
- Backdrop filters with fallbacks

## Related Components

- [CodeEditorDialog](./CodeEditorDialog.md) - Monaco editor for skill content
- [ProjectContext](../architecture/context-management.md) - Project selection context

## Future Enhancements

- Dark mode optimization
- Custom theme support
- Drag-and-drop reordering
- Skill groups/collections
- Advanced filtering
- Search functionality
- Skill templates
- Import/export skills

---

**Design Philosophy**: Clean, modern, professional SaaS aesthetic with excellent user experience and accessibility.

Last updated: 2025-11-14
