---
name: technical-design
description: Comprehensive document formats and templates for technical architecture design test cases and conflict analysis
version: 2.0.0
tags: [architecture, design, technical-requirements, test-cases, conflict-analysis, adr, integration]
---

# Technical Design Skill

**Expert guidance for creating comprehensive technical design documentation including requirements, architecture decisions, test cases, and conflict analysis.**

## Overview

This skill provides structured templates and best practices for:

skill_capabilities[8]{capability,description,use_case}:
Technical Requirements,Detailed what/where/why for changes,Planning implementation with precision
Architecture Decisions,ADR format for design choices,Documenting rationale and trade-offs
Test Case Design,UI backend integration and error test cases,Comprehensive testing strategy
Conflict Analysis,Identify task overlaps and integration points,Prevent merge conflicts and coordination issues
Database Design,Schema changes and migration plans,Data modeling and evolution
API Specifications,Endpoint design and integration,Backend service contracts
Component Design,Frontend and backend component structure,Code organization planning
Risk Assessment,Identify and mitigate project risks,Proactive risk management

## When to Use This Skill

**Trigger Scenarios:**

trigger_scenarios[12]{scenario,skill_application}:
User requests technical requirements,Create comprehensive technical requirements document
User needs architecture decision documentation,Write ADR with context options and rationale
User asks for test cases,Design UI backend integration and error test cases
User mentions task conflicts,Analyze active tasks for overlaps and conflicts
User designs database schema,Document schema changes with migration plan
User creates API endpoint,Specify endpoint design with request/response
User plans component changes,Detail component structure and integration
User needs risk analysis,Identify risks with probability impact mitigation
User asks about integration points,Document internal and external integrations
User mentions dependencies,Map technical and task dependencies
User refactors architecture,Document decisions and migration strategy
User plans implementation,Create complete what/where/why documentation

## Quick Reference

### Document Types

document_types[6]{type,purpose,key_sections}:
Technical Requirements,Implementation planning,Overview What Where Why Integration Conflicts
Architecture Decision Record (ADR),Design rationale documentation,Context Options Decision Consequences
Test Cases,Quality assurance planning,UI Backend Integration Error scenarios
Conflict Analysis,Coordination and risk mitigation,Active tasks overlap mitigation
Integration Specification,System boundaries and contracts,Internal services External APIs Shared components
Risk Assessment,Proactive problem identification,Risks probability impact mitigation

### Quality Criteria

quality_criteria[8]{criterion,requirement,benefit}:
Precision,Use exact file paths and function names,No ambiguity in implementation
Justification,Explain why for every change,Clear rationale for decisions
Impact Analysis,Consider effects on other components,Prevent unexpected side effects
Testability,Include comprehensive test cases,Quality assurance coverage
Risk Awareness,Identify potential problems early,Proactive mitigation
Conflict Detection,Analyze overlaps with other tasks,Coordination and merge safety
Integration Clarity,Document all integration points,Clear system boundaries
Decision Transparency,Record architectural decisions with rationale,Future maintainability

## Documentation Templates

### 1. Technical Requirements Document

**Purpose:** Comprehensive implementation planning with what/where/why structure

**Template Structure:**

```markdown
## Technical Requirements: [Task Title]

### Overview
[High-level technical approach and goals]

### What to Change

#### Frontend Changes
- **Component:** [Component name and path]
  - **What:** [What needs to change]
  - **Why:** [Reason for change]
  - **Impact:** [Effect on other components]

- **Component:** [Another component]
  - **What:** [Details...]
  - **Why:** [Justification...]
  - **Impact:** [Effects...]

#### Backend Changes
- **Service:** [Service name and path]
  - **What:** [What needs to change]
  - **Why:** [Reason for change]
  - **Impact:** [Effect on other services]

- **API Endpoint:** [Method] /path/to/endpoint
  - **What:** [New/modified endpoint]
  - **Why:** [Purpose]
  - **Impact:** [Integration points]

#### Database Changes
- **Table:** [Table name]
  - **What:** [Schema changes (add column, modify constraint, etc.)]
  - **Migration:** [Migration approach (ALTER TABLE, data backfill, etc.)]
  - **Impact:** [Affected queries, data integrity, performance]

### Where to Change

#### File Structure
```
[Project root]/
├── frontend/
│   ├── components/
│   │   └── [ComponentName].tsx  ← [Modify/Create]
│   ├── services/
│   │   └── [ServiceName].ts  ← [Create new]
│   └── types/
│       └── [TypeName].ts  ← [Add types]
├── backend/
│   ├── api/
│   │   └── [endpoint].py  ← [Modify]
│   ├── services/
│   │   └── [service].py  ← [Create new]
│   └── models/
│       └── [model].py  ← [Add model]
└── migrations/
    └── [timestamp]_[description].sql  ← [Create migration]
