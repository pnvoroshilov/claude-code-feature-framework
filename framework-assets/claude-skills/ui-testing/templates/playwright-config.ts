/**
 * Production-Ready Playwright Configuration
 *
 * This configuration includes:
 * - Cross-browser testing (Chromium, Firefox, WebKit)
 * - Mobile device emulation
 * - Parallel execution
 * - Retry logic for flaky tests
 * - Screenshot and video on failure
 * - Trace collection
 * - Global setup/teardown
 * - Environment-specific settings
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directory for test files
  testDir: './tests/e2e',

  // Directory for test artifacts
  outputDir: './test-results',

  // Maximum time one test can run
  timeout: 30 * 1000, // 30 seconds

  // Expect timeout for assertions
  expect: {
    timeout: 5000, // 5 seconds
  },

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Number of parallel workers
  workers: process.env.CI ? 2 : undefined, // Auto-detect on local

  // Reporter to use
  reporter: [
    // HTML reporter for visual results
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    // Line reporter for CI
    ['line'],
    // JUnit XML for CI systems
    ...(process.env.CI ? [['junit', { outputFile: 'test-results/junit.xml' }]] : []),
  ],

  // Shared settings for all projects
  use: {
    // Base URL for all navigation
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // Collect trace when retrying the failed test
    trace: 'on-first-retry',

    // Record video on failure
    video: 'retain-on-failure',

    // Take screenshot on failure
    screenshot: 'only-on-failure',

    // Browser context options
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    acceptDownloads: true,

    // Action timeout
    actionTimeout: 10 * 1000, // 10 seconds

    // Navigation timeout
    navigationTimeout: 30 * 1000, // 30 seconds
  },

  // Configure projects for major browsers
  projects: [
    // ============================================================================
    // DESKTOP BROWSERS
    // ============================================================================

    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome', // Use Google Chrome instead of Chromium
      },
    },

    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
      },
    },

    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
      },
    },

    {
      name: 'edge',
      use: {
        ...devices['Desktop Edge'],
        channel: 'msedge',
      },
    },

    // ============================================================================
    // MOBILE BROWSERS
    // ============================================================================

    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
      },
    },

    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 13'],
      },
    },

    // ============================================================================
    // TABLET DEVICES
    // ============================================================================

    {
      name: 'tablet-ipad',
      use: {
        ...devices['iPad Pro'],
      },
    },

    // ============================================================================
    // BRANDED TESTS (for specific scenarios)
    // ============================================================================

    // Smoke tests - run on every commit
    {
      name: 'smoke-tests',
      testMatch: /.*\.smoke\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
      },
      retries: 0, // No retries for smoke tests
    },

    // Visual regression tests
    {
      name: 'visual-tests',
      testMatch: /.*\.visual\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },

    // Accessibility tests
    {
      name: 'a11y-tests',
      testMatch: /.*\.a11y\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],

  // ============================================================================
  // GLOBAL SETUP AND TEARDOWN
  // ============================================================================

  // Run once before all tests
  globalSetup: require.resolve('./tests/global-setup'),

  // Run once after all tests
  globalTeardown: require.resolve('./tests/global-teardown'),

  // ============================================================================
  // WEB SERVER (for local development)
  // ============================================================================

  // Start local dev server before tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes
    stdout: 'ignore',
    stderr: 'pipe',
  },
});

// ============================================================================
// EXAMPLE: global-setup.ts
// ============================================================================

/*
import { chromium, FullConfig } from '@playwright/test';
import path from 'path';

async function globalSetup(config: FullConfig) {
  console.log('Running global setup...');

  // Create authentication state
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Login once and save state
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL || 'test@example.com');
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD || 'password123');
  await page.getByRole('button', { name: 'Log In' }).click();

  // Wait for login to complete
  await page.waitForURL('**/dashboard');

  // Save authentication state
  await page.context().storageState({
    path: path.join(__dirname, 'tests/auth-state.json'),
  });

  await browser.close();

  console.log('Global setup completed.');
}

export default globalSetup;
*/

// ============================================================================
// EXAMPLE: global-teardown.ts
// ============================================================================

/*
import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('Running global teardown...');

  // Cleanup test data, close databases, etc.
  // Example: Delete test users created during tests

  console.log('Global teardown completed.');
}

export default globalTeardown;
*/

// ============================================================================
// EXAMPLE: Using authentication state in tests
// ============================================================================

/*
import { test, expect } from '@playwright/test';

// Use saved authentication state
test.use({
  storageState: 'tests/auth-state.json',
});

test('user can view profile', async ({ page }) => {
  // Test starts already authenticated
  await page.goto('/profile');
  await expect(page.getByRole('heading', { name: 'My Profile' })).toBeVisible();
});
*/

// ============================================================================
// ENVIRONMENT-SPECIFIC CONFIGURATION
// ============================================================================

// Development config
export const devConfig = defineConfig({
  ...baseConfig,
  use: {
    ...baseConfig.use,
    baseURL: 'http://localhost:3000',
    video: 'off',
    trace: 'off',
  },
  workers: 1,
  retries: 0,
});

// Staging config
export const stagingConfig = defineConfig({
  ...baseConfig,
  use: {
    ...baseConfig.use,
    baseURL: 'https://staging.example.com',
  },
});

// Production config (read-only tests)
export const productionConfig = defineConfig({
  ...baseConfig,
  use: {
    ...baseConfig.use,
    baseURL: 'https://example.com',
  },
  retries: 3, // More retries for production
});

// ============================================================================
// CUSTOM TEST FIXTURES
// ============================================================================

/*
// tests/fixtures.ts
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';

type MyFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  authenticatedPage: Page;
};

export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  authenticatedPage: async ({ page }, use) => {
    // Login before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password');
    await use(page);
  },
});

export { expect } from '@playwright/test';
*/

// ============================================================================
// EXAMPLE USAGE IN TESTS
// ============================================================================

/*
import { test, expect } from './fixtures';

test('user can view dashboard', async ({ authenticatedPage: page }) => {
  // Page is already authenticated
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/.*dashboard/);
});

test('use page objects', async ({ loginPage, dashboardPage }) => {
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password');
  await dashboardPage.expectToBeVisible();
});
*/

// ============================================================================
// PLAYWRIGHT CONFIG FOR CI/CD
// ============================================================================

// Example package.json scripts:
/*
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:smoke": "playwright test --grep @smoke",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:chrome": "playwright test --project=chromium",
    "test:e2e:firefox": "playwright test --project=firefox",
    "test:e2e:webkit": "playwright test --project=webkit",
    "test:e2e:mobile": "playwright test --project=mobile-*",
    "test:e2e:update-snapshots": "playwright test --update-snapshots",
    "test:report": "playwright show-report"
  }
}
*/

// ============================================================================
// GITHUB ACTIONS EXAMPLE
// ============================================================================

/*
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    timeout-minutes: 60
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

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps ${{ matrix.browser }}

      - name: Run E2E tests
        run: npx playwright test --project=${{ matrix.browser }}
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
          TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report-${{ matrix.browser }}
          path: playwright-report/
          retention-days: 30

      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: test-results-${{ matrix.browser }}
          path: test-results/
          retention-days: 7
*/
