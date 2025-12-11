# Security Hardening Checklist - BARQ Fleet Management

## CRITICAL FIXES (Do First - 24 Hours)

### 1. Secret Management Emergency
**Status:** ❌ CRITICAL - Secrets Exposed in Git

**Files to Fix:**
- `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/.env`

**Actions Required:**

```bash
# 1. Immediately rotate these secrets:
# - SECRET_KEY
# - GOOGLE_CLIENT_SECRET (regenerate in Google Console)
# - SYARAH_PASSWORD (change in Syarah dashboard)
# - FMS_PASSWORD (change in FMS settings)
# - SENTRY_DSN (regenerate in Sentry)

# 2. Remove .env from git history
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
echo "credentials.json" >> .gitignore

# 4. Commit changes
git add .gitignore
git commit -m "chore: add .env to gitignore and remove from history"
git push --force --all
```

**New .env.example (template only):**
```env
# Security
SECRET_KEY=CHANGE_ME_IN_PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret_from_google_console

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=barq_fleet
```

---

### 2. CORS Configuration Fix
**Status:** ❌ CRITICAL - Allows Any Origin

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/main.py`
**Line:** 108-116

**Current Code (DANGEROUS):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ ALLOWS ANY WEBSITE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

**Fixed Code:**
```python
# Option 1: Use environment-based config
from app.core.cors import get_cors_middleware

cors_middleware, cors_kwargs = get_cors_middleware()
app.add_middleware(cors_middleware, **cors_kwargs)

# Option 2: Explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "X-Request-ID",
    ],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
)
```

**Then update .env:**
```env
BACKEND_CORS_ORIGINS=["https://app.barq.com","https://admin.barq.com"]
```

---

## HIGH PRIORITY FIXES (1 Week)

### 3. Token Expiration Fix
**Status:** ⚠️ HIGH - 7-day access tokens

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/.env`
**Line:** 12

**Change:**
```env
# BEFORE
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# AFTER
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Development: 1 hour
# Production should be 15 minutes
```

---

### 4. Enable Missing Middleware
**Status:** ⚠️ HIGH - Security middleware not active

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/main.py`
**Location:** After line 116 (after CORS)

**Add These Middlewares:**
```python
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.csrf import CSRFProtectionMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Add in this order (bottom runs first)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CSRFProtectionMiddleware,
    cookie_secure=settings.ENVIRONMENT == "production",
    cookie_samesite="Lax",
)

app.add_middleware(RateLimitMiddleware)
```

---

### 5. Brute Force Protection Integration
**Status:** ⚠️ HIGH - Not connected to auth

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/api/v1/auth.py`
**Function:** `login()` (line 30)

**Add to Login Endpoint:**
```python
from fastapi import Request
from app.core.security import BruteForceProtector

@router.post("/login", response_model=TokenWithOrganization)
def login(
    request: Request,  # ADD THIS
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Check if IP is locked out
    client_ip = request.client.host
    if BruteForceProtector.is_locked_out(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts",
        )

    user = user_service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        # Record failed attempt
        BruteForceProtector.record_failed_attempt(client_ip)

        remaining = BruteForceProtector.get_remaining_attempts(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect email or password. {remaining} attempts remaining.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Clear attempts on successful login
    BruteForceProtector.clear_attempts(client_ip)

    # ... rest of login logic
```

---

### 6. Redis-Based Rate Limiting
**Status:** ⚠️ HIGH - In-memory won't work in production

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/middleware/rate_limit.py`

**Fix:** Replace InMemoryStorage with Redis

**Step 1:** Update .env
```env
REDIS_URL=redis://localhost:6379/0
# Production: Use Google Cloud Memorystore
# REDIS_URL=redis://10.0.0.3:6379/0
```

**Step 2:** Update rate_limit.py (line 106-113)
```python
# BEFORE
limiter = Limiter(
    key_func=get_identifier,
    default_limits=...,
    storage_uri=security_config.rate_limit.storage_uri,  # This is None!
)

# AFTER
import os

