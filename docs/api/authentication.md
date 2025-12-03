# Authentication Guide

## Overview

BARQ Fleet Management API uses JWT (JSON Web Tokens) for authentication and authorization. This guide covers all authentication methods, token management, and security best practices.

---

## Table of Contents

1. [Authentication Methods](#authentication-methods)
2. [JWT Tokens](#jwt-tokens)
3. [Token Refresh](#token-refresh)
4. [API Keys](#api-keys)
5. [OAuth 2.0 (Google)](#oauth-20-google)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Authentication Methods

BARQ API supports three authentication methods:

### 1. Email/Password Authentication
Standard username/password authentication for web and mobile applications.

### 2. Google OAuth 2.0
Single sign-on using Google accounts.

### 3. API Keys
Long-lived tokens for server-to-server integrations and automation.

---

## JWT Tokens

### Token Types

**Access Token:**
- Short-lived (1 hour)
- Used for API requests
- Contains user information and permissions

**Refresh Token:**
- Long-lived (30 days)
- Used to obtain new access tokens
- Invalidated on logout

### Email/Password Login

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 123,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "manager",
  "org_id": 1,
  "org_name": "ACME Corp",
  "org_role": "admin"
}
```

**Note:** The response includes organization context (`org_id`, `org_name`, `org_role`) for multi-tenant support.

### Using JWT Tokens

Include the access token in the `Authorization` header of all API requests:

```http
GET /api/v1/fleet/couriers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Token Structure

JWT tokens contain three parts separated by dots (`.`):
```
header.payload.signature
```

**Decoded Payload Example:**
```json
{
  "sub": "123",
  "exp": 1638360000,
  "iat": 1638356400,
  "nbf": 1638356400,
  "iss": "barq-api",
  "aud": "barq-client",
  "jti": "abc-123-def-456",
  "org_id": 1,
  "org_role": "admin"
}
```

**Important:** The `org_id` and `org_role` claims are included for multi-tenant support. All API requests are scoped to the organization specified in the token.

---

## User Registration

New users can register and automatically get an organization created.

**Endpoint:** `POST /api/v1/auth/register`

**Request:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "organization_name": "ACME Corp"  // Optional - auto-generated if not provided
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 123,
  "email": "user@example.com",
  "full_name": "John Doe",
  "org_id": 1,
  "org_name": "ACME Corp",
  "org_role": "OWNER"
}
```

**Note:** The registering user automatically becomes the OWNER of their organization.

---

## Organization Switching

Users who belong to multiple organizations can switch between them.

**Endpoint:** `POST /api/v1/auth/switch-organization`

**Request:**
```http
POST /api/v1/auth/switch-organization
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "organization_id": 2
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 123,
  "email": "user@example.com",
  "full_name": "John Doe",
  "org_id": 2,
  "org_name": "New Organization",
  "org_role": "admin"
}
```

---

## Get User Organizations

Retrieve all organizations the current user belongs to.

**Endpoint:** `GET /api/v1/auth/me/organizations`

**Response:**
```json
{
  "organizations": [
    {
      "id": 1,
      "name": "ACME Corp",
      "role": "OWNER",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Partner Org",
      "role": "ADMIN",
      "is_active": true
    }
  ]
}
```

### Refresh Token Best Practices

1. Store refresh tokens securely (encrypted storage)
2. Implement automatic token refresh before expiration
3. Handle refresh token expiration (redirect to login)
4. Invalidate refresh tokens on logout

### Example: Auto-Refresh Implementation

```javascript
// JavaScript example
class ApiClient {
  constructor(accessToken, refreshToken) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }

  async request(url, options = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${this.accessToken}`
        }
      });

      if (response.status === 401) {
        // Token expired, refresh it
        await this.refreshAccessToken();
        // Retry the original request
        return this.request(url, options);
      }

      return response;
    } catch (error) {
      console.error('Request failed:', error);
      throw error;
    }
  }

  async refreshAccessToken() {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        refresh_token: this.refreshToken
      })
    });

    if (!response.ok) {
      // Refresh token invalid, redirect to login
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    const data = await response.json();
    this.accessToken = data.access_token;

    // Store new access token
    localStorage.setItem('access_token', data.access_token);
  }
}
```

---

## API Keys

API keys are long-lived tokens for server-to-server integrations and automation scripts.

### Creating an API Key

API keys can only be created by administrators.

**Endpoint:** `POST /api/v1/admin/api-keys`

**Request:**
```http
POST /api/v1/admin/api-keys
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "name": "Production Integration",
  "description": "API key for production order integration",
  "scopes": ["deliveries:read", "deliveries:write"],
  "expires_at": "2026-12-31"
}
```

**Response:**
```json
{
  "id": 456,
  "name": "Production Integration",
  "key": "barq_live_abc123def456ghi789jkl012mno345",
  "scopes": ["deliveries:read", "deliveries:write"],
  "created_at": "2025-12-02T10:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "last_used_at": null
}
```

**IMPORTANT:** The API key is only shown once. Store it securely!

### Using API Keys

Use API keys in the `X-API-Key` header:

```http
GET /api/v1/operations/deliveries
X-API-Key: barq_live_abc123def456ghi789jkl012mno345
Content-Type: application/json
```

### API Key Scopes

API keys support granular permissions:

| Scope | Description |
|-------|-------------|
| `fleet:read` | Read fleet data |
| `fleet:write` | Create/update fleet data |
| `deliveries:read` | Read delivery data |
| `deliveries:write` | Create/update deliveries |
| `analytics:read` | Read analytics data |
| `admin:*` | Full admin access |

### Managing API Keys

**List API Keys:**
```http
GET /api/v1/admin/api-keys
```

**Revoke API Key:**
```http
DELETE /api/v1/admin/api-keys/{key_id}
```

**Rotate API Key:**
```http
POST /api/v1/admin/api-keys/{key_id}/rotate
```

---

## OAuth 2.0 (Google)

### Google Sign-In Flow

1. User clicks "Sign in with Google"
2. Frontend redirects to Google OAuth
3. User authorizes the application
4. Google returns an authorization code
5. Frontend exchanges code for Google token
6. Frontend sends Google token to BARQ API
7. BARQ validates token and returns JWT tokens

### Implementation

**Frontend (JavaScript):**
```javascript
// Initialize Google Sign-In
google.accounts.id.initialize({
  client_id: 'YOUR_GOOGLE_CLIENT_ID',
  callback: handleGoogleSignIn
});

async function handleGoogleSignIn(response) {
  // response.credential contains the Google ID token
  const barqResponse = await fetch('/api/v1/auth/google', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      token: response.credential
    })
  });

  const data = await barqResponse.json();
  // Store BARQ JWT tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
}
```

**Backend Request:**
```http
POST /api/v1/auth/google
Content-Type: application/json

{
  "token": "google_id_token_here"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "user@gmail.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

---

## Security Best Practices

### 1. Token Storage

**Web Applications:**
- Store tokens in memory (React state, Vuex store)
- Use `httpOnly` cookies for refresh tokens
- NEVER store tokens in `localStorage` for sensitive applications

**Mobile Applications:**
- Use secure storage (Keychain on iOS, Keystore on Android)
- Encrypt tokens before storing

**Server-Side:**
- Use environment variables for API keys
- Never commit tokens to version control

### 2. HTTPS Only

ALWAYS use HTTPS in production. Tokens sent over HTTP can be intercepted.

```javascript
// Enforce HTTPS in production
if (process.env.NODE_ENV === 'production' && window.location.protocol !== 'https:') {
  window.location.protocol = 'https:';
}
```

### 3. Token Expiration

- Access tokens: 1 hour
- Refresh tokens: 30 days
- API keys: Custom (max 1 year)

Implement automatic token refresh before expiration.

### 4. CORS Configuration

Configure CORS properly to prevent unauthorized domains from accessing your API:

```python
# Backend CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.barq.com"],  # Only allow your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 5. Rate Limiting

Authentication endpoints are rate-limited:
- Login: 5 attempts per minute per IP
- Refresh: 10 requests per minute
- API key usage: 100 requests per minute

### 6. Password Requirements

When creating user accounts:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### 7. Organization Roles

Users have roles within each organization:

| Role | Description |
|------|-------------|
| `OWNER` | Full access, can delete organization |
| `ADMIN` | Full access except deleting organization |
| `MANAGER` | Can manage day-to-day operations |
| `VIEWER` | Read-only access |

### 8. Multi-Tenant Data Isolation

All API endpoints automatically filter data by the organization specified in the JWT token. This is enforced at the database level using Row-Level Security (RLS).

---

## Troubleshooting

### Common Errors

#### 1. Invalid Token (401)

```json
{
  "detail": "Invalid authentication credentials",
  "status_code": 401
}
```

**Solutions:**
- Check token format (should start with "Bearer ")
- Verify token hasn't expired
- Ensure token is valid and not revoked

#### 2. Token Expired (401)

```json
{
  "detail": "Token has expired",
  "status_code": 401
}
```

**Solution:**
Use refresh token to obtain a new access token.

#### 3. Insufficient Permissions (403)

```json
{
  "detail": "Insufficient permissions for this operation",
  "status_code": 403
}
```

**Solution:**
Request appropriate permissions from an administrator.

#### 4. Rate Limit Exceeded (429)

```json
{
  "detail": "Too many login attempts. Try again in 60 seconds.",
  "status_code": 429,
  "retry_after": 60
}
```

**Solution:**
Wait for the specified time before retrying.

### Debugging Tips

1. **Decode JWT tokens:**
   ```javascript
   const payload = JSON.parse(atob(token.split('.')[1]));
   console.log('Token expires at:', new Date(payload.exp * 1000));
   ```

2. **Check token validity:**
   ```http
   GET /api/v1/auth/me
   Authorization: Bearer {access_token}
   ```

3. **Monitor API responses:**
   - Check `WWW-Authenticate` header in 401 responses
   - Review `X-RateLimit-*` headers

---

## Example Implementations

### Python

```python
import requests
from datetime import datetime, timedelta

class BarqAuth:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"])

        return data["user"]

    def get_headers(self):
        if self._token_expired():
            self.refresh_access_token()

        return {"Authorization": f"Bearer {self.access_token}"}

    def _token_expired(self):
        return datetime.now() >= self.token_expires_at

    def refresh_access_token(self):
        response = requests.post(
            f"{self.base_url}/api/v1/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"])

# Usage
auth = BarqAuth("https://api.barq.com")
auth.login("user@example.com", "password")

# Make authenticated requests
response = requests.get(
    "https://api.barq.com/api/v1/fleet/couriers",
    headers=auth.get_headers()
)
```

### JavaScript/TypeScript

```typescript
interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

class BarqAuthClient {
  private baseUrl: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiresAt: Date | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async login(email: string, password: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data: AuthTokens = await response.json();
    this.setTokens(data);
  }

  private setTokens(data: AuthTokens): void {
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    this.tokenExpiresAt = new Date(Date.now() + data.expires_in * 1000);
  }

  async getAuthHeaders(): Promise<Record<string, string>> {
    if (this.isTokenExpired()) {
      await this.refreshAccessToken();
    }

    return {
      'Authorization': `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json'
    };
  }

  private isTokenExpired(): boolean {
    if (!this.tokenExpiresAt) return true;
    return new Date() >= this.tokenExpiresAt;
  }

  private async refreshAccessToken(): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: this.refreshToken })
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data: AuthTokens = await response.json();
    this.setTokens(data);
  }
}

// Usage
const authClient = new BarqAuthClient('https://api.barq.com');
await authClient.login('user@example.com', 'password');

const headers = await authClient.getAuthHeaders();
const response = await fetch('https://api.barq.com/api/v1/fleet/couriers', {
  headers
});
```

---

## Support

For authentication issues:
- **Email:** auth-support@barq.com
- **Documentation:** https://docs.barq.com/authentication
- **Security Issues:** security@barq.com

---

**Version:** 1.1.0
**Last Updated:** December 3, 2025
