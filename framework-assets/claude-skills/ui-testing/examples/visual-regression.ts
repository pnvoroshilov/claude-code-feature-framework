/**
 * Visual Regression Testing Examples
 *
 * This file demonstrates visual regression testing patterns including:
 * - Basic screenshot comparison
 * - Element-specific snapshots
 * - Responsive testing across viewports
 * - Handling dynamic content
 * - Visual diff configuration
 * - Integration with Percy/Chromatic
 * - Best practices for stable visual tests
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// BASIC VISUAL REGRESSION
// ============================================================================

test('homepage visual snapshot', async ({ page }) => {
  await page.goto('https://example.com');

  // Wait for page to be fully loaded
  await page.waitForLoadState('networkidle');

  // Compare full page screenshot
  await expect(page).toHaveScreenshot('homepage.png');
});

test('element-specific snapshot', async ({ page }) => {
  await page.goto('https://example.com');

  // Snapshot specific element
  const header = page.getByRole('banner');
  await expect(header).toHaveScreenshot('header.png');

  const footer = page.getByRole('contentinfo');
  await expect(footer).toHaveScreenshot('footer.png');
});

// ============================================================================
// HANDLING DYNAMIC CONTENT
// ============================================================================

test('hide dynamic content before snapshot', async ({ page }) => {
  await page.goto('https://example.com/dashboard');

  // Hide elements that change on every load
  await page.addStyleTag({
    content: `
      .timestamp,
      .live-chat,
      .user-avatar,
      .advertisement {
        visibility: hidden !important;
      }
    `,
  });

  await expect(page).toHaveScreenshot('dashboard.png');
});

test('mask sensitive data', async ({ page }) => {
  await page.goto('https://example.com/profile');

  // Take screenshot with masked regions
  await expect(page).toHaveScreenshot('profile.png', {
    mask: [
      page.getByTestId('user-email'),
      page.getByTestId('phone-number'),
      page.getByTestId('address'),
    ],
  });
});

test('replace dynamic text before snapshot', async ({ page }) => {
  await page.goto('https://example.com/orders');

  // Replace timestamps with fixed values
  await page.evaluate(() => {
    document.querySelectorAll('.timestamp').forEach((el) => {
      el.textContent = '2024-01-15 10:00:00';
    });

    // Replace user-specific data
    document.querySelectorAll('.order-id').forEach((el) => {
      el.textContent = 'ORDER-12345';
    });
  });

  await expect(page).toHaveScreenshot('orders.png');
});

// ============================================================================
// DISABLE ANIMATIONS
// ============================================================================

test('disable animations for consistent snapshots', async ({ page }) => {
  await page.goto('https://example.com');

  // Disable all animations and transitions
  await page.addStyleTag({
    content: `
      *,
      *::before,
      *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `,
  });

  await expect(page).toHaveScreenshot('no-animations.png');
});

// Global configuration approach
test.use({
  // Disable animations for all tests
  actionTimeout: 0,
  // Add animation disabling to all pages
  extraHTTPHeaders: {
    'prefers-reduced-motion': 'reduce',
  },
});

// ============================================================================
// RESPONSIVE VISUAL TESTING
// ============================================================================

const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1920, height: 1080 },
];

viewports.forEach(({ name, width, height }) => {
  test(`homepage visual - ${name}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto('https://example.com');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot(`homepage-${name}.png`, {
      fullPage: true,
    });
  });
});

// ============================================================================
// VISUAL DIFF CONFIGURATION
// ============================================================================

test('snapshot with custom threshold', async ({ page }) => {
  await page.goto('https://example.com');

  // Allow small differences (anti-aliasing, font rendering)
  await expect(page).toHaveScreenshot('homepage-threshold.png', {
    maxDiffPixels: 100, // Max 100 pixels can differ
  });
});

test('snapshot with percentage threshold', async ({ page }) => {
  await page.goto('https://example.com');

  // Allow 0.1% difference
  await expect(page).toHaveScreenshot('homepage-percentage.png', {
    maxDiffPixelRatio: 0.001,
  });
});

test('clip specific area for snapshot', async ({ page }) => {
  await page.goto('https://example.com');

  // Snapshot specific region by coordinates
  await expect(page).toHaveScreenshot('header-region.png', {
    clip: {
      x: 0,
      y: 0,
      width: 1920,
      height: 100,
    },
  });
});

// ============================================================================
// WAITING FOR RESOURCES
// ============================================================================

test('wait for images to load', async ({ page }) => {
  await page.goto('https://example.com/gallery');

  // Wait for all images to load
  await page.waitForLoadState('networkidle');

  // Additional wait for images
  await page.evaluate(() => {
    return Promise.all(
      Array.from(document.images)
        .filter((img) => !img.complete)
        .map(
          (img) =>
            new Promise((resolve) => {
              img.onload = img.onerror = resolve;
            })
        )
    );
  });

  await expect(page).toHaveScreenshot('gallery.png');
});

test('wait for fonts to load', async ({ page }) => {
  await page.goto('https://example.com');

  // Wait for fonts to be ready
  await page.evaluate(() => document.fonts.ready);

  await expect(page).toHaveScreenshot('fonts-loaded.png');
});

test('wait for custom loading indicator', async ({ page }) => {
  await page.goto('https://example.com/dashboard');

  // Wait for loading spinner to disappear
  await page.waitForSelector('[data-loading="true"]', { state: 'hidden' });

  // Wait for data-loaded attribute
  await page.waitForSelector('[data-loaded="true"]', { state: 'visible' });

  await expect(page).toHaveScreenshot('dashboard-loaded.png');
});

// ============================================================================
// COMPONENT VISUAL TESTING
// ============================================================================

test.describe('Button Component Visual Tests', () => {
  test('button states', async ({ page }) => {
    await page.goto('https://example.com/components/button');

    // Default state
    const defaultButton = page.getByTestId('button-default');
    await expect(defaultButton).toHaveScreenshot('button-default.png');

    // Hover state
    await defaultButton.hover();
    await expect(defaultButton).toHaveScreenshot('button-hover.png');

    // Active state (simulated)
    await defaultButton.evaluate((el) => el.classList.add('active'));
    await expect(defaultButton).toHaveScreenshot('button-active.png');

    // Disabled state
    const disabledButton = page.getByTestId('button-disabled');
    await expect(disabledButton).toHaveScreenshot('button-disabled.png');
  });

  test('button variants', async ({ page }) => {
    await page.goto('https://example.com/components/button');

    // Snapshot all button variants
    await expect(page.getByTestId('button-primary')).toHaveScreenshot('button-primary.png');
    await expect(page.getByTestId('button-secondary')).toHaveScreenshot('button-secondary.png');
    await expect(page.getByTestId('button-danger')).toHaveScreenshot('button-danger.png');
  });
});

// ============================================================================
// FORM VISUAL TESTING
// ============================================================================

test.describe('Form Visual States', () => {
  test('empty form', async ({ page }) => {
    await page.goto('https://example.com/contact');
    await expect(page.getByTestId('contact-form')).toHaveScreenshot('form-empty.png');
  });

  test('filled form', async ({ page }) => {
    await page.goto('https://example.com/contact');

    // Fill form
    await page.getByLabel('Name').fill('John Doe');
    await page.getByLabel('Email').fill('john@example.com');
    await page.getByLabel('Message').fill('Test message');

    await expect(page.getByTestId('contact-form')).toHaveScreenshot('form-filled.png');
  });

  test('form validation errors', async ({ page }) => {
    await page.goto('https://example.com/contact');

    // Submit empty form to trigger validation
    await page.getByRole('button', { name: 'Submit' }).click();

    // Wait for validation messages
    await page.waitForSelector('[data-validation-error]');

    await expect(page.getByTestId('contact-form')).toHaveScreenshot('form-errors.png');
  });
});

// ============================================================================
// DARK MODE / THEME TESTING
// ============================================================================

test('light theme snapshot', async ({ page }) => {
  await page.goto('https://example.com');

  // Ensure light theme
  await page.evaluate(() => {
    document.documentElement.setAttribute('data-theme', 'light');
  });

  await expect(page).toHaveScreenshot('homepage-light.png');
});

test('dark theme snapshot', async ({ page }) => {
  await page.goto('https://example.com');

  // Switch to dark theme
  await page.evaluate(() => {
    document.documentElement.setAttribute('data-theme', 'dark');
  });

  await expect(page).toHaveScreenshot('homepage-dark.png');
});

// ============================================================================
// SCROLL POSITION SNAPSHOTS
// ============================================================================

test('snapshot at different scroll positions', async ({ page }) => {
  await page.goto('https://example.com/long-page');

  // Top of page
  await expect(page).toHaveScreenshot('page-top.png');

  // Middle of page
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
  await page.waitForTimeout(500); // Wait for smooth scroll
  await expect(page).toHaveScreenshot('page-middle.png');

  // Bottom of page
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(500);
  await expect(page).toHaveScreenshot('page-bottom.png');
});

test('full page snapshot', async ({ page }) => {
  await page.goto('https://example.com/long-page');

  // Capture entire page regardless of viewport
  await expect(page).toHaveScreenshot('full-page.png', {
    fullPage: true,
  });
});

// ============================================================================
// PERCY INTEGRATION (Cloud Visual Testing)
// ============================================================================

// Note: Requires @percy/playwright package

import percySnapshot from '@percy/playwright';

test('Percy snapshot - homepage', async ({ page }) => {
  await page.goto('https://example.com');
  await page.waitForLoadState('networkidle');

  // Send snapshot to Percy
  await percySnapshot(page, 'Homepage');
});

test('Percy responsive snapshots', async ({ page }) => {
  await page.goto('https://example.com');
  await page.waitForLoadState('networkidle');

  // Percy automatically tests multiple viewports
  await percySnapshot(page, 'Homepage - Responsive', {
    widths: [375, 768, 1280, 1920],
  });
});

test('Percy with custom options', async ({ page }) => {
  await page.goto('https://example.com/dashboard');

  await percySnapshot(page, 'Dashboard', {
    widths: [1280],
    minHeight: 1024,
    percyCSS: `
      .timestamp,
      .live-chat {
        visibility: hidden !important;
      }
    `,
  });
});

// ============================================================================
// CHROMATIC INTEGRATION (Storybook Visual Testing)
// ============================================================================

// Chromatic is typically used with Storybook components
// Example configuration in .storybook/main.js:
/*
module.exports = {
  addons: ['@chromatic-com/storybook'],
};
*/

