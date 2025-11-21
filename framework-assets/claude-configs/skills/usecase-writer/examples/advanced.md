# UseCase Examples - Advanced

Complex UseCases with multiple actors, extensive extensions, and sophisticated business logic.

## Advanced Example Overview

advanced_examples[1]{id,title,domain,complexity,key_features}:
UC-002,Place Order,E-commerce,Very Complex,Multiple actors; payment processing; inventory management; 30+ steps; 15+ extensions

---

## Example: Complex UseCase - Place Order

This is a comprehensive example demonstrating all aspects of a complex real-world UseCase.

```markdown
## UseCase: UC-002 Place Order

**Brief Description**: Customer completes purchase of items in shopping cart through checkout process with payment and order confirmation

**Primary Actor**: Customer (Registered User)

**Secondary Actors**: Payment Gateway, Inventory Service, Email Service, Shipping Service, Tax Service

**Stakeholders and Interests**:
stakeholders[5]{stakeholder,interest}:
Customer,Complete purchase quickly securely and receive confirmation
Store Owner,Maximize successful transactions and revenue
Payment Processor,Securely process payment and receive transaction fees
Fulfillment Team,Receive accurate order details for processing and shipping
Finance Team,Accurate revenue recognition and financial reporting

**Preconditions**:
- Customer authenticated with active account
- Shopping cart contains at least one item
- Cart items are in stock and active
- Customer has saved shipping address
- Payment processing service operational

**Trigger**: Customer clicks "Proceed to Checkout" from shopping cart

**Main Success Scenario**:
1. Customer reviews cart items and quantities
2. Customer clicks "Proceed to Checkout"
3. System validates cart contents
4. System checks inventory availability for all items
5. System displays checkout page with sections:
   - Shipping address
   - Billing address
   - Payment method
   - Order summary
6. System loads customer's default shipping address
7. Customer reviews or changes shipping address
8. Customer selects shipping method (Standard, Express, Next-Day)
9. System calculates shipping cost based on method and destination
10. Include UC-050: Calculate Tax (based on shipping address)
11. System loads customer's saved payment method
12. Customer reviews or selects payment method
13. Customer enters CVV security code
14. System displays order summary:
    - Subtotal (sum of item prices)
    - Shipping cost
    - Tax
    - Discount (if applicable)
    - Total
15. Customer reviews order summary
16. Customer accepts terms and conditions
17. Customer clicks "Place Order"
18. System validates all required fields completed
19. System reserves inventory for all items
20. System creates pending order record
21. System initiates payment authorization
22. System sends payment details to payment gateway
23. Payment gateway authorizes payment
24. System receives payment authorization
25. System captures payment amount
26. System updates order status to "Confirmed"
27. System commits inventory reservation
28. System generates order confirmation number
29. System creates shipment request in shipping system
30. System sends order confirmation email with:
    - Order number
    - Items ordered
    - Shipping address
    - Total charged
    - Estimated delivery date
31. System displays order confirmation page
32. System empties shopping cart
33. System adds order to customer's order history

**Extensions**:

**4a. One or more items out of stock**
  4a1. System identifies out-of-stock items
  4a2. System displays "Some items are unavailable"
  4a3. System lists unavailable items with options:
    - Remove from cart
    - Save for later
    - Notify when available
  4a4. Customer selects action for each unavailable item
  4a5. System updates cart
  4a6. IF cart now empty: Use case ends
  4a7. IF cart has items: Resume at step 5

**4b. Price changed since item added to cart**
  4b1. System detects price difference
  4b2. System displays "Price updated" notice
  4b3. System shows old price and new price
  4b4. Customer accepts or removes item
  4b5. System updates cart
  4b6. Resume at step 5

**7a. Customer needs to add new shipping address**
  7a1. Customer clicks "Add New Address"
  7a2. Include UC-025: Add Shipping Address
  7a3. System validates address (format, deliverability)
  7a4. System saves address to customer profile
  7a5. System selects new address as shipping address
  7a6. Resume at step 8

**10a. Tax calculation service unavailable**
  10a1. System logs tax service error
  10a2. System applies default tax rate for state (fallback)
  10a3. System displays notice "Tax calculated using standard rate"
  10a4. System flags order for manual tax review
  10a5. Resume at step 11

**12a. Customer adds new payment method**
  12a1. Customer clicks "Add Payment Method"
  12a2. Include UC-030: Add Payment Method
  12a3. System validates payment method with gateway
  12a4. System saves payment method (tokenized)
  12a5. System selects new method as payment
  12a6. Resume at step 13

**16a. Customer does not accept terms and conditions**
  16a1. Customer attempts to place order without checkbox
  16a2. System prevents order submission
  16a3. System displays "Please accept terms and conditions"
  16a4. System highlights terms checkbox
  16a5. Resume at step 16

**18a. Required field validation fails**
  18a1. System identifies missing required fields
  18a2. System displays validation errors
  18a3. System highlights first invalid field
  18a4. Customer corrects errors
  18a5. Resume at step 17

**19a. Inventory reservation fails (items sold out)**
  19a1. System identifies items no longer available
  19a2. System releases any successfully reserved items
  19a3. System displays "Items no longer available"
  19a4. Branch to extension 4a

**23a. Payment authorization declined**
  23a1. Payment gateway returns decline reason code
  23a2. System releases inventory reservations
  23a3. System deletes pending order
  23a4. System displays user-friendly decline message:
    - "Insufficient funds" → "Payment could not be processed"
    - "Card expired" → "Payment method expired"
    - "Fraud suspected" → "Please contact your bank"
  23a5. System offers options:
    - Try different payment method
    - Update payment method details
    - Contact support
  23a6. Customer selects option
  23a7. IF different payment: Resume at step 12
  23a8. IF update details: Include UC-031: Update Payment Method; Resume at step 12
  23a9. IF contact support: Include UC-080: Contact Support; Use case ends

**23b. Payment gateway timeout**
  23b1. System waits for response (timeout: 30 seconds)
  23b2. System retries payment authorization (1 retry)
  23b3. IF retry successful: Resume at step 24
  23b4. IF retry fails:
    23b4a. System releases inventory
    23b4b. System marks order as "Payment Pending"
    23b4c. System displays "Payment processing. Check status in 5 minutes"
    23b4d. System sends payment status check to queue
    23b4e. Use case ends (background process will verify)

**25a. Payment capture fails**
  25a1. System logs capture failure
  25a2. System retries capture (2 retries, 5-second delay)
  25a3. IF retry successful: Resume at step 26
  25a4. IF all retries fail:
    25a4a. System voids authorization
    25a4b. System releases inventory
    25a4c. System marks order "Payment Failed"
    25a4d. System creates admin task to investigate
    25a4e. System displays "Order could not be completed. Contact support"
    25a4f. Use case ends in failure

**29a. Shipping service unavailable**
  29a1. System logs shipping service error
  29a2. System queues shipment request for retry
  29a3. System continues with order confirmation
  29a4. System creates task for fulfillment team
  29a5. Resume at step 30 (order confirmed; shipment pending)

**30a. Email delivery fails**
  30a1. System logs email failure
  30a2. System queues email for retry (3 attempts)
  30a3. System continues with order completion
  30a4. Resume at step 31

***a. Customer cancels checkout (before step 17)**
  *a1. Customer closes browser or clicks "Cancel"
  *a2. System retains cart contents
  *a3. System does NOT create order
  *a4. System clears any temporary reservations
  *a5. Use case ends

**Postconditions**:
**Success**:
- Order created with status "Confirmed"
- Payment authorized and captured
- Order total charged to customer payment method
- Inventory reduced by quantities ordered
- Shipment request created in shipping system
- Order confirmation email sent
- Shopping cart emptied
- Order added to customer order history
- Transaction logged for accounting

**Failure**:
- No order created
- No payment charged
- Inventory unchanged
- Shopping cart retained with items
- Customer notified of failure reason

**Business Rules**:
business_rules[12]{rule_id,rule_description}:
BR-030,Minimum order total: $10 (before shipping and tax)
BR-031,Maximum order quantity per item: 10 units
BR-032,Shipping cost = Base_Rate × Weight + Fuel_Surcharge
BR-033,Tax calculated based on shipping address jurisdiction
BR-034,Free shipping on orders over $50 (Standard shipping only)
BR-035,Payment authorization must complete within 30 seconds
BR-036,Inventory reserved for 10 minutes during checkout
BR-037,Discount codes validated at checkout (active not expired single-use)
BR-038,Cannot use multiple discount codes per order
BR-039,Express shipping only available for in-stock items
BR-040,PO Box addresses not allowed for Express or Next-Day shipping
BR-041,Order subtotal must match sum of item prices × quantities

**Non-Functional Requirements**:
nfr[7]{category,requirement}:
Performance,Checkout page loads within 2 seconds; Payment processing within 3 seconds
Security,PCI DSS compliant; Payment data encrypted; CVV not stored; TLS 1.3
Availability,Checkout available 24/7 with 99.9% uptime; Payment gateway redundancy
Usability,Mobile responsive; One-page checkout; Auto-save address; Progress indicator
Scalability,Handle 1000 concurrent checkouts; Support peak traffic (Black Friday)
Reliability,Payment idempotency prevents duplicate charges; Automatic retry for transient failures
Compliance,GDPR compliant; ADA accessible; Financial regulations for payment processing

**Traceability**:
traceability[7]{link_type,id,description}:
Requirement,REQ-200,E-commerce checkout requirements
Requirement,REQ-205,Payment processing requirements
User Story,US-045,As a customer I want to complete purchase
User Story,US-046,As a customer I want to choose shipping method
Test Cases,TC-400 to TC-420,Checkout scenarios (21 test cases)
Related UseCases,UC-025,Add Shipping Address (included)
Related UseCases,UC-030,Add Payment Method (included)
Related UseCases,UC-050,Calculate Tax (included)
Related UseCases,UC-031,Update Payment Method (extension 23a8)
Related UseCases,UC-080,Contact Support (extension 23a9)

**Performance Metrics**:
performance_metrics[5]{metric,target,measurement}:
Checkout Completion Rate,> 75%,Orders completed / Checkout initiated
Average Checkout Time,< 3 minutes,Time from step 2 to step 33
Payment Authorization Success,> 95%,Successful / Total authorization attempts
Inventory Accuracy,> 99.5%,Correct availability / Total checks
Email Delivery Rate,> 99%,Emails delivered / Emails sent

**Open Issues**:
- Should guest checkout be supported (without account)?
- Should system support split payment (e.g., gift card + credit card)?
- Should there be order editing after placement (limited time window)?
- International shipping support and currency conversion?
```

