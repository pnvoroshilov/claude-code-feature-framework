# JWT Authentication - Secure Implementation

Complete guide to implementing secure JWT-based authentication with refresh tokens.

## JWT Token Structure

jwt_structure[3]{component,purpose,security_note}:
Header,Algorithm and token type,Use HS256 or RS256 never none
Payload,Claims and user data,Don't store sensitive data expiration required
Signature,Cryptographic signature,Strong secret minimum 256 bits

## Python Implementation (FastAPI)

**Complete JWT Service**:
```python
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class JWTManager:
    def __init__(self):
        self.access_secret = os.environ['JWT_ACCESS_SECRET']
        self.refresh_secret = os.environ['JWT_REFRESH_SECRET']
        self.algorithm = 'HS256'
        self.access_expire_minutes = 15
        self.refresh_expire_days = 30

        # Validate secrets
        if len(self.access_secret) < 32:
            raise ValueError("Access secret must be at least 32 characters")
        if len(self.refresh_secret) < 32:
            raise ValueError("Refresh secret must be at least 32 characters")

    def create_access_token(self, user_id: int, roles: list = None) -> str:
        """Create short-lived access token (15 minutes)"""
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(minutes=self.access_expire_minutes),
            'jti': secrets.token_urlsafe(16),
            'roles': roles or []
        }
        return jwt.encode(payload, self.access_secret, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        """Create long-lived refresh token (30 days)"""
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=self.refresh_expire_days),
            'jti': secrets.token_urlsafe(16)
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
                    'require': ['sub', 'type', 'exp', 'jti']
                }
            )

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
            raise ValueError('Refresh token expired - please log in again')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'Invalid refresh token: {str(e)}')

# Initialize
jwt_manager = JWTManager()
security = HTTPBearer()

# FastAPI app
app = FastAPI()

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Extract and verify user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt_manager.verify_access_token(token)
        user_id = int(payload['sub'])

        # Load user from database (implement your logic)
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Attach roles from token
        user['roles'] = payload.get('roles', [])
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

# Login endpoint
@app.post("/auth/login", response_model=TokenPair)
async def login(username: str, password: str):
    """Authenticate user and return tokens"""
    # Verify credentials (implement your logic)
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Generate tokens
    access_token = jwt_manager.create_access_token(
        user_id=user['id'],
        roles=user['roles']
    )
    refresh_token = jwt_manager.create_refresh_token(user_id=user['id'])

    # Store refresh token in database for revocation capability
    await store_refresh_token(user['id'], refresh_token)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=jwt_manager.access_expire_minutes * 60
    )

# Refresh endpoint
@app.post("/auth/refresh", response_model=TokenPair)
async def refresh_tokens(refresh_token: str):
    """Get new access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt_manager.verify_refresh_token(refresh_token)
        user_id = int(payload['sub'])

        # Check if refresh token is revoked (implement your logic)
        if await is_token_revoked(refresh_token):
            raise HTTPException(status_code=401, detail="Token revoked")

        # Load user and generate new tokens
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = jwt_manager.create_access_token(
            user_id=user['id'],
            roles=user['roles']
        )
        new_refresh_token = jwt_manager.create_refresh_token(user_id=user['id'])

        # Update refresh token in database
        await update_refresh_token(user_id, new_refresh_token)

        return TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=jwt_manager.access_expire_minutes * 60
        )

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Protected endpoint
@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Example protected endpoint"""
    return {
        'message': f'Hello {current_user["username"]}',
        'user_id': current_user['id'],
        'roles': current_user['roles']
    }

# Logout endpoint
@app.post("/auth/logout")
async def logout(
    refresh_token: str,
    current_user: dict = Depends(get_current_user)
):
    """Logout user and revoke refresh token"""
    # Revoke refresh token (implement your logic)
    await revoke_refresh_token(current_user['id'], refresh_token)

    return {'message': 'Logged out successfully'}
```

## TypeScript Implementation (Express)

