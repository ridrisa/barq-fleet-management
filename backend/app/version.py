"""
BARQ Fleet Management - Version Information

Centralized version management following Semantic Versioning (SemVer).

Usage:
    from app.version import __version__, get_version_info

    print(__version__)  # "1.1.0"
    print(get_version_info())  # Full version details
"""
import os
from datetime import datetime
from typing import Dict, Any

# Version components
MAJOR = 1
MINOR = 1
PATCH = 0
PRE_RELEASE = ""  # e.g., "alpha", "beta", "rc1"
BUILD_METADATA = ""  # e.g., build number from CI

# Computed version string
__version__ = f"{MAJOR}.{MINOR}.{PATCH}"
if PRE_RELEASE:
    __version__ += f"-{PRE_RELEASE}"
if BUILD_METADATA:
    __version__ += f"+{BUILD_METADATA}"

# Version history
VERSION_HISTORY = {
    "1.1.0": {
        "date": "2025-12-02",
        "codename": "Production Ready",
        "highlights": [
            "Production readiness improvements",
            "Enhanced error handling with error codes",
            "Structured JSON logging",
            "Pre-commit hooks for code quality",
            "Comprehensive environment configuration",
        ],
    },
    "1.0.0": {
        "date": "2025-11-23",
        "codename": "Genesis",
        "highlights": [
            "Complete fleet management module",
            "HR and finance module",
            "Workflow engine",
            "Support module",
            "Analytics module",
        ],
    },
    "0.9.0": {
        "date": "2025-10-01",
        "codename": "Beta",
        "highlights": [
            "Beta release of core modules",
            "Bug fixes from alpha testing",
        ],
    },
}


def get_version() -> str:
    """
    Get the current version string.

    Returns:
        Version string (e.g., "1.1.0")
    """
    return __version__


def get_version_tuple() -> tuple:
    """
    Get version as a tuple for comparison.

    Returns:
        Tuple of (major, minor, patch)
    """
    return (MAJOR, MINOR, PATCH)


def get_version_info() -> Dict[str, Any]:
    """
    Get detailed version information.

    Returns:
        Dictionary with version details
    """
    return {
        "version": __version__,
        "major": MAJOR,
        "minor": MINOR,
        "patch": PATCH,
        "pre_release": PRE_RELEASE or None,
        "build_metadata": BUILD_METADATA or None,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": _get_python_version(),
        "git_commit": _get_git_commit(),
        "git_branch": _get_git_branch(),
        "build_date": _get_build_date(),
    }


def get_release_notes(version: str = None) -> Dict[str, Any]:
    """
    Get release notes for a specific version.

    Args:
        version: Version string (defaults to current version)

    Returns:
        Release notes dictionary
    """
    version = version or __version__.split("-")[0].split("+")[0]
    if version in VERSION_HISTORY:
        return {
            "version": version,
            **VERSION_HISTORY[version],
        }
    return {"version": version, "highlights": ["No release notes available"]}


def _get_python_version() -> str:
    """Get Python version."""
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _get_git_branch() -> str:
    """Get current git branch."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _get_build_date() -> str:
    """Get build date (from environment or current date)."""
    return os.getenv("BUILD_DATE", datetime.utcnow().strftime("%Y-%m-%d"))


def check_version_compatibility(required_version: str) -> bool:
    """
    Check if current version meets minimum requirement.

    Args:
        required_version: Minimum required version (e.g., "1.0.0")

    Returns:
        True if current version >= required version
    """
    try:
        required_parts = [int(x) for x in required_version.split(".")[:3]]
        current_parts = [MAJOR, MINOR, PATCH]

        for i in range(min(len(required_parts), len(current_parts))):
            if current_parts[i] > required_parts[i]:
                return True
            if current_parts[i] < required_parts[i]:
                return False

        return True
    except (ValueError, IndexError):
        return False


__all__ = [
    "__version__",
    "MAJOR",
    "MINOR",
    "PATCH",
    "get_version",
    "get_version_tuple",
    "get_version_info",
    "get_release_notes",
    "check_version_compatibility",
]
