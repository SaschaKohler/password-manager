# Development Guidelines & Best Practices

This document outlines the development standards, best practices, and agent guidelines for the Password Manager Suite project.

## 🎯 Project Overview

**Mission**: Build a secure, enterprise-grade password manager that prioritizes user privacy and data security above all else.

**Core Principles**:
- Security First: Every decision must prioritize security
- Zero-Knowledge: Server never has access to plaintext data
- Privacy by Design: User data protection is fundamental
- Open Source: Transparent, auditable codebase
- Enterprise Ready: Scalable, maintainable architecture

## 🏗️ Architecture Guidelines

### Backend (Django)

```
password_manager/
├── apps/
│   ├── authentication/     # User auth, 2FA, sessions
│   ├── passwords/          # Password CRUD, encryption
│   ├── teams/             # Team management, sharing
│   ├── security/          # Security monitoring, audit logs
│   └── notifications/     # Email, push notifications
├── core/
│   ├── crypto/            # Encryption utilities
│   ├── middleware/        # Custom middleware
│   ├── permissions/       # Custom permissions
│   └── validators/        # Input validation
├── config/                # Django settings, URLs
├── tests/                 # Test suite
└── utils/                 # Shared utilities
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Route components
│   ├── hooks/            # Custom React hooks
│   ├── store/            # State management (Redux/Zustand)
│   ├── services/         # API clients
│   ├── crypto/           # Client-side encryption
│   └── utils/            # Shared utilities
├── public/               # Static assets
└── tests/                # Test suite
```

## 🔐 Security Requirements

### Mandatory Security Practices

1. **Never log sensitive data** (passwords, tokens, encryption keys)
2. **Always validate input** on both client and server side
3. **Use parameterized queries** to prevent SQL injection
4. **Implement rate limiting** on all authentication endpoints
5. **Encrypt all data at rest** and in transit
6. **Use secure headers** (CSP, HSTS, X-Frame-Options)
7. **Regular security audits** with automated tools

### Encryption Standards

- **Symmetric**: AES-256-GCM for data encryption
- **Asymmetric**: RSA-4096 for key exchange
- **Hashing**: Argon2id for password hashing
- **Key Derivation**: PBKDF2 with 100,000+ iterations
- **Random**: Cryptographically secure RNG only

### Data Classification

- **Highly Sensitive**: Master passwords, encryption keys
- **Sensitive**: User passwords, personal data
- **Internal**: Audit logs, usage analytics
- **Public**: Documentation, marketing content

## 🎨 Frontend Development Standards

### Technology Stack

- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Svelte stores
- **Build Tool**: Vite
- **Testing**: Vitest + Svelte Testing Library
- **Linting**: ESLint + Prettier
- **Type Checking**: TypeScript compiler

### Code Style & Standards

#### TypeScript Requirements
```typescript
// All components must have proper TypeScript types
import type { AuthUser } from '$lib/types/auth';
import { writable } from 'svelte/store';

// Use interfaces for type definitions
export interface PasswordEntry {
  id: number;
  title: string;
  username_hint: string;
  url_hint: string;
  category: string;
  tags: string[];
  is_favorite: boolean;
  has_notes: boolean;
  created_at: string;
  updated_at: string;
  last_accessed: string | null;
}

// Functions must have type hints
export function validatePassword(password: string): boolean {
  return password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password);
}
```

#### Component Structure
```svelte
<script lang="ts">
  // 1. Imports
  import { onMount } from 'svelte';
  import type { PasswordEntry } from '$lib/types/password';
  
  // 2. Props and exports
  export let password: PasswordEntry;
  export let selected = false;
  
  // 3. Local state with types
  let loading = false;
  let error: string | null = null;
  
  // 4. Reactive statements
  $: isValid = password.title.length > 0;
  
  // 5. Lifecycle
  onMount(async () => {
    await loadData();
  });
  
  // 6. Functions with type hints
  async function handleClick(): Promise<void> {
    loading = true;
    try {
      await updatePassword();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
    } finally {
      loading = false;
    }
  }
</script>

<!-- 7. Template with accessibility -->
<div class="component-container" role="button" tabindex="0" on:keypress={handleClick}>
  <h2>{password.title}</h2>
  {#if loading}
    <LoadingSpinner />
  {:else if error}
    <ErrorMessage message={error} />
  {:else}
    <button on:click={handleClick} aria-label="Update password">
      Update
    </button>
  {/if}
</div>

<!-- 8. Styles with Tailwind -->
<style>
  .component-container {
    @apply bg-white rounded-lg p-4 shadow-sm;
  }
</style>
```

