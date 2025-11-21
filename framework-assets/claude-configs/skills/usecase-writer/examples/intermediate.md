# UseCase Examples - Intermediate

Medium complexity UseCases with multiple actors, workflows, and business rules.

## Intermediate Examples Overview

intermediate_examples[3]{id,title,domain,key_features}:
UC-001,User Registration,Authentication,Email verification; password validation; multiple extensions
UC-004,Approve Leave Request,HR Workflow,Multi-step approval; notifications; policy enforcement
UC-007,Submit Support Ticket,Customer Service,File attachments; priority assignment; routing

---

## Example 1: User Registration

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

---

## Example 2: Approve Leave Request

```markdown
## UseCase: UC-004 Approve Leave Request

**Brief Description**: Manager reviews and approves or rejects employee leave request

**Primary Actor**: Manager

**Secondary Actors**: Employee (requestor), HR System, Email Service

**Stakeholders and Interests**:
stakeholders[4]{stakeholder,interest}:
Manager,Efficiently manage team availability and approve valid requests
Employee,Receive timely decision on leave request
HR Department,Maintain accurate leave records and policy compliance
Payroll Team,Accurate leave data for salary calculations

**Preconditions**:
- Leave request submitted by employee (status = 'Pending')
- Manager has 'Approver' role for employee's department
- Manager is authenticated
- Leave policy rules configured in system

**Trigger**: Manager selects pending leave request from approval queue

**Main Success Scenario**:
1. Manager navigates to Leave Approvals dashboard
2. System displays list of pending requests assigned to manager
3. System shows request count by priority (urgent, standard)
4. Manager selects specific leave request
5. System retrieves request details
6. System displays:
   - Employee name and department
   - Leave type (vacation, sick, personal)
   - Start date and end date
   - Duration (days/hours)
   - Reason/comments
   - Employee's current leave balance
   - Team calendar showing overlapping absences
7. Manager reviews request details
8. Manager checks team calendar for conflicts
9. Manager verifies leave balance sufficient
10. Manager enters approval comments (optional)
11. Manager clicks "Approve" button
12. System validates leave balance
13. System validates no policy violations
14. System updates request status to "Approved"
15. System deducts days from employee's leave balance
16. System updates team calendar with approved leave
17. System sends approval email to employee
18. System sends notification to HR system
19. System displays "Request approved successfully" confirmation
20. System returns to pending requests list

**Extensions**:

**8a. Conflict detected - Another team member has overlapping leave**
  8a1. System highlights conflict in team calendar
  8a2. System displays warning "Potential coverage issue"
  8a3. Manager decides to:
    8a3a. Approve despite conflict, or
    8a3b. Discuss with employee (pause decision)
  8a4. If 8a3b: Manager adds comment requesting employee contact
  8a5. If 8a3b: Resume at step 20 without approval

**9a. Insufficient leave balance**
  9a1. System displays "Insufficient leave balance"
  9a2. System shows:
    - Available balance: X days
    - Requested: Y days
    - Shortfall: Y-X days
  9a3. Manager considers options:
    9a3a. Reject request, or
    9a3b. Approve partial leave, or
    9a3c. Approve as unpaid leave (if policy allows)
  9a4. Manager selects option
  9a5. If 9a3a: Branch to extension 11a
  9a6. If 9a3b: Manager modifies dates; Resume at step 12
  9a7. If 9a3c: Manager changes leave type to "Unpaid"; Resume at step 12

**11a. Manager rejects request**
  11a1. System displays rejection reason form
  11a2. Manager enters mandatory rejection reason
  11a3. Manager clicks "Reject" button
  11a4. System updates request status to "Rejected"
  11a5. System does NOT deduct from leave balance
  11a6. System sends rejection email with reason to employee
  11a7. System logs rejection in audit trail
  11a8. System displays "Request rejected" confirmation
  11a9. Resume at step 20

**13a. Policy violation detected**
  13a1. System identifies policy violation (e.g., max consecutive days exceeded)
  13a2. System displays policy violation warning
  13a3. System shows violated policy details
  13a4. Manager options:
    13a4a. Request HR override approval, or
    13a4b. Reject request with policy explanation
  13a5. If 13a4a: Include UC-045: Request Policy Override
  13a6. If 13a4b: Branch to extension 11a

**18a. Email notification fails**
  18a1. System logs email delivery failure
  18a2. System queues email for retry (3 attempts)
  18a3. System continues with approval process
  18a4. System creates task for admin to verify notification
  18a5. Resume at step 19

***a. Manager cancels approval process**
  *a1. Manager clicks "Cancel" or "Back"
  *a2. System displays "Discard changes?" confirmation
  *a3. Manager confirms cancellation
  *a4. System does NOT update request status
  *a5. System returns to pending requests list
  *a6. Use case ends

**Postconditions**:
**Success (Approved)**:
- Leave request status = "Approved"
- Employee leave balance updated (reduced)
- Team calendar updated with leave dates
- Employee notified via email
- HR system updated
- Audit log entry created

**Success (Rejected)**:
- Leave request status = "Rejected"
- Employee leave balance unchanged
- Team calendar unchanged
- Employee notified with rejection reason
- Audit log entry created

**Failure**:
- Leave request status remains "Pending"
- No changes to leave balance or calendar
- Manager notified of failure reason

**Business Rules**:
business_rules[8]{rule_id,rule_description}:
BR-020,Manager can only approve requests for direct reports
BR-021,Leave request must be submitted minimum 2 weeks in advance (except sick leave)
BR-022,Maximum consecutive leave days: 20 days (requires HR approval for more)
BR-023,Minimum leave increment: 0.5 days
BR-024,Employee must have sufficient leave balance (except unpaid leave)
BR-025,Rejection requires mandatory reason (minimum 20 characters)
BR-026,Approved leave cannot be cancelled within 48 hours of start date
BR-027,Manager must respond to request within 5 business days

**Non-Functional Requirements**:
nfr[5]{category,requirement}:
Performance,Approval action completes within 2 seconds
Availability,System available during business hours (99.5% uptime)
Security,Only manager with proper role can approve; all actions logged
Usability,One-click approval for requests with no conflicts
Compliance,GDPR compliant; leave data retained for 7 years per labor law

**Traceability**:
traceability[4]{link_type,id,description}:
Requirement,REQ-150,Leave management system requirements
User Story,US-089,As a manager I want to approve leave requests
Test Cases,TC-300 TC-301 TC-302,Approval scenarios (approve reject conflict)
Related UseCases,UC-045,Request Policy Override (included in extension 13a)
```

