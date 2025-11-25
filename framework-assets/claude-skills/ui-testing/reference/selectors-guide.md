# Comprehensive Selector Strategies for UI Testing

This guide covers selector strategies for Playwright, Cypress, and Selenium with best practices for creating stable, maintainable test selectors.

## Selector Priority Order

Always prefer selectors that are:
1. **Accessible** - Work with screen readers
2. **Stable** - Don't change with styling
3. **Readable** - Express user intent

selector_priority[8]{priority,selector_type,example,reliability}:
1,Accessibility role,getByRole('button' { name: 'Submit' }),Very High
2,Accessibility label,getByLabel('Email address'),Very High
3,Placeholder text,getByPlaceholder('Enter email'),High
4,Text content,getByText('Welcome back'),High
5,Alt text,getByAltText('Company logo'),High
6,Test ID,getByTestId('submit-button'),Very High (custom)
7,CSS selector,[data-action="submit"],Medium
8,XPath,//button[@type='submit'],Low (avoid)

## Playwright Selectors

### Role-Based Selectors (Recommended)

Role selectors query elements by their accessibility role, making tests accessible and stable.

```typescript
// Button
await page.getByRole('button', { name: 'Submit' });
await page.getByRole('button', { name: /save/i }); // regex

// Link
await page.getByRole('link', { name: 'Learn More' });
await page.getByRole('link', { name: 'Home' }).first(); // first match

// Textbox (input, textarea)
await page.getByRole('textbox', { name: 'Email' });
await page.getByRole('textbox').nth(0); // by index

// Checkbox and Radio
await page.getByRole('checkbox', { name: 'Remember me' });
await page.getByRole('radio', { name: 'Credit Card' });

// Combobox (select)
await page.getByRole('combobox', { name: 'Country' });

// Heading
await page.getByRole('heading', { name: 'Welcome' });
await page.getByRole('heading', { level: 1 }); // h1 only

// Navigation
await page.getByRole('navigation');
await page.getByRole('main'); // main content

// Dialog (modal)
await page.getByRole('dialog');
await page.getByRole('alertdialog');

// List items
await page.getByRole('listitem');
await page.getByRole('list');

// Table elements
await page.getByRole('table');
await page.getByRole('row');
await page.getByRole('cell');
```

### Label-Based Selectors

```typescript
// Input by label
await page.getByLabel('Email');
await page.getByLabel('Password');

// Exact match
await page.getByLabel('Email', { exact: true });

// Partial match (default)
await page.getByLabel('Email address');
```

### Text-Based Selectors

```typescript
// By visible text
await page.getByText('Welcome back');
await page.getByText('Click here', { exact: true });

// Regex matching
await page.getByText(/welcome/i); // case insensitive
await page.getByText(/\$\d+\.\d{2}/); // price pattern

// Contains text
await page.getByText('Error', { exact: false });
```

### Placeholder-Based Selectors

```typescript
// By placeholder attribute
await page.getByPlaceholder('Enter your email');
await page.getByPlaceholder(/search/i);
```

### Alt Text Selectors (Images)

```typescript
// By alt attribute
await page.getByAltText('Company Logo');
await page.getByAltText(/profile/i);
```

### Test ID Selectors

Test IDs provide stable selectors for elements without semantic meaning.

```typescript
// By data-testid attribute
await page.getByTestId('submit-button');
await page.getByTestId('user-profile-card');

// Custom attribute name (configured in playwright.config.ts)
// testIdAttribute: 'data-cy'
await page.getByTestId('submit-button'); // uses data-cy
```

### CSS and Locator Selectors

```typescript
// CSS selector
await page.locator('.btn-primary');
await page.locator('#main-content');
await page.locator('[data-action="submit"]');

// Combined selectors
await page.locator('button.primary:visible');
await page.locator('input[type="email"]');

// :has() selector (parent with specific child)
await page.locator('.card:has(.error-message)');

// :has-text() selector
await page.locator('.card:has-text("Welcome")');
```

### Filtering and Chaining

```typescript
// Filter by text
await page.getByRole('listitem').filter({ hasText: 'Active' });

// Filter by another locator
await page.getByRole('listitem').filter({ has: page.getByRole('heading') });

// Chain locators
const card = page.getByTestId('product-card').filter({ hasText: 'Laptop' });
await card.getByRole('button', { name: 'Add to Cart' }).click();

// Get nth element
await page.getByRole('listitem').nth(2); // 0-indexed
await page.getByRole('listitem').first();
await page.getByRole('listitem').last();
```

