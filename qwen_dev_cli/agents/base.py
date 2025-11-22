"""
BaseAgent: Abstract foundation for all specialist agents.

This module defines the core abstractions that all DEVSQUAD agents inherit from.
It enforces capability boundaries, type safety, and provides integration with
the existing LLM and MCP infrastructure.

Architecture:
    BaseAgent (abstract)
        ├── _can_use_tool() - Capability validation
        ├── _call_llm() - LLM provider wrapper
        ├── _execute_tool() - MCP tool execution
        └── execute() - Abstract method (must implement)

Philosophy (Boris Cherny):
    "The type system is documentation that can't lie."
"""

import abc
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Role definitions for specialist agents.
    
    Each role has specific responsibilities and capability constraints.
    """

    ARCHITECT = "architect"  # Feasibility analysis, READ_ONLY
    EXPLORER = "explorer"  # Context navigation, READ_ONLY + search
    PLANNER = "planner"  # Execution planning, DESIGN only
    REFACTORER = "refactorer"  # Code execution, FULL ACCESS
    REVIEWER = "reviewer"  # Quality validation, READ_ONLY + GIT
    SECURITY = "security"  # Vulnerability scanning, READ_ONLY + BASH_EXEC
    PERFORMANCE = "performance"  # Performance analysis, READ_ONLY + BASH_EXEC


class AgentCapability(str, Enum):
    """Capabilities that agents can possess.
    
    Capabilities are enforced at tool execution time. An agent attempting
    to use a tool outside its capabilities will raise CapabilityViolationError.
    """

    READ_ONLY = "read_only"  # ls, cat, grep, find
    FILE_EDIT = "file_edit"  # write_file, edit_file, delete_file
    BASH_EXEC = "bash_exec"  # bash command execution
    GIT_OPS = "git_ops"  # git operations (diff, commit, push)
    DESIGN = "design"  # Planning only, no execution


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUCCESS = "success"
    FAILED = "failed"


class AgentTask(BaseModel):
    """Task definition passed to an agent.
    
    Attributes:
        task_id: Unique identifier (UUID)
        request: Human-readable task description
        context: Additional context (files, constraints, etc.)
        session_id: Session identifier for shared memory
        metadata: Arbitrary metadata dictionary
    """

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: str = Field(..., min_length=1, description="Task description")
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: str = Field(default="default", description="Session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}  # Immutable after creation


# Alias for Day 3 agent tests
class TaskContext(BaseModel):
    """Simplified task context for Day 3 agents (alias compatible with tests)."""
    task_id: str
    description: str
    working_dir: Any  # Path type
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}


class AgentResponse(BaseModel):
    """Response returned by an agent after execution.
    
    Attributes:
        success: Whether task completed successfully
        data: Result data (structure varies by agent)
        reasoning: Explanation of what the agent did and why
        error: Error message if success=False
        metadata: Execution metadata (timing, tokens, etc.)
    """

    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = Field(default="", description="Agent reasoning")
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Alias for Day 3 agent tests
class TaskResult(BaseModel):
    """Task result (alias compatible with tests)."""
    task_id: str
    status: "TaskStatus"
    output: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CapabilityViolationError(Exception):
    """Raised when agent attempts to use tool outside its capabilities."""

    pass


class BaseAgent(abc.ABC):
    """Abstract base class for all DEVSQUAD agents.
    
    Enforces:
        - Role-based capability constraints
        - Type-safe task/response protocol
        - Integration with existing LLM/MCP infrastructure
        - Explicit error handling
    
    Usage:
        class MyAgent(BaseAgent):
            def __init__(self, llm_client, mcp_client):
                super().__init__(
                    role=AgentRole.ARCHITECT,
                    capabilities=[AgentCapability.READ_ONLY],
                    llm_client=llm_client,
                    mcp_client=mcp_client
                )
            
            async def execute(self, task: AgentTask) -> AgentResponse:
                # Implementation here
                pass
    """

    def __init__(
        self,
        role: AgentRole,
        capabilities: List[AgentCapability],
        llm_client: Any,  # LLMClient from core.llm
        mcp_client: Any,  # MCPClient from core.mcp
        system_prompt: str = "",
    ) -> None:
        """Initialize base agent.
        
        Args:
            role: Agent's role (from AgentRole enum)
            capabilities: List of capabilities this agent possesses
            llm_client: Instance of LLMClient for LLM calls
            mcp_client: Instance of MCPClient for tool execution
            system_prompt: Agent-specific system prompt
        """
        self.role = role
        self.capabilities = capabilities
        self.llm_client = llm_client
        self.mcp_client = mcp_client
        self.system_prompt = system_prompt
        self.execution_count = 0

    @abc.abstractmethod
    async def execute(self, task: AgentTask) -> AgentResponse:
        """Execute the given task.
        
        This is the main entry point for agent execution. Each specialist
        agent must implement this method according to its role.
        
        Args:
            task: Task definition with request and context
            
        Returns:
            AgentResponse with success status, data, and reasoning
            
        Raises:
            CapabilityViolationError: If agent attempts disallowed operation
        """
        raise NotImplementedError("Subclass must implement execute()")

    def _can_use_tool(self, tool_name: str) -> bool:
        """Validate if agent has capability to use the specified tool.
        
        Tool to capability mapping:
            - read_file, list_files, grep_search -> READ_ONLY
            - write_file, edit_file, delete_file -> FILE_EDIT
            - bash_command -> BASH_EXEC
            - git_diff, git_commit, git_push -> GIT_OPS
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            True if agent can use this tool, False otherwise
        """
        tool_capability_map = {
            # READ_ONLY tools
            "read_file": AgentCapability.READ_ONLY,
            "list_files": AgentCapability.READ_ONLY,
            "grep_search": AgentCapability.READ_ONLY,
            "find_files": AgentCapability.READ_ONLY,
            # FILE_EDIT tools
            "write_file": AgentCapability.FILE_EDIT,
            "edit_file": AgentCapability.FILE_EDIT,
            "delete_file": AgentCapability.FILE_EDIT,
            "create_directory": AgentCapability.FILE_EDIT,
            # BASH_EXEC tools
            "bash_command": AgentCapability.BASH_EXEC,
            "exec_command": AgentCapability.BASH_EXEC,
            # GIT_OPS tools
            "git_diff": AgentCapability.GIT_OPS,
            "git_commit": AgentCapability.GIT_OPS,
            "git_push": AgentCapability.GIT_OPS,
            "git_status": AgentCapability.GIT_OPS,
        }

        required_capability = tool_capability_map.get(tool_name)
        if required_capability is None:
            return False

        return required_capability in self.capabilities

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Call LLM with agent-specific system prompt.
        
        Wraps the existing LLMClient to inject agent-specific system prompts
        and handle errors consistently.
        
        Args:
            prompt: User prompt/task description
            system_prompt: Override system prompt (uses self.system_prompt if None)
            **kwargs: Additional arguments to pass to LLMClient
            
        Returns:
            LLM response text
            
        Raises:
            Exception: If LLM call fails (propagates from LLMClient)
        """
        final_system_prompt = system_prompt or self.system_prompt

        # Use existing LLMClient interface
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=final_system_prompt,
            **kwargs,
        )

        self.execution_count += 1
        return cast(str, response)

    async def _execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute MCP tool with capability enforcement.
        
        Validates that agent has capability to use the tool before execution.
        Uses existing MCPClient infrastructure.
        
        Args:
            tool_name: Name of the MCP tool to execute
            parameters: Tool parameters dictionary
            
        Returns:
            Tool execution result
            
        Raises:
            CapabilityViolationError: If agent lacks capability for this tool
            Exception: If tool execution fails (propagates from MCPClient)
        """
        if not self._can_use_tool(tool_name):
            raise CapabilityViolationError(
                f"Agent {self.role.value} cannot use tool '{tool_name}'. "
                f"Required capability missing. Agent has: {self.capabilities}"
            )

        # Use existing MCPClient interface
        result = await self.mcp_client.call_tool(
            tool_name=tool_name,
            arguments=parameters,
        )

        return cast(Dict[str, Any], result)

    def __repr__(self) -> str:
        """String representation for debugging."""
        caps = ", ".join(c.value for c in self.capabilities)
        return (
            f"<{self.__class__.__name__} "
            f"role={self.role.value} "
            f"capabilities=[{caps}] "
            f"executions={self.execution_count}>"
        )
