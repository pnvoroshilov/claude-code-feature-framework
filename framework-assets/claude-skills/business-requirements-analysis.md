---
name: business-requirements-analysis
description: Analyzes stakeholder needs and creates comprehensive business requirements documents with user stories, acceptance criteria, and success metrics
version: 1.0.0
tags: [analysis, requirements, business, documentation, agile]
---

# Business Requirements Analysis Skill

Comprehensive business requirements analysis that transforms stakeholder needs into actionable, well-documented requirements with clear success criteria and acceptance tests.

## Capabilities

This skill provides expert-level business analysis including:
- **Stakeholder Analysis**: Identify key stakeholders, their roles, needs, and influence
- **Requirements Elicitation**: Extract and document business, functional, and non-functional requirements
- **User Story Creation**: Generate well-formed user stories with personas, scenarios, and acceptance criteria
- **Process Mapping**: Document current state (AS-IS) and future state (TO-BE) business processes
- **Success Metrics**: Define measurable KPIs and success criteria for requirements
- **Risk Assessment**: Identify business risks, assumptions, and constraints
- **Priority Matrix**: Categorize requirements using MoSCoW or other prioritization frameworks
- **Traceability Matrix**: Link requirements to business objectives and stakeholder needs

## How to Use

### Basic Usage
1. **Provide Context**: Share information about the project, problem, or opportunity
2. **Identify Stakeholders**: List who will be affected by or can influence the solution
3. **Describe Goals**: Explain what business outcomes are desired
4. **Request Analysis**: Ask for specific analysis outputs (user stories, process maps, etc.)

### Advanced Usage
- **Iterative Refinement**: Review initial requirements and request clarifications or expansions
- **Scenario Analysis**: Explore edge cases and exception scenarios
- **Acceptance Testing**: Generate detailed acceptance test scenarios
- **Documentation Export**: Create formatted requirements documents ready for stakeholder review

### Integration with Development
Works seamlessly with:
- Technical specification creation
- System architecture design
- Sprint planning and backlog grooming
- Test case generation

## Input Format

Provide information in any of these formats:

### Natural Language Description
```
"We need to improve our customer onboarding process. Currently, it takes
5 days and involves manual steps. We want to reduce it to 1 day with
automation."
```

### Structured Input
```yaml
Project: Customer Onboarding Improvement
Stakeholders:
  - Sales team (end users)
  - New customers (beneficiaries)
  - IT operations (implementers)
Goals:
  - Reduce onboarding time from 5 days to 1 day
  - Eliminate manual data entry
  - Improve customer satisfaction
Constraints:
  - Budget: $50,000
  - Timeline: 3 months
  - Must integrate with existing CRM
```

### Document Upload
- Existing requirements documents
- Stakeholder interview notes
- Process documentation
- Business case or project charter

## Output Format

### Standard Requirements Document Structure

#### 1. Executive Summary
- Project overview
- Business objectives
- Key stakeholders
- Success criteria

#### 2. Stakeholder Analysis
```markdown
| Stakeholder | Role | Interest | Influence | Needs |
|-------------|------|----------|-----------|-------|
| Sales Team | End User | High | High | Fast, reliable process |
| Customers | Beneficiary | High | Medium | Smooth onboarding |
| IT Ops | Implementer | Medium | High | Maintainable system |
```

#### 3. Business Requirements
```markdown
BR-001: The system shall reduce customer onboarding time
- Current State: 5 business days average
- Target State: 1 business day maximum
- Success Metric: 95% of onboardings complete within 24 hours
- Priority: Must Have
- Rationale: Competitive pressure and customer feedback
```

#### 4. User Stories
```markdown
As a Sales Representative
I want to submit new customer information in a single form
So that I can complete onboarding faster and reduce errors

Acceptance Criteria:
- [ ] Form captures all required customer data
- [ ] Real-time validation prevents submission errors
- [ ] Automated workflow triggers upon submission
- [ ] Sales rep receives confirmation within 5 minutes
- [ ] Customer receives welcome email within 1 hour

Technical Notes:
- Integration with CRM API required
- Email service for notifications
- Data validation rules: email format, phone format, required fields

Business Value: High (reduces processing time by 80%)
Story Points: 5
Priority: Must Have
```

#### 5. Process Flow
```
AS-IS Process:
1. Sales rep emails customer info to ops → 1 day
2. Ops manually enters data into CRM → 2 days
3. Ops creates customer accounts → 1 day
4. Ops sends welcome email → 1 day
Total: 5 days, 4 handoffs, high error rate

TO-BE Process:
1. Sales rep submits form → automated → 5 minutes
2. System creates CRM record → automated → immediate
3. System provisions accounts → automated → 15 minutes
4. System sends welcome email → automated → immediate
Total: <1 hour, 0 handoffs, validated data
```