---

## Analysis of Complex UseCase

This example demonstrates advanced UseCase features:

### Complexity Indicators

complexity_analysis[8]{indicator,instance,explanation}:
Multiple secondary actors,5 external systems,Payment Gateway Inventory Email Shipping Tax services
Long main flow,33 steps,Comprehensive checkout process from cart to confirmation
Extensive extensions,15+ alternatives,Coverage of errors edge cases and business scenarios
Nested extensions,23a 23b 25a,Multiple failure modes at payment processing stage
Include relationships,3 includes,Delegates to UC-025 UC-030 UC-050 for reusable functionality
State management,Order status transitions,Pending → Confirmed or Failed with proper rollback
Transaction handling,Payment capture,Authorization capture void sequence with retry logic
Error recovery,Multiple retry strategies,Graceful degradation for non-critical failures

### Business Logic Patterns

patterns_demonstrated[6]{pattern,location,description}:
Reservation Pattern,Steps 19-27,Reserve → Process → Commit or Release sequence
Payment Two-Phase,Steps 21-25,Authorization then capture for financial safety
Graceful Degradation,Extensions 10a 29a,Continue with fallback when non-critical service fails
Retry with Backoff,Extensions 23b 25a,Automatic retry for transient failures
Idempotency,Step 21,Prevent duplicate orders from retry or double-click
Rollback on Failure,Extension 23a,Release resources when transaction cannot complete