```

### Why These Changes

#### Business Justification
[Why from business perspective: user value, feature requirements, business rules]

#### Technical Justification
[Why from technical perspective: maintainability, performance, scalability, security]

#### Architecture Alignment
[How changes align with existing architecture patterns and principles]

### Integration Points

#### Internal Services
- **[Service 1]:** [How it integrates, what data flows, dependencies]
- **[Service 2]:** [Integration details...]

#### External APIs
- **[API 1]:** [Endpoint, authentication, data format, error handling]
- **[API 2]:** [Integration details...]

#### Shared Components
- **[Component 1]:** [Shared with which features/tasks, potential conflicts]
- **[Component 2]:** [Usage and dependencies...]

### Conflict Analysis

#### Active Tasks Analysis
**Other Active Tasks:**

- **Task #[ID]: [Title]**
  - **Overlap:** [Shared components, files, or database tables]
  - **Conflict Risk:** [High/Medium/Low]
  - **Mitigation:** [How to avoid conflicts: communication, merge order, etc.]

- **Task #[ID]: [Title]**
  - **Overlap:** [Details...]
  - **Conflict Risk:** [Level]
  - **Mitigation:** [Strategy...]

**Coordination Needed:**
- [What needs coordination between teams/tasks]
- [Communication plan and checkpoints]

### Architecture Decisions

#### Decision 1: [Name]
- **Context:** [Situation requiring a decision]
- **Options Considered:**
  - Option A: [Description, pros, cons]
  - Option B: [Description, pros, cons]
  - Option C: [Description, pros, cons]
- **Decision:** [What was chosen]
- **Rationale:** [Why this option was selected]
- **Consequences:** [Trade-offs, technical debt, future implications]

#### Decision 2: [Name]
[Same structure...]

### Dependencies

#### Technical Dependencies
- **[Library/Framework]:** [Version, purpose, installation]
- **[Service]:** [Why needed, how it's used]
- **[Tool]:** [Purpose and configuration]

#### Task Dependencies
- **Must complete before:** [Task IDs and why]
- **Must complete after:** [Task IDs and why]
- **Can run in parallel with:** [Task IDs]
- **Blocks:** [Task IDs that depend on this]

### Risks and Mitigation

#### Risk 1: [Description]
- **Probability:** [High/Medium/Low]
- **Impact:** [High/Medium/Low]
- **Mitigation:** [How to address or prevent]
- **Contingency:** [Backup plan if risk occurs]

#### Risk 2: [Description]
[Same structure...]

### Implementation Checklist

- [ ] All file paths verified and exist (or creation planned)
- [ ] Database migrations tested on copy of production data
- [ ] API contracts reviewed with dependent teams
- [ ] Integration points documented and validated
- [ ] Conflict analysis completed with active tasks
- [ ] Architecture decisions recorded
- [ ] Risks identified with mitigation plans
- [ ] Test cases defined (see Test Cases section)
```

### 2. Test Cases Document

**Purpose:** Comprehensive testing strategy covering all scenarios

**Template Structure:**

```markdown
## Test Cases: [Task Title]

### Overview
[Brief description of what needs testing and testing approach]

### UI Test Cases

#### TC-UI-01: [Test Case Name]
**Objective:** [What to test and why]

**Preconditions:**
- [Condition 1: user logged in, data exists, etc.]
- [Condition 2: specific state or configuration]

**Test Steps:**
1. [Action 1: Navigate to page, click button, etc.]
2. [Action 2: Enter data, select option, etc.]
3. [Action 3: Submit form, verify result, etc.]

**Expected Results:**
- [Expected behavior 1: UI updates correctly]
- [Expected behavior 2: Data displayed accurately]
- [Expected behavior 3: No errors shown]

**Priority:** [High/Medium/Low]

**Test Data:**
- [Specific data values to use]

#### TC-UI-02: [Test Case Name]
[Same structure...]

### Backend Test Cases

#### TC-BE-01: [Test Case Name]
**Objective:** [What to test: business logic, data validation, etc.]

**API Endpoint:** [Method] /path/to/endpoint

**Request Headers:**
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {token}"
}
```

