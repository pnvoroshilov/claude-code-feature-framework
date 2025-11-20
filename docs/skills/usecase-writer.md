# UseCase Writer Skill

Expert skill for creating comprehensive, well-structured UseCases from requirements following industry standards (UML, Cockburn, IEEE 830, RUP).

## Overview

UseCase Writer transforms requirements into detailed, testable UseCases with proper structure, actor identification, and complete documentation. This skill follows industry-standard methodologies for professional requirements documentation.

## Location

`framework-assets/claude-skills/usecase-writer/`

**Files**:
- `SKILL.md` - Main skill instruction file (421 lines)
- `README.md` - Quick start guide (336 lines)
- `reference.md` - Standards and templates reference (467 lines)
- `examples/basic.md` - Simple use case examples (306 lines)
- `examples/intermediate.md` - Complex examples (474 lines)
- `examples/advanced.md` - Enterprise-level examples (376 lines)

## Automatic Activation

This skill automatically activates when you mention:

```
activation_keywords[15]:
use case
usecase
write use case
create use case
user flow
user scenario
acceptance criteria
actors and preconditions
main flow
alternative flow
extension flow
use case diagram
requirements analysis
business requirements
functional specification
```

**Example**:
```
User: "Document the login process as a use case"
→ UseCase Writer skill activates automatically
```

## Manual Activation

```bash
Skill: "usecase-writer"
```

## Core Capabilities

### 1. UseCase Creation
Create complete structured UseCases from raw requirements with all standard sections.

**Standard UseCase Structure**:
```
UseCase: [Name]
ID: UC-XXX
Priority: High/Medium/Low
Actors: [Primary, Secondary, Stakeholders]
Preconditions: [What must be true before]
Postconditions: [What is true after]
Main Success Scenario: [Step-by-step flow]
Extensions: [Alternative flows and exceptions]
Business Rules: [Constraints and policies]
Non-Functional Requirements: [Performance, security, etc.]
Related UseCases: [Dependencies and relationships]
```

### 2. Actor Analysis
Identify and document all actors with roles and interests.

**Actor Categories**:
- **Primary Actors**: Initiate the use case
- **Secondary Actors**: Support the use case
- **Stakeholders**: Have interest in the outcome

### 3. Flow Documentation
Write detailed step-by-step flows including main success scenario and all extensions.

**Flow Structure**:
```
Main Success Scenario:
1. Actor performs action
2. System responds
3. Actor continues...
4. System validates...

Extensions (Alternative Flows):
2a. Invalid input:
    2a1. System displays error
    2a2. Return to step 1
4a. Validation fails:
    4a1. System logs error
    4a2. Notify administrator
```

### 4. Standards Compliance
Follow UML, Cockburn, IEEE 830, and RUP standards for professional documentation.

**Standards Followed**:
- **UML**: Unified Modeling Language use case notation
- **Cockburn**: Alistair Cockburn's use case template
- **IEEE 830**: Software Requirements Specification standard
- **RUP**: Rational Unified Process methodology

### 5. Quality Validation
Ensure UseCases are complete, testable, unambiguous, and follow best practices.

**Quality Checklist**:
- ✅ Clear goal and scope
- ✅ All actors identified
- ✅ Preconditions and postconditions defined
- ✅ Main flow is complete
- ✅ Extensions cover all alternatives
- ✅ Business rules documented
- ✅ NFRs specified
- ✅ Testable and unambiguous

### 6. Traceability
Link UseCases to requirements, test cases, and related use cases.

### 7. Requirements Analysis
Extract and clarify functional requirements from user stories and business needs.

## When to Use This Skill

### Perfect For

1. **Requirements Documentation**
   - Convert user stories to use cases
   - Document system interactions
   - Clarify business requirements

2. **System Design**
   - Define system behavior
   - Identify actors and roles
   - Map user workflows

3. **Testing Preparation**
   - Create testable specifications
   - Define acceptance criteria
   - Plan test scenarios

4. **Stakeholder Communication**
   - Clear, structured documentation
   - Professional format
   - Standards-compliant output

### Not Ideal For

1. **Quick User Stories**
   - Use cases are more detailed
   - Agile stories may be sufficient

