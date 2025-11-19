# UseCase Writing - Reference Documentation

Complete reference for UseCase standards, formats, and methodologies.

## UseCase Definition

A UseCase is a detailed description of how a user (actor) interacts with a system to achieve a specific goal. It captures functional requirements in a structured, testable format that bridges the gap between business requirements and technical implementation.

## Industry Standards Overview

standards[5]{standard,source,focus,best_for}:
UML UseCases,Unified Modeling Language (OMG),Visual diagrams and structural notation,Systems with complex actor relationships
Cockburn Format,Alistair Cockburn (Writing Effective Use Cases),Detailed narrative style with extensions,Agile teams needing comprehensive scenarios
IEEE 830,IEEE Recommended Practice for Software Requirements,Formal structured requirements,Regulated industries and large enterprises
RUP UseCases,Rational Unified Process,Iterative development focus,Enterprise software development
IIBA BABOK,Business Analysis Body of Knowledge,Business analysis perspective,Business analysts and requirements engineers

## Actor Types and Roles

### Actor Categories

actor_categories[4]{category,definition,examples,characteristics}:
Primary Actor,Initiates use case to achieve goal,Customer Employee Administrator,Has stake in outcome; triggers interaction
Secondary Actor,Supports primary actor or system,Payment Gateway Email Service Database,Provides service; doesn't initiate
Offstage Stakeholder,Interested in outcome but doesn't interact,Manager Auditor Compliance Officer,Benefits from use case; sets requirements; doesn't participate
System Actor,External system or service,API Third-party Service Legacy System,Automated interaction; no human involvement

### Actor Naming Conventions

actor_naming[6]{guideline,correct_example,incorrect_example}:
Use roles not names,Customer Support Agent,John Smith from Support
Abstract not specific,System Administrator,Windows Server 2019 Admin
Generalize by function,Payment Processor,Stripe API v2
Focus on responsibility,Content Moderator,Person who checks posts
Business terminology,Account Manager,CRM User
Avoid technical jargon,External System,RESTful API Endpoint

## Preconditions vs Triggers

### Preconditions

**Definition**: Conditions that must be true BEFORE the use case can start. The system assumes these are already satisfied.

precondition_characteristics[5]{characteristic,explanation,example}:
Verifiable,Must be able to check if true,"User is authenticated" (can verify session)
Static,Doesn't change during use case,"Database is accessible" (assumed throughout)
Required,Use case cannot start without it,"Shopping cart contains items" (prerequisite)
System state,Describes system or data state,"Product inventory is updated" (data condition)
Outside scope,Established by other use cases,"User account exists" (from registration use case)

**Good Preconditions**:
- User is authenticated and has active session
- User has "Editor" role or higher
- Document exists in database
- User has sufficient account balance ($50 minimum)
- System is in normal operating mode

**Bad Preconditions** (these are actually part of the flow):
- User clicks login button (this is step in flow)
- System validates password (this is an action)
- User has network connection (too infrastructure-level)

### Triggers

**Definition**: The specific event that initiates the use case execution.

trigger_characteristics[4]{characteristic,explanation,example}:
Observable event,Something happens that can be detected,"User clicks 'Submit Order'" (user action)
Specific moment,Precise point in time,"Daily backup scheduled time reaches 2:00 AM" (time event)
External stimulus,Comes from outside the use case,"Payment confirmation received from gateway" (system event)
Initiating action,First action that starts the flow,"User selects 'Create New Invoice'" (trigger action)

**Trigger Types**:

trigger_types[5]{type,description,example}:
User action,User performs specific action,"User clicks 'Export Report' button"
Time-based,Scheduled or timed event,"System clock reaches midnight for daily batch processing"
System event,Internal system condition met,"Database reaches 90% capacity threshold"
External event,Event from external system,"Webhook received from payment processor"
Data change,Data condition triggers process,"Inventory level falls below reorder point"

## Main Success Scenario (Happy Path)

### Step Writing Guidelines

step_guidelines[10]{guideline,explanation,good_example,bad_example}:
One action per step,Each step single discrete action,"User enters email address","User enters email and password"
Active voice,Clear subject and action,"System validates format","Format is validated"
Observable action,Action can be seen/verified,"System displays error message","System processes internally"
Numbered sequentially,Steps in execution order,"1. 2. 3.","Random or letter numbering"
User-system alternating,Typically alternates between actor and system,"1. User enters 2. System validates","1. User 2. User 3. User"
No implementation,What not how,"System authenticates user","System queries LDAP server"
Specific not vague,Concrete actions,"System sends email to registered address","System notifies user"
Include data details,Specify what data,"User enters (title description priority)","User enters information"
Complete transaction,Flow reaches logical conclusion,"System displays confirmation","System processes request"
Business language,Domain terminology not technical,"System creates invoice","System inserts record in INVOICES table"

