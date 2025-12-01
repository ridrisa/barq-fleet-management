# BARQ Fleet Management - Security Documentation

**Version:** 1.0.0
**Last Updated:** November 23, 2025
**Security Level:** Confidential

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication](#authentication)
3. [Authorization & RBAC](#authorization--rbac)
4. [Data Security](#data-security)
5. [Network Security](#network-security)
6. [API Security](#api-security)
7. [Application Security](#application-security)
8. [Infrastructure Security](#infrastructure-security)
9. [Security Best Practices](#security-best-practices)
10. [Incident Response](#incident-response)
11. [Compliance](#compliance)
12. [Security Audit](#security-audit)

---

## Security Overview

### Security Posture

BARQ Fleet Management implements defense-in-depth security with multiple layers:

```
┌────────────────────────────────────────┐
│     External Threats (Internet)         │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  Layer 1: Network Security             │
│  - Cloud Armor (DDoS Protection)       │
│  - Cloud CDN (Edge Security)           │
│  - SSL/TLS Encryption                  │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  Layer 2: Application Security         │
│  - JWT Authentication                  │
│  - Role-Based Access Control           │
│  - Input Validation                    │
│  - Rate Limiting                       │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  Layer 3: Data Security                │
│  - Encryption at Rest                  │
│  - Encryption in Transit               │
│  - Secret Management                   │
│  - Database Security                   │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  Layer 4: Infrastructure Security      │
│  - VPC Isolation                       │
│  - IAM Policies                        │
│  - Audit Logging                       │
│  - Monitoring & Alerts                 │
└────────────────────────────────────────┘
```

### Security Principles

1. **Zero Trust:** Never trust, always verify
2. **Least Privilege:** Minimal access rights
3. **Defense in Depth:** Multiple security layers
4. **Security by Design:** Security built-in from start
5. **Continuous Monitoring:** 24/7 security monitoring

---

## Authentication

### JWT Token-Based Authentication

**Token Structure:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid",
    "email": "user@barq.com",
    "role": "admin",
    "tenant_id": "uuid",
    "exp": 1700000000,
    "iat": 1699996400
  },
  "signature": "..."
}
```

**Token Lifecycle:**
- **Expiry:** 30 minutes
- **Refresh Token:** 7 days
- **Storage:** HTTP-only cookies (frontend)
- **Transmission:** Authorization header

**Implementation:**
```python
# Backend: app/core/security.py
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Google OAuth 2.0

**Flow:**
```
1. User clicks "Sign in with Google"
   ↓
2. Redirect to Google OAuth consent screen
   ↓
3. User grants permission
   ↓
4. Google redirects back with auth code
   ↓
5. Backend exchanges code for tokens
   ↓
6. Backend verifies Google token
   ↓
7. Backend creates user (if new) or logs in
   ↓
8. Backend issues JWT token
   ↓
9. Client receives JWT token
```

**Configuration:**
```python
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT_URI = "https://api.barq.com/api/v1/auth/google/callback"
```

### Password Security

**Hashing:**
- **Algorithm:** bcrypt
- **Salt Rounds:** 12
- **Rainbow Table Protection:** Yes

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

---

## Authorization & RBAC

### Role-Based Access Control

**Roles:**

| Role | Permissions | Description |
|------|-------------|-------------|
| **admin** | Full access | System administrators |
| **manager** | Fleet, Operations | Fleet managers |
| **hr_manager** | HR, Finance | HR managers |
| **operations** | Deliveries, Incidents | Operations team |
| **support** | Tickets, Basic read | Support agents |
| **courier** | Self-service only | Courier users |

**Permission Format:**
```
resource.action
```

**Examples:**
- `couriers.read` - View couriers
- `couriers.write` - Create/update couriers
- `couriers.delete` - Delete couriers
- `payroll.*` - All payroll actions
- `*` - All permissions (admin only)

**Implementation:**
```python
# Backend: app/core/authorization.py
from functools import wraps
from fastapi import HTTPException, Depends

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/couriers")
@require_permission("couriers.write")
async def create_courier(data: CourierCreate, current_user: User = Depends(get_current_user)):
    # Create courier logic
    pass
```

### Multi-Tenancy Isolation

**Data Isolation:**
- Every query filtered by `tenant_id`
- Row-level security enforced
- No cross-tenant data access

```python
# Automatic tenant filtering
class TenantMixin:
    @declared_attr
    def tenant_id(cls):
        return Column(UUID, ForeignKey('tenants.id'), nullable=False)

# Query filtering
def get_couriers(db: Session, tenant_id: UUID):
    return db.query(Courier).filter(
        Courier.tenant_id == tenant_id,
        Courier.deleted_at.is_(None)
    ).all()
```

---

## Data Security

### Encryption at Rest

**Database:**
- **Cloud SQL:** AES-256 encryption (automatic)
- **Backups:** Encrypted with Google-managed keys
- **Disk:** Encrypted by default

**File Storage:**
- **Cloud Storage:** Server-side encryption (automatic)
- **Encryption:** AES-256
- **Key Management:** Google-managed keys

### Encryption in Transit

**TLS/SSL:**
- **Protocol:** TLS 1.3 (minimum TLS 1.2)
- **Certificates:** Let's Encrypt (auto-renewal)
- **Cipher Suites:** Strong ciphers only
- **HSTS:** Enabled (max-age=31536000)

**Configuration:**
```nginx
# Load Balancer SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers on;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Secret Management

**Google Secret Manager:**
- All secrets stored in Secret Manager
- No hardcoded secrets in code
- Automatic rotation supported
- Audit logging enabled

**Secrets Stored:**
- Database credentials
- JWT secret key
- API keys (Google OAuth, SMTP, etc.)
- Encryption keys

**Access:**
```python
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/barq-production/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

DATABASE_URL = get_secret("database-url")
JWT_SECRET_KEY = get_secret("jwt-secret-key")
```

### Sensitive Data Handling

**PII (Personally Identifiable Information):**
- National IDs
- Phone numbers
- Email addresses
- Bank account details

**Protection Measures:**
1. **Access Control:** Limited to authorized roles
2. **Audit Logging:** All access logged
3. **Masking:** Displayed as `****1234` in logs
4. **Retention:** Deleted per data retention policy

---

## Network Security

### VPC Configuration

**Network Isolation:**
```
┌─────────────────────────────────────┐
│         Public Internet             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Cloud Load Balancer (Public)   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      VPC Network (Private)          │
│  ┌────────────────────────────────┐ │
│  │  Cloud Run (Private)           │ │
│  │  - API Backend                 │ │
│  └────────────┬───────────────────┘ │
│               │                     │
│  ┌────────────▼───────────────────┐ │
│  │  Cloud SQL (Private IP only)   │ │
│  │  - PostgreSQL                  │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  Memorystore (Private IP)      │ │
│  │  - Redis                       │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Firewall Rules:**
- Default: Deny all
- Allow: HTTPS (443) from internet to Load Balancer
- Allow: Internal VPC traffic only
- Database: Private IP only (no public access)

### DDoS Protection

**Cloud Armor:**
- Rate limiting rules
- IP blacklist/whitelist
- SQL injection protection
- XSS protection
- Bot protection

**Configuration:**
```yaml
# Cloud Armor Security Policy
- priority: 1000
  action: deny(403)
  match:
    expr: "origin.region_code == 'CN'"  # Block specific countries

- priority: 2000
  action: rate_based_ban
  rateLimitOptions:
    conformAction: allow
    exceedAction: deny(429)
    rateLimitThreshold:
      count: 100
      intervalSec: 60
```

---

## API Security

### Rate Limiting

**Limits:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Admin: 5000 requests/hour

**Implementation:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/couriers")
@limiter.limit("100/hour")  # For anonymous
async def get_couriers():
    pass
```

**Response Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1700000000
```

### CORS (Cross-Origin Resource Sharing)

**Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.barq.com",
        "https://admin.barq.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-*"]
)
```

### Input Validation

**Pydantic Schemas:**
```python
from pydantic import BaseModel, EmailStr, constr, validator

class CourierCreate(BaseModel):
    name: constr(min_length=1, max_length=255)
    email: EmailStr
    phone: constr(regex=r'^\+966[0-9]{9}$')  # Saudi phone format
    national_id: constr(min_length=10, max_length=10)

    @validator('national_id')
    def validate_national_id(cls, v):
        if not v.isdigit():
            raise ValueError('National ID must contain only digits')
        return v
```

### SQL Injection Prevention

**SQLAlchemy ORM:**
- Parameterized queries (automatic)
- No raw SQL execution
- Input sanitization

```python
# Safe (parameterized)
db.query(Courier).filter(Courier.email == email).first()

# Unsafe (NEVER DO THIS)
db.execute(f"SELECT * FROM couriers WHERE email = '{email}'")
```

### XSS Protection

**Security Headers:**
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## Application Security

### Dependency Security

**Scanning:**
```bash
# Python dependencies
pip-audit

# Node.js dependencies
npm audit

# Fix vulnerabilities
npm audit fix
```

**Automation:**
- GitHub Dependabot enabled
- Weekly vulnerability scans
- Auto-update minor versions

### Code Security

**Static Analysis:**
```bash
# Python
bandit -r app/

# JavaScript/TypeScript
npm run lint:security
```

### Logging Security

**Sensitive Data Masking:**
```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Mask credit card numbers
        record.msg = re.sub(r'\d{4}-\d{4}-\d{4}-\d{4}', '****-****-****-****', record.msg)
        # Mask email addresses
        record.msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.com', record.msg)
        return True

logging.getLogger().addFilter(SensitiveDataFilter())
```

---

## Infrastructure Security

### IAM (Identity and Access Management)

**Service Account:**
```yaml
# Cloud Run service account
name: barq-api@barq-production.iam.gserviceaccount.com

roles:
  - cloudsql.client
  - secretmanager.secretAccessor
  - storage.objectViewer
  - logging.logWriter
  - cloudtrace.agent
```

**Principle of Least Privilege:**
- Each service has dedicated service account
- Minimal permissions granted
- Regular permission audit

### Audit Logging

**Cloud Audit Logs:**
- Admin activity logs (enabled)
- Data access logs (enabled)
- System event logs (enabled)
- 7-year retention

**Application Audit Logs:**
```python
def audit_log(user_id: UUID, action: str, entity_type: str, entity_id: UUID, changes: dict):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(log)
    db.commit()

# Usage
@app.put("/couriers/{courier_id}")
async def update_courier(courier_id: UUID, data: CourierUpdate, current_user: User):
    old_courier = get_courier(courier_id)
    updated_courier = update(courier_id, data)

    audit_log(
        user_id=current_user.id,
        action="update",
        entity_type="courier",
        entity_id=courier_id,
        changes={"before": old_courier, "after": updated_courier}
    )
```

---

## Security Best Practices

### For Developers

1. **Never commit secrets**
   - Use .env files (gitignored)
   - Use Secret Manager for production

2. **Validate all inputs**
   - Use Pydantic schemas
   - Validate on backend AND frontend

3. **Use parameterized queries**
   - Always use ORM
   - Never construct SQL strings

4. **Implement proper error handling**
   - Don't expose stack traces
   - Log errors securely

5. **Keep dependencies updated**
   - Regular security updates
   - Monitor for vulnerabilities

### For Administrators

1. **Enforce strong passwords**
2. **Enable 2FA for all admin accounts**
3. **Regular access reviews**
4. **Monitor audit logs**
5. **Backup encryption keys**

---

## Incident Response

### Security Incident Response Plan

**1. Detection**
- Automated alerts (Cloud Monitoring)
- User reports
- Security scans

**2. Containment**
- Isolate affected systems
- Revoke compromised credentials
- Block malicious IPs

**3. Investigation**
- Review audit logs
- Analyze attack vectors
- Assess damage

**4. Remediation**
- Patch vulnerabilities
- Restore from backups if needed
- Update security controls

**5. Recovery**
- Restore normal operations
- Monitor for recurrence

**6. Post-Incident**
- Document lessons learned
- Update security procedures
- Train team

### Incident Classification

| Severity | Response Time | Examples |
|----------|--------------|----------|
| **Critical** | < 15 minutes | Data breach, system compromise |
| **High** | < 1 hour | DDoS attack, service outage |
| **Medium** | < 4 hours | Suspicious activity, failed attacks |
| **Low** | < 24 hours | Policy violations, minor issues |

---

## Compliance

### GDPR Compliance

- **Data Minimization:** Collect only necessary data
- **Right to Access:** Users can export their data
- **Right to Delete:** Users can request deletion
- **Consent:** Explicit consent for data collection
- **Data Portability:** Export in machine-readable format

### PCI-DSS (If applicable)

- **Secure Payment Processing:** Tokenization
- **No Card Data Storage:** Use payment gateway
- **Encrypted Transmission:** TLS 1.2+

---

## Security Audit

### Last Security Audit: November 1, 2025

**Findings:**
- ✅ All high/critical vulnerabilities resolved
- ✅ All secrets moved to Secret Manager
- ✅ TLS 1.3 enabled
- ✅ Rate limiting implemented
- ✅ Audit logging complete

**Next Audit:** February 1, 2026

---

**Document Owner:** Security Team
**Classification:** Confidential
**Review Cycle:** Quarterly
**Last Updated:** November 23, 2025