2. **Technical Implementation**
   - Use cases describe behavior, not implementation
   - Need separate technical specs

3. **Simple Features**
   - May be overkill for trivial features
   - User story might suffice

## UseCase Template

### Standard Format

```
UseCase: [Descriptive Name]
ID: UC-[Number]
Priority: [High/Medium/Low]
Status: [Draft/Review/Approved]

Actors:
- Primary: [Who initiates this use case]
- Secondary: [Who supports this use case]
- Stakeholders: [Who has interest in the outcome]

Goal: [What this use case achieves]

Scope: [System boundaries]

Level: [User goal/Subfunction/Summary]

Preconditions:
- [Condition 1]
- [Condition 2]

Postconditions:
Success:
- [Outcome 1]
- [Outcome 2]

Failure:
- [Outcome on failure]

Main Success Scenario:
1. [Actor action]
2. [System response]
3. [Actor continues]
4. [System validates]
5. [Success outcome]

Extensions (Alternative Flows):
[Step]a. [Condition]:
    [Step]a1. [Action]
    [Step]a2. [Resolution]
    Return to step [X] or END

[Step]b. [Another condition]:
    [Step]b1. [Action]
    [Step]b2. [Resolution]

Business Rules:
- BR1: [Business rule description]
- BR2: [Business constraint]

Non-Functional Requirements:
- Performance: [Response time requirements]
- Security: [Security constraints]
- Usability: [User experience requirements]
- Reliability: [Uptime requirements]

Related UseCases:
- Includes: [UC-XXX]
- Extends: [UC-XXX]
- Uses: [UC-XXX]

Notes:
[Additional context or considerations]
```

## Examples

### Example 1: User Login (Basic)

```
UseCase: User Login
ID: UC-001
Priority: High

Actors:
- Primary: User (customer, employee, admin)
- Secondary: Authentication Service
- Stakeholders: Security team, business owners

Goal: Allow user to securely access the system

Preconditions:
- User has valid account
- System is operational
- User is on login page

Postconditions:
Success:
- User is authenticated
- Session is created
- User redirected to dashboard

Failure:
- User remains on login page
- Error message displayed
- Failed attempt logged

Main Success Scenario:
1. User enters username and password
2. System validates credentials
3. System creates session
4. System redirects to dashboard
5. User sees personalized dashboard

Extensions:
2a. Invalid credentials:
    2a1. System displays "Invalid username or password"
    2a2. System logs failed attempt
    2a3. Return to step 1

2b. Account locked (3 failed attempts):
    2b1. System displays "Account locked. Contact support."
    2b2. System sends notification to security team
    2b3. END

2c. Password expired:
    2c1. System displays "Password expired"
    2c2. System redirects to password reset
    2c3. Continue to UC-002 (Password Reset)

Business Rules:
- BR1: Maximum 3 failed login attempts before account lock
- BR2: Session timeout after 30 minutes of inactivity
- BR3: Passwords must meet complexity requirements

Non-Functional Requirements:
- Performance: Login must complete within 2 seconds
- Security: Use bcrypt for password hashing
- Security: Implement HTTPS for all communications
- Usability: Clear error messages without exposing security details
- Reliability: 99.9% uptime for authentication service

Related UseCases:
- Extends: UC-002 (Password Reset)
- Uses: UC-010 (Two-Factor Authentication)
```

### Example 2: E-commerce Checkout (Intermediate)

