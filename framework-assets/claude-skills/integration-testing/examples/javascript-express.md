# JavaScript/Node.js Express Integration Testing Examples

Complete examples demonstrating integration testing patterns for Express.js applications.

## Basic Express Application

```javascript
// app.js
const express = require('express');
const { Sequelize } = require('sequelize');

const app = express();
app.use(express.json());

// Database models
const User = sequelize.define('User', {
  name: {
    type: Sequelize.STRING,
    allowNull: false
  },
  email: {
    type: Sequelize.STRING,
    allowNull: false,
    unique: true
  }
});

// Routes
app.post('/users', async (req, res) => {
  try {
    const user = await User.create(req.body);
    res.status(201).json(user);
  } catch (error) {
    if (error.name === 'SequelizeUniqueConstraintError') {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: error.message });
  }
});

app.get('/users/:id', async (req, res) => {
  const user = await User.findByPk(req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

module.exports = app;
```

## Test Configuration

```javascript
// tests/setup.js
const { GenericContainer } = require('testcontainers');
const { Sequelize } = require('sequelize');

let postgresContainer;
let sequelize;

// Start container before all tests
beforeAll(async () => {
  postgresContainer = await new GenericContainer('postgres:15-alpine')
    .withExposedPorts(5432)
    .withEnvironment({
      POSTGRES_USER: 'test',
      POSTGRES_PASSWORD: 'test',
      POSTGRES_DB: 'test'
    })
    .withTmpFs({ '/var/lib/postgresql/data': 'rw' })  // In-memory for speed
    .start();

  const port = postgresContainer.getMappedPort(5432);

  sequelize = new Sequelize({
    dialect: 'postgres',
    host: 'localhost',
    port,
    username: 'test',
    password: 'test',
    database: 'test',
    logging: false
  });

  await sequelize.authenticate();
  await sequelize.sync({ force: true });
}, 30000);

// Stop container after all tests
afterAll(async () => {
  await sequelize.close();
  await postgresContainer.stop();
});

// Clean up between tests
afterEach(async () => {
  await sequelize.truncate({ cascade: true });
});

module.exports = { sequelize };
```

## API Integration Tests with Supertest

```javascript
// tests/integration/users.test.js
const request = require('supertest');
const app = require('../../app');

describe('User API Integration Tests', () => {
  describe('POST /users', () => {
    test('creates a new user successfully', async () => {
      const response = await request(app)
        .post('/users')
        .send({
          name: 'Alice',
          email: 'alice@example.com'
        })
        .expect('Content-Type', /json/)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe('Alice');
      expect(response.body.email).toBe('alice@example.com');
    });

    test('returns 400 for duplicate email', async () => {
      // Create first user
      await request(app)
        .post('/users')
        .send({
          name: 'Bob',
          email: 'bob@example.com'
        });

      // Try duplicate
      const response = await request(app)
        .post('/users')
        .send({
          name: 'Bob2',
          email: 'bob@example.com'
        })
        .expect(400);

      expect(response.body.error).toContain('already exists');
    });

    test('validates required fields', async () => {
      const response = await request(app)
        .post('/users')
        .send({
          name: 'Charlie'
          // Missing email
        })
        .expect(400);

      expect(response.body.error).toBeDefined();
    });
  });

  describe('GET /users/:id', () => {
    test('retrieves existing user', async () => {
      // Create user first
      const createResponse = await request(app)
        .post('/users')
        .send({
          name: 'David',
          email: 'david@example.com'
        });

      const userId = createResponse.body.id;

      // Retrieve user
      const response = await request(app)
        .get(`/users/${userId}`)
        .expect(200);

      expect(response.body.name).toBe('David');
      expect(response.body.id).toBe(userId);
    });

    test('returns 404 for non-existent user', async () => {
      const response = await request(app)
        .get('/users/99999')
        .expect(404);

      expect(response.body.error).toBe('User not found');
    });
  });
});
```

## Database Integration Tests