limiter = Limiter(
    key_func=get_identifier,
    default_limits=[security_config.rate_limit.default_limit] if security_config.rate_limit.enabled else [],
    storage_uri=os.getenv("REDIS_URL", "memory://"),  # ✅ Use Redis
    strategy="fixed-window",
)
```

---

## MEDIUM PRIORITY FIXES (2 Weeks)

### 7. Database Credentials Security
**Status:** ⚠️ MEDIUM - Weak password

**File:** `.env`

**Action:**
```bash
# Generate strong password
openssl rand -base64 32

# Update .env
POSTGRES_PASSWORD=<generated_password>

# Then migrate to Google Secret Manager
```

---

### 8. File Upload Validation
**Status:** ⚠️ MEDIUM - No magic number check

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/core/validators.py`
**Function:** `FileValidator.validate_image()` (line 344)

**Add Magic Number Validation:**
```python
import magic

@classmethod
def validate_image(cls, filename: str, content_type: str, size: int, file_bytes: bytes = None) -> Dict[str, Any]:
    """Validate image upload with magic number check"""

    # Existing checks...
    if content_type not in cls.ALLOWED_IMAGE_TYPES:
        raise ValidationError(...)

    # ✅ ADD: Magic number validation
    if file_bytes:
        mime = magic.Magic(mime=True)
        actual_type = mime.from_buffer(file_bytes)
        if actual_type not in cls.ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f"File content doesn't match extension. Detected: {actual_type}"
            )

    # Rest of validation...
```

**Add to requirements.txt:**
```
python-magic==0.4.27
```

---

### 9. CSP Nonce Implementation
**Status:** ⚠️ MEDIUM - Using unsafe-inline

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/middleware/security_headers.py`

**Implement Nonce-Based CSP:**
```python
import secrets

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate nonce for this request
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # Add CSP with nonce
        csp = self._build_csp_with_nonce(nonce)
        response.headers["Content-Security-Policy"] = csp

        return response

    def _build_csp_with_nonce(self, nonce: str) -> str:
        directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'", f"'nonce-{nonce}'"],  # ✅ No unsafe-inline
            "style-src": ["'self'", f"'nonce-{nonce}'"],
            # ... other directives
        }
        return "; ".join([f"{k} {' '.join(v)}" for k, v in directives.items()])
```

---

### 10. Encryption Salt Management
**Status:** ⚠️ MEDIUM - Fixed salt

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/core/encryption.py`
**Line:** 80-82

**Implement Per-Organization Salts:**
```python
def _derive_key(self, password: bytes, organization_id: Optional[int] = None) -> bytes:
    """Derive key with organization-specific salt"""

    if organization_id:
        # Use organization-specific salt (store in database)
        salt = self._get_org_salt(organization_id)
    else:
        # Global salt for non-tenant data
        salt = b"barq_encryption_salt_v1_do_not_change"

    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=self.KEY_SIZE,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return kdf.derive(password)

def _get_org_salt(self, organization_id: int) -> bytes:
    """Get or create organization-specific salt"""
    # Store in database: organizations.encryption_salt
    # Return organization's unique salt
    pass
```

---

## LOW PRIORITY FIXES (1 Month)

### 11. OAuth State Parameter
**Status:** ✓ LOW - CSRF protection exists via other means

**File:** `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/api/v1/auth.py`

**Add State Parameter:**
```python
import secrets

@router.get("/google/login")
def google_login(request: Request):
    """Initiate Google OAuth flow"""
    state = secrets.token_urlsafe(32)

    # Store state in session
    request.session["oauth_state"] = state

    # Build auth URL with state
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=email profile&"
        f"state={state}"
    )

    return {"auth_url": auth_url}

@router.post("/google/callback")
def google_callback(request: Request, code: str, state: str):
    """Handle Google OAuth callback"""

    # Verify state matches
    stored_state = request.session.get("oauth_state")
    if not stored_state or state != stored_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid state parameter"
        )

    # Clear used state
    del request.session["oauth_state"]

    # Continue with token exchange...
```

---

### 12. Dependency Security Audit
**Status:** ✓ LOW - Regular maintenance

**Action:**
```bash
# Install security tools
pip install safety pip-audit

# Run audits
safety check
pip-audit

# Update vulnerable packages
pip install --upgrade <package_name>

# Test after updates
pytest
```

**Add to CI/CD:**
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: |
          pip install safety pip-audit
          pip install -r requirements.txt
      - name: Run safety check
        run: safety check
      - name: Run pip-audit
        run: pip-audit
