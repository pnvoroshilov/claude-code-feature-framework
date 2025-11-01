# Example 2: Integration Test Setup

## Problem Statement

You need to test how multiple components work together, particularly interactions with a database. Integration tests verify that different parts of your application integrate correctly, catching issues that unit tests miss. The challenge is setting up realistic test environments while keeping tests fast and isolated.

## Use Case

Use integration testing when you need to:
- Test database operations (create, read, update, delete)
- Verify API endpoint behavior with real database
- Test service layer interactions
- Ensure data persistence works correctly
- Validate transaction handling

This is the middle layer of the testing pyramid - more comprehensive than unit tests, faster than end-to-end tests.

## Solution Overview

We'll build a complete integration test setup that includes:
1. Test database creation and teardown
2. Data fixtures and seeding
3. Testing CRUD operations
4. Transaction handling
5. Cleanup between tests
6. Realistic test scenarios

## Complete Code

### JavaScript/TypeScript with SQLite

```javascript
// userService.js - Service layer to test
import { Database } from 'sqlite3';

export class UserService {
  constructor(db) {
    this.db = db;
  }

  async createUser(userData) {
    return new Promise((resolve, reject) => {
      const { name, email, age } = userData;
      const sql = `INSERT INTO users (name, email, age, created_at) VALUES (?, ?, ?, datetime('now'))`;

      this.db.run(sql, [name, email, age], function(err) {
        if (err) reject(err);
        resolve({
          id: this.lastID,
          name,
          email,
          age,
          created_at: new Date()
        });
      });
    });
  }

  async getUserById(id) {
    return new Promise((resolve, reject) => {
      const sql = `SELECT * FROM users WHERE id = ?`;
      this.db.get(sql, [id], (err, row) => {
        if (err) reject(err);
        resolve(row);
      });
    });
  }

  async updateUser(id, updates) {
    return new Promise((resolve, reject) => {
      const { name, email, age } = updates;
      const sql = `UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?`;

      this.db.run(sql, [name, email, age, id], (err) => {
        if (err) reject(err);
        this.getUserById(id).then(resolve).catch(reject);
      });
    });
  }

  async deleteUser(id) {
    return new Promise((resolve, reject) => {
      const sql = `DELETE FROM users WHERE id = ?`;
      this.db.run(sql, [id], (err) => {
        if (err) reject(err);
        resolve({ id, deleted: true });
      });
    });
  }

  async getAllUsers() {
    return new Promise((resolve, reject) => {
      const sql = `SELECT * FROM users ORDER BY created_at DESC`;
      this.db.all(sql, [], (err, rows) => {
        if (err) reject(err);
        resolve(rows);
      });
    });
  }

  async findUserByEmail(email) {
    return new Promise((resolve, reject) => {
      const sql = `SELECT * FROM users WHERE email = ?`;
      this.db.get(sql, [email], (err, row) => {
        if (err) reject(err);
        resolve(row);
      });
    });
  }
}
```