### Step Patterns

**User Input Pattern**:
```
1. User navigates to [form/page]
2. System displays [form] with fields ([field1, field2, field3])
3. User enters [specific data]
4. User submits [form]
5. System validates [data]
6. System [processes/saves/creates]
7. System displays [confirmation/result]
```

**System Processing Pattern**:
```
1. System retrieves [data] from [source]
2. System validates [criteria]
3. System calculates [result]
4. System updates [entity]
5. System logs [transaction]
6. System returns [response]
```

**Decision Point Pattern**:
```
1. System evaluates [condition]
2. IF [condition true]:
     System performs [action A]
   ELSE:
     System performs [action B]  [Note: Use extensions for IF/ELSE]
3. System continues [next step]
```

## Extensions and Alternative Flows

### Extension Numbering System

extension_numbering[6]{format,meaning,example,when_to_use}:
Na,Alternative at step N,"3a. Email format invalid","Simple alternative to specific step"
Na-Nb,Nested alternative,"3a. Invalid format → 3a-1a. Special char error","Sub-alternative within alternative"
Nab,Multiple alternatives at same step,"3a. Format error 3b. Domain error","Multiple distinct alternatives at step N"
N-M,Range of steps,"3-5. Connection lost during steps 3-5","Alternative applies to range"
*,Applies to any step,"*a. User cancels at any time","Can occur anywhere in flow"
[condition],Conditional extension,"[timeout > 30s]. System displays timeout message","Specific condition triggers alternative"

### Extension Structure

**Standard Extension Format**:
```
**Na. [Condition or Error]**: [Brief description]
  Na1. [First action in alternative]
  Na2. [Second action]
  Na3. [Resolution: Resume/End/Include other UC]
```

### Extension Resolution Types

extension_resolution[5]{resolution,when_to_use,example}:
Resume at step N,Alternative resolved returns to main flow,"Resume at step 4 (continues main flow)"
Use case ends,Cannot continue; terminal failure,"Use case ends in failure"
Include other UC,Delegate to another use case,"Include UC-015: Reset Password; Resume at step 1"
Return to step N,Go back to earlier step,"Return to step 2 (retry from earlier point)"
Branch to other UC,Transfer to different use case,"Continue with UC-020: Admin Review"

### Common Extension Patterns

**Validation Error Pattern**:
```
**5a. Validation fails**
  5a1. System identifies invalid fields
  5a2. System displays error messages next to fields
  5a3. System retains valid input values
  5a4. System highlights first invalid field
  5a5. Resume at step 3
```

**System Error Pattern**:
```
**7a. Database connection lost**
  7a1. System logs error with timestamp
  7a2. System attempts reconnection (3 retries)
  7a3. If reconnection successful: Resume at step 7
  7a4. If reconnection fails:
    7a4a. System displays "Service temporarily unavailable"
    7a4b. System saves partial data to recovery queue
    7a4c. System notifies system administrator
    7a4d. Use case ends in failure
```

**Business Rule Violation Pattern**:
```
**8a. Credit limit exceeded**
  8a1. System calculates outstanding balance
  8a2. System displays "Credit limit would be exceeded"
  8a3. System shows available credit amount
  8a4. System offers options:
    - Reduce order quantity
    - Remove items
    - Request credit increase
  8a5. User selects option
  8a6. Resume at appropriate step based on selection
```

**User Cancellation Pattern**:
```
***a. User cancels operation (at any time)**
  *a1. System displays "Are you sure?" confirmation
  *a2. User confirms cancellation
  *a3. System discards unsaved changes
  *a4. System returns to [previous page/screen]
  *a5. Use case ends
```

## Postconditions

### Success Postconditions

**Characteristics**:

success_postcondition_rules[6]{rule,explanation,example}:
Guaranteed outcome,MUST be true after success,"User account created and active"
Observable state,Can be verified by checking system,"Order status is 'Confirmed'"
Data changes,Persistent changes to data,"Transaction recorded in audit log"
State transitions,Entity moved to new state,"Invoice status changed to 'Paid'"
Notifications sent,Messages delivered,"Confirmation email sent to user"
Side effects,Related changes occurred,"Inventory decreased by quantity ordered"

**Good Success Postconditions**:
- User authenticated with active session (ID: SESSION_ID)
- New invoice created with status "Draft" (Invoice-ID: INV-2024-0001)
- Notification email sent to user@example.com
- Account balance decreased by $50.00
- Audit log entry created with timestamp and user ID

### Failure Postconditions

**Characteristics**:

failure_postcondition_rules[5]{rule,explanation,example}:
Safe state,System in consistent state,"No partial data saved; transaction rolled back"
No side effects,No unintended changes,"Inventory levels unchanged"
Error logged,Failure recorded for analysis,"Error logged with code ERR-500"
User informed,User aware of failure,"Error message displayed to user"
Rollback complete,All changes reverted,"Database transaction rolled back"

**Good Failure Postconditions**:
- No user account created; email remains available for registration
- Database transaction rolled back; no partial data saved
- Error logged with error code and timestamp
- User displayed error message with actionable guidance
- System resources released (connections closed, locks released)

## Business Rules

### Types of Business Rules

business_rule_types[6]{type,description,example,enforcement_point}:
Validation Rule,Data format or value constraints,"Email must be valid RFC 5322 format",Input validation step
Calculation Rule,How derived values are computed,"Total = Subtotal + Tax - Discount",Calculation step
Process Rule,Required sequence or workflow,"Invoice must be approved before payment",Flow control
Authorization Rule,Who can perform what action,"Only managers can approve orders over $10000",Precondition or step
State Rule,Valid state transitions,"Order can only be cancelled if status is 'Pending'",State change step
Time-based Rule,Temporal constraints,"Password expires after 90 days",Time-dependent validation

### Business Rule Documentation

**Format**:
```
business_rules[N]{rule_id,category,rule_description,applies_to_step}:
BR-001,Validation,Email must be unique in system,Step 8
BR-002,Authorization,Only account owner can modify profile,Precondition
BR-003,Calculation,Shipping cost = weight * rate + fuel_surcharge,Step 12
BR-004,Process,Cannot delete order with shipped status,Step 5
```

## Non-Functional Requirements

### NFR Categories

nfr_categories[8]{category,description,example_metrics}:
Performance,Response time throughput,"Page load < 2s; 1000 concurrent users"
Scalability,Growth capacity,"Support 10x user growth without redesign"
Availability,Uptime reliability,"99.9% uptime; max 8 hours planned downtime/year"
Security,Protection controls,"SSL/TLS encryption; RBAC; audit logging"
Usability,User experience,"< 5 clicks to complete task; mobile responsive"
Maintainability,Ease of updates,"< 1 hour to deploy hotfix; modular design"
Compatibility,Integration standards,"REST API; OAuth 2.0; JSON format"
Compliance,Regulatory requirements,"GDPR compliant; HIPAA certified; SOC 2"

### NFR Documentation Format

```
nfr[N]{category,requirement,measurement,priority}:
Performance,Search results display within 1 second,Response time: <1000ms,High
Security,All data encrypted at rest and in transit,AES-256 encryption + TLS 1.3,Critical
Usability,Form completion without documentation,Task success rate > 90%,Medium
Availability,Service available 24/7 except maintenance,Uptime: 99.5%,High
```

## Traceability

### Requirement Traceability Matrix

traceability_elements[5]{element,links_to,purpose,format}:
UseCase ID,Unique identifier,Primary key for referencing,UC-[number] (e.g. UC-001)
Requirement IDs,Business/functional requirements,Shows requirement coverage,REQ-[number] or US-[number]
Test Case IDs,Test cases,Ensures testability,TC-[number]
Related UseCases,Other dependent UseCases,Shows dependencies,Includes/Extends UC-[number]
User Story IDs,Agile user stories,Maps to agile artifacts,US-[number]

**Traceability Documentation**:
```
## Traceability

traceability[N]{link_type,id,description}:
Requirement,REQ-042,User authentication requirement
Requirement,REQ-043,Password complexity requirement
User Story,US-123,As a user I want to register
Test Cases,TC-201 TC-202 TC-203,Registration test scenarios
Related UseCases,UC-002,Resend Verification Email (included)
Related UseCases,UC-010,User Login (follows this UC)
```

## UseCase Relationships

### Relationship Types

relationship_types[4]{type,definition,notation,example}:
Include,Base UC always executes included UC,"«include» UC-[number]","UC-001 «include» UC-050 (Calculate Tax)"
Extend,Extension UC optionally extends base UC,"«extend» UC-[number]","UC-010 «extend» UC-011 (Two-Factor Auth)"
Generalization,Specialized UC inherits from general UC,"inherits from UC-[number]","UC-030 (Credit Card Payment) inherits UC-029 (Payment)"
Association,Actor interacts with UC,Line connecting actor to UC,"Customer -- UC-001 (Place Order)"

**Include Relationship Example**:
```
## UseCase: UC-001 Process Order

Main Success Scenario:
1. User adds items to cart
2. User proceeds to checkout
3. Include UC-050: Calculate Tax
4. Include UC-051: Calculate Shipping
5. User confirms order
6. Include UC-052: Process Payment
7. System creates order record
```

