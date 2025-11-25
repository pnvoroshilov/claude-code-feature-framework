// jest.config.js - Place in project root
module.exports = {
  // Test environment
  testEnvironment: 'node',

  // Test file patterns
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.test.ts',
    '**/__tests__/**/*.js',
    '**/__tests__/**/*.ts'
  ],

  // Files to ignore
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/'
  ],

  // Coverage configuration
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{js,ts}',
    '!src/tests/**'
  ],

  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],

  coverageThresholds: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],

  // Module path mappings
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@tests/(.*)$': '<rootDir>/tests/$1'
  },

  // Transform configuration (for TypeScript)
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },

  // Timeout settings
  testTimeout: 30000,

  // Parallel execution
  maxWorkers: '50%',

  // Verbose output
  verbose: true,

  // Clear mocks between tests
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true
};

// tests/setup.js - Global test setup
const { GenericContainer } = require('testcontainers');
const { Sequelize } = require('sequelize');
const Redis = require('ioredis');

// Global containers
let postgresContainer;
let redisContainer;
let sequelize;
let redisClient;

// ============================================================================
// Global Setup (Runs Once Before All Tests)
// ============================================================================

beforeAll(async () => {
  // Start PostgreSQL container
  postgresContainer = await new GenericContainer('postgres:15-alpine')
    .withExposedPorts(5432)
    .withEnvironment({
      POSTGRES_USER: 'test',
      POSTGRES_PASSWORD: 'test',
      POSTGRES_DB: 'test'
    })
    .withTmpFs({ '/var/lib/postgresql/data': 'rw' })
    .start();

  const pgPort = postgresContainer.getMappedPort(5432);

  // Initialize Sequelize
  sequelize = new Sequelize({
    dialect: 'postgres',
    host: 'localhost',
    port: pgPort,
    username: 'test',
    password: 'test',
    database: 'test',
    logging: false
  });

  await sequelize.authenticate();

  // Start Redis container
  redisContainer = await new GenericContainer('redis:7-alpine')
    .withExposedPorts(6379)
    .start();

  const redisPort = redisContainer.getMappedPort(6379);

  // Initialize Redis client
  redisClient = new Redis({
    host: 'localhost',
    port: redisPort
  });

  // Store in global for test access
  global.testContainers = {
    postgres: postgresContainer,
    redis: redisContainer
  };

  global.testClients = {
    sequelize,
    redis: redisClient
  };

  console.log('Test containers started successfully');
}, 60000);

// ============================================================================
// Global Teardown (Runs Once After All Tests)
// ============================================================================

afterAll(async () => {
  // Close database connection
  if (sequelize) {
    await sequelize.close();
  }

  // Close Redis connection
  if (redisClient) {
    redisClient.disconnect();
  }

  // Stop containers
  if (postgresContainer) {
    await postgresContainer.stop();
  }

  if (redisContainer) {
    await redisContainer.stop();
  }

  console.log('Test containers stopped successfully');
}, 60000);

// ============================================================================
// Per-Test Setup
// ============================================================================

beforeEach(async () => {
  // Sync database schema (creates tables if needed)
  await sequelize.sync({ force: true });

  // Clear Redis data
  await redisClient.flushdb();
});

afterEach(async () => {
  // Truncate all tables
  if (sequelize) {
    await sequelize.truncate({ cascade: true, restartIdentity: true });
  }
});

// ============================================================================
// Test Utilities
// ============================================================================

// Make utilities available globally
global.testUtils = {
  // Create test user
  createTestUser: async (overrides = {}) => {
    const { faker } = require('@faker-js/faker');
    const { User } = require('../src/models');

    return await User.create({
      name: faker.person.fullName(),
      email: faker.internet.email(),
      password: 'test_password',
      ...overrides
    });
  },

  // Create test post
  createTestPost: async (userId, overrides = {}) => {
    const { faker } = require('@faker-js/faker');
    const { Post } = require('../src/models');

    return await Post.create({
      title: faker.lorem.sentence(),
      content: faker.lorem.paragraphs(2),
      userId,
      ...overrides
    });
  },

  // Generate JWT token
  generateToken: (payload = {}) => {
    const jwt = require('jsonwebtoken');
    const defaultPayload = {
      userId: 'test_user_123',
      exp: Math.floor(Date.now() / 1000) + 3600
    };

    return jwt.sign(
      { ...defaultPayload, ...payload },
      process.env.JWT_SECRET || 'test_secret'
    );
  },

  // Wait for condition
  waitFor: async (condition, timeout = 5000) => {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      if (await condition()) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Timeout waiting for condition');
  }
};

// ============================================================================
// Environment Variables
// ============================================================================

process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test_secret_key';
process.env.LOG_LEVEL = 'error';

// tests/helpers/factories.js - Test Data Factories
const { faker } = require('@faker-js/faker');

/**
 * Factory for creating test users
 */
class UserFactory {
  constructor(sequelize) {
    this.User = sequelize.models.User;
  }

  /**
   * Create a single user
   */
  async create(overrides = {}) {
    return await this.User.create({
      name: faker.person.fullName(),
      email: faker.internet.email(),
      password: 'password123',
      role: 'user',
      ...overrides
    });
  }

  /**
   * Create multiple users
   */
  async createBatch(count, overrides = {}) {
    const promises = Array(count)
      .fill(null)
      .map(() => this.create(overrides));

    return await Promise.all(promises);
  }