```
UseCase: Complete Purchase Checkout
ID: UC-015
Priority: High

Actors:
- Primary: Customer
- Secondary: Payment Gateway, Inventory System, Email Service
- Stakeholders: Sales team, finance, customer service

Goal: Complete purchase transaction and confirm order

Preconditions:
- Customer is logged in
- Shopping cart has at least one item
- All items are in stock
- Shipping address is on file or provided

Postconditions:
Success:
- Payment processed
- Order created in database
- Inventory updated
- Confirmation email sent
- Customer redirected to order confirmation

Failure:
- Payment not processed
- Cart remains unchanged
- Error displayed to customer

Main Success Scenario:
1. Customer clicks "Proceed to Checkout"
2. System displays order summary
3. Customer reviews order details
4. Customer confirms shipping address
5. Customer selects payment method
6. Customer enters payment information
7. System validates payment information
8. System processes payment via gateway
9. System creates order record
10. System updates inventory
11. System sends confirmation email
12. System displays order confirmation
13. Customer views order confirmation

Extensions:
7a. Invalid payment information:
    7a1. System displays field-level errors
    7a2. Return to step 6

8a. Payment declined:
    8a1. System displays "Payment declined. Please use different payment method."
    8a2. System logs declined attempt
    8a3. Return to step 5

9a. Database error creating order:
    9a1. System initiates payment refund
    9a2. System displays "Transaction error. Please try again."
    9a3. System alerts administrator
    9a4. END

10a. Item out of stock (race condition):
    10a1. System initiates payment refund
    10a2. System removes unavailable items from order
    10a3. System displays "Some items no longer available"
    10a4. Return to step 2

3a. Customer modifies cart:
    3a1. Customer updates quantities or removes items
    3a2. System recalculates totals
    3a3. Return to step 2

4a. Customer changes shipping address:
    4a1. Customer enters new address
    4a2. System validates address
    4a3. System recalculates shipping cost
    4a4. Continue to step 5

Business Rules:
- BR1: Minimum order value: $10
- BR2: Free shipping for orders over $50
- BR3: Maximum 5 items per product in single order
- BR4: Sales tax calculated based on shipping address
- BR5: Payment must be processed within 5 minutes or cart expires

Non-Functional Requirements:
- Performance: Checkout process < 500ms per step
- Performance: Payment processing < 3 seconds
- Security: PCI DSS compliant payment handling
- Security: All payment data encrypted in transit
- Reliability: Payment gateway failover support
- Usability: Progress indicator throughout checkout
- Usability: Mobile-responsive design

Related UseCases:
- Includes: UC-016 (Process Payment)
- Includes: UC-017 (Update Inventory)
- Includes: UC-018 (Send Order Confirmation)
- Extends: UC-019 (Apply Discount Code)
- Uses: UC-004 (Validate Address)
```

## Best Practices

### 1. Start with User Goal
Focus on what the user wants to achieve:
```
✅ Good: "Complete Purchase Checkout"
❌ Poor: "Click Buy Button"
```

### 2. Use Active Voice
Write steps in active voice:
```
✅ Good: "User enters password"
❌ Poor: "Password is entered"
```

### 3. Keep Steps Atomic
Each step should be a single action:
```
✅ Good:
1. User enters email
2. User enters password
3. User clicks login

❌ Poor:
1. User enters credentials and clicks login
```

### 4. Number Extensions Properly
Use hierarchical numbering for extensions:
```
3a. First alternative at step 3
    3a1. Sub-step 1
    3a2. Sub-step 2
3b. Second alternative at step 3
    3b1. Sub-step 1
```

### 5. Document All Paths
Cover success, failure, and edge cases:
```
- Main flow (success path)
- Extensions (alternatives)
- Error handling
- Edge cases
- Race conditions
```

### 6. Be Specific but Technology-Agnostic
Describe behavior without implementation details:
```
✅ Good: "System validates user credentials"
❌ Poor: "System runs SQL query to check bcrypt hash"
```

## UseCase vs User Story

### User Story Format
```
As a [role]
I want [feature]
So that [benefit]

Acceptance Criteria:
- [Criterion 1]
- [Criterion 2]
```

### UseCase Advantage
- More detailed and structured
- Covers all scenarios (success + failures)
- Better for complex workflows
- More testable specifications
- Professional documentation standard

### When to Use Each
- **User Story**: Agile development, simple features, quick documentation
- **UseCase**: Complex workflows, formal documentation, regulatory requirements

## Traceability Matrix

Link use cases to other artifacts:

```
UC-001 (User Login)
├── Requirements
│   ├── REQ-001: User authentication required
│   └── REQ-002: Secure password handling
├── Test Cases
│   ├── TC-001: Valid login
│   ├── TC-002: Invalid credentials
│   └── TC-003: Account lockout
└── Related UseCases
    ├── UC-002: Password Reset
    └── UC-010: Two-Factor Authentication
```

