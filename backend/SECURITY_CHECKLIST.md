# BARQ Fleet Management - Production Security Checklist

**Version**: 1.0
**Date**: December 2, 2025
**Purpose**: Pre-production security verification
**Status**: Use this checklist before production deployment

---

## Pre-Deployment Security Checklist

### 1. Authentication & Authorization ✅

#### Password Security
- [ ] Argon2 password hashing is enabled
- [ ] Password policy enforces minimum 12 characters
- [ ] Password complexity requirements are active (uppercase, lowercase, digits, special chars)
- [ ] Common passwords are blocked
- [ ] Password rehashing works on algorithm changes
- [ ] Test: Try creating user with weak password (should fail)
- [ ] Test: Verify Argon2 hash format in database

#### JWT Tokens
- [ ] Access tokens expire in 15 minutes
- [ ] Refresh tokens expire in 7 days
- [ ] Tokens include JTI for revocation
- [ ] Token signature verification works
- [ ] Test: Expired token is rejected
- [ ] Test: Invalid signature is rejected
- [ ] Test: Modified token payload is rejected

#### Brute Force Protection
- [ ] Account locks after 5 failed attempts
- [ ] Lockout duration is 30 minutes
- [ ] Lockout automatically expires
- [ ] Successful login clears failed attempts
- [ ] Test: 5 failed logins lock account
- [ ] Test: Wait 30 minutes, verify account unlocks

#### Token Blacklist
- [ ] Redis connection is configured
- [ ] Token revocation on logout works
- [ ] User-level token invalidation works
- [ ] Blacklist check is performed on every request
- [ ] Test: Logout invalidates token
- [ ] Test: Blacklisted token is rejected

#### RBAC Authorization
- [ ] All roles are seeded in database
- [ ] Permissions are correctly assigned to roles
- [ ] Permission checks work on all protected routes
- [ ] Tenant isolation is enforced
- [ ] Test: User without permission is denied (403)
- [ ] Test: User can only access own organization data
- [ ] Test: System admin can access all data

---

### 2. Data Protection ✅

#### Encryption
- [ ] ENCRYPTION_KEY environment variable is set (64+ chars)
- [ ] Field-level encryption works for PII fields
- [ ] Decryption works correctly
- [ ] Encryption keys are NOT in version control
- [ ] Test: Encrypt and decrypt national ID
- [ ] Test: Verify encrypted data in database
- [ ] Test: Change encryption key breaks decryption (expected)

#### Data Masking
- [ ] Email masking works (j***@example.com)
- [ ] Phone masking works (+966*****4567)
- [ ] National ID masking works (1****7890)
- [ ] IBAN masking works (SA********************9012)
- [ ] Test: Verify masked data displayed to users

#### Input Validation
- [ ] XSS attempts are blocked
- [ ] SQL injection is prevented
- [ ] File upload validation works
- [ ] Filename sanitization prevents path traversal
- [ ] HTML sanitization removes dangerous tags
- [ ] Test: Submit `<script>alert('xss')</script>` (should be sanitized)
- [ ] Test: Upload file with `../../etc/passwd` name (should be sanitized)
- [ ] Test: Submit `' OR '1'='1` (should not cause SQL error)

---

### 3. Security Middleware ✅

#### Rate Limiting
- [ ] Redis is configured for rate limiting
- [ ] General API limit: 100/minute
- [ ] Authentication limit: 5/minute
- [ ] Rate limit headers are returned
- [ ] Test: Exceed rate limit, verify 429 response
- [ ] Test: Rate limit headers present (X-RateLimit-Limit, etc.)

#### Security Headers
- [ ] All security headers are present in responses
- [ ] CSP header is configured correctly
- [ ] HSTS header is present (production only)
- [ ] X-Frame-Options is DENY
- [ ] X-Content-Type-Options is nosniff
- [ ] Test: Verify headers with `curl -I https://api.barq.sa`

