/**
 * Page Object Model (POM) Pattern - Complete Implementation
 *
 * This file demonstrates a complete Page Object Model implementation including:
 * - Page classes with locators and actions
 * - Component classes for reusable UI elements
 * - Base page class with common functionality
 * - Test examples using page objects
 * - Advanced patterns (fluent API, page factories)
 */

import { test, expect, Page, Locator } from '@playwright/test';

// ============================================================================
// BASE PAGE CLASS
// ============================================================================

/**
 * BasePage provides common functionality for all page objects
 */
export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to the page
   */
  async goto(path: string) {
    await this.page.goto(path);
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get page title
   */
  async getTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * Take screenshot
   */
  async screenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png` });
  }

  /**
   * Check if element is visible
   */
  async isVisible(locator: Locator): Promise<boolean> {
    return await locator.isVisible();
  }
}

// ============================================================================
// COMPONENT CLASSES (Reusable UI Elements)
// ============================================================================

/**
 * Navigation component - appears on all pages
 */
export class NavigationComponent {
  readonly page: Page;
  readonly homeLink: Locator;
  readonly productsLink: Locator;
  readonly cartLink: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.homeLink = page.getByRole('link', { name: 'Home' });
    this.productsLink = page.getByRole('link', { name: 'Products' });
    this.cartLink = page.getByTestId('cart-link');
    this.userMenu = page.getByTestId('user-menu');
    this.logoutButton = page.getByRole('button', { name: 'Logout' });
  }

  async navigateToHome() {
    await this.homeLink.click();
  }

  async navigateToProducts() {
    await this.productsLink.click();
  }

  async navigateToCart() {
    await this.cartLink.click();
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
  }

  async getCartItemCount(): Promise<string> {
    const badge = this.page.getByTestId('cart-badge');
    return await badge.textContent() || '0';
  }
}

/**
 * Modal component - generic modal dialog
 */
export class ModalComponent {
  readonly page: Page;
  readonly modal: Locator;
  readonly title: Locator;
  readonly closeButton: Locator;
  readonly confirmButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.modal = page.getByRole('dialog');
    this.title = this.modal.getByRole('heading');
    this.closeButton = this.modal.getByRole('button', { name: 'Close' });
    this.confirmButton = this.modal.getByRole('button', { name: 'Confirm' });
    this.cancelButton = this.modal.getByRole('button', { name: 'Cancel' });
  }

  async isOpen(): Promise<boolean> {
    return await this.modal.isVisible();
  }

  async getTitle(): Promise<string> {
    return await this.title.textContent() || '';
  }

  async confirm() {
    await this.confirmButton.click();
    await this.modal.waitFor({ state: 'hidden' });
  }

  async cancel() {
    await this.cancelButton.click();
    await this.modal.waitFor({ state: 'hidden' });
  }

  async close() {
    await this.closeButton.click();
    await this.modal.waitFor({ state: 'hidden' });
  }
}

// ============================================================================
// PAGE CLASSES
// ============================================================================

/**
 * LoginPage - Handles login functionality
 */
export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;
  readonly signupLink: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.loginButton = page.getByRole('button', { name: 'Log In' });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot Password?' });
    this.signupLink = page.getByRole('link', { name: 'Sign Up' });
  }

  async goto() {
    await super.goto('/login');
  }

  /**
   * Perform login with email and password
   */
  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  /**
   * Fluent API example - allows chaining
   */
  async fillEmail(email: string): Promise<LoginPage> {
    await this.emailInput.fill(email);
    return this;
  }

  async fillPassword(password: string): Promise<LoginPage> {
    await this.passwordInput.fill(password);
    return this;
  }

  async submit(): Promise<void> {
    await this.loginButton.click();
  }

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string> {
    await this.errorMessage.waitFor({ state: 'visible' });
    return await this.errorMessage.textContent() || '';
  }

  /**
   * Check if login button is enabled
   */
  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.loginButton.isEnabled();
  }
}

/**
 * SignupPage - Handles user registration
 */
export class SignupPage extends BasePage {
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly termsCheckbox: Locator;
  readonly signupButton: Locator;
  readonly validationErrors: Locator;

  constructor(page: Page) {
    super(page);
    this.firstNameInput = page.getByLabel('First Name');
    this.lastNameInput = page.getByLabel('Last Name');
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password', { exact: true });
    this.confirmPasswordInput = page.getByLabel('Confirm Password');
    this.termsCheckbox = page.getByRole('checkbox', { name: 'I agree to the terms' });
    this.signupButton = page.getByRole('button', { name: 'Sign Up' });
    this.validationErrors = page.getByTestId('validation-error');
  }

  async goto() {
    await super.goto('/signup');
  }

  /**
   * Complete signup form with user data
   */
  async signup(userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
  }) {
    await this.firstNameInput.fill(userData.firstName);
    await this.lastNameInput.fill(userData.lastName);
    await this.emailInput.fill(userData.email);
    await this.passwordInput.fill(userData.password);
    await this.confirmPasswordInput.fill(userData.password);
    await this.termsCheckbox.check();
    await this.signupButton.click();
  }

  /**
   * Get all validation errors
   */
  async getValidationErrors(): Promise<string[]> {
    const errors = await this.validationErrors.allTextContents();
    return errors;
  }
}

/**
 * ProductsPage - Product listing and filtering
 */
export class ProductsPage extends BasePage {
  readonly navigation: NavigationComponent;
  readonly searchInput: Locator;
  readonly categoryFilter: Locator;
  readonly priceSort: Locator;
  readonly productCards: Locator;
  readonly loadingSpinner: Locator;

  constructor(page: Page) {
    super(page);
    this.navigation = new NavigationComponent(page);
    this.searchInput = page.getByPlaceholder('Search products...');
    this.categoryFilter = page.getByRole('combobox', { name: 'Category' });
    this.priceSort = page.getByRole('combobox', { name: 'Sort by' });
    this.productCards = page.getByTestId('product-card');
    this.loadingSpinner = page.getByTestId('loading');
  }

  async goto() {
    await super.goto('/products');
  }

  /**
   * Search for products
   */
  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
    await this.waitForProductsLoad();
  }

  /**
   * Filter by category
   */
  async filterByCategory(category: string) {
    await this.categoryFilter.selectOption(category);
    await this.waitForProductsLoad();
  }

  /**
   * Sort products
   */
  async sortBy(option: string) {
    await this.priceSort.selectOption(option);
    await this.waitForProductsLoad();
  }

  /**
   * Wait for products to load
   */
  async waitForProductsLoad() {
    await this.loadingSpinner.waitFor({ state: 'hidden' });
  }

  /**
   * Get product by name and return ProductCard helper
   */
  getProduct(name: string): ProductCard {
    const card = this.page.getByTestId('product-card').filter({ hasText: name });
    return new ProductCard(this.page, card);
  }

  /**
   * Get number of displayed products
   */
  async getProductCount(): Promise<number> {
    return await this.productCards.count();
  }

  /**
   * Get all product names
   */
  async getProductNames(): Promise<string[]> {
    const cards = await this.productCards.all();
    const names = await Promise.all(
      cards.map(card => card.getByTestId('product-name').textContent())
    );
    return names.filter((name): name is string => name !== null);
  }
}

/**
 * ProductCard - Helper class for individual product card
 */
export class ProductCard {
  readonly page: Page;
  readonly card: Locator;
  readonly name: Locator;
  readonly price: Locator;
  readonly addToCartButton: Locator;
  readonly viewDetailsButton: Locator;

  constructor(page: Page, card: Locator) {
    this.page = page;
    this.card = card;
    this.name = card.getByTestId('product-name');
    this.price = card.getByTestId('product-price');
    this.addToCartButton = card.getByRole('button', { name: 'Add to Cart' });
    this.viewDetailsButton = card.getByRole('link', { name: 'View Details' });
  }

  async getName(): Promise<string> {
    return await this.name.textContent() || '';
  }

  async getPrice(): Promise<string> {
    return await this.price.textContent() || '';
  }

  async addToCart() {
    await this.addToCartButton.click();
    // Wait for confirmation
    await this.page.getByText('Added to cart').waitFor({ state: 'visible' });
  }

  async viewDetails() {
    await this.viewDetailsButton.click();
  }
}

/**
 * CartPage - Shopping cart functionality
 */
export class CartPage extends BasePage {
  readonly navigation: NavigationComponent;
  readonly cartItems: Locator;
  readonly totalPrice: Locator;
  readonly checkoutButton: Locator;
  readonly emptyCartMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.navigation = new NavigationComponent(page);
    this.cartItems = page.getByTestId('cart-item');
    this.totalPrice = page.getByTestId('total-price');
    this.checkoutButton = page.getByRole('button', { name: 'Proceed to Checkout' });
    this.emptyCartMessage = page.getByText('Your cart is empty');
  }

  async goto() {
    await super.goto('/cart');
  }

  /**
   * Get cart item by product name
   */
  getCartItem(productName: string): CartItem {
    const item = this.cartItems.filter({ hasText: productName });
    return new CartItem(this.page, item);
  }

  /**
   * Get number of items in cart
   */
  async getItemCount(): Promise<number> {
    return await this.cartItems.count();
  }

  /**
   * Get total price
   */
  async getTotalPrice(): Promise<string> {
    return await this.totalPrice.textContent() || '';
  }

  /**
   * Proceed to checkout
   */
  async proceedToCheckout() {
    await this.checkoutButton.click();
  }

  /**
   * Check if cart is empty
   */
  async isEmpty(): Promise<boolean> {
    return await this.emptyCartMessage.isVisible();
  }
}

/**
 * CartItem - Helper class for cart item
 */
export class CartItem {
  readonly page: Page;
  readonly item: Locator;
  readonly name: Locator;
  readonly price: Locator;
  readonly quantity: Locator;
  readonly increaseButton: Locator;
  readonly decreaseButton: Locator;
  readonly removeButton: Locator;

  constructor(page: Page, item: Locator) {
    this.page = page;
    this.item = item;
    this.name = item.getByTestId('item-name');
    this.price = item.getByTestId('item-price');
    this.quantity = item.getByTestId('item-quantity');
    this.increaseButton = item.getByRole('button', { name: '+' });
    this.decreaseButton = item.getByRole('button', { name: '-' });
    this.removeButton = item.getByRole('button', { name: 'Remove' });
  }

  async getQuantity(): Promise<number> {
    const text = await this.quantity.textContent();
    return parseInt(text || '0', 10);
  }

  async increase() {
    await this.increaseButton.click();
  }

  async decrease() {
    await this.decreaseButton.click();
  }

  async remove() {
    await this.removeButton.click();
  }
}

/**
 * CheckoutPage - Checkout flow
 */
export class CheckoutPage extends BasePage {
  readonly shippingForm: Locator;
  readonly paymentForm: Locator;
  readonly placeOrderButton: Locator;
  readonly orderSummary: Locator;

  constructor(page: Page) {
    super(page);
    this.shippingForm = page.getByTestId('shipping-form');
    this.paymentForm = page.getByTestId('payment-form');
    this.placeOrderButton = page.getByRole('button', { name: 'Place Order' });
    this.orderSummary = page.getByTestId('order-summary');
  }

  async goto() {
    await super.goto('/checkout');
  }

  /**
   * Fill shipping information
   */
  async fillShippingInfo(data: {
    fullName: string;
    address: string;
    city: string;
    zipCode: string;
  }) {
    await this.page.getByLabel('Full Name').fill(data.fullName);
    await this.page.getByLabel('Address').fill(data.address);
    await this.page.getByLabel('City').fill(data.city);
    await this.page.getByLabel('ZIP Code').fill(data.zipCode);
  }

  /**
   * Fill payment information
   */
  async fillPaymentInfo(data: {
    cardNumber: string;
    expiry: string;
    cvv: string;
  }) {
    await this.page.getByLabel('Card Number').fill(data.cardNumber);
    await this.page.getByLabel('Expiry Date').fill(data.expiry);
    await this.page.getByLabel('CVV').fill(data.cvv);
  }

  /**
   * Complete checkout
   */
  async placeOrder() {
    await this.placeOrderButton.click();
  }
}

// ============================================================================
// TEST EXAMPLES USING PAGE OBJECTS
// ============================================================================

test.describe('E-commerce Flow with Page Objects', () => {
  test('complete user journey from signup to checkout', async ({ page }) => {
    // 1. Sign up
    const signupPage = new SignupPage(page);
    await signupPage.goto();
    await signupPage.signup({
      firstName: 'John',
      lastName: 'Doe',
      email: `john-${Date.now()}@example.com`,
      password: 'SecurePass123!',
    });

    // Verify redirect to products
    await expect(page).toHaveURL(/.*products/);

    // 2. Search and add products
    const productsPage = new ProductsPage(page);
    await productsPage.search('laptop');

    const laptop = productsPage.getProduct('Gaming Laptop');
    await laptop.addToCart();

    // 3. View cart
    await productsPage.navigation.navigateToCart();

    const cartPage = new CartPage(page);
    expect(await cartPage.getItemCount()).toBe(1);

    // 4. Proceed to checkout
    await cartPage.proceedToCheckout();

    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.fillShippingInfo({
      fullName: 'John Doe',
      address: '123 Main St',
      city: 'San Francisco',
      zipCode: '94102',
    });

    await checkoutPage.fillPaymentInfo({
      cardNumber: '4242 4242 4242 4242',
      expiry: '12/25',
      cvv: '123',
    });

    await checkoutPage.placeOrder();

    // Verify success
    await expect(page.getByText('Order confirmed')).toBeVisible();
  });

  test('login and browse products', async ({ page }) => {
    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');

    // Browse products
    const productsPage = new ProductsPage(page);
    await productsPage.filterByCategory('Electronics');
    await productsPage.sortBy('price-low-high');

    const productCount = await productsPage.getProductCount();
    expect(productCount).toBeGreaterThan(0);
  });

  test('fluent API example', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Fluent API allows chaining
    await loginPage
      .fillEmail('user@example.com')
      .then(p => p.fillPassword('password123'))
      .then(p => p.submit());

    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('component reusability', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');

    // Navigation component works on any page
    const productsPage = new ProductsPage(page);
    await productsPage.navigation.navigateToProducts();
    await productsPage.navigation.navigateToCart();
    await productsPage.navigation.logout();

    await expect(page).toHaveURL(/.*login/);
  });
});

// ============================================================================
// PAGE FACTORY PATTERN (Advanced)
// ============================================================================

/**
 * PageFactory provides centralized page object creation
 */
export class PageFactory {
  constructor(private page: Page) {}

  getLoginPage(): LoginPage {
    return new LoginPage(this.page);
  }

  getSignupPage(): SignupPage {
    return new SignupPage(this.page);
  }

  getProductsPage(): ProductsPage {
    return new ProductsPage(this.page);
  }

  getCartPage(): CartPage {
    return new CartPage(this.page);
  }

  getCheckoutPage(): CheckoutPage {
    return new CheckoutPage(this.page);
  }

  getNavigation(): NavigationComponent {
    return new NavigationComponent(this.page);
  }

  getModal(): ModalComponent {
    return new ModalComponent(this.page);
  }
}

// Usage example
test('using page factory', async ({ page }) => {
  const factory = new PageFactory(page);

  const loginPage = factory.getLoginPage();
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password');

  const productsPage = factory.getProductsPage();
  await productsPage.search('laptop');

  const navigation = factory.getNavigation();
  await navigation.navigateToCart();
});
