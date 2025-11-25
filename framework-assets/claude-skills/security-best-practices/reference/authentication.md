# Authentication Patterns - Complete Guide

Comprehensive guide to authentication mechanisms, implementation patterns, and security best practices for modern applications.

## Authentication Overview

Authentication verifies the identity of a user, device, or system. This guide covers modern authentication patterns from basic to advanced implementations.

## Authentication Methods Comparison

auth_methods[8]{method,security,complexity,use_case,pros,cons}:
Password-based,Medium,Low,Traditional web apps,Simple to implement,Vulnerable to breaches phishing
JWT Tokens,High,Medium,SPAs APIs microservices,Stateless scalable,Token theft risk
OAuth 2.0,Very High,High,Third-party auth SSO,Industry standard secure,Complex implementation
Session Cookies,High,Medium,Server-rendered apps,Simple secure with HttpOnly,Requires server state
API Keys,Medium,Low,Service-to-service public APIs,Simple for automation,Key leakage risk
Certificate-based,Very High,High,Enterprise mTLS,Strong cryptographic security,Complex infrastructure
Biometric,Very High,High,Mobile apps high-security,User-friendly strong,Privacy concerns cost
Passwordless (Magic links OTP),High,Medium,Consumer apps,Improved UX no passwords,Requires email/SMS access

## 1. Password-Based Authentication

### Secure Password Requirements

password_requirements[8]{requirement,specification,rationale}:
Minimum Length,12 characters or more,Resist brute force attacks
Character Diversity,Mix of upper lower digits symbols,Increase entropy
No Common Passwords,Check against breach databases,Prevent credential stuffing
Password History,Prevent reuse of last 10 passwords,Reduce breach impact
Expiration Policy,90-180 days for high security,Limit exposure window
Account Lockout,5 failed attempts then lockout,Prevent brute force
Complexity Without Frustration,Passphrases over complex rules,Balance security and usability
Breach Detection,Check HaveIBeenPwned database,Proactive breach response

### Secure Password Hashing - bcrypt

**Python Implementation**:
```python
import bcrypt
from typing import Tuple
import re

class PasswordService:
    SALT_ROUNDS = 12  # Cost factor (higher = more secure but slower)

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < 12:
            return False, "Password must be at least 12 characters"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"

        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"

        if not re.search(r'\d', password):
            return False, "Password must contain digit"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"

        # Check against common passwords
        common_passwords = ['Password123!', 'Welcome123!', 'Admin123!']
        if password in common_passwords:
            return False, "Password is too common"

        return True, "Password is strong"

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password with bcrypt"""
        is_valid, message = cls.validate_password_strength(password)
        if not is_valid:
            raise ValueError(message)

        salt = bcrypt.gensalt(rounds=cls.SALT_ROUNDS)
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
        except Exception as e:
            # Log error but don't reveal details
            print(f"Password verification error: {e}")
            return False

    @classmethod
    def needs_rehash(cls, hashed: str) -> bool:
        """Check if hash should be updated with more rounds"""
        try:
            current_rounds = int(hashed.split('$')[2])
            return current_rounds < cls.SALT_ROUNDS
        except:
            return True  # Rehash if can't determine rounds

# Usage Example
service = PasswordService()

# Registration
try:
    password_hash = service.hash_password("SecureP@ssw0rd123")
    # Store password_hash in database
except ValueError as e:
    print(f"Weak password: {e}")

# Login
is_authenticated = service.verify_password("SecureP@ssw0rd123", password_hash)

# Upgrade security - increase rounds over time
if is_authenticated and service.needs_rehash(password_hash):
    new_hash = service.hash_password("SecureP@ssw0rd123")
    # Update database with new_hash
```

