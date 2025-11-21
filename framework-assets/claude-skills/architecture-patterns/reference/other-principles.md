# Other Core Principles Reference

**DRY, KISS, and related software design principles.**

## Overview

core_principles[3]{principle,acronym,core_rule,benefit}:
Don't Repeat Yourself,DRY,Every piece of knowledge should have single representation,Easier maintenance reduced bugs
Keep It Simple Stupid,KISS,Simplicity should be key goal in design,Better readability easier debugging
You Aren't Gonna Need It,YAGNI,Don't add functionality until needed,Faster development less complexity

---

## DRY (Don't Repeat Yourself)

**Rule:** Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

**Key Concept:** Duplication of logic or data leads to maintenance nightmares. Changes must be made in multiple places, increasing risk of bugs.

### Backend Example (Python)

#### Good Example - Single Source of Truth

```python
# Single source of truth for validation rules
class UserValidator:
    """Centralized validation logic"""

    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PASSWORD_MIN_LENGTH = 8
    NAME_MIN_LENGTH = 2

    @classmethod
    def validate_email(cls, email: str) -> tuple[bool, str]:
        if not email:
            return False, "Email is required"
        if not re.match(cls.EMAIL_PATTERN, email):
            return False, "Invalid email format"
        return True, ""

    @classmethod
    def validate_password(cls, password: str) -> tuple[bool, str]:
        if not password:
            return False, "Password is required"
        if len(password) < cls.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {cls.PASSWORD_MIN_LENGTH} characters"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        return True, ""

    @classmethod
    def validate_name(cls, name: str) -> tuple[bool, str]:
        if not name:
            return False, "Name is required"
        if len(name) < cls.NAME_MIN_LENGTH:
            return False, f"Name must be at least {cls.NAME_MIN_LENGTH} characters"
        if not name.replace(" ", "").isalpha():
            return False, "Name must contain only letters"
        return True, ""


# Reuse validation everywhere
class UserService:
    def create_user(self, email: str, name: str, password: str) -> User:
        # Reuse validation
        valid, error = UserValidator.validate_email(email)
        if not valid:
            raise ValueError(error)

        valid, error = UserValidator.validate_name(name)
        if not valid:
            raise ValueError(error)

        valid, error = UserValidator.validate_password(password)
        if not valid:
            raise ValueError(error)

        return self.repository.create(email, name, password)


class UserUpdateService:
    def update_email(self, user_id: int, new_email: str) -> User:
        # Same validation logic, no duplication
        valid, error = UserValidator.validate_email(new_email)
        if not valid:
            raise ValueError(error)

        user = self.repository.get(user_id)
        user.email = new_email
        return self.repository.save(user)

    def update_password(self, user_id: int, new_password: str) -> User:
        # Same validation logic, no duplication
        valid, error = UserValidator.validate_password(new_password)
        if not valid:
            raise ValueError(error)

        user = self.repository.get(user_id)
        user.password = hash_password(new_password)
        return self.repository.save(user)


# Can also use in API validation layer
from fastapi import HTTPException

class UserController:
    @app.post("/users")
    def create_user(self, data: dict):
        # Reuse same validation
        valid, error = UserValidator.validate_email(data['email'])
        if not valid:
            raise HTTPException(400, error)

        # Continue with creation...
```

**Benefits:**
- Validation rules defined once
- Changes to rules update everywhere automatically
- Consistent error messages
- Easy to test validation logic

#### Bad Example - Duplicated Logic

```python
# DON'T DO THIS - Duplicated validation logic
class UserService:
    def create_user(self, email: str, name: str, password: str):
        # Validation duplicated
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email")

        if len(password) < 8 or not any(c.isdigit() for c in password):
            raise ValueError("Invalid password")

        if len(name) < 2:
            raise ValueError("Invalid name")

        # Create user...


class UserUpdateService:
    def update_email(self, user_id: int, new_email: str):
        # Same validation duplicated again
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
            raise ValueError("Invalid email")

        # Update email...

    def update_password(self, user_id: int, new_password: str):
        # Same validation duplicated yet again
        if len(new_password) < 8 or not any(c.isdigit() for c in new_password):
            raise ValueError("Invalid password")

        # Update password...


@app.post("/users")
def create_user_endpoint(data: dict):
    # Validation duplicated in API layer too!
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        raise HTTPException(400, "Invalid email")

    # Continue...
```