#### 6. Non-Functional Requirements
```markdown
NFR-001 Performance: System shall process onboarding requests within 30 minutes
NFR-002 Availability: System shall maintain 99.9% uptime during business hours
NFR-003 Security: All customer data shall be encrypted in transit and at rest
NFR-004 Usability: Sales reps shall complete form training in < 15 minutes
NFR-005 Scalability: System shall support 1000 concurrent onboardings
```

#### 7. Success Metrics & KPIs
```markdown
| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| Onboarding Time | 5 days | 1 day | Timestamp analysis |
| Error Rate | 15% | <2% | Validation reports |
| Sales Rep Satisfaction | 3.2/5 | 4.5/5 | Quarterly survey |
| Customer NPS | 45 | 70 | Post-onboarding survey |
| Processing Cost | $50/customer | $10/customer | Finance reports |
```

## Example Usage

### Example 1: Simple Feature Request
**User Prompt**:
> "We need to add a 'Continue' button to task cards so users can resume work on tasks"

**Output**:
```markdown
# Business Requirements: Task Continuation Feature

## Executive Summary
Enable users to quickly resume in-progress tasks through a dedicated "Continue"
button on task cards, reducing friction in workflow resumption.

## User Story
As a task coordinator
I want to see a "Continue" button on in-progress task cards
So that I can quickly resume work without navigating through multiple screens

Acceptance Criteria:
- [ ] "Continue" button appears on task cards with status "In Progress"
- [ ] Button is not shown on tasks with status "Done" or "Backlog"
- [ ] Clicking button navigates to task detail page
- [ ] Button has clear visual hierarchy (secondary action styling)
- [ ] Keyboard shortcut available (Ctrl/Cmd + Enter when card focused)

## Success Metrics
- 40% reduction in time-to-resume for in-progress tasks
- 80% of users use Continue button vs manual navigation
- User satisfaction score increases by 15%

## Technical Considerations
- Frontend: React component modification in TaskCard
- State management: Check task.status property
- Routing: Navigate to /tasks/:id
- Accessibility: ARIA label, keyboard support
```

### Example 2: Complex Business Process
**User Prompt**:
> "Analyze requirements for an automated invoice processing system that needs to
> handle vendor invoices, match them to purchase orders, and route for approval"

**Output**:
```markdown
# Business Requirements: Automated Invoice Processing System

## Executive Summary
Implement an intelligent invoice processing system that automates vendor invoice
handling, PO matching, and approval routing to reduce processing time from
7 days to 1 day and eliminate 90% of manual data entry.

## Stakeholder Analysis
[Detailed stakeholder matrix with AP team, vendors, approvers, finance, IT]

## Business Requirements
BR-001: System shall automatically extract invoice data from PDF and email
BR-002: System shall match invoices to existing purchase orders (2-way match)
BR-003: System shall route for approval based on amount thresholds
BR-004: System shall integrate with accounting system for payment processing
BR-005: System shall provide real-time status tracking and reporting

## User Stories
[10-15 detailed user stories for invoice submission, matching, approval,
payment, exception handling, reporting]

## Process Flows
[AS-IS vs TO-BE process diagrams with timing and handoff analysis]

## Non-Functional Requirements
[Performance, security, audit, compliance requirements]

## Success Metrics
[Detailed KPI dashboard with baselines and targets]

## Risk Assessment
[Technology risks, change management risks, integration risks with mitigation]
```

### Example 3: Requirements Refinement
**User Prompt**:
> "Review these user stories and add missing acceptance criteria: [paste stories]"

**Output**:
```markdown
# Requirements Review and Enhancement

## Analysis Summary
Reviewed 5 user stories. Found:
- 3 stories missing testable acceptance criteria
- 2 stories with unclear success metrics
- 1 story needing decomposition (too large)

## Enhanced Stories

[Original Story 1]
Issues: Acceptance criteria too vague, no error handling scenarios

[Enhanced Version]
As a [persona]
I want to [action]
So that [benefit]

Acceptance Criteria:
✅ Happy Path: [specific testable criteria]
✅ Edge Cases: [boundary conditions]
✅ Error Handling: [exception scenarios]
✅ Performance: [response time requirements]
✅ Security: [access control requirements]

Definition of Done:
- [ ] Code implemented and peer reviewed
- [ ] Unit tests with 90%+ coverage
- [ ] Integration tests pass
- [ ] UAT completed by product owner
- [ ] Documentation updated
```

## Best Practices

