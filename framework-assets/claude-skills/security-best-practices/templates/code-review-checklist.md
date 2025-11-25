# Security Code Review Checklist

Comprehensive checklist for conducting security-focused code reviews. Use this template to ensure all critical security aspects are covered.

## Review Information

```
Project Name: ___________________________
Review Date: ____________________________
Reviewer: _______________________________
Code Author: ____________________________
Component/Module: _______________________
Language/Framework: _____________________
```

## 1. Input Validation and Sanitization

input_validation_checks[12]{check,status,notes}:
All user inputs validated at entry points,☐,
Whitelist validation used over blacklist,☐,
Length limits enforced on all inputs,☐,
Data types validated before processing,☐,
Special characters properly handled,☐,
File uploads validated (type size content),☐,
Email addresses validated with proper regex,☐,
URLs validated and protocols whitelisted,☐,
Phone numbers validated in standard format,☐,
Numeric inputs checked for range,☐,
Date inputs validated for valid ranges,☐,
JSON/XML inputs validated against schema,☐,

### Critical Issues Found:
```
[ ] None
[ ] Low Priority:
    -
[ ] Medium Priority:
    -
[ ] High Priority:
    -
[ ] Critical:
    -
```

## 2. SQL Injection Prevention

sql_injection_checks[10]{check,status,notes}:
Parameterized queries used for all database operations,☐,
No string concatenation in SQL queries,☐,
ORM used correctly (not bypassing protections),☐,
Dynamic column names whitelisted,☐,
LIKE patterns properly parameterized,☐,
Stored procedures use parameters,☐,
Database user has least privilege,☐,
Error messages don't expose SQL details,☐,
All database frameworks up to date,☐,
SQL injection testing performed,☐,

### SQL Injection Vulnerabilities:
```
[ ] None found
[ ] Potential issues:
    File: _________________
    Line: _________________
    Issue: ________________
    Severity: _____________
```

## 3. Cross-Site Scripting (XSS) Prevention

xss_checks[12]{check,status,notes}:
Output encoding used in all templates,☐,
React/Vue auto-escaping not bypassed,☐,
innerHTML/dangerouslySetInnerHTML avoided or sanitized,☐,
User input not used in eval or Function,☐,
URL parameters properly encoded,☐,
textContent used instead of innerHTML,☐,
DOMPurify or similar sanitization library used,☐,
Content Security Policy implemented,☐,
No inline event handlers with user data,☐,
JSON data properly escaped in templates,☐,
Markdown rendering sanitized,☐,
Links validated to prevent javascript: URLs,☐,

### XSS Vulnerabilities:
```
[ ] None found
[ ] Potential issues:
    Context: ______________
    Location: _____________
    User Input: ___________
    Severity: _____________
```

## 4. Authentication and Authorization

auth_checks[15]{check,status,notes}:
Password hashing uses bcrypt/argon2/scrypt,☐,
Password minimum requirements enforced,☐,
Passwords never logged or stored in plaintext,☐,
JWT tokens have short expiration (15-30 min),☐,
Refresh tokens used for long-lived sessions,☐,
Token secrets are strong (256+ bits),☐,
Session IDs are cryptographically random,☐,
Session cookies are HttpOnly and Secure,☐,
Multi-factor authentication available,☐,
Authorization checked on every request,☐,
Role-based access control implemented,☐,
Principle of least privilege followed,☐,
Sensitive operations require re-authentication,☐,
Account lockout after failed attempts,☐,
Logout properly clears sessions and tokens,☐,

### Authentication Issues:
```
[ ] None found
[ ] Weak password requirements
[ ] Insecure token handling
[ ] Missing authorization checks:
    Endpoint: _____________
    Issue: ________________
[ ] Other:
    -
```

## 5. Sensitive Data Protection

data_protection_checks[12]{check,status,notes}:
Sensitive data encrypted at rest,☐,
TLS 1.2+ used for data in transit,☐,
Strong encryption algorithms used (AES-256),☐,
Encryption keys stored securely (KMS/vault),☐,
Passwords never stored in plaintext,☐,
API keys and secrets in environment variables,☐,
No secrets committed to version control,☐,
Sensitive data not logged,☐,
Sensitive data masked in UI when appropriate,☐,
PII handling complies with regulations,☐,
Secure deletion implemented for sensitive data,☐,
Backups are encrypted,☐,

