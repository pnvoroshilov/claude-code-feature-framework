---
name: security-best-practices
description: Comprehensive security best practices skill covering OWASP Top 10, secure coding patterns, authentication/authorization, input validation, encryption, and security auditing. Use when implementing security measures, reviewing code for vulnerabilities, or hardening applications.
version: 1.0.0
tags: [security, owasp, authentication, encryption, vulnerabilities, secure-coding, auditing]
---

# Security Best Practices Skill

Comprehensive guide to information security best practices, covering OWASP Top 10 vulnerabilities, secure coding patterns, authentication/authorization, input validation, encryption, and security auditing for building secure applications.

## Overview

This skill provides expert-level knowledge in application security, from identifying and preventing common vulnerabilities to implementing defense-in-depth strategies. It covers both offensive security (understanding attacks) and defensive security (implementing protections).

## When to Use This Skill

Use this skill when you need to:

trigger_scenarios[12]{scenario,description}:
Security vulnerabilities,Identify and fix SQL injection XSS CSRF and other vulnerabilities
Secure coding review,Review code for security issues before deployment
Authentication setup,Implement secure authentication with JWT OAuth or sessions
Authorization design,Design and implement RBAC ABAC or custom authorization
Input validation,Validate and sanitize user inputs to prevent injection attacks
Encryption implementation,Add encryption for data at rest and in transit
Security headers,Configure security headers CSP CORS HSTS properly
Password management,Implement secure password hashing and storage
API security,Secure REST or GraphQL APIs against common attacks
Security audit prep,Prepare codebase for security audit or pen testing
Incident response,Setup logging monitoring and incident response
Compliance requirements,Meet security compliance standards like OWASP PCI-DSS

## Quick Start: Common Security Tasks

### SQL Injection Prevention

**Python (with SQLAlchemy)**:
```python
from sqlalchemy import text

# ❌ VULNERABLE - Never use string formatting
def get_user_vulnerable(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ SECURE - Use parameterized queries
def get_user_secure(username):
    query = text("SELECT * FROM users WHERE username = :username")
    return db.execute(query, {"username": username})
```

**JavaScript/TypeScript (with PostgreSQL)**:
```typescript
// ❌ VULNERABLE
async function getUserVulnerable(username: string) {
  const query = `SELECT * FROM users WHERE username = '${username}'`;
  return await db.query(query);
}

// ✅ SECURE - Use parameterized queries
async function getUserSecure(username: string) {
  const query = 'SELECT * FROM users WHERE username = $1';
  return await db.query(query, [username]);
}
```

### XSS Prevention

**React/JavaScript**:
```typescript
// ✅ React automatically escapes content
function UserProfile({ username }) {
  return <div>{username}</div>;  // Safe by default
}

// ❌ DANGEROUS - Using dangerouslySetInnerHTML
function UnsafeProfile({ htmlContent }) {
  return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
}

// ✅ SAFE - Sanitize before rendering
import DOMPurify from 'dompurify';

function SafeProfile({ htmlContent }) {
  const sanitized = DOMPurify.sanitize(htmlContent);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### Password Hashing

**Python (bcrypt)**:
```python
import bcrypt

# Hash password on registration
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Verify password on login
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

**JavaScript/TypeScript (bcrypt)**:
```typescript
import bcrypt from 'bcrypt';

// Hash password on registration
async function hashPassword(password: string): Promise<string> {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
}

// Verify password on login
async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(password, hash);
}
```

## Core Capabilities

This skill provides comprehensive knowledge in:

### 1. OWASP Top 10 Prevention

owasp_top_10[10]{vulnerability,risk_level,primary_defense}:
Injection (SQL Command LDAP),Critical,Parameterized queries input validation
Broken Authentication,Critical,MFA secure session management JWT best practices
Sensitive Data Exposure,High,Encryption at rest and transit key management
XML External Entities (XXE),High,Disable external entity processing input validation
Broken Access Control,Critical,RBAC principle of least privilege enforce authorization
Security Misconfiguration,High,Secure defaults disable debug modes security headers
Cross-Site Scripting (XSS),High,Output encoding CSP headers input sanitization
Insecure Deserialization,High,Integrity checks avoid native deserialization validate inputs
Using Components with Known Vulnerabilities,High,Dependency scanning automated updates SCA tools
Insufficient Logging and Monitoring,Medium,Comprehensive logging SIEM integration alerting

### 2. Secure Coding Patterns

secure_patterns[8]{pattern,description,use_case}:
Input Validation,Whitelist validation at boundaries,All user inputs file uploads API requests
Output Encoding,Context-aware encoding before rendering,HTML JavaScript SQL contexts
Parameterized Queries,Separate SQL code from data,All database operations
Error Handling,Generic errors to users detailed logs internally,Exception handling API responses
Principle of Least Privilege,Minimum necessary permissions,Database access file operations
Defense in Depth,Multiple security layers,Network application data layers
Secure Defaults,Secure by default configuration,New projects frameworks libraries
Fail Securely,Fail to secure state on errors,Authentication authorization critical operations