---

## Example 3: Submit Support Ticket

```markdown
## UseCase: UC-007 Submit Support Ticket

**Brief Description**: Customer creates support ticket to report issue or request assistance, which is categorized and routed to appropriate support team

**Primary Actor**: Customer (Registered User)

**Secondary Actors**: Support Routing Service, Email Service, Support Agent (receives ticket)

**Stakeholders and Interests**:
stakeholders[5]{stakeholder,interest}:
Customer,Quick issue resolution; clear communication; ticket tracking
Support Team,Accurate issue description; proper categorization; manageable workload
Support Manager,Efficient ticket routing; SLA compliance; customer satisfaction metrics
Product Team,Feedback on product issues; bug identification; feature requests
Quality Assurance,Issue tracking; pattern recognition; improvement opportunities

**Preconditions**:
- Customer authenticated with active account
- Support ticket system operational
- At least one support team available
- Customer has product/service to report on

**Trigger**: Customer clicks "Get Help" or "Submit Ticket" from support page

**Main Success Scenario**:
1. Customer navigates to support page
2. System displays support options (Search KB, Chat, Submit Ticket)
3. Customer selects "Submit Ticket"
4. System displays ticket submission form with fields:
   - Subject (required)
   - Category (dropdown: Technical, Billing, Feature Request, Bug Report)
   - Priority (Auto-determined or manual)
   - Description (required, rich text)
   - Affected product/service (dropdown)
   - File attachments (optional, max 5 files, 10MB each)
5. System pre-populates customer information (name, email, account ID)
6. Customer enters ticket subject
7. Customer selects category
8. System displays category-specific fields:
   - Technical: Error message, steps to reproduce
   - Billing: Invoice number, transaction date
   - Bug Report: Expected behavior, actual behavior, environment
9. Customer fills category-specific fields
10. Customer enters detailed description
11. Customer selects affected product/service
12. Customer sets priority (if allowed) or system determines priority
13. Customer optionally attaches screenshots or log files
14. Customer reviews ticket details
15. Customer clicks "Submit Ticket"
16. System validates required fields
17. System validates attachments (size, format, virus scan)
18. System analyzes ticket content for auto-categorization
19. System assigns priority based on:
    - Keywords (critical, urgent, down, not working)
    - Customer tier (premium, enterprise, standard)
    - Category (billing = high, feature request = medium)
20. System generates unique ticket ID (TICK-YYYYMMDD-XXXX)
21. System determines routing based on:
    - Category
    - Product/service
    - Priority
    - Team availability
22. System assigns ticket to appropriate support queue
23. System creates ticket record in database
24. System sends confirmation email to customer with:
    - Ticket ID
    - Subject and description
    - Priority and expected response time (SLA)
    - Link to track ticket status
25. System sends notification to assigned support team
26. System displays confirmation page with ticket details
27. System adds ticket to customer's support history

**Extensions**:

**7a. Customer unsure of category**
  7a1. Customer hovers over category for description
  7a2. System displays category tooltip with examples
  7a3. Customer selects best-match category
  7a4. Resume at step 8

**13a. Attachment upload fails**
  13a1. System detects upload error
  13a2. System displays "Upload failed. Please try again"
  13a3. Customer retries upload or removes attachment
  13a4. Resume at step 13

**17a. Attachment fails virus scan**
  17a1. System quarantines suspicious file
  17a2. System displays "File rejected for security reasons"
  17a3. System logs security event
  17a4. Customer removes or replaces attachment
  17a5. Resume at step 14

**18a. System detects duplicate ticket**
  18a1. System finds similar open ticket by same customer (< 24 hours old)
  18a2. System displays "You have a similar open ticket"
  18a3. System shows existing ticket details
  18a4. Customer confirms:
    18a4a. Yes - Add comment to existing: Branch to UC-008
    18a4b. No - Continue with new ticket: Resume at step 19

**21a. No support team available (outside business hours)**
  21a1. System checks support schedule
  21a2. System assigns to general queue for next business day
  21a3. System adjusts SLA response time
  21a4. System displays "Submitted outside business hours"
  21a5. Resume at step 22

**24a. Confirmation email delivery fails**
  24a1. System logs email failure
  24a2. System queues email for retry
  24a3. System continues with ticket creation
  24a4. Resume at step 26

***a. Customer cancels ticket submission**
  *a1. Customer clicks "Cancel"
  *a2. System displays "Save as draft?" dialog
  *a3. Customer chooses save or discard
  *a4. Use case ends

**Postconditions**:
**Success**:
- Support ticket created with unique ID
- Ticket assigned to support queue
- Customer notified via email
- Support team notified
- Attachments stored
- SLA timer started

**Failure**:
- No ticket created
- Form data retained
- Customer notified of failure

**Business Rules**:
business_rules[8]{rule_id,rule_description}:
BR-070,Subject: 10-100 characters; Description: 20-5000 characters
BR-071,Max 5 attachments; 10MB per file; 50MB total
BR-072,Allowed types: jpg png pdf txt log docx xlsx
BR-073,Priority SLA: Critical (1h) High (4h) Medium (24h) Low (48h)
BR-074,Enterprise customers get 50% faster SLA
BR-075,Duplicate detection: 24h window; 80% similarity
BR-076,After-hours tickets: SLA starts next business day
BR-077,Customer can edit ticket within 15 minutes

**Non-Functional Requirements**:
nfr[4]{category,requirement}:
Performance,Submission completes within 3 seconds
Usability,Mobile responsive; inline validation; auto-save every 30s
Security,Attachments virus scanned; data encrypted; access logged
Availability,99.9% uptime; graceful degradation

**Traceability**:
traceability[4]{link_type,id,description}:
Requirement,REQ-700,Customer support system requirements
User Story,US-150,As a customer I want to submit ticket
Test Cases,TC-700 to TC-715,16 ticket submission test scenarios
Related UseCases,UC-008,Add Comment to Ticket (extension 18a4a)
```

---

## Key Takeaways from Intermediate Examples

takeaways[6]{lesson,example,explanation}:
Multi-actor coordination,UC-004 UC-007,Multiple secondary actors requiring notifications and integration
Workflow states,UC-001 UC-004,Status changes tracked through workflow (Pending → Approved/Rejected)
Policy enforcement,UC-004,Business rules enforced with validation and override mechanisms
File handling,UC-007,Attachment upload validation virus scanning size limits
Auto-categorization,UC-007,System intelligently determines priority and routing
Include relationships,UC-001 UC-004,UseCases reference other UseCases for complex flows

---
**File Size**: 445/500 lines max ✅
