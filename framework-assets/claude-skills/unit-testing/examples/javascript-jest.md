# JavaScript (Jest) Unit Testing Examples

Comprehensive examples for unit testing in JavaScript using Jest framework.

## Basic Test Suite

```javascript
// calculator.test.js
import { Calculator } from './calculator';

describe('Calculator', () => {
    let calc;

    beforeEach(() => {
        calc = new Calculator();
    });

    afterEach(() => {
        // Cleanup if needed
    });

    describe('addition', () => {
        test('adds positive numbers', () => {
            expect(calc.add(2, 3)).toBe(5);
        });

        test('adds negative numbers', () => {
            expect(calc.add(-2, -3)).toBe(-5);
        });

        test('handles zero', () => {
            expect(calc.add(0, 5)).toBe(5);
            expect(calc.add(5, 0)).toBe(5);
        });
    });

    describe('division', () => {
        test('divides evenly', () => {
            expect(calc.divide(10, 2)).toBe(5);
        });

        test('returns float for uneven division', () => {
            expect(calc.divide(5, 2)).toBe(2.5);
        });

        test('throws error when dividing by zero', () => {
            expect(() => calc.divide(10, 0))
                .toThrow('Division by zero');
        });
    });
});
```

## Parametrized Tests with test.each

```javascript
// validator.test.js
import { EmailValidator } from './validator';

describe('EmailValidator', () => {
    const validator = new EmailValidator();

    describe('valid emails', () => {
        test.each([
            ['user@example.com'],
            ['first.last@example.com'],
            ['user+tag@example.co.uk'],
            ['test_user@test-domain.com']
        ])('accepts %s as valid', (email) => {
            expect(validator.isValid(email)).toBe(true);
        });
    });

    describe('invalid emails', () => {
        test.each([
            ['invalid'],
            ['@example.com'],
            ['user@'],
            ['user @example.com'],
            ['user@example'],
            ['']
        ])('rejects %s as invalid', (email) => {
            expect(validator.isValid(email)).toBe(false);
        });
    });

    describe('normalization', () => {
        test.each([
            ['test@EXAMPLE.COM', 'test@example.com'],
            ['  user@test.com  ', 'user@test.com'],
            ['Test@Example.Com', 'test@example.com']
        ])('normalizes %s to %s', (input, expected) => {
            expect(validator.normalize(input)).toBe(expected);
        });
    });
});
```

## Mocking Modules and Functions

```javascript
// userService.test.js
import { UserService } from './userService';
import { Database } from './database';
import { EmailService } from './emailService';

// Mock the modules
jest.mock('./database');
jest.mock('./emailService');

describe('UserService', () => {
    let userService;
    let mockDb;
    let mockEmailService;

    beforeEach(() => {
        // Clear all mocks before each test
        jest.clearAllMocks();

        // Create mock instances
        mockDb = {
            userExists: jest.fn(),
            saveUser: jest.fn(),
            findUser: jest.fn()
        };

        mockEmailService = {
            sendWelcome: jest.fn()
        };

        Database.mockImplementation(() => mockDb);
        EmailService.mockImplementation(() => mockEmailService);

        userService = new UserService();
    });

    describe('createUser', () => {
        test('saves user to database', async () => {
            // Arrange
            mockDb.userExists.mockResolvedValue(false);
            mockDb.saveUser.mockResolvedValue({
                id: 123,
                email: 'test@example.com'
            });

            // Act
            const user = await userService.createUser('test@example.com');

            // Assert
            expect(mockDb.saveUser).toHaveBeenCalledTimes(1);
            expect(user.email).toBe('test@example.com');
        });

        test('sends welcome email after creation', async () => {
            // Arrange
            mockDb.userExists.mockResolvedValue(false);
            mockDb.saveUser.mockResolvedValue({
                id: 123,
                email: 'test@example.com'
            });

            // Act
            await userService.createUser('test@example.com');

            // Assert
            expect(mockEmailService.sendWelcome).toHaveBeenCalledWith({
                email: 'test@example.com',
                userId: 123
            });
        });

        test('throws error if user already exists', async () => {
            // Arrange
            mockDb.userExists.mockResolvedValue(true);

            // Act & Assert
            await expect(
                userService.createUser('existing@example.com')
            ).rejects.toThrow('User already exists');

            expect(mockDb.saveUser).not.toHaveBeenCalled();
        });
    });
});
```

## Testing Async Code with Promises

```javascript
// asyncService.test.js
import { AsyncDataService } from './asyncService';

describe('AsyncDataService', () => {
    let service;

    beforeEach(() => {
        service = new AsyncDataService();
    });

    test('fetches data successfully', async () => {
        const result = await service.fetchData(123);

        expect(result).toHaveProperty('userId');
        expect(result.userId).toBe(123);
    });

    test('handles fetch errors', async () => {
        await expect(
            service.fetchData('invalid-id')
        ).rejects.toThrow('Invalid user ID');
    });

    test('resolves promise with correct data', () => {
        return service.fetchData(123).then(result => {
            expect(result.userId).toBe(123);
        });
    });

    test('can use resolves matcher', async () => {
        await expect(service.fetchData(123))
            .resolves.toHaveProperty('userId', 123);
    });

    test('can use rejects matcher', async () => {
        await expect(service.fetchData('invalid'))
            .rejects.toThrow('Invalid user ID');
    });

    test('multiple async operations', async () => {
        const results = await Promise.all([
            service.fetchData(1),
            service.fetchData(2),
            service.fetchData(3)
        ]);

        expect(results).toHaveLength(3);
        expect(results[0].userId).toBe(1);
    });
});
```

