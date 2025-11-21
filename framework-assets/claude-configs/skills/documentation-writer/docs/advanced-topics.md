# Advanced Documentation Topics

## Table of Contents
- [Documentation Automation](#documentation-automation)
- [API Documentation Generation](#api-documentation-generation)
- [Internationalization (i18n)](#internationalization-i18n)
- [Documentation Testing](#documentation-testing)
- [Version Management Strategies](#version-management-strategies)
- [Documentation as a Service](#documentation-as-a-service)
- [Analytics and Metrics](#analytics-and-metrics)
- [AI-Assisted Documentation](#ai-assisted-documentation)
- [Interactive Documentation](#interactive-documentation)
- [Documentation Architecture](#documentation-architecture)

## Documentation Automation

### Continuous Documentation Deployment

**Strategy:** Automatically build and deploy documentation on every commit to keep docs synchronized with code.

**Implementation with GitHub Actions:**

```yaml
# .github/workflows/docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'src/**/*.py'  # If you extract docstrings
      - 'mkdocs.yml'
  pull_request:
    paths:
      - 'docs/**'

jobs:
  deploy-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for git info

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install mkdocs-material
          pip install mkdocs-git-revision-date-localized-plugin
          pip install mkdocstrings[python]

      - name: Build documentation
        run: mkdocs build --strict

      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: mkdocs gh-deploy --force

      - name: Upload artifacts (for PRs)
        if: github.event_name == 'pull_request'
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: site/
```

### Auto-Generated Documentation

**From Code Comments:**

```python
# src/api/users.py

def create_user(email: str, username: str, role: str = "user") -> dict:
    """
    Create a new user account.

    This function creates a user in the database and sends a welcome email.
    The email address must be unique and valid. Usernames must be 3-20 characters.

    Args:
        email (str): Valid email address for the user. Must be unique.
        username (str): Desired username. Must be 3-20 alphanumeric characters.
        role (str, optional): User role. Valid values: "user", "admin", "moderator".
            Defaults to "user".

    Returns:
        dict: Created user object with keys:
            - id (str): Unique user identifier
            - email (str): User's email address
            - username (str): User's username
            - role (str): User's role
            - created_at (str): ISO 8601 timestamp

    Raises:
        ValueError: If email is invalid or already exists
        ValueError: If username is invalid (length or characters)
        ValueError: If role is not one of the valid values

    Example:
        >>> user = create_user(
        ...     email="john@example.com",
        ...     username="johndoe",
        ...     role="user"
        ... )
        >>> print(user["id"])
        'usr_abc123'

    Note:
        This operation sends a welcome email asynchronously. The user is created
        immediately, but the email may take a few seconds to arrive.

    See Also:
        - update_user(): Update existing user
        - delete_user(): Delete a user account
        - get_user(): Retrieve user information
    """
    # Implementation here
    pass
```

**MkDocs Configuration for Auto-Generation:**

```yaml
# mkdocs.yml
site_name: My API Documentation
theme:
  name: material

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true
            show_symbol_type_heading: true
            show_symbol_type_toc: true
            members_order: source
            merge_init_into_class: true

nav:
  - Home: index.md
  - API Reference:
    - Users: api/users.md
    - Authentication: api/auth.md
```

**API Reference Page (auto-generated):**

```markdown
# User Management API

This module handles all user-related operations.

::: src.api.users
    options:
      show_source: true
      heading_level: 2
```

### OpenAPI/Swagger Generation

**FastAPI Automatic Documentation:**

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

app = FastAPI(
    title="User Management API",
    description="API for managing user accounts",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class UserCreate(BaseModel):
    """Request model for creating a user."""
    email: EmailStr = Field(..., description="Valid email address")
    username: str = Field(..., min_length=3, max_length=20, description="Username (3-20 chars)")
    role: Optional[str] = Field("user", description="User role: user, admin, or moderator")

    class Config:
        schema_extra = {
            "example": {
                "email": "john@example.com",
                "username": "johndoe",
                "role": "user"
            }
        }

class User(BaseModel):
    """User model."""
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")

@app.post(
    "/users",
    response_model=User,
    status_code=201,
    tags=["Users"],
    summary="Create a new user",
    description="Create a new user account with email, username, and role.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input"},
        409: {"description": "Email or username already exists"}
    }
)
async def create_user(user: UserCreate) -> User:
    """
    Create a new user account.

    - **email**: Must be a valid email address and unique
    - **username**: 3-20 alphanumeric characters, must be unique
    - **role**: Optional, defaults to "user"

    Returns the created user object with generated ID and timestamp.
    """
    # Implementation
    pass
```

**This automatically generates:**
- Interactive Swagger UI at `/docs`
- ReDoc documentation at `/redoc`
- OpenAPI schema at `/openapi.json`

### Documentation from Tests

**Extract Examples from Tests:**

```python
# tests/test_api.py
import pytest

def test_create_user_success():
    """
    Example: Create a user successfully

    This test demonstrates the happy path for user creation.
    """
    response = client.post("/users", json={
        "email": "test@example.com",
        "username": "testuser",
        "role": "user"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

def test_create_user_duplicate_email():
    """
    Example: Handle duplicate email error

    This test shows what happens when trying to create a user
    with an email that already exists.
    """
    # First user
    client.post("/users", json={
        "email": "duplicate@example.com",
        "username": "user1"
    })

    # Attempt duplicate
    response = client.post("/users", json={
        "email": "duplicate@example.com",
        "username": "user2"
    })

    assert response.status_code == 409
    assert response.json()["error"] == "Email already exists"
```

**Script to Extract Test Examples:**

```python
# scripts/extract_test_examples.py
import ast
import inspect

def extract_examples_from_tests(test_file):
    """Extract documented test cases as examples."""
    with open(test_file) as f:
        tree = ast.parse(f.read())

    examples = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            # Get docstring
            docstring = ast.get_docstring(node)
            if docstring and "Example:" in docstring:
                # Get source code
                source = ast.get_source_segment(open(test_file).read(), node)

                examples.append({
                    "title": docstring.split('\n')[0].replace("Example:", "").strip(),
                    "description": '\n'.join(docstring.split('\n')[1:]).strip(),
                    "code": source
                })

    return examples

# Generate examples documentation
examples = extract_examples_from_tests("tests/test_api.py")

with open("docs/examples/api-examples.md", "w") as f:
    f.write("# API Examples from Tests\n\n")
    for ex in examples:
        f.write(f"## {ex['title']}\n\n")
        f.write(f"{ex['description']}\n\n")
        f.write(f"```python\n{ex['code']}\n```\n\n")
```

## API Documentation Generation

### REST API Documentation Automation

**Using OpenAPI Specification:**

```yaml
# openapi.yml
openapi: 3.0.0
info:
  title: User Management API
  version: 2.0.0
  description: |
    Complete API for managing user accounts.

    ## Authentication
    All endpoints require Bearer token authentication.

    ## Rate Limiting
    - 100 requests per minute per IP
    - 1000 requests per hour per API key

servers:
  - url: https://api.example.com
    description: Production server
  - url: https://staging-api.example.com
    description: Staging server

paths:
  /users:
    post:
      summary: Create a new user
      description: |
        Create a new user account with email and username.
        Email must be unique and valid.
      tags:
        - Users
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
            examples:
              basic:
                summary: Basic user creation
                value:
                  email: john@example.com
                  username: johndoe
              admin:
                summary: Create admin user
                value:
                  email: admin@example.com
                  username: admin
                  role: admin
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Email or username already exists

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    UserCreate:
      type: object
      required:
        - email
        - username
      properties:
        email:
          type: string
          format: email
          example: john@example.com
        username:
          type: string
          minLength: 3
          maxLength: 20
          pattern: '^[a-zA-Z0-9]+$'
          example: johndoe
        role:
          type: string
          enum: [user, admin, moderator]
          default: user

    User:
      type: object
      properties:
        id:
          type: string
          example: usr_abc123
        email:
          type: string
          format: email
        username:
          type: string
        role:
          type: string
        created_at:
          type: string
          format: date-time

    Error:
      type: object
      properties:
        error:
          type: string
        details:
          type: object
```

**Generate Multiple Documentation Formats:**

```bash
# Install tools
npm install -g @redocly/cli

# Generate HTML documentation
redocly build-docs openapi.yml --output docs/api.html

# Generate Markdown
npx openapi-to-md openapi.yml > docs/api-reference.md

# Validate OpenAPI spec
redocly lint openapi.yml
```

### GraphQL Documentation

**Schema with Documentation:**

```graphql
"""
User management queries and mutations.
All operations require authentication.
"""
type Query {
  """
  Get a user by ID.

  Returns null if user doesn't exist or you don't have permission.

  Example:
    query {
      user(id: "usr_123") {
        id
        email
        username
      }
    }
  """
  user(
    "Unique user identifier"
    id: ID!
  ): User

  """
  Search for users.

  Supports pagination and filtering.

  Example:
    query {
      users(limit: 10, role: USER) {
        edges {
          node {
            id
            username
          }
        }
        pageInfo {
          hasNextPage
        }
      }
    }
  """
  users(
    "Maximum number of results (1-100)"
    limit: Int = 10

    "Filter by user role"
    role: Role

    "Pagination cursor"
    after: String
  ): UserConnection!
}

"""
Possible user roles in the system.
"""
enum Role {
  "Standard user with basic permissions"
  USER

  "Moderator with content management permissions"
  MODERATOR

  "Administrator with full system access"
  ADMIN
}

"""
A user account in the system.
"""
type User {
  "Unique user identifier"
  id: ID!

  "User's email address (only visible to user themselves or admins)"
  email: String!

  "Public username"
  username: String!

  "User's role determining permissions"
  role: Role!

  "ISO 8601 timestamp of account creation"
  createdAt: DateTime!
}
```

**Auto-Generate Documentation:**

```bash
# Using GraphQL Inspector
npm install -g @graphql-inspector/cli

# Generate Markdown docs
graphql-inspector introspect schema.graphql --write docs/graphql-schema.md

# Using Spectaql
npm install -g spectaql

# Generate HTML docs
spectaql config.yml
```

## Internationalization (i18n)

### Multi-Language Documentation Strategy

**Directory Structure:**

```
docs/
├── en/              # English (default)
│   ├── index.md
│   ├── guides/
│   └── api/
├── es/              # Spanish
│   ├── index.md
│   ├── guides/
│   └── api/
├── fr/              # French
│   ├── index.md
│   ├── guides/
│   └── api/
└── ja/              # Japanese
    ├── index.md
    ├── guides/
    └── api/
```

**MkDocs i18n Configuration:**

```yaml
# mkdocs.yml
plugins:
  - i18n:
      default_language: en
      languages:
        en:
          name: English
          build: true
        es:
          name: Español
          build: true
        fr:
          name: Français
          build: true
        ja:
          name: 日本語
          build: true
      nav_translations:
        es:
          Home: Inicio
          Guides: Guías
          API Reference: Referencia de API
        fr:
          Home: Accueil
          Guides: Guides
          API Reference: Référence API
```

### Translation Workflow

**1. Mark Translatable Content:**

```markdown
<!-- en/guides/quickstart.md -->
# Quick Start Guide

{% trans %}
Welcome to our API! This guide will help you get started in 5 minutes.
{% endtrans %}

## {% trans %}Installation{% endtrans %}

{% trans %}
First, install the client library:
{% endtrans %}

```bash
pip install our-api-client
```

{% trans %}
This installs the Python client for our API.
{% endtrans %}
```

**2. Extract Translatable Strings:**

```bash
# Extract all translatable strings
pybabel extract -F babel.cfg -o messages.pot docs/

# Initialize new language
pybabel init -i messages.pot -d docs/locales -l es

# Update existing translations
pybabel update -i messages.pot -d docs/locales
```

**3. Translation File:**

```po
# docs/locales/es/LC_MESSAGES/messages.po
msgid "Quick Start Guide"
msgstr "Guía de Inicio Rápido"

msgid "Welcome to our API! This guide will help you get started in 5 minutes."
msgstr "¡Bienvenido a nuestra API! Esta guía te ayudará a comenzar en 5 minutos."

msgid "Installation"
msgstr "Instalación"

msgid "First, install the client library:"
msgstr "Primero, instala la biblioteca cliente:"
```

**4. Build Translated Docs:**

```bash
# Compile translations
pybabel compile -d docs/locales

# Build all languages
mkdocs build

# Serves localized versions at /en/, /es/, /fr/, /ja/
```

### Code Examples in Multiple Languages

**Tabbed Code Examples:**

```markdown
# API Usage

=== "Python"

    ```python
    import api_client

    client = api_client.Client(api_key="YOUR_KEY")
    user = client.users.create(
        email="user@example.com",
        username="johndoe"
    )
    print(f"Created: {user.id}")
    ```

=== "JavaScript"

    ```javascript
    const ApiClient = require('api-client');

    const client = new ApiClient({ apiKey: 'YOUR_KEY' });

    const user = await client.users.create({
      email: 'user@example.com',
      username: 'johndoe'
    });

    console.log(`Created: ${user.id}`);
    ```

=== "Ruby"

    ```ruby
    require 'api_client'

    client = ApiClient::Client.new(api_key: 'YOUR_KEY')

    user = client.users.create(
      email: 'user@example.com',
      username: 'johndoe'
    )

    puts "Created: #{user.id}"
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.example.com/users \
      -H "Authorization: Bearer YOUR_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "user@example.com",
        "username": "johndoe"
      }'
    ```
```

## Documentation Testing

### Automated Documentation Quality Checks

**Comprehensive Test Suite:**

```python
# tests/test_documentation.py
import pytest
from pathlib import Path
import re
import requests

DOCS_DIR = Path("docs/")

def test_no_broken_internal_links():
    """Verify all internal markdown links work."""
    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text()

        # Find all markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_url in links:
            if link_url.startswith(('http://', 'https://')):
                continue  # Skip external links

            # Resolve relative link
            target = (md_file.parent / link_url).resolve()

            # Handle anchor links
            if '#' in link_url:
                target = Path(str(target).split('#')[0])

            assert target.exists(), f"Broken link in {md_file}: {link_url}"

def test_no_broken_external_links():
    """Verify external links are accessible."""
    external_links = set()

    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text()
        links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', content)

        for link_text, link_url in links:
            external_links.add(link_url)

    for url in external_links:
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            assert response.status_code < 400, f"Broken external link: {url}"
        except requests.RequestException as e:
            pytest.fail(f"Failed to check {url}: {e}")

def test_all_code_blocks_have_language():
    """Ensure all code blocks specify a language for syntax highlighting."""
    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text()

        # Find code blocks without language
        invalid_blocks = re.findall(r'^```\n', content, re.MULTILINE)

        assert len(invalid_blocks) == 0, \
            f"{md_file} has {len(invalid_blocks)} code blocks without language specification"

def test_no_todo_or_fixme_in_docs():
    """Ensure no TODO or FIXME comments in published docs."""
    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text().lower()

        assert 'todo' not in content, f"{md_file} contains TODO"
        assert 'fixme' not in content, f"{md_file} contains FIXME"

def test_all_images_have_alt_text():
    """Verify all images have alt text for accessibility."""
    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text()

        # Find images without alt text: ![](image.png)
        images_without_alt = re.findall(r'!\[\]\([^)]+\)', content)

        assert len(images_without_alt) == 0, \
            f"{md_file} has {len(images_without_alt)} images without alt text"

def test_consistent_terminology():
    """Check for consistent terminology usage."""
    terminology_map = {
        'api key': ['API token', 'access key', 'auth key'],  # Incorrect variations
        'endpoint': ['route', 'URL path'],
        'parameter': ['param', 'arg'],
    }

    issues = []

    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text().lower()

        for correct_term, incorrect_terms in terminology_map.items():
            for incorrect in incorrect_terms:
                if incorrect.lower() in content:
                    issues.append(f"{md_file}: Use '{correct_term}' instead of '{incorrect}'")

    assert len(issues) == 0, '\n'.join(issues)

def test_code_examples_are_runnable():
    """Extract and test Python code examples."""
    import tempfile
    import subprocess

    for md_file in DOCS_DIR.glob("**/*.md"):
        content = md_file.read_text()

        # Find Python code blocks
        python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

        for i, code in enumerate(python_blocks):
            # Skip incomplete examples (marked with ...)
            if '...' in code or 'pass' in code:
                continue

            # Create temp file and run
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ['python', temp_path],
                    capture_output=True,
                    timeout=5
                )

                assert result.returncode == 0, \
                    f"Code example {i} in {md_file} failed:\n{result.stderr.decode()}"

            except subprocess.TimeoutExpired:
                pytest.fail(f"Code example {i} in {md_file} timed out")
            finally:
                Path(temp_path).unlink()
```

## Version Management Strategies

### Versioned Documentation Hosting

**Strategy 1: Multiple Versions Side-by-Side**

```
docs.example.com/
├── latest/          → symlink to v2.0
├── v2.0/
│   ├── index.html
│   └── guides/
├── v1.5/
│   ├── index.html
│   └── guides/
└── v1.0/
    ├── index.html
    └── guides/
```

**Build Script:**

```bash
#!/bin/bash
# scripts/build-versioned-docs.sh

# Build current version
mkdocs build -d site/latest

# Copy to versioned directory
VERSION=$(git describe --tags --abbrev=0)
cp -r site/latest site/$VERSION

# Update symlink
ln -sf $VERSION site/latest

# Deploy all versions
aws s3 sync site/ s3://docs-bucket/ --delete
```

**Version Selector in HTML:**

```html
<!-- In mkdocs theme -->
<div class="version-selector">
  <select onchange="location = this.value;">
    <option value="/v2.0/">v2.0 (Latest)</option>
    <option value="/v1.5/">v1.5</option>
    <option value="/v1.0/">v1.0</option>
  </select>
</div>
```

### Version Branches Strategy

```bash
# Create documentation branch for each release
git checkout -b docs/v1.0 v1.0
git checkout -b docs/v1.5 v1.5
git checkout -b docs/v2.0 v2.0

# Build from each branch
git checkout docs/v1.0
mkdocs build -d versions/v1.0

git checkout docs/v1.5
mkdocs build -d versions/v1.5

git checkout docs/v2.0
mkdocs build -d versions/latest
```

## Documentation as a Service

### Headless CMS for Documentation

**Using Contentful/Strapi:**

```javascript
// docs-fetcher.js
const contentful = require('contentful');

const client = contentful.createClient({
  space: process.env.CONTENTFUL_SPACE_ID,
  accessToken: process.env.CONTENTFUL_ACCESS_TOKEN
});

async function fetchDocumentation() {
  const entries = await client.getEntries({
    content_type: 'documentationPage',
    order: 'fields.order'
  });

  return entries.items.map(item => ({
    id: item.sys.id,
    title: item.fields.title,
    slug: item.fields.slug,
    content: item.fields.content,  // Markdown content
    category: item.fields.category,
    updatedAt: item.sys.updatedAt
  }));
}

// Generate static site from CMS content
async function generateDocs() {
  const docs = await fetchDocumentation();

  for (const doc of docs) {
    const outputPath = `docs/${doc.category}/${doc.slug}.md`;
    fs.writeFileSync(outputPath, doc.content);
  }

  // Build with MkDocs
  execSync('mkdocs build');
}

generateDocs();
```

## Analytics and Metrics

### Documentation Analytics

**Track Documentation Usage:**

```javascript
// docs/javascripts/analytics.js
document.addEventListener('DOMContentLoaded', function() {
  // Track page views
  if (typeof gtag !== 'undefined') {
    gtag('event', 'page_view', {
      page_title: document.title,
      page_path: location.pathname
    });
  }

  // Track search queries
  const searchInput = document.querySelector('.md-search__input');
  if (searchInput) {
    searchInput.addEventListener('input', debounce(function(e) {
      if (e.target.value.length > 2) {
        gtag('event', 'search', {
          search_term: e.target.value
        });
      }
    }, 1000));
  }

  // Track helpful/not helpful feedback
  document.querySelectorAll('.feedback-button').forEach(button => {
    button.addEventListener('click', function() {
      gtag('event', 'feedback', {
        page_path: location.pathname,
        helpful: this.dataset.helpful === 'yes'
      });
    });
  });

  // Track time on page
  let startTime = Date.now();
  window.addEventListener('beforeunload', function() {
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    navigator.sendBeacon('/api/analytics', JSON.stringify({
      event: 'time_on_page',
      page: location.pathname,
      seconds: timeSpent
    }));
  });
});

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}
```

**Metrics Dashboard:**

```python
# scripts/docs_metrics.py
from google.analytics import reporting
from collections import Counter
import json

def get_documentation_metrics():
    """Fetch key metrics from Google Analytics."""
    # Top viewed pages
    top_pages = fetch_top_pages(limit=20)

    # Search queries (what are users looking for?)
    search_queries = fetch_search_queries(limit=50)

    # Pages with low engagement (high bounce rate, low time on page)
    low_engagement = fetch_low_engagement_pages()

    # 404 errors (broken links users are finding)
    not_found = fetch_404_errors()

    return {
        "top_pages": top_pages,
        "search_queries": search_queries,
        "low_engagement": low_engagement,
        "not_found": not_found
    }

def generate_insights(metrics):
    """Generate actionable insights from metrics."""
    insights = []

    # What's popular but has low time-on-page? (Might be unclear)
    for page in metrics["top_pages"]:
        if page["avg_time_on_page"] < 30:  # Less than 30 seconds
            insights.append({
                "type": "clarity_issue",
                "page": page["path"],
                "message": f"Popular page but users leave quickly. Consider improving clarity."
            })

    # What are people searching for that we don't have?
    common_searches = [q for q, count in metrics["search_queries"] if count > 10]
    for query in common_searches:
        if not page_exists_for_query(query):
            insights.append({
                "type": "missing_content",
                "query": query,
                "message": f"Users search for '{query}' but we don't have content for it."
            })

    return insights
```

## AI-Assisted Documentation

### Using AI for Documentation

**AI-Powered Documentation Generation:**

```python
# scripts/ai_doc_generator.py
import anthropic
import ast

def generate_function_documentation(source_code):
    """Use Claude to generate comprehensive documentation."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Generate comprehensive documentation for this Python function.
Include:
- Purpose and description
- Parameter descriptions with types
- Return value description
- Example usage
- Common pitfalls

Function code:
```python
{source_code}
```"""
        }]
    )

    return message.content[0].text

# Extract and document all functions
def document_module(module_path):
    """Generate documentation for all functions in a module."""
    with open(module_path) as f:
        tree = ast.parse(f.read())

    docs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            source = ast.get_source_segment(open(module_path).read(), node)
            docs.append({
                "function": node.name,
                "documentation": generate_function_documentation(source)
            })

    return docs
```

## Interactive Documentation

### Live Code Playgrounds

**Embedded Code Execution:**

```html
<!-- Using RunKit for Node.js -->
<div id="runkit-embed"></div>

<script src="https://embed.runkit.com"></script>
<script>
var notebook = RunKit.createNotebook({
  element: document.getElementById("runkit-embed"),
  source: `
const apiClient = require('api-client');

const client = new apiClient({ apiKey: 'demo_key' });

// Try modifying this code!
const users = await client.users.list({ limit: 5 });
console.log(users);
  `,
  nodeVersion: "18.x.x"
});
</script>
```

### Interactive API Explorer

**Built into Documentation:**

```html
<!-- API Try-It Component -->
<div class="api-explorer">
  <h3>POST /users</h3>

  <form id="api-form">
    <label>
      Authorization:
      <input type="text" name="auth" placeholder="Bearer YOUR_TOKEN">
    </label>

    <label>
      Email:
      <input type="email" name="email" required>
    </label>

    <label>
      Username:
      <input type="text" name="username" required>
    </label>

    <button type="submit">Try It</button>
  </form>

  <div id="response" style="display:none;">
    <h4>Response:</h4>
    <pre><code id="response-body"></code></pre>
  </div>
</div>

<script>
document.getElementById('api-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const response = await fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
      'Authorization': formData.get('auth'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: formData.get('email'),
      username: formData.get('username')
    })
  });

  const data = await response.json();
  document.getElementById('response').style.display = 'block';
  document.getElementById('response-body').textContent = JSON.stringify(data, null, 2);
});
</script>
```

## Documentation Architecture

### Scalable Documentation Systems

**Monorepo Documentation:**

```
project/
├── packages/
│   ├── api/
│   │   ├── src/
│   │   └── docs/
│   ├── client/
│   │   ├── src/
│   │   └── docs/
│   └── cli/
│       ├── src/
│       └── docs/
└── docs/
    ├── index.md
    ├── guides/
    └── api/
        ├── api-package.md      → Aggregates from packages/api/docs
        ├── client-package.md   → Aggregates from packages/client/docs
        └── cli-package.md      → Aggregates from packages/cli/docs
```

**Aggregation Script:**

```javascript
// scripts/aggregate-docs.js
const fs = require('fs-extra');
const glob = require('glob');

function aggregateDocumentation() {
  // Find all package docs
  const docsDirs = glob.sync('packages/*/docs');

  for (const docsDir of docsDirs) {
    const packageName = docsDir.split('/')[1];

    // Copy to central docs
    fs.copySync(
      docsDir,
      `docs/api/${packageName}`,
      { overwrite: true }
    );

    // Add package context to each file
    const files = glob.sync(`docs/api/${packageName}/**/*.md`);
    for (const file of files) {
      let content = fs.readFileSync(file, 'utf8');

      // Add breadcrumb
      content = `[Documentation Home](/) > [API](../) > [${packageName}](./)

${content}`;

      fs.writeFileSync(file, content);
    }
  }
}

aggregateDocumentation();
```

## Related Topics

- **Core Documentation Principles**: See [core-concepts.md](core-concepts.md)
- **Writing Best Practices**: See [best-practices.md](best-practices.md)
- **Documentation Patterns**: See [patterns.md](patterns.md)
- **Troubleshooting Documentation**: See [troubleshooting.md](troubleshooting.md)