```

---

## GOOGLE SECRET MANAGER SETUP

### Step 1: Enable Secret Manager API
```bash
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Create Secrets
```bash
# Create secrets
echo -n "YOUR_SECRET_KEY_HERE" | \
  gcloud secrets create barq-secret-key --data-file=-

echo -n "YOUR_GOOGLE_CLIENT_SECRET" | \
  gcloud secrets create google-client-secret --data-file=-

echo -n "YOUR_SYARAH_PASSWORD" | \
  gcloud secrets create syarah-api-password --data-file=-

echo -n "YOUR_FMS_PASSWORD" | \
  gcloud secrets create fms-api-password --data-file=-
```

### Step 3: Grant Access
```bash
# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding barq-secret-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4: Update Code
**File:** `app/config/settings.py`

```python
from google.cloud import secretmanager
import os

class SecretManager:
    """Helper for accessing Google Secret Manager"""

    def __init__(self):
        self.client = None
        self.project_id = os.getenv("GCP_PROJECT_ID")

        # Only initialize in production
        if os.getenv("ENVIRONMENT") == "production":
            self.client = secretmanager.SecretManagerServiceClient()

    def get(self, secret_id: str, default: str = "") -> str:
        """Get secret value"""
        # Development: use .env
        if not self.client:
            return os.getenv(secret_id, default)

        # Production: use Secret Manager
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to fetch secret {secret_id}: {e}")
            return default

# Initialize secret manager
secrets = SecretManager()

class Settings:
    def __init__(self):
        # Use Secret Manager for sensitive values
        self.SECRET_KEY = secrets.get("barq-secret-key", os.getenv("SECRET_KEY", ""))
        self.GOOGLE_CLIENT_SECRET = secrets.get("google-client-secret")
        self.SYARAH_PASSWORD = secrets.get("syarah-api-password")
        self.FMS_PASSWORD = secrets.get("fms-api-password")
```

---

## PRODUCTION DEPLOYMENT CHECKLIST

Before deploying to production, verify:

### Security Configuration
- [ ] All secrets moved to Google Secret Manager
- [ ] .env file not in git repository
- [ ] CORS origins explicitly set (no wildcards)
- [ ] Rate limiting middleware enabled
- [ ] CSRF middleware enabled
- [ ] Security headers middleware enabled
- [ ] Brute force protection integrated
- [ ] ACCESS_TOKEN_EXPIRE_MINUTES = 15
- [ ] Redis configured for rate limiting/blacklist
- [ ] HTTPS enforced (HSTS enabled)

### Database Security
- [ ] Strong database password
- [ ] Database in private subnet
- [ ] RLS (Row-Level Security) enabled
- [ ] Connection pooling configured
- [ ] Backup strategy in place

### Monitoring
- [ ] Sentry error tracking enabled
- [ ] Audit logging active
- [ ] Failed auth alerts configured
- [ ] Rate limit violation alerts
- [ ] Unusual activity detection

### Testing
- [ ] Security tests passing
- [ ] Penetration test completed
- [ ] OWASP Top 10 checklist complete
- [ ] Load testing passed
- [ ] Incident response plan documented

---

## QUICK REFERENCE

### Security Middleware Order (Bottom to Top)
```python
# 1. Security Headers (runs first)
app.add_middleware(SecurityHeadersMiddleware)

# 2. CSRF Protection
app.add_middleware(CSRFProtectionMiddleware)

# 3. Rate Limiting
app.add_middleware(RateLimitMiddleware)

# 4. CORS (runs last, wraps everything)
app.add_middleware(CORSMiddleware, ...)
```

### Common Security Headers
```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
```

### Password Requirements
- Minimum: 12 characters
- Must include: uppercase, lowercase, digit, special char
- Cannot be common password
- Max repeated chars: 3

### Token Lifetimes
- Access Token: 15 minutes (production), 60 minutes (dev)
- Refresh Token: 7 days
- CSRF Token: Session (until browser closes)

---

## CONTACT & ESCALATION

### Security Incidents
1. Immediately notify: security@barq.com
2. Create incident ticket
3. Follow incident response plan
4. Document all actions

### Questions
- Security Team: security@barq.com
- DevOps: devops@barq.com

---

**Last Updated:** December 10, 2025
**Next Review:** After critical fixes completion
