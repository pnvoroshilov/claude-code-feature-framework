/**
 * Basic Playwright Examples
 *
 * This file demonstrates fundamental Playwright patterns for E2E testing including:
 * - Navigation and page interactions
 * - Form filling and submission
 * - Assertions and expectations
 * - Waiting strategies
 * - Test data management
 * - Authentication flows
 * - Network interception
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// BASIC NAVIGATION AND ASSERTIONS
// ============================================================================

test('homepage loads successfully', async ({ page }) => {
  await page.goto('https://example.com');

  // Assert page title
  await expect(page).toHaveTitle(/Example Domain/);

  // Assert heading is visible
  await expect(page.getByRole('heading', { name: 'Example Domain' })).toBeVisible();

  // Assert URL
  await expect(page).toHaveURL('https://example.com/');
});

test('navigation between pages', async ({ page }) => {
  await page.goto('https://example.com');

  // Click link and wait for navigation
  await page.getByRole('link', { name: 'More information' }).click();

  // Verify navigation occurred
  await expect(page).toHaveURL(/.*iana\.org.*/);
});

// ============================================================================
// FORM INTERACTIONS
// ============================================================================

test('user can submit contact form', async ({ page }) => {
  await page.goto('https://example.com/contact');

  // Fill form using accessibility-focused selectors
  await page.getByLabel('Name').fill('John Doe');
  await page.getByLabel('Email').fill('john@example.com');
  await page.getByLabel('Message').fill('This is a test message');

  // Select dropdown
  await page.getByLabel('Subject').selectOption('Support');

  // Check checkbox
  await page.getByRole('checkbox', { name: 'Subscribe to newsletter' }).check();

  // Submit form
  await page.getByRole('button', { name: 'Submit' }).click();

  // Assert success message
  await expect(page.getByText('Thank you for your message')).toBeVisible();
});

test('form validation works correctly', async ({ page }) => {
  await page.goto('https://example.com/signup');

  // Submit empty form
  await page.getByRole('button', { name: 'Sign Up' }).click();

  // Assert validation errors appear
  await expect(page.getByText('Email is required')).toBeVisible();
  await expect(page.getByText('Password is required')).toBeVisible();

  // Fill with invalid email
  await page.getByLabel('Email').fill('invalid-email');
  await page.getByRole('button', { name: 'Sign Up' }).click();

  // Assert email validation error
  await expect(page.getByText('Please enter a valid email')).toBeVisible();
});

// ============================================================================
// WAITING STRATEGIES
// ============================================================================

test('wait for element to appear', async ({ page }) => {
  await page.goto('https://example.com/dynamic');

  // Click button that loads content dynamically
  await page.getByRole('button', { name: 'Load Content' }).click();

  // Wait for element to appear (auto-wait)
  await expect(page.getByTestId('dynamic-content')).toBeVisible();

  // Alternative: explicit wait
  await page.waitForSelector('[data-testid="dynamic-content"]');
});

