# UseCase Writer

Expert skill for creating comprehensive, well-structured UseCases from requirements following industry standards (UML, Cockburn, IEEE 830).

## What This Skill Does

Transforms requirements into detailed, testable UseCases with:
- **Actor identification** - Primary, secondary, and stakeholder analysis
- **Structured flows** - Main success scenario and extensive alternative paths
- **Complete documentation** - Preconditions, postconditions, business rules, NFRs
- **Standards compliance** - UML, Cockburn, IEEE 830, RUP methodologies
- **Quality assurance** - Testable, clear, unambiguous use case documentation

## Automatic Activation

This skill activates when you mention:

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

## Core Capabilities

capabilities[7]{capability,description}:
UseCase Creation,Create complete structured UseCases from raw requirements with all standard sections
Actor Analysis,Identify and document all actors (primary secondary stakeholders) with roles and interests
Flow Documentation,Write detailed step-by-step flows including main success scenario and all extensions
Standards Compliance,Follow UML Cockburn IEEE 830 and RUP standards for professional documentation
Quality Validation,Ensure UseCases are complete testable unambiguous and follow best practices
Traceability,Link UseCases to requirements test cases and related use cases
Requirements Analysis,Extract and clarify functional requirements from user stories and business needs

## When to Use This Skill

**Perfect for**:
- Converting user stories into detailed use cases
- Documenting system interactions and workflows
- Creating testable specifications for developers
- Defining acceptance criteria for features
- Analyzing and clarifying requirements
- Bridging gap between business and technical teams

**Use this skill when you need to**:
- Document "how user interacts with system to achieve goal"
- Create specifications that developers can implement
- Define acceptance criteria that QA can test
- Analyze all possible scenarios including errors and alternatives
- Ensure requirements are complete and unambiguous

## Quick Start Examples

### Example 1: Basic UseCase Request

**User**: "Create a use case for user login"

**Skill provides**:
```markdown
## UseCase: UC-010 User Login

**Primary Actor**: User (Registered Customer)

**Preconditions**:
- User has registered account
- User is on login page
- System is operational

**Trigger**: User navigates to login page

**Main Success Scenario**:
1. User enters username
2. User enters password
3. User clicks "Login" button
4. System validates credentials
5. System creates session
6. System redirects to dashboard

**Extensions**:
**4a. Invalid credentials**
  4a1. System displays "Invalid username or password"
  4a2. System increments failed login counter
  4a3. Resume at step 1

**4b. Account locked**
  4b1. System displays "Account locked"
  4b2. System sends unlock email
  4b3. Use case ends
```

### Example 2: Complex UseCase from Requirements

**User**: "I have user story: 'As a customer, I want to place an order so I can purchase products.' Create detailed use case."

**Skill provides**:
- Complete UseCase with all sections
- Multiple actors (Customer, Payment Gateway, Inventory, Email)
- 30+ step main flow
- 15+ extension scenarios
- Business rules
- Non-functional requirements
- Traceability links

See `examples.md` for complete example (UC-002 Place Order).

### Example 3: Actor Identification

**User**: "What actors should I include for a leave approval system?"

**Skill provides**:

```
actors[5]{role,type,responsibilities}:
Employee,Primary,Initiates leave request; provides details
Manager,Primary,Reviews and approves/rejects requests
HR Administrator,Secondary,Manages leave policies; handles exceptions
Payroll System,Secondary,Receives approved leave for salary calculation
Email Service,Secondary,Sends notifications to all parties
```

## File Structure

files[6]{file,purpose,size_lines}:
SKILL.md,Main skill documentation with templates and best practices,421/500
reference.md,Detailed standards formats and methodologies,467/500
examples/basic.md,Simple UseCases (2 examples),295/500
examples/intermediate.md,Medium complexity UseCases (3 examples),445/500
examples/advanced.md,Complex UseCase with full analysis (1 example),420/500
README.md,Quick start guide and overview,You are here!

## UseCase Template

Quick reference template:

```markdown
## UseCase: [UC-ID] [Title]

**Brief Description**: [One sentence goal]

**Primary Actor**: [Role who initiates]

**Secondary Actors**: [Supporting actors/systems]

**Preconditions**:
- [Required state 1]
- [Required state 2]

**Trigger**: [Event that starts use case]

**Main Success Scenario**:
1. [Actor] [action]
2. System [response]
3. [Continue step by step...]

**Extensions**:
**Na. [Condition]**:
  Na1. [Alternative action]
  Na2. [Resolution]

**Postconditions**:
**Success**: [Guaranteed outcome]
**Failure**: [Safe state if fails]

**Business Rules**:
BR-XXX: [Rule description]
```

## Key Principles

principles[8]{principle,explanation}:
One Goal,Each UseCase accomplishes ONE clear business goal
Actor Focus,Write from actor's perspective not system implementation
Testable Steps,Every step must be observable and testable by QA
Active Voice,Clear subject and action in each step (Actor does X)
Complete Scenarios,Include all realistic paths not just happy path
Business Language,Use domain terminology understandable to stakeholders
Standards Based,Follow UML Cockburn or IEEE 830 formatting
Traceability,Link to requirements test cases and related use cases

## Common UseCase Patterns

The skill includes templates for:

patterns[5]{pattern,use_case,file_location}:
CRUD Operations,Create Read Update Delete entities,SKILL.md Pattern 1
Authentication,Login logout registration password reset,SKILL.md Pattern 2
Search and Filter,Search with filters pagination sorting,SKILL.md Pattern 3
Approval Workflow,Multi-step approval with notifications,examples.md UC-004
E-commerce Checkout,Shopping cart payment shipping,examples.md UC-002

## Quality Standards

