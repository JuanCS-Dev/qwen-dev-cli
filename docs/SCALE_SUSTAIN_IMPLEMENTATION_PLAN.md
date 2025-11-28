# SCALE & SUSTAIN - Plano Cirúrgico de Implementação

**Sistema**: juan-dev-code
**Data**: 2025-11-26
**Autor**: JuanCS Dev
**Versão**: 1.0

---

## Sumário Executivo

Este plano detalha a estratégia cirúrgica para escalar o sistema juan-dev-code de **346K LOC** para suportar **10x crescimento** mantendo qualidade e manutenibilidade. Baseado em análise exaustiva de 277 arquivos, identificamos:

- **3 God Classes** requerendo decomposição imediata
- **16.43 CC** em shell_main.py (crítico, target <10)
- **10.9%** duplicação de código (8 tipos duplicados)
- **74 métodos** em Bridge (target: 35-40)

---

## FASE 1: ESTABILIZAÇÃO (Q4 2025 - 8 semanas)

### 1.1 Refatoração do Bridge (Semanas 1-3)

#### Diagnóstico
- **Localização**: `jdev_tui/core/bridge.py`
- **LOC**: 1,461
- **Métodos**: 74 (GOD CLASS)
- **Responsabilidades identificadas**: 17 grupos distintos

#### Extrações Cirúrgicas

**1.1.1 TodoManager** (4 métodos → classe dedicada)
```
Métodos a extrair:
- add_todo()
- complete_todo()
- get_todos()
- clear_todos()

Localização destino: jdev_tui/core/managers/todo_manager.py
Interface: ITodoManager
Impacto: -4 métodos do Bridge
```

**1.1.2 AuthenticationManager** (5 métodos → classe dedicada)
```
Métodos a extrair:
- login()
- logout()
- is_authenticated()
- get_auth_status()
- refresh_token()

Localização destino: jdev_tui/core/managers/auth_manager.py
Interface: IAuthManager
Impacto: -5 métodos do Bridge
```

**1.1.3 MemoryManager** (4 métodos → classe dedicada)
```
Métodos a extrair:
- remember()
- recall()
- forget()
- get_memory_stats()

Localização destino: jdev_tui/core/managers/memory_manager.py
Interface: IMemoryManager
Impacto: -4 métodos do Bridge
```

**1.1.4 ContextManager** (5 métodos → classe dedicada)
```
Métodos a extrair:
- add_context()
- clear_context()
- get_context()
- compact_context()
- get_context_stats()

Localização destino: jdev_tui/core/managers/context_manager.py
Interface: IContextManager
Impacto: -5 métodos do Bridge
```

**1.1.5 StatusManager** (2 métodos → classe dedicada)
```
Métodos a extrair:
- get_system_status()
- get_health_check()

Localização destino: jdev_tui/core/managers/status_manager.py
Interface: IStatusManager
Impacto: -2 métodos do Bridge
```

**1.1.6 PullRequestManager** (2 métodos → classe dedicada)
```
Métodos a extrair:
- create_pr()
- create_draft_pr()

Localização destino: jdev_tui/core/managers/pr_manager.py
Interface: IPullRequestManager
Impacto: -2 métodos do Bridge
```

#### Resultado Esperado
- **Bridge**: 74 → ~52 métodos (-30%)
- **Novas classes**: 6 managers especializados
- **Testabilidade**: Cada manager testável isoladamente
- **Padrão**: Facade mantido, delegação para managers

#### Ordem de Execução
1. Criar diretório `jdev_tui/core/managers/`
2. Criar interfaces em `jdev_tui/core/interfaces/`
3. Extrair TodoManager (menor, validar padrão)
4. Extrair StatusManager (simples)
5. Extrair PullRequestManager (simples)
6. Extrair MemoryManager (médio)
7. Extrair ContextManager (médio)
8. Extrair AuthenticationManager (complexo)
9. Atualizar Bridge para usar managers via composição
10. Mover testes existentes + criar novos

---

### 1.2 Redução de Complexidade Ciclomática (Semanas 4-5)

#### Diagnóstico
- **Localização**: `jdev_cli/shell_main.py`
- **LOC**: 2,514
- **CC atual**: 16.43 (crítico)
- **Hotspot**: `_handle_system_command()` - 677 linhas, CC ~45-50

#### Decomposição de `_handle_system_command()`

