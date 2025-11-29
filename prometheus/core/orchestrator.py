"""
Prometheus Orchestrator - Lead Agent.

Coordinates all subsystems:
- Memory System (MIRIX)
- World Model (SimuRA)
- Tool Factory (AutoTools)
- Reflection Engine (Reflexion)
- Co-Evolution Loop (Agent0)

Based on the Orchestrator-Worker pattern from Anthropic:
https://www.anthropic.com/engineering/multi-agent-research-system
"""

from dataclasses import dataclass, field
from typing import AsyncIterator, List, Dict, Optional, Any
from datetime import datetime
import os

from .llm_client import GeminiClient
from .world_model import WorldModel, ActionType, WorldState
from .reflection import ReflectionEngine
from .evolution import CoEvolutionLoop
from ..memory.memory_system import MemorySystem
from ..tools.tool_factory import ToolFactory
from ..sandbox.executor import SandboxExecutor


@dataclass
class ExecutionContext:
    """Context for task execution."""
    task: str
    memory_context: Dict[str, Any]
    world_state: WorldState
    available_tools: List[Dict[str, Any]]
    constraints: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Result of orchestrated execution."""
    task: str
    output: str
    success: bool
    score: float
    actions_taken: List[str]
    tools_used: List[str]
    reflection_score: float
    execution_time: float
    lessons_learned: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task": self.task[:100],
            "success": self.success,
            "score": self.score,
            "actions": len(self.actions_taken),
            "tools_used": self.tools_used,
            "reflection_score": self.reflection_score,
            "execution_time": self.execution_time,
        }


class PrometheusOrchestrator:
    """
    Main Orchestrator for PROMETHEUS.

    Coordinates all subsystems to execute complex tasks
    autonomously with self-improvement capabilities.

    Pipeline:
    1. Memory retrieval for context
    2. World model simulation for planning
    3. Tool execution (with auto-generation)
    4. Reflection and learning
    5. Evolution for continuous improvement
    """

    def __init__(
        self,
        llm_client: Optional[GeminiClient] = None,
        agent_name: str = "Prometheus",
    ):
        # Core LLM client
        self.llm = llm_client or GeminiClient()
        self.agent_name = agent_name

        # Initialize all subsystems
        self.memory = MemorySystem(agent_name=agent_name)
        self.sandbox = SandboxExecutor()
        self.tools = ToolFactory(self.llm, self.sandbox)
        self.world_model = WorldModel(self.llm)
        self.reflection = ReflectionEngine(self.llm, self.memory)
        self.evolution = CoEvolutionLoop(
            self.llm,
            self.tools,
            self.memory,
            self.reflection,
            self.sandbox,
        )

        # Register builtin tools
        self._register_builtin_tools()

        # Execution history
        self.execution_history: List[ExecutionResult] = []

        # State
        self._is_executing = False

    def _register_builtin_tools(self):
        """Register built-in tools."""
        # File operations
        self.tools.register_builtin("read_file", self._tool_read_file)
        self.tools.register_builtin("write_file", self._tool_write_file)
        self.tools.register_builtin("list_files", self._tool_list_files)

        # Code execution
        self.tools.register_builtin("execute_python", self._tool_execute_python)

        # Search and analysis
        self.tools.register_builtin("search_code", self._tool_search_code)
        self.tools.register_builtin("analyze_code", self._tool_analyze_code)

        # Memory operations
        self.tools.register_builtin("remember", self._tool_remember)
        self.tools.register_builtin("recall", self._tool_recall)

    async def execute(
        self,
        task: str,
        stream: bool = True,
        fast_mode: bool = True,  # Default to FAST mode
    ) -> AsyncIterator[str]:
        """
        Execute a task with orchestration.

        Args:
            task: The task to execute
            stream: Whether to stream output
            fast_mode: Skip memory/reflection for speed (default: True)
        """
        self._is_executing = True
        start_time = datetime.now()

        try:
            yield "🔥 **PROMETHEUS** executing...\n\n"

            # FAST MODE: Go directly to execution
            if fast_mode:
                execution_output = await self._execute_task_with_context(
                    task,
                    {},  # No memory context
                    None,  # No plan
                )
                yield execution_output

                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                yield f"\n\n✅ Done in {execution_time:.1f}s\n"
            else:
                # FULL MODE: All the bells and whistles
                yield "📚 Retrieving context...\n"
                memory_context = self.memory.get_context_for_task(task)

                yield "🌍 Planning approach...\n"
                plans = await self.world_model.find_best_plan(
                    goal=task,
                    available_actions=[
                        ActionType.THINK,
                        ActionType.READ_FILE,
                        ActionType.WRITE_FILE,
                        ActionType.EXECUTE_CODE,
                        ActionType.USE_TOOL,
                    ],
                    max_steps=5,
                    num_candidates=2,
                )

                yield "⚡ Executing...\n"
                execution_output = await self._execute_task_with_context(
                    task,
                    memory_context,
                    plans[0] if plans else None,
                )
                yield f"\n{execution_output}\n"

                yield "🪞 Reflecting...\n"
                reflection_result = await self.reflection.critique_action(
                    action=f"Task: {task[:100]}",
                    result=execution_output[:500],
                    context={},
                )

                self.memory.remember_experience(
                    experience=f"Task: {task[:200]}",
                    outcome=f"Result: {execution_output[:200]}",
                    context={"score": reflection_result.score},
                    importance=reflection_result.score,
                )

                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                yield f"\n✅ Done in {execution_time:.1f}s (score: {reflection_result.score:.0%})\n"

        except Exception as e:
            yield f"\n❌ Error: {str(e)}\n"
            raise
        finally:
            self._is_executing = False

    async def execute_simple(self, task: str) -> str:
        """
        Execute a task and return only the final output.

        Simpler interface without streaming.
        """
        output_parts = []

        async for chunk in self.execute(task, stream=True):
            output_parts.append(chunk)

        return "".join(output_parts)

    async def _execute_task_with_context(
        self,
        task: str,
        context: Dict[str, Any],
        plan: Optional[Any] = None,
    ) -> str:
        """Execute the main task with all context."""
        import re

        # Check if task contains a plan with code blocks - DIRECT EXTRACTION MODE
        has_code_blocks = "```" in task
        has_file_refs = any(x in task for x in [".py", "requirements", "Dockerfile", ".yaml", ".json", ".toml"])

        if has_code_blocks and has_file_refs:
            # OPTIMIZED: Direct extraction and file creation - no LLM call needed!
            return await self._direct_plan_execution(task)

        # Standard execution path for non-plan tasks
        context_section = self._format_context(context)
        plan_section = self._format_plan(plan) if plan else ""

        tools_list = self.tools.list_tools()
        tools_section = "\n".join(
            f"- {t['name']}: {t.get('description', 'No description')[:60]}"
            for t in tools_list[:15]
        )

        prompt = f"""You are PROMETHEUS. Execute this task using tools.