**Request Body:**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "field": "value"
  }
}
```

**Expected Status Code:** 200

**Validations:**
- [ ] Business logic executed correctly
- [ ] Data persisted to database properly
- [ ] Side effects handled (notifications, logs, etc.)
- [ ] Response format matches specification
- [ ] Related data updated correctly

**Priority:** [High/Medium/Low]

**Test Database State:**
- Before: [Initial database state]
- After: [Expected database state]

#### TC-BE-02: [Test Case Name]
[Same structure...]

### Integration Test Cases

#### TC-INT-01: [End-to-End Flow Name]
**Scenario:** [Complete user journey from start to finish]

**Flow Steps:**
1. **Frontend:** [User action] → **API Call:** [Method] /endpoint
2. **Backend:** [Processing: validation, business logic] → **Database:** [Update/query]
3. **Backend:** [Response creation] → **Frontend:** [UI update]
4. **Frontend:** [Final state displayed to user]

**Expected Outcome:** [What user sees and experiences]

**Validation Points:**
- [ ] UI reflects data accurately
- [ ] Database state is correct
- [ ] All integrations work smoothly
- [ ] Performance is acceptable

**Priority:** [High/Medium/Low]

#### TC-INT-02: [Another End-to-End Flow]
[Same structure...]

### Edge Cases and Error Scenarios

#### TC-ERR-01: [Error Case Name]
**Scenario:** [What goes wrong: invalid input, network error, etc.]

**Trigger:**
[How to reproduce the error]

**Expected Behavior:**
- **Backend:** [Error handling: log, return error code]
- **Frontend:** [Error display: message, fallback UI]
- **User Experience:** [What user sees and can do]

**Recovery:**
[How user can recover from error]

**Priority:** [High/Medium/Low]

#### TC-ERR-02: [Another Error Case]
[Same structure...]

#### TC-EDG-01: [Edge Case Name]
**Scenario:** [Boundary condition: empty list, max value, etc.]

**Test Setup:**
[How to create edge case scenario]

**Expected Behavior:**
[How system handles edge case gracefully]

**Priority:** [Medium/Low]

### Performance Test Cases

#### TC-PERF-01: [Performance Test Name]
**Objective:** [What to measure: response time, throughput, etc.]

**Load:**
[Number of users, requests per second, data volume]

**Success Criteria:**
- Response time < [X]ms
- Throughput > [Y] requests/second
- No errors under load

**Priority:** [Medium/Low]

### Security Test Cases

#### TC-SEC-01: [Security Test Name]
**Objective:** [What to verify: authentication, authorization, input validation]

**Attack Scenario:**
[What malicious action to test against]

**Expected Behavior:**
[How system prevents or handles attack]

**Priority:** [High/Medium]

### Test Execution Summary

test_categories[7]{category,count,priority_distribution}:
UI Tests,[N] tests,[X] High [Y] Medium [Z] Low
Backend Tests,[N] tests,[X] High [Y] Medium [Z] Low
Integration Tests,[N] tests,[X] High [Y] Medium [Z] Low
Error Scenarios,[N] tests,[X] High [Y] Medium [Z] Low
Edge Cases,[N] tests,[X] High [Y] Medium [Z] Low
Performance Tests,[N] tests,[X] High [Y] Medium [Z] Low
Security Tests,[N] tests,[X] High [Y] Medium [Z] Low

**Total Test Cases:** [Total]
**High Priority:** [Count]
**Estimated Testing Time:** [Hours]
```

### 3. Architecture Decision Record (ADR)

**Purpose:** Document significant architectural decisions with full context

**Template Structure:**

