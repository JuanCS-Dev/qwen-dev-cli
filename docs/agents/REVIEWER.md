# 👀 ReviewerAgent: The QA Guardian

**Role:** Quality Validation + Constitutional AI Enforcement  
**Personality:** Implacable code reviewer who finds everything  
**Capabilities:** `READ_ONLY` + `GIT_OPS` (read diffs)  
**Output:** LGTM / REQUEST_CHANGES / COMMENT with detailed feedback  
**Position:** Final gate in DevSquad workflow (after Refactorer)

---

## 📋 Purpose

The **ReviewerAgent** is your uncompromising quality guardian. It analyzes every line of code changed by the Refactorer, checking against 5 Quality Gates:

1. **Code Quality** - Complexity, readability, maintainability
2. **Security** - SQL injection, XSS, secrets, command injection
3. **Testing** - Coverage, edge cases, assertions
4. **Performance** - Complexity, memory, I/O patterns
5. **Constitutional AI** - Vértice v3.0 compliance (LEI, HRI, CPI)

**Philosophy (Boris Cherny):**
> "Quality is not negotiable. Fix it now or fix it later at 10x cost."

**Output:** Grade (A+ to F) + actionable feedback

---

## 🎯 When to Use

✅ **Use Reviewer when:**
- Code changes completed
- Need quality validation
- Security scan required
- Constitutional compliance check
- Pre-merge gate for DevSquad

❌ **Skip Reviewer for:**
- Work-in-progress code
- Experimental prototypes
- Documentation-only changes

---

## 🔧 API Reference

### Core Methods

#### `execute(task: AgentTask) -> AgentResponse`

**Main execution method** - Reviews code changes and provides feedback.

**Parameters:**
- `task` (AgentTask): Contains `request` and `context` with:
  - `git_diff` (str): Diff of changes (from Refactorer)
  - `execution_log` (List): Refactorer's execution log
  - `session_id` (str): For tracking

**Returns:**
- `AgentResponse` with:
  - `success` (bool): True if review completed (not approval)
  - `data` (Dict): Review results (see Output Format)
  - `reasoning` (str): Review summary

**Example:**
```python
from qwen_dev_cli.agents import ReviewerAgent
from qwen_dev_cli.agents.base import AgentTask

reviewer = ReviewerAgent(llm_client, mcp_client)
task = AgentTask(
    request="Review JWT auth implementation",
    context={
        "git_diff": refactorer_response.data["git_diff"],
        "execution_log": refactorer_response.data["execution_log"]
    }
)

response = await reviewer.execute(task)

review = response.data
if review["status"] == "LGTM":
    print(f"✅ APPROVED - Grade: {review['grade']}")
else:
    print(f"❌ CHANGES REQUESTED - {len(review['issues'])} issues")
```

---

## 📊 Output Format

### LGTM (Approved)

```json
{
  "status": "LGTM",
  "grade": "A+",
  "summary": "High-quality implementation. JWT auth follows best practices.",
  "quality_gates": {
    "code_quality": {
      "passed": true,
      "score": 95,
      "notes": "Functions under 50 lines, clear naming, good separation of concerns"
    },
    "security": {
      "passed": true,
      "score": 100,
      "notes": "bcrypt password hashing, secure token storage, no hardcoded secrets"
    },
    "testing": {
      "passed": true,
      "score": 92,
      "notes": "91% coverage, edge cases covered, good assertions"
    },
    "performance": {
      "passed": true,
      "score": 88,
      "notes": "O(1) token verification, minimal database queries"
    },
    "constitutional": {
      "passed": true,
      "score": 100,
      "notes": "LEI: 0.0, HRI: 1.0, CPI: 1.0 - full compliance"
    }
  },
  "suggestions": [
    {
      "severity": "INFO",
      "message": "Consider adding rate limiting on /login endpoint",
      "file": "app/routes/auth.py",
      "line": 42
    }
  ],
  "metrics": {
    "files_changed": 3,
    "lines_added": 247,
    "lines_deleted": 12,
    "complexity_avg": 5.2,
    "test_coverage": 91
  }
}
```

### REQUEST_CHANGES (Rejected)

