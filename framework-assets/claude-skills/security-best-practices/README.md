# Security Best Practices Skill - README

Comprehensive security skill for Claude Code covering OWASP Top 10, secure coding, authentication, encryption, and security auditing.

## Skill Structure

skill_structure[4]{directory,purpose,file_count}:
Root,Main skill file with overview,1 (SKILL.md)
reference/,Detailed security references,4 files
examples/,Practical code examples,5 files
templates/,Security review templates,1 file

## Quick Navigation

### Main Entry Point
- **[SKILL.md](SKILL.md)** - Start here for skill overview, trigger scenarios, and quick security patterns

### Reference Documentation (In-Depth Knowledge)
- **[owasp-top-10.md](reference/owasp-top-10.md)** - Complete OWASP Top 10 vulnerabilities with prevention
- **[authentication.md](reference/authentication.md)** - Authentication mechanisms: passwords, JWT, OAuth, MFA
- **[input-validation.md](reference/input-validation.md)** - Input validation, sanitization, and injection prevention
- **[encryption.md](reference/encryption.md)** - TO BE CREATED - Encryption patterns and key management

### Practical Examples (Code Implementations)
- **[sql-injection-prevention.md](examples/sql-injection-prevention.md)** - Prevent SQL injection in Python and TypeScript
- **[xss-prevention.md](examples/xss-prevention.md)** - XSS prevention in React, Vue, and templates
- **[jwt-authentication.md](examples/jwt-authentication.md)** - Secure JWT implementation with refresh tokens
- **[csrf-protection.md](examples/csrf-protection.md)** - CSRF protection patterns and implementations
- **[password-handling.md](examples/password-handling.md)** - TO BE CREATED - Secure password flows

### Templates (Ready-to-Use)
- **[code-review-checklist.md](templates/code-review-checklist.md)** - Comprehensive security code review template

## Usage Patterns

### For Quick Security Fixes
1. Start with **[SKILL.md](SKILL.md)** "Quick Start" section
2. Find your vulnerability type in TOON tables
3. Apply the provided code pattern

### For Comprehensive Security Review
1. Use **[code-review-checklist.md](templates/code-review-checklist.md)**
2. Reference specific sections from `reference/` directory
3. Implement fixes from `examples/` directory

### For Learning Security Concepts
1. Read **[owasp-top-10.md](reference/owasp-top-10.md)** for vulnerability understanding
2. Study **[authentication.md](reference/authentication.md)** for auth patterns
3. Practice with examples in `examples/` directory

## TOON Format Usage

This skill extensively uses TOON format for token efficiency:

toon_benefits[4]{benefit,description}:
Token Efficiency,30-60% fewer tokens than JSON
Better Parsing,Higher LLM accuracy for structured data
Readability,Clear tabular format for comparisons
Consistency,Uniform format across all security tables

### Example TOON Tables in This Skill

```
owasp_top_10[10]{vulnerability,risk_level,primary_defense}:
Injection (SQL Command LDAP),Critical,Parameterized queries input validation
Broken Authentication,Critical,MFA secure session management JWT best practices
...
```

## Coverage Summary

security_coverage[8]{area,files,completeness}:
OWASP Top 10,reference/owasp-top-10.md,Comprehensive with examples
SQL Injection,examples/sql-injection-prevention.md,Python and TypeScript complete
XSS Prevention,examples/xss-prevention.md,React Vue Python complete
Authentication,reference/authentication.md + examples/jwt-authentication.md,Password JWT OAuth MFA covered
CSRF Protection,examples/csrf-protection.md,Multiple frameworks covered
Input Validation,reference/input-validation.md,Comprehensive validation patterns
Code Review,templates/code-review-checklist.md,Production-ready checklist
Encryption,TO BE CREATED,Planned for future

## Security Quick Reference

### Most Common Vulnerabilities

top_vulnerabilities[6]{vulnerability,quick_fix,reference}:
SQL Injection,Use parameterized queries,examples/sql-injection-prevention.md
XSS,Use output encoding auto-escaping,examples/xss-prevention.md
Broken Auth,Implement JWT + MFA,reference/authentication.md
CSRF,Add CSRF tokens SameSite cookies,examples/csrf-protection.md
Weak Passwords,Use bcrypt with 12+ rounds,reference/authentication.md
Missing Input Validation,Validate at all entry points,reference/input-validation.md

### Security Headers Checklist

```
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

See [SKILL.md](SKILL.md) for complete security headers table.

## File Size Note

file_sizes[11]{file,lines,status}:
SKILL.md,326,✅ Under 500 limit
code-review-checklist.md,473,✅ Under 500 limit
jwt-authentication.md,503,⚠️ Slightly over - comprehensive reference
csrf-protection.md,513,⚠️ Slightly over - comprehensive reference
owasp-top-10.md,555,⚠️ Over - split recommended
xss-prevention.md,563,⚠️ Over - split recommended
sql-injection-prevention.md,622,⚠️ Over - split recommended
input-validation.md,628,⚠️ Over - split recommended
authentication.md,652,⚠️ Over - split recommended
README.md,This file,Documentation only
Total,~5335,Comprehensive coverage

**Note**: Some reference files exceed 500 lines due to comprehensive code examples in multiple languages. These are reference documentation files meant for deep learning. For quick fixes, use the main SKILL.md file which is well under the limit.

## Integration with Other Skills

This skill integrates well with:
- **api-development** - Secure API design and implementation
- **code-review** - Security-focused code reviews
- **database-design** - Secure database architecture
- **deployment-helper** - Security in CI/CD

## Contributing

To extend this skill:

1. **Adding new vulnerabilities**: Update `reference/owasp-top-10.md`
2. **Adding code examples**: Create new files in `examples/`
3. **New security patterns**: Add to appropriate `reference/` file
4. **New checklists**: Add to `templates/` directory

## Testing This Skill

test_scenarios[6]{scenario,expected_result}:
Ask about SQL injection,Should provide parameterized query examples
Request XSS prevention,Should explain output encoding and CSP
Need authentication setup,Should guide to JWT or OAuth patterns
Security code review,Should provide comprehensive checklist
Ask about OWASP Top 10,Should explain each vulnerability
Request secure API design,Should combine with api-development skill

## Version History

- **v1.0.0** (2025-01-25) - Initial release
  - OWASP Top 10 coverage
  - Authentication patterns
  - Input validation
  - SQL injection prevention
  - XSS prevention
  - JWT implementation
  - CSRF protection
  - Security code review checklist

## Future Enhancements

planned_enhancements[8]{enhancement,priority}:
Encryption reference guide,High
API security examples,High
File upload security,Medium
Session management,Medium
Rate limiting patterns,Medium
Security testing guide,Medium
Compliance checklists (PCI GDPR),Low
Additional language examples (Go Rust),Low

---

**Created with TOON format for optimal token efficiency and LLM accuracy.**
