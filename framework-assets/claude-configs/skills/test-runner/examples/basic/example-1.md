# Example 1: Simple Unit Test Suite

## Problem Statement

You need to create a basic test suite for a utility module that contains simple mathematical and string manipulation functions. The goal is to verify that each function works correctly with various inputs, including edge cases like empty strings, negative numbers, and boundary values.

## Use Case

This pattern is fundamental for any project and serves as the foundation for test-driven development. You'll use this when:
- Starting a new project and writing first tests
- Testing utility functions and helper methods
- Learning test framework basics
- Establishing testing conventions for your team

## Solution Overview

We'll create a comprehensive test suite that covers:
1. Basic function testing with multiple test cases
2. Edge case handling (empty inputs, nulls, boundaries)
3. Clear test organization using describe blocks
4. Descriptive test names following the "should...when..." pattern
5. Proper use of assertions and matchers

## Complete Code

### JavaScript/TypeScript (Jest)

```javascript
// utils.js - Functions to test
export function sum(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function reverseString(str) {
  return str.split('').reverse().join('');
}

export function isPalindrome(str) {
  const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
  return cleaned === cleaned.split('').reverse().join('');
}
```

```javascript
// utils.test.js - Test suite
import { sum, multiply, capitalize, reverseString, isPalindrome } from './utils';

describe('Math Utilities', () => {
  describe('sum', () => {
    test('should add two positive numbers', () => {
      expect(sum(2, 3)).toBe(5);
    });

    test('should add negative numbers', () => {
      expect(sum(-5, -3)).toBe(-8);
    });

    test('should add positive and negative numbers', () => {
      expect(sum(10, -3)).toBe(7);
    });

    test('should handle zero', () => {
      expect(sum(0, 5)).toBe(5);
      expect(sum(5, 0)).toBe(5);
      expect(sum(0, 0)).toBe(0);
    });

    test('should handle decimal numbers', () => {
      expect(sum(1.5, 2.3)).toBeCloseTo(3.8);
    });
  });

  describe('multiply', () => {
    test('should multiply two positive numbers', () => {
      expect(multiply(3, 4)).toBe(12);
    });

    test('should multiply by zero', () => {
      expect(multiply(5, 0)).toBe(0);
      expect(multiply(0, 5)).toBe(0);
    });

    test('should multiply negative numbers', () => {
      expect(multiply(-2, -3)).toBe(6);
      expect(multiply(-2, 3)).toBe(-6);
    });

    test('should handle decimal multiplication', () => {
      expect(multiply(2.5, 4)).toBe(10);
    });
  });
});

describe('String Utilities', () => {
  describe('capitalize', () => {
    test('should capitalize first letter of lowercase word', () => {
      expect(capitalize('hello')).toBe('Hello');
    });

    test('should capitalize first letter and lowercase rest', () => {
      expect(capitalize('hELLO')).toBe('Hello');
    });

    test('should handle single character', () => {
      expect(capitalize('a')).toBe('A');
    });

    test('should handle empty string', () => {
      expect(capitalize('')).toBe('');
    });

    test('should handle null or undefined', () => {
      expect(capitalize(null)).toBe('');
      expect(capitalize(undefined)).toBe('');
    });

    test('should handle string with spaces', () => {
      expect(capitalize('hello world')).toBe('Hello world');
    });
  });

  describe('reverseString', () => {
    test('should reverse a simple string', () => {
      expect(reverseString('hello')).toBe('olleh');
    });

    test('should reverse a palindrome', () => {
      expect(reverseString('noon')).toBe('noon');
    });

    test('should handle empty string', () => {
      expect(reverseString('')).toBe('');
    });

    test('should handle single character', () => {
      expect(reverseString('a')).toBe('a');
    });

    test('should preserve spaces', () => {
      expect(reverseString('hello world')).toBe('dlrow olleh');
    });

    test('should handle numbers in string', () => {
      expect(reverseString('abc123')).toBe('321cba');
    });
  });

  describe('isPalindrome', () => {
    test('should identify simple palindrome', () => {
      expect(isPalindrome('racecar')).toBe(true);
      expect(isPalindrome('noon')).toBe(true);
    });

    test('should identify non-palindrome', () => {
      expect(isPalindrome('hello')).toBe(false);
      expect(isPalindrome('world')).toBe(false);
    });

    test('should be case-insensitive', () => {
      expect(isPalindrome('RaceCar')).toBe(true);
      expect(isPalindrome('Noon')).toBe(true);
    });

    test('should ignore spaces and punctuation', () => {
      expect(isPalindrome('A man a plan a canal Panama')).toBe(true);
      expect(isPalindrome('race a car')).toBe(false);
    });

    test('should handle empty string', () => {
      expect(isPalindrome('')).toBe(true);
    });

    test('should handle single character', () => {
      expect(isPalindrome('a')).toBe(true);
    });
  });
});
```

