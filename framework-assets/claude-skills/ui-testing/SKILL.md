---
name: ui-testing
description: Comprehensive E2E and UI testing best practices covering Playwright, Cypress, Selenium, visual regression, accessibility testing, and Page Object Model patterns. Use when writing E2E tests, setting up test automation, implementing visual regression testing, testing user flows, debugging flaky UI tests, or integrating UI tests into CI/CD pipelines.
version: 1.0.0
tags: [testing, e2e, ui-testing, playwright, cypress, selenium, visual-regression, accessibility, page-object-model]
---

# UI and E2E Testing Expert

Expert guidance for creating, maintaining, and running comprehensive end-to-end (E2E) and user interface (UI) tests that validate complete user workflows and visual elements.

## What is E2E/UI Testing?

E2E testing validates complete user workflows from start to finish through the actual user interface. Unlike unit tests (isolated components) and integration tests (component interactions), E2E tests verify the entire application stack.

test_types_comparison[3]{test_type,scope,examples,speed}:
Unit Tests,Single component in isolation,Function with mocked dependencies,Very Fast (ms)
Integration Tests,Multiple components interacting,API + Database + Cache,Fast-Medium (100ms-2s)
E2E Tests,Complete user workflow through UI,Login create order checkout in browser,Slow (5-30s)

## Test Pyramid Placement

```
     /\
    /E2E\      <- Few (5-10%) - Critical paths only
   /------\
  / Integ \   <- More (20-30%) - Component interactions
 /----------\
/   Unit     \ <- Most (60-75%) - Business logic
--------------
```

e2e_test_principles[6]{principle,description}:
Test critical paths only,Focus on happy paths and high-risk user flows
User perspective,Test what users see and do not implementation
Real browser environment,Use actual browsers not headless when debugging
Independent tests,Each test should be fully isolated and self-contained
Stable selectors,Use data-testid or accessibility selectors not CSS classes
Fast feedback,Keep tests under 30 seconds optimize for quick execution

## When to Use E2E Tests

use_e2e_tests_when[8]{scenario,example}:
Critical user flows,User registration checkout payment processing
Smoke testing,Deploy verification that core features work
Cross-browser compatibility,Verify behavior in Chrome Firefox Safari
Visual regression,Detect unintended UI changes screenshots
User acceptance testing,Validate features meet requirements
Integration validation,Verify frontend backend database work together
Authentication flows,Login logout password reset OAuth
Complex interactions,Multi-step wizards drag-drop file uploads

avoid_e2e_tests_for[4]{scenario,use_instead}:
Business logic validation,Unit tests are faster and more reliable
API contract verification,Integration tests with API client
Edge cases and error handling,Unit or integration tests
Performance testing,Dedicated performance testing tools

## Testing Framework Comparison

framework_comparison[4]{framework,strengths,weaknesses,best_for}:
Playwright,Fast modern multi-browser auto-wait built-in tools,Newer smaller community,New projects modern apps cross-browser testing
Cypress,Excellent DX time travel debugging real-time reload,Chrome-family only network stubbing limitations,SPAs rapid development developer experience
Selenium,Mature huge ecosystem all browsers and languages,Verbose slow setup requires explicit waits,Legacy systems specific browser needs
Puppeteer,Fast Chrome-only good for scraping,Chrome-only limited testing features,Chrome-specific tests scraping automation

framework_selection_criteria[6]{criterion,playwright,cypress,selenium}:
Cross-browser support,Chrome Firefox Safari Webkit,Chrome Edge Electron only,All major browsers
Auto-wait built-in,Yes - intelligent auto-wait,Yes - automatic retries,No - manual explicit waits
Parallel execution,Yes - native support,Paid tier only,Yes - with Selenium Grid
Network interception,Full control,Full control,Limited
Mobile testing,Yes - device emulation,Yes - viewport only,Yes - Appium needed
Learning curve,Low-Medium,Low,Medium-High

## Playwright MCP Server Configuration

When using Playwright MCP (Model Context Protocol) server for browser automation with Claude Code or other AI agents, configure parallel browser sessions properly.

### Key MCP Configuration Parameters

playwright_mcp_params[6]{parameter,description,example}:
--isolated,Keep browser profile in memory without saving to disk,npx @playwright/mcp --isolated
--shared-browser-context,Reuse same browser context between all HTTP clients,npx @playwright/mcp --shared-browser-context
--storage-state <path>,Load cookies/localStorage from file into isolated context,npx @playwright/mcp --storage-state auth.json
--user-data-dir <path>,Persistent profile location for session data,npx @playwright/mcp --user-data-dir ./profile
--viewport-size <size>,Browser viewport dimensions,npx @playwright/mcp --viewport-size 1920x1080
--timeout-action <ms>,Action timeout in milliseconds (default 5000),npx @playwright/mcp --timeout-action 10000

