# Input Validation - Complete Guide

Comprehensive guide to input validation and sanitization techniques for preventing injection attacks and ensuring data integrity.

## Input Validation Principles

validation_principles[8]{principle,description}:
Whitelist Over Blacklist,Define what is allowed not what is forbidden
Validate Early,Validate at entry points before processing
Fail Securely,Reject invalid input don't try to fix
Context-Specific,Different validation for different contexts
Centralized Validation,Reusable validation functions
Type Safety,Use strong typing and schemas
Length Limits,Always enforce maximum lengths
Canonical Form,Convert to standard format before validation

## Validation Layers

validation_layers[5]{layer,purpose,example}:
Syntax Validation,Check format structure,Email regex phone format
Semantic Validation,Check logical correctness,Date ranges business rules
Schema Validation,Validate against data model,JSON schema Pydantic
Business Rule Validation,Domain-specific rules,Credit limit age requirements
Context Validation,Check request context,Authorization rate limits

## 1. String Validation

### Email Validation

**Python**:
```python
import re
from typing import Optional

class EmailValidator:
    # Comprehensive email regex (RFC 5322 compliant)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @classmethod
    def validate(cls, email: str) -> tuple[bool, Optional[str]]:
        """Validate email format"""
        if not email:
            return False, "Email is required"

        if len(email) > 320:  # RFC 5321 limit
            return False, "Email too long (max 320 characters)"

        if not cls.EMAIL_REGEX.match(email):
            return False, "Invalid email format"

        # Additional checks
        local, domain = email.rsplit('@', 1)

        if len(local) > 64:  # RFC 5321 limit
            return False, "Email local part too long (max 64 characters)"

        if len(domain) > 255:  # RFC 5321 limit
            return False, "Email domain too long (max 255 characters)"

        # Check for consecutive dots
        if '..' in email:
            return False, "Email cannot contain consecutive dots"

        return True, None

# Usage
is_valid, error = EmailValidator.validate("user@example.com")
```

**TypeScript**:
```typescript
class EmailValidator {
  private static readonly EMAIL_REGEX =
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  private static readonly MAX_LENGTH = 320;
  private static readonly MAX_LOCAL_LENGTH = 64;
  private static readonly MAX_DOMAIN_LENGTH = 255;

  static validate(email: string): { isValid: boolean; error?: string } {
    if (!email) {
      return { isValid: false, error: 'Email is required' };
    }

    if (email.length > this.MAX_LENGTH) {
      return { isValid: false, error: 'Email too long (max 320 characters)' };
    }

    if (!this.EMAIL_REGEX.test(email)) {
      return { isValid: false, error: 'Invalid email format' };
    }

    const [local, domain] = email.split('@');

    if (local.length > this.MAX_LOCAL_LENGTH) {
      return {
        isValid: false,
        error: 'Email local part too long (max 64 characters)',
      };
    }

    if (domain.length > this.MAX_DOMAIN_LENGTH) {
      return {
        isValid: false,
        error: 'Email domain too long (max 255 characters)',
      };
    }

    if (email.includes('..')) {
      return { isValid: false, error: 'Email cannot contain consecutive dots' };
    }

    return { isValid: true };
  }
}
```

### URL Validation

**Python**:
```python
from urllib.parse import urlparse
from typing import Optional

class URLValidator:
    ALLOWED_SCHEMES = {'http', 'https'}
    BLOCKED_DOMAINS = {'localhost', '127.0.0.1', '0.0.0.0'}

    @classmethod
    def validate(
        cls,
        url: str,
        require_https: bool = False
    ) -> tuple[bool, Optional[str]]:
        """Validate URL format and safety"""
        if not url:
            return False, "URL is required"

        if len(url) > 2048:  # Common browser limit
            return False, "URL too long (max 2048 characters)"

        try:
            parsed = urlparse(url)
        except Exception:
            return False, "Invalid URL format"

        # Check scheme
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            return False, f"URL scheme must be {' or '.join(cls.ALLOWED_SCHEMES)}"

        if require_https and parsed.scheme != 'https':
            return False, "HTTPS is required"

        # Check domain
        if not parsed.netloc:
            return False, "URL must have a domain"

        hostname = parsed.hostname or parsed.netloc
        if hostname in cls.BLOCKED_DOMAINS:
            return False, "URL domain is not allowed"

        # Prevent SSRF - check for private IPs
        if cls._is_private_ip(hostname):
            return False, "Private IP addresses are not allowed"

        return True, None

    @staticmethod
    def _is_private_ip(hostname: str) -> bool:
        """Check if hostname is a private IP"""
        import ipaddress
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            return False

# Usage
is_valid, error = URLValidator.validate("https://example.com", require_https=True)
```

### Phone Number Validation

