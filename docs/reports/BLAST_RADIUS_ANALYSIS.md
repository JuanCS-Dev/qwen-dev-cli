# BLAST RADIUS ANALYSIS - juan-dev-code (jdev_tui + jdev_cli)
## Mapa de Dependências Críticas e Propagação de Falhas

**Análise Data:** 2025-11-26
**Escopo:** jdev_tui, jdev_cli, jdev_core, jdev_governance
**Foco:** Identificação de pontos únicos de falha (SPOF) e efeitos de cascata

---

## RESUMO EXECUTIVO

**Status de Saúde:** VULNERÁVEL
- **Pontos de Falha Únicos (SPOF):** 8 componentes críticos
- **Cadeias de Dependência Longas:** 4 identificadas (profundidade 5+)
- **Sem Fallback:** 6 componentes críticos
- **Impacto Potencial se Falhar:** CRÍTICO

### Dependências Externas Críticas
1. **Gemini API** (Google) - SINGLE POINT OF FAILURE
2. **MCP Client** - Intermediário para todas as ferramentas
3. **Sistema de Arquivos** - I/O em caminho crítico
4. **httpx** - Rede (sem fallback primário)

---

## SEÇÃO 1: DEPENDÊNCIAS EXTERNAS CRÍTICAS

### 1.1 Gemini API (Google Cloud)

| Aspecto | Descrição |
|---------|-----------|
| **Componente** | `GeminiClient` (jdev_tui/core/llm_client.py) |
| **Dependências Diretas** | `google.generativeai` SDK, `httpx` (fallback) |
| **Impacto se Falhar** | **5 (CRÍTICO)** - Toda IA pausa |
| **Tem Fallback?** | Parcial: httpx direct API (sem garantia) |
| **Timeout** | Sem timeout explícito na inicialização |
| **Rate Limit** | Não implementado em llm_client.py |
| **Recurso Compartilhado** | API key em os.environ (sem sincronização) |

**Pontos de Falha Identificados:**
```
GeminiClient._ensure_initialized()
  ├─ google.generativeai.configure(api_key) ← PODE FALHAR
  ├─ API_KEY não validado antes
  ├─ Sem circuit breaker
  └─ _stream_httpx() fallback PODE NÃO FUNCIONAR (httpx timeout 60s = longo)
```

**Cascata Potencial:**
- Falha Gemini API → Bridge.is_connected = False
- → Bridge.chat() retorna erro
- → TUI fica congelada
- → Usuário fica bloqueado

**Recomendação:** Timeout 5s, Circuit breaker em LLMClient

---

### 1.2 MCP Client - Intermediário de Ferramentas

| Aspecto | Descrição |
|---------|-----------|
| **Componente** | `MCPClient` (jdev_cli/core/mcp.py) |
| **Dependências Diretas** | `ToolRegistry`, subprocess (em tools) |
| **Impacto se Falhar** | **5 (CRÍTICO)** - Zero ferramentas |
| **Tem Fallback?** | NÃO |
| **Conexão** | Sem verificação de saúde |
| **Recurso Compartilhado** | Registry único (não replicado) |

**Pontos de Falha:**
```
MCPClient.call_tool()
  ├─ tool = registry.get(name) ← Sem validação
  ├─ result = await tool._execute_validated() ← PODE LANÇAR
  └─ FALHA AQUI = ferramenta não disponível
```

**Cascata:**
- MCP não responde → ToolBridge.execute_tool() falha
- → Bridge.chat() iteration loop quebra
- → Usuário vê erro incompleto

**Problema Específico:** `ToolBridge._create_registry()` tem 7 blocos try/except diferentes, TODOS FALHAM SILENCIOSAMENTE se importação falha.

---

### 1.3 Serviços de Rede Externos

