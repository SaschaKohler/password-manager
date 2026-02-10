# Frontend Development Guidelines & Best Practices

This document outlines the development standards, best practices, and agent guidelines for the Password Manager Frontend project.

## 🎯 Project Overview

**Mission**: Build a modern, secure, and performant frontend for the Password Manager using SvelteKit, TypeScript, and Tailwind CSS.

**Core Principles**:
- **Performance First**: Fast loading and smooth interactions
- **Security by Design**: Secure UI patterns and data handling
- **Accessibility**: WCAG compliant and keyboard navigable
- **Modern Stack**: SvelteKit + TypeScript + Tailwind CSS
- **Developer Experience**: Clean, maintainable, and well-documented code

## 🏗️ Architecture Guidelines

### Frontend Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── PasswordCard.svelte
│   │   │   ├── PasswordForm.svelte
│   │   │   ├── SearchBar.svelte
│   │   │   └── Modal.svelte
│   │   ├── stores/           # State management
│   │   │   ├── auth.ts
│   │   │   ├── passwords.ts
│   │   │   └── settings.ts
│   │   ├── services/         # API and utility services
│   │   │   ├── api.ts
│   │   │   ├── crypto.ts
│   │   │   └── storage.ts
│   │   ├── types/            # TypeScript type definitions
│   │   │   ├── password.ts
│   │   │   ├── auth.ts
│   │   │   └── api.ts
│   │   └── utils/            # Utility functions
│   │       ├── validation.ts
│   │       ├── formatting.ts
│   │       └── constants.ts
│   ├── routes/               # SvelteKit pages
│   │   ├── +page.svelte      # Main dashboard
│   │   ├── +layout.svelte    # Root layout
│   │   ├── login/
│   │   ├── register/
│   │   └── settings/
│   ├── app.html              # HTML template
│   ├── app.css               # Global styles
│   └── app.d.ts              # TypeScript declarations
├── static/                   # Static assets
├── tests/                    # Test files
├── tailwind.config.js        # Tailwind configuration
├── postcss.config.js         # PostCSS configuration
├── vite.config.ts            # Vite configuration
├── svelte.config.js          # Svelte configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

## 🎨 Svelte Development Standards

### Component Structure

```svelte
<script lang="ts">
  // 1. Imports
  import { onMount } from 'svelte';
  import type { PasswordEntry } from '$lib/types/password';
  
  // 2. Props and exports
  export let password: PasswordEntry;
  export let selected = false;
  
  // 3. Local state
  let loading = false;
  let error: string | null = null;
  
  // 4. Reactive statements
  $: isValid = password.title.length > 0;
  
  // 5. Lifecycle
  onMount(async () => {
    await loadData();
  });
  
  // 6. Functions
  async function handleClick() {
    loading = true;
    try {
      await updatePassword();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<!-- 7. Template -->
<div class="component-container">
  <h2>{password.title}</h2>
  {#if loading}
    <LoadingSpinner />
  {:else if error}
    <ErrorMessage message={error} />
  {:else}
    <button on:click={handleClick}>
      Update
    </button>
  {/if}
</div>

<!-- 8. Styles -->
<style>
  .component-container {
    @apply bg-white rounded-lg p-4 shadow-sm;
  }
</style>
```

### TypeScript Best Practices

#### **Type Definitions**
```typescript
// lib/types/password.ts
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

export interface CreatePasswordData {
  title: string;
  username: string;
  password: string;
  url?: string;
  notes?: string;
  category?: string;
  tags?: string[];
  is_favorite?: boolean;
}
```

#### **Generic Types**
```typescript
// lib/types/api.ts
export interface ApiResponse<T> {
  data: T;
  message: string;
  status: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

### State Management with Svelte Stores

#### **Writable Stores**
```typescript
// lib/stores/auth.ts
import { writable, derived } from 'svelte/store';
import type { AuthState, AuthUser } from '$lib/types/auth';

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: false,
    error: null,
  });

  // Derived stores
  const isAuthenticated = derived(
    { subscribe },
    ($state) => $state.isAuthenticated && $state.token !== null
  );

  return {
    subscribe,
    isAuthenticated,
    
    // Actions
    async login(email: string, password: string) {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const response = await api.login(email, password);
        set({
          isAuthenticated: true,
          user: response.user,
          token: response.token,
          loading: false,
          error: null,
        });
      } catch (error) {
        update(state => ({
          ...state,
          loading: false,
          error: error.message,
        }));
      }
    },
    
    logout() {
      set({
        isAuthenticated: false,
        user: null,
        token: null,
        loading: false,
        error: null,
      });
    }
  };
}