### MCP Configuration for Claude Code

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp",
        "--isolated"
      ]
    }
  }
}
```

### Parallel Browser Sessions

For multiple parallel browser instances, use `--isolated` mode:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp",
        "--isolated",
        "--viewport-size", "1920x1080"
      ]
    }
  }
}
```

mcp_session_modes[3]{mode,description,use_case}:
Persistent (default),Retains browser profile across sessions,Development testing with saved login state
Isolated (--isolated),Fresh profile each session no disk writes,CI/CD parallel tests clean state
Shared (--shared-browser-context),Multiple clients share one context,Team collaboration same session

**IMPORTANT:** For parallel test execution, always use `--isolated` mode to prevent session conflicts between concurrent browser instances.

## Playwright Fundamentals (Recommended)

Playwright is the recommended framework for new projects due to modern architecture, excellent tooling, and cross-browser support.

playwright_core_concepts[7]{concept,description}:
Browser Context,Isolated browser session like incognito window
Page,Single browser tab or window within context
Locator,Query to find elements with auto-wait and retry
Action,User interaction like click type hover
Assertion,Verify element state or content with auto-retry
Trace,Complete recording of test execution for debugging
Screenshot/Video,Visual evidence of test execution and failures

### Basic Playwright Test Structure

```typescript
import { test, expect } from '@playwright/test';

test('user can create account', async ({ page }) => {
  // Navigate to page
  await page.goto('https://example.com/signup');

  // Fill form using reliable selectors
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('SecurePass123');

  // Click button
  await page.getByRole('button', { name: 'Sign Up' }).click();

  // Assert success
  await expect(page.getByText('Welcome!')).toBeVisible();
  await expect(page).toHaveURL(/.*dashboard/);
});
```

## Page Object Model (POM) Pattern

The Page Object Model encapsulates page structure and actions, making tests maintainable and reusable.

pom_benefits[6]{benefit,description}:
Maintainability,Change selector once update all tests
Reusability,Share page actions across multiple tests
Readability,Tests read like user stories
Encapsulation,Hide implementation details from tests
Type safety,TypeScript provides autocompletion and validation
Reduced duplication,DRY principle for page interactions

**See [examples/page-object-model.ts](examples/page-object-model.ts) for complete POM implementation.**

## Selector Strategy Best Practices

selector_priority[7]{priority,selector_type,example,why}:
1,Accessibility role,getByRole('button' { name: 'Submit' }),Accessible to screen readers and users
2,Accessibility label,getByLabel('Email address'),Semantic and accessible
3,Placeholder text,getByPlaceholder('Enter email'),User-visible text
4,Text content,getByText('Welcome back'),What users actually see
5,Test ID,getByTestId('submit-button'),Stable across refactors
6,CSS selector,.btn-primary,Fragile - breaks with styling changes
7,XPath,//div[@class='container']//button[1],Very fragile - avoid if possible

selector_anti_patterns[5]{anti_pattern,problem,better_approach}:
CSS classes,Changes with styling refactors,Use semantic selectors or test IDs
Positional selectors,.item:nth-child(3),Breaks when order changes,Use unique identifiers
Generated IDs,#input-1234-abcd,Changes on each build,Use data-testid or labels
Complex XPath,//div[contains(@class 'x')]/..//span,Hard to read and maintain,Use simpler semantic selectors
Text with punctuation,getByText('Hello!'),Breaks with i18n changes,Use test IDs or roles

**See [reference/selectors-guide.md](reference/selectors-guide.md) for comprehensive selector strategies.**

### Adding Test IDs to Your App

```typescript
// React component
<button data-testid="checkout-button" onClick={handleCheckout}>
  Checkout
</button>

// Test
await page.getByTestId('checkout-button').click();
```

## Waiting Strategies

Playwright has built-in auto-wait for most actions. Explicit waits are rarely needed.

wait_strategies[5]{strategy,when_to_use,example}:
Auto-wait (default),Most actions,await page.click('button') // waits automatically
waitForSelector,Element appears dynamically,await page.waitForSelector('[data-loaded=true]')
waitForLoadState,Page navigation complete,await page.waitForLoadState('networkidle')
waitForResponse,API call completes,await page.waitForResponse('**/api/users')
waitForTimeout (avoid),Last resort for timing issues,await page.waitForTimeout(1000) // Anti-pattern

### Common Wait Anti-Patterns

