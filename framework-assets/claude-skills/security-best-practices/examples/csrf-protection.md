# CSRF (Cross-Site Request Forgery) Protection

Complete guide to implementing CSRF protection in web applications.

## Understanding CSRF

CSRF attacks trick authenticated users into executing unwanted actions on a web application where they're authenticated. The attack leverages the browser's automatic inclusion of cookies with requests.

## CSRF Attack Scenario

csrf_attack_flow[5]{step,description}:
1. User authenticates,User logs into trusted site (bank.com) receives session cookie
2. Attacker crafts malicious site,evil.com contains form targeting bank.com/transfer
3. User visits evil site,While still authenticated to bank.com
4. Malicious request sent,Browser automatically includes bank.com cookies
5. Action executed,Bank processes transfer as legitimate request

## Protection Methods

csrf_protection_methods[6]{method,security_level,use_case}:
CSRF Tokens (Synchronizer Token),Very High,Form submissions state-changing operations
Double Submit Cookie,High,Stateless applications SPAs
SameSite Cookies,High,Modern browsers additional layer
Custom Headers,Medium,AJAX requests with CORS
Referer/Origin Validation,Medium,Additional validation layer
Re-authentication,Very High,Critical operations only

## 1. CSRF Token Implementation (Python/Flask)

**Flask with Flask-WTF**:
```python
from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# Enable CSRF protection globally
csrf = CSRFProtect(app)

class TransferForm(FlaskForm):
    """Form with automatic CSRF protection"""
    recipient = StringField('Recipient', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[
        DataRequired(),
        NumberRange(min=0.01, max=10000)
    ])
    submit = SubmitField('Transfer')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    form = TransferForm()

    if form.validate_on_submit():
        # CSRF token automatically validated
        # Process transfer
        recipient = form.recipient.data
        amount = form.amount.data

        # Execute transfer logic
        success = process_transfer(recipient, amount)

        if success:
            return {'message': 'Transfer successful'}, 200
        return {'error': 'Transfer failed'}, 400

    # Render form with CSRF token
    return render_template('transfer.html', form=form)

# For API endpoints (JSON)
@app.route('/api/transfer', methods=['POST'])
def api_transfer():
    """API endpoint with CSRF protection"""
    data = request.get_json()

    # CSRF token expected in header or body
    # Automatically validated by Flask-WTF

    recipient = data.get('recipient')
    amount = data.get('amount')

    if not recipient or not amount:
        return {'error': 'Missing required fields'}, 400

    success = process_transfer(recipient, amount)

    if success:
        return {'message': 'Transfer successful'}, 200
    return {'error': 'Transfer failed'}, 400

# Exempt specific routes (only for public endpoints)
@app.route('/public/data', methods=['GET', 'POST'])
@csrf.exempt
def public_data():
    """Public endpoint without CSRF protection"""
    return {'data': 'public information'}
```

**Jinja2 Template**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Transfer Money</title>
</head>
<body>
    <h1>Transfer Money</h1>

    <form method="POST" action="/transfer">
        <!-- CSRF token automatically added by Flask-WTF -->
        {{ form.hidden_tag() }}

        <div>
            {{ form.recipient.label }}
            {{ form.recipient(size=32) }}
        </div>

        <div>
            {{ form.amount.label }}
            {{ form.amount }}
        </div>

        <div>
            {{ form.submit() }}
        </div>
    </form>

    <!-- For AJAX requests -->
    <script>
        // Get CSRF token from meta tag
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        // Include in AJAX request
        fetch('/api/transfer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                recipient: 'john@example.com',
                amount: 100
            })
        });
    </script>
</body>
</html>
```

## 2. CSRF Token Implementation (Express/TypeScript)

**Express with csurf middleware**:
```typescript
import express, { Request, Response, NextFunction } from 'express';
import csrf from 'csurf';
import cookieParser from 'cookie-parser';

const app = express();

// Required middleware
app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// CSRF protection middleware
const csrfProtection = csrf({ cookie: true });

