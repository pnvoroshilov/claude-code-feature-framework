# TypeScript (Vitest) Unit Testing Examples

Comprehensive examples for unit testing in TypeScript using Vitest framework.

## Basic TypeScript Tests with Types

```typescript
// calculator.test.ts
import { describe, test, expect, beforeEach } from 'vitest';
import { Calculator } from './calculator';

describe('Calculator', () => {
    let calc: Calculator;

    beforeEach(() => {
        calc = new Calculator();
    });

    test('adds two numbers', () => {
        const result: number = calc.add(2, 3);
        expect(result).toBe(5);
    });

    test('subtracts two numbers', () => {
        const result: number = calc.subtract(10, 3);
        expect(result).toBe(7);
    });

    test('divides two numbers', () => {
        const result: number = calc.divide(10, 2);
        expect(result).toBe(5);
    });

    test('throws on division by zero', () => {
        expect(() => calc.divide(10, 0))
            .toThrowError('Division by zero');
    });
});
```

## Testing Generic Classes

```typescript
// repository.test.ts
import { describe, test, expect, beforeEach } from 'vitest';
import { Repository } from './repository';

interface User {
    id: number;
    name: string;
    email: string;
}

interface Product {
    id: number;
    title: string;
    price: number;
}

describe('Repository<T>', () => {
    let userRepo: Repository<User>;

    beforeEach(() => {
        userRepo = new Repository<User>();
    });

    test('stores and retrieves items', () => {
        const user: User = {
            id: 1,
            name: 'Alice',
            email: 'alice@example.com'
        };

        userRepo.save(user);
        const retrieved = userRepo.findById(1);

        expect(retrieved).toEqual(user);
    });

    test('returns undefined for missing items', () => {
        const result = userRepo.findById(999);
        expect(result).toBeUndefined();
    });

    test('filters items by predicate', () => {
        userRepo.save({ id: 1, name: 'Alice', email: 'alice@test.com' });
        userRepo.save({ id: 2, name: 'Bob', email: 'bob@test.com' });

        const filtered = userRepo.filter((user) =>
            user.email.includes('alice')
        );

        expect(filtered).toHaveLength(1);
        expect(filtered[0].name).toBe('Alice');
    });

    test('works with different types', () => {
        const productRepo = new Repository<Product>();
        const product: Product = {
            id: 1,
            title: 'Laptop',
            price: 999.99
        };

        productRepo.save(product);
        const retrieved = productRepo.findById(1);

        expect(retrieved?.price).toBe(999.99);
    });
});
```

## Mocking with Vitest

```typescript
// userService.test.ts
import { describe, test, expect, vi, beforeEach, type Mock } from 'vitest';
import { UserService } from './userService';
import type { Database } from './database';
import type { EmailService } from './emailService';
import type { User } from './types';

// Create typed mock objects
const createMockDb = (): Database => ({
    userExists: vi.fn(),
    saveUser: vi.fn(),
    findUser: vi.fn(),
    deleteUser: vi.fn()
});

const createMockEmailService = (): EmailService => ({
    sendWelcome: vi.fn(),
    sendPasswordReset: vi.fn()
});

describe('UserService', () => {
    let userService: UserService;
    let mockDb: Database;
    let mockEmailService: EmailService;

    beforeEach(() => {
        mockDb = createMockDb();
        mockEmailService = createMockEmailService();
        userService = new UserService(mockDb, mockEmailService);
    });

    test('creates user and sends email', async () => {
        // Arrange
        const mockUser: User = {
            id: 123,
            email: 'test@example.com',
            name: 'Test User'
        };

        vi.mocked(mockDb.userExists).mockResolvedValue(false);
        vi.mocked(mockDb.saveUser).mockResolvedValue(mockUser);

        // Act
        const user = await userService.createUser('test@example.com');

        // Assert
        expect(mockDb.saveUser).toHaveBeenCalledOnce();
        expect(mockEmailService.sendWelcome).toHaveBeenCalledWith({
            email: 'test@example.com',
            userId: 123
        });
    });

    test('throws error if user exists', async () => {
        // Arrange
        vi.mocked(mockDb.userExists).mockResolvedValue(true);

        // Act & Assert
        await expect(
            userService.createUser('existing@example.com')
        ).rejects.toThrow('User already exists');

        expect(mockDb.saveUser).not.toHaveBeenCalled();
    });
});
```