**Complete JWT Service**:
```typescript
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

interface TokenPayload {
  sub: string;
  type: 'access' | 'refresh';
  iat: number;
  exp: number;
  jti: string;
  roles?: string[];
}

interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

class JWTManager {
  private accessSecret: string;
  private refreshSecret: string;
  private algorithm: jwt.Algorithm = 'HS256';
  private accessExpireMinutes = 15;
  private refreshExpireDays = 30;

  constructor() {
    this.accessSecret = process.env.JWT_ACCESS_SECRET!;
    this.refreshSecret = process.env.JWT_REFRESH_SECRET!;

    if (!this.accessSecret || this.accessSecret.length < 32) {
      throw new Error('Access secret must be at least 32 characters');
    }
    if (!this.refreshSecret || this.refreshSecret.length < 32) {
      throw new Error('Refresh secret must be at least 32 characters');
    }
  }

  createAccessToken(userId: number, roles: string[] = []): string {
    const now = Math.floor(Date.now() / 1000);
    const payload: TokenPayload = {
      sub: userId.toString(),
      type: 'access',
      iat: now,
      exp: now + this.accessExpireMinutes * 60,
      jti: crypto.randomBytes(16).toString('base64'),
      roles,
    };

    return jwt.sign(payload, this.accessSecret, { algorithm: this.algorithm });
  }

  createRefreshToken(userId: number): string {
    const now = Math.floor(Date.now() / 1000);
    const payload: Omit<TokenPayload, 'roles'> = {
      sub: userId.toString(),
      type: 'refresh',
      iat: now,
      exp: now + this.refreshExpireDays * 24 * 60 * 60,
      jti: crypto.randomBytes(16).toString('base64'),
    };

    return jwt.sign(payload, this.refreshSecret, { algorithm: this.algorithm });
  }

  verifyAccessToken(token: string): TokenPayload {
    try {
      const payload = jwt.verify(token, this.accessSecret, {
        algorithms: [this.algorithm],
      }) as TokenPayload;

      if (payload.type !== 'access') {
        throw new Error('Invalid token type');
      }

      return payload;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new Error('Token expired');
      }
      throw new Error('Invalid token');
    }
  }

  verifyRefreshToken(token: string): TokenPayload {
    try {
      const payload = jwt.verify(token, this.refreshSecret, {
        algorithms: [this.algorithm],
      }) as TokenPayload;

      if (payload.type !== 'refresh') {
        throw new Error('Invalid token type');
      }

      return payload;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new Error('Refresh token expired - please log in again');
      }
      throw new Error('Invalid refresh token');
    }
  }
}

// Initialize
const jwtManager = new JWTManager();

// Authentication middleware
export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const token = authHeader.substring(7);
    const payload = jwtManager.verifyAccessToken(token);
    const userId = parseInt(payload.sub);

    // Load user (implement your logic)
    const user = await getUserById(userId);
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    // Attach user and roles to request
    req.user = { ...user, roles: payload.roles || [] };
    next();
  } catch (error) {
    res.status(401).json({ error: error.message });
  }
};

// Routes
import express from 'express';
const app = express();

app.post('/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Verify credentials
    const user = await authenticateUser(username, password);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate tokens
    const accessToken = jwtManager.createAccessToken(user.id, user.roles);
    const refreshToken = jwtManager.createRefreshToken(user.id);

    // Store refresh token
    await storeRefreshToken(user.id, refreshToken);

    res.json({
      accessToken,
      refreshToken,
      tokenType: 'bearer',
      expiresIn: 900,
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/auth/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token required' });
    }

    // Verify refresh token
    const payload = jwtManager.verifyRefreshToken(refreshToken);
    const userId = parseInt(payload.sub);

    // Check if revoked
    if (await isTokenRevoked(refreshToken)) {
      return res.status(401).json({ error: 'Token revoked' });
    }

    // Load user
    const user = await getUserById(userId);
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    // Generate new tokens
    const newAccessToken = jwtManager.createAccessToken(user.id, user.roles);
    const newRefreshToken = jwtManager.createRefreshToken(user.id);

    // Update refresh token
    await updateRefreshToken(userId, newRefreshToken);

    res.json({
      accessToken: newAccessToken,
      refreshToken: newRefreshToken,
      tokenType: 'bearer',
      expiresIn: 900,
    });
  } catch (error) {
    res.status(401).json({ error: error.message });
  }
});

app.get('/protected', authenticate, (req, res) => {
  res.json({
    message: `Hello ${req.user.username}`,
    userId: req.user.id,
    roles: req.user.roles,
  });
});

app.post('/auth/logout', authenticate, async (req, res) => {
  try {
    const { refreshToken } = req.body;
    await revokeRefreshToken(req.user.id, refreshToken);
    res.json({ message: 'Logged out successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

## JWT Best Practices

jwt_best_practices[12]{practice,implementation}:
Short Expiration,Access tokens 15-30 minutes maximum
Refresh Tokens,Long-lived tokens for obtaining new access tokens
Strong Secrets,Minimum 256-bit random secrets use crypto.randomBytes
Separate Secrets,Different secrets for access and refresh tokens
Token Type Claim,Include type claim to prevent token confusion
Unique Token ID,Include jti claim for revocation and tracking
Algorithm Whitelist,Only HS256 or RS256 never allow none
HTTPS Only,Never transmit tokens over HTTP
Secure Storage,HttpOnly cookies or secure client storage
Token Revocation,Maintain blacklist or use short expiration
Validate All Claims,Check exp iat sub type aud iss
Rotate Secrets,Periodic secret rotation strategy

## Common Mistakes

jwt_mistakes[8]{mistake,why_dangerous,correct_approach}:
Long Expiration,Extended exposure if token stolen,15-30 minutes for access tokens
Weak Secrets,Tokens can be forged,Minimum 256-bit random secret
Storing Sensitive Data,JWT payload is base64 not encrypted,Store only user ID and non-sensitive claims
No Token Revocation,Cannot invalidate compromised tokens,Implement token blacklist or short expiration
Client-side Validation Only,Attacker can modify token,Always verify on server
Accepting none Algorithm,Allows unsigned tokens,Whitelist only HS256 RS256
Not Checking Token Type,Refresh token used as access token,Validate type claim
Exposing Tokens in URL,Tokens logged in server logs,Use Authorization header only

---

**Remember**: JWT tokens are credentials. Protect them like passwords with short expiration, secure storage, and HTTPS-only transmission.