### Data Protection Issues:
```
[ ] None found
[ ] Unencrypted sensitive data:
    Type: _________________
    Location: _____________
[ ] Secrets in code:
    File: _________________
    Type: _________________
[ ] Other:
    -
```

## 6. Error Handling and Logging

error_handling_checks[10]{check,status,notes}:
Generic error messages shown to users,☐,
Detailed errors logged server-side only,☐,
Stack traces not exposed to users,☐,
Error responses don't leak system info,☐,
All errors properly caught and handled,☐,
Security events logged (login failures etc),☐,
Logs don't contain sensitive data,☐,
Log injection prevented,☐,
Monitoring and alerting configured,☐,
Incident response procedures documented,☐,

### Error Handling Issues:
```
[ ] None found
[ ] Information disclosure:
    Location: _____________
    Information: __________
[ ] Missing error handling:
    Location: _____________
[ ] Other:
    -
```

## 7. Access Control and Authorization

access_control_checks[10]{check,status,notes}:
Authorization checked before all operations,☐,
Direct object references are validated,☐,
Users can only access their own data,☐,
Admin functions require admin role,☐,
File access restricted to allowed directories,☐,
API endpoints have proper authorization,☐,
CORS configured with specific origins,☐,
Rate limiting implemented,☐,
Access control failures logged,☐,
Privilege escalation tested and prevented,☐,

### Access Control Issues:
```
[ ] None found
[ ] Missing authorization:
    Endpoint: _____________
    Risk: _________________
[ ] IDOR vulnerabilities:
    Location: _____________
[ ] Other:
    -
```

## 8. Security Headers

security_headers_checks[10]{header,implemented,value}:
Content-Security-Policy,☐,
Strict-Transport-Security,☐,
X-Frame-Options,☐,
X-Content-Type-Options,☐,
Referrer-Policy,☐,
Permissions-Policy,☐,
Cross-Origin-Embedder-Policy,☐,
Cross-Origin-Opener-Policy,☐,
Cross-Origin-Resource-Policy,☐,
X-XSS-Protection (legacy),☐,

### Header Configuration:
```
Missing headers: __________
Misconfigured headers: ____
Testing results: __________
```

## 9. Dependency Security

dependency_checks[8]{check,status,notes}:
All dependencies up to date,☐,
No known vulnerable dependencies,☐,
Dependency scanning tool used,☐,
Minimal dependencies principle followed,☐,
Dependencies from trusted sources only,☐,
Lock files committed to version control,☐,
Regular dependency updates scheduled,☐,
Security advisories monitored,☐,

### Dependency Issues:
```
[ ] None found
[ ] Vulnerable dependencies:
    Package: ______________
    Vulnerability: ________
    Severity: _____________
    Fix Available: ________
```

## 10. File Upload Security

file_upload_checks[10]{check,status,notes}:
File type validated by content not extension,☐,
File size limits enforced,☐,
Uploaded files stored outside webroot,☐,
Filenames sanitized to prevent traversal,☐,
Unique random filenames generated,☐,
Virus scanning performed if applicable,☐,
Image files re-encoded to strip metadata,☐,
File permissions set correctly,☐,
Upload rate limiting implemented,☐,
Direct file serving prevented,☐,

### File Upload Issues:
```
[ ] None found
[ ] Security issues:
    Issue: ________________
    Risk: _________________
    Location: _____________
```

## 11. API Security

api_security_checks[12]{check,status,notes}:
Authentication required for all endpoints,☐,
API keys rotated regularly,☐,
Rate limiting per endpoint and user,☐,
Input validation on all parameters,☐,
Proper HTTP methods used (GET/POST/etc),☐,
CORS configured correctly,☐,
API versioning implemented,☐,
Pagination limits enforced,☐,
No sensitive data in URLs,☐,
GraphQL query depth limited,☐,
API documentation security reviewed,☐,
API endpoints tested for vulnerabilities,☐,

