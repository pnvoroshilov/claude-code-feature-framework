# Documentation Best Practices

## Table of Contents
- [Writing Style Guidelines](#writing-style-guidelines)
- [Clarity and Conciseness](#clarity-and-conciseness)
- [Code Examples Best Practices](#code-examples-best-practices)
- [Consistency Standards](#consistency-standards)
- [Version Management](#version-management)
- [Review and Quality Assurance](#review-and-quality-assurance)
- [Maintenance Practices](#maintenance-practices)
- [Collaboration Best Practices](#collaboration-best-practices)
- [Documentation Testing](#documentation-testing)
- [Performance and Accessibility](#performance-and-accessibility)

## Writing Style Guidelines

### Use Active Voice

**Principle**: Active voice is clearer, more direct, and easier to understand than passive voice.

**Why It Matters**: Active voice makes instructions clearer and assigns responsibility explicitly, reducing ambiguity.

**Good Examples:**
```markdown
✅ "Click the Submit button to save your changes."
✅ "The function returns a list of user objects."
✅ "Set the timeout parameter to 30 seconds."
```

**Bad Examples:**
```markdown
❌ "The Submit button should be clicked to save your changes."
❌ "A list of user objects is returned by the function."
❌ "The timeout parameter should be set to 30 seconds."
```

**Exception**: Use passive voice when the actor is unknown or unimportant:
```markdown
✅ "The file was corrupted during transfer." (Unknown actor)
✅ "Users are authenticated via JWT tokens." (Implementation detail)
```

### Write in Second Person

**Principle**: Address the reader directly as "you" rather than "the user" or "one".

**Why It Matters**: Creates a conversational, engaging tone and makes instructions feel personal and relevant.

**Good Example:**
```markdown
✅ To start the server, you need to run the following command:
```bash
npm start
```

You'll see output indicating the server is running on port 3000.
```

**Bad Example:**
```markdown
❌ To start the server, the user must run the following command:
```bash
npm start
```

The user will see output indicating the server is running on port 3000.
```

### Use Present Tense

**Principle**: Write in present tense for most technical documentation.

**Why It Matters**: Present tense is more immediate and engaging. It describes how things work now, not how they worked or will work.

**Good Examples:**
```markdown
✅ "The API returns a 404 error when the resource is not found."
✅ "This function calculates the total price including tax."
✅ "Users can upload files up to 10MB in size."
```

**Bad Examples:**
```markdown
❌ "The API will return a 404 error when the resource is not found."
❌ "This function will calculate the total price including tax."
❌ "Users will be able to upload files up to 10MB in size."
```

### Be Specific and Concrete

**Principle**: Provide specific, concrete information rather than vague generalities.

**Why It Matters**: Specificity reduces ambiguity and helps users accomplish tasks correctly.

**Good Example:**
```markdown
✅ **System Requirements:**
- Python 3.9 or higher
- 4GB RAM minimum, 8GB recommended
- 500MB free disk space
- Ubuntu 20.04, macOS 11+, or Windows 10
- Internet connection for initial setup
```

**Bad Example:**
```markdown
❌ **System Requirements:**
- Recent version of Python
- Enough RAM
- Some disk space
- Modern operating system
- Internet connection
```

### Avoid Jargon and Acronyms

**Principle**: Define technical terms and acronyms on first use. Prefer plain language when possible.

**Why It Matters**: Not all readers have the same background. Unexplained jargon creates barriers to understanding.

**Good Example:**
```markdown
✅ Authentication uses JWT (JSON Web Token), a standard for securely transmitting information between parties. JWTs are compact, URL-safe tokens that contain claims about the user.

When you first encounter JWT in the documentation, it's explained.
```

**Bad Example:**
```markdown
❌ Authentication uses JWT. The JWT contains claims and is signed using HMAC SHA256 or RSA. Set the iss, sub, aud, exp, and iat claims appropriately.
```

**Creating a Glossary:**
For documentation with many technical terms:
```markdown
## Glossary

**JWT (JSON Web Token)**: A compact, URL-safe token format for securely transmitting information between parties. Contains three parts: header, payload, and signature.

**HMAC (Hash-based Message Authentication Code)**: A cryptographic method for verifying data integrity and authenticity using a secret key and a hash function.

**Payload**: The middle section of a JWT containing the claims (user information and metadata).
```

## Clarity and Conciseness

### One Idea Per Sentence

**Principle**: Each sentence should convey one main idea.

**Why It Matters**: Complex sentences with multiple ideas are harder to parse and understand.

**Good Example:**
```markdown
✅ The API supports pagination. Use the `page` parameter to specify which page you want. Each page contains up to 100 items.
```

**Bad Example:**
```markdown
❌ The API supports pagination and you can use the `page` parameter to specify which page you want and each page contains up to 100 items by default unless you specify otherwise.
```

### Eliminate Unnecessary Words

**Principle**: Remove words that don't add meaning or clarity.

**Why It Matters**: Concise writing is faster to read and easier to understand.

**Common Unnecessary Phrases:**

| Instead of | Use |
|------------|-----|
| "In order to" | "To" |
| "It is important to note that" | "Note:" or omit |
| "Due to the fact that" | "Because" |
| "At this point in time" | "Now" or "Currently" |
| "For the purpose of" | "To" or "For" |
| "Has the ability to" | "Can" |
| "In the event that" | "If" |

**Good Example:**
```markdown
✅ To install the package, run:
```bash
npm install example-package
```
```

**Bad Example:**
```markdown
❌ In order to install the package, it is important to note that you should run the following command:
```bash
npm install example-package
```
```

### Use Short Paragraphs

**Principle**: Keep paragraphs to 2-4 sentences. Use whitespace liberally.

**Why It Matters**: Short paragraphs are less intimidating and easier to scan.

**Good Example:**
```markdown
✅ ## Error Handling

The API returns standard HTTP status codes to indicate success or failure.

Successful requests return status codes in the 2xx range. Client errors return 4xx codes. Server errors return 5xx codes.

Always check the status code before processing the response. The response body contains error details for failed requests.
```

**Bad Example:**
```markdown
❌ ## Error Handling

The API returns standard HTTP status codes to indicate success or failure and successful requests return status codes in the 2xx range while client errors return 4xx codes and server errors return 5xx codes so you should always check the status code before processing the response because the response body contains error details for failed requests which will help you debug issues.
```

### Front-Load Important Information

**Principle**: Put the most important information first—in documents, paragraphs, and sentences.

**Why It Matters**: Readers may not read to the end. Put critical information where it's most likely to be seen.

**Good Example:**
```markdown
✅ ## Authentication Required

All API endpoints require authentication. Include your API key in the Authorization header.

**Without authentication, requests will fail with a 401 error.**

To obtain an API key, visit your account settings dashboard.
```

**Bad Example:**
```markdown
❌ ## Authentication

To obtain an API key, visit your account settings dashboard. Once you have your key, you'll need to include it in requests. All API endpoints require authentication. If you don't include authentication, requests will fail with a 401 error. The API key goes in the Authorization header.
```

## Code Examples Best Practices

### Always Test Your Examples

**Principle**: Every code example must be tested and verified to work exactly as shown.

**Why It Matters**: Broken examples destroy user trust and waste user time.

**Implementation:**

```markdown
# In your documentation repository

## Testing Code Examples

All code examples in docs/ are tested automatically in CI:

```yaml
# .github/workflows/test-docs.yml
name: Test Documentation Examples

on: [push, pull_request]

jobs:
  test-examples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Extract and test code examples
        run: python scripts/test_doc_examples.py
```

**Documentation Review Checklist:**
- [ ] All code examples tested locally
- [ ] Dependencies listed in example
- [ ] Expected output shown
- [ ] Error cases documented
- [ ] Examples automated in CI
```

### Provide Complete, Runnable Examples

**Principle**: Examples should be complete enough to run as-is, including imports and setup.

**Why It Matters**: Incomplete examples force users to guess at missing pieces.

**Good Example:**
```markdown
✅ ## Creating a User

This example creates a new user with the API:

```python
import requests
import os

# Setup
API_BASE = "https://api.example.com"
API_KEY = os.getenv("API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create user
response = requests.post(
    f"{API_BASE}/users",
    json={
        "email": "user@example.com",
        "username": "johndoe",
        "role": "user"
    },
    headers=headers
)

# Handle response
if response.status_code == 201:
    user = response.json()
    print(f"Created user: {user['username']} (ID: {user['id']})")
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

**Expected output:**
```
Created user: johndoe (ID: usr_abc123)
```
```

**Bad Example:**
```markdown
❌ ## Creating a User

```python
response = requests.post("/users", json=data)
user = response.json()
```
```

### Explain Your Examples

**Principle**: Don't just show code—explain what it does and why.

**Why It Matters**: Understanding enables adaptation. Users need to modify examples for their use case.

**Good Example:**
```markdown
✅ ## Pagination Example

```python
page = 1
all_users = []

while True:
    # Fetch one page of users
    response = requests.get(
        f"{API_BASE}/users",
        params={"page": page, "limit": 100},
        headers=headers
    )

    data = response.json()
    users = data["users"]

    # Add users from this page
    all_users.extend(users)

    # Check if there are more pages
    if not data["has_more"]:
        break

    page += 1

print(f"Retrieved {len(all_users)} total users")
```

**How it works:**

1. **Loop through pages**: Start at page 1 and increment
2. **Fetch each page**: Request 100 users per page
3. **Accumulate results**: Add each page's users to the list
4. **Check for more**: The `has_more` field indicates if additional pages exist
5. **Stop when done**: Break the loop when no more pages remain

**Why use pagination?** For large datasets, fetching all records at once would:
- Timeout the request
- Consume excessive memory
- Put unnecessary load on the server

Pagination fetches data in manageable chunks.
```

**Bad Example:**
```markdown
❌ ## Pagination Example

```python
page = 1
all_users = []
while True:
    response = requests.get(f"{API_BASE}/users", params={"page": page, "limit": 100})
    data = response.json()
    all_users.extend(data["users"])
    if not data["has_more"]:
        break
    page += 1
```
```

### Show Multiple Approaches

**Principle**: When there are multiple valid ways to accomplish something, show the options.

**Why It Matters**: Users have different contexts, preferences, and constraints.

**Good Example:**
```markdown
✅ ## Making API Requests

You can make requests using several libraries:

### Using requests (Recommended for simplicity)

```python
import requests

response = requests.get("https://api.example.com/users")
users = response.json()
```

**Pros:** Simple, widely-used, good documentation
**Cons:** Synchronous only, requires separate library

### Using httpx (Recommended for async)

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
    users = response.json()
```

**Pros:** Supports async/await, modern API, drop-in replacement for requests
**Cons:** Newer, smaller ecosystem

### Using stdlib urllib

```python
import urllib.request
import json

with urllib.request.urlopen("https://api.example.com/users") as response:
    users = json.loads(response.read())
```

**Pros:** No dependencies, always available
**Cons:** More verbose, less intuitive API
```

### Use Consistent Code Style

**Principle**: All code examples should follow the same style conventions.

**Why It Matters**: Consistency reduces cognitive load and establishes quality standards.

**Style Guide Example:**
```markdown
## Documentation Code Style

All Python examples in this documentation follow these conventions:

1. **Indentation**: 4 spaces (no tabs)
2. **Line length**: Max 88 characters (Black formatter)
3. **String quotes**: Double quotes for strings, single for dict keys
4. **Imports**: Standard library, third-party, local (separated by blank lines)
5. **Comments**: Explain "why", not "what"
6. **Variable names**: snake_case, descriptive

```python
# Good example
import os
from datetime import datetime

import requests

API_KEY = os.getenv("API_KEY")

def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from API."""
    # Use timeout to prevent hanging on slow connections
    response = requests.get(
        f"https://api.example.com/users/{user_id}",
        timeout=10
    )
    return response.json()
```
```

## Consistency Standards

### Terminology Consistency

**Principle**: Use the same term for the same concept throughout all documentation.

**Why It Matters**: Varying terms confuse readers—they wonder if different terms mean different things.

**Create a Terminology Guide:**
```markdown
## Approved Terminology

Use these terms consistently:

| Use This | Not These |
|----------|-----------|
| API key | API token, access key, auth key |
| Endpoint | Route, URL, path |
| Request body | Payload, request data, body |
| Response | Result, output, return value |
| User | Account, profile, member |
| Authentication | Auth, login, signin |
| Error | Failure, exception, problem |
```

**Example of Inconsistency (Bad):**
```markdown
❌ File 1: "Include your API key in the header."
❌ File 2: "Pass your access token in the Authorization header."
❌ File 3: "Authenticate using your auth key."
```

**Example of Consistency (Good):**
```markdown
✅ File 1: "Include your API key in the Authorization header."
✅ File 2: "Pass your API key in the Authorization header."
✅ File 3: "Authenticate using your API key in the Authorization header."
```

### Structural Consistency

**Principle**: Use the same structure for similar content.

**Why It Matters**: Predictable structure helps users find information quickly.

**API Endpoint Template:**
```markdown
### [METHOD] /path/to/endpoint

[One-sentence description]

**Authentication:** [Required/Optional]

**Request:**

[Request details]

**Response:**

[Response details]

**Errors:**

[Error conditions]

**Example:**

[Complete example]
```

**Applied Consistently:**
```markdown
### POST /users

Create a new user account.

**Authentication:** Required

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_123",
  "email": "user@example.com",
  "username": "johndoe"
}
```

**Errors:**
- `400`: Invalid input
- `401`: Unauthorized
- `409`: Email already exists

**Example:**
```bash
curl -X POST https://api.example.com/users \
  -H "Authorization: Bearer TOKEN" \
  -d '{"email":"user@example.com","username":"johndoe"}'
```

---

### GET /users/{id}

Retrieve a user by ID.

**Authentication:** Required

[Same structure follows...]
```

### Formatting Consistency

**Principle**: Use consistent formatting for common elements.

**Why It Matters**: Visual consistency creates professionalism and aids recognition.

**Formatting Standards:**
```markdown
## Formatting Guide

- **Code elements**: Use backticks: `variable_name`, `function()`, `"string"`
- **File paths**: Use backticks: `src/app.py`, `/etc/config.yml`
- **Commands**: Use code blocks with bash: ```bash npm start ```
- **Keyboard keys**: Use bold: Press **Ctrl+C**, Click **Enter**
- **UI elements**: Use bold: Click the **Submit** button
- **Parameters**: Use code style with type: `user_id` (integer)
- **Emphasis**: Use italic for *slight* emphasis, bold for **strong** emphasis
- **Notes/Warnings**: Use callouts (see below)
```

**Callout Formatting:**
```markdown
💡 **Tip**: This is a helpful tip or best practice.

⚠️ **Warning**: This is important information about potential problems.

🚨 **Danger**: This is critical information about destructive actions.

ℹ️ **Note**: This is supplementary information.

✅ **Success**: This indicates a successful outcome or correct approach.
```

## Version Management

### Document Version Strategy

**Principle**: Make clear which version of the product each piece of documentation describes.

**Why It Matters**: Users on different versions need different instructions.

**Approaches:**

**1. Multiple Documentation Versions:**
```
docs/
├── v1.x/
│   ├── api-reference.md
│   └── guides/
├── v2.x/
│   ├── api-reference.md
│   └── guides/
└── latest/  (symlink to latest version)
```

**2. Version Badges in Documents:**
```markdown
# Authentication

**Version:** 2.0+ | **Last Updated:** 2025-01-15

[Content for v2.0+]

---

## Legacy (v1.x)

⚠️ **Note**: This section applies to version 1.x only.

[Content for v1.x]
```

**3. Inline Version Indicators:**
```markdown
### create_user(email, name, role="user")

**Added in:** v1.0
**Modified in:** v2.0 (added role parameter)

Creates a new user.

**Parameters:**
- `email` (string): User email address
- `name` (string): Full name
- `role` (string): User role - **Added in v2.0**
```

### Deprecation Documentation

**Principle**: Clearly mark deprecated features and provide migration paths.

**Why It Matters**: Users need time to migrate and clear guidance on how.

**Deprecation Template:**
```markdown
### `old_function()` [Deprecated]

⚠️ **DEPRECATED**: This function is deprecated as of v2.0 and will be removed in v3.0.
**Use [`new_function()`](#new_function) instead.**

**Why deprecated:** The old function had inconsistent error handling and couldn't support new authentication methods.

**Migration Guide:**

```python
# Old way (v1.x - DEPRECATED)
result = old_function(user_id)

# New way (v2.0+)
result = new_function(user_id=user_id, auth_method="jwt")
```

**Breaking changes:**
1. Function now requires keyword arguments
2. New `auth_method` parameter is required
3. Return type changed from dict to User object

**Timeline:**
- **v2.0** (2025-01-15): Deprecated, still functional
- **v2.5** (2025-06-01): Deprecation warnings added
- **v3.0** (2026-01-01): Removed completely
```

## Review and Quality Assurance

### Documentation Review Checklist

**Technical Review:**
```markdown
Technical Accuracy Checklist:
- [ ] All code examples tested and working
- [ ] API signatures match actual implementation
- [ ] Configuration options are complete and correct
- [ ] Version information is accurate
- [ ] System requirements are current
- [ ] Links to code reference actual code
- [ ] Screenshots match current UI
- [ ] No outdated information
```

**Editorial Review:**
```markdown
Editorial Quality Checklist:
- [ ] Grammar and spelling checked
- [ ] Consistent terminology throughout
- [ ] Active voice used (except where passive is appropriate)
- [ ] Present tense used
- [ ] Clear, concise sentences
- [ ] Proper heading hierarchy
- [ ] Consistent formatting
- [ ] No jargon without explanation
- [ ] Audience-appropriate language
```

**Structural Review:**
```markdown
Structure and Navigation Checklist:
- [ ] Clear purpose statement
- [ ] Table of contents (for long pages)
- [ ] Logical information flow
- [ ] All links working
- [ ] Cross-references appropriate
- [ ] "See also" sections included
- [ ] Breadcrumb navigation clear
- [ ] Search-friendly headings
```

### Peer Review Process

**Review Workflow:**
```markdown
## Documentation PR Review Process

1. **Author Self-Review:**
   - Run spell check
   - Test all code examples
   - Check all links
   - Verify screenshots are current
   - Complete quality checklist

2. **Technical Review:**
   - Subject matter expert verifies technical accuracy
   - Tests code examples in clean environment
   - Validates configuration instructions
   - Checks for security issues in examples

3. **Editorial Review:**
   - Documentation team member reviews for:
     - Clarity and conciseness
     - Consistent style and tone
     - Proper grammar and spelling
     - Accessibility compliance

4. **Approval:**
   - Minimum 2 approvals required (1 technical, 1 editorial)
   - All comments addressed or acknowledged
   - Final author review after changes
```

## Maintenance Practices

### Documentation Lifecycle

**Regular Maintenance Schedule:**
```markdown
## Documentation Maintenance Calendar

**Weekly:**
- Review and respond to feedback/issues
- Update any broken links found
- Quick-fix typos and minor errors

**Monthly:**
- Review most-visited pages for accuracy
- Update screenshots if UI has changed
- Review and update version-specific information

**Quarterly:**
- Comprehensive review of core documentation
- Audit and cleanup of old/obsolete content
- Review and update examples for current best practices
- Check accessibility compliance

**Annually:**
- Full documentation audit
- Restructure if needed based on user feedback
- Major updates to reflect product evolution
- Review and update all diagrams and visuals
```

### Keeping Documentation Current

**Documentation in Definition of Done:**
```markdown
## Definition of Done for Features

A feature is not complete until:
- [ ] Code implemented and tested
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] **Documentation written or updated**
- [ ] **Code examples tested**
- [ ] **API reference updated**
- [ ] **Changelog entry added**
- [ ] Peer review completed
- [ ] Deployed to staging
```

**Documentation Requirements by Change Type:**
```markdown
## What Documentation Needs Updating?

**New Feature:**
- [ ] Feature guide or tutorial
- [ ] API reference (if applicable)
- [ ] Code examples
- [ ] Configuration reference
- [ ] Changelog entry

**Bug Fix:**
- [ ] Changelog entry
- [ ] Update any incorrect documentation
- [ ] Add to troubleshooting guide (if significant)

**Breaking Change:**
- [ ] Clear deprecation notice
- [ ] Migration guide
- [ ] Update all affected examples
- [ ] Prominent changelog entry
- [ ] Consider version-specific docs

**Performance Improvement:**
- [ ] Update performance documentation
- [ ] Changelog entry
- [ ] Update benchmarks if documented

**Security Fix:**
- [ ] Update security documentation
- [ ] Changelog entry (may omit details if vulnerability not yet widely known)
- [ ] Update authentication/authorization docs if affected
```

## Collaboration Best Practices

### Documentation Style Guide

**Create and Maintain a Style Guide:**
```markdown
# Documentation Style Guide

## Purpose
Ensure consistency across all documentation written by multiple contributors.

## Tone and Voice
- **Professional but friendly**: Approachable, not stuffy
- **Helpful**: Focus on user success
- **Confident**: "This works" not "This should work"
- **Inclusive**: Use gender-neutral language

## Writing Standards
[Include all standards from this document]

## Templates
[Include templates for common documentation types]

## Review Process
[Define how documentation is reviewed and approved]
```

### Contribution Guidelines

**Make It Easy to Contribute:**
```markdown
# Contributing to Documentation

We welcome documentation improvements! Here's how to contribute:

## Quick Fixes
For typos and small corrections:
1. Click "Edit this page" button
2. Make your change
3. Submit a pull request

## Larger Changes
For new content or significant rewrites:
1. Open an issue describing the proposed changes
2. Get feedback from maintainers
3. Fork the repository
4. Make your changes following our [Style Guide](STYLE_GUIDE.md)
5. Test all code examples
6. Submit a pull request

## Documentation Standards
- All code examples must be tested
- Follow the [Style Guide](STYLE_GUIDE.md)
- Use the appropriate [template](templates/)
- Include diagrams where helpful
- Add cross-references to related topics

## Review Process
1. Automated checks run (link checking, spell check)
2. Technical review for accuracy
3. Editorial review for clarity
4. Maintainer approval
5. Automated deployment
```

## Documentation Testing

### Automated Testing

**Link Checking:**
```bash
# Use a tool to check for broken links
npm install -g broken-link-checker

blc http://localhost:8000/docs -ro
```

**Code Example Testing:**
```python
# extract_code_examples.py
# Extract code blocks from markdown and test them

import re
import subprocess
import sys
from pathlib import Path

def extract_python_examples(markdown_file):
    """Extract Python code blocks from markdown."""
    content = Path(markdown_file).read_text()
    pattern = r'```python\n(.*?)```'
    return re.findall(pattern, content, re.DOTALL)

def test_example(code, file_name, block_number):
    """Test a single code example."""
    try:
        # Write to temp file
        temp_file = f"/tmp/test_{file_name}_{block_number}.py"
        Path(temp_file).write_text(code)

        # Run it
        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ {file_name} block {block_number} failed:")
            print(result.stderr.decode())
            return False

        print(f"✅ {file_name} block {block_number} passed")
        return True

    except subprocess.TimeoutExpired:
        print(f"❌ {file_name} block {block_number} timed out")
        return False

# Test all markdown files
docs_dir = Path("docs/")
all_passed = True

for md_file in docs_dir.glob("**/*.md"):
    examples = extract_python_examples(md_file)
    for i, code in enumerate(examples, 1):
        if not test_example(code, md_file.name, i):
            all_passed = False

sys.exit(0 if all_passed else 1)
```

**Spell Checking:**
```yaml
# .github/workflows/docs-quality.yml
name: Documentation Quality

on: [push, pull_request]

jobs:
  quality-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Spell check
        uses: rojopolis/spellcheck-github-actions@0.5.0
        with:
          config_path: .spellcheck.yml

      - name: Check links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          config-file: '.markdown-link-check.json'

      - name: Test code examples
        run: python scripts/extract_code_examples.py
```

## Performance and Accessibility

### Page Load Performance

**Principles:**
- Optimize images (compress, appropriate formats)
- Minimize external dependencies
- Use lazy loading for images
- Minimize JavaScript
- Cache aggressively

**Image Optimization:**
```markdown
## Image Guidelines

1. **Format:**
   - Use WebP when possible (with PNG/JPG fallback)
   - PNG for screenshots with text
   - JPG for photos
   - SVG for diagrams and icons

2. **Size:**
   - Max width: 1200px for full-width images
   - Max file size: 200KB per image
   - Compress using tools like ImageOptim or TinyPNG

3. **Alt Text:**
   - Always include descriptive alt text
   - Describe what's in the image, not just "screenshot"
   - Include any text visible in the image
```

### Accessibility Best Practices

**WCAG 2.1 AA Compliance:**

```markdown
## Accessibility Checklist

**Content:**
- [ ] Proper heading hierarchy (h1 → h2 → h3, no skipping)
- [ ] Meaningful link text ("read the installation guide" not "click here")
- [ ] Alt text for all images
- [ ] Text transcripts for video/audio
- [ ] Tables have proper headers
- [ ] Lists used for list content

**Design:**
- [ ] Sufficient color contrast (4.5:1 for body text, 3:1 for large text)
- [ ] Information not conveyed by color alone
- [ ] Text can be resized to 200% without losing functionality
- [ ] Focus indicators visible
- [ ] Keyboard navigation works for all features

**Code:**
- [ ] Semantic HTML used
- [ ] ARIA labels where appropriate
- [ ] Skip-to-content link available
- [ ] Language attribute set on HTML element
- [ ] Valid HTML (no major errors)
```

## Related Topics

- **Documentation Patterns**: See [patterns.md](patterns.md)
- **Advanced Documentation**: See [advanced-topics.md](advanced-topics.md)
- **Documentation Tools**: See [api-reference.md](api-reference.md)