#### CSRF Protection
- [ ] CSRF token is set in cookie on first request
- [ ] CSRF validation works for POST/PUT/DELETE/PATCH
- [ ] Origin header validation works
- [ ] Exempt endpoints (like OAuth) are excluded
- [ ] Test: POST without CSRF token (should fail 403)
- [ ] Test: POST with valid CSRF token (should succeed)

---

### 4. Audit & Monitoring ✅

#### Audit Logging
- [ ] Database table `audit_logs` exists
- [ ] Authentication events are logged
- [ ] Authorization events are logged
- [ ] Data access events are logged
- [ ] PII access is flagged in logs
- [ ] Hash chaining works (previous_hash set)
- [ ] Test: Login creates audit log
- [ ] Test: Verify hash chain integrity

#### Security Monitoring
- [ ] Brute force detection works
- [ ] Unusual location detection works
- [ ] Security alerts are created
- [ ] Alert acknowledgment works
- [ ] Security metrics are calculated
- [ ] Test: 5 failed logins create brute force alert
- [ ] Test: Login from new IP creates location alert

#### Session Management
- [ ] Redis is configured for sessions
- [ ] Session creation works
- [ ] Session validation works
- [ ] Concurrent session limit enforced (3)
- [ ] Session renewal works
- [ ] Logout destroys session
- [ ] Test: Create 4 sessions, verify oldest is removed
- [ ] Test: Logout invalidates session

---

### 5. Infrastructure Security ✅

#### HTTPS/TLS
- [ ] HTTPS is enforced in production
- [ ] TLS 1.3 is enabled (minimum TLS 1.2)
- [ ] SSL certificate is valid and not expired
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header is set
- [ ] Test: Access http:// redirects to https://
- [ ] Test: SSL Labs grade A or A+

#### Secrets Management
- [ ] SECRET_KEY is set and strong (64+ characters)
- [ ] ENCRYPTION_KEY is set and different from SECRET_KEY
- [ ] Database credentials are in environment variables
- [ ] Redis credentials are in environment variables
- [ ] OAuth secrets are in environment variables
- [ ] `.env` file is in `.gitignore`
- [ ] Test: Verify no secrets in git history

#### Database Security
- [ ] Database connection uses SSL/TLS
- [ ] Database user has minimum required permissions
- [ ] Database backups are encrypted
- [ ] Transparent Data Encryption (TDE) is enabled
- [ ] Test: Verify SSL connection to database

---

### 6. Dependency Security ✅

#### Dependency Management
- [ ] All dependencies are pinned to specific versions
- [ ] No known vulnerabilities in dependencies
- [ ] Regular dependency updates are scheduled
- [ ] Test: Run `safety check` (no critical vulnerabilities)
- [ ] Test: Run `pip list --outdated`

```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check --full-report

# Should return: No known security vulnerabilities found
```

---

### 7. Configuration ✅

#### Environment Variables
- [ ] ENVIRONMENT=production is set
- [ ] DEBUG=false is set
- [ ] SECRET_KEY is production-grade
- [ ] ENCRYPTION_KEY is production-grade
- [ ] DATABASE_URL is correct
- [ ] REDIS_URL is correct
- [ ] BACKEND_CORS_ORIGINS is correct
- [ ] All required variables are set

```bash
# Verify environment variables
python -c "from app.config.settings import settings; print('Environment:', settings.ENVIRONMENT)"
python -c "from app.core.security_config import security_config; security_config._validate()"
```

#### Security Configuration
- [ ] Password policy is enforced
- [ ] Token expiration is configured
- [ ] Rate limiting is enabled
- [ ] Brute force protection is enabled
- [ ] Audit logging is enabled
- [ ] Field encryption is enabled
- [ ] Test: Print security config and verify values

---

### 8. OWASP Top 10 Verification ✅

#### A01: Broken Access Control
- [ ] RBAC is enforced on all protected routes
- [ ] Tenant isolation prevents cross-organization access
- [ ] Permission checks cannot be bypassed
- [ ] Test: User A cannot access User B's data