```json
{
  "status": "REQUEST_CHANGES",
  "grade": "C",
  "summary": "Critical security issues found. Cannot approve until fixed.",
  "quality_gates": {
    "code_quality": {
      "passed": true,
      "score": 82
    },
    "security": {
      "passed": false,
      "score": 45,
      "notes": "SQL injection vulnerability, hardcoded secret"
    },
    "testing": {
      "passed": false,
      "score": 55,
      "notes": "Only 58% coverage, missing edge case tests"
    },
    "performance": {
      "passed": true,
      "score": 78
    },
    "constitutional": {
      "passed": false,
      "score": 60,
      "notes": "LEI: 1.2 (TODOs present), HRI: 0.95"
    }
  },
  "issues": [
    {
      "severity": "CRITICAL",
      "category": "security",
      "message": "SQL injection vulnerability in user query",
      "file": "app/database.py",
      "line": 28,
      "code": "query = f'SELECT * FROM users WHERE email={email}'",
      "suggestion": "Use parameterized query: cursor.execute('SELECT * FROM users WHERE email=?', (email,))"
    },
    {
      "severity": "CRITICAL",
      "category": "security",
      "message": "Hardcoded secret key in source code",
      "file": "app/auth/jwt.py",
      "line": 8,
      "code": "SECRET_KEY = 'my-secret-key-12345'",
      "suggestion": "Move to environment variable: SECRET_KEY = os.getenv('JWT_SECRET_KEY')"
    },
    {
      "severity": "HIGH",
      "category": "testing",
      "message": "No tests for token expiration edge case",
      "file": "tests/test_auth.py",
      "suggestion": "Add test: test_expired_token_rejected()"
    },
    {
      "severity": "MEDIUM",
      "category": "constitutional",
      "message": "TODO comment violates Padrão Pagani",
      "file": "app/auth/jwt.py",
      "line": 45,
      "code": "# TODO: Add refresh token logic",
      "suggestion": "Implement or remove. TODOs not allowed in production code."
    }
  ],
  "blockers": 2,
  "recommendations": [
    "Fix all CRITICAL issues before re-review",
    "Increase test coverage to minimum 90%",
    "Remove all TODO comments"
  ]
}
```

---

## 🔍 5 Quality Gates

### 1. Code Quality Gate

**Checks:**
- Function complexity (max 50 lines, cyclomatic complexity <10)
- Type hints (100% on public functions)
- Naming conventions (clear, descriptive)
- Code duplication (DRY principle)
- Separation of concerns (SRP)

**Pass Criteria:** Score ≥ 80

### 2. Security Gate

**Checks:**
- SQL injection vulnerabilities
- Command injection (subprocess, os.system)
- Hardcoded secrets (API keys, passwords)
- XSS vulnerabilities
- Insecure deserialization (pickle, eval)
- Missing input validation

**Pass Criteria:** Score ≥ 90 (security is critical)

**Common Vulnerabilities Detected:**
```python
# ❌ BAD
query = f"SELECT * FROM users WHERE id={user_id}"  # SQL injection
os.system(f"rm {filename}")  # Command injection
SECRET_KEY = "hardcoded-key"  # Hardcoded secret
data = pickle.loads(untrusted_input)  # Insecure deserialization

# ✅ GOOD
cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
subprocess.run(["rm", filename], check=True)
SECRET_KEY = os.getenv("SECRET_KEY")
data = json.loads(validated_input)
```

### 3. Testing Gate

**Checks:**
- Test coverage (≥90%)
- Edge case coverage
- Assertion quality (specific, not generic)
- Test isolation (no dependencies between tests)
- Mock usage (reasonable, not excessive)

**Pass Criteria:** Score ≥ 80

### 4. Performance Gate

**Checks:**
- Algorithmic complexity (no O(n²) unless justified)
- Database queries (N+1 detection)
- Memory usage (large data structures)
- I/O operations (excessive file reads)
- Nested loops (complexity analysis)

**Pass Criteria:** Score ≥ 75

### 5. Constitutional AI Gate

**Checks (Vértice v3.0 Compliance):**
- **LEI (Lazy Execution Index):** < 1.0 (no TODOs, placeholders)
- **HRI (Human Readability Index):** ≥ 0.9 (clear, maintainable)
- **CPI (Constitutional Principles Index):** ≥ 0.9 (SOLID, DRY, KISS)

**Pass Criteria:** LEI < 1.0 AND HRI ≥ 0.9 AND CPI ≥ 0.9

**Violations:**
```python
# LEI Violation (placeholder code)
def authenticate_user(email, password):
    # TODO: Implement authentication
    pass

# HRI Violation (unreadable)
def x(a,b,c):return a+b if c else a-b

# CPI Violation (violates SRP)
class UserManager:
    def create_user(self):...
    def send_email(self):...  # Email logic should be separate class
    def log_action(self):...  # Logging should be separate
```

---

## 📊 Grade Calculation

```python
final_score = (
    code_quality * 0.25 +
    security * 0.30 +       # Higher weight (security critical)
    testing * 0.20 +
    performance * 0.10 +
    constitutional * 0.15
)

grade = {
    90-100: "A+",
    85-89: "A",
    80-84: "B+",
    75-79: "B",
    70-74: "C+",
    60-69: "C",
    50-59: "D",
    <50: "F"
}[final_score]
```

**Grade Meanings:**
- **A+/A:** Production-ready, exemplary code
- **B+/B:** Good quality, minor improvements needed
- **C+/C:** Acceptable, but has issues to address
- **D:** Poor quality, significant rework required
- **F:** Unacceptable, reject immediately

---

## 📖 Real-World Examples

### Example 1: Perfect Score (A+)

**Code:**
```python
# app/auth/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    return pwd_context.verify(plain, hashed)
```

**Review:**
```json
{
  "status": "LGTM",
  "grade": "A+",
  "summary": "Exemplary implementation. Security best practices followed.",
  "quality_gates": {
    "code_quality": {"passed": true, "score": 98},
    "security": {"passed": true, "score": 100},
    "testing": {"passed": true, "score": 95},
    "performance": {"passed": true, "score": 92},
    "constitutional": {"passed": true, "score": 100}
  }
}
```