```markdown
## ADR-[Number]: [Decision Title]

**Status:** [Proposed/Accepted/Deprecated/Superseded]
**Date:** [YYYY-MM-DD]
**Deciders:** [Names/roles of decision makers]

### Context

[Describe the issue or situation requiring a decision. Include:]
- Current architecture or approach
- Problem or limitation faced
- Business or technical drivers
- Constraints (time, resources, technology)
- Stakeholder concerns

### Decision Drivers

- [Driver 1: performance requirement]
- [Driver 2: maintainability concern]
- [Driver 3: cost constraint]
- [Driver 4: team expertise]

### Options Considered

#### Option 1: [Name]

**Description:**
[Detailed explanation of this approach]

**Pros:**
- [Advantage 1]
- [Advantage 2]
- [Advantage 3]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]
- [Disadvantage 3]

**Cost/Effort:** [High/Medium/Low]

#### Option 2: [Name]

**Description:**
[Detailed explanation]

**Pros:**
- [Advantages...]

**Cons:**
- [Disadvantages...]

**Cost/Effort:** [Level]

#### Option 3: [Name]

[Same structure...]

### Decision

[Chosen option with clear statement: "We will..."]

### Rationale

[Detailed explanation of why this option was chosen:]
- Why it best addresses decision drivers
- How it compares to alternatives
- What makes it the optimal choice
- How it aligns with architecture principles

### Consequences

#### Positive Consequences
- [Benefit 1: improved performance]
- [Benefit 2: better maintainability]
- [Benefit 3: cost savings]

#### Negative Consequences
- [Trade-off 1: increased complexity]
- [Trade-off 2: technical debt]
- [Trade-off 3: learning curve]

#### Neutral Consequences
- [Change 1: new patterns to learn]
- [Change 2: different tooling]

### Implementation

**Required Changes:**
- [Change 1: update service X]
- [Change 2: refactor component Y]
- [Change 3: add new dependency Z]

**Migration Strategy:**
[How to transition from current to new approach]

**Timeline:**
[Estimated implementation timeline]

### Validation

**Success Criteria:**
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

**Monitoring:**
[How to verify decision is working: metrics, logs, feedback]

### Notes

[Additional context, links to discussions, related ADRs, future considerations]

### Related Decisions

- ADR-[N]: [Related decision]
- Supersedes: ADR-[N]
- Superseded by: ADR-[N]
```

## Best Practices

### Technical Requirements Best Practices

technical_requirements_practices[10]{practice,description,benefit}:
Exact file paths,Use precise paths not vague locations,No ambiguity in implementation
Specific names,Reference actual function/component names,Clear implementation targets
Explain why,Justify every change (business + technical),Understanding rationale
Impact analysis,Consider effects on other components,Prevent unexpected issues
Integration clarity,Document all integration points,Clear system boundaries
Conflict awareness,Analyze overlaps with active tasks,Coordination and safety
Risk identification,Identify potential problems early,Proactive mitigation
Dependency mapping,Map all technical and task dependencies,Clear prerequisites
Architecture alignment,Verify consistency with existing patterns,Maintain coherence
Implementation checklist,Provide verification checklist,Quality assurance

### Test Cases Best Practices

test_cases_practices[10]{practice,description,benefit}:
Clear objectives,State what and why for each test,Purpose-driven testing
Numbered steps,Use sequential step numbers,Easy to follow
Measurable outcomes,Define specific expected results,Objective verification
Happy path coverage,Test normal successful flows,Core functionality validation
Edge case coverage,Test boundary conditions,Robustness verification
Error scenario coverage,Test failure modes,Error handling validation
Integration coverage,Test end-to-end flows,System integration validation
Priority assignment,Mark High/Medium/Low priority,Efficient test execution
Test data specification,Provide specific test data values,Reproducible tests
Execution time estimate,Estimate testing duration,Resource planning

### Architecture Decision Best Practices

adr_practices[10]{practice,description,benefit}:
Document context,Explain situation requiring decision,Future understanding
List alternatives,Consider multiple options,Thorough evaluation
Explain rationale,Justify chosen option,Clear reasoning
Acknowledge trade-offs,Document consequences (positive and negative),Realistic expectations
Status tracking,Mark status (Proposed/Accepted/Deprecated),Lifecycle management
Decision drivers,List factors influencing decision,Priority clarity
Implementation plan,Describe how to implement,Actionable guidance
Success criteria,Define measurable success metrics,Validation approach
Link related ADRs,Reference related decisions,Decision continuity
Update when superseded,Mark as deprecated when replaced,Historical accuracy

### Conflict Analysis Best Practices

conflict_analysis_practices[8]{practice,description,benefit}:
List active tasks,Review all in-progress work,Comprehensive overlap detection
Identify overlaps,Find shared files/components/tables,Conflict awareness
Assess risk level,Rate High/Medium/Low conflict risk,Priority guidance
Define mitigation,Plan how to avoid conflicts,Proactive prevention
Communication plan,Specify coordination needed,Team alignment
Merge strategy,Plan merge order and timing,Smooth integration
Testing coordination,Coordinate testing environments,Resource management
Regular updates,Review conflicts during implementation,Dynamic adaptation

