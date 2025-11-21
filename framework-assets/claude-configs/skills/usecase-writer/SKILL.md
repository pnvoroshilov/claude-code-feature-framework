---
name: usecase-writer
description: |
  Expert in creating comprehensive, detailed UseCases from requirements following UML, Cockburn,
  IEEE 830, and industry best practices. Use when writing use cases, defining user flows,
  creating acceptance criteria, documenting scenarios, analyzing requirements, or defining
  system interactions. Covers actors, preconditions, postconditions, main flows, alternative
  flows, extensions, and exceptions. Helps transform requirements into testable, clear use case
  documentation.
allowed-tools:
  - Read
  - Write
  - Grep
---

# UseCase Writer Expert

Expert in creating comprehensive, well-structured UseCases that transform requirements into clear, testable documentation following industry standards (UML, Cockburn, IEEE 830).

## Core Expertise

expertise_areas[6]{area,description}:
Requirements Analysis,Extract and clarify functional requirements from user stories and business needs
UseCase Structure,Create properly formatted UseCases with all standard sections and elements
Actor Identification,Identify and document all actors (users systems external entities) and their roles
Flow Documentation,Write detailed main flows alternative flows and exception paths
Acceptance Criteria,Define clear testable acceptance criteria for each use case
Standards Compliance,Follow UML Cockburn IEEE 830 and Rational Unified Process standards

## When to Use This Skill

activation_triggers[8]{scenario,keywords}:
Requirements documentation,use case usecase write create document requirements
User flow definition,user flow scenario interaction workflow steps
Acceptance criteria creation,acceptance criteria test cases validation requirements
Actor identification,actors stakeholders users systems roles
Preconditions and postconditions,preconditions postconditions constraints state
Alternative scenarios,alternative flow exception error handling edge cases
System interactions,system boundary interactions integration touchpoints
Requirements analysis,analyze requirements functional specifications business logic

## Key Capabilities

capabilities[5]{capability,description,key_features}:
UseCase Creation,Create complete structured UseCases from requirements,"Actors; Preconditions; Main Flow; Alternative Flows; Postconditions; Exceptions; Extensions; Business Rules"
Flow Documentation,Document detailed step-by-step flows,"Numbered steps; Actor actions; System responses; Decision points; Error handling; Validation rules"
Standards Compliance,Follow industry-standard UseCase formats,"UML notation; Cockburn style; IEEE 830; RUP methodology; IIBA BABOK standards"
Requirements Traceability,Link UseCases to requirements and test cases,"Requirement IDs; Traceability matrix; Test case mapping; Coverage analysis"
Quality Assurance,Ensure UseCases are complete testable and unambiguous,"Completeness checks; Testability validation; Clarity review; Consistency verification"

## UseCase Structure Standards

### Essential Sections

usecase_sections[10]{section,required,description}:
UseCase ID,Yes,Unique identifier for traceability (e.g. UC-001)
UseCase Title,Yes,Clear concise name describing the goal
Brief Description,Yes,One-sentence summary of what the use case accomplishes
Actors,Yes,Primary and secondary actors (users systems services)
Preconditions,Yes,Required system state before execution
Trigger,Yes,Event that initiates the use case
Main Success Scenario,Yes,Step-by-step normal flow (happy path)
Extensions/Alternatives,Conditional,Alternative flows and exception handling
Postconditions,Yes,Guaranteed system state after successful completion
Business Rules,Conditional,Constraints and validation rules that must be enforced

### Cockburn Style UseCase Template

