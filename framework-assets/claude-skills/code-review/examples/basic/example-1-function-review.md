# Example 1: Basic Function Code Review

## Problem Statement

Review a simple function for calculating discounts to ensure correctness, handle edge cases, and follow best practices.

## Code to Review

```python
def calculate_discount(price, customer_type):
    if customer_type == "premium":
        discount = price * 0.2
    elif customer_type == "regular":
        discount = price * 0.1
    return price - discount
```

## Review Output

### Overall Assessment
**Quality Score**: 4/10
**Recommendation**: REQUIRES CHANGES before merge
**Issues Found**: 2 CRITICAL, 2 HIGH, 1 MEDIUM

### Critical Issues

**CRITICAL #1: Missing Error Handling**
- **Line**: 1-6
- **Issue**: Function crashes when customer_type doesn't match known types
- **Impact**: UnboundLocalError when discount not set

**Test Case That Fails**:
```python
calculate_discount(100, "guest")  # UnboundLocalError: discount
```

**Fix**:
```python
def calculate_discount(price: float, customer_type: str) -> float:
    """Calculate discount based on customer type.
    
    Args:
        price: Original price
        customer_type: Type of customer ('premium', 'regular', 'guest')
    
    Returns:
        Price after discount
        
    Raises:
        ValueError: If customer_type is invalid
    """
    DISCOUNT_RATES = {
        "premium": 0.20,
        "regular": 0.10,
        "guest": 0.00
    }
    
    if customer_type not in DISCOUNT_RATES:
        raise ValueError(f"Invalid customer type: {customer_type}")
    
    discount = price * DISCOUNT_RATES[customer_type]
    return price - discount
```

**CRITICAL #2: No Input Validation**
- **Line**: 1
- **Issue**: Accepts negative prices, non-numeric types
- **Impact**: Incorrect calculations, runtime errors

**Test Cases That Should Fail**:
```python
calculate_discount(-100, "premium")    # Negative discount
calculate_discount("invalid", "premium")  # TypeError
calculate_discount(None, "premium")    # TypeError
```

**Fix**:
```python
from decimal import Decimal
from typing import Union

def calculate_discount(
    price: Union[int, float, Decimal], 
    customer_type: str
) -> Decimal:
    """Calculate discount with input validation."""
    
    # Validate price
    try:
        price_decimal = Decimal(str(price))
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price: {price}")
    
    if price_decimal < 0:
        raise ValueError(f"Price cannot be negative: {price}")
    
    # Validate customer type
    DISCOUNT_RATES = {
        "premium": Decimal("0.20"),
        "regular": Decimal("0.10"),
        "guest": Decimal("0.00")
    }
    
    if customer_type not in DISCOUNT_RATES:
        raise ValueError(
            f"Invalid customer type: {customer_type}. "
            f"Valid types: {list(DISCOUNT_RATES.keys())}"
        )
    
    discount = price_decimal * DISCOUNT_RATES[customer_type]
    return price_decimal - discount
```

### High Issues

**HIGH #1: Magic Numbers**
- **Lines**: 3, 5
- **Issue**: Discount rates hard-coded, unclear meaning
- **Fix**: Use named constants or configuration

```python
# Define at module level or in config
PREMIUM_DISCOUNT_RATE = 0.20  # 20% discount for premium customers
REGULAR_DISCOUNT_RATE = 0.10  # 10% discount for regular customers

def calculate_discount(price, customer_type):
    if customer_type == "premium":
        discount = price * PREMIUM_DISCOUNT_RATE
    elif customer_type == "regular":
        discount = price * REGULAR_DISCOUNT_RATE
    else:
        discount = 0
    return price - discount
```

**HIGH #2: No Type Hints**
- **Lines**: 1
- **Issue**: No type annotations for parameters and return value
- **Impact**: Reduced IDE support, potential type errors

**Fix**: Add type hints (shown in previous fixes)

### Medium Issues

**MEDIUM #1: Float Precision**
- **Issue**: Using float for money calculations
- **Impact**: Potential precision errors in financial calculations

**Example Problem**:
```python
>>> 0.1 + 0.2
0.30000000000000004  # Floating point precision error
```