```typescript
// ❌ BAD - Arbitrary sleep
await page.waitForTimeout(3000);
await page.click('button');

// ✅ GOOD - Wait for specific condition
await page.waitForSelector('button:not([disabled])');
await page.click('button');

// ✅ BETTER - Auto-wait with timeout
await page.click('button', { timeout: 5000 });

// ✅ BEST - Wait for network activity
await page.waitForLoadState('networkidle');
await page.click('button');
```

## Test Data Management

test_data_strategies[5]{strategy,use_case,implementation}:
Fixtures,Static test data,JSON files or hardcoded objects
Factory functions,Dynamic test data generation,faker.js or similar library
API setup,Create data via backend API before test,Use API calls in beforeEach
Database seeding,Bulk data insertion,SQL scripts or ORM seeders
In-test creation,Create data through UI as part of test,Use helper functions

### Test Data Best Practices

```typescript
// ✅ GOOD - Unique data per test
test('login works', async ({ page }) => {
  const user = {
    email: `user-${Date.now()}@example.com`,
    password: 'SecurePass123!'
  };
  await api.createUser(user); // Setup via API
  await loginPage.login(user.email, user.password);
});

// ✅ BETTER - Factory function
test('login works', async ({ page }) => {
  const user = createTestUser(); // Generates unique user
  await api.createUser(user);
  await loginPage.login(user.email, user.password);
});
```

## Test Isolation and Independence

isolation_principles[6]{principle,implementation}:
Each test is independent,Don't rely on previous test state or execution order
Clean state before test,Reset DB clear cookies create fresh test data
No shared test data,Each test creates its own data or uses unique data
Parallel execution safe,Tests can run simultaneously without conflicts
Cleanup after test,Delete created resources reset state
Use browser contexts,Isolated sessions prevent cookie/storage leakage

### Browser Context Isolation

```typescript
// Each test gets fresh browser context (cookies, storage isolated)
test('user A can login', async ({ page }) => {
  await page.goto('/login');
  await loginPage.login('userA@example.com', 'password');
  // Test runs in isolation
});

test('user B can login', async ({ page }) => {
  await page.goto('/login');
  await loginPage.login('userB@example.com', 'password');
  // Completely separate session from previous test
});
```

## Handling Flaky Tests

flaky_test_causes[8]{cause,solution}:
Race conditions,Use waitForSelector or waitForLoadState
Network timing,Mock network requests or use waitForResponse
Animation timing,Disable animations in test mode or wait for animationend
Dynamic content,Wait for specific element state not arbitrary timeout
Popup timing,Use waitForSelector for popup elements
Browser caching,Clear cache before test or use incognito context
Third-party scripts,Mock or disable analytics ads chat widgets
Test data conflicts,Use unique test data per test or reset DB

### Debugging Flaky Tests

```typescript
// Enable traces for debugging
test.use({ trace: 'on-first-retry' });

// Add diagnostic logging
test('flaky test', async ({ page }) => {
  console.log('Starting test...');
  await page.goto('/');
  console.log('Page loaded:', await page.title());
  await page.screenshot({ path: 'debug-screenshot.png' });
});

// Run single test multiple times to reproduce
// npx playwright test --repeat-each=20 tests/flaky.spec.ts
```

## Visual Regression Testing

Visual regression testing detects unintended UI changes by comparing screenshots.

visual_testing_tools[5]{tool,approach,best_for}:
Playwright Screenshots,Built-in screenshot comparison,Simple visual regression
Percy,Cloud-based visual diffing,Teams with budget visual review workflow
Chromatic,Storybook integration cloud storage,Component-driven development
BackstopJS,Local reference screenshots CSS selector testing,Free alternative headless testing
Applitools,AI-powered visual testing,Enterprise complex responsive apps

**See [examples/visual-regression.ts](examples/visual-regression.ts) for complete visual testing examples.**

## Accessibility Testing

Accessibility testing ensures your app is usable by people with disabilities and complies with WCAG guidelines.

accessibility_aspects[6]{aspect,what_to_test}:
Keyboard navigation,Tab order focus indicators no keyboard traps
Screen reader support,ARIA labels semantic HTML alt text
Color contrast,Text meets WCAG AA or AAA contrast ratios
Focus management,Focus moves logically focus visible on interactive elements
Form accessibility,Labels associated with inputs error messages
Interactive elements,Buttons links have accessible names and roles

### Accessibility Testing with axe-core

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage has no accessibility violations', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page })
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

### Keyboard Navigation Testing

```typescript
test('user can navigate with keyboard', async ({ page }) => {
  await page.goto('/');

  // Tab through interactive elements
  await page.keyboard.press('Tab');
  let focused = await page.evaluate(() => document.activeElement?.tagName);
  expect(focused).toBe('A'); // First link

  await page.keyboard.press('Tab');
  focused = await page.evaluate(() => document.activeElement?.tagName);
  expect(focused).toBe('BUTTON'); // First button

  // Activate with Enter/Space
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/.*search/);
});
```