```markdown
## UseCase: [UC-ID] [UseCase Title]

**Brief Description**: [One sentence describing the goal]

**Primary Actor**: [Main user or system initiating action]

**Secondary Actors**: [Supporting actors or systems]

**Stakeholders and Interests**:
stakeholders[N]{stakeholder,interest}:
[Stakeholder 1],[Their concern or benefit]
[Stakeholder 2],[Their concern or benefit]

**Preconditions**:
- [Condition 1 that must be true before starting]
- [Condition 2]

**Trigger**: [Event that starts this use case]

**Main Success Scenario**:
1. [Actor] [performs action]
2. System [responds/validates/processes]
3. System [displays/updates/confirms]
4. [Actor] [next action]
5. System [final response]

**Extensions** (Alternative Flows):

**3a. [Condition]: [Alternative path title]**
  3a1. System [alternative action]
  3a2. [Actor] [alternative response]
  3a3. Return to step 4 of Main Success Scenario

**4a. [Error condition]**
  4a1. System [error handling]
  4a2. System [displays error message]
  4a3. Use case ends in failure

**Postconditions**:
**Success**: [What is guaranteed after successful completion]
**Failure**: [System state if use case fails]

**Business Rules**:
business_rules[N]{rule_id,rule_description}:
BR-001,[Business constraint or validation rule]
BR-002,[Another business rule]

**Non-Functional Requirements**:
nfr[N]{category,requirement}:
Performance,[Response time or throughput requirement]
Security,[Authentication authorization encryption requirements]
Usability,[User experience requirements]

**Open Issues**:
- [Any unresolved questions or dependencies]
```

## Best Practices

best_practices[12]{category,practice,explanation}:
Actor Naming,Use role names not personal names,Actors represent roles (Customer) not individuals (John Smith)
Active Voice,Write steps in active voice with clear subject,Each step states who does what explicitly
Numbering,Use hierarchical numbering for extensions,Main flow 1-N extensions 3a 3a1 3a2 for clarity
One Goal,Each UseCase achieves ONE clear business goal,Avoid combining multiple objectives in single use case
Testability,Every step must be testable and verifiable,QA should be able to create test cases directly from steps
User Perspective,Write from user's point of view not system,Focus on what user accomplishes not implementation details
Preconditions,Keep preconditions minimal and verifiable,Only include conditions that must be checked before execution
Postconditions,Postconditions must be guaranteed outcomes,State what is always true after successful completion
Extensions Placement,Place extension at the step where it diverges,Extension 3a means alternative starts at step 3
Completeness,Include all realistic scenarios not just happy path,Consider errors edge cases alternative paths
Business Language,Use domain terminology not technical jargon,Business stakeholders must understand use cases
Atomic Steps,Each step is single meaningful action,Avoid compound steps that do multiple things

## Common UseCase Patterns

### Pattern 1: CRUD Operations

**Create Entity Pattern**:
```
Main Success Scenario:
1. User selects "Create New [Entity]"
2. System displays [Entity] creation form
3. User enters required information
4. User submits form
5. System validates data
6. System creates [Entity] record
7. System assigns unique identifier
8. System displays confirmation with [Entity] ID
9. System returns to [Entity] list

Extensions:
5a. Validation fails
  5a1. System displays validation errors
  5a2. System highlights invalid fields
  5a3. Resume at step 3
```

crud_pattern_variations[4]{operation,key_steps,typical_extensions}:
Create,Display form → Enter data → Validate → Save → Confirm,Validation errors; Duplicate detection; Required field missing
Read,Request entity → Validate access → Retrieve data → Display,Entity not found; Access denied; Data corruption
Update,Display current data → Modify fields → Validate → Save → Confirm,Concurrent modification; Validation failure; Optimistic locking
Delete,Request deletion → Confirm intent → Validate → Remove → Confirm,Referenced by others; Cascade delete; Soft delete option

### Pattern 2: Authentication/Authorization

**Login Pattern**:
```
Main Success Scenario:
1. User navigates to login page
2. System displays login form
3. User enters username and password
4. User submits credentials
5. System validates credentials
6. System creates session
7. System redirects to dashboard
8. System displays personalized welcome

Extensions:
5a. Invalid credentials
  5a1. System increments failed login counter
  5a2. System displays "Invalid username or password"
  5a3. Resume at step 3

5b. Account locked
  5b1. System displays "Account locked" message
  5b2. System sends unlock email to registered address
  5b3. Use case ends

5c. Password expired
  5c1. System displays password reset form
  5c2. Include UC-015: Change Password
  5c3. Resume at step 6 after successful password change
```

