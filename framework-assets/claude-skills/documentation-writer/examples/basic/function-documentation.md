# Example 1: Documenting a Simple Function

## Problem Statement

You have a Python function that needs documentation. The function is working, but other developers don't know how to use it, what parameters it accepts, or what it returns. You need to add clear, comprehensive documentation.

## Use Case

This pattern applies whenever you write a function that will be used by others (or by future you). Good function documentation prevents confusion, reduces support questions, and makes code maintainable.

## Solution Overview

We'll document a function using Python docstrings following the Google style guide. This includes describing the function's purpose, parameters, return values, exceptions, and providing examples.

## Complete Code

```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """
    Calculate the total cost of items including tax and discount.

    This function computes the subtotal of all items, applies any discount,
    and then adds tax. The calculation order is: subtotal → discount → tax.

    Args:
        items (list): List of item prices (float or int). Cannot be empty.
        tax_rate (float, optional): Tax rate as decimal (e.g., 0.08 for 8%).
            Must be between 0.0 and 1.0. Defaults to 0.0.
        discount_percent (float, optional): Discount percentage as decimal
            (e.g., 0.15 for 15% off). Must be between 0.0 and 1.0. Defaults to 0.0.

    Returns:
        float: Total cost rounded to 2 decimal places.

    Raises:
        ValueError: If items list is empty.
        ValueError: If any item price is negative.
        ValueError: If tax_rate is not between 0.0 and 1.0.
        ValueError: If discount_percent is not between 0.0 and 1.0.

    Examples:
        Basic usage with no tax or discount:

        >>> calculate_total([10.00, 20.00, 15.00])
        45.00

        With 8% tax:

        >>> calculate_total([10.00, 20.00], tax_rate=0.08)
        32.40

        With 15% discount and 8% tax:

        >>> calculate_total([100.00], tax_rate=0.08, discount_percent=0.15)
        91.80

        Edge case with single item:

        >>> calculate_total([5.99], tax_rate=0.05)
        6.29

    Note:
        Discount is applied before tax, which is standard practice in most
        retail scenarios. If you need tax calculated before discount,
        use calculate_total_tax_first() instead.

    See Also:
        - calculate_total_tax_first(): Alternative calculation order
        - format_currency(): Format result as currency string
    """
    # Validation
    if not items:
        raise ValueError("Items list cannot be empty")

    if any(item < 0 for item in items):
        raise ValueError("Item prices cannot be negative")

    if not 0.0 <= tax_rate <= 1.0:
        raise ValueError("Tax rate must be between 0.0 and 1.0")

    if not 0.0 <= discount_percent <= 1.0:
        raise ValueError("Discount percent must be between 0.0 and 1.0")

    # Calculate subtotal
    subtotal = sum(items)

    # Apply discount
    discount_amount = subtotal * discount_percent
    subtotal_after_discount = subtotal - discount_amount

    # Apply tax
    tax_amount = subtotal_after_discount * tax_rate
    total = subtotal_after_discount + tax_amount

    # Round to 2 decimal places
    return round(total, 2)
```

## Code Explanation

### Line-by-Line Breakdown

**Lines 1-2: Function Signature**
```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """
```
- Function name is descriptive and uses verb + noun pattern
- Parameters have sensible defaults (0.0 for optional tax/discount)
- Docstring starts immediately after function signature

**Lines 3-5: Summary**
```python
    """
    Calculate the total cost of items including tax and discount.

    This function computes the subtotal of all items, applies any discount,
    and then adds tax. The calculation order is: subtotal → discount → tax.
```
- First line: One-sentence summary (imperative mood)
- Blank line separates summary from details
- Next paragraph: More detailed explanation including important behavior (calculation order)

**Lines 7-13: Args Section**
```python
    Args:
        items (list): List of item prices (float or int). Cannot be empty.
        tax_rate (float, optional): Tax rate as decimal (e.g., 0.08 for 8%).
            Must be between 0.0 and 1.0. Defaults to 0.0.
        discount_percent (float, optional): Discount percentage as decimal
            (e.g., 0.15 for 15% off). Must be between 0.0 and 1.0. Defaults to 0.0.
```
- Each parameter documented with:
  - Name and type
  - Description with constraints
  - Examples of valid values
  - Default values for optional parameters

**Lines 15-16: Returns Section**
```python
    Returns:
        float: Total cost rounded to 2 decimal places.
```
- Type of return value
- Description of what's returned
- Important details (rounding)

**Lines 18-22: Raises Section**
```python
    Raises:
        ValueError: If items list is empty.
        ValueError: If any item price is negative.
        ValueError: If tax_rate is not between 0.0 and 1.0.
        ValueError: If discount_percent is not between 0.0 and 1.0.
```
- All possible exceptions documented
- Conditions that trigger each exception

**Lines 24-41: Examples Section**
```python
    Examples:
        Basic usage with no tax or discount:

        >>> calculate_total([10.00, 20.00, 15.00])
        45.00

        With 8% tax:

        >>> calculate_total([10.00, 20.00], tax_rate=0.08)
        32.40
```
- Multiple examples showing different use cases
- Uses doctest format (>>>)
- Includes expected output
- Covers basic to advanced usage
- Each example has descriptive text

**Lines 43-47: Note Section**
```python
    Note:
        Discount is applied before tax, which is standard practice in most
        retail scenarios. If you need tax calculated before discount,
        use calculate_total_tax_first() instead.
```
- Important behavior notes
- Business logic explanation
- Alternatives for different needs

**Lines 49-51: See Also Section**
```python
    See Also:
        - calculate_total_tax_first(): Alternative calculation order
        - format_currency(): Format result as currency string
```
- Links to related functions
- Brief description of why they're related

### Key Documentation Elements

