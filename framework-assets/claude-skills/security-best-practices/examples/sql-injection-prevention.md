# SQL Injection Prevention - Complete Guide

Comprehensive examples of preventing SQL injection attacks across different frameworks and languages.

## Understanding SQL Injection

SQL injection occurs when untrusted data is inserted into SQL queries without proper escaping or parameterization, allowing attackers to manipulate the query logic.

## Attack Examples

sql_injection_attacks[6]{attack_type,payload,impact}:
Authentication Bypass,admin' OR '1'='1,Login without password
Data Extraction,' UNION SELECT password FROM users--,Steal sensitive data
Data Modification,'; UPDATE users SET role='admin,Escalate privileges
Data Deletion,'; DROP TABLE users;--,Destroy data
Blind SQL Injection,' AND SLEEP(5)--,Infer data through timing
Second-Order Injection,Stored malicious SQL,Exploited on retrieval

## 1. Python - SQLAlchemy (ORM)

### Secure Implementation

**Python (SQLAlchemy ORM)**:
```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    category = Column(String(50))

# Database setup
engine = create_engine('postgresql://user:password@localhost/mydb')
SessionLocal = sessionmaker(bind=engine)

class ProductRepository:
    """Secure product repository using ORM"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """✅ SECURE - ORM handles parameterization"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def search_by_name(self, name: str) -> List[Product]:
        """✅ SECURE - ORM prevents injection"""
        return self.db.query(Product).filter(
            Product.name.ilike(f'%{name}%')
        ).all()

    def get_by_category(self, category: str) -> List[Product]:
        """✅ SECURE - Using filter_by"""
        return self.db.query(Product).filter_by(category=category).all()

    def create(self, name: str, description: str, price: float, category: str) -> Product:
        """✅ SECURE - ORM insert"""
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: int, **kwargs) -> Optional[Product]:
        """✅ SECURE - ORM update"""
        product = self.get_by_id(product_id)
        if not product:
            return None

        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> bool:
        """✅ SECURE - ORM delete"""
        product = self.get_by_id(product_id)
        if not product:
            return False

        self.db.delete(product)
        self.db.commit()
        return True

# Usage with FastAPI
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/products/search")
async def search_products(q: str, db: Session = Depends(get_db)):
    """Search products - automatically protected from SQL injection"""
    repo = ProductRepository(db)
    products = repo.search_by_name(q)
    return products

@app.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID - automatically protected"""
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

### Using Raw SQL (Text Queries)

**Python (SQLAlchemy Core with Parameters)**:
```python
from sqlalchemy import text

class ProductRepositoryRaw:
    """Using raw SQL with proper parameterization"""

    def __init__(self, db: Session):
        self.db = db

    def search_by_name(self, name: str) -> List[dict]:
        """✅ SECURE - Named parameters"""
        query = text("""
            SELECT id, name, description, price, category
            FROM products
            WHERE name ILIKE :search_term
            ORDER BY name
        """)

        result = self.db.execute(query, {"search_term": f"%{name}%"})
        return [dict(row) for row in result]

    def get_by_category_and_price(
        self,
        category: str,
        min_price: float,
        max_price: float
    ) -> List[dict]:
        """✅ SECURE - Multiple parameters"""
        query = text("""
            SELECT id, name, description, price, category
            FROM products
            WHERE category = :category
              AND price BETWEEN :min_price AND :max_price
            ORDER BY price
        """)

        result = self.db.execute(query, {
            "category": category,
            "min_price": min_price,
            "max_price": max_price
        })
        return [dict(row) for row in result]

    def create_product(
        self,
        name: str,
        description: str,
        price: float,
        category: str
    ) -> int:
        """✅ SECURE - Parameterized insert"""
        query = text("""
            INSERT INTO products (name, description, price, category)
            VALUES (:name, :description, :price, :category)
            RETURNING id
        """)

        result = self.db.execute(query, {
            "name": name,
            "description": description,
            "price": price,
            "category": category
        })
        self.db.commit()

        return result.scalar()

    def update_product(self, product_id: int, **kwargs) -> bool:
        """✅ SECURE - Dynamic update with parameterization"""
        if not kwargs:
            return False

        # Build SET clause dynamically (still safe)
        set_clauses = [f"{key} = :{key}" for key in kwargs.keys()]
        set_clause = ", ".join(set_clauses)

        query = text(f"""
            UPDATE products
            SET {set_clause}
            WHERE id = :product_id
        """)

        kwargs['product_id'] = product_id
        result = self.db.execute(query, kwargs)
        self.db.commit()

        return result.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        """✅ SECURE - Parameterized delete"""
        query = text("DELETE FROM products WHERE id = :product_id")
        result = self.db.execute(query, {"product_id": product_id})
        self.db.commit()

        return result.rowcount > 0