### Integration Complexity

integration_points[5]{service,interaction_type,failure_handling}:
Payment Gateway,Synchronous API,Retry on timeout; graceful decline handling
Inventory Service,Database transaction,Reservation with timeout; rollback on failure
Tax Service,API call,Fallback to default rate if unavailable
Shipping Service,Asynchronous queue,Queue for retry if service down
Email Service,Asynchronous queue,Background retry; non-blocking failure

### Quality Attributes

quality_demonstrated[7]{attribute,implementation,benefit}:
Reliability,Multiple retry mechanisms,Handles transient failures automatically
Security,PCI DSS compliance mentioned,Payment data protection
Performance,Response time requirements,User experience expectations
Scalability,Concurrent checkout support,Peak load handling (Black Friday)
Maintainability,Clear extension numbering,Easy to update and extend
Traceability,Comprehensive links,Requirements to tests mapping
Testability,21 test case references,Complete test coverage

### Extension Patterns

extension_patterns[5]{pattern,examples,purpose}:
Validation Failure,4a 4b 18a,Handle invalid or changed data
Service Unavailable,10a 29a 30a,Graceful degradation strategies
Business Rule Violation,16a 19a,Enforce constraints and policies
Payment Failures,23a 23b 25a,Complex payment processing errors
User Actions,7a 12a *a,User-initiated alternatives

### Learning Points

key_learnings[8]{lesson,explanation}:
Comprehensive Extensions,Cover all realistic failure modes not just validation errors
Clear Rollback Strategy,Every failure point has explicit rollback or cleanup
Service Integration,Document behavior when external services fail or timeout
Business Rules Explicit,Complex rules documented separately and referenced
Multiple Postconditions,Success and failure states clearly distinguished
Traceability Matrix,Links to requirements user stories and test cases
Performance Metrics,Measurable success criteria for monitoring
Stakeholder Interests,Multiple stakeholders with different concerns documented

### When to Use Complex UseCases

use_complex_when[5]{scenario,rationale}:
Critical transactions,Financial or high-value operations requiring detailed specification
Multiple integrations,Many external systems requiring coordination
Complex business logic,Sophisticated rules validations and calculations
Regulatory compliance,Audit requirements necessitate detailed documentation
High-risk processes,Failures have significant business or user impact

### Managing Complexity

complexity_management[5]{technique,application}:
Include relationships,Extract reusable sub-UseCases (UC-025 UC-030 UC-050)
Extension numbering,Clear hierarchical structure for alternatives
State diagrams,Supplement with visual state transition diagrams
Sequence diagrams,Show actor and system interaction timing
Modular sections,Separate concerns (payment shipping inventory)

---
**File Size**: 420/500 lines max ✅