### 3. Authentication and Authorization

auth_mechanisms[7]{type,security_level,use_case}:
JWT with Refresh Tokens,High,Modern SPAs mobile apps microservices
OAuth 2.0 / OpenID Connect,Very High,Third-party authentication SSO enterprise apps
API Keys with Rate Limiting,Medium,Public APIs service-to-service
Session-based with HttpOnly Cookies,High,Traditional web apps server-side rendering
Multi-Factor Authentication (MFA),Very High,High-security applications admin panels
Certificate-based Authentication,Very High,Service-to-service mTLS
Passwordless (Magic Links OTP),High,Consumer applications improved UX

### 4. Encryption and Data Protection

encryption_types[6]{type,algorithm,use_case}:
Password Hashing,bcrypt argon2 scrypt,Storing user passwords
Symmetric Encryption,AES-256-GCM ChaCha20-Poly1305,Encrypting data at rest database fields
Asymmetric Encryption,RSA-2048 ECC,Key exchange digital signatures
TLS/SSL,TLS 1.3 TLS 1.2,Data in transit HTTPS APIs
Key Derivation,PBKDF2 argon2,Deriving encryption keys from passwords
Secure Random,crypto.randomBytes secrets.token_bytes,Generating tokens session IDs

### 5. Security Headers

security_headers[10]{header,purpose,example_value}:
Content-Security-Policy,Prevent XSS injection attacks,default-src 'self'; script-src 'self' 'nonce-{random}'
Strict-Transport-Security,Force HTTPS connections,max-age=31536000; includeSubDomains
X-Frame-Options,Prevent clickjacking attacks,DENY or SAMEORIGIN
X-Content-Type-Options,Prevent MIME-sniffing,nosniff
Referrer-Policy,Control referrer information,strict-origin-when-cross-origin
Permissions-Policy,Control browser features,geolocation=() microphone=()
Cross-Origin-Embedder-Policy,Isolate cross-origin resources,require-corp
Cross-Origin-Opener-Policy,Isolate browsing context,same-origin
Cross-Origin-Resource-Policy,Control resource loading,same-site
X-XSS-Protection,Legacy XSS protection,1; mode=block

## Documentation

### Core Security Knowledge
- **[OWASP Top 10 Reference](reference/owasp-top-10.md)** - Detailed coverage of each OWASP vulnerability with examples
- **[Authentication Patterns](reference/authentication.md)** - Complete guide to authentication mechanisms and best practices
- **[Encryption Guide](reference/encryption.md)** - Encryption algorithms, key management, and implementation patterns
- **[Input Validation](reference/input-validation.md)** - Comprehensive input validation and sanitization techniques

### Implementation Guides
- **[Secure Coding Checklist](reference/secure-coding.md)** - Language-agnostic secure coding practices and code review checklist
- **[Security Headers Configuration](reference/security-headers.md)** - Complete security headers configuration for web applications
- **[API Security](reference/api-security.md)** - REST and GraphQL API security best practices
- **[Incident Response](reference/incident-response.md)** - Logging, monitoring, and incident response procedures

## Examples

### Basic Security Examples
Start with fundamental security patterns:
- **[SQL Injection Prevention](examples/sql-injection-prevention.md)** - Complete SQL injection defense strategies
- **[XSS Prevention](examples/xss-prevention.md)** - Cross-site scripting prevention in various contexts
- **[CSRF Protection](examples/csrf-protection.md)** - Cross-site request forgery defense patterns
- **[Secure Password Handling](examples/password-handling.md)** - Password hashing, validation, and reset flows
- **[JWT Authentication](examples/jwt-authentication.md)** - Secure JWT implementation with refresh tokens

### Intermediate Security Examples
Real-world security scenarios:
- **[OAuth 2.0 Implementation](examples/oauth-implementation.md)** - Complete OAuth 2.0 authorization flow
- **[File Upload Security](examples/file-upload-security.md)** - Secure file upload validation and storage
- **[Rate Limiting](examples/rate-limiting.md)** - Implement rate limiting to prevent abuse
- **[Encryption at Rest](examples/encryption-at-rest.md)** - Database field encryption and key management
- **[Security Logging](examples/security-logging.md)** - Comprehensive security event logging

### Advanced Security Examples
Production-grade security implementations:
- **[Multi-Factor Authentication](examples/mfa-implementation.md)** - TOTP-based MFA with backup codes
- **[API Key Management](examples/api-key-management.md)** - Secure API key generation, rotation, and revocation
- **[Web Application Firewall](examples/waf-implementation.md)** - Custom WAF rules and attack detection
- **[Penetration Testing Prep](examples/pentest-preparation.md)** - Prepare application for security testing
- **[Zero Trust Architecture](examples/zero-trust.md)** - Implement zero trust security principles