export const auth = createAuthStore();
```

## 🎨 Tailwind CSS Guidelines

### Design System

#### **Color Palette**
```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#f9fafb',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        }
      }
    }
  }
}
```

#### **Component Classes**
```css
/* app.css */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  
  .btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 shadow-sm;
  }
  
  .btn-secondary {
    @apply bg-secondary-600 text-white hover:bg-secondary-700 focus:ring-secondary-500 shadow-sm;
  }
  
  .form-input {
    @apply block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 sm:text-sm;
  }
  
  .password-card {
    @apply bg-white border border-gray-200 rounded-xl p-4 hover:shadow-medium hover:border-primary-300 transition-all duration-200 cursor-pointer;
  }
}
```

### Responsive Design

#### **Mobile-First Approach**
```svelte
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Cards -->
  </div>
</div>
```

#### **Breakpoint Usage**
- **sm**: 640px and up
- **md**: 768px and up
- **lg**: 1024px and up
- **xl**: 1280px and up

## 🔐 Security Guidelines

### Frontend Security

#### **Data Handling**
```typescript
// Never store sensitive data in localStorage
// Use secure HTTP-only cookies for tokens
// Validate all inputs on client and server

function validatePassword(password: string): boolean {
  // Client-side validation
  if (password.length < 8) return false;
  if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) return false;
  return true;
}
```

#### **XSS Prevention**
```svelte
<!-- Always escape user input -->
<div>{#if userInput}
  {@html userInput} <!-- ❌ NEVER do this -->
{/if}

<!-- ✅ Safe approach -->
<div>{userInput}</div>
```

#### **CSRF Protection**
```typescript
// Include CSRF tokens in API calls
const response = await fetch('/api/passwords/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
  },
  body: JSON.stringify(data),
});
```

## 🧪 Testing Guidelines

### Unit Testing

#### **Component Testing**
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
    expect(screen.getByText('example.com')).toBeInTheDocument();
  });

  it('shows favorite indicator when favorited', () => {
    const favoritePassword = { ...mockPassword, is_favorite: true };
    render(PasswordCard, { props: { password: favoritePassword } });
    
    expect(screen.getByText('⭐')).toBeInTheDocument();
  });
});
```

#### **Store Testing**
```typescript
// tests/stores/auth.test.ts
import { get } from 'svelte/store';
import { describe, it, expect, beforeEach } from 'vitest';
import { auth } from '$lib/stores/auth';

describe('Auth Store', () => {
  beforeEach(() => {
    auth.reset();
  });

  it('updates authentication state on login', async () => {
    await auth.login('test@example.com', 'password');
    
    const state = get(auth);
    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toBeTruthy();
    expect(state.token).toBeTruthy();
  });

  it('clears state on logout', () => {
    auth.logout();
    
    const state = get(auth);
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
  });
});
```

### E2E Testing

#### **Playwright Testing**
```typescript
// tests/e2e/password-manager.test.ts
import { test, expect } from '@playwright/test';

test.describe('Password Manager', () => {
  test('user can login and view passwords', async ({ page }) => {
    await page.goto('/');
    
    // Login
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password');
    await page.click('[data-testid=login-button]');
    
    // Verify dashboard
    await expect(page.locator('h1')).toContainText('Password Manager');
    await expect(page.locator('[data-testid=password-list]')).toBeVisible();
  });

  test('user can create new password', async ({ page }) => {
    await page.goto('/');
    await login(page);
    
    // Create password
    await page.click('[data-testid=add-password-button]');
    await page.fill('[data-testid=password-title]', 'Test Password');
    await page.fill('[data-testid=password-username]', 'testuser');
    await page.fill('[data-testid=password-password]', 'Secret123!');
    await page.click('[data-testid=save-button]');
    
    // Verify password created
    await expect(page.locator('text=Test Password')).toBeVisible();
  });
});
```

## 🚀 Performance Guidelines

### Bundle Optimization

#### **Code Splitting**
```typescript
// Dynamic imports for large components
const PasswordForm = lazy(() => import('$lib/components/PasswordForm.svelte'));

// Route-based code splitting
// SvelteKit automatically handles this
```

#### **Image Optimization**
```svelte
<!-- Use next-gen formats and responsive images -->
<img 
  src="/api/og/image.webp" 
  alt="Password Manager" 
  class="w-full h-auto rounded-lg"
  loading="lazy"
/>
```

### Runtime Performance

#### **Reactivity Optimization**
```svelte
<script>
  // ✅ Good: Use reactive statements efficiently
  $: filteredPasswords = passwords.filter(p => 
    p.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // ❌ Avoid: Complex computations in template
  {#each passwords.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase())) as password}
    <!-- This runs on every render -->
  {/each}
</script>
```