**Extend Relationship Example**:
```
## UseCase: UC-010 User Login

Note: This use case can be extended by:
- UC-011: Two-Factor Authentication (if user has 2FA enabled)
- UC-012: Security Question (if login from new device)

Main Success Scenario:
1. User enters credentials
2. System validates credentials
3. [Extension point: Additional authentication]
4. System creates session
5. System redirects to dashboard
```

## UseCase Complexity Levels

complexity_levels[4]{level,characteristics,typical_steps,extensions}:
Simple,Single actor straightforward flow,3-8 steps,0-2 extensions
Medium,Multiple actors or moderate branching,8-15 steps,3-6 extensions
Complex,Multiple actors significant branching,15-25 steps,7-15 extensions
Very Complex,Multiple systems complex business logic,25+ steps,15+ extensions (consider splitting)

**Complexity Guidelines**:
- **Split if**: UseCase exceeds 30 steps or has more than 20 extensions
- **Combine if**: Multiple UseCases differ only in minor details (use extensions instead)
- **Refactor if**: UseCase has deeply nested extensions (>3 levels)

## Special Scenarios

### Time-Based UseCases

**Scheduled/Batch Processing**:
```
## UseCase: UC-100 Generate Daily Sales Report

**Primary Actor**: System Scheduler

**Trigger**: System clock reaches 11:59 PM

**Preconditions**:
- All daily transactions are committed
- Previous day's report generated successfully
- Report storage has available space

Main Success Scenario:
1. System scheduler initiates daily report job
2. System queries all transactions from 12:00 AM to 11:59 PM
3. System calculates daily totals by category
4. System generates PDF report
5. System stores report in archive directory
6. System sends report to distribution list
7. System updates "last report date" to current date
8. System logs successful completion
```

### Real-Time/Event-Driven UseCases

**Event-Triggered Processing**:
```
## UseCase: UC-200 Process Incoming Webhook

**Primary Actor**: External Payment Gateway

**Trigger**: Webhook HTTP POST received on /api/webhook/payment

**Preconditions**:
- Webhook endpoint is active
- SSL certificate valid
- API authentication configured

Main Success Scenario:
1. External system sends webhook POST request
2. System receives webhook payload
3. System validates webhook signature
4. System parses JSON payload
5. System extracts payment confirmation details
6. System locates matching order by transaction ID
7. System updates order status to "Paid"
8. System sends confirmation email to customer
9. System returns HTTP 200 OK to webhook sender
10. System logs successful webhook processing
```

## Advanced Techniques

### UseCase Modeling Best Practices

modeling_practices[8]{practice,technique,benefit}:
Actor generalization,Group similar actors into general role,Reduces duplication; easier maintenance
UseCase generalization,Abstract common behavior into parent UC,Promotes reuse; consistent patterns
Include for reuse,Extract common sequences to included UC,DRY principle; single source of truth
Extend for variation,Handle optional behavior via extensions,Flexible behavior; clean base case
Boundary definition,Clearly define system boundary,Scope clarity; interface identification
Level consistency,Keep UseCases at consistent abstraction level,Comparable complexity; easier management
Goal-oriented,Focus on user goal not interaction sequence,User-centered; outcome-focused
Atomic goals,Each UC accomplishes single complete goal,Cohesive purpose; clear value

### UseCase Diagram Elements

**UML Notation**:

uml_elements[6]{element,symbol,purpose,example}:
Actor,Stick figure,"Represents user or external system","Customer (stick figure)"
UseCase,Oval/Ellipse,Represents system functionality,"Place Order (oval)"
System Boundary,Rectangle,Defines system scope,"System boundary box containing UseCases"
Association,Solid line,Actor interacts with UseCase,"Line from Customer to Place Order"
Include,Dashed arrow with «include»,Mandatory sub-UseCase,"Process Order → Calculate Tax"
Extend,Dashed arrow with «extend»,Optional extension,"Login ← Two-Factor Auth"

## UseCase Documentation Tools

recommended_tools[6]{tool,type,strengths,best_for}:
Markdown,Text-based,Simple version control human-readable,Agile teams; documentation as code
Enterprise Architect,UML tool,Professional diagrams model management,Large enterprises; formal modeling
Lucidchart,Diagramming,Collaborative visual UML diagrams,Distributed teams; stakeholder communication
Confluence,Wiki,Integration with Jira centralized docs,Atlassian ecosystem users
ReqView,Requirements tool,Requirements management traceability,Regulated industries; formal traceability
PlantUML,Text-to-diagram,Generate diagrams from text version control,Developers; automation; CI/CD integration

---
**File Size**: 431/500 lines max ✅