| Serviço | URL | Timeout | Fallback | Crítico? |
|---------|-----|---------|----------|----------|
| **Gemini API** | `generativelanguage.googleapis.com` | 60s | httpx | SIM |
| **Web Search** | Via httpx | 30s | Nenhum | NÃO |
| **Fetch URL** | httpx | 30s | Nenhum | NÃO |
| **HF Hub** | `huggingface.co` | Padrão | Nenhum | NÃO |

**Vulnerabilidades:**
- TIMEOUT LONGO: 60s em Gemini (pode travar TUI)
- SEM EXPONENTIAL BACKOFF em llm_client.py
- SEM RATE LIMITING em llm_client.py
- httpx.AsyncClient sem pool_timeout

---

### 1.4 Sistema de Arquivos (I/O)

| Aspecto | Descrição |
|---------|-----------|
| **Componente** | `ReadFileTool`, `WriteFileTool` |
| **Operações Críticas** | read_memory(), load_project_memory() |
| **Timeout** | NENHUM (pode travar indefinidamente) |
| **Tem Fallback?** | NÃO |
| **Lock Contention** | HistoryManager pode ter race condition |

**Pontos de Falha:**
```
Bridge._load_credentials()
  └─ creds_file.read_text() ← PODE TRAVAR em NFS/problemas FS
```

```
Bridge.read_memory()
  └─ memory_file.read_text() ← SEM TIMEOUT
```

---

## SEÇÃO 2: DEPENDÊNCIAS INTERNAS

### 2.1 Bridge (Facade Master)

| Propriedade | Valor |
|-------------|-------|
| **Arquivo** | jdev_tui/core/bridge.py |
| **Linhas** | 1444 (GOD CLASS refatorada) |
| **Dependências Diretas** | 12 módulos |
| **Estado Compartilhado** | `_session_tokens`, `_todos`, threading.Lock (2) |
| **Impacto se Falhar** | **5 (CRÍTICO)** |
| **Tem Fallback?** | Parcial (agents 3 = opcional) |

**Mapa de Dependências da Bridge:**
```
Bridge (CENTRAL)
├─ GeminiClient ── (FALHA = SEM IA)
├─ GovernanceObserver ── Não crítico (observer mode)
├─ AgentManager ── (FALHA = atua com 3 agents)
│  └─ AgentRouter
│  └─ AGENT_REGISTRY (14 agents, lazy-loaded)
├─ ToolBridge ── (FALHA = sem tools, mas continua)
│  └─ ToolRegistry (7 importações com try/except)
├─ CommandPaletteBridge ── (FALHA = sem palette, UI funciona)
├─ AutocompleteBridge ── (FALHA = sem autocomplete)
├─ HistoryManager ── (FALHA = sem contexto)
├─ CustomCommandsManager ── Opcional (graceful degradation)
├─ HooksManager ── Opcional
└─ PlanModeManager ── Opcional
```

**Problema Crítico:** Bridge.__init__() tenta inicializar tudo, MAS não valida:
1. GeminiClient.api_key existência
2. ToolRegistry carregamento
3. Arquivo .env acesso

Se QUALQUER um falhar silenciosamente → estado inconsistente

---

### 2.2 Agent System (Cascata de Falhas)

| Aspecto | Descrição |
|---------|-----------|
| **Cadeia de Invocação** | Bridge.chat() → AgentRouter.route() → AgentManager.invoke_agent() → Agent.execute() |
| **Profundidade** | 5 níveis |
| **SPOF** | AgentRouter (confidence threshold = 0.5) |
| **Impacto** | **4 (ALTO)** |
| **Tem Fallback?** | SIM: cai para LLM direto se routing falha |

**Fluxo de Falha:**
```
Bridge.chat(message, auto_route=True)
  ├─ routing = agents.router.route(message) ← PODE RETORNAR NONE
  ├─ if routing → invoke_agent(agent_name) 
  │  └─ agent.execute(task) ← PODE FALHAR
  │     └─ agent._call_llm() ← TIMEOUT?
  │        └─ GeminiClient.stream() ← FALHA CASCATA
  └─ else → continua com LLM direto (fallback OK)
```