### Dependencies Management

```bash
# Install dependencies
npm install

# Add new dependency
npm install @sveltejs/adapter-auto

# Add dev dependency
npm install -D @playwright/test

# Update dependencies
npm update

# Run with npm
npm run dev
npm run build
npm run test
```

### Testing Standards

#### Unit Testing
```typescript
// tests/components/PasswordCard.test.ts
import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import PasswordCard from '$lib/components/PasswordCard.svelte';
import type { PasswordEntry } from '$lib/types/password';

describe('PasswordCard', () => {
  const mockPassword: PasswordEntry = {
    id: 1,
    title: 'Test Password',
    username_hint: 'tes***',
    url_hint: 'example.com',
    category: 'Personal',
    tags: ['test'],
    is_favorite: false,
    has_notes: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    last_accessed: null,
  };

  it('renders password information correctly', () => {
    render(PasswordCard, { props: { password: mockPassword } });
    
    expect(screen.getByText('Test Password')).toBeInTheDocument();
    expect(screen.getByText('tes***')).toBeInTheDocument();
  });

  it('shows favorite indicator when favorited', () => {
    const favoritePassword = { ...mockPassword, is_favorite: true };
    render(PasswordCard, { props: { password: favoritePassword } });
    
    expect(screen.getByText('⭐')).toBeInTheDocument();
  });
});
```

#### E2E Testing with Playwright
```typescript
// tests/e2e/registration.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Registration', () => {
  test('user can register with valid data', async ({ page }) => {
    await page.goto('/register');
    
    // Fill form
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=username]', 'testuser');
    await page.fill('[data-testid=password]', 'SecurePass123!');
    await page.fill('[data-testid=confirmPassword]', 'SecurePass123!');
    await page.fill('[data-testid=masterPassword]', 'VerySecureMasterPassword123');
    
    // Submit
    await page.click('[data-testid=register-button]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/');
    await expect(page.locator('h1')).toContainText('Password Manager');
  });

  test('shows validation errors for duplicate email', async ({ page }) => {
    await page.goto('/register');
    
    await page.fill('[data-testid=email]', 'existing@example.com');
    await page.fill('[data-testid=username]', 'newuser');
    await page.fill('[data-testid=password]', 'SecurePass123!');
    await page.fill('[data-testid=confirmPassword]', 'SecurePass123!');
    await page.fill('[data-testid=masterPassword]', 'VerySecureMasterPassword123');
    
    await page.click('[data-testid=register-button]');
    
    // Should show field-specific error
    await expect(page.locator('[data-testid=email-error]')).toContainText('already exists');
  });
});
```

### Frontend Git Workflow

#### Same Branching Strategy as Backend
The frontend follows the **exact same Git workflow** as the Python backend:

- **Features**: `feature/frontend-feature-name`
- **Extensions**: `extension/frontend-extension-name`
- **Documentation**: `docs/frontend-doc-name`
- **Experimental**: `experimental/frontend-feature-name`
- **Bugfixes**: `bugfix/frontend-frontend-issue`
- **Hotfixes**: `hotfix/frontend-critical-fix`

#### Frontend-Specific Commit Types
```
feat(frontend): add password strength indicator component
fix(frontend): resolve responsive layout issues on mobile
refactor(frontend): extract API service to separate module
test(frontend): add unit tests for password validation
style(frontend): update Tailwind CSS configuration
docs(frontend): update Svelte component documentation
chore(frontend): upgrade SvelteKit to latest version
```

#### Frontend Development Environment Rules

##### Before Starting Frontend Work
1. **Create new branch**: `git checkout -b feature/frontend-your-feature`
2. **Pull latest changes**: `git pull origin develop`
3. **Setup environment**: `cd frontend && npm install`

##### During Frontend Development
1. **Commit frequently**: `git add . && git commit -m "feat(frontend): add login form validation"`
2. **Push regularly**: `git push origin feature/frontend-your-feature`
3. **Run tests**: `npm run test` before each commit
4. **Type checking**: `npm run check` includes TypeScript validation
5. **Linting**: `npm run lint` before PR
6. **Build check**: `npm run build` to ensure production build works

##### Frontend-Specific Quality Gates
- **TypeScript compilation**: Must pass without errors
- **Unit tests**: Must pass with >90% coverage
- **E2E tests**: Critical user flows must pass
- **Accessibility**: WCAG compliance checks
- **Performance**: Bundle size and load time limits
- **Security**: No sensitive data in client-side code

