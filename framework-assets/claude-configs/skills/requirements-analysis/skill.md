---
name: requirements-analysis
description: |
  Comprehensive requirements discovery and analysis framework for transforming user requests into detailed,
  actionable specifications. Use when users mention: requirements gathering, user stories, use cases, functional
  requirements, non-functional requirements, acceptance criteria, business requirements, feature specifications,
  requirements documentation, project scope, stakeholder needs, definition of done, or requirements elicitation.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Requirements Analysis Skill

**Expert guidance for comprehensive requirements discovery, analysis, and documentation, transforming high-level user needs into detailed, actionable specifications.**

## Overview

This skill provides systematic frameworks for:

skill_capabilities[8]{capability,description,use_case}:
Requirements Discovery,Eliciting complete requirements from stakeholders,Initial project kickoff or feature requests
Functional Requirements,Defining what the system should do,Feature specifications and behavior definition
Non-Functional Requirements,Defining system qualities and constraints,Performance security scalability requirements
User Stories,Capturing user-centric requirements,Agile development and sprint planning
Use Cases,Documenting interaction scenarios,Complex workflows and system interactions
Acceptance Criteria,Defining testable completion conditions,Quality assurance and validation
Definition of Done,Establishing completion standards,Team alignment and quality gates
Requirements Documentation,Creating structured requirement documents,Handoff communication and reference

## When to Use This Skill

**Trigger Scenarios:**

trigger_scenarios[12]{scenario,skill_application}:
User provides vague feature request,Conduct requirements discovery to clarify needs
User asks to build new feature,Document functional and non-functional requirements
User mentions user story,Create properly formatted user story with acceptance criteria
User describes workflow,Transform into formal use case documentation
User needs feature specification,Create comprehensive requirements document
User asks about project scope,Define and document clear boundaries
User mentions acceptance criteria,Define measurable testable criteria
User discusses definition of done,Create quality checklist and completion standards
User provides incomplete requirements,Ask clarifying questions to fill gaps
User has conflicting requirements,Identify and resolve conflicts through analysis
User needs requirements review,Validate completeness consistency and feasibility
User starts new project,Conduct full requirements analysis and documentation

## Quick Reference

### Requirements Types

requirements_types[4]{type,purpose,key_questions,output}:
Functional,What the system should do,What actions? What data? What results?,Feature specifications use cases user stories
Non-Functional,How well the system should perform,How fast? How secure? How scalable?,Performance security usability requirements
Business,Why the system is needed,What problem? What value? What ROI?,Business justification success metrics
Constraints,Limitations and restrictions,What limitations? What regulations? What budget?,Technical legal resource constraints

### Requirement Quality Criteria (SMART)

quality_criteria[5]{criterion,description,example}:
Specific,Clear and unambiguous description,User can filter tasks by status instead of User can manage tasks
Measurable,Quantifiable success criteria,Response time under 200ms instead of System should be fast
Achievable,Realistic given constraints,Support 10000 concurrent users instead of unlimited users
Relevant,Aligned with business goals,Directly supports core user workflow
Testable,Can verify if requirement is met,Login succeeds with valid credentials instead of Login works well

### Requirements Elicitation Techniques

elicitation_techniques[6]{technique,description,when_to_use,output}:
Stakeholder Interviews,Direct questioning of stakeholders,Initial discovery gathering perspectives,Raw requirements and pain points
Requirements Workshops,Collaborative group sessions,Complex features needing consensus,Prioritized requirements list
Use Case Analysis,Documenting user interactions,Workflow-heavy features,Detailed use case documents
Prototype Review,Show mockups get feedback,UI/UX focused features,Refined requirements based on feedback
Document Analysis,Review existing docs and systems,Enhancement or migration projects,Gap analysis and requirements
Observation,Watch users in real environment,Unclear workflows or processes,Real-world usage patterns

## Requirements Discovery Workflow

**Systematic approach to gathering complete requirements:**

discovery_workflow[8]{step,action,key_questions,deliverable}:
1. Understand Context,Gather background on problem and stakeholders,What problem? Who are users? What is current state?,Context summary with stakeholders
2. Identify Stakeholders,List all people affected by change,Who will use it? Who decides? Who maintains?,Stakeholder register with roles
3. Elicit Requirements,Use techniques to gather needs,What must it do? What constraints? What quality?,Raw requirements list
4. Analyze Requirements,Examine completeness and feasibility,Any conflicts? Any gaps? Is it realistic?,Analyzed requirements with issues flagged
5. Document Requirements,Create structured specification,What format? What level of detail?,Formal requirements document
6. Validate Requirements,Review with stakeholders for accuracy,Does this match needs? Any missing items?,Validated requirements with signoff
7. Prioritize Requirements,Rank by business value and urgency,What is critical? What is nice-to-have?,Prioritized requirements backlog
8. Baseline Requirements,Lock version for implementation,Is this complete? Is this approved?,Baselined requirements specification

