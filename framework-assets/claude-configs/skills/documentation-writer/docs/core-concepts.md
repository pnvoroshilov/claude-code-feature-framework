# Core Concepts of Technical Documentation

## Table of Contents
- [What is Technical Documentation](#what-is-technical-documentation)
- [Documentation Types](#documentation-types)
- [Audience Analysis](#audience-analysis)
- [Information Architecture](#information-architecture)
- [Documentation as Code](#documentation-as-code)
- [Progressive Disclosure](#progressive-disclosure)
- [Single Source of Truth](#single-source-of-truth)
- [Accessibility in Documentation](#accessibility-in-documentation)
- [Version Control for Documentation](#version-control-for-documentation)
- [Documentation Lifecycle](#documentation-lifecycle)
- [Writing for Scanning](#writing-for-scanning)
- [The Principle of Least Surprise](#the-principle-of-least-surprise)

## What is Technical Documentation

### Definition
Technical documentation is any written content that explains how a technical system, product, or process works, how to use it, or how to build/maintain it. It bridges the gap between complex technical implementations and their users.

### Why It Matters
Good technical documentation:
- **Reduces support burden**: Users find answers independently
- **Accelerates onboarding**: New team members become productive faster
- **Preserves knowledge**: Institutional knowledge survives team changes
- **Improves product quality**: Documenting forces clarity in design
- **Enables adoption**: Users can't use what they don't understand
- **Builds trust**: Professional documentation signals product maturity

### Core Characteristics
Effective technical documentation is:
1. **Accurate**: Information is correct and current
2. **Complete**: Covers all necessary topics without gaps
3. **Clear**: Written in understandable language for the target audience
4. **Concise**: Says what's needed without unnecessary verbosity
5. **Organized**: Information is easy to find and navigate
6. **Maintainable**: Can be kept up-to-date efficiently
7. **Accessible**: Available to all users including those with disabilities

### Example: Good vs Poor Documentation

**Poor Example:**
```markdown
# The System

The system does things. Use the API to interact with it.
```

**Good Example:**
```markdown
# User Management API

The User Management API provides endpoints for creating, reading, updating, and deleting user accounts in your application.

## What You Can Do
- Create new user accounts with email validation
- Retrieve user information and profiles
- Update user preferences and settings
- Delete user accounts and associated data
- Manage user roles and permissions

## Quick Start
```python
import requests

# Create a new user
response = requests.post(
    "https://api.example.com/users",
    json={"email": "user@example.com", "username": "johndoe"},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

user = response.json()
print(f"Created user: {user['username']}")
```

## Prerequisites
- API access token (see [Authentication Guide](../guides/authentication.md))
- Python 3.7+ with requests library installed
```

## Documentation Types

### Reference Documentation
**Purpose**: Comprehensive, detailed information about every feature, function, or component.

**Characteristics**:
- Exhaustive coverage of all features
- Organized alphabetically or by category
- Technical and precise language
- Minimal narrative or tutorial content
- Used for lookup, not learning

**Example Structure**:
```markdown
### `calculate_total(items, tax_rate=0.0)`

Calculates the total cost of items including optional tax.

**Parameters:**
- `items` (list): List of item prices (float or int)
- `tax_rate` (float, optional): Tax rate as decimal (e.g., 0.08 for 8%). Default: 0.0

**Returns:**
- `float`: Total cost including tax, rounded to 2 decimal places

**Raises:**
- `ValueError`: If items list is empty or contains non-numeric values
- `ValueError`: If tax_rate is negative

**Example:**
```python
>>> calculate_total([10.00, 20.00, 15.00], tax_rate=0.08)
48.60
```
```

### Tutorial Documentation
**Purpose**: Teach concepts and skills through hands-on, step-by-step guidance.

**Characteristics**:
- Learning-focused with clear objectives
- Sequential, building on previous steps
- Includes explanations of "why" not just "how"
- Contains complete, working examples
- Guides users to a specific outcome

**Example Structure**:
```markdown
# Tutorial: Building Your First REST API

**What You'll Learn:**
- Setting up a FastAPI project
- Creating GET and POST endpoints
- Validating request data
- Handling errors gracefully

**Time Required:** 30 minutes
**Skill Level:** Beginner

## Step 1: Set Up Your Environment

Create a new directory and virtual environment:

```bash
mkdir my-api && cd my-api
python -m venv venv
source venv/bin/activate
```

**Why use virtual environments?** They keep project dependencies isolated, preventing version conflicts between different projects.
```

### How-To Guides
**Purpose**: Solve specific problems or accomplish specific tasks.

**Characteristics**:
- Task-focused and goal-oriented
- Assumes reader has context/knowledge
- Provides direct steps without extensive explanation
- Practical and action-oriented
- May skip theory in favor of practice

**Example Structure**:
```markdown
# How to Add Authentication to Your API

This guide shows you how to add JWT-based authentication to an existing FastAPI application.

**Prerequisites:**
- Existing FastAPI application
- python-jose and passlib installed

**Steps:**

1. Install dependencies:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

2. Create authentication module (auth.py):
```python
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
```

[Additional steps...]
```

### Explanation/Conceptual Documentation
**Purpose**: Clarify concepts, explain design decisions, provide context and understanding.

**Characteristics**:
- Concept-focused rather than task-focused
- Explains "why" and context
- May include diagrams and analogies
- Helps build mental models
- Less code, more prose

**Example Structure**:
```markdown
# Understanding JWT Authentication

JSON Web Tokens (JWT) are a standard for securely transmitting information between parties as a JSON object. Think of a JWT like a sealed envelope containing a letter—anyone can see the envelope, but only someone with the key can read the contents inside.

## Why Use JWT?

Traditional session-based authentication stores session data on the server. Every request must look up the session in a database or cache, which:
- Creates server-side state
- Doesn't scale well across multiple servers
- Requires session storage management

JWT authentication is **stateless**—the server doesn't need to store anything. The token itself contains all necessary information, encoded and signed.

## How JWT Works

[Diagram would go here]

1. User logs in with credentials
2. Server validates credentials
3. Server creates JWT containing user info
4. Server signs JWT with secret key
5. Client stores JWT (usually in localStorage)
6. Client sends JWT with each request
7. Server verifies JWT signature
8. Server extracts user info from JWT

No database lookup needed—the token is self-contained.
```

## Audience Analysis

### Identifying Your Audience

**Key Questions:**
1. **Who will read this?** (Developers, end-users, administrators, executives)
2. **What is their technical level?** (Beginner, intermediate, expert)
3. **What is their goal?** (Learn, solve a problem, make a decision, implement)
4. **What do they already know?** (Prerequisites and assumptions)
5. **What context do they need?** (Background information required)

### Audience Segmentation

**End Users:**
- Focus: Accomplishing tasks with the product
- Language: Simple, jargon-free
- Examples: Real-world scenarios they relate to
- Depth: Just enough to accomplish their goals

**Developers:**
- Focus: Integrating, extending, or maintaining code
- Language: Technical but clear
- Examples: Code-heavy with implementation details
- Depth: Complete technical details and edge cases

**System Administrators:**
- Focus: Installing, configuring, monitoring
- Language: Technical, operations-focused
- Examples: Configuration examples, troubleshooting
- Depth: Operational details and system requirements

**Decision Makers:**
- Focus: Understanding capabilities, costs, benefits
- Language: Business-focused, high-level
- Examples: Use cases, ROI scenarios
- Depth: Overview with links to details

### Example: Writing for Different Audiences

**For End Users:**
```markdown
# Uploading a File

1. Click the **Upload** button in the top-right corner
2. Select your file from your computer
3. Click **Open**
4. Wait for the upload to complete (you'll see a green checkmark)

**Tip:** Files must be under 10MB. Supported formats: PDF, DOCX, TXT
```

**For Developers:**
```markdown
# File Upload API

**Endpoint:** `POST /api/files`

**Headers:**
- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Request Body:**
```typescript
{
  file: File,          // Max size: 10MB
  folder_id?: string,  // Optional target folder
  overwrite?: boolean  // Default: false
}
```

**Response (201):**
```json
{
  "file_id": "file_abc123",
  "url": "https://cdn.example.com/files/abc123.pdf",
  "size": 1048576,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error Handling:**
- 400: File too large or invalid format
- 401: Invalid or missing authentication token
- 413: Request payload too large
```

## Information Architecture

### Organizing Documentation

**Principles:**
1. **Group by task or concept**, not by implementation detail
2. **Create clear hierarchy**: Main topics → Subtopics → Details
3. **Provide multiple navigation paths**: Search, browse, links
4. **Use consistent structure**: Same template for similar pages
5. **Put most important information first**: Inverted pyramid style

### Common Organization Patterns

**By User Journey:**
```
1. Getting Started
2. Core Concepts
3. Common Tasks
4. Advanced Features
5. Reference
6. Troubleshooting
```

**By Feature:**
```
1. Overview
2. Feature A
   - Overview
   - Basic Usage
   - Advanced Usage
   - API Reference
3. Feature B
   [same structure]
```

**By Audience:**
```
1. User Guide
2. Developer Guide
3. Administrator Guide
4. API Reference
```

### Navigation Best Practices

**Table of Contents:**
- Include at top of long pages
- Link to all major sections
- Use descriptive link text
- Keep hierarchy visible

**Breadcrumbs:**
```
Home > Guides > User Guide > Uploading Files
```

**Cross-References:**
```markdown
For more information on authentication, see the [Authentication Guide](../guides/auth.md).

**Related topics:**
- [User Roles and Permissions](./permissions.md)
- [API Rate Limits](./rate-limits.md)
```

## Documentation as Code

### Philosophy
Treat documentation with the same rigor as code:
- Store in version control (Git)
- Review via pull requests
- Test automatically (broken links, code examples)
- Deploy automatically (CI/CD)
- Version alongside code

### Benefits
1. **Single source of truth**: Docs live with code
2. **Versioning**: Track changes over time
3. **Collaboration**: Multiple contributors
4. **Automation**: Build and deploy automatically
5. **Quality**: Code review for docs
6. **Rollback**: Restore previous versions easily

### Implementation Example

**Directory Structure:**
```
project/
├── src/              # Source code
├── docs/             # Documentation
│   ├── api/
│   ├── guides/
│   └── tutorials/
├── mkdocs.yml        # Documentation config
└── .github/
    └── workflows/
        └── docs.yml  # Auto-deploy docs
```

**CI/CD for Documentation:**
```yaml
# .github/workflows/docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy docs
        run: mkdocs gh-deploy --force
```

## Progressive Disclosure

### Concept
Present information in layers—start simple, add complexity gradually. Don't overwhelm users with everything at once.

### Implementation

**Layer 1: Overview**
```markdown
# User Authentication

Our API uses JWT tokens for authentication. Include your token in the Authorization header.
```

**Layer 2: Quick Start**
```markdown
## Quick Start

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get("https://api.example.com/users", headers=headers)
```
```

**Layer 3: Detailed Explanation**
```markdown
## How It Works

JWTs contain three parts: header, payload, and signature...
[Detailed explanation]
```

**Layer 4: Advanced Topics**
```markdown
## Token Refresh

For long-running sessions, implement token refresh...
[Advanced implementation]
```

### Techniques

1. **Expandable sections**: Hide details until needed
2. **Linked deep-dives**: "Learn more about X"
3. **Tiered examples**: Basic → Intermediate → Advanced
4. **Appendices**: Move complex details to appendices

## Single Source of Truth

### Principle
Each piece of information should exist in exactly one place. All other references should link to that canonical source.

### Why It Matters
- **Consistency**: No conflicting information
- **Maintainability**: Update once, reflected everywhere
- **Trust**: Users know where to find accurate info

### Anti-Pattern
```markdown
# File 1: user-guide.md
The API rate limit is 100 requests per minute.

# File 2: api-reference.md
The API rate limit is 1000 requests per hour.

# File 3: faq.md
Q: What's the rate limit?
A: 60 requests per minute.
```

### Correct Pattern
```markdown
# config/api-limits.md (Single source of truth)
## API Rate Limits
- 100 requests per minute
- 1,000 requests per hour
- 10,000 requests per day

# user-guide.md
Rate limits apply. See [API Rate Limits](../config/api-limits.md) for details.

# api-reference.md
For rate limit details, see [API Rate Limits](../config/api-limits.md).

# faq.md
Q: What's the rate limit?
A: See our [API Rate Limits](../config/api-limits.md) documentation.
```

## Accessibility in Documentation

### Guidelines

1. **Use semantic HTML**: Proper heading hierarchy (h1, h2, h3)
2. **Provide alt text**: Describe images meaningfully
3. **Use sufficient contrast**: Text readable against background
4. **Support keyboard navigation**: All features keyboard-accessible
5. **Provide text transcripts**: For video/audio content
6. **Use descriptive link text**: "Read the installation guide" not "Click here"

### Example: Accessible Image Documentation

**Poor:**
```markdown
![](screenshot.png)
```

**Good:**
```markdown
![Screenshot of the user dashboard showing the navigation menu on the left, user profile in the top-right, and a data table displaying the last 10 transactions with columns for date, amount, and status](dashboard-screenshot.png)
```

## Version Control for Documentation

### Strategies

**Versioned Documentation:**
- Maintain docs for each major version
- URL structure: `/docs/v1/`, `/docs/v2/`
- Version selector in UI

**Single Version with Deprecation Notices:**
```markdown
# create_user() [Deprecated in v2.0]

⚠️ **Deprecated**: Use [`create_user_v2()`](#create_user_v2) instead. This method will be removed in v3.0.

## Migration Guide
```python
# Old way (v1)
create_user(email, name)

# New way (v2)
create_user_v2(email=email, name=name, role="user")
```
```

## Documentation Lifecycle

### Phases

1. **Planning**: Identify what needs documentation
2. **Writing**: Create initial documentation
3. **Review**: Technical and editorial review
4. **Publishing**: Make available to users
5. **Maintenance**: Keep updated as product changes
6. **Deprecation**: Archive outdated documentation

### Continuous Improvement

**Metrics to Track:**
- Page views (popular vs unused content)
- Search queries (what users look for)
- Time on page (engagement)
- Feedback ratings (quality perception)
- Support tickets (what's unclear)

**Regular Reviews:**
- Quarterly: Review top 20 pages
- On releases: Update affected documentation
- Annually: Comprehensive audit

## Writing for Scanning

### Reality
Most users scan rather than read. Optimize for scanning:

**Techniques:**
1. **Use headings liberally**: Break up text
2. **Highlight key points**: Bold important terms
3. **Use lists**: Easier to scan than paragraphs
4. **Add code examples**: Visual break from prose
5. **Use callouts**: Warning, tip, note boxes
6. **Keep paragraphs short**: 2-4 sentences max

**Example:**

**Hard to scan:**
```markdown
When you're setting up authentication you need to first install the required packages which are python-jose and passlib and then you need to create a secret key which should be kept secure and not committed to version control and then configure the algorithm which is usually HS256 and after that you can implement the password hashing and verification functions.
```

**Easy to scan:**
```markdown
## Setting Up Authentication

**Required packages:**
- `python-jose[cryptography]`
- `passlib[bcrypt]`

**Key steps:**
1. **Install dependencies**: `pip install python-jose[cryptography] passlib[bcrypt]`
2. **Generate secret key**: Use a strong, random key
3. **Configure algorithm**: HS256 recommended
4. **Implement password hashing**: Use bcrypt

⚠️ **Security note**: Never commit your secret key to version control.
```

## The Principle of Least Surprise

### Concept
Documentation should match user expectations. Surprises frustrate and confuse.

### Application

**Consistent terminology:**
- Don't use "user", "account", and "profile" interchangeably
- Pick one term and stick with it

**Consistent structure:**
- If endpoint docs follow a pattern, all should follow the same pattern

**Consistent behavior:**
- If examples use a certain style, all examples should use that style

**Example: Inconsistent (Bad)**
```markdown
# POST /users
Creates a user account.

# GET /accounts
Retrieves a user profile.

# DELETE /profiles
Removes a user.
```

**Example: Consistent (Good)**
```markdown
# POST /users
Creates a new user.

# GET /users/{id}
Retrieves a user.

# DELETE /users/{id}
Deletes a user.
```

## Related Concepts

- **Content Strategy**: See [docs/best-practices.md](best-practices.md)
- **Documentation Patterns**: See [docs/patterns.md](patterns.md)
- **Tools and Automation**: See [docs/advanced-topics.md](advanced-topics.md)
