# 🔧 DevSquad Troubleshooting Guide

**Last Updated:** 2025-11-22  
**Coverage:** Common issues + solutions

---

## 🚨 Critical Issues

### Issue 1: Architect Always Vetoes

**Symptoms:**
```
❌ VETO: Request is too vague
❌ VETO: Required dependencies unavailable
```

**Diagnosis:**
1. Check request specificity
2. Verify project context

**Solutions:**
```bash
# ❌ Too vague
> /squad Add auth

# ✅ Specific
> /squad Add JWT authentication using python-jose to FastAPI app

# ✅ With context
> /squad Add JWT auth (existing: FastAPI 0.104, PostgreSQL, SQLAlchemy)
```

**Root Cause:** Architect uses conservative temperature (0.2). Be explicit.

---

### Issue 2: Explorer Finds No Files

**Symptoms:**
```
⚠️ Found 0 relevant files
Token usage: 0/10000
```

**Diagnosis:**
1. Wrong directory?
2. Keywords too specific?
3. Files don't match search pattern?

**Solutions:**
```bash
# Check directory
$ pwd
$ ls -la

# Provide hint files
> /squad Add caching to API (hint: app/routes/api.py, app/services/)

# Broaden keywords
> /squad Add logging to user endpoints  # Not just "logging"
```

---

### Issue 3: Refactorer Fails Repeatedly

**Symptoms:**
```
❌ Step 3/8 failed after 3 attempts
Error: ModuleNotFoundError: jose
```

**Diagnosis:**
Check execution log for error patterns.

**Common Causes + Solutions:**

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | `pip install <module>` |
| `SyntaxError` | Python version mismatch | Check Python version (3.9+) |
| `IntegrityError` | Database state | Reset DB or run migrations |
| `PermissionError` | File permissions | `chmod +w <file>` |

**Debug Mode:**
```bash
$ qwen-dev squad "Add auth" --debug --dry-run
# Dry-run shows what WOULD be executed without executing
```

---

### Issue 4: Reviewer Rejects Everything

**Symptoms:**
```
❌ REQUEST_CHANGES - Grade: C
Issues: 12 (2 CRITICAL, 5 HIGH, 5 MEDIUM)
```

**Diagnosis:**
Review `issues` array in output.

**Common Issues:**

#### A. Security Violations
```python
# ❌ Detected by Reviewer
query = f"SELECT * FROM users WHERE id={user_id}"  # SQL injection

# ✅ Fix
cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
```

#### B. Test Coverage <90%
```bash
# Check current coverage
$ pytest --cov=app tests/
Coverage: 67%  # Below 90% threshold

# Solution: Add more tests
$ pytest tests/ -v  # See what's not covered
```

#### C. Constitutional Violations
```python
# ❌ LEI violation (placeholder code)
def authenticate():
    # TODO: Implement
    pass

# ✅ Fix: Implement fully
def authenticate():
    token = generate_jwt()
    return token
```

---

## ⚠️ Common Warnings

### Warning 1: Token Budget Exceeded

**Symptoms:**
```
⚠️ Token usage: 12,450/10,000 (124%)
```

**Solutions:**
```python
# Increase budget (in config)
EXPLORER_CONFIG = {
    "token_budget": 15000  # Increase from default 10K
}

# OR: Narrow request scope
> /squad Add logging to UserService only  # Not "all services"
```

---

### Warning 2: Self-Correction Loop

**Symptoms:**
```
⚠️ Step 5/8: Attempt 2 - fixing import error
⚠️ Step 5/8: Attempt 3 - fixing type error
```

**Diagnosis:**
Check if same error repeats across attempts.

**Solutions:**
- Validate environment before running
- Check Python version compatibility
- Review error logs for patterns

---

## 🔍 Debugging Techniques

### 1. Dry-Run Mode
```bash
# See what WOULD happen without executing
$ qwen-dev squad "Add auth" --dry-run

Output:
Architect: Would analyze feasibility
Explorer: Would search for auth-related files
Planner: Would generate 8-step plan
[NO EXECUTION]
```

### 2. Verbose Logging
```bash
# Enable debug logs
$ qwen-dev squad "Add auth" --log-level DEBUG

# Logs to: .qwen/logs/devsquad_TIMESTAMP.log
```

### 3. Step-by-Step Execution
```python
# Python API: Execute phases manually
from qwen_dev_cli.orchestration import DevSquad

squad = DevSquad(llm, mcp)

# Phase 1: Architect
arch_result = await squad.architect.execute(task)
print(f"Architect decision: {arch_result.data['decision']}")

# Phase 2: Explorer (only if approved)
if arch_result.success:
    explore_result = await squad.explorer.execute(task)
    print(f"Files found: {len(explore_result.data['relevant_files'])}")

# ... continue manually
```

---

## 🐛 Known Issues

### Issue: LLM Rate Limiting

**Symptoms:**
```
Error: 429 Too Many Requests
```

**Solutions:**
- Wait 60 seconds
- Use different API key
- Switch to different provider (Gemini → OpenAI)

---

### Issue: Git Conflicts

**Symptoms:**
```
Error: CONFLICT (content): Merge conflict in app/main.py
```

**Solutions:**
```bash
# Resolve manually
$ git status
$ git diff app/main.py
$ # Fix conflicts
$ git add app/main.py
$ git commit -m "Resolved conflicts"

# Then re-run mission
> /squad continue
```

---

## 📊 Diagnostic Commands

```bash
# Check DevSquad status
$ qwen-dev squad status

# View recent missions
$ qwen-dev squad history

# Re-run last mission
$ qwen-dev squad retry

# Clear cache
$ qwen-dev squad clear-cache
```

---

## 🆘 Getting Help

### 1. Check Logs
```bash
$ tail -f .qwen/logs/devsquad_latest.log
```

### 2. Report Bug
```bash
$ qwen-dev bug-report
# Generates diagnostic bundle with logs + config
```

### 3. Community Support
- GitHub Issues: https://github.com/JuanCS-Dev/qwen-dev-cli/issues
- Discord: [Join server]

---

**See also:** [DevSquad Quickstart](./DEVSQUAD_QUICKSTART.md) | [Agent Documentation](../agents/)