## Cypress Selectors

### Built-in Commands

```javascript
// By data-cy (recommended)
cy.get('[data-cy="submit-button"]');

// By data-testid
cy.get('[data-testid="login-form"]');

// By CSS
cy.get('.btn-primary');
cy.get('#main-content');

// By tag and attribute
cy.get('button[type="submit"]');
cy.get('input[name="email"]');
```

### Contains and Find

```javascript
// Contains text
cy.contains('Submit');
cy.contains('button', 'Submit'); // button containing text

// Find within element
cy.get('.card').find('.title');
cy.get('form').find('input').first();

// Parent and children
cy.get('li').parent();
cy.get('ul').children();
cy.get('.item').siblings();
```

### Cypress Testing Library

```javascript
// Using @testing-library/cypress
cy.findByRole('button', { name: 'Submit' });
cy.findByLabelText('Email');
cy.findByPlaceholderText('Search...');
cy.findByText('Welcome');
cy.findByTestId('submit-button');

// All variants (multiple elements)
cy.findAllByRole('listitem');
```

## Selenium Selectors (Python)

### By Class Methods

```python
from selenium.webdriver.common.by import By

# By ID
driver.find_element(By.ID, "submit-button")

# By class name
driver.find_element(By.CLASS_NAME, "btn-primary")

# By CSS selector
driver.find_element(By.CSS_SELECTOR, "[data-testid='login-form']")
driver.find_element(By.CSS_SELECTOR, "button.primary")

# By name attribute
driver.find_element(By.NAME, "email")

# By tag name
driver.find_element(By.TAG_NAME, "button")

# By link text
driver.find_element(By.LINK_TEXT, "Learn More")
driver.find_element(By.PARTIAL_LINK_TEXT, "Learn")

# By XPath (avoid if possible)
driver.find_element(By.XPATH, "//button[@type='submit']")
```

### Finding Multiple Elements

```python
# Find all matching elements
buttons = driver.find_elements(By.CSS_SELECTOR, "button")
for btn in buttons:
    print(btn.text)

# Get specific element from list
items = driver.find_elements(By.CLASS_NAME, "list-item")
third_item = items[2]
```

## Adding Test IDs to Your Application

### React/JSX

```jsx
// Basic test ID
<button data-testid="submit-button">Submit</button>

// Dynamic test IDs
<div data-testid={`product-${product.id}`}>
  {product.name}
</div>

// With TypeScript
interface Props {
  'data-testid'?: string;
}

const Button: React.FC<Props> = ({ 'data-testid': testId, children }) => (
  <button data-testid={testId}>{children}</button>
);
```

### Vue

```vue
<template>
  <button data-testid="submit-button">Submit</button>
  <div :data-testid="`product-${product.id}`">{{ product.name }}</div>
</template>
```

### Angular

```html
<!-- Component template -->
<button data-testid="submit-button">Submit</button>
<div [attr.data-testid]="'product-' + product.id">{{ product.name }}</div>
```

### HTML

```html
<button data-testid="submit-button" type="submit">Submit</button>
<input data-testid="email-input" type="email" placeholder="Enter email" />
```

## Selector Anti-Patterns

### Avoid These Patterns

anti_patterns[10]{pattern,why_bad,better_alternative}:
CSS classes,.btn-primary changes with styling,Use role or test ID
Generated IDs,#input_1234 changes on rebuild,Use label or test ID
Position-based,.item:nth-child(3),Use unique identifier or test ID
XPath with indexes,//div[1]/button[2],Use semantic selector
Long CSS chains,div.container > div.row > div.col > button,Use test ID
Text with dynamic content,"Price: $99.99",Use test ID or partial match
Styling attributes,[style*='display'],Use data attribute or state
Framework-specific classes,.MuiButton-root,Use role or test ID
Inline styles,[style='color: red'],Use data attribute
Complex XPath,//div[contains(@class 'x')]/..//span,Use simpler semantic selector

### Anti-Pattern Examples

```typescript
// ❌ BAD - Fragile selectors
await page.locator('.MuiButton-root.MuiButton-contained');
await page.locator('#user_name_input_field_1234');
await page.locator('div:nth-child(3) > div:nth-child(2) > button');
await page.locator('//div[@class="container"]//button[1]');
await page.locator('[class*="btn"][class*="primary"]');

// ✅ GOOD - Stable selectors
await page.getByRole('button', { name: 'Submit' });
await page.getByLabel('Username');
await page.getByTestId('submit-button');
await page.getByRole('listitem').filter({ hasText: 'Active' });
```