The skill ensures UseCases meet these criteria:

quality_standards[10]{criterion,requirement}:
Completeness,All required sections present (actors preconditions flows postconditions)
Clarity,Each step unambiguous and specific
Testability,QA can create test cases directly from steps
Actor Identification,All actors properly identified and roles clear
Extension Coverage,All realistic alternative and error paths documented
Business Rules,Constraints and validations documented and linked
Numbering Consistency,Hierarchical numbering (1 2 3 3a 3a1) throughout
Postconditions,Success and failure outcomes clearly stated
Traceability,Links to requirements test cases and related use cases
Stakeholder Validation,Non-technical readers can understand

## Technologies Covered

technologies[4]{standard,description,compliance_level}:
UML UseCases,Unified Modeling Language use case notation,Full support - diagrams and structure
Cockburn Format,Alistair Cockburn's detailed use case style,Full support - recommended format
IEEE 830,IEEE Recommended Practice for Software Requirements,Full support - formal documentation
RUP,Rational Unified Process use case approach,Full support - iterative development

## Tips for Best Results

tips[10]{tip,explanation}:
Start with actor,Identify who benefits from use case before writing flows
Write main flow first,Document happy path completely before adding extensions
Be specific,Use concrete actions and data not vague terms like 'process'
Number consistently,Use hierarchical numbering for easy reference (3a 3a1 3a2)
Include all extensions,Document every realistic alternative and error path
Business focus,Avoid technical implementation details focus on what not how
Review with stakeholders,Validate use cases with business users not just developers
Link requirements,Maintain traceability to original requirements and test cases
One action per step,Each step is single discrete testable action
Test it,Try creating test cases from use case to verify testability

## Example Domains Covered

The skill provides examples across:

example_domains[8]{domain,use_case,complexity}:
Authentication,User Registration (UC-001),Medium - Email verification; password rules
E-commerce,Place Order (UC-002),Complex - Payment; inventory; shipping
Search,Search Products (UC-003),Simple - Basic flow with filters
Workflow,Approve Leave Request (UC-004),Medium - Multi-step approval
Finance,Generate Invoice (UC-005),Medium - Calculations; PDF; email
System Admin,Backup Database (UC-006),Simple - Scheduled system task
Customer Service,Submit Support Ticket (UC-007),Medium - File attachments; routing
E-commerce,Process Refund (UC-008),Complex - Payment reversal; inventory

## How It Works

workflow[5]{step,action}:
1. Analyze,Extract requirements and identify actors goals and constraints
2. Structure,Create UseCase with all standard sections in proper format
3. Document Flows,Write main success scenario with numbered steps
4. Add Extensions,Document all alternative flows and error handling
5. Validate,Ensure completeness testability and standards compliance

## Best Practices Included

The skill guides you through:

best_practices[12]{category,practice}:
Actor Naming,Use role names not personal names (Customer not John)
Active Voice,Write steps in active voice with clear subject
Numbering,Use hierarchical numbering for extensions (3a 3a1)
One Goal,Each UseCase achieves ONE clear business goal
Testability,Every step must be testable and verifiable
User Perspective,Write from user's point of view not system
Preconditions,Keep preconditions minimal and verifiable
Postconditions,Postconditions must be guaranteed outcomes
Extensions Placement,Place extension at step where it diverges
Completeness,Include all realistic scenarios not just happy path
Business Language,Use domain terminology not technical jargon
Atomic Steps,Each step is single meaningful action

## Standards Compliance

The skill ensures compliance with:

standards_compliance[4]{standard,compliance_areas}:
UML 2.5,Actor identification; use case diagrams; relationships (include extend generalize)
Cockburn Template,Structured format; extensions; goal levels; stakeholder interests
IEEE 830-1998,Requirements specification; traceability; completeness; consistency
IIBA BABOK,Business analysis perspective; requirements elicitation; stakeholder management

## Integration with Development

The skill bridges requirements and implementation:

integration_points[4]{artifact,usecase_mapping}:
User Stories,UseCases expand user stories into detailed specifications
Acceptance Criteria,UseCase steps and extensions become test scenarios
Test Cases,Each flow and extension maps to specific test case
Implementation,Developers implement system responses in each step

## Need More Details?

detailed_resources[5]{resource,description}:
SKILL.md,Complete instructions templates patterns and best practices
reference.md,Detailed standards formats methodologies and advanced techniques
examples/basic.md,Simple UseCases: Search Products and Backup Database
examples/intermediate.md,Medium complexity: Registration Leave Approval Support Ticket
examples/advanced.md,Complex UseCase: Place Order with complete analysis

## Typical Workflow

When you ask for a UseCase, the skill will:

typical_workflow[8]{step,what_happens}:
1. Clarify,Ask clarifying questions about requirements if needed
2. Identify Actors,Determine primary secondary actors and stakeholders
3. Define Goal,Establish single clear goal use case achieves
4. List Preconditions,Identify required system state before execution
5. Write Main Flow,Document step-by-step happy path from trigger to completion
6. Add Extensions,Document all alternative flows and error scenarios
7. Define Postconditions,State guaranteed outcomes for success and failure
8. Add Metadata,Include business rules NFRs and traceability links

---

**Total Skill Size**: 2,048 lines across 6 files (all under 500-line limit per file)

**Documentation Coverage**:
- ✅ Complete UseCase templates
- ✅ Industry standards (UML, Cockburn, IEEE 830)
- ✅ 6 full real-world examples (basic, intermediate, advanced)
- ✅ Best practices and common patterns
- ✅ Quality validation criteria
- ✅ TOON format for structured data throughout

**Ready to use!** Simply mention use cases, flows, or requirements analysis to activate this skill.