## Documentation Structure

**Complete documentation is split across multiple files for maintainability:**

documentation_files[8]{file,content,line_count}:
reference/functional-requirements.md,Functional requirements structure templates examples,~250 lines
reference/non-functional-requirements.md,NFR categories metrics and templates,~200 lines
reference/user-stories.md,User story format templates and examples,~180 lines
reference/use-cases.md,Use case structure templates detailed examples,~200 lines
reference/acceptance-criteria.md,AC formats best practices examples,~150 lines
reference/definition-of-done.md,DoD templates and quality checklists,~120 lines
reference/best-practices.md,Requirements quality pitfalls review checklists,~180 lines
reference/discovery-questions.md,Key questions to ask during requirements gathering,~120 lines

## Usage Workflow

**How to apply this skill effectively:**

usage_steps[8]{step,action,details}:
1. Identify need,Determine what requirements format is needed,User story vs use case vs functional requirements
2. Read reference,Access appropriate reference documentation,Navigate to specific reference/*.md file
3. Apply template,Use template from reference documentation,Fill in template with project-specific details
4. Validate quality,Check against SMART criteria,Review reference/best-practices.md for quality checklist
5. Review completeness,Ensure all necessary information captured,Use discovery questions from reference/discovery-questions.md
6. Resolve conflicts,Identify and address contradictions,Document resolution rationale
7. Obtain approval,Review with stakeholders,Baseline approved requirements
8. Create traceability,Link requirements to implementation,Maintain requirements-to-code mapping

## Quick Start Guide

### Starting a New Feature

quick_start_steps[6]{step,action,reference_file}:
1. Gather Context,Understand problem and stakeholders,reference/discovery-questions.md
2. Write User Stories,Capture user needs with acceptance criteria,reference/user-stories.md
3. Define Functional Requirements,Detail what system should do,reference/functional-requirements.md
4. Define Non-Functional Requirements,Specify quality attributes and metrics,reference/non-functional-requirements.md
5. Create Use Cases,Document complex workflows if needed,reference/use-cases.md
6. Define DoD,Establish quality gates and completion standards,reference/definition-of-done.md

### Requirements Analysis Questions to Ask

**Always ask these questions during requirements gathering:**

key_question_categories[6]{category,focus,reference}:
Users,Who are users and what are their goals?,reference/discovery-questions.md (Lines 1-30)
Functionality,What must the system do?,reference/discovery-questions.md (Lines 31-50)
Data,What data is needed and where?,reference/discovery-questions.md (Lines 51-70)
Integration,What external systems are involved?,reference/discovery-questions.md (Lines 71-85)
Constraints,What are the limitations?,reference/discovery-questions.md (Lines 86-100)
Success,How to measure success?,reference/discovery-questions.md (Lines 101-120)

## Common Use Cases

### Use Case 1: User Requests Vague Feature

**Response Pattern:**

1. Read `reference/discovery-questions.md` for key questions
2. Ask clarifying questions from Users and Functionality categories
3. Read `reference/user-stories.md` for format
4. Create user story with clear acceptance criteria
5. Validate using SMART criteria

### Use Case 2: Building Complex Workflow

**Response Pattern:**

1. Read `reference/use-cases.md` for detailed format
2. Document actors, preconditions, and trigger
3. Map out main flow with numbered steps
4. Identify alternative and exception flows
5. Define postconditions and business rules

### Use Case 3: Defining System Quality

**Response Pattern:**

1. Read `reference/non-functional-requirements.md` for NFR categories
2. Identify applicable NFR categories (performance, security, etc.)
3. Define measurable metrics and target values
4. Specify measurement methods
5. Document rationale for each NFR

### Use Case 4: Establishing Completion Criteria

**Response Pattern:**

1. Read `reference/definition-of-done.md` for DoD template
2. Customize checklist for project context
3. Include functional completeness, code quality, testing, documentation
4. Add security, performance, and deployment criteria
5. Review and approve with team

## Integration with Other Skills

**Requirements analysis integrates with:**

skill_integrations[6]{skill,integration_point,workflow}:
technical-design,Transform requirements into architecture,Requirements → Architecture → Implementation
architecture-patterns,Apply patterns based on requirements,Non-functional requirements drive architecture patterns
testing,Acceptance criteria become test cases,Requirements → Test cases → Test execution
project-management,Requirements inform task breakdown,Requirements → Tasks → Estimation
documentation,Requirements are source of truth,Requirements → User docs → API docs
code-review,Verify implementation meets requirements,Requirements → Code → Review against requirements

## Requirements Quality Best Practices

### Requirement Quality Checklist

requirement_quality[10]{quality_aspect,good_practice,bad_practice}:
Clarity,Use precise unambiguous language,System shall process data quickly
Completeness,Include all necessary information,User can login (missing: how what validation errors)
Consistency,No contradictions between requirements,Req A says 200ms Req B says 1 second
Verifiable,Can test if requirement is met,Response time under 200ms vs good performance
Traceable,Link to source and related requirements,Each requirement has unique ID and dependencies
Feasible,Realistic given constraints,Support unlimited users with $100 budget
Necessary,Truly needed not nice-to-have,Requirement adds business value
Prioritized,Ranked by importance,Critical High Medium Low designation
Atomic,Single clear requirement not compound,One requirement one concern
Unambiguous,Only one interpretation possible,Avoid words like: fast easy flexible simple

### Common Requirements Pitfalls

common_pitfalls[8]{pitfall,description,solution}:
Vague Language,Using ambiguous terms like fast easy flexible,Use measurable quantities: under 200ms minimum 1000 users
Gold Plating,Including unnecessary features,Focus on minimum viable solution
Missing Edge Cases,Only considering happy path,Document error scenarios boundary conditions
Conflicting Requirements,Contradictory specifications,Review for consistency resolve conflicts
Implementation Bias,Specifying how instead of what,Focus on desired outcome not technical approach
Incomplete Acceptance Criteria,Cannot verify when done,Define 3-5 testable conditions per requirement
Scope Creep,Adding requirements mid-development,Baseline requirements freeze scope
Stakeholder Assumptions,Assuming you know what they want,Validate with actual stakeholders

## Key Principles

### Requirements Should Be

key_principles[6]{principle,description,example}:
User-Centric,Focus on user needs not technical implementation,As a user I want to... not System shall implement...
Testable,Include clear acceptance criteria,Response time < 200ms not system is fast
Complete,Cover all scenarios including errors,Define happy path alternatives and exceptions
Prioritized,Ranked by business value,Critical requirements identified vs nice-to-have
Traceable,Linked to business objectives and tests,Each requirement has unique ID and lineage
Baseline-Controlled,Versioned and change-managed,Approved requirements locked before implementation

### Questions to Validate Requirements

validation_questions[8]{question,purpose}:
Is it clear what the system should do?,Test clarity and specificity
Can we test if this is done?,Verify testability
Does it conflict with other requirements?,Check consistency
Is it realistic given constraints?,Assess feasibility
Why is this needed?,Validate business value
Who benefits from this?,Ensure user-centricity
What if this goes wrong?,Cover error scenarios
Is this the minimum viable solution?,Prevent gold plating

## Additional Resources

**For detailed information and templates, see:**

- `reference/functional-requirements.md` - Functional requirements structure and examples
- `reference/non-functional-requirements.md` - NFR categories and metrics
- `reference/user-stories.md` - User story templates and acceptance criteria
- `reference/use-cases.md` - Use case format with detailed examples
- `reference/acceptance-criteria.md` - AC formats and writing guidelines
- `reference/definition-of-done.md` - DoD templates and quality checklists
- `reference/best-practices.md` - Quality guidelines and review checklists
- `reference/discovery-questions.md` - Key questions for requirements gathering

## Example Workflow

### Complete Requirements Analysis Process

```
1. DISCOVERY (reference/discovery-questions.md)
   - Ask key questions about users, functionality, constraints
   - Gather context and identify stakeholders
   - Output: Context summary and stakeholder register

2. USER STORIES (reference/user-stories.md)
   - Write user stories in "As a...I want...So that" format
   - Define 3-5 acceptance criteria per story
   - Output: User story documents with AC

3. FUNCTIONAL REQUIREMENTS (reference/functional-requirements.md)
   - Document what system shall do
   - Include actors, preconditions, flows, postconditions
   - Output: Functional requirements specification

4. NON-FUNCTIONAL REQUIREMENTS (reference/non-functional-requirements.md)
   - Define performance, security, scalability metrics
   - Set measurable target values
   - Output: NFR document with measurement methods

5. USE CASES (reference/use-cases.md) [if complex workflows]
   - Document main, alternative, and exception flows
   - Include business rules and postconditions
   - Output: Detailed use case documents

6. DEFINITION OF DONE (reference/definition-of-done.md)
   - Create quality checklist
   - Include functional, testing, security, deployment criteria
   - Output: DoD checklist for completion

7. VALIDATION (reference/best-practices.md)
   - Review against SMART criteria
   - Check completeness and consistency
   - Obtain stakeholder approval
   - Output: Baselined requirements
```

## Success Criteria

**Effective requirements analysis achieves:**

success_criteria[8]{criterion,indicator}:
Clarity,Stakeholders understand exactly what will be built
Completeness,All scenarios including errors are documented
Consistency,No contradictions between requirements
Testability,Every requirement has measurable acceptance criteria
Traceability,Requirements linked to business objectives and tests
Approval,Stakeholders have reviewed and signed off
Baseline Control,Requirements versioned and change-managed
Team Alignment,Everyone knows what done means (DoD)

---

**File Size**: 250/500 lines max ✅
**Next Steps**: Review reference/*.md files for detailed templates and examples
