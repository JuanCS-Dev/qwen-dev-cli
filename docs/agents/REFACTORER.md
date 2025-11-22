# 🔧 RefactorerAgent: The Code Surgeon

**Role:** Plan Execution with Self-Correction  
**Personality:** Precise surgeon who tries 3 times before giving up  
**Capabilities:** `FULL ACCESS` (READ, EDIT, BASH, GIT)  
**Output:** Modified code + git commits + execution log  
**Position:** Fourth gate in DevSquad workflow (after Planner)

---

## 📋 Purpose

The **RefactorerAgent** is the **ONLY agent** with write permissions. It executes the Planner's atomic steps with surgical precision, self-correcting errors up to 3 times before giving up.

**Key Responsibilities:**
1. **Execute atomic steps** from Planner's plan
2. **Run validation** after each critical operation
3. **Self-correction loop** (max 3 attempts per step)
4. **Automatic rollback** on failure
5. **Git operations** (commit, branch, push)
6. **Test execution** after code changes

**Philosophy (Boris Cherny):**
> "Execute precisely. If it fails, diagnose and retry. If it fails 3 times, escalate to human."

**Safety:** Only agent with FILE_EDIT + BASH_EXEC capabilities

---

## 🎯 When to Use

✅ **Use Refactorer when:**
- Executing multi-step plans
- Need automatic error recovery
- Want git history of changes
- Tests should run after changes
- Rollback capability required

❌ **Skip Refactorer for:**
- Read-only analysis
- Manual exploration
- Direct human coding

---

## 🔧 API Reference

### Core Methods

#### `execute(task: AgentTask) -> AgentResponse`

**Main execution method** - Executes plan steps with self-correction.

**Parameters:**
- `task` (AgentTask): Contains `request` and `context` with:
  - `execution_plan` (Dict): From Planner
  - `session_id` (str): For tracking
  - `dry_run` (bool): Simulate without executing (default: False)

**Returns:**
- `AgentResponse` with:
  - `success` (bool): True if all steps succeeded
  - `data` (Dict): Execution results (see Output Format)
  - `reasoning` (str): Execution summary

**Example:**
```python
from qwen_dev_cli.agents import RefactorerAgent
from qwen_dev_cli.agents.base import AgentTask

refactorer = RefactorerAgent(llm_client, mcp_client)
task = AgentTask(
    request="Execute JWT auth plan",
    context={
        "execution_plan": planner_response.data,
        "session_id": "abc123",
        "dry_run": False
    }
)

response = await refactorer.execute(task)

if response.success:
    print(f"✅ Completed {len(response.data['steps_completed'])} steps")
else:
    print(f"❌ Failed at step {response.data['failed_step']}")
```

---

## 📊 Output Format

### Successful Execution

```json
{
  "steps_completed": 8,
  "steps_failed": 0,
  "execution_log": [
    {
      "step_id": 1,
      "action": "create_directory",
      "status": "SUCCESS",
      "attempts": 1,
      "duration_sec": 0.12,
      "output": "Created app/auth/"
    },
    {
      "step_id": 2,
      "action": "create_file",
      "status": "SUCCESS",
      "attempts": 1,
      "duration_sec": 0.85,
      "output": "Created app/auth/jwt.py (245 lines)"
    },
    {
      "step_id": 3,
      "action": "bash_command",
      "status": "SUCCESS",
      "attempts": 2,
      "duration_sec": 5.32,
      "output": "Tests passed (12/12)",
      "corrections": [
        {
          "attempt": 1,
          "error": "ModuleNotFoundError: jose",
          "diagnosis": "Missing dependency",
          "fix": "pip install python-jose"
        }
      ]
    }
  ],
  "git_commits": [
    {
      "sha": "a1b2c3d",
      "message": "feat(auth): Add JWT authentication",
      "files_changed": 3
    }
  ],
  "tests_passed": 12,
  "tests_failed": 0,
  "total_duration_sec": 125.4
}
```

### Failed Execution (After 3 Attempts)

