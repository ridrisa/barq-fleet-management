#!/usr/bin/env python3
"""
BARQ Fleet Management - Security Verification Script

This script verifies that all P0 security hardening tasks are properly implemented.
Run this before deploying to production.

Usage:
    python scripts/verify_security.py

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class SecurityVerifier:
    """Verifies P0 security hardening implementation"""

    def __init__(self):
        self.backend_path = Path(__file__).parent.parent
        self.passed_checks = 0
        self.failed_checks = 0
        self.warnings = 0

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'=' * 80}")
        print(f"  {text}")
        print(f"{'=' * 80}\n")

    def check_pass(self, message: str):
        """Record passed check"""
        self.passed_checks += 1
        print(f"✅ PASS: {message}")

    def check_fail(self, message: str, details: str = ""):
        """Record failed check"""
        self.failed_checks += 1
        print(f"❌ FAIL: {message}")
        if details:
            print(f"   Details: {details}")

    def check_warning(self, message: str):
        """Record warning"""
        self.warnings += 1
        print(f"⚠️  WARN: {message}")

    def verify_sql_injection_fix(self) -> bool:
        """Verify SQL injection fix in RLS context"""
        self.print_header("1. SQL Injection Fix (RLS Context)")

        files_to_check = [
            self.backend_path / "app/core/dependencies.py",
            self.backend_path / "app/core/database.py",
        ]

        vulnerable_pattern = re.compile(r'text\(f["\'].*SET app\.current_org_id.*["\'].*\)')
        secure_pattern = re.compile(r'text\(["\']SET app\.current_org_id = :org_id["\'].*\)')

        all_secure = True

        for file_path in files_to_check:
            if not file_path.exists():
                self.check_fail(f"File not found: {file_path}")
                all_secure = False
                continue

            content = file_path.read_text()

            # Check for vulnerable f-string pattern
            if vulnerable_pattern.search(content):
                self.check_fail(
                    f"Vulnerable SQL found in {file_path.name}",
                    "f-string used in SET app.current_org_id"
                )
                all_secure = False
            else:
                self.check_pass(f"No f-string SQL injection in {file_path.name}")

            # Check for secure parameterized pattern
            if secure_pattern.search(content):
                self.check_pass(f"Parameterized queries found in {file_path.name}")
            else:
                self.check_warning(f"No RLS queries found in {file_path.name}")

        return all_secure

    def verify_token_blacklist(self) -> bool:
        """Verify token blacklist implementation"""
        self.print_header("2. Token Blacklist Implementation")

        blacklist_file = self.backend_path / "app/core/token_blacklist.py"
        dependencies_file = self.backend_path / "app/core/dependencies.py"

        if not blacklist_file.exists():
            self.check_fail("Token blacklist file not found", str(blacklist_file))
            return False

        self.check_pass("Token blacklist file exists")

        # Check implementation
        content = blacklist_file.read_text()

        required_functions = [
            "is_blacklisted",
            "blacklist_token",
            "blacklist_user_tokens",
        ]

        for func in required_functions:
            if f"def {func}" in content:
                self.check_pass(f"Function '{func}' implemented")
            else:
                self.check_fail(f"Function '{func}' not found")
                return False

        # Check integration in dependencies
        dep_content = dependencies_file.read_text()
        if "from app.core.token_blacklist import" in dep_content:
            self.check_pass("Token blacklist imported in dependencies")
        else:
            self.check_fail("Token blacklist not imported in dependencies")
            return False

        if "is_token_blacklisted(token)" in dep_content:
            self.check_pass("Token blacklist check in get_current_user")
        else:
            self.check_fail("Token blacklist check missing from get_current_user")
            return False

        return True

    def verify_jwt_security(self) -> bool:
        """Verify JWT security configuration"""
        self.print_header("3. JWT Security Configuration")

        settings_file = self.backend_path / "app/config/settings.py"
        dependencies_file = self.backend_path / "app/core/dependencies.py"

        if not settings_file.exists():
            self.check_fail("Settings file not found")
            return False

        settings_content = settings_file.read_text()
        dep_content = dependencies_file.read_text()

        # Check expiration configuration
        if 'default_expire = "15"' in settings_content:
            self.check_pass("Production token expiration set to 15 minutes")
        else:
            self.check_warning("Production token expiration may not be 15 minutes")

        # Check audience and issuer
        if "JWT_AUDIENCE" in settings_content:
            self.check_pass("JWT_AUDIENCE configured")
        else:
            self.check_fail("JWT_AUDIENCE not configured")
            return False

        if "JWT_ISSUER" in settings_content:
            self.check_pass("JWT_ISSUER configured")
        else:
            self.check_fail("JWT_ISSUER not configured")
            return False

        # Check verification in dependencies
        if "audience=settings.JWT_AUDIENCE" in dep_content:
            self.check_pass("Audience verification enabled")
        else:
            self.check_fail("Audience verification not enabled")
            return False

        if "issuer=settings.JWT_ISSUER" in dep_content:
            self.check_pass("Issuer verification enabled")
        else:
            self.check_fail("Issuer verification not enabled")
            return False

        if '"verify_aud": True' in dep_content:
            self.check_pass("Explicit audience verification option set")
        else:
            self.check_warning("Explicit audience verification option may not be set")

        return True

    def verify_org_id_validation(self) -> bool:
        """Verify organization ID validation"""
        self.print_header("4. Organization ID Validation")

        dependencies_file = self.backend_path / "app/core/dependencies.py"
        content = dependencies_file.read_text()

        # Check for integer conversion and validation
        if "org_id = int(org_id)" in content:
            self.check_pass("Organization ID integer conversion")
        else:
            self.check_fail("Organization ID integer conversion missing")
            return False

        if "if org_id < 1:" in content or "org_id < 1" in content:
            self.check_pass("Organization ID range validation (> 0)")
        else:
            self.check_fail("Organization ID range validation missing")
            return False

        if "Invalid organization" in content:
            self.check_pass("Invalid organization error message")
        else:
            self.check_warning("Generic error message for invalid org ID")

        return True

    def verify_oauth_org_context(self) -> bool:
        """Verify OAuth organization context"""
        self.print_header("5. OAuth Organization Context")

        auth_file = self.backend_path / "app/api/v1/auth.py"

        if not auth_file.exists():
            self.check_fail("Auth file not found")
            return False

        content = auth_file.read_text()

        # Check login endpoint
        login_section = self._extract_function(content, "def login")
        if login_section and '"org_id": organization_id' in login_section:
            self.check_pass("Login endpoint includes org_id in token")
        else:
            self.check_fail("Login endpoint missing org_id in token")
            return False

        if login_section and '"org_role": organization_role' in login_section:
            self.check_pass("Login endpoint includes org_role in token")
        else:
            self.check_fail("Login endpoint missing org_role in token")
            return False

        # Check Google OAuth endpoint
        google_section = self._extract_function(content, "def google_auth")
        if google_section and '"org_id": organization_id' in google_section:
            self.check_pass("Google OAuth includes org_id in token")
        else:
            self.check_fail("Google OAuth missing org_id in token")
            return False

        # Check register endpoint
        register_section = self._extract_function(content, "def register")
        if register_section and '"org_id": organization_id' in register_section:
            self.check_pass("Register endpoint includes org_id in token")
        else:
            self.check_fail("Register endpoint missing org_id in token")
            return False

        return True

    def verify_password_reset_hardening(self) -> bool:
        """Verify password reset hardening"""
        self.print_header("6. Password Reset Hardening")

        user_enhancements_file = self.backend_path / "app/api/v1/admin/user_enhancements.py"

        if not user_enhancements_file.exists():
            self.check_fail("User enhancements file not found")
            return False

        content = user_enhancements_file.read_text()

        # Check response schema doesn't include token
        if 'class PasswordResetResponse' in content:
            schema_section = self._extract_class(content, "PasswordResetResponse")
            if 'reset_token' not in schema_section and 'temporary_password' not in schema_section:
                self.check_pass("PasswordResetResponse doesn't expose tokens/passwords")
            else:
                self.check_fail("PasswordResetResponse exposes sensitive data")
                return False

        # Check for generic messages
        if "If an account exists with this email" in content:
            self.check_pass("Generic success message (prevents user enumeration)")
        else:
            self.check_warning("Generic success message not found")

        # Check admin reset doesn't return password
        if "admin_reset_user_password" in content:
            admin_section = self._extract_function(content, "admin_reset_user_password")
            if "temporary_password" not in admin_section or '"temporary_password"' not in admin_section:
                self.check_pass("Admin reset doesn't return temporary password")
            else:
                self.check_fail("Admin reset returns temporary password")
                return False

        return True

    def verify_health_endpoint_protection(self) -> bool:
        """Verify health endpoint protection"""
        self.print_header("7. Health Endpoint Protection")

        health_file = self.backend_path / "app/api/v1/health.py"

        if not health_file.exists():
            self.check_fail("Health file not found")
            return False

        content = health_file.read_text()

        # Check detailed endpoint has authentication
        detailed_section = self._extract_function(content, "def health_check_detailed")
        if detailed_section and "Depends(get_current_user)" in detailed_section:
            self.check_pass("Detailed health endpoint requires authentication")
        else:
            self.check_fail("Detailed health endpoint doesn't require authentication")
            return False

        # Check basic endpoint is minimal
        basic_section = self._extract_function(content, "def health_check_basic")
        if basic_section:
            if "DATABASE_URL" not in basic_section and "SECRET_KEY" not in basic_section:
                self.check_pass("Basic health endpoint doesn't expose credentials")
            else:
                self.check_fail("Basic health endpoint exposes sensitive data")
                return False

        return True

    def verify_environment_config(self) -> bool:
        """Verify environment configuration"""
        self.print_header("8. Environment Configuration")

        # Check for .env.example
        env_example = self.backend_path / ".env.example"
        if env_example.exists():
            self.check_pass(".env.example file exists")
        else:
            self.check_warning(".env.example file not found")

        # Check settings validation
        settings_file = self.backend_path / "app/config/settings.py"
        content = settings_file.read_text()

        if "_require_secret" in content:
            self.check_pass("Secret key validation implemented")
        else:
            self.check_warning("Secret key validation not found")

        return True

    def _extract_function(self, content: str, function_signature: str) -> str:
        """Extract function content"""
        lines = content.split('\n')
        in_function = False
        function_lines = []
        indent_level = None

        for line in lines:
            if function_signature in line:
                in_function = True
                indent_level = len(line) - len(line.lstrip())

            if in_function:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_level and function_lines:
                    break
                function_lines.append(line)

        return '\n'.join(function_lines)

    def _extract_class(self, content: str, class_name: str) -> str:
        """Extract class content"""
        return self._extract_function(content, f"class {class_name}")

    def run_all_checks(self) -> bool:
        """Run all security verification checks"""
        print("\n" + "=" * 80)
        print("  BARQ Fleet Management - Security Verification")
        print("  P0 Security Hardening Checks")
        print("=" * 80)

        checks = [
            self.verify_sql_injection_fix,
            self.verify_token_blacklist,
            self.verify_jwt_security,
            self.verify_org_id_validation,
            self.verify_oauth_org_context,
            self.verify_password_reset_hardening,
            self.verify_health_endpoint_protection,
            self.verify_environment_config,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.check_fail(f"Check failed with exception: {check.__name__}", str(e))

        # Print summary
        self.print_header("Summary")
        print(f"✅ Passed: {self.passed_checks}")
        print(f"❌ Failed: {self.failed_checks}")
        print(f"⚠️  Warnings: {self.warnings}")

        if self.failed_checks == 0:
            print("\n🎉 ALL SECURITY CHECKS PASSED!")
            print("✅ Production-ready from security perspective")
            return True
        else:
            print(f"\n❌ {self.failed_checks} SECURITY CHECK(S) FAILED")
            print("⚠️  Fix issues before deploying to production")
            return False


def main():
    """Main entry point"""
    verifier = SecurityVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
