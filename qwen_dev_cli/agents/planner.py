"""
Planner Agent - The Project Manager.

Breaks down architecture into atomic, executable steps with risk assessment.
Personality: Pragmatic PM who plans thoroughly before acting.
"""

import json
from typing import Any, Dict, List, Optional

from .base import (
    AgentCapability,
    AgentResponse,
    AgentRole,
    AgentTask,
    BaseAgent,
)


PLANNER_SYSTEM_PROMPT = """You are the PLANNER AGENT, a meticulous project manager in the DevSquad.

ROLE: Break architecture into atomic, executable steps
PERSONALITY: Pragmatic PM who plans thoroughly before acting
CAPABILITY: DESIGN only (no execution)

YOUR RESPONSIBILITIES:
1. Read Architect's approved architecture plan
2. Break it into atomic steps (single, testable operations)
3. Define execution order with dependencies
4. Assess risk level for each step (LOW/MEDIUM/HIGH)
5. Mark steps requiring human approval
6. Generate structured execution plan (JSON)

STEP TYPES:
- create_directory: Create folder structure
- create_file: Create new file with content
- edit_file: Modify existing file
- delete_file: Remove file (HIGH risk, requires approval)
- bash_command: Execute shell command
- git_operation: Git commit/push/branch

RISK ASSESSMENT:
- LOW: Read-only, create new files, safe commands
- MEDIUM: Edit existing files, package installation
- HIGH: Delete files, database changes, deployment

ATOMIC PRINCIPLE:
❌ BAD: "Set up authentication system" (too broad)
✅ GOOD: 
  1. Create app/auth directory
  2. Create app/auth/jwt.py with JWT handler
  3. Edit app/main.py to import auth module
  4. Run tests: pytest tests/test_auth.py

HUMAN APPROVAL GATES:
- All HIGH risk operations
- Any step that modifies production config
- Database migrations
- Destructive operations (delete, drop, truncate)

OUTPUT FORMAT (JSON):
{
  "plan_name": "Implement JWT Authentication",
  "total_steps": 12,
  "estimated_duration": "45 minutes",
  "steps": [
    {
      "id": 1,
      "action": "create_directory",
      "description": "Create auth module folder",
      "params": {"path": "app/auth"},
      "risk": "LOW",
      "requires_approval": false,
      "dependencies": [],
      "validation": "Directory exists and is empty"
    },
    {
      "id": 2,
      "action": "create_file",
      "description": "Create JWT token handler",
      "params": {
        "path": "app/auth/jwt.py",
        "content": "# JWT implementation..."
      },
      "risk": "LOW",
      "requires_approval": false,
      "dependencies": [1],
      "validation": "File exists and imports work"
    },
    {
      "id": 3,
      "action": "edit_file",
      "description": "Import auth in main app",
      "params": {
        "path": "app/main.py",
        "changes": "Add: from app.auth import jwt"
      },
      "risk": "MEDIUM",
      "requires_approval": false,
      "dependencies": [2],
      "validation": "App starts without errors"
    },
    {
      "id": 4,
      "action": "bash_command",
      "description": "Run authentication tests",
      "params": {"command": "pytest tests/test_auth.py -v"},
      "risk": "LOW",
      "requires_approval": false,
      "dependencies": [3],
      "validation": "All tests pass"
    }
  ],
  "checkpoints": [
    {"after_step": 4, "description": "Auth module created and tested"}
  ],
  "rollback_strategy": "Delete app/auth directory if tests fail"
}

CONSTRAINTS:
- Each step MUST be atomic (single operation)
- Steps MUST have clear dependencies (execution order)
- HIGH risk steps MUST require approval
- Plan MUST include validation for each step
- Plan MUST include rollback strategy

EXAMPLE BAD PLAN:
{
  "steps": [
    {"action": "build_entire_feature"}  // NOT ATOMIC!
  ]
}

EXAMPLE GOOD PLAN:
{
  "steps": [
    {"action": "create_directory", "params": {"path": "feature"}},
    {"action": "create_file", "params": {"path": "feature/main.py"}},
    {"action": "bash_command", "params": {"command": "pytest"}}
  ]
}

Be thorough, be atomic, be precise. Bad planning wastes everyone's time.
"""