**Python**:
```python
import re

class PhoneValidator:
    # E.164 format: +[country code][number]
    E164_REGEX = re.compile(r'^\+[1-9]\d{1,14}$')

    @classmethod
    def validate(cls, phone: str) -> tuple[bool, Optional[str]]:
        """Validate phone number in E.164 format"""
        if not phone:
            return False, "Phone number is required"

        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        if not cleaned.startswith('+'):
            return False, "Phone must start with + and country code"

        if not cls.E164_REGEX.match(cleaned):
            return False, "Invalid phone number format (use E.164: +1234567890)"

        return True, None

    @staticmethod
    def normalize(phone: str) -> str:
        """Normalize phone to E.164 format"""
        return re.sub(r'[\s\-\(\)]', '', phone)
```

## 2. Numeric Validation

**Python**:
```python
from typing import Optional, Union

class NumericValidator:
    @staticmethod
    def validate_integer(
        value: Union[int, str],
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> tuple[bool, Optional[str], Optional[int]]:
        """Validate integer with optional range"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, "Must be a valid integer", None

        if min_value is not None and int_value < min_value:
            return False, f"Must be at least {min_value}", None

        if max_value is not None and int_value > max_value:
            return False, f"Must be at most {max_value}", None

        return True, None, int_value

    @staticmethod
    def validate_float(
        value: Union[float, str],
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        decimals: Optional[int] = None
    ) -> tuple[bool, Optional[str], Optional[float]]:
        """Validate float with optional range and precision"""
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, "Must be a valid number", None

        if min_value is not None and float_value < min_value:
            return False, f"Must be at least {min_value}", None

        if max_value is not None and float_value > max_value:
            return False, f"Must be at most {max_value}", None

        if decimals is not None:
            rounded = round(float_value, decimals)
            if rounded != float_value:
                return False, f"Maximum {decimals} decimal places allowed", None

        return True, None, float_value

# Usage
is_valid, error, value = NumericValidator.validate_integer("42", min_value=0, max_value=100)
```

## 3. Schema Validation

### Pydantic Models (Python)

**Python**:
```python
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    age: int = Field(..., ge=18, le=120)
    phone: Optional[str] = Field(None, regex=r'^\+[1-9]\d{1,14}$')
    website: Optional[str] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        """Ensure username is alphanumeric with underscores"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric with underscores')
        return v

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '!@#$%^&*()' for c in v):
            raise ValueError('Password must contain special character')
        return v

    @validator('website')
    def validate_website(cls, v):
        """Validate website URL"""
        if v is None:
            return v

        from urllib.parse import urlparse
        try:
            result = urlparse(v)
            if result.scheme not in ('http', 'https'):
                raise ValueError('Website must be HTTP or HTTPS')
            if not result.netloc:
                raise ValueError('Website must have a valid domain')
        except Exception:
            raise ValueError('Invalid website URL')
        return v

    class Config:
        # Additional validation config
        anystr_strip_whitespace = True
        max_anystr_length = 1000

# Usage with FastAPI
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/users")
async def create_user(user: CreateUserRequest):
    """Create user - automatic validation"""
    # If we reach here, validation passed
    return {"message": "User created", "username": user.username}
```

### Zod Schema (TypeScript)

**TypeScript**:
```typescript
import { z } from 'zod';

// Define schema
const CreateUserSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be at most 50 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username must be alphanumeric with underscores'),

  email: z.string().email('Invalid email format'),

  password: z
    .string()
    .min(12, 'Password must be at least 12 characters')
    .max(128, 'Password must be at most 128 characters')
    .refine((val) => /[A-Z]/.test(val), 'Password must contain uppercase letter')
    .refine((val) => /[a-z]/.test(val), 'Password must contain lowercase letter')
    .refine((val) => /\d/.test(val), 'Password must contain digit')
    .refine(
      (val) => /[!@#$%^&*()]/.test(val),
      'Password must contain special character'
    ),

  age: z
    .number()
    .int('Age must be an integer')
    .min(18, 'Must be at least 18 years old')
    .max(120, 'Invalid age'),

  phone: z
    .string()
    .regex(/^\+[1-9]\d{1,14}$/, 'Phone must be in E.164 format')
    .optional(),

  website: z
    .string()
    .url('Invalid website URL')
    .refine(
      (val) => val.startsWith('http://') || val.startsWith('https://'),
      'Website must be HTTP or HTTPS'
    )
    .optional(),
});

type CreateUserRequest = z.infer<typeof CreateUserSchema>;

// Usage with Express
import express from 'express';

app.post('/users', async (req, res) => {
  try {
    const validatedData = CreateUserSchema.parse(req.body);

    // Data is validated, proceed with creation
    res.json({ message: 'User created', username: validatedData.username });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.errors,
      });
    }
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

## 4. File Upload Validation

**Python (FastAPI)**:
```python
from fastapi import UploadFile, HTTPException
from typing import Set
import magic  # python-magic library