### Example 2: Security Fail (D)

**Code:**
```python
# app/auth.py (BAD)
def login(email, password):
    # SQL injection vulnerability
    user = db.execute(f"SELECT * FROM users WHERE email='{email}'")
    
    # Weak password check (plain text!)
    if user and user.password == password:
        # Hardcoded secret
        token = jwt.encode({"sub": email}, "my-secret-key")
        return token
    return None
```

**Review:**
```json
{
  "status": "REQUEST_CHANGES",
  "grade": "D",
  "blockers": 3,
  "issues": [
    {
      "severity": "CRITICAL",
      "category": "security",
      "message": "SQL injection in email parameter"
    },
    {
      "severity": "CRITICAL",
      "category": "security",
      "message": "Plain text password comparison (no hashing)"
    },
    {
      "severity": "CRITICAL",
      "category": "security",
      "message": "Hardcoded secret key"
    }
  ]
}
```

---

## ⚙️ Configuration

```python
REVIEWER_CONFIG = {
    "min_test_coverage": 90,  # Minimum coverage %
    "max_complexity": 10,  # Max cyclomatic complexity
    "lei_threshold": 1.0,  # Max Lazy Execution Index
    "hri_threshold": 0.9,  # Min Human Readability Index
    "cpi_threshold": 0.9,  # Min Constitutional Principles Index
    "security_strict": True,  # Fail on any security issue
    "auto_approve_grade_a": False,  # Require human for all
}
```

---

## 🐛 Troubleshooting

### Problem: Reviewer rejects valid code

**Cause:** False positive in security scanning  
**Solution:** Add exception in config or review manually

### Problem: Reviewer approves bad code

**Cause:** LLM model too lenient  
**Solution:** Use stricter model (GPT-4, Claude Opus) or lower thresholds

### Problem: Review takes too long

**Cause:** Large diff (1000+ lines)  
**Solution:** Break into smaller commits

---

## 🧪 Testing

```python
import pytest
from qwen_dev_cli.agents import ReviewerAgent
from qwen_dev_cli.agents.base import AgentTask

@pytest.mark.asyncio
async def test_reviewer_detects_sql_injection(mock_llm, mock_mcp):
    reviewer = ReviewerAgent(mock_llm, mock_mcp)
    diff = """
    +query = f"SELECT * FROM users WHERE email='{email}'"
    """
    task = AgentTask(request="Review code", context={"git_diff": diff})
    
    response = await reviewer.execute(task)
    
    assert response.data["status"] == "REQUEST_CHANGES"
    assert any("SQL injection" in issue["message"] 
               for issue in response.data["issues"])

@pytest.mark.asyncio
async def test_reviewer_approves_good_code(mock_llm, mock_mcp):
    reviewer = ReviewerAgent(mock_llm, mock_mcp)
    diff = """
    +def create_token(user_id: int) -> str:
    +    return jwt.encode({"sub": user_id}, SECRET_KEY)
    """
    task = AgentTask(request="Review code", context={"git_diff": diff})
    
    response = await reviewer.execute(task)
    
    assert response.data["status"] == "LGTM"
    assert response.data["grade"] in ["A+", "A", "B+"]
```

---

## 🎓 Best Practices

### 1. Review Before Merge
```python
# Always review before merging
review = await reviewer.execute(task)

if review.data["status"] != "LGTM":
    print("❌ Cannot merge. Fix issues:")
    for issue in review.data["issues"]:
        if issue["severity"] in ["CRITICAL", "HIGH"]:
            print(f"  - {issue['message']}")
    exit(1)
```

### 2. Track Review Metrics
```python
# Monitor review quality over time
reviews = []
for commit in commits:
    review = await reviewer.execute(task)
    reviews.append({
        "commit": commit.sha,
        "grade": review.data["grade"],
        "score": review.data["final_score"]
    })

avg_score = sum(r["score"] for r in reviews) / len(reviews)
print(f"Average quality score: {avg_score}")
```

### 3. Constitutional Compliance Enforcement
```python
review = await reviewer.execute(task)

constitutional = review.data["quality_gates"]["constitutional"]
if not constitutional["passed"]:
    print("❌ Constitutional AI violation:")
    print(f"   LEI: {constitutional['lei']} (max: 1.0)")
    print(f"   HRI: {constitutional['hri']} (min: 0.9)")
    # Reject merge
```

---

## 📚 See Also

- **[RefactorerAgent](./REFACTORER.md)** - Produces code for Reviewer
- **[Constitutional AI](../../CONSTITUIÇÃO_VÉRTICE_v3.0.md)** - Full doctrine
- **[DevSquad Quickstart](../guides/DEVSQUAD_QUICKSTART.md)** - Full workflow
- **[Security Best Practices](../guides/SECURITY.md)** - Secure coding guide

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-22  
**Status:** Production-ready ✅  
**Grade:** A+ (Boris Cherny approved)