### Python (pytest)

```python
# utils.py - Functions to test
def sum_numbers(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def capitalize(text):
    """Capitalize first letter"""
    if not text:
        return ''
    return text[0].upper() + text[1:].lower()

def reverse_string(text):
    """Reverse a string"""
    return text[::-1]

def is_palindrome(text):
    """Check if string is palindrome"""
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]
```

```python
# test_utils.py - Test suite
import pytest
from utils import sum_numbers, multiply, capitalize, reverse_string, is_palindrome

class TestMathUtilities:
    """Test mathematical utility functions"""

    class TestSum:
        def test_add_positive_numbers(self):
            assert sum_numbers(2, 3) == 5

        def test_add_negative_numbers(self):
            assert sum_numbers(-5, -3) == -8

        def test_add_positive_and_negative(self):
            assert sum_numbers(10, -3) == 7

        def test_handle_zero(self):
            assert sum_numbers(0, 5) == 5
            assert sum_numbers(5, 0) == 5
            assert sum_numbers(0, 0) == 0

        def test_handle_decimals(self):
            assert sum_numbers(1.5, 2.3) == pytest.approx(3.8)

    class TestMultiply:
        def test_multiply_positive_numbers(self):
            assert multiply(3, 4) == 12

        def test_multiply_by_zero(self):
            assert multiply(5, 0) == 0
            assert multiply(0, 5) == 0

        def test_multiply_negative_numbers(self):
            assert multiply(-2, -3) == 6
            assert multiply(-2, 3) == -6

        def test_handle_decimals(self):
            assert multiply(2.5, 4) == 10

class TestStringUtilities:
    """Test string utility functions"""

    class TestCapitalize:
        def test_capitalize_lowercase_word(self):
            assert capitalize('hello') == 'Hello'

        def test_capitalize_and_lowercase_rest(self):
            assert capitalize('hELLO') == 'Hello'

        def test_handle_single_character(self):
            assert capitalize('a') == 'A'

        def test_handle_empty_string(self):
            assert capitalize('') == ''

        def test_handle_none(self):
            assert capitalize(None) == ''

        def test_handle_spaces(self):
            assert capitalize('hello world') == 'Hello world'

    class TestReverseString:
        def test_reverse_simple_string(self):
            assert reverse_string('hello') == 'olleh'

        def test_reverse_palindrome(self):
            assert reverse_string('noon') == 'noon'

        def test_handle_empty_string(self):
            assert reverse_string('') == ''

        def test_handle_single_character(self):
            assert reverse_string('a') == 'a'

        def test_preserve_spaces(self):
            assert reverse_string('hello world') == 'dlrow olleh'

        def test_handle_numbers(self):
            assert reverse_string('abc123') == '321cba'

    class TestIsPalindrome:
        def test_identify_simple_palindrome(self):
            assert is_palindrome('racecar') is True
            assert is_palindrome('noon') is True

        def test_identify_non_palindrome(self):
            assert is_palindrome('hello') is False
            assert is_palindrome('world') is False

        def test_case_insensitive(self):
            assert is_palindrome('RaceCar') is True
            assert is_palindrome('Noon') is True

        def test_ignore_spaces_and_punctuation(self):
            assert is_palindrome('A man a plan a canal Panama') is True
            assert is_palindrome('race a car') is False

        def test_handle_empty_string(self):
            assert is_palindrome('') is True

        def test_handle_single_character(self):
            assert is_palindrome('a') is True
```