**Agents Lazy-Loaded (Risco):**
```
AGENT_REGISTRY[agent_name].module_path = "jdev_cli.agents.executor"
                        ↓ import dinâmico
                        ↓ PODE FALHAR (ImportError)
                        ↓ Agent não instanciado
                        ↓ ERRO PARA USUÁRIO
```

---

### 2.3 Tools Bridge - Cascata de Carregamento

| Propriedade | Valor |
|-------------|-------|
| **Dependências** | 6 categorias × 7 imports = 42 possíveis falhas |
| **Estratégia Falha** | Cada categoria tem try/except (silencioso) |
| **Load Errors** | Não reportados ao usuário |
| **Impacto** | **3 (MÉDIO)** - apenas tools falham, app continua |

**Estrutura de Risco:**
```
ToolBridge.registry (lazy-loaded)
  ├─ FileOperations (5 imports)
  │  └─ ImportError → silencioso
  ├─ Terminal (9 imports)  
  │  └─ ImportError → silencioso
  ├─ Web (6 imports)
  │  └─ ImportError → silencioso
  └─ Si nenhuma categoria carrega
     └─ MinimalRegistry() vazio retorna
     └─ tools.list_tools() = []
     └─ Bridge UI mostra "0 tools loaded"
```

**Impacto Específico:**
- WriteFileTool não carrega → `/write_file` retorna "not found"
- Usuario tenta criar arquivo → "Tool not found: write_file"
- Mas Bridge continua funcionando!

---

## SEÇÃO 3: PONTOS DE PROPAGAÇÃO DE FALHA

### 3.1 Cadeia Crítica: Gemini → Agents → Ferramentas

```
┌─────────────────────────────────────────────────────────┐
│ CAMINHO 1: Execução via Agente                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Bridge.chat(message)                                  │
│    ↓                                                    │
│  routing = AgentRouter.route(message)                  │
│    ↓                                                    │
│  invoke_agent(agent_name, message)                    │
│    ↓ (Lazy load)                                       │
│  agent = AgentManager._load_agent(agent_name)          │
│    ├─ FALHA: ImportError do módulo agent              │
│    │   → Retorna None ou erro                          │
│    │   → USUÁRIO VÊ: "Failed to load agent"           │
│    └─ SUCESSO: Agent instanciado                       │
│       ↓                                                 │
│       agent.execute(task)                             │
│         ↓                                              │
│         agent._stream_llm(prompt) ← Requer Gemini     │
│           ├─ TIMEOUT: 60s (httpx) = congelado          │
│           ├─ FALHA API: Sem retry/backoff             │
│           └─ SUCESSO: Stream de tokens                 │
│             ↓                                          │
│             agent._execute_tool(tool_name)            │
│               ├─ MCP client falha → Tool erro          │
│               └─ Tool sucesso → Resultado             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Vulnerabilidades Identificadas:**
1. **Sem timeout em `_load_credentials()`** (fs I/O)
2. **Sem timeout em httpx** (60s = muito longo)
3. **Agent load falha sem retry**
4. **MCP client falha sem fallback**

---

### 3.2 Timeout Que Causa Cascata

| Timeout | Localização | Duração | Efeito |
|---------|------------|---------|--------|
| LLM Response | llm_client.py:378 | **NENHUM** | Congelado indefinidamente |
| httpx streaming | llm_client.py:412 | 60s | TUI travada 1min |
| File I/O | bridge.py:174 | NENHUM | Travada em NFS |
| Agent load | N/A | NENHUM | Bloqueado em import |
| Tool execution | ToolBridge | Depende tool | Varia |

**Cenário Cascata:**
```
Usuário digita: "/execute python long_script.py"
  ↓
ExecutorAgent carrega (import OK)
  ↓