## UseCase Modeling

### Include Relationship
```
UC-A <<includes>> UC-B

UC-015 (Checkout) includes UC-016 (Process Payment)
→ Checkout always invokes Process Payment
```

### Extend Relationship
```
UC-A <<extends>> UC-B

UC-019 (Apply Discount) extends UC-015 (Checkout)
→ Discount is optional extension to Checkout
```

### Generalization
```
UC-Generic
├── UC-Specific-A
└── UC-Specific-B

UC-001 (User Login)
├── UC-001a (Employee Login)
└── UC-001b (Customer Login)
```

## Integration with Framework

### With Task Management
```
1. Create task for feature
2. Use UseCase Writer skill to document requirements
3. Attach use case to task
4. Implement based on use case
5. Test against use case scenarios
```

### With Testing
```
UseCase → Test Scenarios → Test Cases

Main Success Scenario → Happy path test
Extensions → Negative tests
Business Rules → Validation tests
NFRs → Performance/security tests
```

### With Documentation
```
UseCase → API Documentation
UseCase → User Guide
UseCase → Technical Specifications
```

## Quality Checklist

Before finalizing a use case, verify:

- [ ] Clear, descriptive title
- [ ] All actors identified
- [ ] Primary actor and goal stated
- [ ] Preconditions complete
- [ ] Postconditions for success and failure
- [ ] Main scenario is complete end-to-end
- [ ] All extensions documented
- [ ] Business rules captured
- [ ] NFRs specified
- [ ] Related use cases linked
- [ ] Steps are testable
- [ ] Language is clear and unambiguous
- [ ] No implementation details leaked

## Troubleshooting

### UseCase Too Complex
**Issue**: UseCase has too many steps and extensions.

**Solution**:
- Split into multiple use cases
- Use "includes" relationship
- Extract subfunctions

### Unclear Actors
**Issue**: Not sure who the actors are.

**Solution**:
- Focus on who initiates (primary actor)
- Identify who supports (secondary actors)
- Note who cares about outcome (stakeholders)

### Missing Extensions
**Issue**: Not covering all scenarios.

**Solution**:
- Ask "What can go wrong at each step?"
- Consider validation failures
- Think about race conditions
- Review business rules for constraints

## Related Skills

- **TOON Format** - Document use cases in TOON for token efficiency
- **Requirements Analysis** - Extract requirements before writing use cases (future)
- **Test Strategy** - Convert use cases to test scenarios (future)

## Resources

### Documentation
- `framework-assets/claude-skills/usecase-writer/README.md` - Quick start (336 lines)
- `framework-assets/claude-skills/usecase-writer/SKILL.md` - Full skill (421 lines)
- `framework-assets/claude-skills/usecase-writer/reference.md` - Complete reference (467 lines)
- `framework-assets/claude-skills/usecase-writer/examples/basic.md` - Simple examples (306 lines)
- `framework-assets/claude-skills/usecase-writer/examples/intermediate.md` - Complex examples (474 lines)
- `framework-assets/claude-skills/usecase-writer/examples/advanced.md` - Enterprise examples (376 lines)

### Standards References
- UML 2.5 Specification
- Alistair Cockburn's "Writing Effective Use Cases"
- IEEE 830 Software Requirements Specification
- Rational Unified Process (RUP)

## Example Categories

The skill includes extensive examples across three levels:

### Basic Examples (306 lines)
- Simple login
- Registration
- Password reset
- Profile update
- Search functionality

### Intermediate Examples (474 lines)
- E-commerce checkout
- Multi-step wizards
- Admin dashboards
- Report generation
- Notification systems

### Advanced Examples (376 lines)
- Complex workflows
- Multi-actor systems
- Integration scenarios
- Enterprise processes
- Regulatory compliance

## Skill Version

**Version**: 1.0
**Last Updated**: 2025-11-20
**Status**: Active
**Category**: Requirements Analysis

---

**Total Documentation**: 2,380 lines
**Standards**: UML, Cockburn, IEEE 830, RUP
**Example Count**: 15+ complete use cases
**Complexity Levels**: Basic, Intermediate, Advanced