```

## 2. JavaScript/TypeScript - PostgreSQL

### Using node-postgres (pg)

**TypeScript**:
```typescript
import { Pool, PoolClient } from 'pg';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
}

class ProductRepository {
  constructor(private pool: Pool) {}

  async getById(productId: number): Promise<Product | null> {
    // ✅ SECURE - Parameterized query with $1 placeholder
    const query = 'SELECT * FROM products WHERE id = $1';
    const result = await this.pool.query(query, [productId]);

    return result.rows[0] || null;
  }

  async searchByName(name: string): Promise<Product[]> {
    // ✅ SECURE - Parameterized LIKE query
    const query = `
      SELECT id, name, description, price, category
      FROM products
      WHERE name ILIKE $1
      ORDER BY name
    `;
    const result = await this.pool.query(query, [`%${name}%`]);

    return result.rows;
  }

  async getByCategoryAndPriceRange(
    category: string,
    minPrice: number,
    maxPrice: number
  ): Promise<Product[]> {
    // ✅ SECURE - Multiple parameters
    const query = `
      SELECT id, name, description, price, category
      FROM products
      WHERE category = $1
        AND price BETWEEN $2 AND $3
      ORDER BY price
    `;
    const result = await this.pool.query(query, [category, minPrice, maxPrice]);

    return result.rows;
  }

  async create(
    name: string,
    description: string,
    price: number,
    category: string
  ): Promise<Product> {
    // ✅ SECURE - Parameterized insert with RETURNING
    const query = `
      INSERT INTO products (name, description, price, category)
      VALUES ($1, $2, $3, $4)
      RETURNING *
    `;
    const result = await this.pool.query(query, [
      name,
      description,
      price,
      category,
    ]);

    return result.rows[0];
  }

  async update(
    productId: number,
    updates: Partial<Omit<Product, 'id'>>
  ): Promise<Product | null> {
    // ✅ SECURE - Dynamic update with parameterization
    const fields = Object.keys(updates);
    if (fields.length === 0) {
      return this.getById(productId);
    }

    const setClause = fields
      .map((field, index) => `${field} = $${index + 2}`)
      .join(', ');

    const query = `
      UPDATE products
      SET ${setClause}
      WHERE id = $1
      RETURNING *
    `;

    const values = [productId, ...Object.values(updates)];
    const result = await this.pool.query(query, values);

    return result.rows[0] || null;
  }

  async delete(productId: number): Promise<boolean> {
    // ✅ SECURE - Parameterized delete
    const query = 'DELETE FROM products WHERE id = $1';
    const result = await this.pool.query(query, [productId]);

    return result.rowcount > 0;
  }

  async searchWithFilters(filters: {
    name?: string;
    category?: string;
    minPrice?: number;
    maxPrice?: number;
  }): Promise<Product[]> {
    // ✅ SECURE - Dynamic WHERE clause with parameterization
    const conditions: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (filters.name) {
      conditions.push(`name ILIKE $${paramIndex++}`);
      values.push(`%${filters.name}%`);
    }

    if (filters.category) {
      conditions.push(`category = $${paramIndex++}`);
      values.push(filters.category);
    }

    if (filters.minPrice !== undefined) {
      conditions.push(`price >= $${paramIndex++}`);
      values.push(filters.minPrice);
    }

    if (filters.maxPrice !== undefined) {
      conditions.push(`price <= $${paramIndex++}`);
      values.push(filters.maxPrice);
    }

    const whereClause =
      conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const query = `
      SELECT id, name, description, price, category
      FROM products
      ${whereClause}
      ORDER BY name
    `;

    const result = await this.pool.query(query, values);
    return result.rows;
  }
}

// Usage with Express
import express from 'express';

const app = express();
const pool = new Pool({
  host: 'localhost',
  database: 'mydb',
  user: 'user',
  password: 'password',
});

const productRepo = new ProductRepository(pool);