## Usage Workflow

### Creating Technical Requirements

requirements_workflow[8]{step,action,details}:
1. Analyze task,Understand requirements and scope,Review user stories and acceptance criteria
2. Plan changes,Determine what needs to change (frontend backend database),Be specific with file paths and function names
3. Justify changes,Explain why (business and technical),Document rationale clearly
4. Map integration,Identify internal and external integration points,Document all dependencies
5. Analyze conflicts,Review active tasks for overlaps,Assess risk and plan mitigation
6. Document decisions,Record architecture decisions in ADR format,Capture context and alternatives
7. Identify risks,List potential problems with mitigation,Proactive risk management
8. Create checklist,Provide verification checklist,Quality assurance

### Creating Test Cases

test_cases_workflow[8]{step,action,details}:
1. Review requirements,Understand what needs testing,Analyze technical requirements document
2. Identify scenarios,List happy path edge cases errors,Comprehensive coverage planning
3. Design UI tests,Create user interaction test cases,Focus on user experience
4. Design backend tests,Create API and business logic tests,Focus on functionality and data
5. Design integration tests,Create end-to-end flow tests,Focus on system integration
6. Design error tests,Create failure scenario tests,Focus on error handling
7. Prioritize tests,Mark High/Medium/Low priority,Efficient test execution
8. Estimate effort,Calculate testing time needed,Resource planning

### Creating Architecture Decision Records

adr_workflow[8]{step,action,details}:
1. Identify decision,Determine what needs deciding,Significant architectural choice
2. Gather context,Document situation and constraints,Full background information
3. List options,Identify 2-5 viable alternatives,Thorough option generation
4. Analyze options,List pros/cons for each option,Objective evaluation
5. Choose option,Select best option with rationale,Clear decision statement
6. Document consequences,List positive negative neutral consequences,Realistic expectations
7. Plan implementation,Describe migration strategy and timeline,Actionable guidance
8. Define validation,Specify success criteria and monitoring,Measurable outcomes

## Integration with Other Skills

**This skill complements:**

skill_integrations[6]{skill,integration_point,benefit}:
requirements-analysis,Technical requirements follow from user stories,Business to technical translation
architecture-patterns,Architecture decisions apply design principles,Pattern-based decision making
code-review,Test cases guide review verification,Quality assurance alignment
testing,Test cases become actual test implementation,Testing strategy execution
documentation,Technical requirements become implementation docs,Documentation consistency
project-management,Conflict analysis informs task scheduling,Coordination and planning

## Example Scenarios

### Scenario 1: Planning New Feature Implementation

**User Request:** "I need to add user authentication to the application"

**Response Pattern:**

1. **Read context:** Review existing codebase structure
2. **Create Technical Requirements:**
   - Frontend: Login/register components, auth service, protected routes
   - Backend: Auth endpoints, JWT generation, user service
   - Database: Users table, sessions table
   - Integration: Frontend → Backend API → Database
3. **Analyze Conflicts:** Check if any active tasks modify auth-related code
4. **Document Architecture Decisions:**
   - ADR: JWT vs Session-based authentication
   - ADR: Password hashing algorithm (bcrypt vs argon2)
5. **Create Test Cases:**
   - UI: Login form validation, successful/failed login, protected routes
   - Backend: Auth endpoint tests, token generation, token validation
   - Integration: End-to-end login flow
   - Errors: Invalid credentials, expired token, unauthorized access

### Scenario 2: Database Schema Change

**User Request:** "Add support for user roles and permissions"

**Response Pattern:**

1. **Create Technical Requirements:**
   - Database: New `roles` and `permissions` tables, `user_roles` junction table
   - Backend: Role/permission models, authorization middleware
   - Frontend: Role-based UI rendering, permission checks
   - Migration: SQL migration scripts, data backfill strategy
2. **Analyze Risks:**
   - Risk: Data migration failure → Mitigation: Test on production data copy
   - Risk: Performance impact on queries → Mitigation: Add database indexes
3. **Create Test Cases:**
   - Backend: Role assignment, permission checking, authorization middleware
   - Integration: User with role can access feature, user without role denied
   - Errors: Invalid role, missing permissions, authorization failures