**TypeScript Implementation**:
```typescript
import bcrypt from 'bcrypt';
import { promisify } from 'util';

interface PasswordValidationResult {
  isValid: boolean;
  message: string;
}

class PasswordService {
  private static readonly SALT_ROUNDS = 12;

  static validatePasswordStrength(password: string): PasswordValidationResult {
    if (password.length < 12) {
      return {
        isValid: false,
        message: 'Password must be at least 12 characters',
      };
    }

    if (!/[A-Z]/.test(password)) {
      return {
        isValid: false,
        message: 'Password must contain uppercase letter',
      };
    }

    if (!/[a-z]/.test(password)) {
      return {
        isValid: false,
        message: 'Password must contain lowercase letter',
      };
    }

    if (!/\d/.test(password)) {
      return { isValid: false, message: 'Password must contain digit' };
    }

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      return {
        isValid: false,
        message: 'Password must contain special character',
      };
    }

    const commonPasswords = ['Password123!', 'Welcome123!', 'Admin123!'];
    if (commonPasswords.includes(password)) {
      return { isValid: false, message: 'Password is too common' };
    }

    return { isValid: true, message: 'Password is strong' };
  }

  static async hashPassword(password: string): Promise<string> {
    const validation = this.validatePasswordStrength(password);
    if (!validation.isValid) {
      throw new Error(validation.message);
    }

    return await bcrypt.hash(password, this.SALT_ROUNDS);
  }

  static async verifyPassword(
    password: string,
    hash: string
  ): Promise<boolean> {
    try {
      return await bcrypt.compare(password, hash);
    } catch (error) {
      console.error('Password verification error:', error);
      return false;
    }
  }

  static needsRehash(hash: string): boolean {
    try {
      const currentRounds = bcrypt.getRounds(hash);
      return currentRounds < this.SALT_ROUNDS;
    } catch {
      return true; // Rehash if can't determine rounds
    }
  }
}

// Usage Example
async function example() {
  try {
    const passwordHash = await PasswordService.hashPassword('SecureP@ssw0rd123');
    // Store passwordHash in database
  } catch (error) {
    console.error('Weak password:', error.message);
  }

  // Login
  const isAuthenticated = await PasswordService.verifyPassword(
    'SecureP@ssw0rd123',
    passwordHash
  );

  // Upgrade security
  if (isAuthenticated && PasswordService.needsRehash(passwordHash)) {
    const newHash = await PasswordService.hashPassword('SecureP@ssw0rd123');
    // Update database with newHash
  }
}
```

## 2. JWT Token Authentication

### JWT Structure and Security

jwt_components[3]{component,purpose,security_note}:
Header,Algorithm and token type,Never use 'none' algorithm
Payload,Claims (user info permissions),Don't store sensitive data
Signature,Cryptographic signature,Use strong secret minimum 256 bits

### Secure JWT Implementation

**Python (PyJWT + FastAPI)**:
```python
import jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTService:
    def __init__(
        self,
        access_secret: str,
        refresh_secret: str,
        algorithm: str = 'HS256'
    ):
        if len(access_secret) < 32:
            raise ValueError("Access secret must be at least 32 characters")
        if len(refresh_secret) < 32:
            raise ValueError("Refresh secret must be at least 32 characters")

        self.access_secret = access_secret
        self.refresh_secret = refresh_secret
        self.algorithm = algorithm

    def create_access_token(
        self,
        user_id: int,
        additional_claims: dict = None,
        expires_minutes: int = 15
    ) -> str:
        """Create short-lived access token"""
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),  # Subject (user ID)
            'type': 'access',
            'iat': now,  # Issued at
            'exp': now + timedelta(minutes=expires_minutes),  # Expiration
            'jti': secrets.token_urlsafe(16),  # JWT ID (unique)
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.access_secret, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        user_id: int,
        expires_days: int = 30
    ) -> str:
        """Create long-lived refresh token"""
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=expires_days),
            'jti': secrets.token_urlsafe(16),
        }

        return jwt.encode(payload, self.refresh_secret, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> dict:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(
                token,
                self.access_secret,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'require': ['sub', 'type', 'exp', 'iat', 'jti']
                }
            )

            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError('Invalid token type')

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'Invalid token: {str(e)}')

    def verify_refresh_token(self, token: str) -> dict:
        """Verify and decode refresh token"""
        try:
            payload = jwt.decode(
                token,
                self.refresh_secret,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'require': ['sub', 'type', 'exp', 'jti']
                }
            )

            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError('Refresh token has expired')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'Invalid token: {str(e)}')

    def refresh_access_token(self, refresh_token: str) -> str:
        """Generate new access token from refresh token"""
        payload = self.verify_refresh_token(refresh_token)
        user_id = int(payload['sub'])
        return self.create_access_token(user_id)

# FastAPI Integration
jwt_service = JWTService(
    access_secret=os.environ['JWT_ACCESS_SECRET'],
    refresh_secret=os.environ['JWT_REFRESH_SECRET']
)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt_service.verify_access_token(token)
        user_id = int(payload['sub'])

        # Load user from database
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Usage in endpoints
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    """Login and return tokens"""
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = jwt_service.create_access_token(
        user.id,
        additional_claims={'roles': user.roles}
    )
    refresh_token = jwt_service.create_refresh_token(user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'expires_in': 900  # 15 minutes
    }

@app.post("/auth/refresh")
async def refresh(refresh_token: str):
    """Refresh access token"""
    try:
        new_access_token = jwt_service.refresh_access_token(refresh_token)
        return {
            'access_token': new_access_token,
            'token_type': 'bearer',
            'expires_in': 900
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Protected endpoint requiring authentication"""
    return {'message': f'Hello {current_user["username"]}'}
```

