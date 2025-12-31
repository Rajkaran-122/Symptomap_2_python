# 🤝 Contributing to SymptoMap Doctor Station

Thank you for considering contributing to SymptoMap! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Code Style](#code-style)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)
8. [Reporting Bugs](#reporting-bugs)
9. [Feature Requests](#feature-requests)

---

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility for mistakes
- Prioritize public health impact

---

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Basic knowledge of FastAPI and React

### Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/symptomap.git
cd symptomap

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/symptomap.git
```

---

## Development Setup

### Backend Setup
```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Run Development Servers
```bash
# Terminal 1 - Backend
cd backend-python
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## Making Changes

### Branching Strategy
```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Conventions
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

Examples:
- `feature/alert-expiry-notification`
- `fix/map-marker-placement`
- `docs/update-api-documentation`

---

## Code Style

### Python (Backend)
We use **black** for formatting and **flake8** for linting.

```bash
# Format code
black backend-python/

# Check linting
flake8 backend-python/

# Type checking
mypy backend-python/
```

**Style Guidelines:**
- Use type hints
- Maximum line length: 100 characters
- Follow PEP 8
- Write docstrings for all functions
- Use meaningful variable names

**Example:**
```python
from typing import List, Optional

def get_active_outbreaks(city: Optional[str] = None) -> List[Outbreak]:
    """
    Retrieve active outbreaks, optionally filtered by city.
    
    Args:
        city: Optional city name to filter by
        
    Returns:
        List of active outbreak objects
    """
    # Implementation
    pass
```

### TypeScript (Frontend)
We use **Prettier** for formatting and **ESLint** for linting.

```bash
# Format code
npx prettier --write "src/**/*.{ts,tsx}"

# Check linting
npm run lint

# Fix linting issues
npm run lint -- --fix
```

**Style Guidelines:**
- Use TypeScript, avoid `any` types
- Use functional components with hooks
- Follow Airbnb React style guide
- Use meaningful component and variable names
- Maximum line length: 100 characters

**Example:**
```typescript
interface OutbreakProps {
  disease: string;
  cases: number;
  onSubmit: (data: OutbreakData) => void;
}

export const OutbreakForm: React.FC<OutbreakProps> = ({ 
  disease, 
  cases, 
  onSubmit 
}) => {
  // Implementation
};
```

---

## Testing

### Backend Tests (pytest)
```bash
cd backend-python
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html
```

**Writing Tests:**
```python
import pytest
from fastapi.testclient import TestClient

def test_doctor_login(client: TestClient):
    """Test doctor login endpoint"""
    response = client.post(
        "/api/v1/doctor/login",
        json={"password": "Doctor@SymptoMap2025"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Frontend Tests (Vitest)
```bash
cd frontend
npm test

# With coverage
npm test -- --coverage
```

**Writing Tests:**
```typescript
import { render, screen } from '@testing-library/react';
import { DoctorLogin } from './DoctorLogin';

describe('DoctorLogin', () => {
  it('renders login form', () => {
    render(<DoctorLogin />);
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
});
```

---

## Pull Request Process

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Checked for console errors
- [ ] Tested on multiple browsers (if frontend)

### Commit Messages
Follow **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(outbreak): add CSV import functionality

fix(map): correct marker placement on mobile devices

docs(readme): update installation instructions

test(auth): add login integration tests
```

### Submitting Pull Request
1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to GitHub and create a Pull Request

3. Fill in the PR template:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   How was this tested?
   
   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated
   ```

4. Wait for review and address feedback

---

## Reporting Bugs

### Before Reporting
- Check existing issues
- Test on latest version
- Gather relevant information

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g. Windows 10, macOS 12]
- Browser: [e.g. Chrome 120]
- Python: [e.g. 3.10.5]
- Node: [e.g. 18.16.0]

## Screenshots
If applicable

## Additional Context
Any other information
```

---

## Feature Requests

### Template
```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this needed? Who will use it?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Mockups, examples, references
```

---

## Code Review Guidelines

### For Reviewers
- Be respectful andconstructive
- Focus on code quality, not personal preferences
- Explain reasoning behind suggestions
- Approve or request changes within 48 hours

### For Contributors
- Respond to feedback promptly
- Don't take criticism personally
- Ask questions if unclear
- Request re-review after making changes

---

## Development Workflow

### Typical Flow
```bash
# 1. Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and commit
git add .
git commit -m "feat(scope): description"

# 4. Keep branch updated
git fetch upstream
git rebase upstream/main

# 5. Push to your fork
git push origin feature/my-feature

# 6. Create Pull Request on GitHub
```

---

## Project Structure

```
symptomap/
├── backend-python/         # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   └── main.py        # App entry point
│   └── tests/             # Backend tests
│
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/    # Reusable components
│   │   └── App.tsx       # Main app component
│   └── tests/            # Frontend tests
│
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── README.md
```

---

## Need Help?

- 📖 Read existing documentation
- 💬 Ask in GitHub Discussions
- 📧 Email: contribute@symptomap.example.com
- 🐛 Report issues on GitHub

---

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

**Thank you for making SymptoMap better!** 🎉

Every contribution helps support public health initiatives worldwide.