#### A02: Cryptographic Failures
- [ ] Passwords use Argon2
- [ ] PII fields use AES-256-GCM
- [ ] TLS 1.3 is enforced
- [ ] Test: Verify encryption in database

#### A03: Injection
- [ ] SQL injection is prevented (parameterized queries)
- [ ] XSS is prevented (input sanitization)
- [ ] Path traversal is prevented
- [ ] Test: Inject malicious payloads

#### A04: Insecure Design
- [ ] Security requirements documented
- [ ] Threat model created
- [ ] Security controls designed in

#### A05: Security Misconfiguration
- [ ] Security headers configured
- [ ] Error messages don't leak info
- [ ] Defaults are secure
- [ ] Test: Verify headers with security scanner

#### A06: Vulnerable Components
- [ ] No known vulnerabilities
- [ ] Dependencies up to date
- [ ] Test: Run safety check

#### A07: Authentication Failures
- [ ] Brute force protection active
- [ ] Strong password policy
- [ ] Session management secure
- [ ] Test: Account lockout works

#### A08: Software & Data Integrity
- [ ] Audit logging enabled
- [ ] Hash chaining for tamper detection
- [ ] Test: Verify audit log integrity

#### A09: Logging Failures
- [ ] All security events logged
- [ ] Logs protected from tampering
- [ ] Test: Security events create logs

#### A10: SSRF
- [ ] URL validation implemented
- [ ] Internal URLs blocked
- [ ] Test: SSRF attacks blocked

---

### 9. Penetration Testing Preparation ✅

#### Pre-Test Checklist
- [ ] All security features implemented
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Staging environment ready
- [ ] Penetration test scope defined
- [ ] Emergency contact list prepared
- [ ] Backup and rollback plan ready

#### Test Coverage Areas
- [ ] Authentication bypass attempts
- [ ] Authorization bypass attempts
- [ ] Session hijacking attempts
- [ ] CSRF attacks
- [ ] XSS attacks
- [ ] SQL injection attacks
- [ ] Rate limiting bypass
- [ ] Token manipulation
- [ ] Brute force attacks
- [ ] Privilege escalation
- [ ] Data exfiltration

---

### 10. Compliance ✅

#### ZATCA (Saudi Tax Authority)
- [ ] E-invoicing audit trail
- [ ] 7-year data retention configured
- [ ] Tamper-evident logs
- [ ] Test: Generate e-invoice and verify audit log

#### GDPR Principles
- [ ] Data minimization implemented
- [ ] User can delete account
- [ ] User can export data
- [ ] Privacy policy documented
- [ ] Test: User data export works

---

## Production Deployment Checklist

### Pre-Deployment (T-7 days)
- [ ] All security tests passing
- [ ] Penetration test completed and findings addressed
- [ ] Security documentation complete
- [ ] Team training completed
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Emergency contacts updated

### Deployment Day (T-0)
- [ ] Backup database
- [ ] Verify all environment variables
- [ ] Deploy to production
- [ ] Verify HTTPS works
- [ ] Verify Redis connection
- [ ] Verify database connection
- [ ] Run smoke tests
- [ ] Monitor logs for errors
- [ ] Verify security headers
- [ ] Test authentication flow
- [ ] Test authorization
- [ ] Verify audit logs created

### Post-Deployment (T+1 to T+7)
- [ ] Monitor security metrics daily
- [ ] Review audit logs daily
- [ ] Check for security alerts
- [ ] Verify no errors in logs
- [ ] Performance monitoring
- [ ] User feedback collection
- [ ] Schedule first security review (T+30)

---

## Security Testing Commands

### Authentication Tests
```bash
# Test login with correct credentials
curl -X POST https://api.barq.sa/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "correct"}'

# Test brute force protection (5+ attempts)
for i in {1..6}; do
  curl -X POST https://api.barq.sa/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "test@example.com", "password": "wrong"}'
done
# 6th attempt should return 429 Too Many Requests
```

