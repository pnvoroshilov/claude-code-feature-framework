---
name: technical-design
description: Document formats and templates for technical architecture design, test cases, and conflict analysis
tags: [architecture, design, technical-requirements, test-cases, conflict-analysis]
version: 1.0.0
---

# Technical Design Skill

This skill provides document formats, templates, and examples for creating technical design documentation.

## Document Formats

### 1. Technical Requirements

```markdown
## Technical Requirements: [Task Title]

### Overview
[High-level technical approach]

### What to Change

#### Frontend Changes
- **Component:** [Component name and path]
  - **What:** [What needs to change]
  - **Why:** [Reason for change]
  - **Impact:** [Effect on other components]

- **Component:** [Another component]
  - [Details...]

#### Backend Changes
- **Service:** [Service name and path]
  - **What:** [What needs to change]
  - **Why:** [Reason for change]
  - **Impact:** [Effect on other services]

- **API Endpoint:** [Endpoint path]
  - **What:** [New/modified endpoint]
  - **Why:** [Purpose]
  - **Impact:** [Integration points]

#### Database Changes
- **Table:** [Table name]
  - **What:** [Schema changes]
  - **Migration:** [Migration approach]
  - **Impact:** [Data and queries affected]

### Where to Change

#### File Structure
```
src/
├── frontend/
│   ├── components/
│   │   └── [ComponentName].tsx  ← Modify
│   ├── services/
│   │   └── [ServiceName].ts  ← Create new
│   └── types/
│       └── [TypeName].ts  ← Add types
├── backend/
│   ├── api/
│   │   └── [endpoint].py  ← Modify
│   ├── services/
│   │   └── [service].py  ← Create new
│   └── models/
│       └── [model].py  ← Add model
```

### Why These Changes

#### Business Justification
[Why from business perspective]

#### Technical Justification
[Why from technical perspective]

#### Architecture Alignment
[How changes align with existing architecture]

### Integration Points

#### Internal Services
- [Service 1]: [How it integrates]
- [Service 2]: [How it integrates]

#### External APIs
- [API 1]: [How it integrates]
- [API 2]: [How it integrates]

#### Shared Components
- [Component 1]: [Shared with which tasks]
- [Component 2]: [Potential conflicts]

### Conflict Analysis

#### Active Tasks Analysis
**Other Active Tasks:**
- Task #[ID]: [Title]
  - **Overlap:** [Shared components/files]
  - **Conflict Risk:** [High/Medium/Low]
  - **Mitigation:** [How to avoid conflicts]

- Task #[ID]: [Title]
  - [Details...]

**Coordination Needed:**
- [What needs coordination]
- [With which teams/tasks]

### Architecture Decisions

#### Decision 1: [Name]
- **Context:** [Situation]
- **Options Considered:** [Alternatives]
- **Decision:** [What was chosen]
- **Rationale:** [Why]
- **Consequences:** [Trade-offs]

#### Decision 2: [Name]
[Details...]

### Dependencies

#### Technical Dependencies
- [Library/Framework]: [Version, purpose]
- [Service]: [Why needed]

#### Task Dependencies
- Must complete before: [Task IDs]
- Must complete after: [Task IDs]
- Can run in parallel with: [Task IDs]

### Risks and Mitigation

#### Risk 1: [Description]
- **Probability:** [High/Medium/Low]
- **Impact:** [High/Medium/Low]
- **Mitigation:** [How to address]

#### Risk 2: [Description]
[Details...]
```

### 2. Test Cases

```markdown
## Test Cases: [Task Title]

### UI Test Cases

#### TC-UI-01: [Test Case Name]
**Objective:** [What to test]

**Preconditions:**
- [Condition 1]
- [Condition 2]

**Test Steps:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Expected Results:**
- [Expected behavior 1]
- [Expected behavior 2]

**Priority:** [High/Medium/Low]

#### TC-UI-02: [Test Case Name]
[Details...]

### Backend Test Cases

#### TC-BE-01: [Test Case Name]
**Objective:** [What to test]

**API Endpoint:** [Method] /path/to/endpoint

**Request:**
```json
{
  "field": "value"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {}
}
```

**Expected Status Code:** 200

**Validations:**
- [ ] Business logic correct
- [ ] Data persisted properly
- [ ] Side effects handled

**Priority:** [High/Medium/Low]

#### TC-BE-02: [Test Case Name]
[Details...]

### Integration Test Cases

#### TC-INT-01: [End-to-End Flow]
**Scenario:** [User journey]

**Steps:**
1. [Frontend action] → [API call]
2. [Backend processing] → [Database update]
3. [Response] → [UI update]

**Expected Outcome:** [What user sees]

#### TC-INT-02: [Another Flow]
[Details...]

### Edge Cases and Error Scenarios

#### TC-ERR-01: [Error Case]
**Scenario:** [What goes wrong]
**Expected Behavior:** [How system handles it]
**UI Feedback:** [What user sees]

#### TC-ERR-02: [Another Error]
[Details...]
```

## Best Practices for Document Quality

### Technical Requirements Best Practices
- ✅ Use exact file paths (not "somewhere in the code")
- ✅ Specify function/component names precisely
- ✅ Explain "why" for each change (business + technical justification)
- ✅ Consider impact on other components

### Test Cases Best Practices
- ✅ Write clear, numbered steps
- ✅ Define measurable expected outcomes
- ✅ Cover both happy path and edge cases
- ✅ Include error scenarios

### Architecture Decisions Best Practices
- ✅ Document the context (why decision was needed)
- ✅ List alternatives considered
- ✅ Explain rationale for chosen option
- ✅ Acknowledge trade-offs and consequences