#### Frontend Pull Request Requirements

##### PR Template for Frontend
```markdown
## Description
Brief description of frontend changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] UI/UX improvement

## Frontend Testing
- [ ] Unit tests pass (>90% coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass for critical flows
- [ ] Manual testing completed
- [ ] Accessibility testing completed

## Technical Requirements
- [ ] TypeScript compilation passes
- [ ] ESLint/Prettier checks pass
- [ ] Build process succeeds
- [ ] Bundle size within limits
- [ ] Performance metrics acceptable

## UI/UX Review
- [ ] Design system compliance
- [ ] Responsive design verified
- [ ] Cross-browser compatibility
- [ ] Accessibility standards met
- [ ] Screenshots included for UI changes

## Security Review
- [ ] No sensitive data in client code
- [ ] Input validation implemented
- [ ] XSS prevention measures
- [ ] CSRF protection included
- [ ] Secure headers configured

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Type hints comprehensive
```

#### Frontend Emergency Procedures

##### Hotfix Process for Frontend
```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/frontend-critical-ui-issue

# Fix, test, commit
cd frontend
npm run build
npm run test
git add . && git commit -m "fix(frontend): critical security vulnerability in auth component"

# Merge immediately
git checkout main
git merge --no-ff hotfix/frontend-critical-ui-issue
git push origin main

# Deploy frontend
npm run build -- --prod
# Deploy to production
```

### Frontend Security Guidelines

#### Client-Side Security
```typescript
// Never store sensitive data in localStorage
// Use secure HTTP-only cookies for tokens
// Validate all inputs on client and server

function sanitizeInput(input: string): string {
  // Sanitize user input to prevent XSS
  return input
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .trim()
    .substring(0, 1000); // Limit length
}

// Secure API calls
async function secureAPICall(endpoint: string, data: any): Promise<any> {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}
```

#### Content Security Policy
```html
<!-- In app.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:;">
```

## 🐍 Python Development Standards

### Code Style

```python
# Use Black for formatting
# Use isort for import sorting
# Use flake8 for linting
# Use mypy for type checking

# Example of clean, secure code:
from cryptography.fernet import Fernet
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()

class PasswordService:
    """Secure password management service."""
    
    def __init__(self, encryption_key: bytes) -> None:
        self._cipher = Fernet(encryption_key)
    
    def encrypt_password(self, password: str) -> bytes:
        """Encrypt password with AES-256."""
        if not password:
            raise ValueError("Password cannot be empty")
        return self._cipher.encrypt(password.encode())
    
    def decrypt_password(self, encrypted_data: bytes) -> str:
        """Decrypt password safely."""
        try:
            return self._cipher.decrypt(encrypted_data).decode()
        except Exception as e:
            # Log security event, don't expose details
            security_logger.warning("Password decryption failed")
            raise DecryptionError("Invalid encrypted data")
```

### Dependencies Management (uv)

```bash
# Initialize project with uv
uv init --python 3.11

# Add dependencies
uv add django djangorestframework
uv add --group dev pytest pytest-django black isort mypy
uv add --group security bandit safety

# Sync environment
uv sync

# Run with uv
uv run python manage.py runserver
uv run pytest
```

### Testing Standards

```python
# tests/test_password_service.py
import pytest
from apps.passwords.services import PasswordService
from tests.factories import UserFactory

class TestPasswordService:
    """Test suite for PasswordService."""
    
    @pytest.fixture
    def password_service(self):
        """Create test password service."""
        test_key = Fernet.generate_key()
        return PasswordService(test_key)
    
    def test_encrypt_decrypt_roundtrip(self, password_service):
        """Test password encryption/decryption."""
        password = "SuperSecurePassword123!"
        encrypted = password_service.encrypt_password(password)
        decrypted = password_service.decrypt_password(encrypted)
        assert decrypted == password
    
    def test_empty_password_raises_error(self, password_service):
        """Test empty password validation."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            password_service.encrypt_password("")
```

## 🐳 Docker Guidelines

### Dockerfile Best Practices

```dockerfile
# Multi-stage build for security
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Production stage
FROM python:3.11-slim as production

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy dependencies
COPY --from=builder /opt/uv /opt/uv
COPY --from=builder /app /app
WORKDIR /app

# Security: Set proper permissions
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check || exit 1

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]
```

### Docker Compose Development

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:password@db:5432/password_manager
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uv run python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=password_manager
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## ☸️ Kubernetes Guidelines

