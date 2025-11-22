# 🎨 Customizing Agents

**Target audience:** Advanced users  
**Prerequisite:** Python knowledge, understanding of DevSquad

---

## 📋 Why Customize?

Default agents work well for 85% of tasks. Customize when:
- ✅ Domain-specific requirements (e.g., medical, financial)
- ✅ Different coding standards
- ✅ Custom security policies
- ✅ Specialized workflows

---

## 🔧 Customization Levels

### Level 1: Configuration (Easy)

**File:** `config/agents.yaml`

```yaml
agents:
  architect:
    system_prompt_override: |
      You are a medical software architect. FDA compliance is mandatory.
      Veto any request that violates HIPAA regulations.
    temperature: 0.1  # More conservative
    
  reviewer:
    min_test_coverage: 95  # Stricter than default 90
    security_rules:
      - no_phi_in_logs  # Custom rule
      - encryption_required
```

---

### Level 2: Extend Agent (Medium)

```python
# custom_agents/medical_architect.py
from qwen_dev_cli.agents import ArchitectAgent

class MedicalArchitectAgent(ArchitectAgent):
    """Architect with HIPAA compliance checks."""
    
    async def execute(self, task):
        # Pre-check for PHI handling
        if self._contains_phi(task.request):
            if not self._has_encryption_plan(task.context):
                return AgentResponse(
                    success=False,
                    data={"decision": "VETO"},
                    reasoning="PHI detected but no encryption plan provided"
                )
        
        # Delegate to parent
        return await super().execute(task)
    
    def _contains_phi(self, request: str) -> bool:
        phi_keywords = ["patient", "medical_record", "ssn", "diagnosis"]
        return any(kw in request.lower() for kw in phi_keywords)
```

**Register:**
```python
# config/__init__.py
from custom_agents.medical_architect import MedicalArchitectAgent

CUSTOM_AGENTS = {
    "architect": MedicalArchitectAgent
}
```

---

### Level 3: New Agent (Advanced)

```python
# custom_agents/compliance_checker.py
from qwen_dev_cli.agents.base import BaseAgent, AgentRole, AgentCapability

class ComplianceCheckerAgent(BaseAgent):
    """Custom agent for regulatory compliance."""
    
    role = AgentRole.REVIEWER
    capabilities = [AgentCapability.READ_ONLY]
    
    SYSTEM_PROMPT = """You are a compliance checker.
    Check code against SOC2, ISO27001, and GDPR requirements."""
    
    async def execute(self, task):
        # Implement compliance checks
        violations = await self._check_compliance(task.context["git_diff"])
        
        if violations:
            return AgentResponse(
                success=False,
                data={"violations": violations},
                reasoning="Compliance violations found"
            )
        
        return AgentResponse(
            success=True,
            data={"status": "COMPLIANT"},
            reasoning="All compliance checks passed"
        )
```

**Add to DevSquad workflow:**
```python
from qwen_dev_cli.orchestration import DevSquad

squad = DevSquad(llm_client, mcp_client)
squad.add_agent("compliance", ComplianceCheckerAgent(llm, mcp))

# Compliance check runs after Reviewer
result = await squad.execute_mission("Add user signup")
```

---

## 🎨 Custom System Prompts

### Example: Security-Focused Architect

```python
SECURITY_ARCHITECT_PROMPT = """You are a paranoid security architect.

VETO IMMEDIATELY if:
- Any use of eval(), exec(), pickle
- SQL queries without parameterization
- Passwords in plain text
- Secrets hardcoded
- HTTP (not HTTPS)
- No input validation

APPROVE ONLY if:
- All inputs validated and sanitized
- All secrets in environment variables
- All database queries parameterized
- HTTPS enforced
- Authentication and authorization present
"""
```

---

## 🧪 Testing Custom Agents

```python
import pytest
from custom_agents.medical_architect import MedicalArchitectAgent

@pytest.mark.asyncio
async def test_medical_architect_vetoes_unencrypted_phi():
    agent = MedicalArchitectAgent(mock_llm, mock_mcp)
    task = AgentTask(
        request="Add patient records to database",
        context={"encryption": None}
    )
    
    response = await agent.execute(task)
    
    assert response.success is False
    assert "encryption" in response.reasoning.lower()

@pytest.mark.asyncio
async def test_medical_architect_approves_encrypted_phi():
    agent = MedicalArchitectAgent(mock_llm, mock_mcp)
    task = AgentTask(
        request="Add encrypted patient records",
        context={"encryption": "AES-256"}
    )
    
    response = await agent.execute(task)
    
    assert response.success is True
```

---

## 📚 Advanced: Agent Chains

```python
# Create custom workflow with agent chain
from qwen_dev_cli.orchestration import DevSquad

squad = DevSquad(llm_client, mcp_client)

# Custom chain: Architect → ComplianceChecker → Planner → ...
squad.workflow = [
    ("architect", ArchitectAgent),
    ("compliance", ComplianceCheckerAgent),  # Custom agent
    ("explorer", ExplorerAgent),
    ("planner", PlannerAgent),
    ("refactorer", RefactorerAgent),
    ("reviewer", ReviewerAgent),
    ("compliance_final", ComplianceCheckerAgent)  # Re-check after changes
]

result = await squad.execute_mission("Add GDPR data export")
```

---

## 🎓 Best Practices

### 1. Don't Break Base Behavior
```python
class CustomArchitect(ArchitectAgent):
    async def execute(self, task):
        # ✅ Good: Add checks, then delegate to parent
        if self._custom_check(task):
            return await super().execute(task)
        
        # ❌ Bad: Completely override parent behavior
        # return self._my_implementation(task)
```

### 2. Use Configuration Over Code
```python
# ✅ Good: Configurable
class CustomReviewer(ReviewerAgent):
    def __init__(self, llm, mcp, rules):
        super().__init__(llm, mcp)
        self.rules = rules

# ❌ Bad: Hardcoded
class CustomReviewer(ReviewerAgent):
    def __init__(self, llm, mcp):
        super().__init__(llm, mcp)
        self.rules = ["rule1", "rule2"]  # Can't change without editing code
```

### 3. Test Thoroughly
```python
# Test matrix: edge cases, normal cases, failure cases
test_cases = [
    ("valid_request", True),
    ("phi_without_encryption", False),
    ("encrypted_phi", True),
    ("malicious_sql", False),
]

for request, expected_success in test_cases:
    response = await agent.execute(AgentTask(request=request))
    assert response.success == expected_success
```

---

**See also:** [Creating Workflows](./CREATING_WORKFLOWS.md) | [Agent Documentation](../agents/)
