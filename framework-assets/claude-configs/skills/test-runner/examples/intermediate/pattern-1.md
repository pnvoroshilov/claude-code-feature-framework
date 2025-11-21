# Pattern 1: Test Organization Architecture

## Problem Statement

As your codebase grows, test organization becomes crucial. Without a clear structure, tests become hard to find, maintain, and run selectively. You need a scalable test architecture that works for teams and large projects.

## Solution Overview

Implement a comprehensive test organization strategy with:
- Clear directory structure matching source code
- Shared test utilities and fixtures
- Consistent naming conventions
- Test categorization (unit, integration, e2e)
- Helper functions and custom matchers

## Implementation

### Directory Structure

```
project/
├── src/
│   ├── modules/
│   │   ├── users/
│   │   │   ├── UserService.ts
│   │   │   ├── UserController.ts
│   │   │   └── UserModel.ts
│   │   └── payments/
│   │       ├── PaymentService.ts
│   │       └── PaymentGateway.ts
│   └── utils/
│       └── validation.ts
├── tests/
│   ├── unit/
│   │   ├── modules/
│   │   │   ├── users/
│   │   │   │   ├── UserService.test.ts
│   │   │   │   └── UserController.test.ts
│   │   │   └── payments/
│   │   │       └── PaymentService.test.ts
│   │   └── utils/
│   │       └── validation.test.ts
│   ├── integration/
│   │   ├── api/
│   │   │   ├── users.integration.test.ts
│   │   │   └── payments.integration.test.ts
│   │   └── database/
│   │       └── migrations.integration.test.ts
│   ├── e2e/
│   │   ├── user-workflows.e2e.test.ts
│   │   └── checkout-flow.e2e.test.ts
│   ├── helpers/
│   │   ├── testDatabase.ts
│   │   ├── mockData.ts
│   │   └── customMatchers.ts
│   ├── fixtures/
│   │   ├── users.json
│   │   └── products.json
│   └── setup.ts
└── jest.config.js
```

### Shared Test Utilities

```typescript
// tests/helpers/testDatabase.ts
import { createConnection, Connection } from 'typeorm';

export async function createTestDatabase(): Promise<Connection> {
  return await createConnection({
    type: 'sqlite',
    database: ':memory:',
    entities: ['src/models/**/*.ts'],
    synchronize: true
  });
}

export async function clearDatabase(connection: Connection): Promise<void> {
  const entities = connection.entityMetadatas;

  for (const entity of entities) {
    const repository = connection.getRepository(entity.name);
    await repository.clear();
  }
}
```

```typescript
// tests/helpers/mockData.ts
export function createMockUser(overrides = {}) {
  return {
    id: Math.random().toString(36),
    name: 'Test User',
    email: 'test@example.com',
    age: 25,
    createdAt: new Date(),
    ...overrides
  };
}

export function createMockUsers(count: number) {
  return Array.from({ length: count }, (_, i) =>
    createMockUser({ name: `User ${i + 1}`, email: `user${i + 1}@example.com` })
  );
}
```

```typescript
// tests/helpers/customMatchers.ts
export const customMatchers = {
  toBeValidEmail(received: string) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const pass = emailRegex.test(received);

    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid email`
          : `expected ${received} to be a valid email`
    };
  },

  toBeWithinRange(received: number, min: number, max: number) {
    const pass = received >= min && received <= max;

    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be within range ${min}-${max}`
          : `expected ${received} to be within range ${min}-${max}`
    };
  }
};
```

### Test Suite with Shared Utilities

```typescript
// tests/unit/modules/users/UserService.test.ts
import { UserService } from '@/modules/users/UserService';
import { createTestDatabase, clearDatabase } from '@helpers/testDatabase';
import { createMockUser } from '@helpers/mockData';
import { customMatchers } from '@helpers/customMatchers';

expect.extend(customMatchers);

describe('UserService', () => {
  let database;
  let userService;

  beforeAll(async () => {
    database = await createTestDatabase();
    userService = new UserService(database);
  });

  beforeEach(async () => {
    await clearDatabase(database);
  });

  afterAll(async () => {
    await database.close();
  });

  describe('createUser', () => {
    test('should create user with valid data', async () => {
      const userData = createMockUser();

      const user = await userService.createUser(userData);

      expect(user.id).toBeDefined();
      expect(user.email).toBeValidEmail();
      expect(user.age).toBeWithinRange(0, 150);
    });
  });
});
```

### Configuration for Test Organization

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',

  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.{js,ts}',
    '**/*.{spec,test}.{js,ts}'
  ],

  // Module path aliases
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@helpers/(.*)$': '<rootDir>/tests/helpers/$1',
    '^@fixtures/(.*)$': '<rootDir>/tests/fixtures/$1'
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],

  // Coverage
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{js,ts}'
  ],

  // Test organization
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/tests/unit/**/*.test.{js,ts}']
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/tests/integration/**/*.test.{js,ts}']
    },
    {
      displayName: 'e2e',
      testMatch: ['<rootDir>/tests/e2e/**/*.test.{js,ts}'],
      testTimeout: 30000
    }
  ]
};
```

### Running Tests by Category

```bash
# Run all tests
npm test

# Run only unit tests
npm test -- --selectProjects unit

# Run only integration tests
npm test -- --selectProjects integration

# Run specific test file
npm test tests/unit/modules/users/UserService.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="createUser"

# Watch mode for unit tests
npm test -- --selectProjects unit --watch
```

## Benefits

1. **Scalability**: Structure grows with project
2. **Maintainability**: Easy to find and update tests
3. **Selective Execution**: Run only needed test categories
4. **Code Reuse**: Shared utilities reduce duplication
5. **Team Collaboration**: Consistent conventions

## See Also

- [Pattern 2: Advanced Coverage Strategies](pattern-2.md)
- [Best Practices: Test Organization](../../docs/best-practices.md#test-organization)