## Cross-Browser Testing

Cross-browser testing validates your app works consistently across different browsers.

browser_testing_strategy[4]{priority,browsers,reason}:
Must test,Chrome Firefox Safari,Cover 90%+ of users
Should test,Edge,Significant market share especially enterprise
Consider testing,Mobile Safari Chrome Mobile,Mobile traffic important
Low priority,IE11 Opera older browsers,Minimal usage unless specific requirement

**See [templates/playwright-config.ts](templates/playwright-config.ts) for complete cross-browser configuration.**

## Performance Optimization

Keep E2E tests fast to maintain rapid feedback loops.

performance_tips[10]{technique,impact}:
Run tests in parallel,3-5x faster with multiple workers
Use headed mode only for debugging,Headless is 20-30% faster
Disable unnecessary browser features,Images CSS can be disabled for speed tests
Reuse authentication state,Save logged-in state reuse across tests
Mock external APIs,Eliminate network latency for third-party services
Skip animations,Reduce wait times for CSS animations
Use global setup,Share expensive setup across all tests
Optimize selectors,Efficient selectors reduce query time
Limit visual tests,Screenshots are slow use sparingly
Strategic test selection,Run smoke tests first full suite on CI

### Reusing Authentication State

```typescript
// global-setup.ts
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Login once
  await page.goto('https://example.com/login');
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');

  // Save authentication state
  await page.context().storageState({ path: 'auth.json' });
  await browser.close();
}

export default globalSetup;

// Use in config
export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  use: { storageState: 'auth.json' },
});
```

## CI/CD Integration

ci_cd_best_practices[8]{practice,implementation}:
Parallel execution,Use matrix strategy to run multiple browsers simultaneously
Retry failed tests,Playwright --retries=2 to handle transient failures
Record traces on failure,Enable trace: 'retain-on-failure' for debugging
Upload artifacts,Save screenshots videos traces for failed tests
Cache dependencies,Cache node_modules and Playwright browsers
Run on multiple OS,Test on Linux macOS Windows if needed
Separate smoke and full suite,Fast smoke tests on every commit full suite nightly
Integrate with PR checks,Block merge if E2E tests fail

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps ${{ matrix.browser }}
      - run: npx playwright test --project=${{ matrix.browser }}
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-results-${{ matrix.browser }}
          path: playwright-report/
```

## Best Practices Summary

e2e_best_practices[15]{practice,explanation}:
Test critical paths only,Focus on high-value user flows not every feature
Use Page Object Model,Encapsulate page logic for maintainability
Prefer semantic selectors,Use roles labels text over CSS selectors
Add data-testid for dynamic content,Stable selectors for elements without semantic meaning
Wait for conditions not timeouts,Use waitForSelector not sleep
Keep tests independent,Each test should run in isolation
Use unique test data,Avoid conflicts between parallel tests
Enable traces for debugging,Capture full context when tests fail
Run in parallel,Faster feedback loop
Mock external services,Reduce flakiness and improve speed
Test accessibility,Ensure app is usable by everyone
Visual regression for critical pages,Catch unintended UI changes
Cross-browser testing,Verify consistent behavior
Optimize for speed,Fast tests run more often
Monitor flaky tests,Fix or quarantine unstable tests

## Quick Reference Commands

playwright_commands[10]{command,description}:
npx playwright test,Run all tests
npx playwright test --project=chromium,Run tests in specific browser
npx playwright test tests/login.spec.ts,Run specific test file
npx playwright test --grep "@smoke",Run tests with tag
npx playwright test --headed,Run with browser visible
npx playwright test --debug,Run in debug mode with inspector
npx playwright test --ui,Run with UI mode
npx playwright codegen,Generate tests by recording interactions
npx playwright show-report,View HTML test report
npx playwright show-trace trace.zip,View trace for debugging

## See Also

- **[README.md](README.md)** - Overview and quick start
- **[examples/playwright-basic.ts](examples/playwright-basic.ts)** - Basic Playwright examples
- **[examples/page-object-model.ts](examples/page-object-model.ts)** - Complete POM implementation
- **[examples/visual-regression.ts](examples/visual-regression.ts)** - Visual testing examples
- **[templates/playwright-config.ts](templates/playwright-config.ts)** - Production-ready config
- **[reference/selectors-guide.md](reference/selectors-guide.md)** - Comprehensive selector strategies

---

**Need more details?** Check the examples and reference directories for comprehensive code samples and advanced patterns.
