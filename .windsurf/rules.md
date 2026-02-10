# Windsurf AI Development Rules

## 🚀 Branch Management Rules

### MANDATORY: Always Create Branches
- **NEVER work directly on `main` or `develop`**
- **ALWAYS create a new branch** before making any changes
- **Branch naming must follow convention**:
  - `feature/feature-name` for new features
  - `extension/extension-name` for extensions
  - `docs/doc-name` for documentation
  - `experimental/feature-name` for experiments
  - `bugfix/description` for bug fixes
  - `hotfix/critical-fix` for urgent fixes

### Branch Creation Workflow
```bash
# Before any work - ALWAYS do this:
git checkout -b feature/your-descriptive-name
git pull origin develop  # or main for hotfixes
```

## 🔄 Commit Frequency Rules

### Commit Often, Commit Early
- **Commit after every meaningful change**
- **Atomic commits only** - one logical change per commit
- **Revert-friendly commits** - should be easily reversible
- **Fail-fast recovery** - if code breaks, revert immediately

### When to Commit
- ✅ After completing a function/method
- ✅ After fixing a bug
- ✅ After adding tests
- ✅ After updating documentation
- ✅ After refactoring
- ❌ Never commit broken code
- ❌ Never commit with sensitive data

### Commit Message Format
```
type(scope): description

[optional body explaining what and why]

[optional footer with references]
```

**Examples:**
```
feat(auth): add TOTP 2FA support
fix(crypto): resolve encryption key rotation bug
docs(api): update authentication endpoints
refactor(models): simplify password validation
test(auth): add unit tests for 2FA flows
```

## 🎯 Pull Request Requirements

### PR Creation Rules
- **Create PR for EVERY branch** before merging
- **Title must follow commit format**
- **Description must include**:
  - What was changed
  - Why it was changed
  - How to test
  - Any breaking changes

### PR Template Usage
Always use the provided PR template with checkboxes completed.

### Merge Strategy
- **Squash merge** for feature branches
- **Merge commit** for hotfixes only
- **NEVER force push** to shared branches
- **DELETE feature branches** after merge

## 🚨 Emergency Procedures

### When Code Fails
1. **STOP immediately** - don't continue with broken code
2. **Revert to last working commit**:
   ```bash
   git reset --hard HEAD~1
   ```
3. **Create new branch** for alternative approach
4. **Document the failure** in commit/PR description
5. **Ask for help** if needed

### Recovery Commands
```bash
# If everything breaks completely
git checkout main
git pull origin main
git checkout -b feature/recovery-start

# See commit history for rollback point
git log --oneline --graph -10
git reset --hard <last-working-commit-hash>
```

## 🤖 AI Assistant Specific Rules

### For Windsurf AI
- **ALWAYS check current branch** before suggesting changes
- **ALWAYS suggest branch creation** if on main/develop
- **ALWAYS provide commit message** with each change
- **ALWAYS ask for confirmation** before destructive operations
- **ALWAYS provide rollback instructions** for complex changes

### Code Review Rules
- **Check security implications** of all changes
- **Validate input handling** and sanitization
- **Ensure no sensitive data** in logs/commits
- **Verify tests pass** before suggesting merge
- **Check documentation** is updated

## 📋 Development Workflow Checklist

### Before Starting Work
- [ ] Created new branch with proper naming
- [ ] Pulled latest changes from develop/main
- [ ] Environment is setup and working
- [ ] Tests are passing

### During Development
- [ ] Committing frequently with descriptive messages
- [ ] Running tests before each commit
- [ ] Following security guidelines
- [ ] Updating documentation as needed

### Before Creating PR
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Security review completed
- [ ] Documentation updated
- [ ] PR description filled out completely

## 🔒 Security Rules

### NEVER Commit
- Passwords, API keys, tokens
- Encryption keys or secrets
- User credentials or personal data
- Temporary debug code with sensitive output

### ALWAYS Verify
- Input validation is implemented
- Error handling doesn't expose sensitive data
- Logging doesn't contain passwords/tokens
- Encryption is properly implemented

## 🎯 Quality Gates

### Code Must Pass
- `make lint` - Code style and formatting
- `make test` - All tests with coverage
- `make security` - Security scans
- Manual review - Human brain validation

### Before Merge
- All automated checks pass
- Security review completed
- Documentation updated
- Tests added/updated
- PR approved by human reviewer

---

**Remember**: This is a vibe-coding project, but security and quality still matter. Commit often, branch always, and never be afraid to revert and try again! 🚀