## Templates

Ready-to-use security templates:
- **[Secure API Template](templates/secure-api-template.md)** - Production-ready secure API with all protections
- **[Security Code Review Checklist](templates/code-review-checklist.md)** - Comprehensive security review checklist
- **[Security Audit Report](templates/audit-report-template.md)** - Template for documenting security findings
- **[Incident Response Plan](templates/incident-response-plan.md)** - Security incident response procedure template
- **[Security Policy Document](templates/security-policy.md)** - Application security policy template

## Security Testing Approaches

testing_types[5]{type,tools,purpose}:
SAST (Static Analysis),SonarQube Semgrep Bandit,Find vulnerabilities in source code
DAST (Dynamic Analysis),OWASP ZAP Burp Suite Nikto,Test running application for vulnerabilities
SCA (Composition Analysis),Snyk Dependabot OWASP Dependency-Check,Identify vulnerable dependencies
Penetration Testing,Metasploit Nmap Manual testing,Simulate real-world attacks
Security Code Review,Manual review with checklist,Human review of security-critical code

## Common Security Mistakes to Avoid

common_mistakes[10]{mistake,why_dangerous,correct_approach}:
Trusting user input,All input can be malicious,Validate sanitize and encode all inputs
Rolling your own crypto,Cryptography is extremely complex,Use established libraries like bcrypt OpenSSL
Storing plaintext passwords,Passwords exposed in breaches,Use bcrypt or argon2 with salt
Exposing sensitive errors,Reveals system information,Generic errors to users log details internally
Insufficient authorization checks,Users access unauthorized resources,Check authorization on every request
Hardcoded secrets,Secrets exposed in version control,Use environment variables secrets management
Using weak random numbers,Predictable tokens and IDs,Use cryptographically secure random generators
Missing rate limiting,Enables brute force attacks,Implement rate limiting on all endpoints
Insufficient logging,Cannot detect or investigate attacks,Log all security-relevant events
Not updating dependencies,Known vulnerabilities exploited,Regular dependency updates and scanning

## Security Principles

security_principles[8]{principle,description}:
Defense in Depth,Multiple layers of security controls
Principle of Least Privilege,Minimum necessary access and permissions
Fail Securely,System fails to secure state not open state
Complete Mediation,Check authorization on every access
Open Design,Security should not depend on secrecy of design
Separation of Duties,No single person has complete control
Economy of Mechanism,Keep security mechanisms simple and small
Psychological Acceptability,Security measures should be easy to use correctly

## Integration with Other Skills

This skill works well with:
- **API Development** - Secure REST and GraphQL APIs
- **Authentication Systems** - Advanced authentication patterns
- **Database Design** - Secure database architecture
- **DevOps** - Security in CI/CD pipelines
- **Code Review** - Security-focused code reviews

## Compliance and Standards

compliance_standards[6]{standard,scope,key_requirements}:
OWASP Top 10,Web application security,Address top 10 vulnerabilities
PCI-DSS,Payment card data,Encryption access control logging
GDPR,Personal data protection,Data minimization encryption consent
HIPAA,Healthcare data,Encryption audit trails access control
SOC 2,Service organization controls,Security monitoring incident response
ISO 27001,Information security management,Risk assessment security controls

## Getting Help

If you need security guidance:
1. Check **[OWASP Top 10 Reference](reference/owasp-top-10.md)** for vulnerability details
2. Review **[Examples](examples/)** for secure implementation patterns
3. Use **[Templates](templates/)** for security checklists and procedures
4. Consult **[Secure Coding Guide](reference/secure-coding.md)** for code review

## Next Steps

1. **Understand threats** - Read [OWASP Top 10](reference/owasp-top-10.md)
2. **Learn authentication** - Study [Authentication Patterns](reference/authentication.md)
3. **Practice secure coding** - Review [Secure Coding Checklist](reference/secure-coding.md)
4. **Try examples** - Implement [Basic Examples](examples/)
5. **Use templates** - Start with [Security Templates](templates/)

## Security Resources

external_resources[8]{resource,description}:
OWASP.org,Web application security best practices
CWE Top 25,Most dangerous software weaknesses
NIST Cybersecurity Framework,Comprehensive security framework
CVE Database,Common vulnerabilities and exposures
Security Headers,Test and validate security headers
SSL Labs,Test SSL/TLS configuration
Have I Been Pwned,Check for compromised credentials
SANS Top 25,Most dangerous programming errors

---

**Version**: 1.0.0
**Last Updated**: 2025-01-25
**Maintainer**: Claude Code Skills Team
**Security Level**: Production-Ready

**⚠️ IMPORTANT**: Security is critical. Always validate implementations with security professionals, use established libraries, and stay updated on latest vulnerabilities and patches.
