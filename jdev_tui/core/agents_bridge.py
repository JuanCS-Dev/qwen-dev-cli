"""
Agents Bridge Module - Agent Registry, Router, and Manager
==========================================================

Extracted from Bridge GOD CLASS (Nov 2025 Refactoring).

Features:
- AgentInfo: Metadata about agents
- AGENT_REGISTRY: 14 specialized agents
- AgentRouter: Intelligent intent-based routing (PT-BR + EN)
- AgentManager: Lazy-loading agent lifecycle management
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_client import GeminiClient


@dataclass
class AgentInfo:
    """Metadata about an agent."""
    name: str
    role: str
    description: str
    capabilities: List[str]
    module_path: str
    class_name: str


# Agent registry - lazy loaded
AGENT_REGISTRY: Dict[str, AgentInfo] = {
    "planner": AgentInfo(
        name="planner",
        role="PLANNER",
        description="Goal-Oriented Action Planning (GOAP)",
        capabilities=["planning", "coordination", "decomposition"],
        module_path="jdev_cli.agents.planner",
        class_name="PlannerAgent",
    ),
    "executor": AgentInfo(
        name="executor",
        role="EXECUTOR",
        description="Secure code execution with sandbox",
        capabilities=["bash", "python", "tools"],
        module_path="jdev_cli.agents.executor",
        class_name="NextGenExecutorAgent",
    ),
    "architect": AgentInfo(
        name="architect",
        role="ARCHITECT",
        description="Architecture analysis and feasibility",
        capabilities=["design", "analysis", "veto"],
        module_path="jdev_cli.agents.architect",
        class_name="ArchitectAgent",
    ),
    "reviewer": AgentInfo(
        name="reviewer",
        role="REVIEWER",
        description="Enterprise code review",
        capabilities=["review", "analysis", "suggestions"],
        module_path="jdev_cli.agents.reviewer",
        class_name="ReviewerAgent",
    ),
    "explorer": AgentInfo(
        name="explorer",
        role="EXPLORER",
        description="Codebase exploration and navigation",
        capabilities=["search", "navigate", "understand"],
        module_path="jdev_cli.agents.explorer",
        class_name="ExplorerAgent",
    ),
    "refactorer": AgentInfo(
        name="refactorer",
        role="REFACTORER",
        description="Code refactoring and improvement",
        capabilities=["refactor", "improve", "transform"],
        module_path="jdev_cli.agents.refactorer",
        class_name="RefactorerAgent",
    ),
    "testing": AgentInfo(
        name="testing",
        role="TESTING",
        description="Test generation and execution",
        capabilities=["generate_tests", "run_tests", "coverage"],
        module_path="jdev_cli.agents.testing",
        class_name="TestingAgent",
    ),
    "security": AgentInfo(
        name="security",
        role="SECURITY",
        description="Security analysis (OWASP)",
        capabilities=["scan", "audit", "vulnerabilities"],
        module_path="jdev_cli.agents.security",
        class_name="SecurityAgent",
    ),
    "documentation": AgentInfo(
        name="documentation",
        role="DOCUMENTATION",
        description="Documentation generation",
        capabilities=["docstrings", "readme", "api_docs"],
        module_path="jdev_cli.agents.documentation",
        class_name="DocumentationAgent",
    ),
    "performance": AgentInfo(
        name="performance",
        role="PERFORMANCE",
        description="Performance profiling and optimization",
        capabilities=["profile", "optimize", "benchmark"],
        module_path="jdev_cli.agents.performance",
        class_name="PerformanceAgent",
    ),
    "devops": AgentInfo(
        name="devops",
        role="DEVOPS",
        description="Infrastructure and deployment",
        capabilities=["docker", "kubernetes", "ci_cd"],
        module_path="jdev_cli.agents.devops_agent",
        class_name="DevOpsAgent",
    ),
    "justica": AgentInfo(
        name="justica",
        role="GOVERNANCE",
        description="Constitutional governance",
        capabilities=["evaluate", "approve", "block"],
        module_path="jdev_cli.agents.justica_agent",
        class_name="JusticaIntegratedAgent",
    ),
    "sofia": AgentInfo(
        name="sofia",
        role="COUNSELOR",
        description="Ethical counsel and wisdom",
        capabilities=["counsel", "ethics", "reflection"],
        module_path="jdev_cli.agents.sofia_agent",
        class_name="SofiaIntegratedAgent",
    ),
    "data": AgentInfo(
        name="data",
        role="DATABASE",
        description="Database optimization and analysis",
        capabilities=["schema_analysis", "query_optimization", "migration"],
        module_path="jdev_cli.agents.data_agent_production",
        class_name="DataAgent",
    ),
}


class AgentRouter:
    """
    Intelligent request router that detects user intent and routes to agents.

    Claude Code Parity: Implements automatic agent invocation like Claude Code's
    subagent system - users can naturally describe tasks and the router decides
    which specialized agent should handle it.

    Philosophy:
        "The user shouldn't need to know which agent does what - just ask."

    Routing Strategy:
        1. Keyword matching (fast, deterministic)
        2. Intent patterns (regex-based)
        3. Confidence scoring (multiple matches = ask user)
    """

    # Intent patterns → agent mapping with confidence weights
    # Enhanced for PT-BR and EN detection
    # v6.1: Added patterns for multi-plan, clarification, and exploration modes
    INTENT_PATTERNS: Dict[str, List[tuple]] = {
        "planner": [
            (r"\b(plan[oe]?|planeja[r]?|planejamento|cri[ae]\s*(um\s*)?plano)\b", 0.9),
            (r"\b(break\s*down|decompo[ns]|roadmap|estratégia)\b", 0.9),
            (r"\b(como\s*(fa[zç]o|implement|começ)|how\s*(to|do\s*i|should)|steps?\s*to)\b", 0.75),
            (r"\b(preciso\s*(de\s*)?(um\s*)?plano|help\s*me\s*(plan|with))\b", 0.8),
            (r"\bimplementa[rç].*passo\b", 0.85),
        ],
        # v6.1: Planner sub-modes (multi-plan, clarification, exploration)
        "planner:multi": [
            (r"\b(multi[- ]?plan|m[uú]ltiplos?\s*planos?|alternativ[ao]s?|3\s*planos?)\b", 0.95),
            (r"\b(compare\s*(multiple\s*)?plans?|compar[ae]\s*planos?|multiple\s*plans?)\b", 0.9),
            (r"\b(options?|op[çc][oõ]es|escolhas?|choices?)\b", 0.85),
            (r"\b(risk.*reward|risco.*recompensa|trade-?offs?)\b", 0.85),
            (r"\b(conservative|agressivo|creative|criativ[ao]|lateral)\b", 0.8),
        ],
        "planner:clarify": [
            (r"\b(clarif[iy]|esclare[çc][ae]|pergunt[ae]s?\s*(antes|primeiro))\b", 0.95),
            (r"\b(fa[çz]a\s*perguntas?|ask\s*(me\s*)?questions?)\b", 0.95),
            (r"\b(before\s*plan|antes\s*de\s*plan[ae]jar)\b", 0.9),
            (r"\b(need\s*more\s*info|preciso\s*mais\s*info)\b", 0.85),
        ],
        "planner:explore": [
            (r"\b(explor[ae]\s*(sem|without)\s*(modific|alter|mudar))\b", 0.95),
            (r"\b(read[- ]?only|somente\s*leitura|apenas\s*an[aá]lise)\b", 0.95),
            (r"\b(analys[ei]s?\s*only|s[oó]\s*an[aá]lise)\b", 0.9),
            (r"\b(don'?t\s*(change|modify)|n[aã]o\s*(mude|altere|modifique))\b", 0.85),
        ],
        "executor": [
            (r"\b(execut[ae]|run|roda[r]?|execute|bash|shell|terminal)\b", 0.9),
            (r"\b(comando?s?|command)\b", 0.75),
            (r"\b(pip\s+install|npm\s+(install|run)|make|cargo|go\s+(run|build))\b", 0.95),
            (r"\b(git\s+(status|diff|add|commit|push|pull|clone|log))\b", 0.9),
            (r"\b(pytest|unittest|jest|npm\s+test|testa[r]?\s+)\b", 0.85),
            (r"\b(delet[ae]|remov[ae]|apag[ae]|clean|limp[ae])\b", 0.85),  # DELETE/CLEAN → Executor
        ],
        "architect": [
            (r"\b(arquitetur[a]?|architect(ure)?|design\s*(pattern)?)\b", 0.9),
            (r"\b(estrutur[ae]|system\s*design|analisa[r]?\s*(a\s*)?arquitetura)\b", 0.85),
            (r"\b(diagrama?|uml|flowchart|fluxo(grama)?)\b", 0.85),
            (r"\b(clean\s*architect|hexagonal|onion|layered|microservice)\b", 0.95),
            (r"\b(trade-?off|decision|escolh[ae]\s*(entre|de\s*design))\b", 0.7),
        ],
        "reviewer": [
            (r"\b(review|revis[ae]|code\s*review)\b", 0.9),
            (r"\b(analys[ei]s?\s*(de\s*)?(c[oó]digo)?|análise)\b", 0.8),
            (r"\b(qualidade|quality|best\s*practice|boas\s*pr[aá]ticas)\b", 0.8),
            (r"\b(pr\s*review|pull\s*request|merge\s*request)\b", 0.95),
            (r"\b(code\s*smell|technical\s*debt|d[ií]vida\s*t[eé]cnica)\b", 0.85),
        ],
        "explorer": [
            (r"\b(explor[ae]|search|busc[ae]|find|encontr[ae]|localiz[ae])\b", 0.85),
            (r"\b(onde\s*(est[aá]|fica)|where\s*(is|are)|acha[re]?)\b", 0.8),
            (r"\b(naveg[ae]|codebase|estrutura\s*(do\s*)?(projeto|c[oó]digo))\b", 0.75),
            (r"\b(grep|ripgrep|ag\s|search\s*for|procur[ae])\b", 0.9),
        ],
        "refactorer": [
            (r"\b(refactor|refatora|refactoring|melhora[re]?\s*(o\s*)?(c[oó]digo)?)\b", 0.9),
            (r"\b(simplif[iy])\b", 0.7),  # Simplify code structure only
            (r"\b(extract|extrai|mover?\s*para|move\s*to)\b", 0.7),
            (r"\b(rename|renomea|dry|don'?t\s*repeat)\b", 0.8),
        ],
        "testing": [
            (r"\b(test[aes]?|testa[re]?|unittest|pytest|coverage|cobertura)\b", 0.9),
            (r"\b(tdd|bdd|test\s*driven|behavior\s*driven)\b", 0.95),
            (r"\b(mock|stub|fixture|parametriz[ae])\b", 0.85),
            (r"\b(integration\s*test|unit\s*test|e2e|end.to.end)\b", 0.9),
            (r"\b(unit[aá]rio|cria[r]?\s*testes?|write\s*tests?)\b", 0.9),
        ],
        "security": [
            (r"\b(security|seguran[çc]a|owasp|vulnerabil\w*|cve)\b", 0.95),
            (r"\b(injection|xss|csrf|sqli|auth[nz]?|exploit)\b", 0.9),
            (r"\b(audit|auditoria|pentest|penetration|scan)\b", 0.85),
            (r"\b(sanitiz|escap[ae]|valid[ae]|malware|trojan)\b", 0.75),
            (r"\bquais\s*(vulner|falh|brech)\w*", 0.9),
        ],
        "documentation": [
            (r"\b(document[ae]?|documenta[çc][aã]o|docs?|readme)\b", 0.9),
            (r"\b(docstring|jsdoc|pydoc|api\s*doc)\b", 0.95),
            (r"\b(coment[aá]rio|comment|explain|explic[ae])\b", 0.7),
            (r"\b(changelog|release\s*notes)\b", 0.85),
        ],
        "performance": [
            (r"\b(perform|performance|desempenho|otimiz[ae]|optim[iz])\b", 0.9),
            (r"\b(profil[ae]|profiling|benchmark|cprofile|perf)\b", 0.95),
            (r"\b(lento|slow|fast|r[aá]pido|speed\s*up|acelera)\b", 0.75),
            (r"\b(memory|mem[oó]ria|leak|cpu|io\s*bound)\b", 0.8),
        ],
        "devops": [
            (r"\b(devops|docker|kubernetes|k8s|ci\s*/?\s*cd|pipeline)\b", 0.95),
            (r"\b(deploy|implant[ae]|infra|terraform|ansible)\b", 0.9),
            (r"\b(container|imagem|image|pod|service)\b", 0.8),
            (r"\b(github\s*actions?|gitlab\s*ci|jenkins|circleci)\b", 0.95),
        ],
        "data": [
            (r"\b(database|banco\s*de\s*dados)\b", 0.9),
            (r"\b(sql|query|consulta)\b", 0.92),
            (r"\b(schema|esquema|migration|migra[çc][aã]o)\b", 0.85),
            (r"\b(orm|sqlalchemy|django\s*orm|prisma|sequelize)\b", 0.9),
            (r"\b(index|[ií]ndice|foreign\s*key|constraint)\b", 0.8),
            (r"\botimiza.*\b(query|sql|consulta)\b", 0.95),
        ],
        "justica": [
            (r"\b(justi[çc]a|governance|governan[çc]a|constitu[çi])\b", 0.95),
            (r"\b(compliance|conformidade|regulat[oó]rio)\b", 0.85),
            (r"\b(v[eé]rtice|article|artigo)\b", 0.7),
        ],
        "sofia": [
            (r"\b(sofia|counsel|conselho|[eé]tic[ao]|ethical|sabedoria|wisdom)\b", 0.95),
            (r"\b(filosof|philosophy|moral|virtue|virtude)\b", 0.85),
            (r"\b(socrat|dile[mn]ma|reflection|reflex[aã]o)\b", 0.8),
        ],
    }

    # Keywords that indicate NOT to route (general chat or direct tool use)
    NO_ROUTE_PATTERNS = [
        r"^(oi|ol[aá]|hi|hello|hey|e\s*a[ií])\b",  # Greetings
        r"^(obrigad[oa]|thanks?|valeu|vlw)\b",      # Thanks
        r"^(ok|certo|entend[io]|got\s*it)\b",      # Acknowledgments
        # File creation/save commands - should use tools directly, not route to agents
        r"\b(salv[ae]|save|cri[ae]|create|escrev[ae]|write)\s*(o[s]?\s*)?(arquivo|file)",
        r"\b(grav[ae]|persist|gravar)\s*(no\s*)?(disco|disk)",
        r"\bde\s*acordo\s*com\s*o\s*plano\b",  # "de acordo com o plano"
        r"\bseguindo\s*o\s*plano\b",  # "seguindo o plano"
        r"\bexecut[ae]\s*o\s*plano\b",  # "executa o plano"
        r"\bimplementa\s*(isso|o\s*plano)\b",  # "implementa isso/o plano"
        r"\bmaterializ[ae]\s*(isso)?\b",  # "materializa isso"
        r"^materializ",  # starts with materializa
        r"^agora\s*(salv|cri|faz|execut)",  # "agora salva/cria/faz"
        r"^(faz|fa[çc]a)\s*(isso|os?\s*arquivos?)",  # "faz isso", "faça os arquivos"
        # Code modification commands - should use tools directly
        r"^add\s+\w+.*\s+to\s+(the\s+)?(main|file|code)",  # "Add X to the main file"
        r"^(adiciona|inclui|coloca)\s+.*\s+(no|na|em)\s+",  # "adiciona X no arquivo"
        r"^(update|modify|change|alter)\s+(the\s+)?(file|code|main)",  # "update the file"
        r"^(atualiza|modifica|altera)\s+(o\s+)?(arquivo|código)",  # "atualiza o arquivo"
        r"\bmiddleware\b.*\b(to|no|na)\b",  # "middleware to..." - code addition
        r"^insert\s+",  # "insert ..."
        # Plan execution phrases - should use tools to create files, NOT executor agent
        r"^make\s+it\s+real",  # "make it real"
        r"^do\s+it\b",  # "do it"
        r"^build\s+it\b",  # "build it"
        r"^create\s+it\b",  # "create it"
        r"^(go|let'?s\s+go|vamos|bora)\b",  # "go", "let's go", "vamos", "bora"
        r"^(now|agora)\s+(create|build|make|do)",  # "now create/build/make"
        r"^proceed\b",  # "proceed"
        r"^(yes|sim|s[ií]|yep|yeah)\s*(,|\.|\!)?$",  # Simple confirmations
        r"^execute\s+(the\s+)?(plan|plano)",  # "execute the plan"
        r"^execute\s+\w+\s+plan",  # "execute neuro_api plan"
        r"^run\s+(the\s+)?(plan|plano)",  # "run the plan"
        r"^implement\s+(the\s+)?(plan|plano|it)",  # "implement the plan"
        r"^create\s+(the\s+)?files?",  # "create the files"
        r"^write\s+(the\s+)?files?",  # "write the files"
        r"^generate\s+(the\s+)?(code|files?)",  # "generate the code"
    ]

    MIN_CONFIDENCE = 0.7

    def __init__(self):
        self._compiled_patterns: Dict[str, List[tuple]] = {}
        self._no_route_patterns = [re.compile(p, re.IGNORECASE) for p in self.NO_ROUTE_PATTERNS]

        # Pre-compile all patterns
        for agent, patterns in self.INTENT_PATTERNS.items():
            self._compiled_patterns[agent] = [
                (re.compile(pattern, re.IGNORECASE), weight)
                for pattern, weight in patterns
            ]

    def should_route(self, message: str) -> bool:
        """Check if message should be considered for routing."""
        if len(message.strip()) < 5:
            return False

        for pattern in self._no_route_patterns:
            if pattern.search(message):
                return False

        return True

    def detect_intent(self, message: str) -> List[tuple]:
        """
        Detect which agent(s) should handle this message.

        Returns:
            List of (agent_name, confidence) tuples, sorted by confidence desc
        """
        if not self.should_route(message):
            return []

        scores: Dict[str, float] = {}

        for agent, patterns in self._compiled_patterns.items():
            max_score = 0.0
            for compiled_pattern, weight in patterns:
                if compiled_pattern.search(message):
                    max_score = max(max_score, weight)

            if max_score > 0:
                scores[agent] = max_score

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores

    def route(self, message: str) -> Optional[tuple]:
        """
        Route message to best agent.

        Returns:
            (agent_name, confidence) if confident routing found
            None if no clear routing (let LLM handle naturally)
        """
        intents = self.detect_intent(message)

        if not intents:
            return None

        best_agent, best_confidence = intents[0]

        if best_confidence >= self.MIN_CONFIDENCE:
            return (best_agent, best_confidence)

        return None

    def get_routing_suggestion(self, message: str) -> Optional[str]:
        """
        Get a suggestion message for ambiguous routing.

        Returns markdown message if multiple agents could handle this.
        """
        intents = self.detect_intent(message)

        high_conf = [(a, c) for a, c in intents if c >= 0.6]

        if len(high_conf) > 1:
            suggestions = [f"- `/{a}` ({int(c*100)}%)" for a, c in high_conf[:3]]
            return (
                "🤔 Multiple agents could help:\n" +
                "\n".join(suggestions) +
                "\n\nType one of the commands or ask naturally."
            )

        return None


class AgentManager:
    """
    Lazy-loading agent manager.

    Only imports agents when first used to keep startup fast.
    """

    def __init__(self, llm_client: Optional['GeminiClient'] = None):
        # Lazy import to avoid circular dependency
        if llm_client is None:
            from .llm_client import GeminiClient
            llm_client = GeminiClient()
        self.llm_client = llm_client
        self._agents: Dict[str, Any] = {}
        self._load_errors: Dict[str, str] = {}
        self.router = AgentRouter()
        self._last_plan: Optional[str] = None  # Store last plan for execution

    @property
    def available_agents(self) -> List[str]:
        """List of available agent names."""
        return list(AGENT_REGISTRY.keys())

    def get_agent_info(self, name: str) -> Optional[AgentInfo]:
        """Get agent metadata."""
        return AGENT_REGISTRY.get(name)

    def _normalize_streaming_chunk(self, chunk: Any) -> str:
        """
        Normalize streaming chunk from any agent protocol to displayable string.

        Handles multiple agent streaming protocols:
        1. StreamingChunk dataclass - New standard (preferred)
        2. Protocol A: {"content": "text"} - LLMAdapter style
        3. Protocol B: {"type": "thinking"/"status"/"result", "data": "text"} - Agent style
        4. Protocol C: tuple[str, Optional[AgentResponse]] - SofiaAgent style
        5. Plain string - Direct passthrough

        This unifies the streaming output from all agents to a single string format
        suitable for UI rendering.

        Args:
            chunk: Raw chunk from agent streaming

        Returns:
            String suitable for display/streaming to UI
        """
        # Case 0: StreamingChunk dataclass (new standard - preferred)
        # Uses duck typing to avoid import
        if hasattr(chunk, 'type') and hasattr(chunk, 'data') and hasattr(chunk, '__dataclass_fields__'):
            return str(chunk)  # StreamingChunk has __str__ method

        # Case 1: Already a string
        if isinstance(chunk, str):
            return chunk

        # Case 2: Tuple (SofiaAgent style) - (chunk_text, optional_response)
        if isinstance(chunk, tuple) and len(chunk) >= 1:
            return str(chunk[0]) if chunk[0] else ""

        # Case 3: Dict - multiple protocols
        if isinstance(chunk, dict):
            chunk_type = chunk.get('type', '')

            # Protocol A: {"content": "..."} - LLMAdapter
            if 'content' in chunk:
                return str(chunk['content'])

            # Protocol B: {"type": "...", "data": "..."} - Most agents
            if 'data' in chunk:
                data = chunk['data']

                # Skip certain types that are not for display
                if chunk_type == 'error':
                    error_data = data if isinstance(data, dict) else {'error': str(data)}
                    return f"❌ Error: {error_data.get('error', data)}\n"

                # Status messages - display with formatting
                if chunk_type == 'status':
                    return f"{data}\n"

                # Thinking tokens - display raw for streaming effect
                if chunk_type == 'thinking':
                    return str(data)

                # Command - display with syntax highlighting marker
                if chunk_type == 'command':
                    return f"\n```bash\n{data}\n```\n"

                # Executing - show status
                if chunk_type == 'executing':
                    return f"⚡ Executing: {data}\n"

                # Result - format appropriately (Claude Code style)
                if chunk_type == 'result':
                    # Extract the actual displayable content from result
                    result_data = data

                    # If it's an AgentResponse, get the inner data
                    if hasattr(data, 'data'):
                        result_data = data.data

                    # Now handle the result_data appropriately
                    if isinstance(result_data, dict):
                        # Priority 1: formatted_markdown (PlannerAgent style)
                        if 'formatted_markdown' in result_data:
                            return result_data['formatted_markdown']

                        # Priority 2: markdown field
                        if 'markdown' in result_data:
                            return result_data['markdown']

                        # Priority 3: response/result text
                        if 'response' in result_data:
                            return str(result_data['response'])
                        if 'result' in result_data:
                            return str(result_data['result'])

                        # Priority 4: stdout for executor results
                        if 'stdout' in result_data:
                            output_parts = []
                            if result_data.get('command'):
                                output_parts.append(f"$ {result_data['command']}")
                            if result_data.get('stdout'):
                                output_parts.append(result_data['stdout'])
                            if result_data.get('stderr'):
                                output_parts.append(f"stderr: {result_data['stderr']}")
                            return '\n'.join(output_parts) if output_parts else ""

                        # Priority 5: Don't dump raw dicts - return empty or summary
                        # This prevents ugly dict dumps in the UI
                        return ""

                    elif hasattr(result_data, 'to_markdown'):
                        return result_data.to_markdown()

                    return str(result_data) if result_data else ""

                # Other types with data - just return data as string
                return str(data)

            # Protocol C: {"type": "...", "text": "..."} - Legacy executor
            if 'text' in chunk:
                return str(chunk['text'])

            # Fallback: stringify the whole dict (shouldn't happen with proper protocol)
            # Log warning in production
            return ""  # Silent fallback - don't dump raw dicts

        # Case 4: Has common attributes
        if hasattr(chunk, 'data'):
            return str(chunk.data)
        if hasattr(chunk, 'content'):
            return str(chunk.content)
        if hasattr(chunk, 'to_markdown'):
            return chunk.to_markdown()

        # Last resort: stringify
        return str(chunk) if chunk else ""

    async def get_agent(self, name: str) -> Optional[Any]:
        """
        Get or create agent instance.

        Lazy loads the agent module on first use.
        Uses inspect.signature() to detect constructor parameters and pass appropriate args.
        """
        if name in self._agents:
            return self._agents[name]

        if name in self._load_errors:
            return None

        info = AGENT_REGISTRY.get(name)
        if not info:
            self._load_errors[name] = f"Unknown agent: {name}"
            return None

        try:
            # Dynamic import
            import importlib
            module = importlib.import_module(info.module_path)
            agent_class = getattr(module, info.class_name)

            # FIX CRÍTICO: Detectar assinatura do __init__ e passar parâmetros corretos
            sig = inspect.signature(agent_class.__init__)
            params = sig.parameters

            init_kwargs: Dict[str, Any] = {}
            if 'llm_client' in params:
                init_kwargs['llm_client'] = self.llm_client
            if 'mcp_client' in params:
                init_kwargs['mcp_client'] = None
            if 'model' in params:
                init_kwargs['model'] = self.llm_client

            agent = agent_class(**init_kwargs)
            self._agents[name] = agent
            return agent

        except ImportError as e:
            self._load_errors[name] = f"Import error: {e}"
            return None
        except Exception as e:
            self._load_errors[name] = f"Init error: {e}"
            return None

    async def invoke_agent(
        self,
        name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Invoke an agent and stream response.

        Falls back to LLM if agent unavailable.
        """
        agent = await self.get_agent(name)

        if agent is None:
            # Fallback: use LLM directly with agent-specific prompt
            info = AGENT_REGISTRY.get(name)
            if info:
                system_prompt = f"You are a {info.role}. {info.description}. Capabilities: {', '.join(info.capabilities)}."
                async for chunk in self.llm_client.stream(task, system_prompt):
                    yield chunk
            else:
                yield f"❌ Agent '{name}' not available"
            return

        # FIX CRÍTICO: Criar AgentTask corretamente
        from jdev_core import AgentTask
        agent_task = AgentTask(request=task, context=context or {})

        # Track plan output for later execution
        plan_chunks = [] if name == "planner" else None

        # Try streaming interface first
        if hasattr(agent, 'execute_streaming'):
            try:
                # Detectar assinatura de execute_streaming
                sig = inspect.signature(agent.execute_streaming)
                param_count = len([p for p in sig.parameters.values()
                                   if p.default == inspect.Parameter.empty])

                if param_count == 1:  # Apenas task (AgentTask)
                    async for chunk in agent.execute_streaming(agent_task):
                        normalized = self._normalize_streaming_chunk(chunk)
                        if plan_chunks is not None:
                            plan_chunks.append(normalized)
                        yield normalized
                else:  # task + context (str, dict)
                    async for chunk in agent.execute_streaming(task, context or {}):
                        normalized = self._normalize_streaming_chunk(chunk)
                        if plan_chunks is not None:
                            plan_chunks.append(normalized)
                        yield normalized

                # Save plan for later execution
                if plan_chunks:
                    plan_text = "".join(plan_chunks)
                    self._last_plan = plan_text
                    # Log that plan was saved
                    yield f"\n💾 *Plan saved. Say 'create the files' or 'make it real' to execute.*\n"
                return
            except Exception as e:
                yield f"⚠️ Streaming failed: {e}\n"

        # Fallback to sync execute
        if hasattr(agent, 'execute'):
            try:
                result = await agent.execute(agent_task)
                # Format AgentResponse nicely instead of dumping raw dict
                if hasattr(result, 'data') and hasattr(result, 'reasoning'):
                    # This is an AgentResponse - format it properly
                    data = result.data
                    reasoning = result.reasoning

                    # For ArchitectAgent decisions, format nicely
                    if isinstance(data, dict) and 'decision' in data:
                        decision = data.get('decision', 'UNKNOWN')
                        emoji = "✅" if decision == "APPROVED" else "❌"
                        yield f"{emoji} **{decision}**\n\n"
                        yield f"*{reasoning}*\n"

                        # Show architecture details if available
                        arch = data.get('architecture', {})
                        if arch.get('approach'):
                            yield f"\n**Approach:** {arch['approach']}\n"
                        if arch.get('risks'):
                            yield f"\n**Risks:** {', '.join(arch['risks'])}\n"
                        if arch.get('estimated_complexity'):
                            yield f"\n**Complexity:** {arch['estimated_complexity']}\n"
                        if data.get('recommendations'):
                            yield f"\n**Recommendations:**\n"
                            for rec in data['recommendations']:
                                yield f"- {rec}\n"
                    # ExplorerAgent results
                    elif isinstance(data, dict) and 'relevant_files' in data:
                        if data.get('context_summary'):
                            yield f"{data['context_summary']}\n\n"
                        relevant_files = data.get('relevant_files', [])
                        if relevant_files:
                            yield "**Relevant Files:**\n"
                            for f in relevant_files:
                                # Handle both dict format and string format
                                if isinstance(f, dict):
                                    path = f.get('path', 'unknown')
                                    relevance = f.get('relevance', '')
                                    reason = f.get('reason', '')
                                    relevance_badge = f" [{relevance}]" if relevance else ""
                                    reason_text = f" - {reason}" if reason else ""
                                    yield f"- `{path}`{relevance_badge}{reason_text}\n"
                                else:
                                    yield f"- `{f}`\n"
                        else:
                            yield "⚠️ No relevant files found for this query.\n"
                        if data.get('dependencies'):
                            yield "\n**Dependencies:**\n"
                            for d in data['dependencies']:
                                if isinstance(d, dict):
                                    from_file = d.get('from', '')
                                    to_file = d.get('to', '')
                                    dep_type = d.get('type', '')
                                    yield f"- `{from_file}` → `{to_file}` ({dep_type})\n"
                                else:
                                    yield f"- {d}\n"
                        if data.get('token_estimate'):
                            yield f"\n📊 *Token estimate: ~{data['token_estimate']} tokens*\n"
                    elif isinstance(data, dict) and 'formatted_markdown' in data:
                        yield data['formatted_markdown']
                    elif isinstance(data, dict) and 'markdown' in data:
                        yield data['markdown']
                    elif isinstance(data, str):
                        yield data
                    else:
                        # Generic: show reasoning if available
                        if reasoning and reasoning != "None":
                            yield f"{reasoning}\n"
                elif hasattr(result, 'data'):
                    data = result.data
                    if isinstance(data, str):
                        yield data
                    elif isinstance(data, dict) and 'formatted_markdown' in data:
                        yield data['formatted_markdown']
                    else:
                        yield str(data)
                elif hasattr(result, 'result'):
                    yield str(result.result)
                else:
                    yield str(result)
                return
            except Exception as e:
                yield f"❌ Agent error: {e}"
                return

        yield f"❌ Agent '{name}' has no execute method"

    # =========================================================================
    # PLANNER v6.1 SPECIFIC METHODS
    # =========================================================================

    async def invoke_planner_multi(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Invoke planner with Multi-Plan Generation (v6.1).

        Generates 3 alternative plans with different strategies:
        - STANDARD: Conservative, low-risk approach
        - ACCELERATOR: Fast execution, higher risk
        - LATERAL: Creative, unconventional approach

        Each plan includes probability estimates (P(Success), P(Friction), etc.)
        based on Zhang et al. 2025 Verbalized Sampling.
        """
        agent = await self.get_agent("planner")

        if agent is None:
            yield "❌ Planner agent not available"
            return

        if not hasattr(agent, 'generate_multi_plan'):
            yield "⚠️ Planner doesn't support multi-plan (requires v6.1+)\n"
            # Fallback to regular planning
            async for chunk in self.invoke_agent("planner", task, context):
                yield chunk
            return

        try:
            from jdev_core import AgentTask
            agent_task = AgentTask(request=task, context=context or {})

            yield "🎯 **Generating 3 Alternative Plans...**\n\n"

            # Generate multi-plan
            result = await agent.generate_multi_plan(agent_task)

            # Stream the markdown output
            yield result.to_markdown()

        except Exception as e:
            yield f"❌ Multi-plan generation failed: {e}"

    async def invoke_planner_clarify(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Invoke planner with Clarification Mode (v6.1).

        Before planning, the agent asks 2-3 clarifying questions
        to better understand requirements (Cursor 2.1 pattern).
        """
        agent = await self.get_agent("planner")

        if agent is None:
            yield "❌ Planner agent not available"
            return

        if not hasattr(agent, 'generate_clarifying_questions'):
            yield "⚠️ Planner doesn't support clarification (requires v6.1+)\n"
            async for chunk in self.invoke_agent("planner", task, context):
                yield chunk
            return

        try:
            from jdev_core import AgentTask
            agent_task = AgentTask(request=task, context=context or {})

            yield "🤔 **Analyzing your request...**\n\n"

            # Generate clarifying questions
            questions = await agent.generate_clarifying_questions(agent_task)

            if questions:
                yield "Before I create a plan, I have some questions:\n\n"
                for i, q in enumerate(questions, 1):
                    yield f"**{i}.** {q.question}\n"
                    if q.options:
                        for opt in q.options:
                            yield f"   - {opt}\n"
                    yield "\n"
                yield "\n💡 *Answer these questions, then run `/plan` again with the context.*\n"
            else:
                yield "✅ No clarification needed. Proceeding with planning...\n\n"
                # Proceed with regular planning
                async for chunk in self.invoke_agent("planner", task, context):
                    yield chunk

        except Exception as e:
            yield f"❌ Clarification failed: {e}"

    async def invoke_planner_explore(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Invoke planner in Exploration Mode (v6.1).

        Read-only analysis mode - gathers context and analyzes
        without proposing modifications (Claude Plan Mode pattern).
        """
        agent = await self.get_agent("planner")

        if agent is None:
            yield "❌ Planner agent not available"
            return

        if not hasattr(agent, 'explore'):
            yield "⚠️ Planner doesn't support exploration (requires v6.1+)\n"
            async for chunk in self.invoke_agent("planner", task, context):
                yield chunk
            return

        try:
            from jdev_core import AgentTask
            agent_task = AgentTask(request=task, context=context or {})

            yield "🔍 **Exploration Mode (Read-Only)**\n\n"
            yield "_No modifications will be made - analysis only._\n\n"

            # Run exploration
            result = await agent.explore(agent_task)

            if result.success:
                exploration = result.data.get('exploration', {})

                # Format exploration results
                if 'files_analyzed' in exploration:
                    yield f"**📁 Files Analyzed:** {exploration['files_analyzed']}\n\n"

                if 'key_findings' in exploration:
                    yield "**🔑 Key Findings:**\n"
                    for finding in exploration['key_findings']:
                        yield f"- {finding}\n"
                    yield "\n"

                if 'dependencies' in exploration:
                    yield "**🔗 Dependencies:**\n"
                    for dep in exploration['dependencies'][:10]:
                        yield f"- {dep}\n"
                    yield "\n"

                if 'recommendations' in exploration:
                    yield "**💡 Recommendations:**\n"
                    for rec in exploration['recommendations']:
                        yield f"- {rec}\n"
                    yield "\n"

                yield "\n✅ *Exploration complete. Use `/plan` to create an execution plan.*\n"
            else:
                yield f"❌ Exploration failed: {result.error}\n"

        except Exception as e:
            yield f"❌ Exploration failed: {e}"

    def detect_planner_mode(self, message: str) -> Optional[str]:
        """
        Detect which planner mode should be used based on message content.

        Returns:
            "multi" | "clarify" | "explore" | None (regular planning)
        """
        # Check for sub-mode patterns
        for mode in ["planner:multi", "planner:clarify", "planner:explore"]:
            patterns = self.router._compiled_patterns.get(mode, [])
            for compiled_pattern, weight in patterns:
                if compiled_pattern.search(message) and weight >= 0.85:
                    return mode.split(":")[1]  # Return "multi", "clarify", or "explore"

        return None


__all__ = [
    'AgentInfo',
    'AGENT_REGISTRY',
    'AgentRouter',
    'AgentManager',
]