## Snapshot Testing

```javascript
// component.test.js
import { UserCard } from './UserCard';

describe('UserCard', () => {
    test('renders user information correctly', () => {
        const user = {
            id: 1,
            name: 'Alice Smith',
            email: 'alice@example.com',
            role: 'admin'
        };

        const card = new UserCard(user);
        const html = card.render();

        expect(html).toMatchSnapshot();
    });

    test('handles missing optional fields', () => {
        const user = {
            id: 2,
            name: 'Bob Jones'
            // email and role are optional
        };

        const card = new UserCard(user);
        const html = card.render();

        expect(html).toMatchSnapshot();
    });

    test('inline snapshot for small outputs', () => {
        const user = { id: 1, name: 'Test' };
        const card = new UserCard(user);

        expect(card.getTitle()).toMatchInlineSnapshot(`"User: Test"`);
    });
});
```

## Testing Timers and Delays

```javascript
// scheduler.test.js
import { Scheduler } from './scheduler';

describe('Scheduler', () => {
    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    test('executes callback after delay', () => {
        const callback = jest.fn();
        const scheduler = new Scheduler();

        scheduler.scheduleTask(callback, 1000);

        // Fast-forward time
        jest.advanceTimersByTime(999);
        expect(callback).not.toHaveBeenCalled();

        jest.advanceTimersByTime(1);
        expect(callback).toHaveBeenCalledTimes(1);
    });

    test('can cancel scheduled task', () => {
        const callback = jest.fn();
        const scheduler = new Scheduler();

        const taskId = scheduler.scheduleTask(callback, 1000);
        scheduler.cancelTask(taskId);

        jest.advanceTimersByTime(1000);
        expect(callback).not.toHaveBeenCalled();
    });

    test('repeats task at interval', () => {
        const callback = jest.fn();
        const scheduler = new Scheduler();

        scheduler.scheduleRepeating(callback, 500);

        jest.advanceTimersByTime(1500);
        expect(callback).toHaveBeenCalledTimes(3);
    });

    test('runs all timers', () => {
        const callback = jest.fn();
        const scheduler = new Scheduler();

        scheduler.scheduleTask(callback, 1000);
        scheduler.scheduleTask(callback, 2000);

        jest.runAllTimers();
        expect(callback).toHaveBeenCalledTimes(2);
    });
});
```

## Spies and Partial Mocks

```javascript
// logger.test.js
import { Logger } from './logger';
import * as utils from './utils';

describe('Logger', () => {
    test('spies on method calls', () => {
        const logger = new Logger();
        const logSpy = jest.spyOn(logger, 'log');

        logger.info('Test message');

        expect(logSpy).toHaveBeenCalledWith('INFO', 'Test message');
        logSpy.mockRestore();
    });

    test('partial mock of module', () => {
        // Mock only specific functions from module
        jest.spyOn(utils, 'formatDate').mockReturnValue('2024-01-15');

        const logger = new Logger();
        const message = logger.createTimestampedMessage('Test');

        expect(message).toContain('2024-01-15');
        expect(utils.formatDate).toHaveBeenCalled();
    });

    test('spy with implementation', () => {
        const logger = new Logger();
        const writeSpy = jest.spyOn(logger, 'write')
            .mockImplementation(() => 'mocked');

        const result = logger.write('data');

        expect(result).toBe('mocked');
        expect(writeSpy).toHaveBeenCalledWith('data');
    });
});
```

## Custom Matchers

```javascript
// custom-matchers.js
expect.extend({
    toHaveValidEmail(user) {
        const pass = user.email &&
                     user.email.includes('@') &&
                     user.email.includes('.');
        return {
            pass,
            message: () =>
                `expected ${user.email} to ${pass ? 'not ' : ''}be a valid email`
        };
    },

    toBeAdmin(user) {
        const pass = user.role === 'admin';
        return {
            pass,
            message: () =>
                `expected user to ${pass ? 'not ' : ''}be an admin`
        };
    },

    toBeWithinRange(received, floor, ceiling) {
        const pass = received >= floor && received <= ceiling;
        return {
            pass,
            message: () =>
                pass
                    ? `expected ${received} not to be within range ${floor} - ${ceiling}`
                    : `expected ${received} to be within range ${floor} - ${ceiling}`
        };
    }
});

// test file
test('user has valid email', () => {
    const user = new User('test@example.com');
    expect(user).toHaveValidEmail();
});

test('admin user has correct role', () => {
    const user = new User('admin@example.com', 'admin');
    expect(user).toBeAdmin();
});

test('score is within acceptable range', () => {
    const score = 75;
    expect(score).toBeWithinRange(0, 100);
});
```