### Pattern 3: Search and Filter

**Search Pattern**:
```
Main Success Scenario:
1. User enters search criteria
2. User applies optional filters
3. User initiates search
4. System validates search parameters
5. System queries database
6. System sorts results by relevance
7. System displays paginated results with count
8. User selects result from list
9. System displays detailed view

Extensions:
5a. No results found
  5a1. System displays "No results found"
  5a2. System suggests alternative search terms
  5a3. Resume at step 1

7a. Too many results (>1000)
  7a1. System displays "Refine your search"
  7a2. System suggests additional filters
  7a3. Resume at step 1
```

## Quality Checklist

quality_criteria[15]{criterion,requirement,validation}:
Clear Title,UseCase title describes goal in 3-7 words,Title answers "what does user accomplish"
Actor Identification,All actors identified with clear roles,Primary actor is the goal initiator
Preconditions Listed,All required states documented,Each precondition is verifiable and necessary
Trigger Defined,Triggering event explicitly stated,Trigger is observable and specific
Main Flow Complete,Happy path documented step-by-step,Each step is testable and unambiguous
Extensions Documented,All alternative paths included,Extensions cover errors and variations
Postconditions Clear,Success and failure outcomes stated,Postconditions are guaranteed results
Active Voice,All steps use active voice,Each step has clear subject and action
Numbering Consistent,Hierarchical numbering for all flows,Extensions use parent step number (3a 3a1)
Business Rules,Constraints and validations documented,Rules are linked to specific steps
Testable Steps,Every step can be tested,QA can create test cases directly
No Implementation,Focus on what not how,No technical implementation details
Complete Scenarios,All realistic paths covered,Includes errors edge cases alternatives
Traceability,Linked to requirements and tests,UseCase ID requirement IDs test IDs present
Stakeholder Review,Validated by business stakeholders,Non-technical readers can understand

## Integration with Development

### Requirements to UseCase Mapping

requirements_mapping[4]{source,usecase_elements,output}:
User Stories,Actors goal preconditions main flow,Detailed UseCases with all scenarios
Business Requirements,Business rules constraints NFRs,Complete use case with quality attributes
Functional Specs,Step-by-step flows system responses,Implementable specifications
Acceptance Criteria,Extensions postconditions validation,Testable scenarios

### UseCase to Test Case Mapping

test_mapping[5]{usecase_element,test_type,test_focus}:
Main Success Scenario,Happy path test,Verify normal flow from start to completion
Extensions,Alternative flow tests,Test each extension path separately
Preconditions,Setup validation tests,Verify system enforces preconditions
Postconditions,Outcome verification tests,Assert postconditions after execution
Business Rules,Validation tests,Test each business rule enforcement

## Common Mistakes to Avoid

common_mistakes[10]{mistake,problem,correction}:
Vague steps,Steps like "System processes data" unclear,Be specific: "System validates email format"
Implementation details,Including technical implementation,Focus on what system does not how
Multiple goals,UseCase trying to accomplish too much,Split into separate focused use cases
Missing extensions,Only documenting happy path,Include all realistic error and alternative paths
Passive voice,Steps like "Data is validated" unclear actor,Use "System validates data"
No preconditions,Assuming starting state without stating,Explicitly list required preconditions
Guaranteed postconditions,Postconditions that aren't always true,Only include guaranteed outcomes
UI-specific language,Mentioning buttons screens widgets,Use abstract interaction language
No business rules,Missing validation constraints,Document all business rules and link to steps
Untestable steps,Steps that cannot be verified,Make every step observable and testable

## Example UseCases

### Example 1: User Registration