#### **Memory Management**
```typescript
// ✅ Good: Cleanup subscriptions
import { onDestroy } from 'svelte';

const unsubscribe = auth.subscribe(handleAuthChange);
onDestroy(unsubscribe);

// ✅ Good: Use stores for shared state
// ❌ Avoid: Global variables or singletons
```

## 📱 Accessibility Guidelines

### WCAG Compliance

#### **Semantic HTML**
```svelte
<!-- ✅ Good: Semantic elements -->
<main>
  <header>
    <h1>Password Manager</h1>
    <nav aria-label="Main navigation">
      <ul>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/settings">Settings</a></li>
      </ul>
    </nav>
  </header>
  
  <section aria-labelledby="passwords-heading">
    <h2 id="passwords-heading">Your Passwords</h2>
    <!-- Password list -->
  </section>
</main>
```

#### **ARIA Attributes**
```svelte
<button 
  on:click={handleToggle}
  aria-expanded={isOpen}
  aria-controls="password-details"
  aria-label="Toggle password details"
>
  {isOpen ? 'Hide' : 'Show'} Details
</button>

<div 
  id="password-details"
  class={isOpen ? 'block' : 'hidden'}
  aria-hidden={!isOpen}
>
  <!-- Password details -->
</div>
```

#### **Keyboard Navigation**
```typescript
// Handle keyboard events
function handleKeydown(event: KeyboardEvent) {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault();
      handleClick();
      break;
    case 'Escape':
      event.preventDefault();
      close();
      break;
  }
}
```

## 🔄 Development Workflow

### Branch Strategy

#### **Branch Naming**
- `feature/component-name` - New components
- `feature/auth-flow` - Authentication features
- `fix/ui-bug` - UI fixes
- `refactor/tailwind-migration` - Refactoring

### Code Review Checklist

#### **Component Review**
- [ ] TypeScript types are correct
- [ ] Props are properly typed
- [ ] Event handlers are properly named
- [ ] Accessibility attributes are included
- [ ] Responsive design works
- [ ] Loading states are handled
- [ ] Error states are handled

#### **Store Review**
- [ ] Store has proper typing
- [ ] Reactive statements are efficient
- [ ] Actions handle errors properly
- [ ] Store cleanup is implemented

### Git Workflow

#### **Commit Messages**
```
feat(components): add password card component
fix(auth): resolve login validation issue
refactor(stores): optimize password store reactivity
style(tailwind): migrate to utility classes
test(e2e): add login flow tests
```

## 🛠️ Tool Configuration

### ESLint Configuration

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:svelte/recommended"
  ],
  "rules": {
    "svelte/no-at-html-tags": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "prefer-const": "error"
  }
}
```

### Prettier Configuration

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "svelteIndentScriptAndStyle": true
}
```

### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true
  }
}
```

## 📚 Learning Resources

### Svelte Documentation
- [Svelte Tutorial](https://svelte.dev/tutorial)
- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Svelte FAQ](https://svelte.dev/faq)

### Tailwind CSS Resources
- [Tailwind Docs](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com/components)
- [Headless UI](https://headlessui.dev/)

### Testing Resources
- [Vitest Docs](https://vitest.dev/guide/)
- [Playwright Docs](https://playwright.dev/docs)
- [Testing Library](https://testing-library.com/docs/)

## 🎯 Best Practices Summary

### ✅ Do's
- Use TypeScript for all new code
- Follow the established component structure
- Implement proper error handling
- Write tests for new features
- Use Tailwind utility classes
- Follow accessibility guidelines
- Optimize for performance
- Write clear commit messages

### ❌ Don'ts
- Don't use `any` type
- Don't store sensitive data in localStorage
- Don't skip accessibility testing
- Don't use inline styles (except for dynamic values)
- Don't commit sensitive information
- Don't ignore TypeScript errors
- Don't skip testing

## 🔍 Code Quality Tools

### Required Tools
```bash
# Install development dependencies
yarn add -D eslint @typescript-eslint/eslint-plugin eslint-plugin-svelte
yarn add -D prettier prettier-plugin-svelte
yarn add -D vitest @testing-library/svelte @testing-library/jest-dom
yarn add -D playwright @playwright/test
```

### Pre-commit Hooks
```bash
# Install husky for git hooks
yarn add -D husky lint-staged

# package.json
{
  "lint-staged": {
    "*.{svelte,ts,js}": ["eslint --fix", "prettier --write"],
    "*.{svelte,ts}": ["vitest related"]
  }
}
```

---

This document serves as the definitive guide for frontend development practices. All contributors should follow these guidelines to ensure code quality, consistency, and maintainability.
