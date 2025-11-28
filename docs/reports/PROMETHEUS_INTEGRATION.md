# PROMETHEUS Integration Documentation

> **Blaxel MCP Hackathon - November 2025**
>
> Self-Evolving Meta-Agent integrated into qwen-dev-cli ecosystem

---

## Quick Start

### 1. Deploy to Blaxel

```bash
cd prometheus/
bl deploy
```

**URL:** https://app.blaxel.ai/juancs-dev/global-agentic-network/agent/prometheus

### 2. Run via CLI

```bash
# Direct execution
bl run agent prometheus --data '{"inputs": "Your task here"}'

# Via qwen-dev-cli (auto-detect mode)
jdev "Implement a binary search algorithm"
```

### 3. Test Integration

```bash
# Quick E2E test
python tests/prometheus/test_e2e_quick.py

# Full validation
python tests/prometheus/validate_integration.py

# Stress test (30 requests)
python tests/prometheus/stress_test.py
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AUTO-DETECT LAYER                          │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ Simple Tasks    │    │ Complex Tasks                     │   │
│  │ (questions,     │───▶│ (multi-step, code, simulation)   │   │
│  │  greetings)     │    │                                   │   │
│  └────────┬────────┘    └────────────────┬─────────────────┘   │
│           │                               │                     │
│           ▼                               ▼                     │
│    ┌──────────────┐              ┌────────────────────┐        │
│    │   GEMINI     │              │    PROMETHEUS      │        │
│    │   (Fast)     │              │  (Self-Evolving)   │        │
│    └──────────────┘              └────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROMETHEUS PIPELINE                          │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ MEMORY   │──▶│  WORLD   │──▶│ EXECUTE  │──▶│ REFLECT  │    │
│  │ (MIRIX)  │   │  MODEL   │   │  TASK    │   │ & LEARN  │    │
│  │          │   │ (SimuRA) │   │          │   │          │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    │    EVOLUTION      │                        │
│                    │    (Agent0)       │                        │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. PROMETHEUS Core (`prometheus/`)

| Component | File | Description |
|-----------|------|-------------|
| **Main Agent** | `prometheus/main.py` | Blaxel-deployable agent |
| **Orchestrator** | `prometheus/core/orchestrator.py` | Central coordinator |
| **Memory (MIRIX)** | `prometheus/memory/memory_system.py` | 6-type persistent memory |
| **World Model (SimuRA)** | `prometheus/core/world_model.py` | Action simulation |
| **Reflection** | `prometheus/core/reflection.py` | Self-critique engine |
| **Evolution (Agent0)** | `prometheus/core/evolution.py` | Self-improvement |
| **Tool Factory** | `prometheus/tools/tool_factory.py` | Dynamic tool creation |

### 2. Integration Layer

| Component | File | Description |
|-----------|------|-------------|
| **Provider** | `jdev_cli/core/providers/prometheus_provider.py` | LLM provider interface |
| **Client** | `jdev_tui/core/prometheus_client.py` | TUI streaming client |
| **Tools** | `jdev_cli/tools/prometheus_tools.py` | 8 MCP tools |

### 3. UI Integration

| Component | File | Description |
|-----------|------|-------------|
| **Bridge** | `jdev_tui/core/bridge.py` | Auto-detect routing |
| **Gradio Bridge** | `gradio_ui/prometheus_bridge.py` | Gradio streaming |
| **Dashboard** | `gradio_ui/prometheus_components.py` | UI components |

---

## MCP Tools (8 Tools)

| Tool | Description |
|------|-------------|
| `prometheus_execute` | Execute task with full PROMETHEUS pipeline |
| `prometheus_memory_query` | Query 6-type memory system |
| `prometheus_simulate` | Simulate action via world model |
| `prometheus_evolve` | Run self-evolution cycle |
| `prometheus_reflect` | Trigger reflection on action |
| `prometheus_create_tool` | Generate new tool dynamically |
| `prometheus_get_status` | Get full system status |
| `prometheus_benchmark` | Run capability benchmark |

---

## User Preferences

| Feature | Setting | Description |
|---------|---------|-------------|
| **CLI Mode** | `Auto-detect` | Automatically routes simple→Gemini, complex→PROMETHEUS |
| **Gradio UI** | `Dashboard` | Full panels for Memory, World Model, Evolution |
| **MCP Tools** | `Expanded (8+)` | All 8 tools registered |

---

## Test Results

### Stress Test (30 requests)

| Metric | Value |
|--------|-------|
| Total Requests | 30 |
| Success Rate | **100%** |
| Avg Response Time | 23.69s |
| Duration | 2.5 min |

### Categories Tested

| Category | Success |
|----------|---------|
| Tool Factory | 6/6 (100%) |
| Sandbox | 4/4 (100%) |
| World Model | 3/3 (100%) |
| Reasoning | 2/2 (100%) |
| Memory | 3/3 (100%) |
| Reflection | 2/2 (100%) |
| Evolution | 3/3 (100%) |
| Integration | 5/5 (100%) |
| Benchmark | 2/2 (100%) |

---

## Running the Demo

### Option 1: Blaxel Direct

```bash
bl run agent prometheus --data '{"inputs": "Write a Python function to check if a number is prime"}'
```

### Option 2: Local Shell (Auto-detect)

```bash
# Start the shell
python -m jdev_cli

# Type your request (auto-routes to PROMETHEUS for complex tasks)
> Implement a recursive factorial function with memoization
```

### Option 3: Gradio UI

```bash
python -m gradio_ui
# Open http://localhost:7860
# Toggle PROMETHEUS in the dashboard
```

---

## Research References

PROMETHEUS implements cutting-edge AI research from November 2025:

| Paper | ArXiv | Capability |
|-------|-------|------------|
| Agent0 | 2511.16043 | Self-Evolution |
| SimuRA | 2507.23773 | World Model Simulation |
| MIRIX | 2507.07957 | 6-Type Memory System |
| AutoTools | 2405.16533 | Dynamic Tool Creation |
| Reflexion | 2303.11366 | Self-Reflection |

---

## Files Structure

```
qwen-dev-cli/
├── prometheus/                          # PROMETHEUS Core
│   ├── main.py                         # Blaxel Agent
│   ├── core/
│   │   ├── orchestrator.py             # Central Coordinator
│   │   ├── world_model.py              # SimuRA
│   │   ├── reflection.py               # Reflexion
│   │   └── evolution.py                # Agent0
│   ├── memory/
│   │   └── memory_system.py            # MIRIX
│   └── tools/
│       └── tool_factory.py             # AutoTools
│
├── jdev_cli/                           # CLI Integration
│   ├── core/providers/
│   │   └── prometheus_provider.py      # LLM Provider
│   └── tools/
│       └── prometheus_tools.py         # 8 MCP Tools
│
├── jdev_tui/                           # TUI Integration
│   └── core/
│       ├── bridge.py                   # Auto-detect Routing
│       └── prometheus_client.py        # Streaming Client
│
├── gradio_ui/                          # Gradio Integration
│   ├── prometheus_bridge.py            # Streaming Bridge
│   └── prometheus_components.py        # Dashboard Components
│
└── tests/prometheus/                   # Tests
    ├── stress_test.py
    ├── test_e2e_quick.py
    └── validate_integration.py
```

---

## Contact

- **GitHub:** [JuanCS-Dev/qwen-dev-cli](https://github.com/JuanCS-Dev/qwen-dev-cli)
- **Hackathon:** Blaxel MCP Hackathon - November 2025

---

*Generated by PROMETHEUS Self-Evolving Meta-Agent*
