# BARQ Fleet - Security Checklist for Developers

**Quick Reference Guide for Secure Development**

---

## ✅ Before Every Deployment

### Critical Security Checks

- [ ] **Environment Variables Set**
  - [ ] `SECRET_KEY` is strong and unique (not default)
  - [ ] `ENVIRONMENT=production` for prod deployments
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=15` for production
  - [ ] `REDIS_URL` configured for token blacklist
  - [ ] Database credentials secured

- [ ] **Authentication & Authorization**
  - [ ] All endpoints use `Depends(get_current_user)` or public
  - [ ] Organization context checked via `Depends(get_current_organization)`
  - [ ] No hardcoded credentials in code

- [ ] **Token Security**
  - [ ] JWT includes `org_id` and `org_role` for multi-tenant
  - [ ] Tokens expire appropriately (15 min access, 7 days refresh)
  - [ ] Audience and Issuer verification enabled

- [ ] **SQL Security**
  - [ ] All queries use parameterized statements (no f-strings)
  - [ ] RLS context set correctly (`SET app.current_org_id = :org_id`)
  - [ ] No raw SQL with user input

- [ ] **API Responses**
  - [ ] No sensitive data in responses (tokens, passwords, secrets)
  - [ ] Error messages don't leak system information
  - [ ] Health endpoint doesn't expose credentials

---

## 🔒 Secure Coding Patterns

### ✅ DO: SQL Queries

```python
# CORRECT - Parameterized query
db.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": user_email}
)

# CORRECT - SQLAlchemy ORM
db.query(User).filter(User.email == user_email).first()

# CORRECT - RLS context
db.execute(
    text("SET app.current_org_id = :org_id"),
    {"org_id": str(int(org_id))}
)
```

### ❌ DON'T: SQL Queries

```python
# WRONG - SQL Injection vulnerability
db.execute(text(f"SELECT * FROM users WHERE email = '{user_email}'"))

# WRONG - RLS SQL Injection
db.execute(text(f"SET app.current_org_id = '{org_id}'"))
```

---

### ✅ DO: Authentication

```python
# CORRECT - Protected endpoint
@router.get("/sensitive-data")
def get_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    # User and org verified
    return db.query(Model).filter(Model.organization_id == current_org.id).all()

# CORRECT - Token creation with org context
access_token = create_access_token(
    data={
        "sub": str(user.id),
        "org_id": organization_id,
        "org_role": organization_role,
    },
    expires_delta=timedelta(minutes=15),
)
```

### ❌ DON'T: Authentication

```python
# WRONG - No authentication
@router.get("/sensitive-data")
def get_data(db: Session = Depends(get_db)):
    return db.query(Model).all()  # ❌ No user verification

# WRONG - Token without org context
access_token = create_access_token(data={"sub": str(user.id)})
```

---

### ✅ DO: Password Reset

```python
# CORRECT - No token in response
@router.post("/password-reset/request")
def request_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    # Generic response (prevent user enumeration)
    if not user:
        return {
            "message": "If an account exists, a reset link has been sent."
        }

    # Generate token
    reset_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(reset_token.encode()).hexdigest()

    # Store HASH only
    PasswordResetToken.create(user_id=user.id, token_hash=token_hash)

    # Send token via email (not in response)
    send_email(user.email, reset_link=f"...?token={reset_token}")

    # Generic response
    return {
        "message": "If an account exists, a reset link has been sent."
    }
```

### ❌ DON'T: Password Reset

```python
# WRONG - Token in response
return {
    "message": "Reset email sent",
    "reset_token": reset_token,  # ❌ NEVER expose token
}

# WRONG - Different messages
if not user:
    return {"message": "User not found"}  # ❌ User enumeration
else:
    return {"message": "Email sent"}
```

---

### ✅ DO: Error Handling

```python
# CORRECT - Generic error messages
try:
    user = authenticate(email, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"  # Generic message
        )
except Exception as e:
    logger.error(f"Auth error: {str(e)}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="An error occurred"  # Don't leak details
    )
```

### ❌ DON'T: Error Handling

```python
# WRONG - Specific error messages
if not user:
    raise HTTPException(detail="Email not found")  # ❌ User enumeration

# WRONG - Leaking system info
except Exception as e:
    raise HTTPException(detail=str(e))  # ❌ Exposes stack trace
```

---

### ✅ DO: Health Endpoints

```python
# CORRECT - Public basic health
@router.get("/health")
def health():
    return {"status": "healthy"}