## Code Explanation

### Line-by-Line Breakdown

**Test Structure:**
1. **Describe blocks** group related tests (e.g., all tests for `sum` function)
2. **Test names** use descriptive patterns: "should [expected behavior] when [condition]"
3. **Assertions** verify expected outcomes using appropriate matchers

**Key Testing Patterns:**

```javascript
// Pattern 1: Basic equality assertion
test('should add two positive numbers', () => {
  expect(sum(2, 3)).toBe(5);
});
```
- `expect(value)`: Wraps the actual value
- `.toBe(expected)`: Strict equality matcher (===)

```javascript
// Pattern 2: Floating point comparison
test('should handle decimal numbers', () => {
  expect(sum(1.5, 2.3)).toBeCloseTo(3.8);
});
```
- `.toBeCloseTo()`: Handles floating point precision issues
- Avoids problems with `0.1 + 0.2 !== 0.3`

```javascript
// Pattern 3: Multiple assertions in related scenarios
test('should handle zero', () => {
  expect(sum(0, 5)).toBe(5);
  expect(sum(5, 0)).toBe(5);
  expect(sum(0, 0)).toBe(0);
});
```
- Groups related edge cases together
- Tests commutative properties

```javascript
// Pattern 4: Edge case testing
test('should handle empty string', () => {
  expect(capitalize('')).toBe('');
});

test('should handle null or undefined', () => {
  expect(capitalize(null)).toBe('');
  expect(capitalize(undefined)).toBe('');
});
```
- Always test boundary conditions
- Test null/undefined/empty inputs

### Key Points

1. **Comprehensive Coverage**: Each function has multiple test cases covering:
   - Happy path (normal inputs)
   - Edge cases (empty, null, zero)
   - Boundary conditions (single character, negative numbers)
   - Special scenarios (decimals, mixed cases)

2. **Clear Organization**: Tests grouped logically:
   - By module (Math vs String utilities)
   - By function (sum, multiply, etc.)
   - Nested describe blocks for clarity

3. **Descriptive Names**: Test names read like specifications:
   - "should capitalize first letter of lowercase word"
   - "should multiply by zero"

4. **Appropriate Matchers**:
   - `.toBe()` for primitives and strict equality
   - `.toBeCloseTo()` for floating point numbers
   - `.toBe(true/false)` for boolean results

## Variations

### Variation 1: Using Test.each for Data-Driven Tests

```javascript
describe('sum - data driven', () => {
  test.each([
    [2, 3, 5],
    [-5, -3, -8],
    [10, -3, 7],
    [0, 5, 5],
    [0, 0, 0]
  ])('sum(%i, %i) should equal %i', (a, b, expected) => {
    expect(sum(a, b)).toBe(expected);
  });
});
```

**When to use**: Multiple similar test cases with different inputs.

### Variation 2: Setup/Teardown for Shared State

```javascript
describe('String utilities with setup', () => {
  let testStrings;

  beforeEach(() => {
    testStrings = {
      empty: '',
      single: 'a',
      simple: 'hello',
      mixed: 'HeLLo',
      withSpaces: 'hello world'
    };
  });

  test('capitalize handles various strings', () => {
    expect(capitalize(testStrings.empty)).toBe('');
    expect(capitalize(testStrings.simple)).toBe('Hello');
    expect(capitalize(testStrings.mixed)).toBe('Hello');
  });
});
```

**When to use**: Complex test data that needs initialization.

### Variation 3: Grouped Assertions with describe.each