app.get('/products/search', async (req, res) => {
  try {
    const { q } = req.query;
    const products = await productRepo.searchByName(q as string);
    res.json(products);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/products/:id', async (req, res) => {
  try {
    const productId = parseInt(req.params.id);
    const product = await productRepo.getById(productId);

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    res.json(product);
  } catch (error) {
    console.error('Get product error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

### Using TypeORM

**TypeScript**:
```typescript
import { Entity, PrimaryGeneratedColumn, Column, Repository } from 'typeorm';
import { AppDataSource } from './data-source';

@Entity('products')
class Product {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100 })
  name: string;

  @Column({ length: 500 })
  description: string;

  @Column('decimal')
  price: number;

  @Column({ length: 50 })
  category: string;
}

class ProductService {
  private repository: Repository<Product>;

  constructor() {
    this.repository = AppDataSource.getRepository(Product);
  }

  async getById(productId: number): Promise<Product | null> {
    // ✅ SECURE - TypeORM handles parameterization
    return await this.repository.findOne({ where: { id: productId } });
  }

  async searchByName(name: string): Promise<Product[]> {
    // ✅ SECURE - QueryBuilder with parameters
    return await this.repository
      .createQueryBuilder('product')
      .where('product.name ILIKE :name', { name: `%${name}%` })
      .orderBy('product.name', 'ASC')
      .getMany();
  }

  async getByCategoryAndPrice(
    category: string,
    minPrice: number,
    maxPrice: number
  ): Promise<Product[]> {
    // ✅ SECURE - Multiple parameters
    return await this.repository
      .createQueryBuilder('product')
      .where('product.category = :category', { category })
      .andWhere('product.price BETWEEN :minPrice AND :maxPrice', {
        minPrice,
        maxPrice,
      })
      .orderBy('product.price', 'ASC')
      .getMany();
  }

  async create(data: Omit<Product, 'id'>): Promise<Product> {
    // ✅ SECURE - TypeORM insert
    const product = this.repository.create(data);
    return await this.repository.save(product);
  }

  async update(
    productId: number,
    updates: Partial<Omit<Product, 'id'>>
  ): Promise<Product | null> {
    // ✅ SECURE - TypeORM update
    await this.repository.update(productId, updates);
    return await this.getById(productId);
  }

  async delete(productId: number): Promise<boolean> {
    // ✅ SECURE - TypeORM delete
    const result = await this.repository.delete(productId);
    return result.affected > 0;
  }
}
```

## 3. Common Vulnerabilities and Fixes

### Vulnerability: String Concatenation

```python
# ❌ VULNERABLE - NEVER DO THIS
def get_user_by_username(username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Attack: username = "admin' OR '1'='1"
# Result: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# Returns all users!

# ✅ FIX - Use parameterized query
def get_user_by_username_secure(username: str):
    query = "SELECT * FROM users WHERE username = :username"
    return db.execute(query, {"username": username})
```

### Vulnerability: Dynamic Column Names

```python
# ❌ VULNERABLE - User controls ORDER BY
def get_products_sorted(sort_by: str):
    query = f"SELECT * FROM products ORDER BY {sort_by}"
    return db.execute(query)

# Attack: sort_by = "id; DROP TABLE products;--"

# ✅ FIX - Whitelist allowed columns
def get_products_sorted_secure(sort_by: str):
    ALLOWED_COLUMNS = {'name', 'price', 'created_at'}

    if sort_by not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid sort column. Allowed: {ALLOWED_COLUMNS}")

    # Safe to use in query since it's whitelisted
    query = f"SELECT * FROM products ORDER BY {sort_by}"
    return db.execute(query)
```

### Vulnerability: LIKE Injection

```python
# ❌ VULNERABLE - Unescaped LIKE pattern
def search_products(search: str):
    query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
    return db.execute(query)

# ✅ FIX - Parameterize the entire LIKE expression
def search_products_secure(search: str):
    query = "SELECT * FROM products WHERE name LIKE :pattern"
    return db.execute(query, {"pattern": f"%{search}%"})
```

## Prevention Checklist

sql_injection_prevention[12]{technique,description}:
Parameterized Queries,Use ? or $1 placeholders NEVER concatenate
ORM Usage,Use SQLAlchemy TypeORM Prisma for automatic protection
Input Validation,Validate data types and formats before queries
Whitelist Columns,Whitelist column names for dynamic ORDER BY
Least Privilege,Database user with minimum necessary permissions
Stored Procedures,Pre-defined procedures with parameters
Escape Functions,Use database-specific escape functions
Error Handling,Don't expose SQL errors to users
Code Review,Review all database queries for vulnerabilities
Static Analysis,Use tools like Bandit SQLMap for detection
Prepared Statements,Use prepared statements for repeated queries
Query Logging,Log all queries for security monitoring

## Testing for SQL Injection

**Test cases to verify protection**:

```python
import pytest

def test_sql_injection_attempts(product_repo):
    """Test common SQL injection payloads"""

    injection_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE products;--",
        "' UNION SELECT * FROM users--",
        "admin'--",
        "' OR 1=1--",
        "1' AND '1'='1",
    ]

    for payload in injection_payloads:
        # Should return empty or specific product, never all products
        result = product_repo.search_by_name(payload)

        # Verify injection didn't work
        assert len(result) == 0 or all(
            payload in p.name for p in result
        ), f"Possible SQL injection with payload: {payload}"
```

---

**Remember**: Always use parameterized queries or ORM. Never concatenate user input into SQL queries.