ExecutorAgent._stream_llm() inicia
  ↓
GeminiClient.stream() abre httpx connection
  ↓
Gemini API não responde (servidor down)
  ↓
httpx aguarda 60 segundos = CONGELADO
  ↓
TUI não responde a keyboard
  ↓
Usuário força kill (não graceful)
```

---

### 3.3 Recursos Compartilhados (Locks)

| Recurso | Localização | Tipo Lock | Crítico? |
|---------|------------|-----------|----------|
| `_router_lock` | bridge.py:142 | threading.Lock | Sim |
| `_plan_mode_lock` | bridge.py:143 | threading.Lock | Sim |
| `_plan_mode_lock` | plan_mode_manager.py:70 | threading.Lock | Sim |
| `_bridge_lock` (singleton) | bridge.py:1391 | threading.Lock | Sim |
| HistoryManager.context | history_manager.py | Lista mutável | Sim |

**Problemas Identificados:**

1. **Singleton Pattern Double-Check Locking (VULNERÁVEL)**
```python
# bridge.py:1390-1402
def get_bridge() -> Bridge:
    global _bridge_instance
    if _bridge_instance is None:  # ← RACE CONDITION AQUI
        with _bridge_lock:
            if _bridge_instance is None:
                _bridge_instance = Bridge()
    return _bridge_instance
```
**Problema:** Verificação sem lock antes = múltiplas threads podem entrar

2. **HistoryManager Context Mutation (SEM LOCK)**
```python
# bridge.py:296-298
self.history.add_command(message)  # Modifica lista
self.history.add_context("user", message)  # Modifica lista
# Se async e múltiplos chats simultâneos → CORRUPTS HISTORY
```

3. **Router State Mutation (SEM SINCRONIZAÇÃO)**
```python
# agents_bridge.py
routing = self.agents.router.route(message)  # Lê padrões
# Se router recebe update durante rota → inconsistência
```

---

## SEÇÃO 4: IMPACTO POR FALHA DE COMPONENTE

### Matriz de Impacto

| Componente | Falha Tipo | Impacto Direto | Impacto Cascata | Severidade | Recovery |
|-----------|-----------|---|---|---|---|
| **GeminiClient** | API Down | Sem IA | Todo chat para | 5 | Manual reconnect |
| **GeminiClient** | Timeout | TUI congelada | Sem responsividade | 5 | Kill + restart |
| **MCP Client** | Import fail | Sem tools | Chat funciona | 3 | Fallback ok |
| **AgentRouter** | Pattern fail | Agent não rota | Cai para LLM | 2 | Graceful |
| **ToolBridge** | Tool fail | Tool não exec | Erro ao usuário | 2 | Erro handled |
| **HistoryManager** | Corruption | Estado ruim | Chat com erro | 3 | Reset history |
| **File I/O** | NFS timeout | Travada | TUI congelada | 4 | Manual kill |
| **Governance** | Fail | Regras não aplicadas | Nenhum impacto | 1 | Optional |

---

## SEÇÃO 5: ANÁLISE DETALHADA POR COMPONENTE

### 5.1 jdev_tui/core/bridge.py

**Características:**
- 1444 linhas (GOD CLASS refatorada para Facade)
- 12 dependências diretas
- 2 threading locks
- Estado: `_session_tokens`, `_todos`, `_auto_route_enabled`

**Dependências Diretas Críticas:**
```python
from .governance import GovernanceObserver           # Impacto: 1 (não crítico)
from .llm_client import GeminiClient                # Impacto: 5 (CRÍTICO)
from .agents_bridge import AgentManager             # Impacto: 4 (alto)
from .tools_bridge import ToolBridge                # Impacto: 3 (médio)
from .ui_bridge import CommandPaletteBridge         # Impacto: 2 (baixo)
from .history_manager import HistoryManager         # Impacto: 3 (médio)
```

**Métodos com Risco de Timeout:**
- `__init__()` - Não valida API key antes de criar GeminiClient
- `_load_credentials()` - File I/O SEM TIMEOUT
- `_configure_llm_tools()` - Chama tools.get_schemas_for_llm() SEM TIMEOUT
- `chat()` - Loop agentic até MAX_TOOL_ITERATIONS sem timeout global

**Problemas Thread-Safety:**
```python
# bridge.py:142-143
_router_lock = threading.Lock()   # OK
_plan_mode_lock = threading.Lock()  # OK