class FileValidator:
    ALLOWED_EXTENSIONS: Set[str] = {'jpg', 'jpeg', 'png', 'pdf', 'txt'}
    ALLOWED_MIME_TYPES: Set[str] = {
        'image/jpeg',
        'image/png',
        'application/pdf',
        'text/plain'
    }
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

    @classmethod
    async def validate_upload(cls, file: UploadFile) -> tuple[bool, Optional[str]]:
        """Comprehensive file upload validation"""

        # Check filename
        if not file.filename:
            return False, "Filename is required"

        # Validate extension
        extension = file.filename.rsplit('.', 1)[-1].lower()
        if extension not in cls.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"

        # Read file content for validation
        content = await file.read()
        await file.seek(0)  # Reset for later use

        # Check file size
        file_size = len(content)
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File too large (max {cls.MAX_FILE_SIZE // 1024 // 1024} MB)"

        if file_size == 0:
            return False, "File is empty"

        # Validate actual MIME type (not just extension)
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in cls.ALLOWED_MIME_TYPES:
            return False, f"Invalid file type detected: {mime_type}"

        # Additional checks for images
        if mime_type.startswith('image/'):
            if not cls._validate_image(content):
                return False, "Invalid or corrupted image file"

        return True, None

    @staticmethod
    def _validate_image(content: bytes) -> bool:
        """Validate image file"""
        try:
            from PIL import Image
            from io import BytesIO

            img = Image.open(BytesIO(content))
            img.verify()  # Verify it's actually an image
            return True
        except Exception:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        import re
        import os

        # Remove path separators
        filename = os.path.basename(filename)

        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)

        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]

        return f"{name}{ext}"

# Usage
@app.post("/upload")
async def upload_file(file: UploadFile):
    """Upload file with validation"""
    is_valid, error = await FileValidator.validate_upload(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Sanitize filename
    safe_filename = FileValidator.sanitize_filename(file.filename)

    # Save file
    # ... save logic here

    return {"filename": safe_filename, "message": "File uploaded successfully"}
```

## 5. SQL Injection Prevention

**Always use parameterized queries**:

```python
# ❌ VULNERABLE - String concatenation
def get_user_vulnerable(username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ SECURE - Parameterized query
def get_user_secure(username: str):
    query = "SELECT * FROM users WHERE username = :username"
    return db.execute(query, {"username": username})

# ✅ SECURE - ORM
def get_user_orm(username: str):
    return db.query(User).filter_by(username=username).first()
```

## 6. Command Injection Prevention

**Never use shell=True with user input**:

```python
import subprocess
import shlex

# ❌ VULNERABLE
def ping_vulnerable(host: str):
    os.system(f"ping -c 1 {host}")

# ✅ SECURE - Use subprocess with list
def ping_secure(host: str):
    # Validate hostname first
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        raise ValueError("Invalid hostname")

    subprocess.run(['ping', '-c', '1', host], check=True, shell=False)

# ✅ BETTER - Use library instead
import ping3
def ping_library(host: str):
    return ping3.ping(host)
```

## 7. Path Traversal Prevention

**Python**:
```python
import os
from pathlib import Path

class PathValidator:
    def __init__(self, base_directory: str):
        self.base_dir = Path(base_directory).resolve()

    def validate_path(self, user_path: str) -> tuple[bool, Optional[str], Optional[Path]]:
        """Validate path is within allowed directory"""
        try:
            # Resolve to absolute path
            requested_path = (self.base_dir / user_path).resolve()

            # Check if path is within base directory
            if not requested_path.is_relative_to(self.base_dir):
                return False, "Access denied: path outside allowed directory", None

            # Check file exists
            if not requested_path.exists():
                return False, "File not found", None

            # Check it's a file not directory
            if not requested_path.is_file():
                return False, "Not a file", None

            return True, None, requested_path

        except Exception as e:
            return False, f"Invalid path: {str(e)}", None

# Usage
validator = PathValidator('/var/www/uploads')
is_valid, error, safe_path = validator.validate_path('../../../etc/passwd')
# Returns: (False, "Access denied: path outside allowed directory", None)
```

## Input Validation Checklist

validation_checklist[15]{check,description}:
Type Validation,Verify data type matches expected
Length Validation,Enforce min and max lengths
Format Validation,Check format with regex or parser
Range Validation,Verify numeric ranges
Whitelist Validation,Allow only known good values
Encoding Validation,Check character encoding
Sanitization,Remove or escape dangerous characters
Canonicalization,Convert to standard format
Business Rules,Apply domain-specific rules
Cross-Field Validation,Validate relationships between fields
File Upload Validation,Check extension MIME type and content
Path Validation,Prevent directory traversal
SQL Injection Prevention,Use parameterized queries
Command Injection Prevention,Avoid shell commands with user input
XSS Prevention,Encode output context-specific

---

**For practical examples, see the examples directory.**
