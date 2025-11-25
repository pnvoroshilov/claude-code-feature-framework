# OWASP Top 10 - Complete Reference

Comprehensive guide to the OWASP Top 10 web application security risks, with detailed explanations, attack scenarios, and prevention strategies.

## 1. Injection

**Risk Level**: Critical

### What is Injection?

Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. The attacker's hostile data tricks the interpreter into executing unintended commands or accessing unauthorized data.

### Common Injection Types

injection_types[6]{type,target,impact}:
SQL Injection,Database queries,Full database compromise data theft
Command Injection,Operating system commands,Server takeover arbitrary code execution
LDAP Injection,LDAP queries,Authentication bypass information disclosure
XPath Injection,XML queries,Data extraction authentication bypass
NoSQL Injection,NoSQL databases,Data extraction authentication bypass
Template Injection,Template engines,Remote code execution data leakage

### SQL Injection Examples

**Vulnerable Code (Python)**:
```python
# ❌ VULNERABLE - String concatenation
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Attack: username = "admin' OR '1'='1"
# Result: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# Returns all users!
```

**Secure Code (Python)**:
```python
# ✅ SECURE - Parameterized query
from sqlalchemy import text

def get_user(username):
    query = text("SELECT * FROM users WHERE username = :username")
    return db.execute(query, {"username": username})

# ✅ SECURE - ORM (SQLAlchemy)
def get_user_orm(username):
    return db.query(User).filter_by(username=username).first()
```

**Vulnerable Code (JavaScript/TypeScript)**:
```typescript
// ❌ VULNERABLE - Template literal
async function getUser(username: string) {
  const query = `SELECT * FROM users WHERE username = '${username}'`;
  return await db.query(query);
}
```

**Secure Code (JavaScript/TypeScript)**:
```typescript
// ✅ SECURE - Parameterized query (PostgreSQL)
async function getUser(username: string) {
  const query = 'SELECT * FROM users WHERE username = $1';
  return await db.query(query, [username]);
}

// ✅ SECURE - ORM (TypeORM)
async function getUserORM(username: string) {
  return await User.findOne({ where: { username } });
}

// ✅ SECURE - Query builder (Knex)
async function getUserKnex(username: string) {
  return await knex('users').where({ username }).first();
}
```

### Command Injection Examples

**Vulnerable Code (Python)**:
```python
import os

# ❌ VULNERABLE
def ping_host(hostname):
    os.system(f"ping -c 1 {hostname}")

# Attack: hostname = "google.com; rm -rf /"
```

**Secure Code (Python)**:
```python
import subprocess
import shlex

# ✅ SECURE - Use subprocess with list arguments
def ping_host(hostname):
    # Validate hostname format
    if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
        raise ValueError("Invalid hostname")

    subprocess.run(['ping', '-c', '1', hostname], check=True)

# ✅ EVEN BETTER - Use library instead of shell commands
import ping3

def ping_host_safe(hostname):
    return ping3.ping(hostname)
```

### Prevention Strategies

injection_prevention[8]{strategy,description,example}:
Parameterized Queries,Separate SQL from data,Use ? or $1 placeholders
ORM/Query Builders,Abstract away raw SQL,SQLAlchemy TypeORM Prisma
Input Validation,Whitelist allowed characters,Only allow alphanumeric for usernames
Least Privilege,Database user minimal permissions,Read-only for SELECT operations
Escape Special Characters,Context-specific escaping,Escape quotes in SQL context
Prepared Statements,Pre-compile SQL statements,Use JDBC PreparedStatement
Stored Procedures,Pre-defined database procedures,Call procedures with parameters
Input Sanitization,Remove dangerous characters,Strip shell metacharacters

## 2. Broken Authentication

**Risk Level**: Critical

### What is Broken Authentication?

Authentication mechanisms are often implemented incorrectly, allowing attackers to compromise passwords, keys, session tokens, or exploit implementation flaws to assume other users' identities.

### Common Authentication Vulnerabilities

auth_vulnerabilities[8]{vulnerability,description,impact}:
Weak Passwords,No complexity requirements,Easy brute force attacks
Credential Stuffing,Reused passwords from breaches,Account takeover
Session Fixation,Attacker sets session ID,Session hijacking
Session Hijacking,Stolen session tokens,Unauthorized access
Insecure Password Storage,Plaintext or weak hashing,Mass credential exposure
Missing MFA,Single factor authentication,Easy account compromise
Predictable Session IDs,Sequential or weak random,Session prediction
Long Session Timeouts,Sessions never expire,Extended unauthorized access

### Secure Password Hashing

**Python (bcrypt)**:
```python
import bcrypt
from typing import Tuple

class PasswordHasher:
    @staticmethod
    def hash_password(password: str, rounds: int = 12) -> str:
        """Hash password with bcrypt"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hashed: str, rounds: int = 12) -> bool:
        """Check if password needs rehashing with more rounds"""
        salt = hashed.encode('utf-8')
        return bcrypt.gensalt(rounds=rounds) != salt[:29]

# Usage
hasher = PasswordHasher()

# Registration
password_hash = hasher.hash_password("user_password_123")

# Login
is_valid = hasher.verify_password("user_password_123", password_hash)

# Check if rehashing needed (increase security over time)
if is_valid and hasher.needs_rehash(password_hash, rounds=14):
    new_hash = hasher.hash_password("user_password_123", rounds=14)
    # Update database with new_hash
```