TASK: {task}

CONTEXT:
{context_section}

{plan_section}

TOOLS: {tools_section}

Use [TOOL:name:args] format. Example: [TOOL:write_file:path=x.py,content=code]"""

        response = await self.llm.generate(prompt)
        response = await self._execute_inline_tools(response)
        return response

    async def _direct_plan_execution(self, task: str) -> str:
        """
        OPTIMIZED: Extract files directly from plan and create them.
        No additional LLM call - parse the plan text directly.
        """
        import re

        results = []

        # Step 1: Find project directory (e.g., neuro_api, my_project)
        dir_patterns = [
            r'mkdir\s+(\w+)',
            r'cd\s+(\w+)',
            r'directory[:\s]+[`\'"]*(\w+)[`\'"]*',
            r'project[:\s]+[`\'"]*(\w+)[`\'"]*',
            r'called\s+[`\'"]*(\w+)[`\'"]*',
        ]
        project_dir = None
        for pattern in dir_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                if candidate not in ['python', 'pip', 'source', 'venv', 'app']:
                    project_dir = candidate
                    break

        # Create project directory
        if project_dir:
            os.makedirs(project_dir, exist_ok=True)
            results.append(f"📁 Created: {project_dir}/")

        # Step 2: Extract ALL code blocks with file associations
        # Pattern: filename followed by code block (various formats)
        file_patterns = [
            # `filename.py`: ```python
            r'[`\'"]+([a-zA-Z_][\w/\-\.]*\.(?:py|txt|md|yaml|yml|json|toml|dockerfile|cfg|ini))[`\'"]*[:\s]*\n*```[\w]*\n(.*?)```',
            # **filename.py** or filename.py:
            r'\*?\*?([a-zA-Z_][\w/\-\.]*\.(?:py|txt|md|yaml|yml|json|toml|dockerfile|cfg|ini))\*?\*?[:\s]*\n*```[\w]*\n(.*?)```',
            # Create filename.py or File: filename.py
            r'(?:Create|File|create|file)[:\s]+[`\'"]*([a-zA-Z_][\w/\-\.]*\.(?:py|txt|md|yaml|yml|json|toml))[`\'"]*[:\s]*\n*```[\w]*\n(.*?)```',
        ]

        created_files = set()
        for pattern in file_patterns:
            for match in re.finditer(pattern, task, re.DOTALL | re.IGNORECASE):
                filename = match.group(1).strip('`\'"* ')
                content = match.group(2).strip()

                if not content or len(content) < 5:
                    continue
                if filename in created_files:
                    continue

                # Determine full path
                if project_dir and not filename.startswith(project_dir):
                    # Check if it's a nested file like utils/ml_utils.py
                    if '/' in filename:
                        full_path = os.path.join(project_dir, filename)
                    else:
                        full_path = os.path.join(project_dir, filename)
                else:
                    full_path = filename

                # Create parent directories
                parent = os.path.dirname(full_path)
                if parent:
                    os.makedirs(parent, exist_ok=True)

                # Write file
                try:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    results.append(f"✅ Created: {full_path} ({len(content)} bytes)")
                    created_files.add(filename)
                except Exception as e:
                    results.append(f"❌ Failed: {full_path} - {e}")

        # Step 3: Also check for requirements.txt or Dockerfile specifically
        special_files = {
            'requirements.txt': r'requirements\.txt[`\'":\s]*\n*```[^\n]*\n(.*?)```',
            'Dockerfile': r'Dockerfile[`\'":\s]*\n*```[^\n]*\n(.*?)```',
            '.env': r'\.env[`\'":\s]*\n*```[^\n]*\n(.*?)```',
        }

        for filename, pattern in special_files.items():
            if filename in created_files:
                continue
            match = re.search(pattern, task, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content and len(content) > 3:
                    full_path = os.path.join(project_dir, filename) if project_dir else filename
                    try:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        results.append(f"✅ Created: {full_path}")
                        created_files.add(filename)
                    except Exception as e:
                        results.append(f"❌ Failed: {full_path} - {e}")

        if results:
            return "**Direct Plan Execution Results:**\n" + "\n".join(results)
        else:
            return "No files extracted from plan. Check code block formatting."

    async def _execute_inline_tools(self, response: str) -> str:
        """Parse and execute inline tool calls from response."""
        import re

        executed_results = []

        # Pattern 1: [TOOL:tool_name:args]
        tool_pattern = r'\[TOOL:(\w+):([^\]]+)\]'
        for match in re.finditer(tool_pattern, response):
            tool_name = match.group(1)
            args_str = match.group(2)
            args = {}
            for pair in args_str.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    args[key.strip()] = value.strip()
            result = await self._execute_tool(tool_name, args)
            executed_results.append(f"✅ {tool_name}: {result[:100]}")

        # Pattern 2: mkdir("path") or mkdir('path')
        mkdir_pattern = r'mkdir\(["\']([^"\']+)["\']\)'
        for match in re.finditer(mkdir_pattern, response):
            path = match.group(1)
            result = await self._execute_tool("mkdir", {"path": path})
            executed_results.append(f"✅ mkdir: {result[:100]}")

        # Pattern 3: write_file("path", "content") - basic version
        write_pattern = r'write_file\(["\']([^"\']+)["\'],\s*["\']([^"\']*)["\']'
        for match in re.finditer(write_pattern, response):
            path = match.group(1)
            content = match.group(2)
            result = await self._execute_tool("write_file", {"path": path, "content": content})
            executed_results.append(f"✅ write_file: {result[:100]}")

        # Pattern 4: Extract code blocks and create files from plan context
        # Look for file paths followed by code blocks
        file_code_pattern = r'(?:Create|create|File:|file:)\s*[`\'"]*([a-zA-Z_][a-zA-Z0-9_/\.]*\.(?:py|txt|md|yaml|yml|json|toml))[`\'"]*\s*[:]*\s*```[\w]*\n(.*?)```'
        for match in re.finditer(file_code_pattern, response, re.DOTALL):
            path = match.group(1)
            content = match.group(2).strip()
            if content and len(content) > 10:  # Meaningful content
                result = await self._execute_tool("write_file", {"path": path, "content": content})
                executed_results.append(f"✅ write_file({path}): {result[:60]}")

        if executed_results:
            return response + "\n\n---\n**Tool Execution Results:**\n" + "\n".join(executed_results)

        return response

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a single tool by name."""
        try:
            if tool_name == "write_file":
                path = args.get("path", "")
                content = args.get("content", "")
                return await self._tool_write_file(path, content)

            elif tool_name == "mkdir":
                path = args.get("path", "")
                os.makedirs(path, exist_ok=True)
                return f"Created directory: {path}"

            elif tool_name == "read_file":
                path = args.get("path", "")
                return await self._tool_read_file(path)

            elif tool_name == "list_files":
                directory = args.get("path", ".")
                return await self._tool_list_files(directory)

            elif tool_name == "execute_python":
                code = args.get("code", "")
                return await self._tool_execute_python(code)

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format memory context for prompt."""
        sections = []

        if context.get("relevant_experiences"):
            exp_text = "\n".join(
                f"  - {e.get('content', '')[:80]}"
                for e in context["relevant_experiences"][:3]
            )
            sections.append(f"Past Experiences:\n{exp_text}")

        if context.get("relevant_knowledge"):
            know_text = "\n".join(
                f"  - [{k.get('topic', '')}]: {k.get('content', '')[:60]}"
                for k in context["relevant_knowledge"][:3]
            )
            sections.append(f"Relevant Knowledge:\n{know_text}")

        if context.get("relevant_procedures"):
            proc_text = "\n".join(
                f"  - {p.get('skill', '')}: {p.get('steps', [])[:2]}"
                for p in context["relevant_procedures"][:3]
            )
            sections.append(f"Known Procedures:\n{proc_text}")

        return "\n\n".join(sections) if sections else "No specific context retrieved."

    def _format_plan(self, plan: Any) -> str:
        """Format plan for prompt."""
        if not plan or not hasattr(plan, 'actions_taken'):
            return ""

        steps = []
        for i, action in enumerate(plan.actions_taken[:5], 1):
            steps.append(f"  {i}. {action.action_type.value}: {action.predicted_outcome[:50]}")

        return f"""