**Fix**: Use Decimal for money
```python
from decimal import Decimal

def calculate_discount(price: Decimal, customer_type: str) -> Decimal:
    # Use Decimal for all calculations
    DISCOUNT_RATES = {
        "premium": Decimal("0.20"),
        "regular": Decimal("0.10")
    }
    # ... rest of implementation
```

## Complete Fixed Version

```python
from decimal import Decimal
from typing import Union

# Configuration (could be in separate config file)
DISCOUNT_RATES = {
    "premium": Decimal("0.20"),  # 20% off for premium customers
    "regular": Decimal("0.10"),  # 10% off for regular customers
    "guest": Decimal("0.00")     # No discount for guests
}

def calculate_discount(
    price: Union[int, float, Decimal],
    customer_type: str
) -> Decimal:
    """Calculate discounted price based on customer type.
    
    Args:
        price: Original price (must be non-negative)
        customer_type: Customer category (premium/regular/guest)
    
    Returns:
        Final price after applying discount
    
    Raises:
        ValueError: If price is invalid or customer_type unknown
    
    Example:
        >>> calculate_discount(100, "premium")
        Decimal('80.00')
        >>> calculate_discount(50, "regular")
        Decimal('45.00')
    """
    # Input validation
    try:
        price_decimal = Decimal(str(price))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid price '{price}': must be a number") from e
    
    if price_decimal < 0:
        raise ValueError(f"Price cannot be negative: {price_decimal}")
    
    if customer_type not in DISCOUNT_RATES:
        raise ValueError(
            f"Unknown customer type '{customer_type}'. "
            f"Valid types: {', '.join(DISCOUNT_RATES.keys())}"
        )
    
    # Calculate discount
    discount_rate = DISCOUNT_RATES[customer_type]
    discount_amount = price_decimal * discount_rate
    final_price = price_decimal - discount_amount
    
    return final_price
```

## Comprehensive Tests

```python
import pytest
from decimal import Decimal

class TestCalculateDiscount:
    """Comprehensive test suite for discount calculation."""
    
    def test_premium_customer_discount(self):
        """Premium customers get 20% off."""
        result = calculate_discount(100, "premium")
        assert result == Decimal("80.00")
    
    def test_regular_customer_discount(self):
        """Regular customers get 10% off."""
        result = calculate_discount(50, "regular")
        assert result == Decimal("45.00")
    
    def test_guest_no_discount(self):
        """Guest customers get no discount."""
        result = calculate_discount(100, "guest")
        assert result == Decimal("100.00")
    
    def test_zero_price(self):
        """Handle zero price correctly."""
        result = calculate_discount(0, "premium")
        assert result == Decimal("0.00")
    
    def test_invalid_customer_type(self):
        """Reject invalid customer types."""
        with pytest.raises(ValueError, match="Unknown customer type"):
            calculate_discount(100, "invalid")
    
    def test_negative_price(self):
        """Reject negative prices."""
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_discount(-50, "regular")
    
    def test_invalid_price_type(self):
        """Reject non-numeric prices."""
        with pytest.raises(ValueError, match="must be a number"):
            calculate_discount("invalid", "regular")
    
    def test_precision_with_decimal(self):
        """Ensure precise calculations with Decimal."""
        result = calculate_discount(Decimal("33.33"), "premium")
        assert result == Decimal("26.664")  # Precise calculation
```

## Key Learnings

**What Went Wrong**:
1. No input validation (critical for user-facing functions)
2. Poor error handling (crashes instead of helpful errors)
3. Magic numbers (maintenance nightmare)
4. Float precision issues (dangerous for money)
5. No type hints (reduced safety and IDE support)
6. No documentation (future developers confused)

**How to Prevent**:
1. Always validate inputs at boundaries
2. Use explicit error handling with descriptive messages
3. Extract constants with meaningful names
4. Use Decimal for financial calculations
5. Add type hints to all functions
6. Document expected behavior and edge cases
7. Write comprehensive tests including edge cases

**Best Practices Applied**:
- ✅ Input validation
- ✅ Type hints
- ✅ Documentation (docstring)
- ✅ Named constants
- ✅ Decimal for money
- ✅ Descriptive error messages
- ✅ Comprehensive tests