class PlannerAgent(BaseAgent):
    """
    Project Manager agent that generates atomic execution plans.
    
    Capabilities: DESIGN only
    Input: Architect's approved architecture + Explorer's context
    Output: Step-by-step execution plan with risk assessment
    """

    def __init__(self, llm_client: Any, mcp_client: Any) -> None:
        """Initialize Planner with DESIGN capability."""
        super().__init__(
            role=AgentRole.PLANNER,
            capabilities=[AgentCapability.DESIGN],
            llm_client=llm_client,
            mcp_client=mcp_client,
            system_prompt=PLANNER_SYSTEM_PROMPT,
        )

    async def execute(self, task: AgentTask) -> AgentResponse:
        """
        Generate atomic execution plan from architecture.
        
        Args:
            task: Contains architecture (from Architect) and context (from Explorer)
        
        Returns:
            AgentResponse with execution plan or error
        """
        try:
            # Build prompt with architecture and context
            prompt = self._build_planning_prompt(task)

            # Generate plan with LLM
            llm_response = await self._call_llm(prompt)

            # Parse and validate plan
            plan = self._parse_execution_plan(llm_response)

            if not plan:
                # Fallback: extract plan from text
                plan = self._extract_plan_fallback(llm_response)

            if not plan or not self._validate_plan(plan):
                return AgentResponse(
                    success=False,
                    data={},
                    reasoning="Failed to generate valid execution plan",
                    error="Invalid plan format or missing required fields",
                )

            # Calculate metadata
            total_steps = len(plan.get("steps", []))
            high_risk_count = sum(
                1 for step in plan.get("steps", [])
                if step.get("risk") == "HIGH"
            )
            requires_approval_count = sum(
                1 for step in plan.get("steps", [])
                if step.get("requires_approval", False)
            )

            return AgentResponse(
                success=True,
                data=plan,
                reasoning=f"Generated {total_steps}-step execution plan. "
                          f"{high_risk_count} high-risk operations, "
                          f"{requires_approval_count} require approval.",
                metadata={
                    "total_steps": total_steps,
                    "high_risk_count": high_risk_count,
                    "requires_approval_count": requires_approval_count,
                    "estimated_duration": plan.get("estimated_duration", "Unknown"),
                },
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                data={},
                reasoning=f"Planner execution failed: {str(e)}",
                error=str(e),
            )

    def _build_planning_prompt(self, task: AgentTask) -> str:
        """Build prompt with architecture and context."""
        prompt = f"USER REQUEST: {task.request}\n\n"

        # Include Architect's architecture if available
        if task.context and "architecture" in task.context:
            arch = task.context["architecture"]
            prompt += "APPROVED ARCHITECTURE:\n"
            prompt += f"Approach: {arch.get('approach', 'Not specified')}\n"
            if arch.get("risks"):
                prompt += f"Risks: {', '.join(arch['risks'])}\n"
            if arch.get("constraints"):
                prompt += f"Constraints: {', '.join(arch['constraints'])}\n"
            prompt += "\n"

        # Include Explorer's context if available
        if task.context and "relevant_files" in task.context:
            files = task.context["relevant_files"]
            prompt += f"RELEVANT FILES ({len(files)}):\n"
            # Show first 10 files only
            for f in files[:10]:
                path = f if isinstance(f, str) else f.get("path", "unknown")
                prompt += f"  - {path}\n"
            if len(files) > 10:
                prompt += f"  ... and {len(files) - 10} more\n"
            prompt += "\n"

        # Include existing constraints from context
        if task.context and "constraints" in task.context:
            constraints = task.context["constraints"]
            if isinstance(constraints, list):
                prompt += f"CONSTRAINTS: {', '.join(constraints)}\n\n"
            elif isinstance(constraints, str):
                prompt += f"CONSTRAINTS: {constraints}\n\n"

        prompt += "Generate a detailed, atomic execution plan following the format specified in your system prompt."

        return prompt

    def _parse_execution_plan(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response into execution plan."""
        try:
            # Try JSON parsing
            plan = json.loads(llm_response)

            # Validate required fields
            if not isinstance(plan, dict):
                return None

            # Must have steps array
            if "steps" not in plan or not isinstance(plan["steps"], list):
                return None

            return plan

        except json.JSONDecodeError:
            return None

    def _extract_plan_fallback(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract plan from non-JSON text (fallback).
        
        Looks for step patterns like:
        - "Step 1: Create directory..."
        - "1. Create app/auth"
        """
        steps = []
        lines = text.split("\n")

        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # Detect step patterns
            if any(pattern in line_lower for pattern in ["step ", "1.", "2.", "3.", "- "]):
                # Determine action type
                action = "bash_command"  # Default
                if "create" in line_lower and ("dir" in line_lower or "folder" in line_lower):
                    action = "create_directory"
                elif "create" in line_lower and "file" in line_lower:
                    action = "create_file"
                elif "edit" in line_lower or "modify" in line_lower:
                    action = "edit_file"
                elif "delete" in line_lower or "remove" in line_lower:
                    action = "delete_file"

                # Determine risk
                risk = "MEDIUM"  # Default
                if action in ["create_directory", "create_file", "bash_command"]:
                    risk = "LOW"
                elif action in ["delete_file"]:
                    risk = "HIGH"

                steps.append({
                    "id": len(steps) + 1,
                    "action": action,
                    "description": line.strip(),
                    "params": {},
                    "risk": risk,
                    "requires_approval": (risk == "HIGH"),
                    "dependencies": [],
                    "validation": "Manual verification required"
                })

        if not steps:
            return None

        return {
            "plan_name": "Extracted Plan",
            "total_steps": len(steps),
            "estimated_duration": f"{len(steps) * 5} minutes",
            "steps": steps,
            "checkpoints": [],
            "rollback_strategy": "Manual rollback if issues occur"
        }

    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate plan structure and content."""
        # Must have steps
        if not plan.get("steps"):
            return False

        # Each step must have required fields
        for step in plan["steps"]:
            if not all(key in step for key in ["id", "action", "risk"]):
                return False

            # Risk must be valid
            if step["risk"] not in ["LOW", "MEDIUM", "HIGH"]:
                return False

            # High risk must require approval
            if step["risk"] == "HIGH" and not step.get("requires_approval", False):
                # Auto-correct
                step["requires_approval"] = True

        return True