// Apply to all routes (except explicitly exempted)
app.use(csrfProtection);

// Add CSRF token to all rendered pages
app.use((req: Request, res: Response, next: NextFunction) => {
  res.locals.csrfToken = req.csrfToken();
  next();
});

// Render form with CSRF token
app.get('/transfer', (req, res) => {
  res.render('transfer', {
    csrfToken: req.csrfToken()
  });
});

// Handle form submission
app.post('/transfer', (req, res) => {
  // CSRF token automatically validated
  const { recipient, amount } = req.body;

  // Process transfer
  const success = processTransfer(recipient, amount);

  if (success) {
    res.json({ message: 'Transfer successful' });
  } else {
    res.status(400).json({ error: 'Transfer failed' });
  }
});

// API endpoint
app.post('/api/transfer', (req, res) => {
  // CSRF token validated from cookie
  const { recipient, amount } = req.body;

  if (!recipient || !amount) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const success = processTransfer(recipient, amount);

  if (success) {
    res.json({ message: 'Transfer successful' });
  } else {
    res.status(400).json({ error: 'Transfer failed' });
  }
});

// Exempt public endpoints
app.get('/public/data', (req, res, next) => {
  // Skip CSRF for this route
  res.json({ data: 'public information' });
});

// Error handler for CSRF errors
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  if (err.code === 'EBADCSRFTOKEN') {
    res.status(403).json({ error: 'Invalid CSRF token' });
  } else {
    next(err);
  }
});
```

**EJS Template**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Transfer Money</title>
    <meta name="csrf-token" content="<%= csrfToken %>">
</head>
<body>
    <h1>Transfer Money</h1>

    <form method="POST" action="/transfer">
        <!-- Hidden CSRF token field -->
        <input type="hidden" name="_csrf" value="<%= csrfToken %>">

        <div>
            <label>Recipient:</label>
            <input type="text" name="recipient" required>
        </div>

        <div>
            <label>Amount:</label>
            <input type="number" name="amount" step="0.01" required>
        </div>

        <button type="submit">Transfer</button>
    </form>

    <!-- For AJAX requests -->
    <script>
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        fetch('/api/transfer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                recipient: 'john@example.com',
                amount: 100
            })
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
    </script>
</body>
</html>
```

## 3. Double Submit Cookie Pattern

**Custom Implementation (Express)**:
```typescript
import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';

// Generate CSRF token
function generateCSRFToken(): string {
  return crypto.randomBytes(32).toString('base64');
}

// Middleware to set CSRF cookie
export const setCSRFToken = (req: Request, res: Response, next: NextFunction) => {
  if (!req.cookies['csrf-token']) {
    const token = generateCSRFToken();

    res.cookie('csrf-token', token, {
      httpOnly: false, // Needs to be accessible to JavaScript
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 3600000 // 1 hour
    });
  }
  next();
};

// Middleware to verify CSRF token
export const verifyCSRFToken = (req: Request, res: Response, next: NextFunction) => {
  // Skip for safe methods
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    return next();
  }

  // Get token from cookie
  const cookieToken = req.cookies['csrf-token'];

  // Get token from header or body
  const headerToken = req.headers['x-csrf-token'] ||
                     req.body._csrf ||
                     req.body.csrf_token;

  // Verify tokens match
  if (!cookieToken || !headerToken || cookieToken !== headerToken) {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }

  next();
};

// Apply middleware
app.use(cookieParser());
app.use(setCSRFToken);
app.use(verifyCSRFToken);

// Client-side code
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf-token='))
  ?.split('=')[1];

fetch('/api/transfer', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({ recipient: 'john@example.com', amount: 100 })
});
```

## 4. SameSite Cookie Attribute

**Cookie Configuration**:
```python
# Python/Flask
from flask import Flask, session

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
)

@app.route('/login', methods=['POST'])
def login():
    # Set session cookie with SameSite
    session['user_id'] = user.id
    return {'message': 'Logged in'}
```