**JavaScript/TypeScript (bcrypt)**:
```typescript
import bcrypt from 'bcrypt';

class PasswordHasher {
  private static readonly SALT_ROUNDS = 12;

  static async hashPassword(password: string): Promise<string> {
    if (password.length < 8) {
      throw new Error('Password must be at least 8 characters');
    }

    return await bcrypt.hash(password, this.SALT_ROUNDS);
  }

  static async verifyPassword(
    password: string,
    hash: string
  ): Promise<boolean> {
    try {
      return await bcrypt.compare(password, hash);
    } catch {
      return false;
    }
  }

  static async needsRehash(
    hash: string,
    newRounds: number = 14
  ): Promise<boolean> {
    const currentRounds = bcrypt.getRounds(hash);
    return currentRounds < newRounds;
  }
}

// Usage
const passwordHash = await PasswordHasher.hashPassword('user_password_123');
const isValid = await PasswordHasher.verifyPassword('user_password_123', passwordHash);

if (isValid && await PasswordHasher.needsRehash(passwordHash, 14)) {
  const newHash = await PasswordHasher.hashPassword('user_password_123');
  // Update database with newHash
}
```

### Secure JWT Implementation

**Python (PyJWT)**:
```python
import jwt
from datetime import datetime, timedelta
import secrets

class JWTManager:
    def __init__(self, secret_key: str, refresh_secret: str):
        self.secret_key = secret_key
        self.refresh_secret = refresh_secret
        self.algorithm = 'HS256'

    def generate_access_token(self, user_id: int, expires_in: int = 900) -> str:
        """Generate short-lived access token (15 minutes)"""
        payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: int, expires_in: int = 2592000) -> str:
        """Generate long-lived refresh token (30 days)"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)
        }
        return jwt.encode(payload, self.refresh_secret, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> dict:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError('Invalid token type')
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError('Token expired')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'Invalid token: {str(e)}')

    def verify_refresh_token(self, token: str) -> dict:
        """Verify and decode refresh token"""
        try:
            payload = jwt.decode(token, self.refresh_secret, algorithms=[self.algorithm])
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError('Refresh token expired')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'Invalid token: {str(e)}')

# Usage
jwt_manager = JWTManager(
    secret_key=os.environ['JWT_SECRET'],
    refresh_secret=os.environ['JWT_REFRESH_SECRET']
)

# Login - generate both tokens
access_token = jwt_manager.generate_access_token(user_id=123)
refresh_token = jwt_manager.generate_refresh_token(user_id=123)

# Verify access token
try:
    payload = jwt_manager.verify_access_token(access_token)
    user_id = payload['user_id']
except ValueError as e:
    # Handle invalid/expired token
    pass

# Refresh access token
try:
    payload = jwt_manager.verify_refresh_token(refresh_token)
    new_access_token = jwt_manager.generate_access_token(payload['user_id'])
except ValueError:
    # Refresh token invalid, require login
    pass
```

### Prevention Strategies

auth_prevention[10]{strategy,description}:
Strong Password Policy,Minimum 12 characters complexity requirements
Multi-Factor Authentication,TOTP SMS or hardware tokens
Secure Password Storage,bcrypt argon2 or scrypt with salt
Session Management,Secure random session IDs HttpOnly cookies
Token Expiration,Short-lived access tokens refresh tokens
Rate Limiting,Limit login attempts CAPTCHA after failures
Account Lockout,Temporary lockout after failed attempts
Secure Password Reset,Token-based reset with expiration
Audit Logging,Log all authentication events
Regular Security Review,Periodic review of auth mechanisms

## 3. Sensitive Data Exposure

**Risk Level**: High

### What is Sensitive Data Exposure?

Applications don't properly protect sensitive data such as financial, healthcare, or personally identifiable information (PII). Attackers may steal or modify such weakly protected data.

### Types of Sensitive Data

sensitive_data_types[8]{type,examples,protection_required}:
PII,Names addresses SSN,Encryption access control
Financial,Credit cards bank accounts,PCI-DSS compliance encryption
Healthcare,Medical records PHI,HIPAA compliance encryption
Authentication,Passwords tokens API keys,Hashing secure storage
Business,Trade secrets proprietary data,Access control encryption
Legal,Contracts legal documents,Access control audit trail
Technical,Source code database credentials,Secrets management access control
Communication,Private messages emails,End-to-end encryption

### Encryption at Rest

