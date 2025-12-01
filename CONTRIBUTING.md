# Contributing to BARQ Fleet Management

Thank you for considering contributing to BARQ Fleet Management! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Issue Guidelines](#issue-guidelines)
10. [Community](#community)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Report unacceptable behavior to: conduct@barq.com

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:
- Read the [README.md](README.md)
- Set up your development environment (see [DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md))
- Reviewed existing issues and pull requests
- Joined our Slack workspace (#engineering channel)

### First Time Contributors

If this is your first contribution:

1. **Find a Good First Issue**
   - Look for issues labeled `good-first-issue`
   - These are specifically curated for newcomers
   - Comment on the issue to claim it

2. **Read Documentation**
   - [Architecture Documentation](docs/ARCHITECTURE.md)
   - [API Reference](docs/API_REFERENCE.md)
   - [Developer Setup Guide](docs/DEVELOPER_SETUP.md)

3. **Ask Questions**
   - Don't hesitate to ask in #engineering Slack channel
   - Comment on the issue if you need clarification

---

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports**
   - Report bugs via GitHub Issues
   - Include detailed reproduction steps
   - Provide system information

2. **Feature Requests**
   - Suggest new features or enhancements
   - Explain the use case
   - Discuss in issues before implementing

3. **Code Contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - Code refactoring

4. **Documentation**
   - Fix typos or unclear explanations
   - Add examples
   - Improve API documentation
   - Write tutorials

5. **Testing**
   - Add test cases
   - Improve test coverage
   - Report test failures

---

## Development Workflow

### Branch Strategy

We follow **Git Flow**:

```
main                  → Production-ready code
├── develop           → Integration branch
    ├── feature/xxx   → New features
    ├── bugfix/xxx    → Bug fixes
    ├── hotfix/xxx    → Urgent production fixes
    └── refactor/xxx  → Code refactoring
```

### Branch Naming Convention

**Format:** `type/description-in-kebab-case`

**Examples:**
```
feature/add-courier-profile
bugfix/fix-vehicle-assignment
hotfix/security-patch
refactor/optimize-database-queries
docs/update-api-reference
test/add-courier-unit-tests
```

### Workflow Steps

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/barq-fleet-clean.git
   cd barq-fleet-clean
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/barq/barq-fleet-clean.git
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add courier profile page"
   ```

6. **Keep Branch Updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

7. **Push Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in PR template
   - Request review

---

## Coding Standards

### General Principles

1. **Write Clean Code**
   - Self-documenting code
   - Meaningful variable names
   - Keep functions small and focused
   - DRY (Don't Repeat Yourself)

2. **Follow SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

### Backend (Python/FastAPI)

**Code Style:**
```python
# Use Black formatter (line length: 100)
# Run: black .

# Type hints required
def get_courier(courier_id: UUID) -> Courier:
    """
    Get courier by ID.

    Args:
        courier_id: UUID of the courier

    Returns:
        Courier object

    Raises:
        HTTPException: If courier not found
    """
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier
```

**Imports:**
```python
# Standard library imports
import os
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local imports
from app.models import Courier
from app.schemas import CourierCreate, CourierResponse
from app.services import CourierService
```

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `CourierService`)
- Functions: `snake_case` (e.g., `get_courier_by_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_PAGE_SIZE`)
- Private: `_leading_underscore` (e.g., `_internal_method`)

### Frontend (React/TypeScript)

**Code Style:**
```typescript
// Use ESLint + Prettier
// Run: npm run lint && npm run format

// TypeScript strict mode enabled
interface CourierProps {
  id: string;
  onUpdate: (courier: Courier) => void;
}

const CourierCard: React.FC<CourierProps> = ({ id, onUpdate }) => {
  const [courier, setCourier] = useState<Courier | null>(null);

  // Clear, descriptive function names
  const handleUpdateCourier = async () => {
    // Implementation
  };

  return (
    <div className="courier-card">
      {/* JSX */}
    </div>
  );
};

export default CourierCard;
```

**Naming Conventions:**
- Components: `PascalCase` (e.g., `CourierList`)
- Functions: `camelCase` (e.g., `getCouriers`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Hooks: `useCamelCase` (e.g., `useCouriers`)

### Database

**Naming Conventions:**
- Tables: `lowercase_plural` (e.g., `couriers`, `vehicles`)
- Columns: `lowercase_snake_case` (e.g., `full_name`, `created_at`)
- Indexes: `idx_table_column` (e.g., `idx_couriers_email`)
- Foreign Keys: `fk_table_column` (e.g., `fk_couriers_tenant_id`)

**Migration Naming:**
```
YYYYMMDD_HHMMSS_descriptive_name.py
```

Example: `20251123_140000_add_courier_profile_fields.py`

---

## Testing Guidelines

### Test Coverage

**Minimum Requirements:**
- Backend: 80% code coverage
- Frontend: 70% code coverage
- All new features must include tests

### Backend Testing

**Structure:**
```
backend/tests/
├── unit/              # Unit tests
│   ├── test_services.py
│   ├── test_models.py
│   └── test_schemas.py
├── integration/       # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── e2e/              # End-to-end tests
    └── test_workflows.py
```

**Example Unit Test:**
```python
import pytest
from app.services import CourierService

def test_create_courier(db_session):
    """Test creating a courier."""
    service = CourierService(db_session)
    courier_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+966501234567",
        "national_id": "1234567890"
    }

    courier = service.create_courier(courier_data)

    assert courier.id is not None
    assert courier.name == "John Doe"
    assert courier.email == "john@example.com"

def test_create_courier_duplicate_email(db_session):
    """Test creating courier with duplicate email fails."""
    service = CourierService(db_session)
    # First courier
    service.create_courier({"email": "john@example.com", ...})

    # Second courier with same email should fail
    with pytest.raises(ValueError, match="Email already exists"):
        service.create_courier({"email": "john@example.com", ...})
```

**Run Tests:**
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_services.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose
pytest -v
```

### Frontend Testing

**Structure:**
```
frontend/src/
├── components/
│   ├── CourierList.tsx
│   └── CourierList.test.tsx
└── hooks/
    ├── useCouriers.ts
    └── useCouriers.test.ts
```

**Example Component Test:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { CourierList } from './CourierList';

describe('CourierList', () => {
  it('renders courier list', () => {
    const couriers = [
      { id: '1', name: 'John Doe', email: 'john@example.com' },
      { id: '2', name: 'Jane Smith', email: 'jane@example.com' },
    ];

    render(<CourierList couriers={couriers} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    const handleEdit = jest.fn();
    const courier = { id: '1', name: 'John Doe' };

    render(<CourierCard courier={courier} onEdit={handleEdit} />);

    fireEvent.click(screen.getByRole('button', { name: /edit/i }));

    expect(handleEdit).toHaveBeenCalledWith(courier);
  });
});
```

**Run Tests:**
```bash
# All tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

---

## Documentation

### Code Comments

**When to comment:**
- Complex algorithms
- Non-obvious business logic
- Workarounds or hacks
- Public API functions

**When NOT to comment:**
- Self-explanatory code
- Redundant comments

**Good Example:**
```python
def calculate_eos(hire_date: date, termination_date: date, salary: float) -> float:
    """
    Calculate End of Service (EOS) benefit according to Saudi labor law.

    Formula:
    - First 5 years: Half month salary per year
    - After 5 years: Full month salary per year

    Args:
        hire_date: Employee hire date
        termination_date: Employee termination date
        salary: Monthly salary in SAR

    Returns:
        EOS amount in SAR
    """
    years = (termination_date - hire_date).days / 365.25
    first_five_years = min(years, 5)
    remaining_years = max(years - 5, 0)

    eos = (first_five_years * 0.5 * salary) + (remaining_years * salary)
    return round(eos, 2)
```

### Docstrings

**Python (Google Style):**
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description of function.

    Longer description if needed, explaining behavior,
    edge cases, and examples.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is empty
        HTTPException: If resource not found

    Example:
        >>> function_name("test", 42)
        True
    """
```

**TypeScript (JSDoc):**
```typescript
/**
 * Fetch courier by ID
 *
 * @param id - Courier UUID
 * @returns Promise resolving to Courier object
 * @throws Error if courier not found
 *
 * @example
 * ```ts
 * const courier = await getCourier('uuid-here');
 * ```
 */
async function getCourier(id: string): Promise<Courier> {
  // Implementation
}
```

### Documentation Updates

When adding features, update:
- [ ] API documentation (if adding endpoints)
- [ ] README.md (if changing setup)
- [ ] CHANGELOG.md (always)
- [ ] User Guide (if user-facing)
- [ ] Architecture docs (if changing design)

---

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] Branch is up to date with main
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(fleet): add courier profile page

Add comprehensive courier profile page with:
- Personal information display
- Document management
- Assignment history
- Performance metrics

Closes #123

---

fix(api): resolve vehicle assignment bug

Fixed issue where multiple vehicles could be assigned
to the same courier simultaneously.

Added unique index to prevent duplicate assignments.

Fixes #456

---

docs(api): update authentication endpoints

- Added OAuth 2.0 flow diagram
- Updated request/response examples
- Added error codes reference
```

### PR Template

When creating a PR, fill in this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issue
Closes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests passing
- [ ] No merge conflicts

## Screenshots (if applicable)
[Add screenshots]

## Additional Notes
[Any additional context]
```

### Review Process

1. **Automatic Checks**
   - CI pipeline runs automatically
   - All checks must pass

2. **Code Review**
   - At least 2 approvals required
   - Address all review comments
   - Request re-review after changes

3. **Merge**
   - Squash and merge (default)
   - Delete branch after merge

---

## Issue Guidelines

### Creating an Issue

**Bug Report Template:**
```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information
```

**Feature Request Template:**
```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Mockups, diagrams, etc.
```

### Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `feature` | New feature request |
| `enhancement` | Improvement to existing feature |
| `documentation` | Documentation improvements |
| `good-first-issue` | Good for newcomers |
| `help-wanted` | Extra attention needed |
| `priority: high` | High priority |
| `priority: low` | Low priority |
| `status: blocked` | Blocked by another issue |
| `status: in-progress` | Currently being worked on |

---

## Community

### Communication Channels

- **Slack:** #engineering (for general discussion)
- **GitHub Issues:** For bugs and feature requests
- **Email:** dev@barq.com (for private inquiries)

### Office Hours

Weekly office hours every Wednesday 2-3 PM UTC+3:
- Ask questions
- Get help with PRs
- Discuss architecture decisions

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor awards

---

## License

By contributing to BARQ Fleet Management, you agree that your contributions will be licensed under the same license as the project.

---

## Questions?

If you have questions not covered here:
- Check existing documentation
- Ask in #engineering Slack
- Email dev@barq.com

**Thank you for contributing!** 🎉

---

**Document Owner:** Engineering Team
**Last Updated:** November 23, 2025