### Security Configuration

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: password-manager
  labels:
    security.kubernetes.io/enforce: "strict"

---
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: password-manager
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  SECRET_KEY: <base64-encoded>
  ENCRYPTION_KEY: <base64-encoded>

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: password-manager-api
  namespace: password-manager
spec:
  replicas: 3
  selector:
    matchLabels:
      app: password-manager-api
  template:
    metadata:
      labels:
        app: password-manager-api
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: api
        image: password-manager:latest
        ports:
        - containerPort: 8000
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🧪 Testing Strategy

### Test Pyramid

1. **Unit Tests (70%)**: Fast, isolated tests for individual functions
2. **Integration Tests (20%)**: Test component interactions
3. **E2E Tests (10%)**: Full application workflows

### Security Testing

```bash
# Static analysis
bandit -r ./apps/
safety check

# Dependency scanning
uv pip-audit

# Dynamic analysis
python manage.py test --settings=config.settings.test

# Penetration testing
docker run -it owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000
```

### Performance Testing

```bash
# Load testing
locust -f tests/locustfile.py --host=http://localhost:8000

# Database query analysis
python manage.py test --settings=config.settings.test --parallel
```

## � Development Workflow

### Branching Strategy

#### Branch Naming Convention
- **Features**: `feature/feature-name`
- **Extensions**: `extension/extension-name`  
- **Documentation**: `docs/doc-name`
- **Experimental**: `experimental/feature-name`
- **Bugfixes**: `bugfix/description`
- **Hotfixes**: `hotfix/critical-fix`

#### Branch Creation Rules
1. **Every feature gets its own branch** - no exceptions
2. **Branch from `develop`** for features
3. **Branch from `main`** only for hotfixes
4. **Descriptive names** - no `feature-1` or `temp-branch`

### Git Workflow

#### Commit Frequency
- **Commit often, commit early** - after every meaningful change
- **Atomic commits** - one logical change per commit
- **Revert-friendly** - commits should be easily reversible
- **Fail-fast recovery** - if code breaks, revert to last working commit

#### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add 2FA with TOTP support
fix(crypto): resolve encryption key rotation issue
docs(api): update authentication endpoints documentation
refactor(models): simplify password encryption logic
```

### Pull Request Process

#### PR Requirements
1. **Create PR for every branch** before merging
2. **Title must follow commit format**
3. **Description must include**:
   - What was changed
   - Why it was changed
   - How to test
   - Screenshots if UI changes

#### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Security Review
- [ ] No sensitive data logged
- [ ] Input validation implemented
- [ ] Encryption properly handled

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

#### Merge Strategy
- **Squash merge** for feature branches
- **Merge commit** for hotfixes
- **Never force push** to shared branches
- **Delete feature branches** after merge

### Development Environment Rules

#### Before Starting Work
1. **Create new branch**: `git checkout -b feature/your-feature-name`
2. **Pull latest changes**: `git pull origin develop`
3. **Setup environment**: `make dev`

#### During Development
1. **Commit frequently**: `git add . && git commit -m "feat(scope): progress message"`
2. **Push regularly**: `git push origin feature/your-feature-name`
3. **Run tests**: `make test` before each commit
4. **Security checks**: `make security` before PR
5. **Type checking**: `make lint` includes mypy type validation
6. **Coverage check**: Ensure >90% test coverage before PR

#### When Stuck or Code Fails
1. **Revert to last working commit**: `git reset --hard HEAD~1`
2. **Create new branch**: `git checkout -b feature/alternative-approach`
3. **Document failure**: Add notes to PR description
4. **Ask for help**: Tag team members in PR

### AI Assistant Guidelines

#### For Windsurf AI
- **Always create branches** before making changes
- **Commit after each major change** with descriptive messages
- **Never work directly on main/develop**
- **Ask for confirmation** before destructive operations
- **Provide rollback options** in suggestions
- **Add comprehensive type hints** to all functions
- **Write tests for new code** before suggesting merge
- **Run mypy type checking** before completing changes

#### For KiloSoft AI  
- **Review code before suggesting merges**
- **Check security implications** of changes
- **Validate commit messages** follow convention
- **Ensure tests pass** before PR approval
- **Verify type hints are comprehensive**
- **Check test coverage meets >90% requirement**
- **Run security scans** on proposed changes

### Emergency Procedures

#### Code Recovery
```bash
# If everything breaks
git checkout main
git pull origin main
git checkout -b feature/recovery-start

