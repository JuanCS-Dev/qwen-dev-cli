# PROMETHEUS Architecture Documentation

> Technical deep-dive into the Self-Evolving Meta-Agent architecture

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            PROMETHEUS                                     │
│                    Self-Evolving Meta-Agent                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     ORCHESTRATOR LAYER                              │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │              PrometheusOrchestrator                           │  │ │
│  │  │  - Coordinates all subsystems                                 │  │ │
│  │  │  - Manages execution flow                                     │  │ │
│  │  │  - Handles streaming responses                                │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│         ┌──────────────────────────┼──────────────────────────┐         │
│         │                          │                          │         │
│         ▼                          ▼                          ▼         │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐   │
│  │   MEMORY    │           │   WORLD     │           │ REFLECTION  │   │
│  │   SYSTEM    │           │   MODEL     │           │   ENGINE    │   │
│  │  (MIRIX)    │           │  (SimuRA)   │           │ (Reflexion) │   │
│  └─────────────┘           └─────────────┘           └─────────────┘   │
│         │                          │                          │         │
│         └──────────────────────────┼──────────────────────────┘         │
│                                    │                                     │
│                                    ▼                                     │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      EXECUTION LAYER                                │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │ │
│  │  │  Tool Factory  │  │   Sandbox      │  │   Evolution    │       │ │
│  │  │  (AutoTools)   │  │   Executor     │  │   (Agent0)     │       │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. PrometheusOrchestrator

**File:** `prometheus/core/orchestrator.py`

The central coordinator that manages all subsystems.

```python
class PrometheusOrchestrator:
    """
    Central orchestrator for PROMETHEUS agent.

    Coordinates:
    - Memory retrieval before task execution
    - World model simulation for planning
    - Task execution with tool calling
    - Reflection and learning after execution
    - Evolution cycles for self-improvement
    """

    def __init__(self, llm_client, agent_name):
        self.llm_client = llm_client
        self.memory = MemorySystem()
        self.world_model = WorldModel(llm_client)
        self.reflection = ReflectionEngine(llm_client)
        self.evolution = EvolutionEngine(llm_client)
        self.tool_factory = ToolFactory(llm_client)
```

**Execution Flow:**

```
execute(task) →
  1. Memory.get_context(task)        # Retrieve relevant memories
  2. WorldModel.simulate(task)       # Plan before acting
  3. LLM.generate(task + context)    # Execute with context
  4. Reflection.analyze(result)      # Learn from outcome
  5. Memory.store(experience)        # Persist learning
```

---

### 2. Memory System (MIRIX)

**File:** `prometheus/memory/memory_system.py`

6-type persistent memory system based on MIRIX research.

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEM (MIRIX)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   EPISODIC   │  │   SEMANTIC   │  │  PROCEDURAL  │      │
│  │              │  │              │  │              │      │
│  │ Past events  │  │ Facts &      │  │ Learned      │      │
│  │ & experiences│  │ knowledge    │  │ skills       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    CORE      │  │   RESOURCE   │  │    VAULT     │      │
│  │              │  │              │  │              │      │
│  │ Identity &   │  │ Available    │  │ Consolidated │      │
│  │ goals        │  │ tools/APIs   │  │ long-term    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Methods:**

```python
class MemorySystem:
    def get_context_for_task(self, task: str) -> Dict
    def store_episode(self, episode: Episode)
    def learn_fact(self, topic: str, content: str)
    def store_procedure(self, name: str, steps: List[str])
    def search_knowledge(self, query: str, top_k: int) -> List
    def consolidate_to_vault(self)  # Periodic consolidation
```

---

### 3. World Model (SimuRA)

**File:** `prometheus/core/world_model.py`

Simulates actions before execution to predict outcomes.

```
┌─────────────────────────────────────────────────────────────┐
│                   WORLD MODEL (SimuRA)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Input: "Delete all files in /tmp"                         │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              SIMULATION ENGINE                       │   │
│   │                                                      │   │
│   │  1. Parse action intent                             │   │
│   │  2. Predict state changes                           │   │
│   │  3. Identify risks/side effects                     │   │
│   │  4. Generate alternative approaches                  │   │
│   │  5. Score confidence                                │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Output:                                                    │
│   {                                                          │
│     "predicted_outcome": "All files deleted",               │
│     "risks": ["Data loss", "Permission errors"],            │
│     "confidence": 0.85,                                     │
│     "alternatives": ["Delete only *.tmp files"]             │
│   }                                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. Reflection Engine (Reflexion)

**File:** `prometheus/core/reflection.py`

Self-critique and improvement after task execution.

```python
class ReflectionEngine:
    """
    Implements Reflexion paper for self-improvement.

    After each task:
    1. Analyze what worked
    2. Identify mistakes
    3. Generate lessons learned
    4. Update memory with insights
    """

    async def reflect(self, task, outcome, context) -> Dict:
        # Generate self-critique
        critique = await self._generate_critique(task, outcome)

        # Extract lessons
        lessons = await self._extract_lessons(critique)

        # Score quality
        quality_score = await self._score_quality(outcome)

        return {
            "quality_score": quality_score,
            "improvements": critique["improvements"],
            "lessons_learned": lessons
        }
