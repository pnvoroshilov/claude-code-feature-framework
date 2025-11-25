# UI Testing Skill

Comprehensive E2E and UI testing best practices and examples for creating, maintaining, and running user interface tests with modern frameworks like Playwright, Cypress, and Selenium.

## What This Skill Provides

This skill helps Claude Code assist with:

- Writing effective E2E tests for critical user flows
- Implementing Page Object Model (POM) pattern
- Setting up test frameworks (Playwright, Cypress, Selenium)
- Visual regression testing with screenshots
- Accessibility testing with axe-core
- Cross-browser testing strategies
- Debugging flaky UI tests
- CI/CD integration for automated testing

## Quick Start

**Read the main skill file**: [SKILL.md](SKILL.md)

The main skill file contains:
- E2E testing fundamentals and test pyramid
- Testing framework comparison (Playwright, Cypress, Selenium)
- Playwright core concepts and best practices
- Page Object Model pattern
- Selector strategies and best practices
- Test isolation and data management
- Visual regression and accessibility testing
- Cross-browser testing and CI/CD integration

## Examples

**Comprehensive code examples**: [examples/](examples/)

Framework-specific examples are organized by use case:

- [Playwright Basic Examples](examples/playwright-basic.ts)
- [Page Object Model Pattern](examples/page-object-model.ts)
- [Visual Regression Testing](examples/visual-regression.ts)

## Templates

**Production-ready configuration templates**: [templates/](templates/)

Ready-to-use configurations:

- [Playwright Configuration](templates/playwright-config.ts) - Complete setup for cross-browser testing

## Reference

**Detailed reference guides**: [reference/](reference/)

In-depth documentation:

- [Selectors Guide](reference/selectors-guide.md) - Comprehensive selector strategies

## When Claude Should Use This Skill

Claude should activate this skill when you:

trigger_scenarios[15]{user_mention,claude_action}:
"write E2E tests",Create end-to-end tests for user flows
"test user flow",Implement tests for complete workflows
"Playwright setup",Configure Playwright for testing
"Cypress tests",Write tests using Cypress framework
"page object model",Implement POM pattern for maintainability
"visual regression",Set up screenshot comparison tests
"accessibility testing",Test with axe-core for WCAG compliance
"cross-browser testing",Configure multi-browser test execution
"flaky test",Debug and fix unreliable UI tests
"test selectors",Improve selector strategies
"E2E CI/CD",Integrate UI tests into deployment pipeline
"test authentication",Test login/logout flows
"mock API in tests",Intercept network requests
"screenshot tests",Implement visual testing
"keyboard navigation test",Test accessibility with keyboard

## Key Concepts

### Test Pyramid

E2E tests should be:
- **Few in number** (5-10% of total tests) - Only critical paths
- **Focused on user flows** - Test what users actually do
- **Fast** - Keep under 30 seconds per test
- **Stable** - No flaky tests allowed

### Testing Framework Selection

framework_comparison[4]{framework,best_for,key_strength}:
Playwright,Modern apps cross-browser testing,Auto-wait multi-browser built-in tools
Cypress,SPAs rapid development,Excellent DX time travel debugging
Selenium,Legacy systems specific browsers,Mature ecosystem all browsers
Puppeteer,Chrome automation scraping,Fast Chrome-only simple API

### Selector Priority

Always prefer accessibility-focused selectors:

1. **Accessibility role** - `getByRole('button', { name: 'Submit' })`
2. **Accessibility label** - `getByLabel('Email address')`
3. **User-visible text** - `getByText('Welcome back')`
4. **Test ID** - `getByTestId('submit-button')`
5. Avoid CSS classes and XPath (fragile)

### Page Object Model Benefits

pom_benefits[6]{benefit,value}:
Maintainability,Change selector once update all tests
Reusability,Share page actions across tests
Readability,Tests read like user stories
Type safety,TypeScript provides validation
Reduced duplication,DRY principle for interactions
Encapsulation,Hide implementation details

## Quick Reference Commands

### Playwright

```bash
npx playwright test                    # Run all tests
npx playwright test --project=chromium # Run specific browser
npx playwright test --headed           # Show browser
npx playwright test --debug            # Debug mode
npx playwright codegen                 # Record tests
npx playwright show-report             # View results
```

### Cypress

```bash
npx cypress open                       # Interactive mode
npx cypress run                        # Headless mode
npx cypress run --browser chrome       # Specific browser
npx cypress run --spec "**/*login*"   # Run specific tests
```

