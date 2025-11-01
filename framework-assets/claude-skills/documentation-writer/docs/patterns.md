# Documentation Patterns

## Table of Contents
- [Document Structure Patterns](#document-structure-patterns)
- [API Documentation Patterns](#api-documentation-patterns)
- [Tutorial Patterns](#tutorial-patterns)
- [Navigation Patterns](#navigation-patterns)
- [Code Example Patterns](#code-example-patterns)
- [Error Documentation Patterns](#error-documentation-patterns)
- [Versioning Patterns](#versioning-patterns)
- [Search Optimization Patterns](#search-optimization-patterns)
- [Cross-Reference Patterns](#cross-reference-patterns)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Document Structure Patterns

### The Inverted Pyramid Pattern

**When to Use:** Most documentation, especially user guides and how-tos.

**Structure:**
1. **Most Important Information First**: Answer the main question immediately
2. **Supporting Details**: Provide necessary context and details
3. **Background Information**: Historical context, edge cases, alternatives

**Example:**
```markdown
# How to Reset Your Password

Click the "Forgot Password?" link on the login page, enter your email, and check your inbox for a reset link.

## Detailed Steps

1. Go to the login page at https://app.example.com/login
2. Click the "Forgot Password?" link below the password field
3. Enter your registered email address
4. Click "Send Reset Link"
5. Check your email inbox (and spam folder if needed)
6. Click the link in the email (valid for 24 hours)
7. Enter and confirm your new password
8. Click "Reset Password"

You'll be automatically logged in with your new password.

## Troubleshooting

**Didn't receive the email?**
- Check your spam/junk folder
- Verify you entered the correct email
- Wait 5-10 minutes for delivery
- Try again or contact support if it doesn't arrive

## Why This Process?

We use email verification to ensure account security. The reset link expires after 24 hours to prevent unauthorized access if someone gains access to your email later.
```

### The Tutorial Pattern

**When to Use:** Teaching concepts through hands-on practice.

**Structure:**
1. **Learning Objectives**: What the user will accomplish
2. **Prerequisites**: Required knowledge and setup
3. **Estimated Time**: How long it takes
4. **Step-by-Step Instructions**: Detailed, sequential steps
5. **Checkpoints**: Ways to verify progress
6. **Summary**: Recap of what was learned
7. **Next Steps**: Where to go from here

**Template:**
```markdown
# Tutorial: [Title]

Learn [specific skill or concept] by [what you'll build/do].

## What You'll Learn
- Skill/concept 1
- Skill/concept 2
- Skill/concept 3

## Prerequisites
- Requirement 1 (with link to setup guide)
- Requirement 2
- Estimated time: XX minutes
- Skill level: Beginner/Intermediate/Advanced

## Overview

[Brief description of what you'll build and why it's useful]

## Step 1: [First Major Task]

[Introduction to this step]

```language
[Code for this step]
```

**What this does:**
[Explanation]

**Checkpoint:** You should now see/have [expected result].

## Step 2: [Next Major Task]

[Continue pattern...]

## Complete Code

Here's the complete code for reference:

```language
[Full, working code]
```

## What You Learned

In this tutorial, you:
- Learned [concept 1]
- Built [thing 1]
- Implemented [feature 1]

## Next Steps

Now that you understand [concept], you can:
- Try [exercise 1]
- Learn about [related topic] (link)
- Build [suggested project]

## Troubleshooting

[Common issues specific to this tutorial]
```

### The Reference Pattern

**When to Use:** API documentation, configuration references, command references.

**Structure:**
```markdown
## [Function/Class/Command Name]

[One-sentence description]

### Syntax

```language
[Function signature or command syntax]
```

### Description

[Detailed description of what it does, when to use it, how it works]

### Parameters / Options

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| param1 | string | Yes | - | Description with constraints |
| param2 | integer | No | 0 | Description with valid range |
| param3 | boolean | No | false | Description with behavior |

### Returns / Output

[What it returns, including type and structure]

### Errors / Exceptions

| Error | Cause | Resolution |
|-------|-------|------------|
| ErrorType1 | When X happens | Do Y to fix |
| ErrorType2 | When Z is invalid | Ensure Z is valid |

### Examples

#### Example 1: Basic Usage

```language
[Simple, common case]
```

[Explanation]

#### Example 2: Advanced Usage

```language
[Complex case showing multiple features]
```

[Explanation]

### Notes

- Note 1 about behavior
- Note 2 about performance
- Note 3 about compatibility

### See Also

- [Related function 1](link)
- [Related function 2](link)
```

### The Problem-Solution Pattern

**When to Use:** Troubleshooting guides, error documentation, FAQs.

**Structure:**
```markdown
# [Problem Statement as User Would Describe It]

## Symptoms

- Symptom 1: What the user observes
- Symptom 2: Error messages or behavior
- Symptom 3: When/where it occurs

## Cause

[Explanation of why this problem occurs]

## Solution

### Quick Fix

[Immediate solution for users who just want it fixed]

```language
[Code or commands to fix it]
```

### Detailed Explanation

[Why this fixes it, what it does]

### Prevention

[How to avoid this problem in the future]

## Alternative Solutions

### Option 1: [Alternative approach]

[When to use this instead]

```language
[Alternative code/commands]
```

### Option 2: [Another alternative]

[Trade-offs and considerations]

## Related Issues

- [Related problem 1](link)
- [Related problem 2](link)
```

## API Documentation Patterns

### RESTful API Endpoint Pattern

**Standard Structure for Every Endpoint:**

```markdown
## [METHOD] /path/to/resource/{id}

[One-line description]

### Authentication

[Required/Optional, what type]

### Rate Limiting

[Rate limit info if applicable]

### Request

**Path Parameters:**
- `id` (string): [Description, format, example]

**Query Parameters:**
- `param1` (string, optional): [Description, default value]
- `param2` (integer, optional): [Description, valid range]

**Request Headers:**
- `Authorization`: Bearer token (required)
- `Content-Type`: application/json (required)

**Request Body:**

```json
{
  "field1": "value",
  "field2": 123,
  "nested": {
    "field3": true
  }
}
```

**Field Descriptions:**
- `field1` (string, required): [Description, constraints]
- `field2` (integer, optional): [Description, default]
- `nested.field3` (boolean, required): [Description]

### Response

**Success Response (200 OK):**

```json
{
  "id": "abc123",
  "field1": "value",
  "field2": 123,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Response Fields:**
- `id`: Unique identifier
- `created_at`: ISO 8601 timestamp

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 400 Bad Request | Invalid input | `{"error": "field1 is required"}` |
| 401 Unauthorized | Missing/invalid auth | `{"error": "Invalid token"}` |
| 404 Not Found | Resource doesn't exist | `{"error": "User not found"}` |
| 429 Too Many Requests | Rate limit exceeded | `{"error": "Rate limit exceeded", "retry_after": 60}` |

### Examples

#### cURL

```bash
curl -X POST https://api.example.com/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field1": "value",
    "field2": 123
  }'
```

#### Python

```python
import requests

response = requests.post(
    "https://api.example.com/users",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"field1": "value", "field2": 123}
)

data = response.json()
print(f"Created: {data['id']}")
```

#### JavaScript

```javascript
const response = await fetch('https://api.example.com/users', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    field1: 'value',
    field2: 123
  })
});

const data = await response.json();
console.log(`Created: ${data.id}`);
```

### Notes

[Any important notes about behavior, performance, or gotchas]
```

### GraphQL API Pattern

```markdown
## [Query/Mutation Name]

[Description]

### Schema

```graphql
type Query {
  queryName(
    arg1: String!
    arg2: Int
  ): ReturnType
}

type ReturnType {
  field1: String!
  field2: Int
  nested: NestedType
}
```

### Arguments

- `arg1` (String!, required): [Description]
- `arg2` (Int, optional): [Description, default value]

### Returns

[Description of return type]

### Example Query

```graphql
query {
  queryName(arg1: "value", arg2: 10) {
    field1
    field2
    nested {
      nestedField
    }
  }
}
```

### Example Response

```json
{
  "data": {
    "queryName": {
      "field1": "value",
      "field2": 10,
      "nested": {
        "nestedField": "value"
      }
    }
  }
}
```

### Client Example

```javascript
import { gql, useQuery } from '@apollo/client';

const QUERY = gql`
  query GetData($arg1: String!, $arg2: Int) {
    queryName(arg1: $arg1, arg2: $arg2) {
      field1
      field2
    }
  }
`;

function Component() {
  const { data, loading, error } = useQuery(QUERY, {
    variables: { arg1: "value", arg2: 10 }
  });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return <div>{data.queryName.field1}</div>;
}
```
```

## Tutorial Patterns

### The Progressive Complexity Pattern

**Structure:** Start with simplest possible example, add complexity incrementally.

```markdown
# Tutorial: [Topic]

## Part 1: The Absolute Basics

Let's start with the simplest possible version:

```language
[Minimal working example - 5-10 lines]
```

This works, but it's limited because [limitation].

## Part 2: Adding [Feature]

Let's make it more useful by adding [feature]:

```language
[Previous code + new feature - 10-20 lines]
```

Now it can [new capability], but we still need [next thing].

## Part 3: Handling [Complexity]

Real-world usage requires handling [complexity]:

```language
[Previous code + error handling/edge cases - 20-40 lines]
```

This is now production-ready because [why].

## Part 4: Advanced Techniques

For advanced use cases, you can [advanced technique]:

```language
[Full-featured version - 40+ lines]
```
```

### The Parallel Comparison Pattern

**When to Use:** Showing migration paths, comparing approaches, explaining choices.

```markdown
# [Feature]: Old vs New Approach

## Old Approach (Before v2.0)

```language
[Old code]
```

**Problems with this approach:**
- Problem 1: [Explanation]
- Problem 2: [Explanation]
- Problem 3: [Explanation]

## New Approach (v2.0+)

```language
[New code]
```

**Benefits of new approach:**
- ✅ Benefit 1: [Explanation]
- ✅ Benefit 2: [Explanation]
- ✅ Benefit 3: [Explanation]

## Migration Guide

To migrate from old to new:

1. **Step 1**: [What to change]

```diff
- old_code()
+ new_code()
```

2. **Step 2**: [Next change]

```diff
- old_pattern
+ new_pattern
```

## Side-by-Side Comparison

| Aspect | Old Approach | New Approach |
|--------|--------------|--------------|
| Performance | Slow (5s avg) | Fast (0.5s avg) |
| Memory | High (500MB) | Low (50MB) |
| Complexity | High | Medium |
| Features | Limited | Full-featured |
```

## Navigation Patterns

### Breadcrumb Navigation

```markdown
[Home](/) > [Documentation](/docs) > [Guides](/docs/guides) > Current Page

# Current Page Title

[Content...]
```

### Hub and Spoke Pattern

**Hub Page (Overview):**
```markdown
# [Topic] Documentation

[Overview paragraph]

## Getting Started

New to [topic]? Start here:

1. **[Installation Guide](guides/installation.md)**: Set up your environment
2. **[Quick Start](guides/quickstart.md)**: Build your first [thing] in 5 minutes
3. **[Core Concepts](concepts/overview.md)**: Understand the fundamentals

## Guides

**By Task:**
- [Task 1 Guide](guides/task1.md): How to accomplish task 1
- [Task 2 Guide](guides/task2.md): How to accomplish task 2
- [Task 3 Guide](guides/task3.md): How to accomplish task 3

**By Feature:**
- [Feature A](features/feature-a.md): Everything about feature A
- [Feature B](features/feature-b.md): Everything about feature B

## Reference

- **[API Reference](reference/api.md)**: Complete API documentation
- **[Configuration](reference/config.md)**: All configuration options
- **[CLI Reference](reference/cli.md)**: Command-line interface

## Resources

- [Troubleshooting](resources/troubleshooting.md)
- [FAQ](resources/faq.md)
- [Examples](examples/)
```

**Spoke Pages (Individual Topics):** Link back to hub and to related spokes.

```markdown
[← Back to Documentation Home](/docs)

# [Specific Topic]

[Content...]

## Related Topics

- [Related Topic 1](../related1.md)
- [Related Topic 2](../related2.md)

## Next Steps

- [What to Learn Next](../next-topic.md)

[← Back to Documentation Home](/docs) | [Next: Another Topic →](../next.md)
```

### Table of Contents Pattern

**For Long Pages:**

```markdown
# Long Document Title

## Table of Contents

- [Section 1](#section-1)
  - [Subsection 1.1](#subsection-11)
  - [Subsection 1.2](#subsection-12)
- [Section 2](#section-2)
  - [Subsection 2.1](#subsection-21)
  - [Subsection 2.2](#subsection-22)
- [Section 3](#section-3)

---

## Section 1

[Content...]

### Subsection 1.1

[Content...]

[⬆ Back to top](#table-of-contents)
```

## Code Example Patterns

### The Annotated Example Pattern

```markdown
## Example: [Description]

```language
# 1. Setup and imports
import required_module

# 2. Configuration
config = {
    "option1": "value1",  # Controls X behavior
    "option2": 123,       # Must be between 1-1000
}

# 3. Main logic
result = perform_operation(
    data=input_data,      # Your input data here
    config=config,        # Configuration from step 2
    validate=True         # Always validate in production
)

# 4. Error handling
if result.success:
    print(f"Success: {result.data}")
else:
    # Log the error for debugging
    logger.error(f"Operation failed: {result.error}")
    # Implement retry logic or fallback
    handle_error(result.error)
```

**Line-by-line explanation:**

1. **Lines 1-2**: Import the required module for this operation
2. **Lines 4-7**: Configure the operation with two options:
   - `option1` controls X behavior (values: "value1", "value2", "value3")
   - `option2` sets the Y parameter (valid range: 1-1000)
3. **Lines 9-13**: Execute the main operation:
   - `data`: Your input data (must be a list or dict)
   - `config`: Pass our configuration
   - `validate`: Enable input validation (recommended for production)
4. **Lines 15-22**: Handle the result:
   - Check `result.success` to determine if operation succeeded
   - On success, process `result.data`
   - On failure, log error and implement recovery logic

**Common mistakes:**
- ❌ Forgetting to set `validate=True` in production
- ❌ Not handling the error case
- ❌ Using `option2` values outside valid range

**Performance note:** This operation is O(n) where n is the size of input_data.
```

### The Before/After Pattern

```markdown
## Example: [Task] - Before and After

### ❌ Before (Don't Do This)

```language
[Problematic code]
```

**Problems:**
- Problem 1: [Explanation]
- Problem 2: [Explanation]
- Problem 3: [Explanation]

### ✅ After (Do This Instead)

```language
[Improved code]
```

**Improvements:**
- ✅ Fix 1: [Explanation]
- ✅ Fix 2: [Explanation]
- ✅ Fix 3: [Explanation]

**Why this is better:**
[Detailed explanation of benefits]
```

### The Progressive Example Pattern

```markdown
## Example: Building [Feature] Step by Step

### Step 1: Basic Version

```language
[Minimal code - 10 lines]
```

**What this does:** [Explanation]
**Limitations:** Can only [limited capability]

### Step 2: Add Error Handling

```language
[Previous code + error handling - 20 lines]
```

**New capabilities:**
- ✅ Handles [error type 1]
- ✅ Handles [error type 2]

### Step 3: Add Configuration

```language
[Previous code + configuration - 30 lines]
```

**New capabilities:**
- ✅ Configurable [option 1]
- ✅ Configurable [option 2]

### Step 4: Production-Ready Version

```language
[Full code with logging, monitoring - 50 lines]
```

**This version includes:**
- ✅ Complete error handling
- ✅ Logging and monitoring
- ✅ Configuration options
- ✅ Input validation
- ✅ Performance optimization

This is suitable for production use.
```

## Error Documentation Patterns

### Error Reference Pattern

```markdown
## Error: [ERROR_CODE] - [Error Message]

### Description

[What this error means in user-friendly terms]

### Common Causes

1. **Cause 1**: [Explanation]
   - **Check for**: [What to look for]
   - **Example scenario**: [When this happens]

2. **Cause 2**: [Explanation]
   - **Check for**: [What to look for]
   - **Example scenario**: [When this happens]

### Solution

#### Quick Fix

For most cases, this fixes it:

```language
[Quick solution code/commands]
```

#### Detailed Solution

**If quick fix doesn't work:**

1. **Verify**: [What to check]
   ```language
   [Verification command]
   ```

2. **Fix**: [What to change]
   ```language
   [Fix command]
   ```

3. **Validate**: [How to confirm it's fixed]
   ```language
   [Validation command]
   ```

### Prevention

Avoid this error by:
- [Prevention tip 1]
- [Prevention tip 2]
- [Prevention tip 3]

### Example

**Scenario that triggers this error:**

```language
[Code that causes the error]
```

**Output:**
```
[Error message]
```

**Fixed version:**

```language
[Corrected code]
```

**Output:**
```
[Success message]
```

### Related Errors

- [Related error 1](error1.md)
- [Related error 2](error2.md)

### Still Having Issues?

If this doesn't resolve your issue:
1. Check [troubleshooting guide](../troubleshooting.md)
2. Search [community forum](https://forum.example.com)
3. [Contact support](https://support.example.com)
```

## Versioning Patterns

### Version Badge Pattern

```markdown
# Feature Name

**Version**: 2.0+ | **Added**: 2025-01-01 | **Updated**: 2025-01-15

[Content for current version...]

---

## Version History

### Version 2.0 Changes (2025-01-01)
- ✨ Added: New capability X
- 🔧 Changed: Behavior Y now works differently
- ⚠️ Deprecated: Old method Z (use Z2 instead)

### Version 1.5 Changes (2024-06-01)
- 🐛 Fixed: Issue with edge case
- ⚡ Improved: Performance by 50%

[Link to full changelog](../changelog.md)
```

### Inline Version Indicators

```markdown
### `function_name(param1, param2, param3=None)`

**Added in**: v1.0
**Modified in**: v2.0 (added param3)

[Description]

**Parameters:**
- `param1` (string): [Description]
- `param2` (integer): [Description]
- `param3` (boolean, optional): [Description] - **Added in v2.0**
```

## Search Optimization Patterns

### SEO-Friendly Documentation Pattern

```markdown
# [Clear, Descriptive Title Using Common Search Terms]

**Summary**: [One-paragraph summary that answers the main question - appears in search results]

**Keywords**: [topic 1], [topic 2], [topic 3] (help with internal search)

## What [Audience] Need to Know About [Topic]

[First paragraph answers the main question using natural language]

### Common Questions

This guide answers:
- How do I [common task 1]?
- What is [concept they search for]?
- Why does [problem] happen?
- When should I use [feature]?

[Rest of content...]

## Summary

[Repeat key points at end for people who skim to bottom]
```

## Cross-Reference Patterns

### Contextual Links Pattern

```markdown
For more details on authentication, see the [Authentication Guide](../auth.md).

ℹ️ **Note**: This feature requires authentication. If you haven't set up authentication yet, start with our [Authentication Guide](../auth.md).

⚠️ **Warning**: Before using this in production, read the [Security Best Practices](../security.md) guide.

💡 **Tip**: For better performance, consider using caching as described in the [Performance Optimization Guide](../performance.md).
```

### "See Also" Section Pattern

```markdown
## See Also

**Related Concepts:**
- [Concept A](../concepts/concept-a.md) - Understand the underlying concept
- [Concept B](../concepts/concept-b.md) - Related theory

**Related Tasks:**
- [How to X](../guides/how-to-x.md) - Accomplish related task X
- [How to Y](../guides/how-to-y.md) - Accomplish related task Y

**Related Reference:**
- [API Function A](../api/function-a.md) - Related API function
- [Configuration Option B](../reference/config.md#option-b) - Related configuration

**External Resources:**
- [Official Specification](https://example.org/spec) - Technical specification
- [Community Tutorial](https://blog.example.com/tutorial) - Detailed community guide
```

## Anti-Patterns to Avoid

### ❌ The Endless Scroll

**Problem:** One giant page with everything

**Solution:** Break into multiple focused pages with clear navigation

### ❌ The Jargon Jungle

**Problem:** Unexplained technical terms everywhere

**Solution:** Define terms or use plain language

### ❌ The Example Vacuum

**Problem:** Lots of explanation, no code examples

**Solution:** Show, don't just tell. Code examples for every concept.

### ❌ The Assumption Trap

**Problem:** "Obviously...", "Simply...", "Just..."

**Solution:** State prerequisites explicitly, explain every step

### ❌ The Version Maze

**Problem:** Unclear which version documentation applies to

**Solution:** Clear version indicators on every page

### ❌ The Link Desert

**Problem:** No cross-references or navigation

**Solution:** Liberal use of related links and navigation

### ❌ The Update Ghost

**Problem:** No last-updated dates, unclear if current

**Solution:** Automated dates, version tracking, regular reviews

### ❌ The Hello World Halt

**Problem:** Only basic examples, no real-world patterns

**Solution:** Progressive examples from basic to production-ready

### ❌ The Error Silence

**Problem:** Only happy path documented

**Solution:** Document errors, edge cases, failures

### ❌ The Maintenance Mirage

**Problem:** Created once, never updated

**Solution:** Documentation in definition of done, regular audits

## Related Topics

- **Implementation**: See [advanced-topics.md](advanced-topics.md)
- **Quality Standards**: See [best-practices.md](best-practices.md)
- **Core Principles**: See [core-concepts.md](core-concepts.md)