```typescript
// TypeScript/Express
import session from 'express-session';

app.use(session({
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production', // HTTPS only
    httpOnly: true,                                 // No JavaScript access
    sameSite: 'lax',                               // CSRF protection
    maxAge: 3600000                                // 1 hour
  }
}));
```

### SameSite Values

samesite_values[3]{value,protection,use_case}:
Strict,Highest protection - cookie never sent cross-site,Banking critical applications
Lax,Good protection - allows top-level navigation,Most web applications default choice
None,No protection - requires Secure flag,Third-party integrations (requires HTTPS)

## 5. React/SPA Implementation

**React with Axios**:
```typescript
import axios from 'axios';
import { useEffect, useState } from 'react';

// Configure axios to include CSRF token
axios.defaults.xsrfCookieName = 'csrf-token';
axios.defaults.xsrfHeaderName = 'X-CSRF-Token';
axios.defaults.withCredentials = true;

function TransferForm() {
  const [csrfToken, setCsrfToken] = useState('');

  useEffect(() => {
    // Get CSRF token on component mount
    axios.get('/api/csrf-token')
      .then(response => setCsrfToken(response.data.token));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Axios automatically includes CSRF token from cookie
      await axios.post('/api/transfer', {
        recipient: 'john@example.com',
        amount: 100
      }, {
        headers: {
          'X-CSRF-Token': csrfToken // Or from cookie
        }
      });

      alert('Transfer successful');
    } catch (error) {
      alert('Transfer failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" name="recipient" required />
      <input type="number" name="amount" required />
      <button type="submit">Transfer</button>
    </form>
  );
}
```

## CSRF Protection Checklist

csrf_protection_checklist[12]{requirement,implementation}:
Token for State Changes,Use CSRF tokens for POST PUT DELETE PATCH
Synchronizer Token Pattern,Generate unique token per session include in forms
Token Validation,Verify token on server before processing request
SameSite Cookies,Set SameSite=Lax or Strict on session cookies
Custom Headers for AJAX,Require custom header (X-Requested-With X-CSRF-Token)
Referer/Origin Check,Validate Referer and Origin headers
Re-auth for Critical Operations,Require password for sensitive actions
Token Expiration,Tokens expire with session
Per-Request Tokens,Generate new token for each request (highest security)
HTTPS Only,Always use HTTPS in production
Error Handling,Don't reveal CSRF failures in detail
Testing,Test CSRF protection with security tools

## Common Mistakes

csrf_mistakes[8]{mistake,why_dangerous,fix}:
No CSRF on API,APIs vulnerable to CSRF,Implement token or custom header validation
GET for State Changes,GET requests can be CSRF attacked,Use POST for state changes
Token in URL,Tokens leaked in logs and Referer,Use header or hidden form field
Same Token Everywhere,One compromised token affects all,Per-session or per-request tokens
Not Validating Token,Token present but not checked,Always validate on server
Disabling for Convenience,Leaving endpoints unprotected,Exempt only truly public endpoints
Weak Token Generation,Predictable tokens,Use crypto-secure random generation
Not Using SameSite,Missing defense layer,Set SameSite attribute on cookies

## Testing CSRF Protection

**Manual Test**:
```html
<!-- Create test page on different domain -->
<!DOCTYPE html>
<html>
<body>
  <h1>CSRF Test</h1>

  <!-- This should be blocked by CSRF protection -->
  <form action="https://target-site.com/transfer" method="POST">
    <input type="hidden" name="recipient" value="attacker@evil.com">
    <input type="hidden" name="amount" value="1000">
    <button type="submit">Click here for free prize!</button>
  </form>

  <!-- Auto-submit for testing -->
  <script>
    // This should fail due to CSRF protection
    document.forms[0].submit();
  </script>
</body>
</html>
```

**Expected Result**: Request should be rejected with 403 Forbidden due to missing/invalid CSRF token.

---

**Remember**: CSRF protection is essential for any state-changing operation. Use synchronizer tokens, SameSite cookies, and validate on every request.