### Authorization Tests
```bash
# Test unauthorized access
curl -X DELETE https://api.barq.sa/couriers/1 \
  -H "Authorization: Bearer [user_token_without_delete_permission]"
# Should return 403 Forbidden
```

### Security Headers Tests
```bash
# Check security headers
curl -I https://api.barq.sa/health

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# Content-Security-Policy: ...
```

### Rate Limiting Tests
```bash
# Test rate limiting (100+ requests in 1 minute)
for i in {1..101}; do
  curl https://api.barq.sa/api/v1/health
done
# 101st request should return 429
```

### CSRF Tests
```bash
# Test CSRF protection
curl -X POST https://api.barq.sa/api/v1/couriers \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Courier"}'
# Without CSRF token, should return 403
```

---

## Security Metrics to Monitor

### Daily Monitoring
- Failed login attempts
- Account lockouts
- Permission denied events
- Security alerts (unacknowledged)
- Unusual login locations
- API error rates
- Rate limit violations

### Weekly Monitoring
- New security vulnerabilities
- Dependency updates available
- Audit log integrity
- Session cleanup statistics
- Token blacklist size

### Monthly Monitoring
- Security incident review
- Penetration test results
- Compliance checklist review
- Security training completion
- Access control review

---

## Emergency Procedures

### Security Incident Response

**Level 1 - Low/Medium**: Response within 24 hours
- Unusual login location
- Minor configuration issue
- Single failed authorization

**Level 2 - High**: Response within 1 hour
- Brute force attack detected
- Multiple privilege escalation attempts
- Data exfiltration alert
- Audit log tampering detected

**Level 3 - Critical**: Immediate response
- Active data breach
- System compromise
- Mass account takeover
- Production database leak

### Emergency Contacts
- Security Team Lead: security-lead@barq.sa
- CTO: cto@barq.sa
- Emergency Hotline: +966-XXX-XXX-XXXX
- External Security Consultant: [contact info]

---

## Sign-Off

This security checklist must be completed and signed off before production deployment.

### Pre-Production Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Security Specialist | _________________ | _________________ | _______ |
| Lead Developer | _________________ | _________________ | _______ |
| DevOps Engineer | _________________ | _________________ | _______ |
| CTO | _________________ | _________________ | _______ |

### Post-Deployment Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Security Specialist | _________________ | _________________ | _______ |
| Operations Manager | _________________ | _________________ | _______ |
| CTO | _________________ | _________________ | _______ |

---

**Document Version**: 1.0
**Last Updated**: December 2, 2025
**Next Review**: January 2, 2026 (monthly)
**Classification**: Internal - Security Critical

---

## Appendix: Security Tool Commands

### Dependency Scanning
```bash
# Install safety
pip install safety

# Check vulnerabilities
safety check --full-report

# Alternative: pip-audit
pip install pip-audit
pip-audit
```

### SSL/TLS Testing
```bash
# Test SSL configuration
openssl s_client -connect api.barq.sa:443 -tls1_3

# Check certificate
openssl s_client -connect api.barq.sa:443 </dev/null 2>/dev/null | openssl x509 -noout -dates

# SSL Labs scan (online)
# https://www.ssllabs.com/ssltest/analyze.html?d=api.barq.sa
```

### Security Headers Testing
```bash
# Using curl
curl -I https://api.barq.sa

# Using httpx (better output)
pip install httpx
python -c "import httpx; r = httpx.get('https://api.barq.sa'); print(r.headers)"

# Online scanner
# https://securityheaders.com/?q=api.barq.sa
```

### Penetration Testing Tools
```bash
# OWASP ZAP (automated security testing)
# Download: https://www.zaproxy.org/download/

# Burp Suite (manual testing)
# Download: https://portswigger.net/burp/communitydownload

# Nuclei (vulnerability scanner)
nuclei -u https://api.barq.sa -t cves/ -t vulnerabilities/
```

---

**END OF SECURITY CHECKLIST**