## Testing Async/Await with Types

```typescript
// asyncService.test.ts
import { describe, test, expect } from 'vitest';
import { AsyncDataService } from './asyncService';
import type { UserData } from './types';

describe('AsyncDataService', () => {
    let service: AsyncDataService;

    beforeEach(() => {
        service = new AsyncDataService();
    });

    test('fetches user data', async () => {
        const result: UserData = await service.fetchUser(123);

        expect(result).toHaveProperty('userId');
        expect(result.userId).toBe(123);
    });

    test('handles fetch errors', async () => {
        await expect(
            service.fetchUser(-1)
        ).rejects.toThrow('Invalid user ID');
    });

    test('fetches multiple users', async () => {
        const userIds = [1, 2, 3];
        const results: UserData[] = await Promise.all(
            userIds.map(id => service.fetchUser(id))
        );

        expect(results).toHaveLength(3);
        expect(results[0].userId).toBe(1);
    });

    test('uses resolves matcher', async () => {
        await expect(service.fetchUser(123))
            .resolves.toMatchObject({ userId: 123 });
    });
});
```

## Testing Classes with Inheritance

```typescript
// shape.test.ts
import { describe, test, expect } from 'vitest';
import { Shape, Circle, Rectangle } from './shapes';

describe('Shape hierarchy', () => {
    describe('Circle', () => {
        test('calculates area correctly', () => {
            const circle = new Circle(5);
            expect(circle.area()).toBeCloseTo(78.54, 2);
        });

        test('calculates circumference correctly', () => {
            const circle = new Circle(5);
            expect(circle.circumference()).toBeCloseTo(31.42, 2);
        });

        test('extends Shape base class', () => {
            const circle = new Circle(5);
            expect(circle).toBeInstanceOf(Shape);
            expect(circle).toBeInstanceOf(Circle);
        });
    });

    describe('Rectangle', () => {
        test('calculates area correctly', () => {
            const rect = new Rectangle(4, 5);
            expect(rect.area()).toBe(20);
        });

        test('calculates perimeter correctly', () => {
            const rect = new Rectangle(4, 5);
            expect(rect.perimeter()).toBe(18);
        });

        test('validates dimensions', () => {
            expect(() => new Rectangle(-1, 5))
                .toThrow('Dimensions must be positive');
        });
    });
});
```

## Testing with Type Guards

```typescript
// typeGuards.test.ts
import { describe, test, expect } from 'vitest';
import { isUser, isAdmin, type User, type Admin } from './types';

describe('Type Guards', () => {
    test('identifies user objects', () => {
        const user = { id: 1, name: 'Alice', role: 'user' };
        expect(isUser(user)).toBe(true);
    });

    test('rejects non-user objects', () => {
        const notUser = { id: 1, name: 'Alice' }; // Missing role
        expect(isUser(notUser)).toBe(false);
    });

    test('identifies admin objects', () => {
        const admin = {
            id: 1,
            name: 'Admin',
            role: 'admin',
            permissions: ['read', 'write']
        };
        expect(isAdmin(admin)).toBe(true);
    });

    test('uses type narrowing in tests', () => {
        const user: User | Admin = {
            id: 1,
            name: 'Test',
            role: 'admin',
            permissions: ['read']
        };

        if (isAdmin(user)) {
            // TypeScript knows user is Admin here
            expect(user.permissions).toContain('read');
        }
    });
});
```

## Testing Enums and Unions