### API Security Issues:
```
[ ] None found
[ ] Issues found:
    Endpoint: _____________
    Issue: ________________
    Severity: _____________
```

## 12. Cryptography

crypto_checks[10]{check,status,notes}:
Strong algorithms used (AES-256 RSA-2048),☐,
No deprecated algorithms (MD5 SHA1 DES),☐,
Secure random number generator used,☐,
Proper key management implemented,☐,
Initialization vectors (IV) random and unique,☐,
No custom crypto implementations,☐,
TLS 1.2+ enforced,☐,
Certificate validation not disabled,☐,
Cryptographic libraries up to date,☐,
Key rotation strategy in place,☐,

### Cryptography Issues:
```
[ ] None found
[ ] Weak algorithms:
    Algorithm: ____________
    Usage: ________________
[ ] Other:
    -
```

## 13. Session Management

session_checks[10]{check,status,notes}:
Session IDs cryptographically random,☐,
Session cookies HttpOnly and Secure,☐,
SameSite attribute set on cookies,☐,
Session timeout implemented,☐,
Session regeneration on privilege change,☐,
Logout destroys session completely,☐,
Concurrent session limits if applicable,☐,
Session fixation prevented,☐,
No sensitive data in session storage,☐,
Session hijacking mitigations in place,☐,

### Session Management Issues:
```
[ ] None found
[ ] Issues:
    Issue: ________________
    Risk: _________________
```

## 14. Business Logic Security

business_logic_checks[8]{check,status,notes}:
Price manipulation prevented,☐,
Quantity limits enforced,☐,
Race conditions handled,☐,
Transaction integrity maintained,☐,
State transitions validated,☐,
Business rules consistently enforced,☐,
Duplicate submissions prevented,☐,
Time-of-check time-of-use issues addressed,☐,

### Business Logic Issues:
```
[ ] None found
[ ] Issues:
    Flow: _________________
    Issue: ________________
    Risk: _________________
```

## 15. Third-Party Integrations

third_party_checks[8]{check,status,notes}:
API keys for third-party services secured,☐,
Third-party responses validated,☐,
Timeouts set for external calls,☐,
Failures handled gracefully,☐,
Third-party service SLAs reviewed,☐,
Data shared with third-parties minimized,☐,
Third-party security posture verified,☐,
Webhooks validated with signatures,☐,

### Third-Party Issues:
```
[ ] None found
[ ] Issues:
    Service: ______________
    Issue: ________________
```

## Overall Security Assessment

### Summary Statistics
```
Total Checks: ___________
Passed: _________________
Failed: _________________
Not Applicable: _________
```

### Risk Level
```
[ ] Low - Minor issues, no immediate action required
[ ] Medium - Issues should be addressed in next sprint
[ ] High - Issues must be addressed before deployment
[ ] Critical - Deployment should be blocked
```

### Critical Findings
```
1. ___________________________
   Severity: __________________
   Impact: ____________________
   Remediation: _______________

2. ___________________________
   Severity: __________________
   Impact: ____________________
   Remediation: _______________

3. ___________________________
   Severity: __________________
   Impact: ____________________
   Remediation: _______________
```

### Recommendations

high_priority_actions[]{action}:
-
-
-

medium_priority_actions[]{action}:
-
-
-

security_improvements[]{improvement}:
-
-
-

## Testing Requirements

tests_required[]{test_type,description}:
Penetration Testing,Required for critical findings
SAST Scan,Run static analysis tools
DAST Scan,Run dynamic security testing
Dependency Scan,Check for vulnerable dependencies
Manual Testing,Test security-critical flows

## Sign-Off

```
Code Review Completed: [ ]
Security Approved: [ ]
Requires Re-Review After Changes: [ ]

Reviewer Signature: _______________
Date: _____________________________

Developer Acknowledgment: _________
Date: _____________________________
```

## Notes and Comments
```
Additional observations, concerns, or context:

________________________________________
________________________________________
________________________________________
________________________________________
```

---

**Remember**: This checklist is a guide. Adapt it to your specific application, technology stack, and security requirements.