## Testing Error Boundaries

```javascript
// errorHandler.test.js
import { ErrorHandler } from './errorHandler';

describe('ErrorHandler', () => {
    let handler;
    let consoleErrorSpy;

    beforeEach(() => {
        handler = new ErrorHandler();
        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore();
    });

    test('catches and logs errors', () => {
        const error = new Error('Test error');
        handler.handle(error);

        expect(consoleErrorSpy).toHaveBeenCalledWith(
            expect.stringContaining('Test error')
        );
    });

    test('calls error callback', () => {
        const callback = jest.fn();
        handler.onError(callback);

        const error = new Error('Test');
        handler.handle(error);

        expect(callback).toHaveBeenCalledWith(error);
    });

    test('does not throw when handling error', () => {
        expect(() => {
            handler.handle(new Error('Test'));
        }).not.toThrow();
    });
});
```

## Testing with Setup Files

```javascript
// jest.setup.js - Global test setup
import '@testing-library/jest-dom';

// Extend Jest with custom matchers
expect.extend({
    toHaveValidEmail(user) {
        // Custom matcher implementation
    }
});

// Mock global objects
global.fetch = jest.fn();

// Set up test environment
process.env.NODE_ENV = 'test';
```

## Data Builder Pattern

```javascript
// builders/userBuilder.js
export class UserBuilder {
    constructor() {
        this.email = 'test@example.com';
        this.role = 'user';
        this.name = 'Test User';
        this.verified = false;
    }

    withEmail(email) {
        this.email = email;
        return this;
    }

    withRole(role) {
        this.role = role;
        return this;
    }

    withName(name) {
        this.name = name;
        return this;
    }

    asVerified() {
        this.verified = true;
        return this;
    }

    asAdmin() {
        this.role = 'admin';
        return this;
    }

    build() {
        return {
            email: this.email,
            role: this.role,
            name: this.name,
            verified: this.verified
        };
    }
}

// Usage in tests
import { UserBuilder } from './builders/userBuilder';

test('admin users can delete', () => {
    const admin = new UserBuilder()
        .asAdmin()
        .asVerified()
        .build();

    expect(admin.role).toBe('admin');
    expect(canDelete(admin)).toBe(true);
});

test('unverified users cannot post', () => {
    const user = new UserBuilder().build();
    expect(canPost(user)).toBe(false);
});
```

## Testing DOM Manipulation

```javascript
// dom.test.js
import { createElement, updateElement } from './dom';

describe('DOM utilities', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
    });

    test('creates element with attributes', () => {
        const element = createElement('div', {
            id: 'test',
            class: 'container'
        });

        expect(element.tagName).toBe('DIV');
        expect(element.id).toBe('test');
        expect(element.className).toBe('container');
    });

    test('updates element content', () => {
        const div = document.createElement('div');
        document.body.appendChild(div);

        updateElement(div, { text: 'Updated' });

        expect(div.textContent).toBe('Updated');
    });

    test('appends child elements', () => {
        const parent = createElement('div');
        const child = createElement('span', { text: 'Child' });

        parent.appendChild(child);

        expect(parent.children.length).toBe(1);
        expect(parent.firstChild.textContent).toBe('Child');
    });
});
```

## Testing Event Handlers

```javascript
// eventHandler.test.js
import { ButtonHandler } from './buttonHandler';

describe('ButtonHandler', () => {
    let button;
    let handler;

    beforeEach(() => {
        button = document.createElement('button');
        document.body.appendChild(button);
        handler = new ButtonHandler(button);
    });

    afterEach(() => {
        document.body.innerHTML = '';
    });

    test('handles click events', () => {
        const callback = jest.fn();
        handler.onClick(callback);

        button.click();

        expect(callback).toHaveBeenCalledTimes(1);
    });

    test('removes event listener', () => {
        const callback = jest.fn();
        handler.onClick(callback);
        handler.removeClickHandler();

        button.click();

        expect(callback).not.toHaveBeenCalled();
    });

    test('passes event object to callback', () => {
        const callback = jest.fn();
        handler.onClick(callback);

        button.click();

        expect(callback).toHaveBeenCalledWith(
            expect.objectContaining({
                type: 'click',
                target: button
            })
        );
    });
});
```

## Best Practices Demonstrated

All JavaScript/Jest examples above demonstrate:

1. **Clear test structure** with describe blocks for organization
2. **Proper setup and teardown** using beforeEach/afterEach
3. **Descriptive test names** that explain the scenario
4. **AAA pattern** (Arrange, Act, Assert) in test bodies
5. **Appropriate mocking** of external dependencies
6. **Testing both success and error paths**
7. **Using parametrized tests** with test.each
8. **Async/await patterns** for asynchronous code
9. **Spy usage** for tracking function calls
10. **Clean, readable test code** with clear intentions