```typescript
// status.test.ts
import { describe, test, expect } from 'vitest';
import { TaskStatus, isValidTransition } from './taskStatus';

enum TaskStatus {
    TODO = 'TODO',
    IN_PROGRESS = 'IN_PROGRESS',
    DONE = 'DONE',
    CANCELLED = 'CANCELLED'
}

describe('TaskStatus', () => {
    test('validates status transitions', () => {
        expect(isValidTransition(TaskStatus.TODO, TaskStatus.IN_PROGRESS))
            .toBe(true);

        expect(isValidTransition(TaskStatus.TODO, TaskStatus.DONE))
            .toBe(false);

        expect(isValidTransition(TaskStatus.DONE, TaskStatus.TODO))
            .toBe(false);
    });

    test('enum values are strings', () => {
        expect(TaskStatus.TODO).toBe('TODO');
        expect(typeof TaskStatus.DONE).toBe('string');
    });
});

// Union types
type Result<T> =
    | { success: true; data: T }
    | { success: false; error: string };

describe('Result type', () => {
    test('handles success case', () => {
        const result: Result<number> = {
            success: true,
            data: 42
        };

        expect(result.success).toBe(true);
        if (result.success) {
            expect(result.data).toBe(42);
        }
    });

    test('handles error case', () => {
        const result: Result<number> = {
            success: false,
            error: 'Something went wrong'
        };

        expect(result.success).toBe(false);
        if (!result.success) {
            expect(result.error).toBe('Something went wrong');
        }
    });
});
```

## Testing with Interfaces

```typescript
// interfaces.test.ts
import { describe, test, expect } from 'vitest';

interface PaymentProcessor {
    processPayment(amount: number): Promise<PaymentResult>;
    refund(transactionId: string): Promise<void>;
}

interface PaymentResult {
    transactionId: string;
    status: 'success' | 'failed';
    amount: number;
}

class MockPaymentProcessor implements PaymentProcessor {
    async processPayment(amount: number): Promise<PaymentResult> {
        return {
            transactionId: 'mock-123',
            status: 'success',
            amount
        };
    }

    async refund(transactionId: string): Promise<void> {
        // Mock implementation
    }
}

describe('PaymentProcessor interface', () => {
    let processor: PaymentProcessor;

    beforeEach(() => {
        processor = new MockPaymentProcessor();
    });

    test('processes payment', async () => {
        const result = await processor.processPayment(100);

        expect(result).toMatchObject({
            transactionId: expect.any(String),
            status: 'success',
            amount: 100
        });
    });

    test('refund does not throw', async () => {
        await expect(
            processor.refund('txn-123')
        ).resolves.not.toThrow();
    });
});
```

## Parametrized Tests with Type Safety

```typescript
// parametrized.test.ts
import { describe, test, expect } from 'vitest';
import { calculateDiscount } from './pricing';

interface DiscountTestCase {
    price: number;
    percentage: number;
    expected: number;
}

describe('calculateDiscount', () => {
    const testCases: DiscountTestCase[] = [
        { price: 100, percentage: 10, expected: 90 },
        { price: 50, percentage: 20, expected: 40 },
        { price: 200, percentage: 50, expected: 100 },
        { price: 0, percentage: 10, expected: 0 }
    ];

    test.each(testCases)(
        'discounts $price by $percentage% to get $expected',
        ({ price, percentage, expected }) => {
            const result = calculateDiscount(price, percentage);
            expect(result).toBe(expected);
        }
    );
});
```

## Testing Decorators

```typescript
// decorators.test.ts
import { describe, test, expect, vi } from 'vitest';

function Log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = function (...args: any[]) {
        console.log(`Calling ${propertyKey} with`, args);
        return originalMethod.apply(this, args);
    };

    return descriptor;
}

class Calculator {
    @Log
    add(a: number, b: number): number {
        return a + b;
    }
}

describe('Log decorator', () => {
    test('logs method calls', () => {
        const consoleSpy = vi.spyOn(console, 'log');
        const calc = new Calculator();

        calc.add(2, 3);

        expect(consoleSpy).toHaveBeenCalledWith(
            'Calling add with',
            [2, 3]
        );

        consoleSpy.mockRestore();
    });

    test('returns correct result', () => {
        const calc = new Calculator();
        expect(calc.add(2, 3)).toBe(5);
    });
});
```

## Testing with Branded Types

