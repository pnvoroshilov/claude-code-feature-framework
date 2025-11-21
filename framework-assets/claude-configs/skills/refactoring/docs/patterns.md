# Refactoring Patterns Catalog

Complete catalog of refactoring techniques organized by category, with detailed examples and step-by-step instructions.

## Table of Contents

- [Method-Level Refactorings](#method-level-refactorings)
- [Class-Level Refactorings](#class-level-refactorings)
- [Data Refactorings](#data-refactorings)
- [Conditional Refactorings](#conditional-refactorings)
- [API Refactorings](#api-refactorings)
- [Hierarchical Refactorings](#hierarchical-refactorings)
- [Pattern Application](#pattern-application)
- [Anti-Pattern Elimination](#anti-pattern-elimination)

## Method-Level Refactorings

### Extract Method

**When**: Method is too long or does multiple things
**Goal**: Create focused, reusable methods

**Before**:
```python
def print_owing(amount):
    print_banner()

    # Print details
    print(f"name: {name}")
    print(f"amount: {amount}")
```

**After**:
```python
def print_owing(amount):
    print_banner()
    print_details(amount)

def print_details(amount):
    print(f"name: {name}")
    print(f"amount: {amount}")
```

**Steps**:
1. Identify code segment to extract
2. Create new method with intention-revealing name
3. Copy code to new method
4. Replace original with method call
5. Run tests
6. Remove any duplicate variables

### Inline Method

**When**: Method body is as clear as method name
**Goal**: Remove unnecessary indirection

**Before**:
```java
public int getRating() {
    return moreThanFiveLateDeliveries() ? 2 : 1;
}

public boolean moreThanFiveLateDeliveries() {
    return numberOfLateDeliveries > 5;
}
```

**After**:
```java
public int getRating() {
    return numberOfLateDeliveries > 5 ? 2 : 1;
}
```

**Steps**:
1. Verify method is not overridden
2. Find all calls to method
3. Replace calls with method body
4. Run tests after each replacement
5. Remove method definition

### Rename Method

**When**: Method name doesn't reveal intention
**Goal**: Improve clarity through better naming

**Before**:
```javascript
function calc(d) {
    return d * 0.1;
}
```

**After**:
```javascript
function calculateDiscount(orderTotal) {
    return orderTotal * DISCOUNT_RATE;
}
```

**Steps**:
1. Create new method with better name
2. Copy old method body to new method
3. Make old method call new method
4. Find all references to old method
5. Update references to use new method
6. Remove old method
7. Run tests

### Extract Variable

**When**: Complex expression is hard to understand
**Goal**: Name intermediate results

**Before**:
```python
if (platform.toUpperCase().indexOf("MAC") > -1 and
    browser.toUpperCase().indexOf("IE") > -1 and
    wasInitialized() and resize > 0):
    # do something
```

**After**:
```python
is_mac_os = platform.toUpperCase().indexOf("MAC") > -1
is_ie_browser = browser.toUpperCase().indexOf("IE") > -1
was_resized = wasInitialized() and resize > 0

if is_mac_os and is_ie_browser and was_resized:
    # do something
```

### Inline Variable

**When**: Variable name doesn't add clarity
**Goal**: Remove unnecessary variables

**Before**:
```javascript
const basePrice = order.basePrice;
return basePrice > 1000;
```

**After**:
```javascript
return order.basePrice > 1000;
```

### Split Temporary Variable

**When**: Variable assigned multiple times for different purposes
**Goal**: One variable per purpose

**Before**:
```python
temp = 2 * (height + width)
print(temp)
temp = height * width
print(temp)
```

**After**:
```python
perimeter = 2 * (height + width)
print(perimeter)
area = height * width
print(area)
```

### Remove Assignments to Parameters

**When**: Parameter is reassigned in method
**Goal**: Avoid confusion, use temp variable

**Before**:
```java
int discount(int inputVal, int quantity) {
    if (inputVal > 50) inputVal -= 2;
    if (quantity > 100) inputVal -= 1;
    return inputVal;
}
```

**After**:
```java
int discount(int inputVal, int quantity) {
    int result = inputVal;
    if (inputVal > 50) result -= 2;
    if (quantity > 100) result -= 1;
    return result;
}
```

### Replace Method with Method Object

**When**: Long method with many local variables
**Goal**: Convert method to class for easier extraction

**Before**:
```python
def calculate_score(player):
    score = 0
    multiplier = 1
    # 50 lines using score, multiplier, and other locals
    return score
```

**After**:
```python
class ScoreCalculator:
    def __init__(self, player):
        self.player = player
        self.score = 0
        self.multiplier = 1

    def calculate(self):
        self._process_base_score()
        self._apply_bonuses()
        self._apply_multiplier()
        return self.score

    def _process_base_score(self):
        # Extracted method using instance variables

    def _apply_bonuses(self):
        # Extracted method using instance variables
```

## Class-Level Refactorings

### Extract Class

**When**: Class doing work of two or more classes
**Goal**: Split into focused classes

**Before**:
```python
class Person:
    def __init__(self, name, office_phone, office_extension):
        self.name = name
        self.office_phone = office_phone
        self.office_extension = office_extension

    def get_office_number(self):
        return f"{self.office_phone} x{self.office_extension}"
```

**After**:
```python
class Person:
    def __init__(self, name):
        self.name = name
        self.office_phone = TelephoneNumber()

class TelephoneNumber:
    def __init__(self, phone="", extension=""):
        self.phone = phone
        self.extension = extension

    def get_full_number(self):
        return f"{self.phone} x{self.extension}"
```

**Steps**:
1. Identify cohesive subset of fields/methods
2. Create new class
3. Add link from old class to new class
4. Move fields to new class
5. Move methods to new class
6. Reduce visibility of old class
7. Update all references

### Inline Class

**When**: Class isn't doing enough to justify existence
**Goal**: Merge into another class

**Before**:
```java
class Person {
    private TelephoneNumber phoneNumber;

    public String getPhoneNumber() {
        return phoneNumber.toString();
    }
}

class TelephoneNumber {
    private String number;

    public String toString() {
        return number;
    }
}
```

**After**:
```java
class Person {
    private String phoneNumber;

    public String getPhoneNumber() {
        return phoneNumber;
    }
}
```

### Extract Interface

**When**: Multiple clients use same subset of class
**Goal**: Define contract for subset

**Before**:
```typescript
class Employee {
    calculatePay(): number { }
    getName(): string { }
    getDepartment(): string { }
    reportHours(hours: number): void { }
}

// Payroll only needs calculatePay and reportHours
```

**After**:
```typescript
interface Payable {
    calculatePay(): number;
    reportHours(hours: number): void;
}

class Employee implements Payable {
    calculatePay(): number { }
    getName(): string { }
    getDepartment(): string { }
    reportHours(hours: number): void { }
}
```

### Move Method

**When**: Method uses features of another class more than its own
**Goal**: Move to appropriate class

**Before**:
```python
class Account:
    def overdraft_charge(self):
        if self.type.is_premium():
            return 10
        else:
            return 20

class AccountType:
    def is_premium(self):
        return self.name == "Premium"
```

**After**:
```python
class Account:
    def overdraft_charge(self):
        return self.type.overdraft_charge()

class AccountType:
    def is_premium(self):
        return self.name == "Premium"

    def overdraft_charge(self):
        if self.is_premium():
            return 10
        else:
            return 20
```

### Move Field

**When**: Field used more by another class
**Goal**: Move to appropriate class

**Before**:
```java
class Account {
    private AccountType type;
    private double interestRate;

    double calculateInterest() {
        return balance * interestRate;
    }
}
```

**After**:
```java
class Account {
    private AccountType type;

    double calculateInterest() {
        return balance * type.getInterestRate();
    }
}

class AccountType {
    private double interestRate;

    double getInterestRate() {
        return interestRate;
    }
}
```

### Hide Delegate

**When**: Client calls method on object returned by another method
**Goal**: Hide delegation chain

**Before**:
```python
# Client code
manager = employee.get_department().get_manager()
```

**After**:
```python
class Employee:
    def get_manager(self):
        return self.department.get_manager()

# Client code
manager = employee.get_manager()
```

### Remove Middle Man

**When**: Class doing too much simple delegation
**Goal**: Client calls delegate directly

**Before**:
```javascript
class Person {
    getDepartment() {
        return this.department;
    }

    getManager() {
        return this.department.getManager();
    }

    // Many more delegation methods
}
```

**After**:
```javascript
class Person {
    getDepartment() {
        return this.department;
    }
}

// Client gets department and calls it directly
person.getDepartment().getManager();
```

## Data Refactorings

### Encapsulate Field

**When**: Public field exposed
**Goal**: Hide field behind getter/setter

**Before**:
```python
class Person:
    def __init__(self):
        self.name = ""  # Public field
```

**After**:
```python
class Person:
    def __init__(self):
        self._name = ""  # Private field

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
```

### Replace Magic Number with Named Constant

**When**: Literal number with special meaning
**Goal**: Use named constant

**Before**:
```java
double potentialEnergy(double mass, double height) {
    return mass * 9.81 * height;
}
```

**After**:
```java
static final double GRAVITATIONAL_CONSTANT = 9.81;

double potentialEnergy(double mass, double height) {
    return mass * GRAVITATIONAL_CONSTANT * height;
}
```

### Replace Type Code with Class

**When**: Type code doesn't affect behavior
**Goal**: Use type-safe class

**Before**:
```python
class Person:
    O = 0  # Blood type O
    A = 1  # Blood type A
    B = 2  # Blood type B
    AB = 3  # Blood type AB

    def __init__(self, blood_type):
        self.blood_type = blood_type
```

**After**:
```python
class BloodType:
    def __init__(self, code):
        self._code = code

    @staticmethod
    def type_o():
        return BloodType(0)

    @staticmethod
    def type_a():
        return BloodType(1)

class Person:
    def __init__(self, blood_type):
        self.blood_type = blood_type  # BloodType instance
```

### Replace Array with Object

**When**: Array elements represent different things
**Goal**: Use object with named fields

**Before**:
```javascript
const row = [];
row[0] = "Liverpool";
row[1] = 15;

const name = row[0];
const wins = row[1];
```

**After**:
```javascript
class TeamStats {
    constructor(name, wins) {
        this.name = name;
        this.wins = wins;
    }
}

const stats = new TeamStats("Liverpool", 15);
const name = stats.name;
const wins = stats.wins;
```

### Introduce Parameter Object

**When**: Group of parameters naturally go together
**Goal**: Replace with object

**Before**:
```python
def create_booking(customer_name, start_date, end_date, room_type, num_guests):
    # ...
```

**After**:
```python
class BookingRequest:
    def __init__(self, customer_name, start_date, end_date, room_type, num_guests):
        self.customer_name = customer_name
        self.start_date = start_date
        self.end_date = end_date
        self.room_type = room_type
        self.num_guests = num_guests

def create_booking(booking_request):
    # ...
```

### Replace Data Value with Object

**When**: Data item needs additional behavior
**Goal**: Turn into object

**Before**:
```java
class Order {
    private String customer;

    public String getCustomer() {
        return customer;
    }
}
```

**After**:
```java
class Order {
    private Customer customer;

    public Customer getCustomer() {
        return customer;
    }
}

class Customer {
    private final String name;

    public Customer(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
```

## Conditional Refactorings

### Decompose Conditional

**When**: Complex conditional logic
**Goal**: Extract conditions and branches

**Before**:
```python
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate
```

**After**:
```python
if is_not_summer(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)

def is_not_summer(date):
    return date.before(SUMMER_START) or date.after(SUMMER_END)

def winter_charge(quantity):
    return quantity * winter_rate + winter_service_charge

def summer_charge(quantity):
    return quantity * summer_rate
```

### Consolidate Conditional Expression

**When**: Multiple conditionals with same result
**Goal**: Combine into single expression

**Before**:
```javascript
function disabilityAmount() {
    if (seniority < 2) return 0;
    if (monthsDisabled > 12) return 0;
    if (isPartTime) return 0;
    // Calculate amount
}
```

**After**:
```javascript
function disabilityAmount() {
    if (isNotEligibleForDisability()) return 0;
    // Calculate amount
}

function isNotEligibleForDisability() {
    return seniority < 2
        || monthsDisabled > 12
        || isPartTime;
}
```

### Replace Nested Conditional with Guard Clauses

**When**: Nested conditionals obscure normal flow
**Goal**: Use early returns

**Before**:
```python
def get_payment():
    if is_dead:
        result = dead_amount()
    else:
        if is_separated:
            result = separated_amount()
        else:
            if is_retired:
                result = retired_amount()
            else:
                result = normal_amount()
    return result
```

**After**:
```python
def get_payment():
    if is_dead:
        return dead_amount()
    if is_separated:
        return separated_amount()
    if is_retired:
        return retired_amount()
    return normal_amount()
```

### Replace Conditional with Polymorphism

**When**: Type code determines behavior
**Goal**: Use inheritance/interfaces

**Before**:
```java
class Bird {
    private String type;

    public double getSpeed() {
        switch (type) {
            case "EUROPEAN":
                return getBaseSpeed();
            case "AFRICAN":
                return getBaseSpeed() - getLoadFactor();
            case "NORWEGIAN":
                return (isNailed) ? 0 : getBaseSpeed();
        }
    }
}
```

**After**:
```java
abstract class Bird {
    abstract double getSpeed();
}

class European extends Bird {
    double getSpeed() {
        return getBaseSpeed();
    }
}

class African extends Bird {
    double getSpeed() {
        return getBaseSpeed() - getLoadFactor();
    }
}

class Norwegian extends Bird {
    double getSpeed() {
        return (isNailed) ? 0 : getBaseSpeed();
    }
}
```

### Introduce Null Object

**When**: Repeated null checks
**Goal**: Use Null Object pattern

**Before**:
```python
if customer is None:
    plan = billing_plan.basic()
else:
    plan = customer.get_plan()
```

**After**:
```python
class NullCustomer:
    def get_plan(self):
        return billing_plan.basic()

    def is_null(self):
        return True

class RealCustomer:
    def get_plan(self):
        return self.plan

    def is_null(self):
        return False

# Usage - no null check needed
plan = customer.get_plan()
```

### Replace Control Flag with Break

**When**: Variable used as control flag in loop
**Goal**: Use break/continue/return

**Before**:
```javascript
let found = false;
for (let person of people) {
    if (!found) {
        if (person.name === "Don") {
            sendAlert();
            found = true;
        }
    }
}
```

**After**:
```javascript
for (let person of people) {
    if (person.name === "Don") {
        sendAlert();
        break;
    }
}
```

## API Refactorings

### Separate Query from Modifier

**When**: Method returns value and changes state
**Goal**: Split into two methods

**Before**:
```python
def get_total_and_send():
    total = calculate_total()
    send_notification()
    return total
```

**After**:
```python
def get_total():
    return calculate_total()

def send_notification():
    # Send notification
    pass
```

### Parameterize Method

**When**: Similar methods differ only by values
**Goal**: Use single method with parameter

**Before**:
```java
void raiseSalaryByFivePercent() {
    salary *= 1.05;
}

void raiseSalaryByTenPercent() {
    salary *= 1.10;
}
```

**After**:
```java
void raiseSalary(double factor) {
    salary *= (1 + factor);
}
```

### Replace Parameter with Method Call

**When**: Parameter can be obtained by calling method
**Goal**: Remove parameter

**Before**:
```python
base_price = quantity * item_price
discount = get_discount_level()
final_price = discounted_price(base_price, discount)

def discounted_price(base_price, discount):
    if discount == 2:
        return base_price * 0.9
    else:
        return base_price * 0.95
```

**After**:
```python
base_price = quantity * item_price
final_price = discounted_price(base_price)

def discounted_price(base_price):
    if get_discount_level() == 2:
        return base_price * 0.9
    else:
        return base_price * 0.95
```

### Preserve Whole Object

**When**: Passing multiple values from same object
**Goal**: Pass whole object

**Before**:
```javascript
const low = daysTempRange.getLow();
const high = daysTempRange.getHigh();
const withinPlan = plan.withinRange(low, high);
```

**After**:
```javascript
const withinPlan = plan.withinRange(daysTempRange);
```

### Replace Error Code with Exception

**When**: Method returns error code
**Goal**: Throw exception

**Before**:
```python
def withdraw(amount):
    if amount > balance:
        return -1
    else:
        balance -= amount
        return 0

# Caller
if account.withdraw(100) == -1:
    handle_error()
```

**After**:
```python
def withdraw(amount):
    if amount > balance:
        raise InsufficientFundsException()
    balance -= amount

# Caller
try:
    account.withdraw(100)
except InsufficientFundsException:
    handle_error()
```

### Replace Exception with Test

**When**: Exception for expected condition
**Goal**: Use conditional test

**Before**:
```java
try {
    ResourcePool pool = ResourcePool.getInstance();
    Resource resource = pool.getResource();
    // Use resource
} catch (ResourceUnavailableException e) {
    // Handle unavailable
}
```

**After**:
```java
ResourcePool pool = ResourcePool.getInstance();
if (pool.hasAvailableResource()) {
    Resource resource = pool.getResource();
    // Use resource
} else {
    // Handle unavailable
}
```

## Hierarchical Refactorings

### Pull Up Method

**When**: Methods in subclasses do same thing
**Goal**: Move to superclass

**Before**:
```python
class Customer:
    pass

class RegularCustomer(Customer):
    def create_bill(self):
        return Bill(self)

class PreferredCustomer(Customer):
    def create_bill(self):
        return Bill(self)
```

**After**:
```python
class Customer:
    def create_bill(self):
        return Bill(self)

class RegularCustomer(Customer):
    pass

class PreferredCustomer(Customer):
    pass
```

### Push Down Method

**When**: Method only relevant to some subclasses
**Goal**: Move to those subclasses

**Before**:
```java
class Employee {
    int getQuota() {
        // Only engineers have quotas
    }
}

class Engineer extends Employee { }
class Salesman extends Employee { }
```

**After**:
```java
class Employee { }

class Engineer extends Employee {
    int getQuota() { }
}

class Salesman extends Employee { }
```

### Extract Subclass

**When**: Class features used only in some instances
**Goal**: Create subclass for variant

**Before**:
```python
class JobItem:
    def __init__(self, unit_price, quantity, is_labor):
        self.unit_price = unit_price
        self.quantity = quantity
        self.is_labor = is_labor

    def get_total_price(self):
        return self.unit_price * self.quantity

    def get_employee(self):
        return self.employee if self.is_labor else None
```

**After**:
```python
class JobItem:
    def __init__(self, unit_price, quantity):
        self.unit_price = unit_price
        self.quantity = quantity

    def get_total_price(self):
        return self.unit_price * self.quantity

class LaborItem(JobItem):
    def __init__(self, unit_price, quantity, employee):
        super().__init__(unit_price, quantity)
        self.employee = employee

    def get_employee(self):
        return self.employee
```

### Extract Superclass

**When**: Two classes have similar features
**Goal**: Create superclass

**Before**:
```javascript
class Employee {
    constructor(name, id) {
        this.name = name;
        this.id = id;
    }
}

class Department {
    constructor(name, id) {
        this.name = name;
        this.id = id;
    }
}
```

**After**:
```javascript
class Party {
    constructor(name, id) {
        this.name = name;
        this.id = id;
    }
}

class Employee extends Party { }
class Department extends Party { }
```

### Replace Inheritance with Delegation

**When**: Subclass uses only part of superclass
**Goal**: Use composition instead

**Before**:
```python
class Stack(list):
    def push(self, item):
        self.append(item)

    def pop(self):
        return super().pop()
```

**After**:
```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()
```

### Replace Delegation with Inheritance

**When**: Simple delegation to all methods
**Goal**: Make delegate a subclass

**Before**:
```java
class Employee {
    private Person person;

    public String getName() {
        return person.getName();
    }

    public void setName(String name) {
        person.setName(name);
    }
}
```

**After**:
```java
class Employee extends Person {
    // Inherited getName() and setName()
}
```

## Pattern Application

### Strategy Pattern

**Use when**: Multiple algorithms for same operation

```python
# Before - conditional logic
def calculate_price(order, pricing_type):
    if pricing_type == "REGULAR":
        return order.total
    elif pricing_type == "SALE":
        return order.total * 0.9
    elif pricing_type == "VIP":
        return order.total * 0.8

# After - Strategy pattern
class PricingStrategy:
    def calculate(self, order):
        raise NotImplementedError

class RegularPricing(PricingStrategy):
    def calculate(self, order):
        return order.total

class SalePricing(PricingStrategy):
    def calculate(self, order):
        return order.total * 0.9

class VipPricing(PricingStrategy):
    def calculate(self, order):
        return order.total * 0.8

class Order:
    def __init__(self, pricing_strategy):
        self.pricing_strategy = pricing_strategy

    def calculate_price(self):
        return self.pricing_strategy.calculate(self)
```

### Factory Pattern

**Use when**: Complex object creation logic

```java
// Before - complex construction
if (type.equals("SAVINGS")) {
    return new SavingsAccount(accountNumber, balance, interestRate);
} else if (type.equals("CHECKING")) {
    return new CheckingAccount(accountNumber, balance, overdraftLimit);
}

// After - Factory pattern
class AccountFactory {
    public static Account createAccount(String type, String accountNumber, double balance) {
        if (type.equals("SAVINGS")) {
            return new SavingsAccount(accountNumber, balance);
        } else if (type.equals("CHECKING")) {
            return new CheckingAccount(accountNumber, balance);
        }
        throw new IllegalArgumentException("Unknown account type");
    }
}
```

### Observer Pattern

**Use when**: Multiple objects need to be notified of changes

```typescript
// Before - tight coupling
class Order {
    completeOrder() {
        this.status = 'COMPLETED';
        emailService.sendConfirmation(this);
        inventoryService.updateStock(this);
        analyticsService.trackOrder(this);
    }
}

// After - Observer pattern
interface OrderObserver {
    update(order: Order): void;
}

class Order {
    private observers: OrderObserver[] = [];

    addObserver(observer: OrderObserver) {
        this.observers.push(observer);
    }

    completeOrder() {
        this.status = 'COMPLETED';
        this.notifyObservers();
    }

    private notifyObservers() {
        for (const observer of this.observers) {
            observer.update(this);
        }
    }
}
```

## Anti-Pattern Elimination

### God Object

**Problem**: One class does everything
**Solution**: Extract multiple focused classes

**Before**: UserManager with 2000 lines handling validation, persistence, email, logging

**After**: UserValidator, UserRepository, EmailService, ActivityLogger

### Spaghetti Code

**Problem**: Complex, tangled control flow
**Solution**: Extract methods, simplify conditionals

**Before**: 500-line method with 10-level nesting

**After**: 20 focused methods with clear flow

### Copy-Paste Programming

**Problem**: Duplicated code everywhere
**Solution**: Extract method/class, introduce abstraction

**Before**: Same logic in 5 places

**After**: One reusable function called from 5 places

### Magic Numbers

**Problem**: Unexplained literal values
**Solution**: Replace with named constants

**Before**: `if (status == 3)`

**After**: `if (status == STATUS_COMPLETED)`

### Shotgun Surgery

**Problem**: One change requires editing many places
**Solution**: Move method, inline class

**Before**: Email format change requires updating 20 files

**After**: Email formatting in one EmailFormatter class

## Summary

### Refactoring Selection Guide

| Smell | Refactoring |
|-------|-------------|
| Long Method | Extract Method |
| Large Class | Extract Class |
| Duplicate Code | Extract Method/Class |
| Long Parameter List | Introduce Parameter Object |
| Divergent Change | Extract Class |
| Shotgun Surgery | Move Method, Inline Class |
| Feature Envy | Move Method |
| Data Clumps | Extract Class |
| Primitive Obsession | Replace with Object |
| Switch Statements | Replace with Polymorphism |

### Next Steps

- Practice with [Examples](../examples/)
- Use [Templates](../templates/) for common refactorings
- Reference [Checklists](../resources/checklists.md) during work
- Study [Advanced Topics](advanced-topics.md) for complex scenarios