  /**
   * Create admin user
   */
  async createAdmin(overrides = {}) {
    return await this.create({
      role: 'admin',
      ...overrides
    });
  }
}

/**
 * Factory for creating test posts
 */
class PostFactory {
  constructor(sequelize) {
    this.Post = sequelize.models.Post;
  }

  /**
   * Create a single post
   */
  async create(overrides = {}) {
    // Create user if not provided
    if (!overrides.userId) {
      const userFactory = new UserFactory(
        this.Post.sequelize
      );
      const user = await userFactory.create();
      overrides.userId = user.id;
    }

    return await this.Post.create({
      title: faker.lorem.sentence(),
      content: faker.lorem.paragraphs(3),
      status: 'published',
      ...overrides
    });
  }

  /**
   * Create multiple posts
   */
  async createBatch(count, overrides = {}) {
    const promises = Array(count)
      .fill(null)
      .map(() => this.create(overrides));

    return await Promise.all(promises);
  }

  /**
   * Create draft post
   */
  async createDraft(overrides = {}) {
    return await this.create({
      status: 'draft',
      ...overrides
    });
  }
}

/**
 * Factory manager - provides easy access to all factories
 */
class FactoryManager {
  constructor(sequelize) {
    this.sequelize = sequelize;
    this.users = new UserFactory(sequelize);
    this.posts = new PostFactory(sequelize);
  }

  /**
   * Reset all factories
   */
  async reset() {
    await this.sequelize.truncate({ cascade: true });
  }
}

module.exports = {
  UserFactory,
  PostFactory,
  FactoryManager
};

// tests/helpers/assertions.js - Custom Jest Matchers
expect.extend({
  /**
   * Check if response has valid pagination metadata
   */
  toHaveValidPagination(received) {
    const pass = (
      received &&
      typeof received.page === 'number' &&
      typeof received.pageSize === 'number' &&
      typeof received.total === 'number' &&
      Array.isArray(received.data)
    );

    return {
      pass,
      message: () =>
        pass
          ? `Expected response not to have valid pagination`
          : `Expected response to have valid pagination with page, pageSize, total, and data fields`
    };
  },

  /**
   * Check if response has error format
   */
  toHaveErrorFormat(received) {
    const pass = (
      received &&
      typeof received.error === 'string' &&
      (received.statusCode === undefined ||
        typeof received.statusCode === 'number')
    );

    return {
      pass,
      message: () =>
        pass
          ? `Expected response not to have error format`
          : `Expected response to have error format with error message`
    };
  },

  /**
   * Check if date is recent (within last N seconds)
   */
  toBeRecent(received, seconds = 10) {
    const date = new Date(received);
    const now = new Date();
    const diff = (now - date) / 1000;
    const pass = diff >= 0 && diff <= seconds;

    return {
      pass,
      message: () =>
        pass
          ? `Expected date not to be within last ${seconds} seconds`
          : `Expected date to be within last ${seconds} seconds, but was ${diff.toFixed(1)}s ago`
    };
  }
});

// tests/helpers/mocks.js - Common Mock Helpers
const nock = require('nock');

/**
 * Mock external API service
 */
function mockExternalAPI() {
  return {
    /**
     * Mock successful user fetch
     */
    mockGetUser: (userId, userData = {}) => {
      nock('https://api.external.com')
        .get(`/users/${userId}`)
        .reply(200, {
          id: userId,
          name: 'External User',
          status: 'active',
          ...userData
        });
    },

    /**
     * Mock failed request
     */
    mockError: (path, statusCode = 500) => {
      nock('https://api.external.com')
        .get(path)
        .reply(statusCode, { error: 'Service error' });
    },

    /**
     * Mock with delay
     */
    mockWithDelay: (path, delay = 1000) => {
      nock('https://api.external.com')
        .get(path)
        .delay(delay)
        .reply(200, { status: 'ok' });
    },

    /**
     * Clean all mocks
     */
    cleanAll: () => {
      nock.cleanAll();
    }
  };
}

module.exports = {
  mockExternalAPI
};

// Example test file using setup
// tests/integration/users.test.js
const request = require('supertest');
const app = require('../../src/app');
const { FactoryManager } = require('../helpers/factories');

describe('User API Integration Tests', () => {
  let factories;

  beforeEach(() => {
    factories = new FactoryManager(global.testClients.sequelize);
  });

  describe('GET /users', () => {
    test('returns paginated users', async () => {
      // Create test data
      await factories.users.createBatch(15);

      const response = await request(app)
        .get('/users?page=1&pageSize=10')
        .expect(200);

      expect(response.body).toHaveValidPagination();
      expect(response.body.data).toHaveLength(10);
      expect(response.body.total).toBe(15);
    });

    test('filters users by role', async () => {
      await factories.users.create({ role: 'admin' });
      await factories.users.createBatch(5, { role: 'user' });

      const response = await request(app)
        .get('/users?role=admin')
        .expect(200);

      expect(response.body.data).toHaveLength(1);
      expect(response.body.data[0].role).toBe('admin');
    });
  });

  describe('POST /users', () => {
    test('creates new user', async () => {
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };

      const response = await request(app)
        .post('/users')
        .send(userData)
        .expect(201);

      expect(response.body.id).toBeDefined();
      expect(response.body.name).toBe(userData.name);
      expect(response.body.createdAt).toBeRecent();
    });
  });
});