**1.2.1 CommandDispatcher** (Redução: -30 a -40 CC)
```python
# Estrutura proposta
class CommandDispatcher:
    """Dispatch commands to specialized handlers."""

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
        self._register_handlers()

    def _register_handlers(self):
        self._handlers = {
            '/help': HelpHandler(),
            '/clear': ClearHandler(),
            '/model': ModelHandler(),
            '/context': ContextHandler(),
            '/lsp': LSPHandler(),
            # ... 28 outros comandos
        }

    async def dispatch(self, command: str, args: str) -> CommandResult:
        handler = self._handlers.get(command)
        if handler:
            return await handler.execute(args)
        return CommandResult.unknown(command)

Localização: jdev_cli/handlers/command_dispatcher.py
```

**1.2.2 LSPCommandHandler** (Redução: -20 a -25 CC)
```python
# 6 handlers LSP × 5-6 CC cada = 30-36 CC total

class LSPCommandHandler:
    """Handle all LSP-related commands."""

    async def handle_completion(self, params) -> CompletionResult: ...
    async def handle_hover(self, params) -> HoverResult: ...
    async def handle_definition(self, params) -> DefinitionResult: ...
    async def handle_references(self, params) -> ReferencesResult: ...
    async def handle_diagnostics(self, params) -> DiagnosticsResult: ...
    async def handle_formatting(self, params) -> FormattingResult: ...

Localização: jdev_cli/handlers/lsp_handler.py
```

**1.2.3 ToolResultFormatter** (Redução: -10 a -12 CC)
```python
# Registry pattern para formatadores de resultado

class ToolResultFormatter:
    """Format tool results for display."""

    _formatters: Dict[str, Callable] = {
        'bash': format_bash_result,
        'read_file': format_file_content,
        'write_file': format_write_result,
        'glob': format_glob_result,
        'grep': format_grep_result,
        # ... outros formatadores
    }

    def format(self, tool_name: str, result: Any) -> str:
        formatter = self._formatters.get(tool_name, format_generic)
        return formatter(result)

Localização: jdev_cli/formatters/tool_formatter.py
```

**1.2.4 InputHandler** (Redução: -5 a -8 CC)
```python
class InputHandler:
    """Handle user input processing."""

    def parse_input(self, raw: str) -> ParsedInput: ...
    def validate_input(self, parsed: ParsedInput) -> ValidationResult: ...
    def preprocess_input(self, validated: ParsedInput) -> str: ...

Localização: jdev_cli/handlers/input_handler.py
```

#### Resultado Esperado
- **CC**: 16.43 → ~8-9 (target <10 atingido)
- **Redução total**: 65-85 pontos de CC
- **Arquivos novos**: 4 handlers especializados
- **Manutenibilidade**: Cada handler testável isoladamente

#### Ordem de Execução
1. Criar `jdev_cli/handlers/` se não existir
2. Extrair CommandDispatcher (maior impacto)
3. Extrair LSPCommandHandler (segundo maior)
4. Extrair ToolResultFormatter (padrão registry)
5. Extrair InputHandler (menor)
6. Refatorar `_handle_system_command()` para usar dispatcher
7. Atualizar testes existentes
8. Medir CC novamente com radon

---

### 1.3 Consolidação de Tipos (Semanas 6-7)

#### Diagnóstico
8 tipos duplicados identificados em múltiplas localizações:

| Tipo | Localização 1 | Localização 2 | Status |
|------|--------------|---------------|--------|
| CircuitBreaker | jdev_cli/core/llm.py:52 | jdev_tui/core/llm_client.py:61 | Diferentes |
| CircuitState | jdev_cli/core/llm.py:44 | jdev_tui/core/llm_client.py:33 | Idênticos |
| BlockType | block_detector.py:17 | block_renderers.py:48 | String vs Auto |
| AgentIdentity | agent_identity.py:71 | protocol.py:149 | Diferentes propósitos |
| AgentRole | jdev_core/types.py:51 | protocol.py:52 | Subset |
| AgentPriority | planner/types.py | planner/priority.py | Duplicado |
| CheckpointType | planner/types.py | planner/checkpoint.py | Duplicado |
| Action | planner/types.py | planner/actions.py | Duplicado |

#### Estratégia de Consolidação

**1.3.1 Criar Estrutura Unificada de Tipos**
```
jdev_core/
├── types/
│   ├── __init__.py          # Re-exports públicos
│   ├── circuit.py            # CircuitBreaker, CircuitState
│   ├── blocks.py             # BlockType unificado
│   ├── agents.py             # AgentIdentity, AgentRole, AgentPriority
│   ├── planner.py            # CheckpointType, Action
│   └── protocols.py          # Protocolos comuns
```