# Mas: history.context é lista mutável SEM LOCK
# Múltiplas threads → corrupted context

# Também: _session_tokens é int mutável
# Sem atomic operations
```

---

### 5.2 jdev_tui/core/llm_client.py

**Características:**
- Streaming Gemini client
- Fallback httpx (sem garantia)
- Suporta function calling via tool schemas

**Vulnerabilidades Críticas:**

1. **SEM TIMEOUT** em _ensure_initialized()
```python
# Linha 242: genai.configure(api_key=self.api_key)
# Pode hangar indefinidamente se genai travado
```

2. **SEM EXPONENTIAL BACKOFF**
```python
# _stream_sdk() usa SDK nativo sem retry
# Se API rate-limited → error direto
```

3. **SEM CIRCUIT BREAKER**
```python
# Múltiplos erros consecutivos = múltiplas tentativas
# Sem cool-down
```

4. **httpx TIMEOUT LONGO**
```python
# Linha 412: async with httpx.AsyncClient(timeout=60.0)
# 60 segundos = TUI congelada por 1 minuto
```

**Fluxo de Falha:**
```
stream(prompt, system_prompt, context)
  ↓
_ensure_initialized() ← PODE HANGAR
  ├─ API key não validado
  ├─ genai.configure() pode falhar
  └─ Sem timeout
```

---

### 5.3 jdev_cli/agents/base.py

**Características:**
- Abstract base para todos os 14 agentes
- Implementa OODA loop (Observe, Orient, Decide, Act)
- Acesso a MCP client para tool execution

**Dependências Críticas:**
```python
from jdev_core.types import AgentTask, AgentResponse  # OK
# llm_client via self.llm_client (dependência runtime)
# mcp_client via self.mcp_client (pode ser None!)
```

**Pontos de Falha:**

1. **mcp_client pode ser None**
```python
# Linha 243-245
if self.mcp_client is None:
    return {"success": False, "error": "MCP client not initialized"}
# Tool execution fica inacessível!
```

2. **_stream_llm() tenta múltiplos métodos**
```python
# Linha 169-186
if hasattr(self.llm_client, 'stream_chat'):
    # ...
elif hasattr(self.llm_client, 'stream'):
    # ...
else:
    response = await self._call_llm(...)  # Fallback
# Ordem importa! Se llm_client não tem métodos → use generate()
```

3. **_call_llm() SEM TIMEOUT**
```python
# Linha 132-137
response = await self.llm_client.generate(
    prompt=prompt,
    system_prompt=final_sys_prompt,
    **kwargs,
)
# Sem timeout → pode hangar indefinidamente
```

---

### 5.4 jdev_cli/agents/executor.py

**Características:**
- NextGen CLI Code Executor Agent (Nov 2025)
- 432 linhas
- Suporta: LOCAL, DOCKER, E2B execution modes
- Security levels: PERMISSIVE, STANDARD, STRICT, PARANOID

**Dependências Críticas:**
```python
from .base import BaseAgent
from ..core.llm import LLMClient        # Pode não estar disponível
from ..core.mcp_client import MCPClient # Pode falhar
from ..permissions import PermissionManager
```

**Pontos de Falha:**

1. **LLMClient não importado no topo (linha 58)**
```python
from ..core.llm import LLMClient  # ← Pode falhar
# Se falha → ExecutorAgent não pode ser instanciado
```

2. **MCP Client sem fallback**
```python
# Executor depende MCP para executar commands
# Se MCP falha → tool execution impossível
```

3. **Subprocess execution SEM TIMEOUT**
```python
# Se usando LOCAL mode
# subprocess.run() SEM TIMEOUT = pode ficar preso
```

---

### 5.5 jdev_cli/core/llm.py

**Características:**
- Production-grade multi-backend LLM client
- Implementa: CircuitBreaker, RateLimiter, RequestMetrics
- Suporta: Gemini, OpenAI, Anthropic, Nebius, Groq

**Estrutura de Resiliência:**
```python
@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    # IMPLEMENTADO CORRETAMENTE

