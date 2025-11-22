# 🔧 Creating Custom Workflows

**Target audience:** Advanced users  
**Time to create workflow:** 15-30 minutes  
**Prerequisite:** Understanding of DevSquad phases

---

## 📋 What is a Workflow?

A **workflow** is a pre-defined sequence of DevSquad phases for common tasks. Instead of describing a task each time, you run a parameterized workflow.

**Benefits:**
- ✅ Consistent execution (same steps every time)
- ✅ Faster (no Architect/Explorer analysis)
- ✅ Parameterized (reusable across projects)
- ✅ Shareable (team can use your workflows)

---

## 🏗️ Workflow Structure

```python
from qwen_dev_cli.orchestration.workflows import Workflow, WorkflowStep, WorkflowType

my_workflow = Workflow(
    name="setup-django",
    description="Create Django project with best practices",
    type=WorkflowType.SETUP,
    parameters={
        "project_name": {"type": "string", "required": True},
        "use_postgres": {"type": "boolean", "default": True}
    },
    steps=[
        WorkflowStep(
            name="create_project",
            description="Create Django project structure",
            agent="Refactorer",
            params={
                "action": "bash_command",
                "command": "django-admin startproject {project_name}"
            }
        ),
        # ... more steps
    ]
)
```

---

## 🎨 Example 1: Setup FastAPI Workflow

**File:** `config/workflows/setup_fastapi.yaml`

```yaml
name: setup-fastapi
description: Create FastAPI project from scratch
type: SETUP
parameters:
  project_name:
    type: string
    required: true
    description: Name of the FastAPI project
  use_docker:
    type: boolean
    default: false
    description: Include Dockerfile

steps:
  - name: create_directory
    agent: Refactorer
    action: create_directory
    params:
      path: "{project_name}"
    
  - name: create_main
    agent: Refactorer
    action: create_file
    params:
      path: "{project_name}/main.py"
      content: |
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        def root():
            return {"message": "Hello World"}
  
  - name: create_requirements
    agent: Refactorer
    action: create_file
    params:
      path: "{project_name}/requirements.txt"
      content: |
        fastapi==0.104.1
        uvicorn[standard]==0.24.0
  
  - name: install_deps
    agent: Refactorer
    action: bash_command
    params:
      command: "cd {project_name} && pip install -r requirements.txt"
  
  - name: run_tests
    agent: Refactorer
    action: bash_command
    params:
      command: "cd {project_name} && pytest"
```

**Usage:**
```bash
$ qwen-dev workflow run setup-fastapi --project-name my_api --use-docker true
```

---

## 📚 Workflow Types

```python
class WorkflowType(Enum):
    SETUP = "setup"          # Create new project
    MIGRATION = "migration"  # Migrate tech stack
    ENHANCEMENT = "enhancement"  # Add feature
    MAINTENANCE = "maintenance"  # Refactor/cleanup
```

---

## 🔧 Advanced: Python Workflow

```python
# config/workflows/add_auth_workflow.py
from qwen_dev_cli.orchestration.workflows import Workflow, WorkflowStep, WorkflowType

def create_add_auth_workflow():
    return Workflow(
        name="add-jwt-auth",
        description="Add JWT authentication to FastAPI",
        type=WorkflowType.ENHANCEMENT,
        parameters={
            "secret_key_env": {
                "type": "string",
                "default": "JWT_SECRET_KEY",
                "description": "Environment variable name for secret key"
            }
        },
        steps=[
            WorkflowStep(
                name="create_auth_module",
                description="Create authentication module",
                agent="Refactorer",
                params={
                    "action": "create_directory",
                    "path": "app/auth"
                }
            ),
            WorkflowStep(
                name="create_jwt_utils",
                description="Create JWT utility functions",
                agent="Refactorer",
                params={
                    "action": "create_file",
                    "path": "app/auth/jwt.py",
                    "template": "jwt_utils_template.py"
                }
            ),
            # ... more steps
        ]
    )
```

**Register workflow:**
```python
# In your config
from config.workflows.add_auth_workflow import create_add_auth_workflow

CUSTOM_WORKFLOWS = [
    create_add_auth_workflow()
]
```

---

## 🎓 Best Practices

### 1. Use Templates
```python
# Create reusable templates
templates/jwt_utils_template.py:
"""
from jose import jwt
SECRET_KEY = os.getenv("{secret_key_env}")
...
"""
```

### 2. Validate Parameters
```python
parameters={
    "project_name": {
        "type": "string",
        "required": True,
        "validator": lambda x: x.isalnum() and len(x) <= 50
    }
}
```

### 3. Add Rollback Steps
```python
steps=[
    WorkflowStep(name="backup", agent="Refactorer", ...),
    WorkflowStep(name="migrate", agent="Refactorer", ...),
    WorkflowStep(
        name="rollback",
        agent="Refactorer",
        trigger="on_failure",  # Only run if migrate fails
        params={"action": "restore_backup"}
    )
]
```

---

## 📊 Testing Workflows

```python
import pytest
from qwen_dev_cli.orchestration import DevSquad

@pytest.mark.asyncio
async def test_setup_fastapi_workflow():
    squad = DevSquad(llm_client, mcp_client)
    result = await squad.run_workflow(
        "setup-fastapi",
        params={"project_name": "test_api", "use_docker": False}
    )
    
    assert result["status"] == "success"
    assert os.path.exists("test_api/main.py")
    assert os.path.exists("test_api/requirements.txt")
```

---

**See also:** [Customizing Agents](./CUSTOMIZING_AGENTS.md) | [DevSquad Quickstart](./DEVSQUAD_QUICKSTART.md)