# CORRECT - Protected detailed health
@router.get("/health/detailed")
def detailed_health(current_user: User = Depends(get_current_user)):
    return {
        "status": "healthy",
        "cpu_percent": psutil.cpu_percent(),
        # ❌ NO environment variables
        # ❌ NO database credentials
        # ❌ NO secret keys
    }
```

### ❌ DON'T: Health Endpoints

```python
# WRONG - Exposing sensitive info
@router.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": os.environ,  # ❌ Exposes secrets
        "database_url": settings.DATABASE_URL,  # ❌ Exposes credentials
    }
```

---

## 🛡️ Security Features to Use

### Token Blacklist
```python
from app.core.token_blacklist import blacklist_token, is_token_blacklisted

# Logout - blacklist token
@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    blacklist_token(token, reason="user_logout")
    return {"message": "Logged out successfully"}

# Check before using token (automatic in dependencies)
if is_token_blacklisted(token):
    raise HTTPException(status_code=401, detail="Token revoked")
```

### Password Validation
```python
from app.core.security import PasswordValidator

# Validate password strength
is_valid, error_msg = PasswordValidator.validate(password)
if not is_valid:
    raise HTTPException(status_code=400, detail=error_msg)
```

### Brute Force Protection
```python
from app.core.security import BruteForceProtector

# Check if locked out
if BruteForceProtector.is_locked_out(email):
    raise HTTPException(
        status_code=429,
        detail="Too many failed attempts. Try again later."
    )

# Record failed attempt
if not user or not verify_password(password, user.hashed_password):
    BruteForceProtector.record_failed_attempt(email)
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Clear on success
BruteForceProtector.clear_attempts(email)
```

---

## 🔍 Code Review Checklist

### When Reviewing Pull Requests

- [ ] **No hardcoded secrets** (API keys, passwords, tokens)
- [ ] **All SQL queries parameterized** (no f-strings in SQL)
- [ ] **Authentication required** for protected endpoints
- [ ] **Organization context validated** for multi-tenant data
- [ ] **No sensitive data in logs** (passwords, tokens, PII)
- [ ] **Error messages are generic** (no system info leakage)
- [ ] **Input validation present** (type, range, format checks)
- [ ] **Password reset doesn't leak tokens** or user existence
- [ ] **Health endpoints don't expose credentials**
- [ ] **CORS configured correctly** (not `allow_origins=["*"]`)

---

## 📊 Security Metrics to Monitor

### Production Monitoring

```python
# Track these metrics:
- Failed login attempts (by IP, by email)
- Blacklisted tokens count
- Password reset requests (rate)
- 401/403 errors (unauthorized access attempts)
- Slow queries (potential SQL injection attempts)
- Large request bodies (potential DoS)
```

### Alerting Thresholds

```yaml
Critical Alerts:
  - 10+ failed logins from same IP in 5 minutes
  - 100+ blacklisted tokens per hour
  - 50+ password reset requests per hour
  - 500+ 401 errors per minute
  - Database query time > 5 seconds

Warning Alerts:
  - 5+ failed logins from same IP in 5 minutes
  - 50+ blacklisted tokens per hour
  - 20+ password reset requests per hour
  - 200+ 401 errors per minute
```

---

## 🚨 Security Incident Response

### If You Discover a Vulnerability

1. **DO NOT** commit a fix to main/production immediately
2. **DO** notify the security team (create private issue)
3. **DO** assess impact (how many users affected?)
4. **DO** create a hotfix branch with the fix
5. **DO** test thoroughly before deploying
6. **DO** rotate any compromised secrets
7. **DO** notify affected users if PII compromised

### Emergency Contacts

- **Security Lead:** [Email/Slack]
- **DevOps Lead:** [Email/Slack]
- **CTO:** [Email/Slack]

---

## 📚 Additional Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

### Internal Docs
- `/backend/docs/SECURITY_AUDIT_P0_COMPLETE.md` - Full security audit
- `/backend/docs/SECURITY_HARDENING_PASSWORD_RESET.md` - Password reset guide
- `/backend/app/core/security.py` - Security utilities
- `/backend/app/core/token_blacklist.py` - Token revocation

---

## 🎯 Quick Security Self-Test

Before pushing code, ask yourself:

1. ✅ Would I be comfortable if this code was public?
2. ✅ Could an attacker bypass authentication?
3. ✅ Could an attacker access another org's data?
4. ✅ Are passwords/tokens visible in logs?
5. ✅ Do error messages reveal system internals?
6. ✅ Is user input validated and sanitized?
7. ✅ Are SQL queries parameterized?
8. ✅ Is sensitive data encrypted?

**If any answer is NO, fix before pushing!**

---

**Last Updated:** 2025-12-06
**Version:** 1.0
**Status:** Active

---