@dataclass  
class RateLimiter:
    requests_per_minute: int = 50
    tokens_per_minute: int = 10000
    # IMPLEMENTADO CORRETAMENTE
```

**MAS:** Não é usado em llm_client.py (jdev_tui/core/)!
- GeminiClient in jdev_tui não usa CircuitBreaker/RateLimiter
- Apenas LLMClient em jdev_cli/core/ tem resiliência
- **DESCONEXÃO: 2 implementações diferentes**

---

## SEÇÃO 6: CENÁRIOS DE CASCATA CRÍTICA

### Cenário 1: Gemini API Down (Cascata Total)

**Tempo: 0:00**
```
Usuário inicia jdev-tui
↓
Bridge.__init__() called
  ├─ GeminiClient() instanciado (api_key verificado)
  └─ GeminiClient._ensure_initialized() NÃO CHAMADO YET
↓
User digita: "Generate code"
↓
Impacto: ✓ VISÍVEL
```

**Tempo: 0:05**
```
Bridge.chat("Generate code")
  ├─ GeminiClient.stream() called (LAZY INIT)
  │   └─ _ensure_initialized() 
  │       └─ genai.configure(api_key) ← API UNREACHABLE
  │           └─ TIMEOUT AFTER 60s (httpx)
  ├─ TUI fica congelada por 60 segundos
  ├─ Usuário pensa app crashou
  └─ CASCATA: Chat completo bloqueado
```

**Recovery Possível?**
- Não automático (sem retry)
- Usuário deve Ctrl+C e reiniciar
- Estado pode ficar corrupto

---

### Cenário 2: MCP Client Falha com File Tools

**Tempo: 0:00**
```
Bridge.__init__()
  └─ ToolBridge()
      └─ registry (lazy-loaded)
```

**Tempo: 0:05**
```
User digita: "/architect analyze src/main.py"
↓
Architect Agent carrega (OK)
↓
Agent executa: "read_file(path='src/main.py')"
↓
ToolBridge.execute_tool('read_file', path='src/main.py')
  ├─ tool = registry.get('read_file')
  ├─ MCP.call_tool('read_file', {'path': 'src/main.py'})
  │   └─ IF MCP falha → ERRO
  └─ Usuário vê: "Tool execution failed"
```

**Cascata?**
- Agent continua (graceful)
- Chat não completa (mas não trava)
- Impacto: 3/5 (médio)

**Recovery:**
- Automático: retry ou fallback
- Possível: Sim

---

### Cenário 3: Agent Router + Executor Chain Falha

**Tempo: 0:00**
```
User digita: "/plan refactor database layer"
```

**Tempo: 0:02**
```
Bridge.chat() with auto_route=True
  ├─ routing = agents.router.route(message)
  │   └─ Matches: "planner" (confidence=0.8)
  ├─ invoke_agent('planner', message)
  │   ├─ IMPORT jdev_cli.agents.planner ← FALHA (module not found)
  │   ├─ CATCH: ImportError (silencioso!)
  │   └─ Agente não instanciado
  └─ ERROR: Agent invocation failed