## Building a Selector Strategy

### Step 1: Start with Accessibility

```typescript
// First, try role-based selectors
await page.getByRole('button', { name: 'Add to Cart' });
await page.getByRole('textbox', { name: 'Search' });
await page.getByRole('checkbox', { name: 'Remember me' });
```

### Step 2: Fall Back to Label/Text

```typescript
// If role doesn't work, try label or text
await page.getByLabel('Email Address');
await page.getByPlaceholder('Enter your email');
await page.getByText('Welcome to our store');
```

### Step 3: Use Test IDs for Complex Cases

```typescript
// For elements without semantic meaning
await page.getByTestId('sidebar-toggle');
await page.getByTestId('product-card-123');
await page.getByTestId('chart-container');
```

### Step 4: Combine and Filter

```typescript
// When you need to be more specific
const productCard = page.getByTestId('product-card').filter({ hasText: 'Laptop' });
const addButton = productCard.getByRole('button', { name: 'Add to Cart' });
await addButton.click();
```

## Selector Debugging

### Playwright

```typescript
// Highlight element
await page.locator('.my-element').highlight();

// Log element info
const element = page.locator('.my-element');
console.log(await element.evaluate(el => el.outerHTML));

// Count elements
const count = await page.locator('.item').count();
console.log(`Found ${count} items`);

// Check if exists
const exists = await page.locator('.my-element').count() > 0;
```

### Browser DevTools

1. **Playwright Inspector**: `npx playwright test --debug`
2. **Chrome DevTools**: `$x('//button')` for XPath, `$$('button')` for CSS
3. **Accessibility Inspector**: Chrome DevTools > Elements > Accessibility tab

### Validating Selectors

```typescript
test('validate selector finds correct element', async ({ page }) => {
  await page.goto('/');

  // Check selector matches exactly one element
  const button = page.getByRole('button', { name: 'Submit' });
  await expect(button).toHaveCount(1);

  // Verify it's the right element
  await expect(button).toHaveAttribute('type', 'submit');
  await expect(button).toBeVisible();
});
```

## Selector Strategy Checklist

When writing selectors, ask:

selector_checklist[8]{question,action_if_no}:
Is this element accessible?,Add ARIA attributes or use test ID
Does selector use semantic role?,Try getByRole first
Is selector stable across styling changes?,Avoid CSS classes use role/testid
Is selector readable and expresses intent?,Refactor to semantic selector
Does selector work across browsers?,Test in multiple browsers
Is selector unique on page?,Add filtering or more specific selector
Will selector break with i18n?,Use test ID for internationalized text
Is selector maintainable?,Document selector strategy

## Framework-Specific Best Practices

### Playwright

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    testIdAttribute: 'data-testid', // or 'data-cy', 'data-qa'
  },
});

// Test file
test('use configured test ID', async ({ page }) => {
  await page.getByTestId('submit-button').click();
});
```

### Cypress

```javascript
// cypress.config.js
module.exports = {
  env: {
    testIdAttribute: 'data-cy',
  },
};

// cypress/support/commands.js
Cypress.Commands.add('getByTestId', (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args);
});

// Test file
cy.getByTestId('submit-button').click();
```

### Selenium

```python
# Custom helper
def get_by_testid(driver, testid):
    return driver.find_element(By.CSS_SELECTOR, f'[data-testid="{testid}"]')

# Usage
submit_btn = get_by_testid(driver, "submit-button")
submit_btn.click()
```

## Summary

### Golden Rules

1. **Prefer accessibility selectors** - They're stable and test accessibility
2. **Add test IDs strategically** - For complex UI without semantic meaning
3. **Avoid CSS classes** - They change with styling
4. **Keep selectors simple** - One level of specificity
5. **Document unusual selectors** - Explain why complex selectors are needed

### Quick Reference

quick_reference[6]{scenario,recommended_selector}:
Button with text,getByRole('button' { name: 'Submit' })
Form input with label,getByLabel('Email')
Search box,getByPlaceholder('Search...')
Navigation link,getByRole('link' { name: 'Home' })
Custom component,getByTestId('custom-widget')
List item by content,getByRole('listitem').filter({ hasText: 'Active' })

---

**Need more examples?** Check the main [SKILL.md](../SKILL.md) and [examples/](../examples/) directory for comprehensive code samples.