### JWT Best Practices

jwt_best_practices[12]{practice,rationale}:
Short Expiration,Limit access token to 15-30 minutes
Use Refresh Tokens,Long-lived refresh tokens for new access tokens
Strong Secrets,Minimum 256-bit random secrets
Algorithm Whitelist,Only allow HS256 RS256 never none
Token Revocation,Maintain blacklist or use short expiration
HTTPS Only,Never transmit tokens over HTTP
Secure Storage,HttpOnly cookies or secure storage APIs
Validate All Claims,Check exp iat nbf sub aud iss
Unique Token ID,Include jti claim for tracking revocation
Separate Secrets,Different secrets for access and refresh
Limit Payload Size,Keep claims minimal avoid sensitive data
Rotate Secrets,Periodic secret rotation strategy

## 3. OAuth 2.0 / OpenID Connect

### OAuth 2.0 Flows

oauth_flows[4]{flow,use_case,security,complexity}:
Authorization Code,Web apps with backend,High - most secure,Medium
Implicit Flow,DEPRECATED - use Authorization Code,Low - insecure,Low
Client Credentials,Service-to-service,High,Low
Resource Owner Password,DEPRECATED - use other flows,Low,Low

### Authorization Code Flow Implementation

**Python (with authlib)**:
```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# OAuth Configuration
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.get('/login')
async def login(request: Request):
    """Initiate OAuth login"""
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/callback')
async def auth_callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        # Create or update user in database
        user = await create_or_update_user(
            email=user_info['email'],
            name=user_info['name'],
            picture=user_info.get('picture')
        )

        # Create session or JWT
        access_token = jwt_service.create_access_token(user.id)

        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'user': user
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 4. Session-Based Authentication

### Secure Session Management

**Python (FastAPI with sessions)**:
```python
from starlette.middleware.sessions import SessionMiddleware
import secrets

app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    session_cookie='session',
    max_age=3600,  # 1 hour
    same_site='lax',
    https_only=True
)

@app.post("/login")
async def login(credentials: LoginRequest, request: Request):
    """Create session on login"""
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    request.session['roles'] = user.roles

    return {'message': 'Logged in successfully'}

@app.get("/protected")
async def protected(request: Request):
    """Protected route checking session"""
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {'user_id': user_id}

@app.post("/logout")
async def logout(request: Request):
    """Clear session on logout"""
    request.session.clear()
    return {'message': 'Logged out successfully'}
```

### Session Security Configuration

session_security[10]{setting,value,purpose}:
HttpOnly,True,Prevent JavaScript access
Secure,True,HTTPS only transmission
SameSite,Lax or Strict,CSRF protection
Max-Age,3600-86400 seconds,Limit exposure window
Path,/ or specific path,Limit cookie scope
Domain,Specific domain only,Prevent subdomain attacks
Session ID Length,128+ bits,Prevent session prediction
Session Regeneration,On privilege change,Prevent session fixation
Idle Timeout,15-30 minutes,Auto logout inactive users
Absolute Timeout,8-24 hours,Force re-authentication

## 5. Multi-Factor Authentication (MFA)

### TOTP Implementation

**Python (pyotp)**:
```python
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAService:
    @staticmethod
    def generate_secret() -> str:
        """Generate new TOTP secret"""
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(secret: str, username: str, issuer: str) -> str:
        """Generate TOTP URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)

    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """Generate QR code as base64 image"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 interval drift

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """Generate backup codes"""
        return [secrets.token_hex(4) for _ in range(count)]

# Usage
@app.post("/mfa/enable")
async def enable_mfa(current_user: User = Depends(get_current_user)):
    """Enable MFA for user"""
    secret = MFAService.generate_secret()
    uri = MFAService.get_totp_uri(secret, current_user.email, "MyApp")
    qr_code = MFAService.generate_qr_code(uri)
    backup_codes = MFAService.generate_backup_codes()

    # Store secret and backup codes (hashed) in database
    await store_mfa_secret(current_user.id, secret, backup_codes)

    return {
        'secret': secret,
        'qr_code': qr_code,
        'backup_codes': backup_codes
    }

@app.post("/mfa/verify")
async def verify_mfa(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """Verify MFA token"""
    secret = await get_mfa_secret(current_user.id)
    if not secret:
        raise HTTPException(status_code=400, detail="MFA not enabled")

    is_valid = MFAService.verify_totp(secret, token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid MFA token")

    return {'message': 'MFA verified successfully'}
```

---

**For more authentication patterns, see examples directory.**