**1.3.2 CircuitBreaker Unificado**
```python
# jdev_core/types/circuit.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
import time

class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

@dataclass
class CircuitConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3

class CircuitBreaker:
    """Unified circuit breaker implementation."""

    def __init__(self, config: Optional[CircuitConfig] = None):
        self.config = config or CircuitConfig()
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0

    def record_success(self) -> None: ...
    def record_failure(self) -> None: ...
    def can_execute(self) -> bool: ...
    def reset(self) -> None: ...
```

**1.3.3 BlockType Unificado**
```python
# jdev_core/types/blocks.py

from enum import Enum

class BlockType(Enum):
    """Unified block types for detection and rendering."""
    CODE = "code"
    MARKDOWN = "markdown"
    JSON = "json"
    ERROR = "error"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
```

**1.3.4 AgentIdentity Consolidado**
```python
# jdev_core/types/agents.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class AgentRole(Enum):
    """All agent roles in the system."""
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    SECURITY = "security"
    EXPLORER = "explorer"
    REFACTOR = "refactor"
    TESTER = "tester"
    DOCS = "docs"
    DEVOPS = "devops"
    DATA = "data"
    JUSTICA = "justica"
    SOFIA = "sofia"

class AgentPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class AgentIdentity:
    """Complete agent identity."""
    name: str
    role: AgentRole
    priority: AgentPriority = AgentPriority.NORMAL
    description: Optional[str] = None
    capabilities: List[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
```

#### Migração
```python
# Fase 1: Criar tipos unificados (não quebra nada)
# Fase 2: Adicionar deprecation warnings aos tipos antigos
# Fase 3: Migrar imports gradualmente
# Fase 4: Remover tipos antigos após 2 releases

# Exemplo de deprecation
import warnings
from jdev_core.types import CircuitBreaker as _CircuitBreaker

class CircuitBreaker(_CircuitBreaker):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Import from jdev_core.types.circuit instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

#### Resultado Esperado
- **Duplicação**: 10.9% → ~5% (-54%)
- **Tipos consolidados**: 8 → 1 localização cada
- **Imports padronizados**: `from jdev_core.types import X`

---

### 1.4 Testes e Validação (Semana 8)

#### Checklist de Validação

- [ ] Todos os 558+ testes passando
- [ ] CC de shell_main.py < 10
- [ ] Bridge com ≤ 55 métodos
- [ ] Zero tipos duplicados
- [ ] Cobertura de testes ≥ 80%
- [ ] Nenhum import circular
- [ ] Documentação atualizada

#### Métricas de Sucesso Fase 1
| Métrica | Antes | Depois | Target |
|---------|-------|--------|--------|
| Bridge métodos | 74 | ≤52 | ≤55 |
| shell_main CC | 16.43 | ≤9 | <10 |
| Duplicação | 10.9% | ≤6% | <7% |
| Testes | 558 | ≥600 | +42 |

---

## FASE 2: MODULARIZAÇÃO (Q1 2026 - 6 semanas)

### 2.1 Sistema de Plugins (Semanas 1-3)

#### Arquitetura

```
plugins/
├── core/
│   ├── __init__.py
│   ├── base.py              # Plugin, PluginMetadata
│   ├── loader.py            # PluginLoader
│   ├── registry.py          # PluginRegistry
│   └── hooks.py             # PluginHooks
├── builtin/
│   ├── git/                 # Git integration plugin
│   ├── lsp/                 # LSP plugin
│   ├── testing/             # Test runner plugin
│   └── security/            # Security scanner plugin
└── examples/
    └── hello_world/         # Example plugin template
```

#### Interface Base
```python
# plugins/core/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class PluginPriority(Enum):
    CORE = 0        # Sistema core, sempre carrega primeiro
    HIGH = 100      # Plugins importantes
    NORMAL = 500    # Plugins padrão
    LOW = 900       # Plugins opcionais

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    priority: PluginPriority = PluginPriority.NORMAL
    dependencies: List[str] = None
    provides: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.provides is None:
            self.provides = []