RECOMMENDED APPROACH:
{chr(10).join(steps)}
(Success probability: {plan.overall_success_probability:.0%})
"""

    def _identify_needed_tools(self, task: str) -> List[str]:
        """Identify tools that might be needed for the task."""
        needed = []
        task_lower = task.lower()

        tool_keywords = {
            "read_file": ["read", "file", "content", "load"],
            "write_file": ["write", "save", "create file", "output to"],
            "execute_python": ["run", "execute", "python", "code"],
            "search_code": ["search", "find", "grep", "locate"],
            "analyze_code": ["analyze", "review", "examine", "check"],
        }

        for tool_name, keywords in tool_keywords.items():
            if any(kw in task_lower for kw in keywords):
                needed.append(tool_name)

        return needed

    # =========================================================================
    # BUILTIN TOOLS
    # =========================================================================

    async def _tool_read_file(self, path: str) -> str:
        """Read file contents."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:10000]  # Limit size
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error reading file: {e}"

    async def _tool_write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    async def _tool_list_files(self, directory: str = ".", pattern: str = "*") -> str:
        """List files in directory."""
        import glob
        try:
            files = glob.glob(os.path.join(directory, pattern))
            return "\n".join(files[:50])
        except Exception as e:
            return f"Error listing files: {e}"

    async def _tool_execute_python(self, code: str) -> str:
        """Execute Python code in sandbox."""
        result = await self.sandbox.execute(code, timeout=30)
        if result.success:
            return result.stdout or "Code executed successfully (no output)"
        return f"Error: {result.stderr or result.error_message}"

    async def _tool_search_code(self, query: str, path: str = ".") -> str:
        """Search for code patterns."""
        # Simple grep-like search
        import subprocess
        try:
            result = subprocess.run(
                ["grep", "-r", "-n", query, path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout[:5000] or "No matches found"
        except Exception as e:
            return f"Search error: {e}"

    async def _tool_analyze_code(self, code: str) -> str:
        """Analyze code for issues."""
        prompt = f"""Analyze this code for potential issues:

```
{code}
```

Identify:
1. Bugs or errors
2. Performance issues
3. Security concerns
4. Style improvements

Be specific and actionable."""

        return await self.llm.generate(prompt)

    async def _tool_remember(self, key: str, value: str) -> str:
        """Store something in memory."""
        self.memory.learn_fact(key, value, source="tool_remember")
        return f"Remembered: {key}"

    async def _tool_recall(self, query: str) -> str:
        """Recall from memory."""
        results = self.memory.search_knowledge(query, top_k=5)
        if results:
            return "\n".join(
                f"- {r['topic']}: {r['content']}"
                for r in results
            )
        return "Nothing relevant found in memory"

    # =========================================================================
    # EVOLUTION & LEARNING
    # =========================================================================

    async def evolve_capabilities(
        self,
        iterations: int = 10,
        domain: str = "general",
    ) -> Dict[str, Any]:
        """
        Run evolution cycle to improve capabilities.

        Useful for "warming up" the agent before production use.
        """
        from ..agents.curriculum_agent import TaskDomain

        domain_enum = TaskDomain[domain.upper()] if domain.upper() in TaskDomain.__members__ else TaskDomain.GENERAL

        async for progress in self.evolution.evolve(
            num_iterations=iterations,
            domain=domain_enum,
            yield_progress=True,
        ):
            pass  # Consume generator

        return self.evolution.get_evolution_summary()

    async def benchmark_capabilities(self) -> Dict[str, Any]:
        """Run a benchmark of current capabilities."""
        return await self.evolution.benchmark(num_tasks_per_level=2)

    # =========================================================================
    # STATUS & EXPORT
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        return {
            "agent_name": self.agent_name,
            "is_executing": self._is_executing,
            "memory": self.memory.get_stats(),
            "tools": self.tools.get_stats(),
            "world_model": self.world_model.get_stats(),
            "reflection": self.reflection.get_learning_summary(),
            "evolution": self.evolution.get_evolution_summary() if self.evolution.evolution_history else {},
            "execution_history": len(self.execution_history),
        }

    def get_learning_report(self) -> Dict[str, Any]:
        """Get comprehensive learning report."""
        return {
            "memory_stats": self.memory.get_stats(),
            "skills_report": self.evolution.executor.get_skill_report() if hasattr(self.evolution, 'executor') else {},
            "reflection_summary": self.reflection.get_learning_summary(),
            "improvement_suggestions": self.reflection.get_improvement_suggestions(),
            "evolution_recommendations": self.evolution.get_recommendations(),
        }

    def export_state(self) -> Dict[str, Any]:
        """Export complete orchestrator state for persistence."""
        return {
            "agent_name": self.agent_name,
            "memory": self.memory.export_state(),
            "tools": self.tools.export_tools(),
            "evolution": self.evolution.export_state(),
            "reflections": self.reflection.export_reflections(),
            "execution_history": [r.to_dict() for r in self.execution_history[-100:]],
        }

    def import_state(self, state: Dict[str, Any]):
        """Import previously exported state."""
        if "agent_name" in state:
            self.agent_name = state["agent_name"]

        if "memory" in state:
            self.memory.import_state(state["memory"])

        if "tools" in state:
            self.tools.import_tools(state["tools"])

    @property
    def is_busy(self) -> bool:
        """Check if orchestrator is currently executing."""
        return self._is_executing