**Problems:**
- Logic repeated in 4+ places
- If validation rules change, must update all places
- Easy to miss one location causing inconsistencies
- Inconsistent error messages
- Hard to maintain

### DRY in Configuration

#### Good Example - Centralized Config

```python
# config.py - Single source of truth
class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'myapp')
    DB_URL = f"postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASS = os.getenv('SMTP_PASS')

    # API Keys
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')

# Use everywhere
from config import Config

db_engine = create_engine(Config.DB_URL)
smtp_client = SMTPClient(Config.SMTP_HOST, Config.SMTP_PORT)
stripe.api_key = Config.STRIPE_API_KEY
```

---

## KISS (Keep It Simple, Stupid)

**Rule:** Most systems work best if they are kept simple rather than made complicated.

**Key Concept:** Avoid over-engineering. Choose the simplest solution that solves the problem effectively.

### Backend Example (Python)

#### Good Example - Simple and Clear

```python
# Simple discount calculation
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price."""
    return price * (1 - discount_percent / 100)


# Simple shipping cost calculation
def get_shipping_cost(weight_kg: float) -> float:
    """Calculate shipping cost based on weight."""
    if weight_kg < 1:
        return 5.0
    elif weight_kg < 5:
        return 10.0
    elif weight_kg < 10:
        return 15.0
    else:
        return 20.0


# Simple user status check
def is_user_eligible_for_premium(user: User) -> bool:
    """Check if user is eligible for premium features."""
    return (
        user.is_verified and
        user.account_age_days >= 30 and
        user.total_purchases > 0
    )


# Usage
discounted_price = calculate_discount(100.0, 10)  # $90
shipping = get_shipping_cost(3.5)  # $10
if is_user_eligible_for_premium(user):
    # Grant premium access
    pass
```

**Benefits:**
- Easy to understand
- Easy to test
- Easy to modify
- No unnecessary complexity

#### Bad Example - Over-engineered

```python
# DON'T DO THIS - Over-engineered for simple task
from abc import ABC, abstractmethod
from enum import Enum

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, price: float) -> float:
        pass


class PercentageDiscountStrategy(DiscountStrategy):
    def __init__(self, percent: float):
        self.percent = percent

    def calculate(self, price: float) -> float:
        return price * (1 - self.percent / 100)


class FixedAmountDiscountStrategy(DiscountStrategy):
    def __init__(self, amount: float):
        self.amount = amount

    def calculate(self, price: float) -> float:
        return max(0, price - self.amount)


class DiscountStrategyFactory:
    @staticmethod
    def create(discount_type: str, value: float) -> DiscountStrategy:
        if discount_type == "percentage":
            return PercentageDiscountStrategy(value)
        elif discount_type == "fixed":
            return FixedAmountDiscountStrategy(value)
        else:
            raise ValueError(f"Unknown discount type: {discount_type}")


class DiscountCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def calculate_final_price(self, price: float) -> float:
        return self.strategy.calculate(price)


# Too complex for simple task
factory = DiscountStrategyFactory()
strategy = factory.create("percentage", 10)
calculator = DiscountCalculator(strategy)
final_price = calculator.calculate_final_price(100)  # Just to get $90!
```

**Problems:**
- 5 classes for simple calculation
- Difficult to understand
- Maintenance overhead
- Premature abstraction
- No real benefit over simple function

### Frontend Example (React)

#### Good Example - Simple Component

```typescript
// Simple button component
interface ButtonProps {
  text: string;
  onClick: () => void;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ text, onClick, disabled = false }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className="btn"
  >
    {text}
  </button>
);

// Usage
<Button text="Submit" onClick={handleSubmit} />
<Button text="Cancel" onClick={handleCancel} disabled={loading} />
```

#### Bad Example - Over-complicated Component