```javascript
describe.each([
  ['racecar', true],
  ['noon', true],
  ['hello', false],
  ['A man a plan a canal Panama', true]
])('isPalindrome("%s")', (input, expected) => {
  test(`returns ${expected}`, () => {
    expect(isPalindrome(input)).toBe(expected);
  });
});
```

**When to use**: Testing similar behavior with different inputs.

## Common Pitfalls

### Pitfall 1: Not Testing Edge Cases

```javascript
// ❌ BAD: Only testing happy path
test('capitalizes string', () => {
  expect(capitalize('hello')).toBe('Hello');
});

// ✅ GOOD: Testing edge cases
test('capitalizes string', () => {
  expect(capitalize('hello')).toBe('Hello');
});

test('handles empty string', () => {
  expect(capitalize('')).toBe('');
});

test('handles null', () => {
  expect(capitalize(null)).toBe('');
});
```

### Pitfall 2: Vague Test Names

```javascript
// ❌ BAD: Unclear what's being tested
test('sum test 1', () => {
  expect(sum(2, 3)).toBe(5);
});

// ✅ GOOD: Clear, descriptive name
test('should add two positive numbers', () => {
  expect(sum(2, 3)).toBe(5);
});
```

### Pitfall 3: Wrong Matcher for Floating Point

```javascript
// ❌ BAD: May fail due to floating point precision
test('adds decimals', () => {
  expect(sum(0.1, 0.2)).toBe(0.3); // Fails!
});

// ✅ GOOD: Use toBeCloseTo
test('adds decimals', () => {
  expect(sum(0.1, 0.2)).toBeCloseTo(0.3);
});
```

## Testing

### Running the Tests

```bash
# JavaScript (Jest)
npm test                          # Run all tests
npm test utils.test.js           # Run specific file
npm test -- --coverage           # With coverage
npm test -- --watch              # Watch mode

# Python (pytest)
pytest test_utils.py             # Run specific file
pytest test_utils.py -v          # Verbose
pytest test_utils.py --cov      # With coverage
pytest -k "palindrome"          # Run tests matching pattern
```

### Expected Output

```
 PASS  tests/utils.test.js
  Math Utilities
    sum
      ✓ should add two positive numbers (2 ms)
      ✓ should add negative numbers (1 ms)
      ✓ should add positive and negative numbers
      ✓ should handle zero
      ✓ should handle decimal numbers (1 ms)
    multiply
      ✓ should multiply two positive numbers
      ✓ should multiply by zero
      ✓ should multiply negative numbers
      ✓ should handle decimal multiplication
  String Utilities
    capitalize
      ✓ should capitalize first letter of lowercase word
      ✓ should capitalize first letter and lowercase rest
      ✓ should handle single character
      ✓ should handle empty string
      ✓ should handle null or undefined
      ✓ should handle string with spaces
    reverseString
      ✓ should reverse a simple string
      ✓ should reverse a palindrome
      ✓ should handle empty string
      ✓ should handle single character
      ✓ should preserve spaces
      ✓ should handle numbers in string
    isPalindrome
      ✓ should identify simple palindrome
      ✓ should identify non-palindrome
      ✓ should be case-insensitive
      ✓ should ignore spaces and punctuation
      ✓ should handle empty string
      ✓ should handle single character

Test Suites: 1 passed, 1 total
Tests:       26 passed, 26 total
```

## Next Steps

1. **Add More Edge Cases**: Think about what could break your functions
2. **Try Test-Driven Development**: Write tests before implementation
3. **Explore Coverage Reports**: See what code isn't tested
4. **Practice Refactoring**: Change implementation, ensure tests still pass
5. **Move to Integration Tests**: See [Example 2](example-2.md)

## See Also

- [Example 2: Integration Test Setup](example-2.md)
- [Example 3: Mock and Stub Usage](example-3.md)
- [Core Concepts: Test Types](../../docs/core-concepts.md#test-types-and-hierarchy)
- [Best Practices: Test Structure](../../docs/best-practices.md#test-structure)