```json
{
  "steps_completed": 5,
  "steps_failed": 1,
  "failed_step": {
    "step_id": 6,
    "action": "bash_command",
    "status": "FAILED",
    "attempts": 3,
    "errors": [
      {
        "attempt": 1,
        "error": "TypeError: User() missing 1 required positional argument: 'password_hash'",
        "diagnosis": "Database model mismatch",
        "fix_attempted": "Added password_hash field to User model"
      },
      {
        "attempt": 2,
        "error": "IntegrityError: NOT NULL constraint failed: users.password_hash",
        "diagnosis": "Existing records without password_hash",
        "fix_attempted": "Backfilled existing users with temp hash"
      },
      {
        "attempt": 3,
        "error": "OperationalError: no such column: users.password_hash",
        "diagnosis": "Migration not applied",
        "fix_attempted": "Ran alembic upgrade head"
      }
    ],
    "escalation": "Human intervention required. Database migration issue beyond agent capability."
  },
  "rollback_executed": true,
  "rollback_command": "git checkout .",
  "recommendation": "Review database schema. Migration file may be corrupt."
}
```

---

## 🔄 Self-Correction Protocol

```python
MAX_ATTEMPTS = 3

for step in plan.steps:
    success = False
    for attempt in range(1, MAX_ATTEMPTS + 1):
        result = execute_step(step)
        
        if result.success:
            success = True
            break
        
        if attempt < MAX_ATTEMPTS:
            # Attempt correction
            diagnosis = analyze_error(result.error)
            correction = generate_fix(diagnosis)
            apply_correction(correction)
        else:
            # Max attempts reached - ABORT
            rollback()
            escalate_to_human(step, result.errors)
            break
    
    if not success:
        break  # Stop execution
```

**Correction Strategies:**
1. **Attempt 1:** Fix obvious errors (typos, imports, syntax)
2. **Attempt 2:** Analyze full stack trace, check dependencies
3. **Attempt 3:** Review recent changes, validate environment

---

## 🚨 Safety Mechanisms

### 1. Backup Before Destructive Operations
```python
if step.action == "delete_file" or step.risk == "HIGH":
    # Create git commit before executing
    await git_commit("Backup before step {step.id}")
```

### 2. Test Execution After Code Changes
```python
if step.action in ["create_file", "edit_file"]:
    # Run tests after file operations
    test_result = await run_tests()
    if not test_result.success:
        # Rollback if tests fail
        await git_checkout(".")
```

### 3. Validation Commands
```python
if step.validation:
    # Run validation command after step
    validation_result = await bash_exec(step.validation)
    if not validation_result.success:
        # Mark step as failed
        step.status = "FAILED"
```

### 4. Automatic Rollback
```python
if step.failed and attempts >= MAX_ATTEMPTS:
    print("Max attempts reached. Rolling back...")
    await git_checkout(".")  # Undo all changes
    raise ExecutionFailed(f"Could not complete step {step.id}")
```

---

## 📖 Real-World Examples

### Example 1: Successful Execution with Self-Correction

**Step:** Create file with Python code

**Attempt 1:**
```python
# Missing import
def generate_token(user_id):
    return jwt.encode({"sub": user_id}, SECRET_KEY)
```
**Error:** `NameError: name 'jwt' is not defined`

**Attempt 2 (Self-Correction):**
```python
# Added import
from jose import jwt

def generate_token(user_id):
    return jwt.encode({"sub": user_id}, SECRET_KEY)
```
**Success:** ✅ File created, tests passing

### Example 2: Database Migration Failure

**Step:** Run `alembic upgrade head`

**Attempt 1:**
```bash
$ alembic upgrade head
Error: Can't locate revision identified by 'abc123'
```
**Diagnosis:** Migration file missing or corrupted

**Attempt 2:**
```bash
# Regenerate migration
$ alembic revision --autogenerate -m "add password_hash"
$ alembic upgrade head
```
**Error:** `IntegrityError: NOT NULL constraint failed`

**Attempt 3:**
```bash
# Backfill data first
$ python scripts/backfill_password_hash.py
$ alembic upgrade head
```
**Success:** ✅ Migration applied

### Example 3: Escalation to Human

**Step:** Delete production database

**Attempt 1-3:** All attempts fail due to Constitutional AI block  
**Escalation:**
```
⚠️ HUMAN INTERVENTION REQUIRED

Step: DELETE production database
Risk: CRITICAL
Blocker: Constitutional AI Policy (no destructive production operations)
Recommendation: Use production-safe migration strategy or manual approval
```