```

**Cascata?**
- Usuário vê erro (handled)
- Chat pode continuar sem agent
- Impacto: 2/5 (baixo)

**Recovery:**
- Automático: fallback to LLM
- Possível: Sim

---

### Cenário 4: HistoryManager Corruption (Race Condition)

**Tempo: Simultaneous**
```
Thread 1 (Chat input):
  bridge.chat(message1)
    └─ history.add_context("user", message1)
        └─ self.context.append({role, content})  ← Write

Thread 2 (Agent execution):
  agent.execute()
    └─ bridge._get_system_prompt()
        └─ self.history.get_context()
            └─ return self.context.copy()  ← Read
                        ↑
            RACE CONDITION: Context being modified
```

**Cascata?**
- Corrupted history = bad context for LLM
- LLM gera resposta inconsistente
- User vê erros aleatórios
- Impacto: 3/5 (médio)

**Recovery:**
- Não automático
- User deve clear history

---

## SEÇÃO 7: MATRIZ DE SEVERIDADE FINAL

### Legenda
- **Severidade 5:** CRÍTICO - Toda aplicação para
- **Severidade 4:** ALTO - Feature major bloqueada
- **Severidade 3:** MÉDIO - Degradação notável
- **Severidade 2:** BAIXO - Impacto limitado
- **Severidade 1:** MÍNIMO - Quase nenhum impacto

### Tabela Final

| # | Componente | Dependência | Falha Tipo | Severidade | Fallback? | Timeout? | SPOF? |
|----|-----------|-----------|-----------|-----------|----------|----------|--------|
| 1 | GeminiClient | google.generativeai | API Down | **5** | Sim (weak) | Não | **SIM** |
| 2 | GeminiClient | httpx stream | Network | **4** | Não | 60s | SIM |
| 3 | MCP Client | Tool Registry | Import | **3** | Sim | Não | Não |
| 4 | AgentRouter | Intent patterns | Logic fail | **2** | Sim | Não | Não |
| 5 | BaseAgent | llm_client | Stream timeout | **4** | Não | Não | **SIM** |
| 6 | Executor Agent | subprocess | Hang | **4** | Não | Depende | SIM |
| 7 | HistoryManager | context list | Race condition | **3** | Não | N/A | Não |
| 8 | Bridge singleton | get_bridge() | Double init | **2** | Sim | Não | Não |
| 9 | File I/O | OS filesystem | NFS timeout | **4** | Não | Não | Não |
| 10 | Tool execution | MCP call | Tool fail | **2** | Sim | Depende | Não |

---

## SEÇÃO 8: RECOMENDAÇÕES CRÍTICAS

### Priority 1 (IMEDIATO)

1. **Adicione timeout em GeminiClient._ensure_initialized()**
```python
async def _ensure_initialized(self) -> bool:
    if self._initialized:
        return True
    
    if not self.api_key:
        return False
    
    try:
        import google.generativeai as genai
        # ADICIONE:
        import asyncio
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: genai.configure(api_key=self.api_key)
            ),
            timeout=5.0  # 5 segundo timeout
        )
        # ...
```

2. **Implemente Circuit Breaker em llm_client.py**
```python
from jdev_cli.core.llm import CircuitBreaker

class GeminiClient:
    def __init__(self, ...):
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30.0
        )
    
    async def stream(self, ...):
        can_attempt, reason = self._circuit_breaker.can_attempt()
        if not can_attempt:
            yield f"Circuit open: {reason}"
            return
        
        try:
            # ... stream logic ...
            self._circuit_breaker.record_success()
        except Exception as e:
            self._circuit_breaker.record_failure()
            raise
```

3. **Reduza timeout httpx para 10s máximo**
```python
# Linha 412 em llm_client.py
async with httpx.AsyncClient(timeout=10.0) as client:  # Foi 60.0
```

### Priority 2 (SEMANA 1)

4. **Implemente thread-safe HistoryManager**
```python
import threading