4. **Document Architecture Decision:**
   - ADR: RBAC vs ABAC approach
   - Context: Need flexible permission system
   - Decision: RBAC with role hierarchy
   - Rationale: Simpler implementation, sufficient for current needs

### Scenario 3: API Integration

**User Request:** "Integrate with external payment service"

**Response Pattern:**

1. **Create Technical Requirements:**
   - Backend: Payment service client, webhook handlers, transaction models
   - Frontend: Payment form, status display, error handling
   - Integration: External payment API documentation and contracts
2. **Document Integration Points:**
   - External API: Payment service REST API
   - Authentication: API key in headers
   - Webhooks: Payment confirmation callback URL
   - Error handling: Retry logic, timeout handling
3. **Analyze Risks:**
   - Risk: Payment service downtime → Mitigation: Implement retry queue
   - Risk: Webhook security → Mitigation: HMAC signature verification
   - Risk: Data inconsistency → Mitigation: Idempotent webhook handling
4. **Create Test Cases:**
   - Backend: Payment initiation, webhook handling, refund processing
   - Integration: End-to-end payment flow with test API
   - Errors: Payment failure, network timeout, webhook signature validation

### Scenario 4: Large Refactoring

**User Request:** "Refactor monolithic service into microservices"

**Response Pattern:**

1. **Document Architecture Decisions:**
   - ADR: Monolith vs Microservices decomposition
   - Context: Current monolith is difficult to scale and maintain
   - Options: Keep monolith, extract services by domain, extract by functionality
   - Decision: Extract services by domain (DDD approach)
   - Consequences: Increased complexity, better scalability, team autonomy
2. **Create Technical Requirements:**
   - Services: User service, Order service, Payment service, Notification service
   - Communication: REST APIs, message queue for async events
   - Database: Separate database per service
   - Migration: Strangler pattern - gradual migration
3. **Analyze Conflicts:**
   - High risk: Multiple teams working on refactoring
   - Mitigation: Clear service boundaries, API contracts, migration schedule
4. **Identify Risks:**
   - Risk: Data consistency across services → Mitigation: Event sourcing pattern
   - Risk: Distributed transaction complexity → Mitigation: Saga pattern
   - Risk: Increased operational complexity → Mitigation: Kubernetes deployment

## Quality Checklist

**Before completing technical design, verify:**

quality_checks[15]{check,requirement,reference}:
Exact file paths,All file paths are precise and specific,Technical Requirements section
Function/component names,All names reference actual code entities,Technical Requirements section
Why explanations,Every change has business and technical justification,Why These Changes section
Impact analysis,Effects on other components considered,Integration Points section
Integration documented,All integration points identified and documented,Integration Points section
Conflicts analyzed,Active tasks reviewed for overlaps,Conflict Analysis section
Risks identified,Potential problems identified with mitigation,Risks and Mitigation section
Dependencies mapped,Technical and task dependencies documented,Dependencies section
Architecture decisions,Significant decisions recorded in ADR format,Architecture Decisions section
Test cases created,Comprehensive test coverage planned,Test Cases document
Happy path tested,Normal flows have test cases,UI and Backend Test Cases
Edge cases tested,Boundary conditions have test cases,Edge Cases section
Error handling tested,Failure scenarios have test cases,Error Scenarios section
Priorities assigned,All test cases have priority levels,Test case Priority fields
Implementation checklist,Verification checklist provided,Implementation Checklist section

## Key Principles for Technical Design

### Precision

**Be specific and exact:**

- Use absolute file paths, not vague locations
- Reference actual function/component/table names
- Specify exact API endpoints with HTTP methods
- Provide specific test data values
- Define measurable success criteria

### Justification

**Explain the why:**

- Business justification: user value, requirements
- Technical justification: maintainability, performance
- Architecture alignment: consistency with patterns
- Risk rationale: why risks matter and mitigation approach

### Comprehensiveness

**Cover all aspects:**

- What: Detailed changes needed
- Where: Exact file locations
- Why: Business and technical reasons
- Integration: All internal and external connections
- Conflicts: Overlaps with other work
- Risks: Potential problems and mitigation
- Tests: Complete test coverage

### Transparency

**Document decisions openly:**

- Record architectural decisions with full context
- List all options considered, not just chosen one
- Acknowledge trade-offs and negative consequences
- Provide clear rationale for choices
- Link related decisions together

---

**File Size**: 487/500 lines max ✅
**Version**: 2.0.0 - Complete rewrite with TOON format and modern structure
