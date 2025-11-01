# Troubleshooting - API Development

Common issues, debugging strategies, and solutions for API development problems.

## Table of Contents

- [1. CORS Issues](#1-cors-issues)
- [2. Authentication Failures](#2-authentication-failures)
- [3. 422 Validation Errors](#3-422-validation-errors)
- [4. Database Connection Problems](#4-database-connection-problems)
- [5. Performance Issues](#5-performance-issues)
- [6. Rate Limiting Problems](#6-rate-limiting-problems)
- [7. WebSocket Connection Issues](#7-websocket-connection-issues)
- [8. File Upload Failures](#8-file-upload-failures)
- [9. Timeout Errors](#9-timeout-errors)
- [10. Memory Leaks](#10-memory-leaks)

---

## 1. CORS Issues

### Symptom
```
Access to fetch at 'http://api.example.com/data' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

### Root Cause
- CORS middleware not configured
- Wrong origin in allow list
- Credentials without proper headers

### Solution

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://app.example.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Debugging

```python
# Log CORS headers
@app.middleware("http")
async def log_cors(request: Request, call_next):
    origin = request.headers.get("origin")
    print(f"Origin: {origin}")

    response = await call_next(request)

    print(f"CORS Headers: {response.headers}")
    return response
```

---

## 2. Authentication Failures

### Symptom
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### Common Causes
1. **Expired token**
2. **Wrong secret key**
3. **Missing Authorization header**
4. **Incorrect token format**

### Solution

```python
import jwt
from datetime import datetime

def verify_token(token: str):
    """Debug token verification"""
    try:
        # Decode without verification first to inspect
        unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"Token payload: {unverified}")

        # Check expiration
        exp = unverified.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise ValueError("Token expired")

        # Now verify with secret
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        print("Token expired!")
        raise
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        raise
```

### Testing

```python
# Test token generation
token = create_access_token({"sub": "test@example.com"})
print(f"Generated token: {token}")

# Test verification
try:
    payload = verify_token(token)
    print(f"Verified payload: {payload}")
except Exception as e:
    print(f"Verification failed: {e}")
```

---

## 3. 422 Validation Errors

### Symptom
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Root Cause
- Invalid input data
- Type mismatch
- Missing required fields
- Constraint violations

### Solution

```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class UserCreate(BaseModel):
    """Add clear validation messages"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex="^[a-zA-Z0-9_-]+$",
        description="Alphanumeric username, 3-50 characters"
    )
    email: EmailStr = Field(..., description="Valid email address")
    age: Optional[int] = Field(None, ge=13, le=150, description="Age between 13-150")

    @validator('username')
    def validate_username(cls, v):
        """Custom validation with helpful messages"""
        if v.lower() in ['admin', 'root']:
            raise ValueError('Username is reserved')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "age": 30
            }
        }
```

### Custom Error Handler

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """More helpful validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])
        errors.append({
            "field": field,
            "message": f"{field}: {error['msg']}",
            "input": error.get("input"),
            "expected_type": error.get("type")
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": errors,
            "documentation": "https://api.example.com/docs"
        }
    )
```

---

## 4. Database Connection Problems

### Symptom
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

### Checklist
- [ ] Database server running?
- [ ] Correct connection string?
- [ ] Network accessible?
- [ ] Credentials valid?
- [ ] Connection pool exhausted?

### Solution

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Proper connection with retry
def create_db_engine(retries=3):
    """Create engine with connection retry"""
    for attempt in range(retries):
        try:
            engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle after 1 hour
                echo=True            # Log SQL (disable in production)
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Debug Connection Issues

```python
import psycopg2

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mydb",
            user="user",
            password="password",
            connect_timeout=5
        )
        print("✓ Connection successful")
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"✗ Connection failed: {e}")
```

---

## 5. Performance Issues

### Symptom
- Slow response times
- High CPU usage
- Memory growing
- Timeouts

### Common Causes

#### N+1 Query Problem

```python
# ❌ Bad: N+1 queries
@app.get("/users")
async def get_users():
    users = db.query(User).all()
    return [
        {
            "user": user,
            "posts": db.query(Post).filter(Post.user_id == user.id).all()
        }
        for user in users  # Queries posts for each user!
    ]

# ✅ Good: Join or eager loading
@app.get("/users")
async def get_users():
    users = db.query(User).options(
        joinedload(User.posts)
    ).all()
    return users
```

#### Missing Indexes

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)  # Index for lookups
    created_at = Column(DateTime, index=True)  # Index for sorting

    # Composite index for common query
    __table_args__ = (
        Index('idx_user_status_created', 'status', 'created_at'),
    )
```

### Debug with Profiling

```python
import cProfile
import pstats

@app.get("/slow-endpoint")
async def slow_endpoint():
    """Profile this endpoint"""
    profiler = cProfile.Profile()
    profiler.enable()

    # Your code here
    result = do_expensive_operation()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 slowest functions

    return result
```

### SQL Query Logging

```python
import logging

# Enable SQL logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Now all queries are logged:
# INFO:sqlalchemy.engine:SELECT * FROM users WHERE id = 1
```

---

## 6. Rate Limiting Problems

### Symptom
```json
{
  "error": "rate_limit_exceeded",
  "retry_after": 60
}
```

### Debugging Rate Limits

```python
from slowapi import Limiter
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@app.get("/debug/rate-limit")
async def check_rate_limit(request: Request):
    """Check current rate limit status"""
    key = get_remote_address(request)
    current = limiter.current_limit

    return {
        "key": key,
        "limit": current.limit,
        "remaining": current.remaining,
        "reset_at": current.reset_time
    }
```

### Custom Rate Limit Response

```python
from slowapi.errors import RateLimitExceeded

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Too many requests. Limit: {exc.limit}",
            "retry_after": exc.reset_time - time.time()
        },
        headers={
            "Retry-After": str(int(exc.reset_time - time.time())),
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(exc.reset_time)
        }
    )
```

---

## 7. WebSocket Connection Issues

### Symptom
- Connection closes immediately
- Unable to send/receive messages
- Authentication fails

### Debugging

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Debug WebSocket connection"""
    print(f"Connection attempt from: {websocket.client}")
    print(f"Headers: {websocket.headers}")

    try:
        await websocket.accept()
        print("✓ Connection accepted")

        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")

            await websocket.send_text(f"Echo: {data}")
            print(f"Sent: Echo: {data}")

    except WebSocketDisconnect as e:
        print(f"✗ Disconnected: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
        await websocket.close(code=1011)
```

### Common Issues

```python
# Issue: Authentication failure
@app.websocket("/ws")
async def ws_with_auth(websocket: WebSocket):
    # Get token from query params (WebSocket can't use headers)
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=403, reason="Missing token")
        return

    try:
        user = verify_token(token)
    except Exception:
        await websocket.close(code=403, reason="Invalid token")
        return

    await websocket.accept()
    # Continue...
```

---

## 8. File Upload Failures

### Symptom
- File too large error
- Timeout during upload
- Corrupted files

### Solution

```python
from fastapi import File, UploadFile, HTTPException
import aiofiles

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload with validation"""

    # Check file size (10MB limit)
    MAX_SIZE = 10 * 1024 * 1024
    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_SIZE} bytes"
        )

    # Validate file type
    ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid file type. Allowed: {ALLOWED_TYPES}"
        )

    # Save file
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

### Streaming Large Files

```python
@app.post("/upload/stream")
async def upload_large_file(file: UploadFile = File(...)):
    """Stream large files to avoid memory issues"""
    file_path = f"uploads/{file.filename}"

    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)

    return {"filename": file.filename}
```

---

## 9. Timeout Errors

### Symptom
```
TimeoutError: Request timed out after 30 seconds
```

### Solutions

```python
import httpx
import asyncio

# Increase timeout for external API calls
async def call_external_api():
    """Call with custom timeout"""
    timeout = httpx.Timeout(
        connect=5.0,  # Connection timeout
        read=30.0,    # Read timeout
        write=5.0,    # Write timeout
        pool=None     # Pool timeout
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get("https://slow-api.example.com/data")
        return response.json()

# Add timeout to async operations
@app.get("/slow-operation")
async def slow_operation():
    """Operation with timeout"""
    try:
        result = await asyncio.wait_for(
            expensive_operation(),
            timeout=10.0
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Operation timed out"
        )
```

---

## 10. Memory Leaks

### Symptom
- Memory usage continuously grows
- Eventually crashes
- Slower over time

### Common Causes

#### 1. Unclosed Database Connections

```python
# ❌ Bad: Connection not closed
@app.get("/users")
async def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    return users  # Connection never closed!

# ✅ Good: Proper cleanup
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """Dependency handles cleanup"""
    return db.query(User).all()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Always closed
```

#### 2. Caching Everything

```python
# ❌ Bad: Unbounded cache
cache = {}

@app.get("/data/{key}")
async def get_data(key: str):
    if key not in cache:
        cache[key] = fetch_expensive_data(key)  # Cache grows forever!
    return cache[key]

# ✅ Good: Bounded cache
from functools import lru_cache

@lru_cache(maxsize=1000)  # Limited size
def fetch_expensive_data(key: str):
    return expensive_operation(key)
```

### Memory Profiling

```python
import tracemalloc
import linecache

tracemalloc.start()

@app.get("/memory-debug")
async def debug_memory():
    """Check memory usage"""
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 memory consumers ]")
    for stat in top_stats[:10]:
        print(stat)

    return {"memory_usage": "Check logs"}
```

---

## Debugging Checklist

### When Things Go Wrong:

1. **Check Logs**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Enable SQL Logging**
   ```python
   engine = create_engine(url, echo=True)
   ```

3. **Test with curl**
   ```bash
   curl -X GET http://localhost:8000/api/endpoint -H "Authorization: Bearer token"
   ```

4. **Check Interactive Docs**
   Navigate to `/docs` for OpenAPI interface

5. **Profile Slow Endpoints**
   Use cProfile to find bottlenecks

6. **Monitor Database**
   Check active connections, slow queries

7. **Review Error Logs**
   Look for patterns in errors

8. **Test Auth Separately**
   Verify token generation and validation

9. **Validate Input/Output**
   Use Pydantic models with examples

10. **Check Network**
    Verify firewalls, DNS, connectivity

---

## Getting More Help

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://pydantic-docs.helpmanual.io/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Stack Overflow**: Tag questions with `fastapi`, `pydantic`, `sqlalchemy`

Most issues can be resolved by:
1. Checking logs for detailed error messages
2. Verifying configuration (database URL, secret keys, etc.)
3. Testing components in isolation
4. Reviewing official documentation
5. Using interactive debugging tools

Happy debugging!