// Example story with Chromatic
/*
// Button.stories.tsx
import { Button } from './Button';

export default {
  component: Button,
  parameters: {
    chromatic: {
      // Delay screenshot for animations
      delay: 300,
      // Disable animations
      pauseAnimationAtEnd: true,
      // Test specific viewports
      viewports: [320, 768, 1200],
    },
  },
};

export const Primary = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
};

export const Hover = {
  args: {
    variant: 'primary',
    children: 'Hover me',
  },
  parameters: {
    pseudo: { hover: true },
  },
};
*/

// ============================================================================
// BEST PRACTICES EXAMPLES
// ============================================================================

test.describe('Visual Testing Best Practices', () => {
  test('stable snapshot workflow', async ({ page }) => {
    await page.goto('https://example.com');

    // 1. Wait for all resources
    await page.waitForLoadState('networkidle');
    await page.evaluate(() => document.fonts.ready);

    // 2. Hide/replace dynamic content
    await page.addStyleTag({
      content: `
        .timestamp,
        .advertisement,
        .live-chat {
          visibility: hidden !important;
        }
      `,
    });

    // 3. Disable animations
    await page.addStyleTag({
      content: `
        * {
          animation-duration: 0s !important;
          transition-duration: 0s !important;
        }
      `,
    });

    // 4. Wait for custom indicators
    await page.waitForSelector('[data-loaded="true"]');

    // 5. Take snapshot with threshold
    await expect(page).toHaveScreenshot('stable-snapshot.png', {
      maxDiffPixels: 50,
    });
  });

  test('avoid flaky snapshots', async ({ page }) => {
    await page.goto('https://example.com');

    // ❌ BAD - Random timeout
    // await page.waitForTimeout(3000);

    // ✅ GOOD - Wait for specific condition
    await page.waitForSelector('[data-loaded="true"]');
    await page.evaluate(() => document.fonts.ready);

    // ✅ GOOD - Hide dynamic content
    await page.evaluate(() => {
      document.querySelectorAll('.dynamic-content').forEach((el) => {
        el.style.display = 'none';
      });
    });

    await expect(page).toHaveScreenshot('stable.png');
  });

  test('organize snapshots by feature', async ({ page }) => {
    // Use descriptive names with feature prefix
    await page.goto('https://example.com/auth/login');
    await expect(page).toHaveScreenshot('auth-login-page.png');

    await page.goto('https://example.com/auth/signup');
    await expect(page).toHaveScreenshot('auth-signup-page.png');

    await page.goto('https://example.com/checkout/payment');
    await expect(page).toHaveScreenshot('checkout-payment-page.png');
  });
});

// ============================================================================
// UPDATING SNAPSHOTS
// ============================================================================

// To update all snapshots when intentional changes are made:
// npx playwright test --update-snapshots

// To update specific test:
// npx playwright test visual-regression.spec.ts --update-snapshots

// To update snapshots for specific browser:
// npx playwright test --update-snapshots --project=chromium

// ============================================================================
// CI/CD VISUAL TESTING
// ============================================================================

// Example GitHub Actions workflow:
/*
name: Visual Regression Tests

on: [pull_request]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run visual tests
        run: npx playwright test visual-regression.spec.ts

      - name: Upload diff images on failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: visual-diffs
          path: test-results/**/*-diff.png
          retention-days: 7
*/