```markdown
## UseCase: UC-001 Register New User Account

**Brief Description**: New visitor creates user account to access system features

**Primary Actor**: Visitor (Unregistered User)

**Secondary Actors**: Email Service, Authentication Service

**Stakeholders and Interests**:
stakeholders[3]{stakeholder,interest}:
Visitor,Wants quick easy registration process
System Owner,Wants valid user data and security compliance
Marketing Team,Wants user contact information for campaigns

**Preconditions**:
- User has valid email address
- System is accessible
- Email service is operational

**Trigger**: User selects "Sign Up" or "Register"

**Main Success Scenario**:
1. User navigates to registration page
2. System displays registration form (email, password, confirm password, terms checkbox)
3. User enters email address
4. User creates password
5. User confirms password
6. User accepts terms and conditions
7. User submits registration form
8. System validates email format (RFC 5322)
9. System validates password strength (min 8 chars, uppercase, lowercase, number)
10. System checks passwords match
11. System verifies email not already registered
12. System creates user account with status "Pending Verification"
13. System generates unique verification token
14. System sends verification email with token link
15. System displays "Check your email" confirmation message
16. User checks email and clicks verification link
17. System validates token and expiration
18. System updates account status to "Active"
19. System displays "Account verified" success message
20. System redirects to login page

**Extensions**:

**8a. Email format invalid**
  8a1. System displays "Invalid email format"
  8a2. System highlights email field
  8a3. Resume at step 3

**9a. Password too weak**
  9a1. System displays password strength requirements
  9a2. System shows strength meter
  9a3. Resume at step 4

**10a. Passwords don't match**
  10a1. System displays "Passwords do not match"
  10a2. System clears password fields
  10a3. Resume at step 4

**11a. Email already registered**
  11a1. System displays "Email already in use"
  11a2. System offers "Forgot Password?" link
  11a3. Use case ends

**14a. Email delivery fails**
  14a1. System logs delivery failure
  14a2. System displays "Email delivery failed. Contact support"
  14a3. System keeps account in "Pending" status
  14a4. Use case ends

**17a. Verification token expired (>24 hours)**
  17a1. System displays "Verification link expired"
  17a2. System offers "Resend verification email" option
  17a3. Include UC-002: Resend Verification Email
  17a4. Use case ends

**17b. Invalid or tampered token**
  17b1. System logs security event
  17b2. System displays "Invalid verification link"
  17b3. System offers contact support option
  17b4. Use case ends

**Postconditions**:
**Success**:
- User account created with status "Active"
- User can log in with credentials
- Verification email sent and confirmed
- User data stored in database

**Failure**:
- No account created
- Email address remains available
- No verification email sent

**Business Rules**:
business_rules[5]{rule_id,rule_description}:
BR-001,Email must be unique across all user accounts
BR-002,Password must be minimum 8 characters with mixed case and number
BR-003,Verification token expires after 24 hours
BR-004,User must verify email before accessing protected features
BR-005,Terms and conditions acceptance is mandatory and logged

**Non-Functional Requirements**:
nfr[4]{category,requirement}:
Performance,Registration completes within 2 seconds
Security,Passwords hashed with bcrypt before storage
Usability,Form provides real-time validation feedback
Availability,Email service has fallback retry mechanism
```

## Additional Resources

resources[5]{resource,location,description}:
Reference Documentation,reference.md,Detailed UseCase standards and formats
Basic Examples,examples/basic.md,Simple UseCases (Search Products; Backup Database)
Intermediate Examples,examples/intermediate.md,Medium complexity (Registration; Leave Approval; Support Ticket)
Advanced Examples,examples/advanced.md,Complex UseCase (Place Order with full detail)
README,README.md,Quick start guide and overview

## Tips for Success

success_tips[8]{tip,explanation}:
Start with actors,Identify who benefits from use case before writing flows
Write main flow first,Document happy path completely before adding extensions
Number consistently,Use clear hierarchical numbering for easy reference
Review with stakeholders,Validate use cases with business users not just developers
Keep it business-focused,Avoid technical implementation details
Include all extensions,Document every realistic alternative and error path
Link to requirements,Maintain traceability to original requirements
Iterate and refine,Use cases evolve as understanding deepens

---
**File Size**: 437/500 lines max ✅