test('wait for network idle', async ({ page }) => {
  await page.goto('https://example.com/dashboard');

  // Wait for all network requests to complete
  await page.waitForLoadState('networkidle');

  // Now safe to interact with fully loaded page
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

test('wait for specific API response', async ({ page }) => {
  await page.goto('https://example.com/users');

  // Wait for specific API call
  const responsePromise = page.waitForResponse('**/api/users');

  // Trigger action that makes the request
  await page.getByRole('button', { name: 'Load Users' }).click();

  // Wait for and inspect response
  const response = await responsePromise;
  expect(response.status()).toBe(200);
});

// ============================================================================
// AUTHENTICATION FLOWS
// ============================================================================

test('user can login with valid credentials', async ({ page }) => {
  await page.goto('https://example.com/login');

  // Fill login form
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('SecurePassword123!');

  // Submit
  await page.getByRole('button', { name: 'Log In' }).click();

  // Assert redirect to dashboard
  await expect(page).toHaveURL(/.*dashboard/);

  // Assert user is logged in
  await expect(page.getByText('Welcome, User')).toBeVisible();
});

test('login fails with invalid credentials', async ({ page }) => {
  await page.goto('https://example.com/login');

  // Fill with wrong credentials
  await page.getByLabel('Email').fill('wrong@example.com');
  await page.getByLabel('Password').fill('wrongpassword');

  // Submit
  await page.getByRole('button', { name: 'Log In' }).click();

  // Assert error message
  await expect(page.getByRole('alert')).toContainText('Invalid credentials');

  // Assert still on login page
  await expect(page).toHaveURL(/.*login/);
});

// ============================================================================
// TEST DATA MANAGEMENT
// ============================================================================

// Factory function for unique test data
function createTestUser() {
  const timestamp = Date.now();
  return {
    email: `test-user-${timestamp}@example.com`,
    password: 'TestPassword123!',
    firstName: 'Test',
    lastName: 'User',
  };
}

test('user registration with unique data', async ({ page }) => {
  const user = createTestUser();

  await page.goto('https://example.com/signup');

  // Fill registration form
  await page.getByLabel('First Name').fill(user.firstName);
  await page.getByLabel('Last Name').fill(user.lastName);
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Password').fill(user.password);
  await page.getByLabel('Confirm Password').fill(user.password);

  // Submit
  await page.getByRole('button', { name: 'Sign Up' }).click();

  // Assert success
  await expect(page.getByText('Account created successfully')).toBeVisible();
  await expect(page).toHaveURL(/.*dashboard/);
});

// ============================================================================
// NETWORK INTERCEPTION AND MOCKING
// ============================================================================

test('mock API response', async ({ page }) => {
  // Intercept API call and return mock data
  await page.route('**/api/users', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Alice', email: 'alice@example.com' },
        { id: 2, name: 'Bob', email: 'bob@example.com' },
      ]),
    });
  });

  await page.goto('https://example.com/users');

  // Assert mocked data is displayed
  await expect(page.getByText('Alice')).toBeVisible();
  await expect(page.getByText('Bob')).toBeVisible();
});

test('test API error handling', async ({ page }) => {
  // Simulate API failure
  await page.route('**/api/products', async (route) => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' }),
    });
  });

  await page.goto('https://example.com/products');

  // Assert error message is shown
  await expect(page.getByText('Failed to load products')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

// ============================================================================
// ELEMENT STATE ASSERTIONS
// ============================================================================

test('element state assertions', async ({ page }) => {
  await page.goto('https://example.com/form');

  // Assert element visibility
  await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();
  await expect(page.getByTestId('hidden-field')).toBeHidden();

  // Assert element enabled/disabled
  await expect(page.getByRole('button', { name: 'Submit' })).toBeDisabled();
  await page.getByLabel('Email').fill('test@example.com');
  await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();

  // Assert element text
  await expect(page.getByRole('heading')).toHaveText('Contact Form');
  await expect(page.getByTestId('error-message')).toContainText('required');

  // Assert input values
  await expect(page.getByLabel('Email')).toHaveValue('test@example.com');

  // Assert checkbox/radio state
  await expect(page.getByRole('checkbox', { name: 'Agree' })).not.toBeChecked();
  await page.getByRole('checkbox', { name: 'Agree' }).check();
  await expect(page.getByRole('checkbox', { name: 'Agree' })).toBeChecked();
});

// ============================================================================
// KEYBOARD AND MOUSE INTERACTIONS
// ============================================================================

test('keyboard interactions', async ({ page }) => {
  await page.goto('https://example.com/search');

  // Type in search box
  const searchBox = page.getByPlaceholder('Search...');
  await searchBox.type('playwright testing');

  // Press Enter to submit
  await searchBox.press('Enter');

  // Assert search results
  await expect(page.getByTestId('search-results')).toBeVisible();
});

test('mouse interactions', async ({ page }) => {
  await page.goto('https://example.com/interactive');

  // Hover over element
  await page.getByTestId('dropdown-trigger').hover();
  await expect(page.getByTestId('dropdown-menu')).toBeVisible();

  // Double click
  await page.getByTestId('editable-field').dblclick();
  await expect(page.getByTestId('edit-mode')).toBeVisible();

  // Right click (context menu)
  await page.getByTestId('item').click({ button: 'right' });
  await expect(page.getByTestId('context-menu')).toBeVisible();
});

// ============================================================================
// FILE UPLOADS AND DOWNLOADS
// ============================================================================

test('upload file', async ({ page }) => {
  await page.goto('https://example.com/upload');

  // Upload file
  const fileInput = page.getByLabel('Upload file');
  await fileInput.setInputFiles('./test-files/sample.pdf');

  // Assert file is uploaded
  await expect(page.getByText('sample.pdf')).toBeVisible();
});

test('download file', async ({ page }) => {
  await page.goto('https://example.com/download');

  // Start waiting for download before clicking
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download Report' }).click();

  // Wait for download to complete
  const download = await downloadPromise;

  // Assert download properties
  expect(download.suggestedFilename()).toBe('report.pdf');

  // Save file
  await download.saveAs('./downloads/report.pdf');
});

// ============================================================================
// WORKING WITH IFRAMES
// ============================================================================

test('interact with iframe content', async ({ page }) => {
  await page.goto('https://example.com/iframe-page');

  // Get iframe by selector
  const iframe = page.frameLocator('#payment-iframe');

  // Interact with elements inside iframe
  await iframe.getByLabel('Card Number').fill('4242 4242 4242 4242');
  await iframe.getByLabel('Expiry').fill('12/25');
  await iframe.getByLabel('CVC').fill('123');

  // Submit form in iframe
  await iframe.getByRole('button', { name: 'Pay Now' }).click();

  // Assert result in main page
  await expect(page.getByText('Payment successful')).toBeVisible();
});

// ============================================================================
// MULTIPLE TABS AND WINDOWS
// ============================================================================

test('handle new tab', async ({ page, context }) => {
  await page.goto('https://example.com');

  // Click link that opens new tab
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.getByRole('link', { name: 'Open in new tab' }).click(),
  ]);

  // Wait for new page to load
  await newPage.waitForLoadState();

  // Interact with new page
  await expect(newPage).toHaveURL(/.*new-page/);
  await expect(newPage.getByRole('heading')).toBeVisible();

  // Close new page
  await newPage.close();
});