1. **Clear Summary**: One-line description tells you exactly what the function does
2. **Complete Parameter Documentation**: Every parameter explained with types, constraints, and examples
3. **Return Value Documentation**: What you get back and in what format
4. **Exception Documentation**: All error cases documented
5. **Multiple Examples**: Different use cases with expected output
6. **Important Notes**: Business logic and behavioral details
7. **Cross-References**: Links to related functions

## Variations

### Variation 1: Minimal Documentation (Not Recommended)

```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """Calculate total cost with tax and discount."""
    subtotal = sum(items)
    subtotal_after_discount = subtotal * (1 - discount_percent)
    total = subtotal_after_discount * (1 + tax_rate)
    return round(total, 2)
```

**Why this is insufficient:**
- No parameter documentation
- No information about calculation order
- No examples
- No exception documentation
- Users must read code to understand behavior

### Variation 2: Numpy Style Docstring

```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """
    Calculate the total cost of items including tax and discount.

    Parameters
    ----------
    items : list of float
        List of item prices. Cannot be empty.
    tax_rate : float, optional
        Tax rate as decimal (default is 0.0)
    discount_percent : float, optional
        Discount percentage as decimal (default is 0.0)

    Returns
    -------
    float
        Total cost rounded to 2 decimal places

    Raises
    ------
    ValueError
        If items list is empty or contains negative values

    Examples
    --------
    >>> calculate_total([10.00, 20.00, 15.00])
    45.00
    """
    # Implementation
```

**When to use Numpy style:**
- Scientific Python projects
- Projects already using Numpy/Scipy
- When longer parameter descriptions are needed

### Variation 3: Sphinx/RestructuredText Style

```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """
    Calculate the total cost of items including tax and discount.

    :param items: List of item prices. Cannot be empty.
    :type items: list
    :param tax_rate: Tax rate as decimal (default: 0.0)
    :type tax_rate: float
    :param discount_percent: Discount percentage as decimal (default: 0.0)
    :type discount_percent: float
    :return: Total cost rounded to 2 decimal places
    :rtype: float
    :raises ValueError: If items list is empty

    **Example:**

    .. code-block:: python

        >>> calculate_total([10.00, 20.00, 15.00])
        45.00
    """
    # Implementation
```

**When to use Sphinx style:**
- Projects using Sphinx documentation generator
- Need for cross-references between docs
- Building comprehensive API documentation

## Common Pitfalls

### Pitfall 1: Vague Parameter Descriptions

**Bad:**
```python
def calculate_total(items, tax_rate, discount_percent):
    """
    Args:
        items: The items
        tax_rate: The tax
        discount_percent: The discount
    """
```

**Why it's wrong:** Doesn't specify types, constraints, or formats
**How to fix:** Be specific about types, formats, and valid ranges

### Pitfall 2: Missing Examples

**Bad:**
```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """
    Calculate the total cost of items including tax and discount.

    Args:
        items (list): List of item prices
        tax_rate (float): Tax rate as decimal
        discount_percent (float): Discount percentage as decimal

    Returns:
        float: Total cost
    """
```

**Why it's wrong:** Users have to guess how to use it
**How to fix:** Always include at least one basic example

### Pitfall 3: Not Documenting Exceptions

**Bad:**
```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """Calculate total with tax and discount."""
    if not items:
        raise ValueError("Items cannot be empty")  # Not documented!
    # More code
```

**Why it's wrong:** Surprises users with unexpected exceptions
**How to fix:** Document all exceptions in Raises section

### Pitfall 4: Outdated Documentation

**Bad:**
```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0, shipping=0.0):
    """
    Calculate total cost with tax and discount.

    Args:
        items (list): List of item prices
        tax_rate (float): Tax rate
        discount_percent (float): Discount percentage
        # Oops! Forgot to document the new 'shipping' parameter
    """
```

**Why it's wrong:** Documentation doesn't match actual signature
**How to fix:** Update docs whenever you change function signature

### Pitfall 5: Assuming Knowledge

**Bad:**
```python
def calculate_total(items, tax_rate=0.0, discount_percent=0.0):
    """
    Calculate total using standard retail calculation.

    Args:
        items (list): Item prices
        tax_rate (float): Tax (obvously as decimal)
        discount_percent (float): Discount (duh, as decimal)
    """
```

**Why it's wrong:** "Obviously" and "duh" indicate assumptions
**How to fix:** Be explicit about formats and conventions

## Testing

Test your documentation by:

1. **Run doctests:**
```bash
python -m doctest your_module.py -v
```

2. **Generate API docs:**
```bash
# Using Sphinx
sphinx-apidoc -o docs/ src/
sphinx-build docs/ docs/_build

# Using pdoc
pdoc --html your_module.py
```

3. **Ask someone else to use it:**
- Give the function to a colleague
- Only provide the docstring
- Watch them try to use it
- Note where they get confused

## Benefits of Good Function Documentation

1. **Reduced Support Load**: Users find answers in docs, not in tickets
2. **Faster Onboarding**: New developers understand code quickly
3. **Fewer Bugs**: Clear contracts prevent misuse
4. **Better APIs**: Writing docs forces you to think about API design
5. **Maintainability**: Future you understands past you's intent

## Next Steps

- **Apply this pattern** to your own functions
- **Try different docstring styles** (Google, Numpy, Sphinx) to find what works for your project
- **Set up automated doc generation** with Sphinx or pdoc
- **Add docstring requirements** to your code review checklist

## Related Examples

- [README File Documentation](readme-file.md): Documenting entire projects
- [API Endpoint Documentation](../intermediate/api-endpoint-docs.md): Documenting REST APIs
- [Class Documentation](../intermediate/class-documentation.md): Documenting classes