class HistoryManager:
    def __init__(self):
        self._context_lock = threading.RLock()
        self.context = []
    
    def add_context(self, role, content):
        with self._context_lock:
            self.context.append({...})
    
    def get_context(self):
        with self._context_lock:
            return copy.deepcopy(self.context)
```

5. **Valide API key antes de criar Bridge**
```python
# bridge.py
def __init__(self):
    # ADICIONE VALIDAÇÃO:
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY não configurada")
        self._api_key_missing = True
    else:
        self._api_key_missing = False
    
    # ... resto do init ...
```

6. **Implemente retry logic com backoff exponencial**
```python
async def stream_with_retry(self, prompt, system_prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            async for chunk in self.llm.stream(prompt, system_prompt):
                yield chunk
            return
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Retry {attempt + 1}/{max_retries}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise
```

### Priority 3 (SEMANA 2)

7. **Combine implementações de resiliência**
   - Unify CircuitBreaker entre jdev_cli.core.llm e jdev_tui.core.llm_client
   - Use jdev_cli.core.llm como "source of truth"
   - jdev_tui.llm_client importa de lá

8. **Implemente health check periódico**
```python
async def health_check_loop(self):
    while True:
        try:
            await asyncio.wait_for(
                self.llm.generate("ping", system_prompt="Respond with 'pong'"),
                timeout=5.0
            )
            self._health_status = "ok"
        except:
            self._health_status = "degraded"
        
        await asyncio.sleep(30)  # Check a cada 30s
```

9. **Adicione observabilidade**
```python
class MetricsCollector:
    def __init__(self):
        self.api_latencies = []
        self.tool_exec_times = []
        self.error_count = 0
        self.timeout_count = 0
    
    def record_api_call(self, duration, success):
        self.api_latencies.append(duration)
        if not success:
            self.error_count += 1
    
    def get_stats(self):
        return {
            'avg_latency': statistics.mean(self.api_latencies),
            'errors': self.error_count,
            'p95_latency': statistics.quantiles(...),
        }
```

---

## SEÇÃO 9: ESTRUTURA DE RECUPERAÇÃO RECOMENDADA

### Hierarquia de Fallbacks

```
┌─────────────────────────────────────────┐
│ NÍVEL 0: Circuito Aberto (Circuit Open)│
│ Gemini API completamente indisponível  │
└──────────────┬──────────────────────────┘
               ↓ Tenta fallback
┌─────────────────────────────────────────┐
│ NÍVEL 1: Cache de Respostas             │
│ Se visto antes, retorna cached response │
└──────────────┬──────────────────────────┘
               ↓ Se não tem cache
┌─────────────────────────────────────────┐
│ NÍVEL 2: Resposta Genérica              │
│ "I cannot access my AI backend now..."  │
└──────────────┬──────────────────────────┘
               ↓ Se nada funciona
┌─────────────────────────────────────────┐
│ NÍVEL 3: Modo Offline                   │
│ Só permitir operações locais (read/git) │
└─────────────────────────────────────────┘
```

---

## CONCLUSÃO

### Vulnerabilidades Críticas Identificadas:
1. **Gemini API = SPOF sem timeout** (Severidade 5)
2. **MCP Client sem fallback** (Severidade 3)
3. **HistoryManager race conditions** (Severidade 3)
4. **File I/O sem timeout** (Severidade 4)
5. **Agent loading dinâmico sem validação** (Severidade 3)

### Impacto Potencial:
- **Cenário Pior Caso:** Usuário digita comando, app trava por 60+ segundos
- **Cascata Máxima:** Gemini down → ToolBridge fail → AgentManager fail → Chat não funciona
- **Recuperação:** Não automática em muitos casos

### Próximos Passos:
1. Implementar timeout em TODOS os I/O
2. Usar CircuitBreaker para APIs externas
3. Adicionar observabilidade
4. Testar cascatas (chaos engineering)
5. Documentar SLAs e recovery procedures