```typescript
// brandedTypes.test.ts
import { describe, test, expect } from 'vitest';

// Branded types for type safety
type UserId = string & { readonly brand: unique symbol };
type Email = string & { readonly brand: unique symbol };

function createUserId(id: string): UserId {
    if (!id || id.length === 0) {
        throw new Error('Invalid user ID');
    }
    return id as UserId;
}

function createEmail(email: string): Email {
    if (!email.includes('@')) {
        throw new Error('Invalid email');
    }
    return email as Email;
}

describe('Branded types', () => {
    test('creates valid UserId', () => {
        const userId = createUserId('user-123');
        expect(userId).toBe('user-123');
    });

    test('rejects invalid UserId', () => {
        expect(() => createUserId('')).toThrow('Invalid user ID');
    });

    test('creates valid Email', () => {
        const email = createEmail('test@example.com');
        expect(email).toBe('test@example.com');
    });

    test('prevents type confusion at compile time', () => {
        const userId = createUserId('user-123');
        const email = createEmail('test@example.com');

        // These would cause TypeScript compile errors:
        // const mixed1: Email = userId;  // Type error
        // const mixed2: UserId = email;  // Type error

        // Runtime tests still work
        expect(userId).not.toBe(email);
    });
});
```

## Testing Builder Pattern with Types

```typescript
// builder.test.ts
import { describe, test, expect } from 'vitest';

interface User {
    id: number;
    email: string;
    name: string;
    role: 'user' | 'admin';
    verified: boolean;
}

class UserBuilder {
    private id: number = 0;
    private email: string = 'test@example.com';
    private name: string = 'Test User';
    private role: 'user' | 'admin' = 'user';
    private verified: boolean = false;

    withId(id: number): this {
        this.id = id;
        return this;
    }

    withEmail(email: string): this {
        this.email = email;
        return this;
    }

    withName(name: string): this {
        this.name = name;
        return this;
    }

    asAdmin(): this {
        this.role = 'admin';
        return this;
    }

    asVerified(): this {
        this.verified = true;
        return this;
    }

    build(): User {
        return {
            id: this.id,
            email: this.email,
            name: this.name,
            role: this.role,
            verified: this.verified
        };
    }
}

describe('UserBuilder', () => {
    test('builds user with defaults', () => {
        const user = new UserBuilder().build();

        expect(user).toMatchObject({
            id: 0,
            email: 'test@example.com',
            role: 'user',
            verified: false
        });
    });

    test('builds admin user', () => {
        const admin = new UserBuilder()
            .withId(1)
            .withEmail('admin@example.com')
            .asAdmin()
            .asVerified()
            .build();

        expect(admin.role).toBe('admin');
        expect(admin.verified).toBe(true);
    });

    test('method chaining preserves type', () => {
        const builder = new UserBuilder();
        const chainedBuilder = builder.withId(1).withName('Alice');

        // TypeScript ensures chainedBuilder is still UserBuilder
        expect(chainedBuilder).toBeInstanceOf(UserBuilder);
    });
});
```

## Testing with Utility Types

```typescript
// utilityTypes.test.ts
import { describe, test, expect } from 'vitest';

interface User {
    id: number;
    email: string;
    name: string;
    password: string;
}

// Pick - select specific properties
type UserProfile = Pick<User, 'id' | 'email' | 'name'>;

// Omit - exclude specific properties
type UserWithoutPassword = Omit<User, 'password'>;

// Partial - make all properties optional
type UserUpdate = Partial<User>;

// Required - make all properties required
type RequiredUser = Required<User>;

describe('Utility types', () => {
    test('Pick creates subset type', () => {
        const profile: UserProfile = {
            id: 1,
            email: 'test@example.com',
            name: 'Test'
            // password not allowed here
        };

        expect(profile).not.toHaveProperty('password');
    });

    test('Omit excludes properties', () => {
        const user: UserWithoutPassword = {
            id: 1,
            email: 'test@example.com',
            name: 'Test'
        };

        expect(user).not.toHaveProperty('password');
    });

    test('Partial allows optional properties', () => {
        const update: UserUpdate = {
            name: 'New Name'
            // All other properties are optional
        };

        expect(update.name).toBe('New Name');
        expect(update.email).toBeUndefined();
    });
});
```

## Best Practices Demonstrated

All TypeScript/Vitest examples above demonstrate:

1. **Full type safety** with proper TypeScript types
2. **Generic testing** for reusable components
3. **Interface-based testing** for loose coupling
4. **Type guards** for runtime type checking
5. **Branded types** for domain-specific validation
6. **Utility types** for type transformations
7. **Proper async/await** patterns with types
8. **Builder pattern** with fluent interfaces
9. **Enum testing** for state management
10. **Union types** for type-safe error handling