// ============================================================================
// GEOLOCATION AND PERMISSIONS
// ============================================================================

test('mock geolocation', async ({ page, context }) => {
  // Set geolocation
  await context.setGeolocation({ latitude: 37.7749, longitude: -122.4194 });

  // Grant geolocation permission
  await context.grantPermissions(['geolocation']);

  await page.goto('https://example.com/location');

  // Click button to get location
  await page.getByRole('button', { name: 'Get My Location' }).click();

  // Assert location is displayed
  await expect(page.getByText('San Francisco')).toBeVisible();
});

// ============================================================================
// SCREENSHOTS AND VIDEOS
// ============================================================================

test('take screenshot on failure', async ({ page }) => {
  await page.goto('https://example.com');

  try {
    // This will fail
    await expect(page.getByText('Non-existent text')).toBeVisible();
  } catch (error) {
    // Take screenshot of failure
    await page.screenshot({ path: 'test-failure.png', fullPage: true });
    throw error;
  }
});

test('take element screenshot', async ({ page }) => {
  await page.goto('https://example.com');

  // Screenshot specific element
  const header = page.getByRole('banner');
  await header.screenshot({ path: 'header.png' });
});

// ============================================================================
// MOBILE DEVICE EMULATION
// ============================================================================

test('test mobile viewport', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });

  await page.goto('https://example.com');

  // Assert mobile menu is visible
  await expect(page.getByTestId('mobile-menu-button')).toBeVisible();

  // Assert desktop menu is hidden
  await expect(page.getByTestId('desktop-menu')).toBeHidden();
});

// ============================================================================
// BEST PRACTICES EXAMPLES
// ============================================================================

test.describe('Best Practices Examples', () => {
  // Use beforeEach for common setup
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('example 1: semantic selectors', async ({ page }) => {
    // ✅ GOOD - Use accessibility-focused selectors
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByText('Welcome back').click();

    // ❌ AVOID - CSS selectors that break with styling changes
    // await page.click('.btn-primary');
    // await page.fill('#email-input-1234');
  });

  test('example 2: proper waiting', async ({ page }) => {
    // ✅ GOOD - Wait for specific condition
    await page.getByRole('button', { name: 'Load Data' }).click();
    await page.waitForSelector('[data-loaded="true"]');
    await expect(page.getByTestId('data-table')).toBeVisible();

    // ❌ AVOID - Arbitrary timeout
    // await page.waitForTimeout(3000);
  });

  test('example 3: descriptive test names', async ({ page }) => {
    // ✅ GOOD - Test name describes what is being tested and expected outcome
    // "user can complete checkout with valid payment method"
    // "form validation prevents submission with invalid email"
    // "admin can delete user account and cascade related data"
  });
});