---

## ⚙️ Configuration

```python
REFACTORER_CONFIG = {
    "max_attempts": 3,  # Max correction attempts per step
    "auto_test": True,  # Run tests after code changes
    "auto_commit": True,  # Git commit after each step
    "rollback_on_failure": True,  # Auto rollback on failure
    "backup_before_high_risk": True,  # Git commit before HIGH-risk steps
    "validation_required": True,  # Run validation commands
}
```

---

## 🐛 Troubleshooting

### Problem: Refactorer fails on first attempt every time

**Cause:** Environment issues (missing deps, wrong Python version)  
**Solution:** Validate environment before running DevSquad

### Problem: Self-correction loops infinitely

**Cause:** Bug in correction logic  
**Solution:** Max attempts enforced (3), but report if this happens

### Problem: Tests fail after successful execution

**Cause:** Tests are outdated or incorrect  
**Solution:** Update tests or run `pytest --lf` to re-run last failed

### Problem: Git rollback didn't restore state

**Cause:** Uncommitted changes before DevSquad start  
**Solution:** Always commit/stash before running DevSquad

---

## 🧪 Testing

```python
import pytest
from qwen_dev_cli.agents import RefactorerAgent
from qwen_dev_cli.agents.base import AgentTask

@pytest.mark.asyncio
async def test_refactorer_executes_plan(mock_llm, mock_mcp):
    refactorer = RefactorerAgent(mock_llm, mock_mcp)
    plan = {
        "steps": [
            {"id": 1, "action": "create_file", "params": {...}},
            {"id": 2, "action": "bash_command", "params": {"command": "pytest"}}
        ]
    }
    task = AgentTask(request="Execute plan", context={"execution_plan": plan})
    
    response = await refactorer.execute(task)
    
    assert response.success is True
    assert response.data["steps_completed"] == 2

@pytest.mark.asyncio
async def test_refactorer_self_corrects(mock_llm, mock_mcp):
    refactorer = RefactorerAgent(mock_llm, mock_mcp)
    # Simulate step that fails on attempt 1, succeeds on attempt 2
    plan = {
        "steps": [
            {"id": 1, "action": "bash_command", "params": {"command": "flaky_test.sh"}}
        ]
    }
    task = AgentTask(request="Execute plan", context={"execution_plan": plan})
    
    response = await refactorer.execute(task)
    
    # Should succeed after correction
    assert response.success is True
    # Check that correction happened
    step_log = response.data["execution_log"][0]
    assert step_log["attempts"] == 2
    assert "corrections" in step_log
```

---

## 🎓 Best Practices

### 1. Dry-Run First
```python
# Test plan without executing
task = AgentTask(
    request="Execute plan",
    context={"execution_plan": plan, "dry_run": True}
)
response = await refactorer.execute(task)
print(f"Dry-run: {len(response.data['steps_completed'])} steps would execute")
```

### 2. Review Execution Log
```python
response = await refactorer.execute(task)

for step_log in response.data["execution_log"]:
    if step_log["attempts"] > 1:
        print(f"⚠️ Step {step_log['step_id']} required {step_log['attempts']} attempts")
        print(f"   Corrections: {step_log.get('corrections', [])}")
```

### 3. Use Checkpoints
```python
# Planner defines checkpoints
checkpoints = plan["checkpoints"]  # [3, 6, 9]

# Refactorer pauses at checkpoints for validation
response = await refactorer.execute(task)

# Check which checkpoints were reached
completed_steps = response.data["steps_completed"]
reached_checkpoints = [cp for cp in checkpoints if cp <= completed_steps]
print(f"Reached checkpoints: {reached_checkpoints}")
```

---

## 📚 See Also

- **[PlannerAgent](./PLANNER.md)** - Generates plan for Refactorer
- **[ReviewerAgent](./REVIEWER.md)** - Validates Refactorer's output
- **[DevSquad Quickstart](../guides/DEVSQUAD_QUICKSTART.md)** - Full workflow
- **[Troubleshooting Guide](../guides/TROUBLESHOOTING.md)** - Common issues

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-22  
**Status:** Production-ready ✅  
**Grade:** A+ (Boris Cherny approved)