```

---

### 5. Evolution Engine (Agent0)

**File:** `prometheus/core/evolution.py`

Self-evolution through practice and frontier exploration.

```
┌─────────────────────────────────────────────────────────────┐
│                   EVOLUTION (Agent0)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   EVOLUTION CYCLE:                                          │
│                                                              │
│   1. GENERATE CHALLENGE                                     │
│      └─▶ Create task at frontier of capability              │
│                                                              │
│   2. ATTEMPT SOLUTION                                       │
│      └─▶ Try to solve with current abilities                │
│                                                              │
│   3. REFLECT ON RESULT                                      │
│      └─▶ Analyze success/failure                            │
│                                                              │
│   4. UPDATE CAPABILITIES                                    │
│      └─▶ Learn from experience                              │
│                                                              │
│   5. EXPAND FRONTIER                                        │
│      └─▶ Increase difficulty if successful                  │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Iteration 1: Basic math       ──▶ Success          │   │
│   │  Iteration 2: Algebra          ──▶ Success          │   │
│   │  Iteration 3: Calculus         ──▶ Partial          │   │
│   │  Iteration 4: Calculus (retry) ──▶ Success          │   │
│   │  Iteration 5: Differential eq. ──▶ In progress...   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 6. Tool Factory (AutoTools)

**File:** `prometheus/tools/tool_factory.py`

Dynamically creates new tools on-demand.

```python
class ToolFactory:
    """
    Creates tools dynamically based on task requirements.

    Example:
    - Task: "Parse this CSV and calculate statistics"
    - Factory creates: csv_parser_tool, stats_calculator_tool
    """

    async def create_tool(self, description: str, language: str = "python") -> Tool:
        # Generate tool code
        code = await self._generate_tool_code(description)

        # Validate in sandbox
        is_valid = await self._validate_in_sandbox(code)

        if is_valid:
            # Register tool
            tool = self._register_tool(code)
            return tool
```

---

## Integration Architecture

### Provider Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    PROVIDER LAYER                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PrometheusProvider                      │    │
│  │                                                      │    │
│  │  Implements LLM Provider interface:                  │    │
│  │  - stream(prompt, context) → AsyncIterator[str]     │    │
│  │  - generate(prompt) → str                           │    │
│  │  - evolve(iterations) → Dict                        │    │
│  │  - get_status() → Dict                              │    │
│  │                                                      │    │
│  │  Routes through PrometheusOrchestrator              │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PrometheusClient                        │    │
│  │                                                      │    │
│  │  TUI-specific client with:                          │    │
│  │  - Streaming support                                │    │
│  │  - Timeout handling                                 │    │
│  │  - Health metrics                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Auto-Detect Routing

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTO-DETECT LAYER                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Message: "Implement a recursive Fibonacci function"   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           _detect_task_complexity()                  │    │
│  │                                                      │    │
│  │  Patterns checked:                                   │    │
│  │  - Multi-step tasks ✓                               │    │
│  │  - Code generation ✓                                │    │
│  │  - Memory-dependent ✗                               │    │
│  │  - Simulation needed ✗                              │    │
│  │                                                      │    │
│  │  Complexity score: 2                                │    │
│  │  Threshold: 2                                       │    │
│  │  Result: PROMETHEUS                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│              Route to PrometheusClient                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Complete Request Flow

```
┌──────┐    ┌────────┐    ┌──────────┐    ┌────────────┐
│ User │───▶│ Bridge │───▶│ Provider │───▶│Orchestrator│
└──────┘    └────────┘    └──────────┘    └────────────┘
                                                │
                                                ▼
                          ┌─────────────────────────────────┐
                          │         PROMETHEUS PIPELINE      │
                          │                                  │
                          │  1. Memory.get_context()        │
                          │          ↓                       │
                          │  2. WorldModel.simulate()       │
                          │          ↓                       │
                          │  3. LLM.generate()              │
                          │          ↓                       │
                          │  4. Reflection.analyze()        │
                          │          ↓                       │
                          │  5. Memory.store()              │
                          └─────────────────────────────────┘
                                                │
                                                ▼
┌──────┐    ┌────────┐    ┌──────────┐    ┌────────────┐
│ User │◀───│   UI   │◀───│ Provider │◀───│  Response  │
└──────┘    └────────┘    └──────────┘    └────────────┘
```

---

## Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_api_key
# or
GEMINI_API_KEY=your_api_key

# Optional
JDEV_PROVIDER=auto  # auto, prometheus, gemini
PROMETHEUS_ENABLE_EVOLUTION=false
PROMETHEUS_MEMORY_CONSOLIDATION_INTERVAL=10
```

### PrometheusConfig

```python
@dataclass
class PrometheusConfig:
    enable_world_model: bool = True
    enable_memory: bool = True
    enable_reflection: bool = True
    enable_evolution: bool = False  # Expensive
    evolution_iterations: int = 5
    memory_consolidation_interval: int = 10
```

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Cold start | ~2-3s | First request initializes all systems |
| Warm request | ~8-15s | With memory + world model |
| Simple query | ~3-5s | Bypasses simulation |
| Evolution cycle | ~2-5 min | Per 5 iterations |
| Memory consolidation | ~30s | Background process |

---

## Research Papers

| Paper | ArXiv | Key Contribution |
|-------|-------|------------------|
| **Agent0** | 2511.16043 | Self-evolution through frontier exploration |
| **SimuRA** | 2507.23773 | World model for action simulation (+124% task completion) |
| **MIRIX** | 2507.07957 | 6-type memory architecture |
| **AutoTools** | 2405.16533 | Dynamic tool creation |
| **Reflexion** | 2303.11366 | Self-reflection for improvement |

---

*PROMETHEUS Architecture Documentation - Blaxel MCP Hackathon November 2025*