```javascript
// tests/integration/database.test.js
const { User, Post } = require('../../models');
const { sequelize } = require('../setup');

describe('Database Integration Tests', () => {
  describe('User CRUD Operations', () => {
    test('creates and retrieves user', async () => {
      const user = await User.create({
        name: 'TestUser',
        email: 'test@example.com'
      });

      expect(user.id).toBeDefined();

      const retrieved = await User.findByPk(user.id);
      expect(retrieved.name).toBe('TestUser');
    });

    test('updates user', async () => {
      const user = await User.create({
        name: 'Original',
        email: 'original@example.com'
      });

      await user.update({ name: 'Updated' });
      await user.reload();

      expect(user.name).toBe('Updated');
    });

    test('deletes user', async () => {
      const user = await User.create({
        name: 'ToDelete',
        email: 'delete@example.com'
      });

      await user.destroy();

      const deleted = await User.findByPk(user.id);
      expect(deleted).toBeNull();
    });
  });

  describe('Relationships', () => {
    test('creates user with posts', async () => {
      const user = await User.create({
        name: 'Author',
        email: 'author@example.com'
      });

      const post = await Post.create({
        title: 'Test Post',
        content: 'Content here',
        userId: user.id
      });

      const userWithPosts = await User.findByPk(user.id, {
        include: [Post]
      });

      expect(userWithPosts.Posts).toHaveLength(1);
      expect(userWithPosts.Posts[0].title).toBe('Test Post');
    });

    test('cascade delete removes related posts', async () => {
      const user = await User.create({
        name: 'Author',
        email: 'author@example.com'
      });

      await Post.create({
        title: 'Post 1',
        content: 'Content',
        userId: user.id
      });

      await user.destroy();

      const posts = await Post.findAll({ where: { userId: user.id } });
      expect(posts).toHaveLength(0);
    });
  });

  describe('Transactions', () => {
    test('commits successful transaction', async () => {
      const transaction = await sequelize.transaction();

      try {
        const user = await User.create({
          name: 'TransactionUser',
          email: 'transaction@example.com'
        }, { transaction });

        await transaction.commit();

        const found = await User.findOne({
          where: { email: 'transaction@example.com' }
        });
        expect(found).not.toBeNull();
      } catch (error) {
        await transaction.rollback();
        throw error;
      }
    });

    test('rolls back failed transaction', async () => {
      const transaction = await sequelize.transaction();

      try {
        await User.create({
          name: 'User1',
          email: 'rollback@example.com'
        }, { transaction });

        // Simulate error
        throw new Error('Simulated error');

        await transaction.commit();
      } catch (error) {
        await transaction.rollback();
      }

      const found = await User.findOne({
        where: { email: 'rollback@example.com' }
      });
      expect(found).toBeNull();
    });
  });
});
```

## Authentication Integration Tests

```javascript
// tests/integration/auth.test.js
const request = require('supertest');
const jwt = require('jsonwebtoken');
const app = require('../../app');
const { User } = require('../../models');
const bcrypt = require('bcrypt');

describe('Authentication Integration Tests', () => {
  let testUser;

  beforeEach(async () => {
    const hashedPassword = await bcrypt.hash('password123', 10);
    testUser = await User.create({
      name: 'AuthUser',
      email: 'auth@example.com',
      password: hashedPassword
    });
  });

  describe('POST /auth/login', () => {
    test('logs in with valid credentials', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          email: 'auth@example.com',
          password: 'password123'
        })
        .expect(200);

      expect(response.body.accessToken).toBeDefined();
      expect(response.body.refreshToken).toBeDefined();

      // Verify token is valid
      const decoded = jwt.verify(
        response.body.accessToken,
        process.env.JWT_SECRET || 'test_secret'
      );
      expect(decoded.userId).toBe(testUser.id);
    });

    test('rejects invalid password', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          email: 'auth@example.com',
          password: 'wrongpassword'
        })
        .expect(401);

      expect(response.body.error).toBe('Invalid credentials');
    });

    test('rejects non-existent user', async () => {
      await request(app)
        .post('/auth/login')
        .send({
          email: 'nonexistent@example.com',
          password: 'password123'
        })
        .expect(401);
    });
  });

  describe('Protected Routes', () => {
    let validToken;

    beforeEach(() => {
      validToken = jwt.sign(
        { userId: testUser.id },
        process.env.JWT_SECRET || 'test_secret',
        { expiresIn: '1h' }
      );
    });

    test('accesses protected route with valid token', async () => {
      await request(app)
        .get('/api/protected')
        .set('Authorization', `Bearer ${validToken}`)
        .expect(200);
    });

    test('rejects access without token', async () => {
      await request(app)
        .get('/api/protected')
        .expect(401);
    });

    test('rejects expired token', async () => {
      const expiredToken = jwt.sign(
        { userId: testUser.id },
        process.env.JWT_SECRET || 'test_secret',
        { expiresIn: '0s' }
      );

      await new Promise(resolve => setTimeout(resolve, 100));

      await request(app)
        .get('/api/protected')
        .set('Authorization', `Bearer ${expiredToken}`)
        .expect(401);
    });
  });

  describe('Token Refresh', () => {
    test('refreshes access token with valid refresh token', async () => {
      const refreshToken = jwt.sign(
        { userId: testUser.id },
        process.env.REFRESH_SECRET || 'refresh_secret',
        { expiresIn: '7d' }
      );

      const response = await request(app)
        .post('/auth/refresh')
        .send({ refreshToken })
        .expect(200);

      expect(response.body.accessToken).toBeDefined();
    });
  });
});
```