```typescript
// DON'T DO THIS - Too complex for simple button
interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger' | 'success' | 'warning';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  rounded?: boolean;
  outlined?: boolean;
  elevated?: boolean;
  elevation?: 0 | 1 | 2 | 3 | 4;
  ripple?: boolean;
  tooltip?: string;
  badge?: number;
}

const Button: React.FC<ButtonProps> = ({
  text, onClick, variant = 'primary', size = 'md',
  disabled = false, loading = false, icon, iconPosition = 'left',
  fullWidth = false, rounded = false, outlined = false,
  elevated = false, elevation = 0, ripple = true,
  tooltip, badge
}) => {
  // Complex logic for simple button
  const classes = useMemo(() => classNames(
    'button',
    `button--${variant}`,
    `button--${size}`,
    { 'button--disabled': disabled },
    { 'button--loading': loading },
    { 'button--full-width': fullWidth },
    { 'button--rounded': rounded },
    { 'button--outlined': outlined },
    { 'button--elevated': elevated },
    `button--elevation-${elevation}`
  ), [variant, size, disabled, loading, fullWidth, rounded, outlined, elevated, elevation]);

  const handleClick = useCallback((e: React.MouseEvent) => {
    if (ripple) {
      createRippleEffect(e);
    }
    onClick();
  }, [onClick, ripple]);

  return (
    <Tooltip content={tooltip}>
      <button className={classes} onClick={handleClick} disabled={disabled || loading}>
        {loading && <Spinner size={size} />}
        {icon && iconPosition === 'left' && <Icon>{icon}</Icon>}
        {text}
        {icon && iconPosition === 'right' && <Icon>{icon}</Icon>}
        {badge && <Badge count={badge} />}
      </button>
    </Tooltip>
  );
};
```

**Problems when you only need a simple button:**
- 15+ props for basic functionality
- Complex rendering logic
- Over-abstraction
- Most props rarely used
- Hard to understand and maintain

---

## YAGNI (You Aren't Gonna Need It)

**Rule:** Don't add functionality until it's actually needed.

**Key Concept:** Avoid building features "just in case" or for potential future use. Build what you need now.

### Example - Avoiding Premature Features

#### Good Example - Build What's Needed

```python
# User model - only what's needed now
@dataclass
class User:
    id: int
    email: str
    name: str
    created_at: datetime

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, email: str, name: str) -> User:
        """Create user with required fields only."""
        return self.repository.create(email, name)

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.repository.find_by_id(user_id)
```

#### Bad Example - Premature Features

```python
# DON'T DO THIS - Building features "just in case"
@dataclass
class User:
    id: int
    email: str
    name: str
    created_at: datetime
    # Features not needed yet:
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    twitter_handle: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_username: Optional[str] = None
    preferences: dict = field(default_factory=dict)
    notifications_enabled: bool = True
    email_verified: bool = False
    phone_number: Optional[str] = None
    address: Optional[dict] = None
    # ... and many more "future" fields

class UserService:
    # Methods not needed yet
    def update_avatar(self, user_id: int, avatar_url: str): pass
    def update_bio(self, user_id: int, bio: str): pass
    def update_social_links(self, user_id: int, links: dict): pass
    def toggle_notifications(self, user_id: int): pass
    def verify_phone(self, user_id: int, code: str): pass
    # ... and many more "future" methods
```

**Problems:**
- Wasted development time
- Increased complexity
- More code to maintain
- More surface area for bugs
- Harder to understand actual requirements

---

## Best Practices Summary

principle_best_practices[8]{practice,description,benefit}:
Extract common logic,Create reusable functions for repeated code,Apply DRY reduce duplication
Use configuration files,Centralize settings and constants,Single source of truth
Start simple,Choose simplest solution first,Apply KISS avoid complexity
Defer abstractions,Add abstractions when pattern emerges,Apply YAGNI avoid premature optimization
Refactor when needed,Improve code as requirements become clear,Balance simplicity with extensibility
Avoid premature optimization,Optimize after identifying bottlenecks,Focus on clarity first
Use meaningful names,Clear descriptive variable and function names,Self-documenting code
Keep functions small,Single responsibility under 20 lines,Easier to understand and test

---

**File Size**: 200/500 lines max ✅