### 1. SMART Requirements
Ensure all requirements are:
- **Specific**: Clear and unambiguous
- **Measurable**: Can verify when complete
- **Achievable**: Realistic given constraints
- **Relevant**: Tied to business objectives
- **Time-bound**: Have delivery expectations

### 2. User Story Quality
Follow the INVEST criteria:
- **Independent**: Can be developed separately
- **Negotiable**: Details can be refined
- **Valuable**: Delivers business value
- **Estimable**: Team can size the work
- **Small**: Can be completed in one sprint
- **Testable**: Has clear acceptance criteria

### 3. Stakeholder Engagement
- Identify all affected parties early
- Document needs from multiple perspectives
- Prioritize conflicting requirements transparently
- Maintain traceability to stakeholder needs
- Review requirements with stakeholders regularly

### 4. Requirements Traceability
Link every requirement to:
- Business objective or goal
- Stakeholder need
- System capability
- Test case
- Implementation component

### 5. Progressive Elaboration
Start high-level and refine iteratively:
1. Epic: Large business capability
2. Feature: Coherent functionality
3. User Story: Implementable work item
4. Task: Technical implementation detail

### 6. Non-Functional Requirements
Don't forget the "ilities":
- Usability, Accessibility
- Reliability, Availability
- Performance, Scalability
- Security, Compliance
- Maintainability, Testability

## Limitations

This skill focuses on business analysis and documentation. It does **not**:
- Generate technical specifications (use `technical-specification` skill)
- Create system architecture designs (use `system-architecture` skill)
- Write actual code implementation (use development skills)
- Perform market research or competitive analysis
- Make final business decisions (provides analysis to inform decisions)

## Troubleshooting

### Issue: Requirements too vague
**Symptoms**: Acceptance criteria unclear, implementation ambiguous
**Solution**: Ask follow-up questions:
- "What does success look like specifically?"
- "How will we measure if this requirement is met?"
- "What are the boundary conditions?"

### Issue: Conflicting stakeholder needs
**Symptoms**: Requirements that contradict each other
**Solution**:
1. Document both perspectives
2. Identify the root conflict
3. Propose prioritization criteria
4. Escalate to decision maker with analysis

### Issue: Scope creep during analysis
**Symptoms**: Requirements list keeps growing
**Solution**:
1. Use MoSCoW prioritization (Must/Should/Could/Won't)
2. Define clear project boundaries
3. Create backlog for future enhancements
4. Link each requirement to core objectives

### Issue: Missing technical constraints
**Symptoms**: Requirements don't account for system limitations
**Solution**:
1. Collaborate with technical stakeholders early
2. Identify integration points and dependencies
3. Document technical assumptions
4. Include non-functional requirements

## Related Skills

Works best in combination with:
- `technical-specification`: Translate business requirements to technical specs
- `system-architecture`: Design system to meet requirements
- `test-case-generation`: Create test scenarios from acceptance criteria
- `project-planning`: Estimate effort and create implementation roadmap
- `stakeholder-communication`: Create presentations and status reports

## Workflow Integration

### Typical Requirements Analysis Workflow
1. **Discovery**: Use this skill to analyze stakeholder needs
2. **Documentation**: Generate requirements document
3. **Technical Design**: Pass to `technical-specification` skill
4. **Architecture**: Pass to `system-architecture` skill
5. **Planning**: Use for sprint planning and estimation
6. **Testing**: Generate test cases from acceptance criteria
7. **Validation**: Review with stakeholders and refine

### Agile Integration
- **Product Backlog**: Generate and prioritize user stories
- **Sprint Planning**: Provide detailed acceptance criteria
- **Refinement**: Elaborate stories before sprint
- **Review**: Validate against acceptance criteria
- **Retrospective**: Analyze requirements quality metrics

## Templates and Frameworks

### Requirements Document Template
Provides structured templates for:
- Business Requirements Document (BRD)
- Functional Requirements Specification (FRS)
- Product Requirements Document (PRD)
- Software Requirements Specification (SRS)
- User Stories and Epics

### Prioritization Frameworks
- **MoSCoW**: Must/Should/Could/Won't have
- **RICE**: Reach, Impact, Confidence, Effort
- **Kano Model**: Basic, Performance, Delight features
- **Value vs Effort Matrix**: Quick wins, major projects, fill-ins, thankless tasks

### Analysis Techniques
- **5 Whys**: Root cause analysis
- **SWOT**: Strengths, Weaknesses, Opportunities, Threats
- **Force Field**: Driving and restraining forces
- **Decision Matrix**: Multi-criteria decision analysis

## Version History

- **1.0.0** (2025-01-30): Initial release with core business analysis capabilities
  - Stakeholder analysis
  - User story generation
  - Process mapping
  - Success metrics definition
  - Requirements documentation templates