## External Service Mocking with Nock

```javascript
// tests/integration/external-api.test.js
const nock = require('nock');
const ExternalService = require('../../services/external');

describe('External API Integration Tests', () => {
  afterEach(() => {
    nock.cleanAll();
  });

  test('fetches user data from external API', async () => {
    nock('https://api.external.com')
      .get('/users/123')
      .reply(200, {
        id: 123,
        name: 'External User',
        status: 'active'
      });

    const service = new ExternalService();
    const userData = await service.fetchUser(123);

    expect(userData.name).toBe('External User');
    expect(userData.status).toBe('active');
  });

  test('handles external API errors', async () => {
    nock('https://api.external.com')
      .get('/users/123')
      .reply(404, { error: 'Not found' });

    const service = new ExternalService();

    await expect(service.fetchUser(123)).rejects.toThrow('Not found');
  });

  test('retries on transient failures', async () => {
    // First call fails, second succeeds
    nock('https://api.external.com')
      .get('/users/123')
      .reply(500, { error: 'Server error' })
      .get('/users/123')
      .reply(200, { id: 123, name: 'Success' });

    const service = new ExternalService({ maxRetries: 2 });
    const userData = await service.fetchUser(123);

    expect(userData.name).toBe('Success');
  });

  test('respects timeout settings', async () => {
    nock('https://api.external.com')
      .get('/users/123')
      .delay(3000)  // 3 second delay
      .reply(200, { id: 123 });

    const service = new ExternalService({ timeout: 1000 });

    await expect(service.fetchUser(123)).rejects.toThrow(/timeout/i);
  });
});
```

## Redis Integration Tests

```javascript
// tests/integration/redis.test.js
const { GenericContainer } = require('testcontainers');
const Redis = require('ioredis');
const CacheService = require('../../services/cache');

describe('Redis Integration Tests', () => {
  let redisContainer;
  let redisClient;
  let cacheService;

  beforeAll(async () => {
    redisContainer = await new GenericContainer('redis:7-alpine')
      .withExposedPorts(6379)
      .start();

    const port = redisContainer.getMappedPort(6379);
    redisClient = new Redis({ host: 'localhost', port });
    cacheService = new CacheService(redisClient);
  }, 30000);

  afterAll(async () => {
    await redisClient.quit();
    await redisContainer.stop();
  });

  afterEach(async () => {
    await redisClient.flushdb();
  });

  test('sets and gets cache value', async () => {
    await cacheService.set('key1', 'value1');
    const value = await cacheService.get('key1');

    expect(value).toBe('value1');
  });

  test('respects TTL expiration', async () => {
    await cacheService.set('key2', 'value2', 1); // 1 second TTL

    const immediate = await cacheService.get('key2');
    expect(immediate).toBe('value2');

    // Wait for expiration
    await new Promise(resolve => setTimeout(resolve, 1100));

    const expired = await cacheService.get('key2');
    expect(expired).toBeNull();
  });

  test('deletes cache key', async () => {
    await cacheService.set('key3', 'value3');
    await cacheService.delete('key3');

    const deleted = await cacheService.get('key3');
    expect(deleted).toBeNull();
  });

  test('handles complex objects', async () => {
    const obj = { user: { id: 1, name: 'Alice' }, roles: ['admin', 'user'] };
    await cacheService.set('obj1', obj);

    const retrieved = await cacheService.get('obj1');
    expect(retrieved).toEqual(obj);
  });
});
```

## Test Factories

```javascript
// tests/factories.js
const { faker } = require('@faker-js/faker');
const { User, Post } = require('../models');

class UserFactory {
  static async create(overrides = {}) {
    return await User.create({
      name: faker.person.fullName(),
      email: faker.internet.email(),
      password: await bcrypt.hash('password123', 10),
      ...overrides
    });
  }

  static async createBatch(count, overrides = {}) {
    const promises = Array(count).fill(null).map(() => this.create(overrides));
    return await Promise.all(promises);
  }
}

class PostFactory {
  static async create(overrides = {}) {
    let userId = overrides.userId;

    if (!userId) {
      const user = await UserFactory.create();
      userId = user.id;
    }

    return await Post.create({
      title: faker.lorem.sentence(),
      content: faker.lorem.paragraphs(3),
      userId,
      ...overrides
    });
  }

  static async createBatch(count, overrides = {}) {
    const promises = Array(count).fill(null).map(() => this.create(overrides));
    return await Promise.all(promises);
  }
}

module.exports = { UserFactory, PostFactory };
```

## Using Factories in Tests

