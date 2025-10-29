# Business Requirements Analysis Skill

## Purpose
This skill helps analyze business requirements, stakeholder needs, and translate them into actionable user stories with acceptance criteria.

## Capabilities
- **Stakeholder Analysis**: Identify and analyze key stakeholders and their needs
- **User Story Creation**: Write effective user stories (As a [role], I want [feature], So that [benefit])
- **Acceptance Criteria**: Define clear, testable acceptance criteria (Given/When/Then format)
- **Business Value Assessment**: Evaluate and prioritize features based on business value
- **Feature Prioritization**: Apply prioritization frameworks (MoSCoW, Value vs Effort)

## When to Use
- Starting a new feature or project
- Breaking down high-level requirements into implementable stories
- Clarifying ambiguous or incomplete requirements
- Aligning technical work with business objectives
- Prioritizing backlog items

## Usage Guidelines

### 1. Stakeholder Analysis
Identify who will be affected by and benefit from the feature:
- Primary users (who will use it directly)
- Secondary stakeholders (who will be impacted)
- Business owners (who requested it)
- Technical stakeholders (who will build/maintain it)

### 2. User Story Template
```
As a [specific role/persona],
I want to [perform specific action],
So that [achieve specific benefit].
```

### 3. Acceptance Criteria (Given/When/Then)
```
Given [initial context/precondition]
When [action is performed]
Then [expected result]
And [additional expected results]
```

## Example Output

**Feature Request**: "We need a task board for the project"

**Analysis**:

### Stakeholders
- **Primary Users**: Project managers, team leads
- **Secondary Users**: Individual contributors, executives
- **Business Owner**: Product Management
- **Technical Owner**: Engineering Team

### User Story
```
As a project manager,
I want to view all tasks in a Kanban board,
So that I can track project progress visually and identify bottlenecks quickly.
```

### Acceptance Criteria
```
Given I am logged in as a project manager
When I navigate to the task board page
Then I see columns for each task status (Backlog, In Progress, Testing, Done)
And I see task cards in their respective columns
And each task card displays title, priority, and assignee
And I can drag and drop tasks between columns to update their status
And the changes are persisted to the database
And other users see the updated board in real-time
```

### Business Value
- **High Priority**: Core feature for MVP
- **Business Impact**: Improves team productivity by 30% (estimated)
- **User Impact**: Affects all project managers daily
- **Revenue Impact**: Enables enterprise sales (required feature)

### Success Metrics
- 80% of project managers use task board daily
- Average time to check project status reduced by 50%
- Task status updates increase by 40%
- User satisfaction score > 4.5/5

### Risks & Considerations
- **Technical Risk**: Real-time updates may have performance impact
- **UX Risk**: Drag-and-drop may not work well on mobile devices
- **Business Risk**: Users may resist change from current process

## Best Practices

### Do's ✅
- Write user stories from the user's perspective, not the system's
- Make acceptance criteria specific and testable
- Include both positive and negative test cases
- Consider edge cases and error scenarios
- Validate with actual users when possible
- Keep stories small and focused (completable in one sprint)
- Include non-functional requirements (performance, security, accessibility)

### Don'ts ❌
- Don't make stories too large or vague
- Don't skip the "So that" part (business value is critical)
- Don't write technical implementation details in user stories
- Don't forget about error handling and edge cases
- Don't ignore non-functional requirements
- Don't prioritize without considering dependencies

## Integration with Development Process

### Phase 1: Discovery
- Gather requirements from stakeholders
- Document business objectives
- Identify constraints and assumptions

### Phase 2: Analysis
- Create user stories with acceptance criteria
- Assess business value and impact
- Identify technical dependencies
- Estimate effort (rough)

### Phase 3: Refinement
- Review stories with development team
- Clarify technical questions
- Update estimates
- Split large stories if needed

### Phase 4: Development
- Stories guide implementation
- Acceptance criteria used for testing
- Business value tracked throughout

## Related Skills
- **System Architecture Design**: For technical feasibility analysis
- **Quality Assurance Review**: For acceptance criteria validation
- **Product Roadmap Planning**: For prioritization context
- **UI/UX Design Validation**: For user-centered design alignment