class Plugin(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    async def activate(self, context: 'PluginContext') -> None:
        """Called when plugin is activated."""
        pass

    @abstractmethod
    async def deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass

    def on_command(self, command: str, args: str) -> Optional[Any]:
        """Handle custom commands. Return None if not handled."""
        return None

    def on_tool_execute(self, tool_name: str, params: Dict) -> Optional[Any]:
        """Intercept tool execution. Return None to continue."""
        return None
```

#### Plugin Loader
```python
# plugins/core/loader.py

import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict

class PluginLoader:
    """Load plugins from directories."""

    def __init__(self, plugin_dirs: List[Path]):
        self.plugin_dirs = plugin_dirs
        self._loaded: Dict[str, Plugin] = {}

    def discover(self) -> List[PluginMetadata]:
        """Discover available plugins."""
        plugins = []
        for dir in self.plugin_dirs:
            for path in dir.glob("*/plugin.py"):
                try:
                    meta = self._load_metadata(path)
                    plugins.append(meta)
                except Exception as e:
                    logger.warning(f"Failed to load {path}: {e}")
        return sorted(plugins, key=lambda p: p.priority.value)

    async def load(self, name: str) -> Plugin:
        """Load and activate a plugin."""
        if name in self._loaded:
            return self._loaded[name]

        plugin_path = self._find_plugin(name)
        plugin = self._instantiate(plugin_path)
        await plugin.activate(self._create_context())
        self._loaded[name] = plugin
        return plugin
```

### 2.2 Extração de Interfaces (Semanas 3-4)

#### Interfaces Principais

```python
# jdev_core/interfaces/__init__.py

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any, List

class ILLMClient(ABC):
    """Interface for LLM clients."""

    @abstractmethod
    async def chat(
        self,
        message: str,
        context: Optional[List[Dict]] = None
    ) -> AsyncIterator[str]:
        """Stream chat response."""
        pass

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Get completion (non-streaming)."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if client is connected."""
        pass

class IToolExecutor(ABC):
    """Interface for tool execution."""

    @abstractmethod
    async def execute(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> 'ToolResult':
        """Execute a tool."""
        pass

    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        pass

class IAgentRouter(ABC):
    """Interface for agent routing."""

    @abstractmethod
    async def route(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> 'AgentRouteResult':
        """Route query to appropriate agent."""
        pass

class IGovernance(ABC):
    """Interface for governance/security."""

    @abstractmethod
    def assess_risk(self, action: str) -> 'RiskAssessment':
        """Assess risk of an action."""
        pass

    @abstractmethod
    def is_allowed(self, action: str) -> bool:
        """Check if action is allowed."""
        pass
```

### 2.3 SDK Inicial (Semanas 5-6)

#### Estrutura do SDK

```
juan-dev-sdk/
├── pyproject.toml
├── src/
│   └── juan_dev_sdk/
│       ├── __init__.py
│       ├── client.py         # JuanDevClient
│       ├── agents.py         # Agent creation helpers
│       ├── tools.py          # Tool creation helpers
│       ├── plugins.py        # Plugin creation helpers
│       └── types.py          # Public types
└── examples/
    ├── custom_agent.py
    ├── custom_tool.py
    └── custom_plugin.py
```

#### Cliente SDK
```python
# juan_dev_sdk/client.py

from typing import AsyncIterator, Optional, Dict, List
from .types import Message, ToolResult

class JuanDevClient:
    """SDK client for juan-dev-code integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8080"
    ):
        self.api_key = api_key or os.getenv("JUAN_DEV_API_KEY")
        self.base_url = base_url

    async def chat(
        self,
        message: str,
        agent: Optional[str] = None,
        tools: Optional[List[str]] = None
    ) -> AsyncIterator[str]:
        """Stream chat with optional agent and tool selection."""
        async with self._session() as session:
            async for chunk in self._stream_chat(session, message, agent, tools):
                yield chunk

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict
    ) -> ToolResult:
        """Execute a tool directly."""
        pass

    def register_plugin(self, plugin: 'Plugin') -> None:
        """Register a custom plugin."""
        pass
```

---

## FASE 3: DISTRIBUIÇÃO (Q2-Q4 2026)

### 3.1 Async Everywhere (Q2 - Semanas 1-4)

#### Migração para Full Async

**Áreas de Migração**:
1. File I/O → `aiofiles`
2. HTTP requests → `httpx.AsyncClient`
3. Process execution → `asyncio.create_subprocess_exec`
4. Database → `aiosqlite` ou `asyncpg`

**Padrão de Migração**:
```python
# Antes
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# Depois
async def read_file(path: str) -> str:
    async with aiofiles.open(path) as f:
        return await f.read()

# Wrapper de compatibilidade temporário
def read_file_sync(path: str) -> str:
    import asyncio
    return asyncio.run(read_file(path))
```

### 3.2 Connection Pooling (Q2 - Semanas 5-8)

#### Pools Necessários

```python
# connection_pools.py

from contextlib import asynccontextmanager
import httpx
import aiosqlite

class ConnectionManager:
    """Manage all connection pools."""

    def __init__(self, config: 'PoolConfig'):
        self.config = config
        self._http_pool: Optional[httpx.AsyncClient] = None
        self._db_pool: Optional[aiosqlite.Connection] = None

    async def startup(self) -> None:
        """Initialize all pools."""
        self._http_pool = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=self.config.http_max_connections,
                max_keepalive_connections=self.config.http_keepalive
            ),
            timeout=httpx.Timeout(self.config.http_timeout)
        )

    async def shutdown(self) -> None:
        """Close all pools."""
        if self._http_pool:
            await self._http_pool.aclose()

    @asynccontextmanager
    async def http(self):
        """Get HTTP client from pool."""
        yield self._http_pool
```

### 3.3 Message Queue (Q3 - Semanas 1-6)

#### Arquitetura com Redis/RabbitMQ

```python
# message_queue.py

from abc import ABC, abstractmethod
from typing import Callable, Awaitable
import json

class MessageQueue(ABC):
    """Abstract message queue interface."""

    @abstractmethod
    async def publish(self, topic: str, message: dict) -> None:
        pass

    @abstractmethod
    async def subscribe(
        self,
        topic: str,
        handler: Callable[[dict], Awaitable[None]]
    ) -> None:
        pass

class RedisQueue(MessageQueue):
    """Redis-based message queue."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis = None

    async def publish(self, topic: str, message: dict) -> None:
        await self._redis.publish(topic, json.dumps(message))

# Tópicos definidos
TOPICS = {
    "agent.request": "Requests for agent processing",
    "agent.response": "Agent responses",
    "tool.execute": "Tool execution requests",
    "tool.result": "Tool execution results",
    "event.system": "System events",
}
```

### 3.4 Multi-Tenant (Q4 - Semanas 1-8)

#### Isolamento por Tenant

```python
# multi_tenant.py

from dataclasses import dataclass
from typing import Optional
from contextvars import ContextVar

current_tenant: ContextVar[Optional['Tenant']] = ContextVar('tenant', default=None)

@dataclass
class Tenant:
    id: str
    name: str
    config: 'TenantConfig'
    limits: 'TenantLimits'

@dataclass
class TenantLimits:
    max_requests_per_minute: int = 100
    max_tokens_per_day: int = 1_000_000
    max_concurrent_agents: int = 5
    allowed_tools: List[str] = None

class TenantMiddleware:
    """Middleware for tenant isolation."""

    async def __call__(self, request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            tenant = await self._load_tenant(tenant_id)
            current_tenant.set(tenant)

        response = await call_next(request)
        return response
```

---

## Cronograma Consolidado

```
2025 Q4 (Nov-Dez)
├── Semana 1-3: Refatoração Bridge (6 managers)
├── Semana 4-5: Redução CC shell_main.py
├── Semana 6-7: Consolidação de tipos
└── Semana 8: Testes e validação

2026 Q1 (Jan-Fev)
├── Semana 1-3: Sistema de plugins
├── Semana 3-4: Extração de interfaces
└── Semana 5-6: SDK inicial

2026 Q2 (Mar-Abr)
├── Semana 1-4: Async everywhere
└── Semana 5-8: Connection pooling

2026 Q3 (Mai-Jun)
└── Semana 1-6: Message queue

2026 Q4 (Jul-Ago)
└── Semana 1-8: Multi-tenant
```

---

## Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Breaking changes na API | Alto | Médio | Versionamento semântico, deprecation warnings |
| Regressões em refatorações | Alto | Alto | Cobertura de testes >80%, CI/CD rigoroso |
| Complexidade do plugin system | Médio | Médio | MVP primeiro, iterar |
| Performance degradation | Alto | Baixo | Benchmarks automatizados |
| Resistência à mudança | Médio | Baixo | Documentação clara, migration guides |

---

## Métricas de Sucesso Final

| Fase | Métrica | Target |
|------|---------|--------|
| Fase 1 | CC máximo | <10 |
| Fase 1 | Duplicação | <7% |
| Fase 1 | God classes | 0 |
| Fase 2 | Plugins funcionais | ≥5 |
| Fase 2 | SDK coverage | 100% |
| Fase 3 | Latência p99 | <500ms |
| Fase 3 | Throughput | 10x baseline |
| Fase 3 | Tenants suportados | 100+ |

---

**Soli Deo Gloria**

*Plano criado por JuanCS Dev - 2025-11-26*