**Python (Fernet symmetric encryption)**:
```python
from cryptography.fernet import Fernet
import base64
import os

class DataEncryptor:
    def __init__(self, key: bytes = None):
        """Initialize with encryption key"""
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
        self.key = key

    @staticmethod
    def generate_key() -> bytes:
        """Generate new encryption key"""
        return Fernet.generate_key()

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        encrypted = self.cipher.encrypt(plaintext.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string"""
        decoded = base64.b64decode(ciphertext.encode('utf-8'))
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode('utf-8')

# Usage - Store key securely (environment variable or key management service)
encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    # First time - generate and save key securely
    encryption_key = base64.b64encode(DataEncryptor.generate_key()).decode()
    print(f"Save this key securely: {encryption_key}")

encryptor = DataEncryptor(base64.b64decode(encryption_key))

# Encrypt sensitive data before storing
sensitive_data = "123-45-6789"  # SSN
encrypted = encryptor.encrypt(sensitive_data)
# Store encrypted in database

# Decrypt when needed
decrypted = encryptor.decrypt(encrypted)
```

### Prevention Strategies

data_exposure_prevention[10]{strategy,description}:
Classify Data,Identify all sensitive data in system
Encrypt at Rest,Use AES-256 for stored data
Encrypt in Transit,Use TLS 1.3 or 1.2 minimum
Key Management,Use KMS or vault for keys
Minimize Storage,Don't store unnecessary sensitive data
Secure Deletion,Securely wipe deleted sensitive data
Access Control,Restrict access to sensitive data
Data Masking,Mask sensitive data in logs and UI
Secure Backup,Encrypt backups test restoration
Regular Audits,Audit data protection measures

## 4. XML External Entities (XXE)

**Risk Level**: High

### What is XXE?

Many older XML processors evaluate external entity references within XML documents. External entities can be used to disclose internal files, execute remote requests, scan internal ports, and execute remote code.

### Prevention

**Python (defusedxml)**:
```python
# ❌ VULNERABLE - Standard library
import xml.etree.ElementTree as ET
tree = ET.parse('untrusted.xml')  # Vulnerable to XXE

# ✅ SECURE - Use defusedxml
from defusedxml import ElementTree as DefusedET
tree = DefusedET.parse('untrusted.xml')  # Protected against XXE
```

**JavaScript (disable external entities)**:
```javascript
const libxmljs = require('libxmljs');

// ✅ SECURE - Disable external entities
const xmlDoc = libxmljs.parseXml(xmlString, {
  noent: false,  // Disable entity substitution
  nonet: true,   // Disable network access
  dtdload: false // Disable DTD loading
});
```

### XXE Prevention

xxe_prevention[6]{strategy,description}:
Disable External Entities,Configure parser to reject external entities
Use JSON Instead,Prefer JSON over XML for data exchange
Input Validation,Validate XML against strict schema
Whitelist Parsing,Only parse known safe XML structures
Update XML Libraries,Use latest versions with XXE protections
Least Privilege,XML parser runs with minimal permissions

## 5. Broken Access Control

**Risk Level**: Critical

### What is Broken Access Control?

Restrictions on what authenticated users are allowed to do are often not properly enforced. Attackers can exploit these flaws to access unauthorized functionality or data.

### Common Access Control Failures

access_control_failures[8]{failure,description,example}:
Insecure Direct Object Reference,Access objects by ID without authorization,/api/users/123 returns any user
Missing Function Level Control,No authorization on admin functions,Regular user accesses /admin/delete
Path Traversal,Access files outside allowed directory,../../etc/passwd
Privilege Escalation,User gains higher privileges,User modifies role in request
CORS Misconfiguration,Allows unauthorized cross-origin access,Access-Control-Allow-Origin: *
Force Browsing,Access pages without authentication,Direct URL access to /admin
Insecure ID Generation,Predictable resource IDs,Sequential user IDs
Missing Authorization,Endpoints lack authorization checks,API endpoint checks authentication only

### Secure Authorization Pattern

**Python (FastAPI)**:
```python
from fastapi import Depends, HTTPException, status
from functools import wraps

class AuthorizationService:
    @staticmethod
    def check_resource_owner(user_id: int, resource_user_id: int):
        """Verify user owns the resource"""
        if user_id != resource_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )

    @staticmethod
    def check_role(user_roles: list, required_role: str):
        """Verify user has required role"""
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}"
            )

# ✅ SECURE - Always check authorization
@app.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # Check if user can access this profile
    AuthorizationService.check_resource_owner(
        current_user.id,
        user_id
    )

    return await get_profile(user_id)

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # Check admin role required
    AuthorizationService.check_role(
        current_user.roles,
        "admin"
    )

    return await delete_user_account(user_id)
```

### Prevention Strategies

access_control_prevention[8]{strategy,description}:
Deny by Default,Require explicit authorization grants
Principle of Least Privilege,Minimum necessary permissions
Centralized Authorization,Single authorization service
Check on Every Request,Never cache authorization decisions
Use UUIDs,Non-sequential unpredictable IDs
Indirect Object References,Map user input to internal IDs
Log Access Control Failures,Monitor unauthorized access attempts
Regular Access Reviews,Periodic review of permissions

---

**Continued in next section due to length limits...**