```javascript
// tests/integration/with-factories.test.js
const request = require('supertest');
const app = require('../../app');
const { UserFactory, PostFactory } = require('../factories');

describe('Integration Tests with Factories', () => {
  test('retrieves user with posts', async () => {
    const user = await UserFactory.create();
    await PostFactory.createBatch(3, { userId: user.id });

    const response = await request(app)
      .get(`/users/${user.id}/posts`)
      .expect(200);

    expect(response.body.posts).toHaveLength(3);
  });

  test('creates multiple users efficiently', async () => {
    const users = await UserFactory.createBatch(10);

    expect(users).toHaveLength(10);
    users.forEach(user => {
      expect(user.id).toBeDefined();
      expect(user.email).toContain('@');
    });
  });

  test('overrides factory defaults', async () => {
    const user = await UserFactory.create({
      name: 'Custom Name',
      email: 'custom@example.com'
    });

    expect(user.name).toBe('Custom Name');
    expect(user.email).toBe('custom@example.com');
  });
});
```

## Message Queue Integration Tests

```javascript
// tests/integration/message-queue.test.js
const { GenericContainer } = require('testcontainers');
const amqp = require('amqplib');
const QueueService = require('../../services/queue');

describe('RabbitMQ Integration Tests', () => {
  let rabbitmqContainer;
  let connection;
  let queueService;

  beforeAll(async () => {
    rabbitmqContainer = await new GenericContainer('rabbitmq:3-alpine')
      .withExposedPorts(5672)
      .start();

    const port = rabbitmqContainer.getMappedPort(5672);
    connection = await amqp.connect(`amqp://localhost:${port}`);
    queueService = new QueueService(connection);
  }, 60000);

  afterAll(async () => {
    await connection.close();
    await rabbitmqContainer.stop();
  });

  test('publishes and consumes message', async () => {
    const testQueue = 'test_queue';
    const testMessage = { id: 1, data: 'test' };

    await queueService.publish(testQueue, testMessage);

    const received = await new Promise((resolve) => {
      queueService.consume(testQueue, (msg) => {
        resolve(JSON.parse(msg.content.toString()));
      });
    });

    expect(received).toEqual(testMessage);
  });

  test('handles multiple consumers', async () => {
    const queue = 'multi_consumer_queue';
    const messages = [];

    // Start two consumers
    const consumer1 = queueService.consume(queue, (msg) => {
      messages.push({ consumer: 1, data: msg.content.toString() });
    });

    const consumer2 = queueService.consume(queue, (msg) => {
      messages.push({ consumer: 2, data: msg.content.toString() });
    });

    // Publish messages
    await queueService.publish(queue, 'message1');
    await queueService.publish(queue, 'message2');

    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 100));

    expect(messages).toHaveLength(2);
  });
});
```

## Complete Integration Test Suite

```javascript
// tests/integration/user-lifecycle.test.js
const request = require('supertest');
const app = require('../../app');
const { UserFactory } = require('../factories');

describe('User Lifecycle Integration Tests', () => {
  describe('Registration and Login Flow', () => {
    test('completes full registration and login', async () => {
      // Register
      const registerResponse = await request(app)
        .post('/auth/register')
        .send({
          name: 'NewUser',
          email: 'newuser@example.com',
          password: 'SecurePass123!'
        })
        .expect(201);

      expect(registerResponse.body.id).toBeDefined();
      const userId = registerResponse.body.id;

      // Login
      const loginResponse = await request(app)
        .post('/auth/login')
        .send({
          email: 'newuser@example.com',
          password: 'SecurePass123!'
        })
        .expect(200);

      expect(loginResponse.body.accessToken).toBeDefined();
      const token = loginResponse.body.accessToken;

      // Access profile
      const profileResponse = await request(app)
        .get(`/users/${userId}`)
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(profileResponse.body.name).toBe('NewUser');
    });
  });

  describe('Content Creation Flow', () => {
    let user, token;

    beforeEach(async () => {
      user = await UserFactory.create();
      token = generateToken(user.id);
    });

    test('creates and retrieves content', async () => {
      // Create post
      const createResponse = await request(app)
        .post('/posts')
        .set('Authorization', `Bearer ${token}`)
        .send({
          title: 'Integration Test Post',
          content: 'This is test content'
        })
        .expect(201);

      const postId = createResponse.body.id;

      // Retrieve post
      const getResponse = await request(app)
        .get(`/posts/${postId}`)
        .expect(200);

      expect(getResponse.body.title).toBe('Integration Test Post');
    });

    test('updates content', async () => {
      const post = await PostFactory.create({ userId: user.id });

      await request(app)
        .put(`/posts/${post.id}`)
        .set('Authorization', `Bearer ${token}`)
        .send({ title: 'Updated Title' })
        .expect(200);

      const updated = await request(app)
        .get(`/posts/${post.id}`)
        .expect(200);

      expect(updated.body.title).toBe('Updated Title');
    });
  });
});
```