# Reset to last known good state
git log --oneline --graph
git reset --hard <commit-hash>
```

#### Hotfix Process
```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue

# Fix, test, commit
git add . && git commit -m "fix(scope): critical security issue"

# Merge immediately
git checkout main
git merge --no-ff hotfix/critical-issue
git push origin main
```

## � Agent Guidelines

### Development Agent Responsibilities

1. **Code Quality**: Ensure all code passes linting and type checking
2. **Security**: Never commit sensitive data or security vulnerabilities
3. **Testing**: Maintain >90% test coverage for critical paths
4. **Documentation**: Update docs for all API changes
5. **Performance**: Monitor and optimize database queries
6. **Type Safety**: Use comprehensive type hints throughout codebase
7. **Test Coverage**: Write tests for all new features and functions

### Code Quality Standards

#### Type Hints Requirements
- **All functions must have type hints** for parameters and return values
- **Use specific types** instead of generic `Any` when possible
- **Import types from typing module** for complex type definitions
- **Create TypedDict classes** for structured data
- **Use Optional[]** for nullable parameters
- **Document complex types** with inline comments

#### Type Hint Examples
```python
# Good: Comprehensive type hints
from typing import List, Optional, Dict, TypedDict
from rest_framework.request import Request
from rest_framework.response import Response

class UserData(TypedDict):
    email: str
    username: str
    password: str

def create_user(data: UserData) -> Optional[User]:
    """Create user with validated data."""
    return User.objects.create_user(**data)

def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email address."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

# API views with proper typing
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    """Register new user with enhanced security."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user: User = serializer.save()
        return Response({'user_id': user.id}, status=201)
    return Response(serializer.errors, status=400)
```

#### Testing Requirements
- **Write tests for all new functions** and methods
- **Test both happy path and error cases**
- **Use descriptive test method names**
- **Test type annotations** with mypy
- **Mock external dependencies** appropriately
- **Maintain >90% test coverage** for critical code

#### Test Examples
```python
# Good: Comprehensive test with type hints
class UserModelTests(TestCase):
    """Test cases for User model."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user_data: UserData = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
    
    def test_create_user_with_totp(self) -> None:
        """Test user creation with TOTP functionality."""
        user = User.objects.create_user(**self.user_data)
        
        # Generate TOTP secret
        secret: str = user.generate_totp_secret()
        self.assertIsNotNone(secret)
        
        # Verify TOTP token
        token_valid: bool = user.verify_totp('123456')
        self.assertIsInstance(token_valid, bool)
    
    def test_user_registration_api(self) -> None:
        """Test user registration API endpoint."""
        url = reverse('authentication:register')
        response: Response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_id', response.data)
```

### Code Review Checklist

- [ ] Security implications reviewed
- [ ] Tests written and passing (>90% coverage)
- [ ] Documentation updated
- [ ] Performance impact assessed
- [ ] Error handling implemented
- [ ] Logging appropriate (no sensitive data)
- [ ] Dependencies vetted
- [ ] Migration scripts provided
- [ ] **Type hints added for all functions**
- [ ] **Type checking passes with mypy**
- [ ] **Tests cover type annotations**
- [ ] **No `Any` types used without justification**

### Deployment Checklist

- [ ] All tests passing in CI/CD
- [ ] Security scans clean
- [ ] Database migrations tested
- [ ] Environment variables validated
- [ ] Health checks passing
- [ ] Rollback plan prepared
- [ ] Monitoring configured
- [ ] Backup strategy verified

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v3
    - name: Install dependencies
      run: uv sync
    - name: Run tests
      run: uv run pytest --cov=.
    - name: Security scan
      run: uv run bandit -r ./apps/
    - name: Type check
      run: uv run mypy ./apps/

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run security audit
      run: |
        uv pip-audit
        safety check
        trivy fs --security-checks vuln,config .

  deploy:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/
        kubectl rollout status deployment/password-manager-api
```

## 📚 Learning Resources

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Cryptography Handbook](https://cryptography.io/en/latest/hazmat/)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)

### Django
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)

### Kubernetes
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Helm Charts](https://helm.sh/docs/)

## 🔄 Continuous Improvement

### Metrics to Track
- Code coverage percentage
- Security scan results
- Performance benchmarks
- Bug escape rate
- Deployment frequency
- Mean time to recovery

### Regular Activities
- Weekly security reviews
- Monthly dependency updates
- Quarterly architecture reviews
- Annual security audits

---

**Remember**: In password management, there's no room for security compromises. Every line of code should be written with security as the primary concern.