```javascript
// userService.test.js - Integration tests
import { Database } from 'sqlite3';
import { UserService } from './userService';

describe('UserService Integration Tests', () => {
  let db;
  let userService;

  // Setup: Create test database once before all tests
  beforeAll(async () => {
    // Use in-memory SQLite database for speed
    db = new Database(':memory:');

    // Create schema
    await new Promise((resolve, reject) => {
      db.run(`
        CREATE TABLE users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          age INTEGER,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `, (err) => {
        if (err) reject(err);
        resolve();
      });
    });

    userService = new UserService(db);
  });

  // Cleanup: Clear data before each test for isolation
  beforeEach(async () => {
    await new Promise((resolve, reject) => {
      db.run('DELETE FROM users', (err) => {
        if (err) reject(err);
        resolve();
      });
    });
  });

  // Teardown: Close database after all tests
  afterAll(async () => {
    await new Promise((resolve) => {
      db.close(resolve);
    });
  });

  describe('createUser', () => {
    test('should create user with valid data', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        age: 30
      };

      const user = await userService.createUser(userData);

      expect(user.id).toBeDefined();
      expect(user.name).toBe('John Doe');
      expect(user.email).toBe('john@example.com');
      expect(user.age).toBe(30);
    });

    test('should auto-generate ID', async () => {
      const user1 = await userService.createUser({
        name: 'User 1',
        email: 'user1@example.com',
        age: 25
      });

      const user2 = await userService.createUser({
        name: 'User 2',
        email: 'user2@example.com',
        age: 35
      });

      expect(user1.id).toBe(1);
      expect(user2.id).toBe(2);
    });

    test('should reject duplicate email', async () => {
      await userService.createUser({
        name: 'User 1',
        email: 'same@example.com',
        age: 25
      });

      await expect(
        userService.createUser({
          name: 'User 2',
          email: 'same@example.com',
          age: 30
        })
      ).rejects.toThrow();
    });
  });

  describe('getUserById', () => {
    test('should retrieve existing user', async () => {
      const created = await userService.createUser({
        name: 'Jane Smith',
        email: 'jane@example.com',
        age: 28
      });

      const retrieved = await userService.getUserById(created.id);

      expect(retrieved.id).toBe(created.id);
      expect(retrieved.name).toBe('Jane Smith');
      expect(retrieved.email).toBe('jane@example.com');
    });

    test('should return undefined for non-existent user', async () => {
      const user = await userService.getUserById(999);
      expect(user).toBeUndefined();
    });
  });

  describe('updateUser', () => {
    test('should update user fields', async () => {
      const user = await userService.createUser({
        name: 'Original Name',
        email: 'original@example.com',
        age: 25
      });

      const updated = await userService.updateUser(user.id, {
        name: 'Updated Name',
        email: 'updated@example.com',
        age: 26
      });

      expect(updated.id).toBe(user.id);
      expect(updated.name).toBe('Updated Name');
      expect(updated.email).toBe('updated@example.com');
      expect(updated.age).toBe(26);
    });

    test('should persist changes to database', async () => {
      const user = await userService.createUser({
        name: 'Test User',
        email: 'test@example.com',
        age: 30
      });

      await userService.updateUser(user.id, {
        name: 'Updated User',
        email: 'updated@example.com',
        age: 31
      });

      // Fetch again to verify persistence
      const fetched = await userService.getUserById(user.id);
      expect(fetched.name).toBe('Updated User');
      expect(fetched.age).toBe(31);
    });
  });

  describe('deleteUser', () => {
    test('should delete existing user', async () => {
      const user = await userService.createUser({
        name: 'To Delete',
        email: 'delete@example.com',
        age: 40
      });

      const result = await userService.deleteUser(user.id);

      expect(result.deleted).toBe(true);

      // Verify user no longer exists
      const fetched = await userService.getUserById(user.id);
      expect(fetched).toBeUndefined();
    });
  });

  describe('getAllUsers', () => {
    test('should return empty array when no users', async () => {
      const users = await userService.getAllUsers();
      expect(users).toEqual([]);
    });

    test('should return all users ordered by creation', async () => {
      await userService.createUser({
        name: 'User 1',
        email: 'user1@example.com',
        age: 25
      });

      await new Promise(resolve => setTimeout(resolve, 10)); // Small delay

      await userService.createUser({
        name: 'User 2',
        email: 'user2@example.com',
        age: 30
      });

      const users = await userService.getAllUsers();

      expect(users).toHaveLength(2);
      expect(users[0].name).toBe('User 2'); // Most recent first
      expect(users[1].name).toBe('User 1');
    });
  });

  describe('findUserByEmail', () => {
    test('should find user by exact email', async () => {
      await userService.createUser({
        name: 'Findable User',
        email: 'find@example.com',
        age: 35
      });

      const found = await userService.findUserByEmail('find@example.com');

      expect(found).toBeDefined();
      expect(found.name).toBe('Findable User');
    });

    test('should return undefined for non-existent email', async () => {
      const found = await userService.findUserByEmail('notfound@example.com');
      expect(found).toBeUndefined();
    });

    test('should be case-sensitive', async () => {
      await userService.createUser({
        name: 'Test User',
        email: 'test@example.com',
        age: 30
      });

      const found = await userService.findUserByEmail('TEST@EXAMPLE.COM');
      expect(found).toBeUndefined();
    });
  });

  describe('Complex scenarios', () => {
    test('should handle multiple operations in sequence', async () => {
      // Create
      const user = await userService.createUser({
        name: 'Sequential Test',
        email: 'sequential@example.com',
        age: 25
      });

      // Read
      const fetched1 = await userService.getUserById(user.id);
      expect(fetched1.name).toBe('Sequential Test');

      // Update
      await userService.updateUser(user.id, {
        name: 'Updated Sequential',
        email: 'sequential@example.com',
        age: 26
      });

      // Read again
      const fetched2 = await userService.getUserById(user.id);
      expect(fetched2.name).toBe('Updated Sequential');
      expect(fetched2.age).toBe(26);

      // Delete
      await userService.deleteUser(user.id);

      // Verify deletion
      const fetched3 = await userService.getUserById(user.id);
      expect(fetched3).toBeUndefined();
    });

    test('should handle concurrent operations', async () => {
      // Create multiple users concurrently
      const promises = [
        userService.createUser({ name: 'User 1', email: 'concurrent1@example.com', age: 20 }),
        userService.createUser({ name: 'User 2', email: 'concurrent2@example.com', age: 30 }),
        userService.createUser({ name: 'User 3', email: 'concurrent3@example.com', age: 40 })
      ];

      const users = await Promise.all(promises);

      expect(users).toHaveLength(3);
      expect(users[0].id).toBeDefined();
      expect(users[1].id).toBeDefined();
      expect(users[2].id).toBeDefined();

      // All users should be retrievable
      const allUsers = await userService.getAllUsers();
      expect(allUsers).toHaveLength(3);
    });
  });
});
```