### Selenium (Python)

```bash
pytest tests/e2e/                      # Run all E2E tests
pytest tests/e2e/test_login.py         # Run specific file
pytest -k "login"                      # Run matching tests
pytest --headed                        # Show browser
```

## Common Patterns

### Basic Test Structure

```typescript
test('user completes checkout', async ({ page }) => {
  // Setup: Navigate and login
  await page.goto('/shop');
  await loginPage.login('user@example.com', 'password');

  // Action: Complete checkout flow
  await page.getByTestId('add-to-cart').click();
  await page.getByRole('button', { name: 'Checkout' }).click();
  await checkoutPage.fillShippingInfo(testAddress);
  await checkoutPage.submitPayment(testCard);

  // Assert: Verify success
  await expect(page.getByText('Order confirmed')).toBeVisible();
  await expect(page).toHaveURL(/.*order-success/);
});
```

### Page Object Pattern

```typescript
// pages/login.page.ts
export class LoginPage {
  constructor(private page: Page) {}

  async login(email: string, password: string) {
    await this.page.getByLabel('Email').fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Log In' }).click();
  }
}

// tests/login.spec.ts
test('user can login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('user@example.com', 'password');
  await expect(page).toHaveURL(/.*dashboard/);
});
```

## Common Anti-Patterns to Avoid

anti_patterns_summary[8]{pattern,why_bad,alternative}:
Arbitrary timeouts,Flaky unreliable,Wait for specific conditions
CSS class selectors,Breaks with styling,Use semantic selectors or test IDs
Shared test data,Conflicts in parallel,Generate unique data per test
Testing every feature,Slow expensive,Focus on critical paths only
No Page Objects,Hard to maintain,Use POM for reusability
Deep CSS selectors,Fragile breaks easily,Use semantic selectors
Ignoring accessibility,Excludes users,Test with axe-core
No test isolation,Tests depend on each other,Each test fully independent

## Best Practices Summary

best_practices[10]{practice,why_important}:
Test critical paths only,Maximize value minimize maintenance
Use Page Object Model,Maintainable scalable test code
Prefer semantic selectors,Stable accessible reliable
Wait for conditions not timeouts,Eliminate flakiness
Keep tests independent,Parallel execution reliable results
Generate unique test data,Avoid conflicts isolation
Enable trace on failure,Debug issues effectively
Run in parallel,Fast feedback loop
Mock external services,Speed stability
Monitor and fix flaky tests,Maintain confidence in suite

## Testing Strategies

### Smoke Tests (Run on every deployment)

```typescript
test.describe('Smoke Tests', () => {
  test('homepage loads @smoke', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
  });

  test('user can login @smoke', async ({ page }) => {
    // Critical login flow
  });

  test('user can view products @smoke', async ({ page }) => {
    // Essential product browsing
  });
});
```

### Full Regression Suite (Nightly or pre-release)

```typescript
test.describe('Full Regression', () => {
  test('complete checkout flow', async ({ page }) => {
    // Full user journey
  });

  test('admin can manage inventory', async ({ page }) => {
    // Complex admin workflows
  });

  test('password reset works', async ({ page }) => {
    // Edge case flows
  });
});
```

## File Structure

```
ui-testing/
├── README.md                  # This file - overview and quick start
├── SKILL.md                   # Main skill file (478 lines)
├── examples/                  # Code examples
│   ├── playwright-basic.ts    # Basic Playwright patterns
│   ├── page-object-model.ts   # Complete POM implementation
│   └── visual-regression.ts   # Visual testing examples
├── templates/                 # Configuration templates
│   └── playwright-config.ts   # Production-ready config
└── reference/                 # Detailed guides
    └── selectors-guide.md     # Comprehensive selector strategies
```

## Testing Frameworks Documentation

- [Playwright Documentation](https://playwright.dev/)
- [Cypress Documentation](https://docs.cypress.io/)
- [Selenium Documentation](https://www.selenium.dev/)
- [Testing Library](https://testing-library.com/)
- [Axe Accessibility Testing](https://github.com/dequelabs/axe-core)

## Additional Resources

- [Martin Fowler - Testing Strategies](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google Testing Blog](https://testing.googleblog.com/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Web.dev Accessibility Testing](https://web.dev/accessibility/)

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-01-25
- **Maintained by**: Claude Code Skills

---

**Note**: This skill focuses on UI and E2E testing specifically. For unit testing or integration testing, refer to other specialized skills in the `.claude/skills/` directory.