### Python with SQLAlchemy

```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# user_service.py
class UserService:
    def __init__(self, session):
        self.session = session

    def create_user(self, name, email, age):
        user = User(name=name, email=email, age=age)
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id, name=None, email=None, age=None):
        user = self.get_user_by_id(user_id)
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
            if age:
                user.age = age
            self.session.commit()
        return user

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def get_all_users(self):
        return self.session.query(User).order_by(User.created_at.desc()).all()

    def find_user_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()
```

```python
# test_user_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from user_service import UserService

@pytest.fixture(scope='function')
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')

    # Create tables
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()

@pytest.fixture
def user_service(db_session):
    """Create UserService with test database"""
    return UserService(db_session)

class TestUserService:
    def test_create_user(self, user_service):
        user = user_service.create_user('John Doe', 'john@example.com', 30)

        assert user.id is not None
        assert user.name == 'John Doe'
        assert user.email == 'john@example.com'
        assert user.age == 30
        assert user.created_at is not None

    def test_get_user_by_id(self, user_service):
        created = user_service.create_user('Jane Smith', 'jane@example.com', 28)

        retrieved = user_service.get_user_by_id(created.id)

        assert retrieved.id == created.id
        assert retrieved.name == 'Jane Smith'
        assert retrieved.email == 'jane@example.com'

    def test_update_user(self, user_service):
        user = user_service.create_user('Original', 'original@example.com', 25)

        updated = user_service.update_user(
            user.id,
            name='Updated',
            email='updated@example.com',
            age=26
        )

        assert updated.name == 'Updated'
        assert updated.email == 'updated@example.com'
        assert updated.age == 26

    def test_delete_user(self, user_service):
        user = user_service.create_user('To Delete', 'delete@example.com', 40)

        result = user_service.delete_user(user.id)
        assert result is True

        fetched = user_service.get_user_by_id(user.id)
        assert fetched is None

    def test_get_all_users(self, user_service):
        user_service.create_user('User 1', 'user1@example.com', 25)
        user_service.create_user('User 2', 'user2@example.com', 30)

        users = user_service.get_all_users()

        assert len(users) == 2

    def test_find_user_by_email(self, user_service):
        user_service.create_user('Findable', 'find@example.com', 35)

        found = user_service.find_user_by_email('find@example.com')

        assert found is not None
        assert found.name == 'Findable'
```

## Code Explanation

### Test Database Setup

The key to integration testing is proper database management:

```javascript
beforeAll(async () => {
  // Create in-memory database (fast, isolated)
  db = new Database(':memory:');

  // Run schema migrations
  await createSchema(db);

  // Initialize service
  userService = new UserService(db);
});
```

**Why in-memory?**
- Extremely fast (no disk I/O)
- Completely isolated
- Automatic cleanup
- Perfect for tests

### Data Isolation Pattern

```javascript
beforeEach(async () => {
  // Clear all data before each test
  await db.run('DELETE FROM users');
});
```

**This ensures:**
- Each test starts with clean state
- No test affects another
- Tests can run in any order
- Reproducible results

### Next Steps

- [Example 3: Mock and Stub Usage](example-3.md)
- [Intermediate Pattern 1: Test Organization](../intermediate/pattern-1.md)
- [Advanced Topics: Performance Testing](../../docs/advanced-topics.md#performance-testing)
