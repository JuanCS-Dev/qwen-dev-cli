# 🔧 INTEGRATION MASTER PLAN - QWEN-DEV-CLI
> **Plano Detalhado de Integração: Conectando Features Existentes**  
> **Data:** 2025-11-20 18:00 UTC  
> **Baseline:** 32% parity (Grade D+)  
> **Target:** 80% parity (Grade B) em 4 semanas  
> **Método:** Integration-First (não construir, conectar)

---

## 📊 SITUAÇÃO ATUAL (Baseline)

### **Descoberta Crítica:**
- ✅ **Código existe:** 33.446 linhas, 21 componentes TUI
- ✅ **Testes passam:** 96.3% coverage, 1002 tests
- ❌ **Features offline:** 67% dos componentes não integrados
- ❌ **Usuário não vê:** 80% das features implementadas

### **Componentes Offline (Desperdiçados):**
```
qwen_dev_cli/tui/components/
├── palette.py (300 linhas)         ❌ Command Palette Ctrl+K
├── preview.py (400 linhas)         ❌ Inline diff preview
├── dashboard.py (200 linhas)       ❌ Real-time dashboard
├── workflow_visualizer.py (700)    ⚠️ Importado mas não usado
├── context_awareness.py (528)      ❌ Token tracking (DAY 8!)
├── markdown_enhanced.py            ❌ Enhanced markdown
└── animations.py (200 linhas)      ❌ Smooth animations
```

### **Parity Real vs. Claimed:**
| Categoria | Claimed | Real | Gap |
|-----------|---------|------|-----|
| Core | 100% | 100% ✅ | 0 |
| UX | 100% | **5%** 🔴 | -95% |
| Tools | 80% | 23% 🔴 | -57% |
| Advanced | 50% | 0% 🔴 | -50% |
| **Overall** | **88%** | **32%** 🔴 | **-56%** |

---

## 🎯 ESTRATÉGIA DE INTEGRAÇÃO

### **Princípio:** Integration-First, Not Build-First

**OLD Approach (ERRADO):**
1. Build new features
2. Test in isolation
3. Hope they work together
4. Result: Code grows, integration lags

**NEW Approach (CORRETO):**
1. Audit existing code (✅ DONE)
2. **Connect offline features FIRST**
3. Test with real usage
4. Build only what's truly missing
5. Result: Fast progress, real impact

### **Roadmap Overview:**
```
Week 1 (20h): INTEGRATION SPRINT → 32% → 55% (+23 points) 🔴 CRITICAL
Week 2 (20h): Dogfooding + Tools → 55% → 65% (+10 points) 🟡 HIGH
Week 3 (20h): Polish + LSP Basic → 65% → 72% (+7 points) 🟢 MEDIUM
Week 4 (20h): Semantic Search + Refactoring → 72% → 80% (+8 points) 🟢 MEDIUM
```

**Total:** 80h to reach 80% parity (Grade B)

---

## 📅 WEEK 1: INTEGRATION SPRINT (20h)

**Goal:** Connect existing features → 32% to 55% parity

### **DAY 1 (4h): Command Palette & Token Tracking**

#### **Task 1.1: Command Palette Integration (2h)**

**Objetivo:** Fazer Ctrl+K funcionar

**Files to Modify:**
1. `qwen_dev_cli/shell.py`
2. `qwen_dev_cli/tui/input_enhanced.py`

**Implementation Steps:**

**Step 1.1.1: Add Keybinding Handler (30min)**
```python
# File: qwen_dev_cli/tui/input_enhanced.py
# Add after line 156 (in __init__)

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

self.kb = KeyBindings()

@self.kb.add('c-k')  # Ctrl+K
async def _(event):
    """Open command palette"""
    # Signal to shell to open palette
    event.app.exit(result="__PALETTE__")

# Update PromptSession with key_bindings
self.session: PromptSession[str] = PromptSession(
    # ... existing params ...
    key_bindings=self.kb,  # ADD THIS
)
```

**Step 1.1.2: Handle Palette in Shell Loop (1h)**
```python
# File: qwen_dev_cli/shell.py
# Add after line 947 (in async def run)

# At top of file, add import:
from .tui.components.palette import create_default_palette, CommandPalette

# In __init__ (line ~176), add:
self.palette = create_default_palette()
self._register_palette_commands()  # New method

# New method after __init__:
def _register_palette_commands(self):
    """Register commands in palette"""
    from .tui.components.palette import Command, CommandCategory
    
    # File commands
    self.palette.add_command(Command(
        id="file.read",
        title="Read File",
        description="Read file contents",
        category=CommandCategory.FILE,
        keywords=["open", "cat", "view"],
        action=lambda: self._prompt_and_read_file()
    ))
    
    self.palette.add_command(Command(
        id="file.edit",
        title="Edit File",
        description="Edit file with AI",
        category=CommandCategory.EDIT,
        keywords=["modify", "change", "update"],
        action=lambda: self._prompt_and_edit_file()
    ))
    
    # Git commands
    self.palette.add_command(Command(
        id="git.status",
        title="Git Status",
        description="Show git status",
        category=CommandCategory.GIT,
        keywords=["git", "status", "changes"],
        action=lambda: self._run_git_status()
    ))
    
    # Add 10-15 more commands...
    # (Full list in implementation)

# In async def run() loop (after line 969):
user_input = await self.enhanced_input.prompt_async()

# ADD THIS CHECK:
if user_input == "__PALETTE__":
    # Palette triggered via Ctrl+K
    self.console.print("\n[cyan]Opening command palette...[/cyan]")
    
    # Show palette (interactive)
    selected = await self._show_palette_interactive()
    
    if selected:
        # Execute selected command
        try:
            await selected.action()
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
    continue

# New async method:
async def _show_palette_interactive(self) -> Optional[Command]:
    """Show interactive palette and return selected command"""
    from prompt_toolkit.shortcuts import radiolist_dialog
    from .tui.components.palette import Command
    
    # Search loop
    while True:
        query = await self.enhanced_input.prompt_async(
            prompt="Search commands: ",
            placeholder="Type to search..."
        )
        
        if not query:
            return None
        
        # Fuzzy search
        results = self.palette.search(query, limit=10)
        
        if not results:
            self.console.print("[yellow]No commands found[/yellow]")
            continue
        
        # Show results
        choices = [
            (cmd.id, f"{cmd.title} - {cmd.description}")
            for cmd in results
        ]
        
        # Let user select
        selected_id = await radiolist_dialog(
            title="Select Command",
            values=choices
        ).run_async()
        
        if selected_id:
            return self.palette.get_command(selected_id)
```

**Step 1.1.3: Test (30min)**
```bash
# Test 1: Ctrl+K opens palette
$ qwen-dev
> (press Ctrl+K)
# Expected: "Opening command palette..."

# Test 2: Search works
Search commands: read
# Expected: Shows "Read File" option

# Test 3: Execute works
(select "Git Status")
# Expected: Runs git status command
```

**Acceptance Criteria:**
- [ ] Ctrl+K opens palette
- [ ] Fuzzy search works (score >0.5 for matches)
- [ ] Execute command runs action
- [ ] Palette shows categories
- [ ] Recent commands shown first
- [ ] ESC cancels palette

---

#### **Task 1.2: Token Tracking Integration (2h)**

**Objetivo:** Mostrar uso de tokens em tempo real

**Files to Modify:**
1. `qwen_dev_cli/shell.py`
2. `qwen_dev_cli/core/llm.py`

**Implementation Steps:**

**Step 1.2.1: Initialize Context Engine (15min)**
```python
# File: qwen_dev_cli/shell.py
# In __init__ (after line 176)

from .tui.components.context_awareness import ContextAwarenessEngine

self.context_engine = ContextAwarenessEngine(
    max_context_tokens=100_000,  # 100k token window
    console=self.console
)
```

**Step 1.2.2: Hook into LLM Streaming (45min)**
```python
# File: qwen_dev_cli/core/llm.py
# Find the streaming loop (around line 200-250)

# ADD THIS: Track streaming tokens
async for chunk in response:
    content = chunk.get("content", "")
    if content:
        yield content
        
        # NEW: Track tokens in real-time
        token_count = len(content.split())  # Rough estimate
        if hasattr(self, 'context_engine'):
            self.context_engine.update_streaming_tokens(token_count)

# After streaming completes:
# NEW: Finalize session
if hasattr(self, 'context_engine'):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost = self._estimate_cost(input_tokens, output_tokens)
    
    self.context_engine.finalize_streaming_session(
        final_input_tokens=input_tokens,
        final_output_tokens=output_tokens,
        cost_estimate=cost
    )
```

**Step 1.2.3: Display Token Usage (30min)**
```python
# File: qwen_dev_cli/shell.py
# In async def run() loop, after LLM response completes

# ADD THIS: Show token usage after each response
if self.context_engine.window.current_output_tokens > 0:
    token_panel = self.context_engine.render_token_usage_realtime()
    self.console.print(token_panel)
    
    # Warning if approaching limit
    if self.context_engine.window.is_critical:
        self.console.print(
            "\n[bold red]⚠️  WARNING: Context window >90% full![/bold red]"
        )
        self.console.print(
            "[yellow]Consider using /clear to reset context[/yellow]\n"
        )
```

**Step 1.2.4: Add /tokens Command (15min)**
```python
# File: qwen_dev_cli/shell.py
# In _handle_system_command() method

elif command == "/tokens":
    # Show detailed token usage
    panel = self.context_engine.render_token_usage_realtime()
    self.console.print(panel)
    
    # Show history
    if self.context_engine.window.usage_history:
        history_table = Table(title="Token Usage History")
        history_table.add_column("Time", style="cyan")
        history_table.add_column("Input", justify="right")
        history_table.add_column("Output", justify="right")
        history_table.add_column("Total", justify="right")
        history_table.add_column("Cost", justify="right")
        
        for snapshot in list(self.context_engine.window.usage_history)[-10:]:
            history_table.add_row(
                snapshot.timestamp.strftime("%H:%M:%S"),
                f"{snapshot.input_tokens:,}",
                f"{snapshot.output_tokens:,}",
                f"{snapshot.total_tokens:,}",
                f"${snapshot.cost_estimate_usd:.4f}"
            )
        
        self.console.print(history_table)
    
    return False, None
```

**Step 1.2.5: Test (15min)**
```bash
# Test 1: Real-time counter during streaming
$ qwen-dev
> explain this code
# Expected: See "🔄 Streaming: 45 tokens" during response

# Test 2: Token panel after response
# Expected: Shows:
#   Input:  1,234 tokens
#   Output: 567 tokens
#   Total:  1,801 tokens

# Test 3: /tokens command
> /tokens
# Expected: Shows detailed history (last 10 interactions)

# Test 4: Warning when >90%
# (use large context)
# Expected: "⚠️  WARNING: Context window >90% full!"
```

**Acceptance Criteria:**
- [ ] Streaming counter shows during LLM generation
- [ ] Token panel shows after response
- [ ] /tokens command works
- [ ] Warnings at 80% and 90%
- [ ] Cost estimation accurate (±10%)
- [ ] History persists across sessions

---

### **DAY 2 (4h): Inline Preview & Workflow Visualizer**

#### **Task 1.3: Inline Preview Integration (2h 30min)**

**Objetivo:** Mostrar preview antes de aplicar mudanças em arquivos

**Files to Modify:**
1. `qwen_dev_cli/tools/file_ops.py` (WriteFileTool, EditFileTool)
2. `qwen_dev_cli/shell.py`

**Implementation Steps:**

**Step 1.3.1: Add Preview Hook in WriteFileTool (45min)**
```python
# File: qwen_dev_cli/tools/file_ops.py
# In WriteFileTool.execute() method

from ..tui.components.preview import EditPreview, DiffHunk
from pathlib import Path

async def execute(self, path: str, content: str, **kwargs) -> ToolResult:
    """Write content to file with preview"""
    
    # Check if file exists
    file_path = Path(path)
    show_preview = kwargs.get("preview", True)
    
    if file_path.exists() and show_preview:
        # Read existing content
        with open(file_path, 'r') as f:
            original = f.read()
        
        # Create preview
        preview = EditPreview()
        accepted = await preview.show_diff_interactive(
            original_content=original,
            proposed_content=content,
            file_path=str(file_path),
            console=kwargs.get("console")  # Pass console from shell
        )
        
        if not accepted:
            return ToolResult(
                success=False,
                data={"path": path},
                message="Edit cancelled by user"
            )
    
    # If accepted (or new file), write
    with open(file_path, 'w') as f:
        f.write(content)
    
    return ToolResult(
        success=True,
        data={"path": path, "size": len(content)},
        message=f"File written: {path}"
    )
```

**Step 1.3.2: Add Interactive Preview Method (45min)**
```python
# File: qwen_dev_cli/tui/components/preview.py
# Add new method to EditPreview class

async def show_diff_interactive(
    self,
    original_content: str,
    proposed_content: str,
    file_path: str,
    console: Console
) -> bool:
    """
    Show interactive diff and ask user to accept/reject
    
    Returns:
        True if user accepts, False if rejects
    """
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.syntax import Syntax
    from prompt_toolkit.shortcuts import yes_no_dialog
    
    # Generate diff
    diff_panel = self.render_side_by_side_diff(
        original_content,
        proposed_content,
        file_path
    )
    
    # Show diff
    console.print(Panel(
        diff_panel,
        title=f"[bold cyan]Preview: {file_path}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Show stats
    stats = self._calculate_diff_stats(original_content, proposed_content)
    console.print(
        f"\n[green]+{stats['added']} lines[/green] "
        f"[red]-{stats['removed']} lines[/red] "
        f"[yellow]~{stats['modified']} lines[/yellow]\n"
    )
    
    # Ask user
    result = await yes_no_dialog(
        title="Accept Changes?",
        text="Do you want to apply these changes to the file?"
    ).run_async()
    
    return result if result is not None else False
```

**Step 1.3.3: Pass Console to Tools (30min)**
```python
# File: qwen_dev_cli/shell.py
# In _process_request_with_llm() method (around line 600-700)

# When calling tools, pass console:
for tool_call in tool_calls:
    tool = self.registry.get(tool_call["name"])
    args = tool_call["arguments"]
    
    # ADD THIS: Pass console for preview
    args["console"] = self.console
    args["preview"] = True  # Enable preview by default
    
    result = await self._execute_with_recovery(
        tool, tool_call["name"], args, turn
    )
```

**Step 1.3.4: Add /nopreview Mode (15min)**
```python
# File: qwen_dev_cli/shell.py
# In SessionContext class (line ~100)

class SessionContext:
    def __init__(self):
        # ... existing ...
        self.preview_enabled = True  # NEW: Default to True

# In _handle_system_command():
elif command == "/nopreview":
    self.context.preview_enabled = False
    return False, "[yellow]Preview disabled. Files will be written directly.[/yellow]"

elif command == "/preview":
    self.context.preview_enabled = True
    return False, "[green]Preview enabled.[/green]"

# Update tool call args:
args["preview"] = self.context.preview_enabled
```

**Step 1.3.5: Test (15min)**
```bash
# Test 1: Preview shows for existing file
$ qwen-dev
> edit file.py to add docstring
# Expected: Shows side-by-side diff, asks "Accept Changes?"

# Test 2: Accept works
(select Yes)
# Expected: File is modified

# Test 3: Reject works
(select No)
# Expected: File NOT modified, message "Edit cancelled by user"

# Test 4: /nopreview disables
> /nopreview
> edit file.py
# Expected: No preview, writes directly

# Test 5: New file no preview
> create newfile.py with content
# Expected: No preview (new file), writes directly
```

**Acceptance Criteria:**
- [ ] Preview shows for existing files
- [ ] Side-by-side diff is readable
- [ ] Accept applies changes
- [ ] Reject cancels (file unchanged)
- [ ] /nopreview disables preview
- [ ] New files skip preview
- [ ] Syntax highlighting in diff

---

#### **Task 1.4: Workflow Visualizer Integration (1h 30min)**

**Objetivo:** Mostrar progresso visual durante operações complexas

**Files to Modify:**
1. `qwen_dev_cli/shell.py`

**Implementation Steps:**

**Step 1.4.1: Add Workflow Steps (30min)**
```python
# File: qwen_dev_cli/shell.py
# In async def run() main loop (line 947+)

# After user input, before LLM call:
# ADD THIS: Initialize workflow
self.workflow_viz.add_step(
    "parse_input",
    "Analyzing request",
    dependencies=[]
)
self.workflow_viz.update_step(
    "parse_input",
    status=StepStatus.RUNNING
)

# Analyze what tools might be needed
suggestion = suggestion_engine.analyze(user_input)
self.workflow_viz.update_step(
    "parse_input",
    status=StepStatus.COMPLETED,
    progress=1.0
)

# Add LLM step
self.workflow_viz.add_step(
    "llm_call",
    f"Calling {self.llm_client.provider} LLM",
    dependencies=["parse_input"]
)
self.workflow_viz.update_step("llm_call", status=StepStatus.RUNNING)

# During LLM streaming:
for chunk in stream:
    # Update progress based on tokens
    progress = min(1.0, token_count / estimated_total)
    self.workflow_viz.update_step(
        "llm_call",
        progress=progress
    )

# After LLM completes:
self.workflow_viz.update_step(
    "llm_call",
    status=StepStatus.COMPLETED,
    progress=1.0
)

# For each tool call:
for tool_call in tool_calls:
    step_id = f"tool_{tool_call['name']}_{i}"
    self.workflow_viz.add_step(
        step_id,
        f"Executing: {tool_call['name']}",
        dependencies=["llm_call"]
    )
    self.workflow_viz.update_step(step_id, status=StepStatus.RUNNING)
    
    # Execute tool
    result = await tool.execute(**args)
    
    # Update status
    if result.success:
        self.workflow_viz.update_step(
            step_id,
            status=StepStatus.COMPLETED,
            progress=1.0
        )
    else:
        self.workflow_viz.update_step(
            step_id,
            status=StepStatus.FAILED,
            error=result.message
        )
```

**Step 1.4.2: Display Workflow (30min)**
```python
# File: qwen_dev_cli/shell.py

# Option 1: Live display (blocks until completion)
async def _process_with_workflow(self, ...):
    with self.workflow_viz.live_display(target_fps=60) as live:
        # ... process steps ...
        live.update(self.workflow_viz.render_full_view())

# Option 2: Summary after completion
async def _process_with_workflow(self, ...):
    # ... process steps ...
    
    # Show summary
    metrics = self.workflow_viz.get_metrics()
    self.console.print(
        f"\n[cyan]Workflow completed in {metrics['total_duration']:.2f}s[/cyan]"
    )
    self.console.print(f"  Steps: {metrics['completed']}/{metrics['total']}")
    
    if metrics['failed'] > 0:
        self.console.print(f"  [red]Failed: {metrics['failed']}[/red]")
```

**Step 1.4.3: Add /workflow Command (15min)**
```python
# In _handle_system_command():
elif command == "/workflow":
    # Show current workflow state
    panel = self.workflow_viz.render_full_view()
    self.console.print(panel)
    
    # Show metrics
    metrics = self.workflow_viz.get_performance_metrics()
    self.console.print(f"\nPerformance:")
    self.console.print(f"  FPS: {metrics['current_fps']:.1f}")
    self.console.print(f"  Render time: {metrics['last_frame_time_ms']:.2f}ms")
    
    return False, None
```

**Step 1.4.4: Test (15min)**
```bash
# Test 1: Workflow shows during operation
$ qwen-dev
> read file.py and summarize
# Expected: Shows:
#   ✓ Analyzing request
#   ⟳ Calling Qwen LLM (45%)
#   ○ Executing: read_file (waiting)

# Test 2: Metrics correct
# Expected after completion:
#   Workflow completed in 3.45s
#   Steps: 3/3
#   FPS: 7612

# Test 3: /workflow command
> /workflow
# Expected: Shows current workflow state + metrics
```

**Acceptance Criteria:**
- [ ] Workflow shows during operations
- [ ] Progress accurate (based on tokens/steps)
- [ ] Failed steps marked red
- [ ] Completed steps marked green
- [ ] Metrics show (duration, FPS)
- [ ] /workflow command works

---

### **DAY 3 (4h): Animations & Dashboard**

#### **Task 1.5: Animations Integration (2h)**

**Objetivo:** Substituir prints estáticos por animações suaves

**Files to Modify:**
1. `qwen_dev_cli/shell.py`
2. `qwen_dev_cli/tui/components/status.py`

**Implementation Steps:**

**Step 1.5.1: Replace Static Prints (1h)**
```python
# File: qwen_dev_cli/shell.py
# Import animator
from .tui.animations import smooth_animator, Animator, AnimationConfig

# Initialize animator in __init__:
self.animator = Animator(AnimationConfig(
    duration=0.3,
    easing="ease-out",
    fps=60
))

# REPLACE all console.print with animated versions:

# OLD:
self.console.print("[cyan]Processing...[/cyan]")

# NEW:
await self._print_animated(
    "[cyan]Processing...[/cyan]",
    animation="fade_in"
)

# Add helper method:
async def _print_animated(
    self,
    text: str,
    animation: str = "fade_in"
):
    """Print with animation"""
    if animation == "fade_in":
        # Fade in from 0 to 1 opacity
        def update(opacity):
            # Rich doesn't support opacity, but we can simulate
            # by changing brightness
            if opacity < 0.3:
                style = "dim"
            elif opacity < 0.7:
                style = ""
            else:
                style = "bold"
            self.console.print(f"[{style}]{text}[/{style}]", end="\r")
        
        self.animator.fade_in(update)
        self.console.print(text)  # Final version
    
    elif animation == "fade_out":
        # Similar for fade_out
        pass
```

**Step 1.5.2: Animate Status Transitions (45min)**
```python
# File: qwen_dev_cli/tui/components/status.py
# Add animation to StatusBadge

class StatusBadge:
    def __init__(self, ...):
        self.animator = Animator()
    
    def transition_to(self, new_level: StatusLevel):
        """Transition to new status with animation"""
        old_level = self.level
        
        # Animate color transition
        def update(progress):
            # Interpolate between old and new colors
            # (Rich limitation: can't do true color interpolation)
            # So we pulse instead
            if progress < 0.5:
                self.render()  # Show old
            else:
                self.level = new_level
                self.render()  # Show new
        
        self.animator.animate(0.0, 1.0, update)
```

**Step 1.5.3: Add Loading Animations (15min)**
```python
# File: qwen_dev_cli/shell.py
# Replace spinners with animated versions

# OLD:
with self.console.status("[cyan]Loading...[/cyan]"):
    await long_operation()

# NEW:
async with self._animated_status("Loading...") as status:
    await long_operation()

# Add helper:
@asynccontextmanager
async def _animated_status(self, message: str):
    """Animated status context manager"""
    from .tui.animations import animate_pulse
    
    stop_animation = False
    
    async def animation_loop():
        while not stop_animation:
            for frame in animate_pulse(message):
                if stop_animation:
                    break
                self.console.print(frame, end="\r")
                await asyncio.sleep(0.1)
    
    task = asyncio.create_task(animation_loop())
    
    try:
        yield
    finally:
        stop_animation = True
        await task
        self.console.print()  # Clear line
```

**Step 1.5.4: Test (15min)**
```bash
# Test 1: Fade-in works
$ qwen-dev
> help
# Expected: Text fades in smoothly (not instant)

# Test 2: Status transitions animated
# (trigger status change)
# Expected: Color transition visible

# Test 3: Loading animation
> (long operation)
# Expected: Pulsing "Loading..." text

# Test 4: Performance
# Expected: No lag, smooth 60fps
```

**Acceptance Criteria:**
- [ ] Fade-in/fade-out work
- [ ] Status transitions smooth
- [ ] Loading animations pulse
- [ ] No performance degradation
- [ ] Can disable with /noanimate
- [ ] Accessibility mode supported

---

#### **Task 1.6: Dashboard Integration (2h)**

**Objetivo:** Mostrar dashboard em tempo real durante sessão

**Files to Modify:**
1. `qwen_dev_cli/shell.py`
2. `qwen_dev_cli/tui/components/dashboard.py`

**Implementation Steps:**

**Step 1.6.1: Initialize Dashboard (30min)**
```python
# File: qwen_dev_cli/shell.py
# Import dashboard
from .tui.components.dashboard import SystemDashboard

# In __init__:
self.dashboard = SystemDashboard(
    console=self.console,
    update_interval=1.0  # Update every second
)

# Start background update task:
async def dashboard_update_loop():
    while True:
        self.dashboard.update_metrics({
            "memory": self._get_memory_usage(),
            "tokens": self.context_engine.window.current_input_tokens + 
                     self.context_engine.window.current_output_tokens,
            "files_modified": len(self.context.modified_files),
            "tools_called": len(self.context.tool_calls),
            "session_duration": time.time() - self.start_time
        })
        await asyncio.sleep(1.0)

self.dashboard_task = asyncio.create_task(dashboard_update_loop())
```

**Step 1.6.2: Display Dashboard (45min)**
```python
# Option 1: Dashboard in sidebar (split screen)
# (Requires Textual app)

# Option 2: Dashboard on /dashboard command
elif command == "/dashboard":
    panel = self.dashboard.render()
    self.console.print(panel)
    return False, None

# Option 3: Mini dashboard in prompt
# Show in EnhancedInputSession bottom bar
```

**Step 1.6.3: Add Dashboard to Welcome (15min)**
```python
# File: qwen_dev_cli/shell.py
# In _show_welcome() method

# After welcome panel, show dashboard
self.console.print("\n")
self.console.print(self.dashboard.render())
```

**Step 1.6.4: Add /dash Short Command (15min)**
```python
# Quick access to dashboard
elif command in ["/dash", "/dashboard", "/stats"]:
    self.console.print(self.dashboard.render())
    return False, None
```

**Step 1.6.5: Test (15min)**
```bash
# Test 1: Dashboard shows on start
$ qwen-dev
# Expected: Shows dashboard with:
#   Memory: 120MB
#   Tokens: 0
#   Files: 0
#   Tools: 0
#   Session: 0s

# Test 2: Dashboard updates
> (do some operations)
> /dash
# Expected: Metrics updated

# Test 3: Performance
# Expected: No lag from background updates
```

**Acceptance Criteria:**
- [ ] Dashboard shows on start
- [ ] Metrics update in real-time
- [ ] /dash command works
- [ ] Memory usage accurate
- [ ] Token count accurate
- [ ] No performance impact

---

### **DAY 4-5 (8h): Testing & Polish**

#### **Task 1.7: Integration Testing (4h)**

**Test Each Integration:**

1. **Command Palette Tests (1h)**
```python
# File: tests/integration/test_palette_integration.py

async def test_ctrl_k_opens_palette():
    """Test Ctrl+K triggers palette"""
    shell = InteractiveShell()
    # Simulate Ctrl+K
    result = await shell.enhanced_input.handle_key('c-k')
    assert result == "__PALETTE__"

async def test_palette_search():
    """Test fuzzy search in palette"""
    shell = InteractiveShell()
    results = shell.palette.search("git")
    assert len(results) > 0
    assert any("git" in r.title.lower() for r in results)

async def test_palette_execute():
    """Test command execution"""
    shell = InteractiveShell()
    cmd = shell.palette.get_command("git.status")
    # Mock execution
    result = await cmd.action()
    assert result is not None
```

2. **Token Tracking Tests (1h)**
```python
# File: tests/integration/test_token_tracking.py

async def test_tokens_display_after_response():
    """Test token panel shows after LLM response"""
    shell = InteractiveShell()
    # Mock LLM response
    await shell._process_request_with_llm("test")
    # Check tokens were tracked
    assert shell.context_engine.window.current_output_tokens > 0

async def test_tokens_command():
    """Test /tokens command"""
    shell = InteractiveShell()
    exit, msg = await shell._handle_system_command("/tokens")
    assert exit == False
    # Should display history

async def test_warning_at_90_percent():
    """Test warning when context >90% full"""
    shell = InteractiveShell()
    # Fill context to 95%
    shell.context_engine.window.total_tokens = 95000
    # Trigger warning
    await shell._process_request_with_llm("test")
    # Check warning displayed (check console output)
```

3. **Preview Tests (1h)**
```python
# File: tests/integration/test_preview_integration.py

async def test_preview_shows_for_edit():
    """Test preview displays before file edit"""
    shell = InteractiveShell()
    # Create test file
    Path("test.txt").write_text("old content")
    
    # Mock user accepts preview
    with patch('prompt_toolkit.shortcuts.yes_no_dialog') as mock:
        mock.return_value.run_async.return_value = True
        
        # Execute edit
        tool = shell.registry.get("write_file")
        result = await tool.execute(
            path="test.txt",
            content="new content",
            console=shell.console
        )
    
    assert result.success
    assert Path("test.txt").read_text() == "new content"

async def test_preview_reject():
    """Test rejecting preview leaves file unchanged"""
    shell = InteractiveShell()
    Path("test.txt").write_text("old content")
    
    # Mock user rejects
    with patch('prompt_toolkit.shortcuts.yes_no_dialog') as mock:
        mock.return_value.run_async.return_value = False
        
        tool = shell.registry.get("write_file")
        result = await tool.execute(
            path="test.txt",
            content="new content",
            console=shell.console
        )
    
    assert not result.success
    assert Path("test.txt").read_text() == "old content"
```

4. **Workflow & Animations Tests (1h)**
```python
# File: tests/integration/test_workflow_integration.py

async def test_workflow_tracks_steps():
    """Test workflow visualizer tracks operation steps"""
    shell = InteractiveShell()
    
    # Process request
    await shell._process_request_with_llm("test")
    
    # Check steps were added
    assert len(shell.workflow_viz.steps) > 0
    assert "parse_input" in shell.workflow_viz.steps
    assert "llm_call" in shell.workflow_viz.steps

async def test_workflow_metrics():
    """Test workflow performance metrics"""
    shell = InteractiveShell()
    await shell._process_request_with_llm("test")
    
    metrics = shell.workflow_viz.get_performance_metrics()
    assert metrics['current_fps'] > 0
    assert metrics['last_frame_time_ms'] < 20  # <20ms = good
```

---

#### **Task 1.8: Polish & Bug Fixes (4h)**

**Focus Areas:**

1. **Error Handling (1h)**
   - Add try/catch around all new integrations
   - Graceful degradation if feature fails
   - User-friendly error messages

2. **Performance Optimization (1h)**
   - Profile integration points
   - Ensure no blocking operations
   - Optimize hot paths

3. **Documentation (1h)**
   - Update README with new features
   - Add /help entries for new commands
   - Create GIFs/screenshots

4. **User Testing (1h)**
   - Dogfood the integrated features
   - Fix critical UX issues
   - Collect feedback

---

### **WEEK 1 DELIVERABLES**

**Expected Results:**
```
Parity Score:
  Before: 32% (Grade D+)
  After:  55% (Grade C)
  Gain:   +23 points

Features Integrated:
  ✅ Command Palette (Ctrl+K)
  ✅ Token Tracking (real-time)
  ✅ Inline Preview (before apply)
  ✅ Workflow Visualizer (progress)
  ✅ Animations (smooth)
  ✅ Dashboard (metrics)

Tests:
  Integration Tests: 12+ new tests
  Coverage: 96.3% → 97%+ (maintain high coverage)

Documentation:
  Updated README
  New GIFs/screenshots
  Help system updated
```

**Acceptance Criteria:**
- [ ] All 6 features integrated and working
- [ ] 12+ integration tests passing
- [ ] No performance regression
- [ ] Documentation complete
- [ ] Ready for dogfooding (Week 2)

---

## 📅 WEEK 2: DOGFOODING + TOOLS (20h)

**Goal:** Use integrated features + add critical missing tools → 55% to 65%

### **DAY 6-7 (8h): Dogfooding**

**Objective:** Use Qwen-Dev to develop Qwen-Dev, find and fix issues

**Activities:**

1. **Daily Usage (2h/day × 4 days = 8h)**
   - Use Qwen-Dev for ALL development tasks
   - Use Ctrl+K palette for commands
   - Check token usage after each interaction
   - Accept/reject previews
   - Note all friction points

2. **Issue Log Format:**
   ```markdown
   ## Issue #1: Palette search too strict
   **Severity:** Medium
   **Description:** "git status" doesn't match "Git Status" command
   **Fix:** Improve fuzzy matching (case-insensitive)
   **Time:** 30min
   
   ## Issue #2: Preview diff hard to read
   **Severity:** High
   **Description:** No syntax highlighting in diff
   **Fix:** Add Syntax() to diff rendering
   **Time:** 1h
   ```

3. **Fix Critical Issues (included in 8h)**
   - Fix top 5 most annoying issues
   - Improve UX based on real usage
   - Optimize slow operations

**Expected Issues (proactive list):**
- Palette search might be too strict
- Token display might be too verbose
- Preview might be slow for large files
- Animations might feel laggy
- Dashboard might not update correctly

**Deliverable:** Clean, dogfooded product ready for external beta.

---

### **DAY 8-10 (12h): Critical Tools**

**Objective:** Add 10-15 missing tools → increase tool coverage from 23% to 40%

#### **Tool Priority List (based on Cursor comparison):**

**Priority 1: Test Tools (4h)**
1. **Test Runner Tool (2h)**
   ```python
   # qwen_dev_cli/tools/test_runner.py
   class PytestRunnerTool(BaseTool):
       """Run pytest tests"""
       async def execute(self, pattern: str = "test_*.py", **kwargs):
           result = subprocess.run(
               ["pytest", pattern, "-v"],
               capture_output=True
           )
           return ToolResult(
               success=result.returncode == 0,
               data={"output": result.stdout.decode()},
               message="Tests completed"
           )
   ```

2. **Test Generator Tool (2h)**
   ```python
   class TestGeneratorTool(BaseTool):
       """Generate tests for a function using LLM"""
       async def execute(self, file_path: str, function_name: str):
           # Read function code
           code = extract_function(file_path, function_name)
           
           # Ask LLM to generate tests
           prompt = f"Generate pytest tests for:\n\n{code}"
           tests = await llm_client.generate(prompt)
           
           # Write tests to test_<file>.py
           test_file = f"test_{Path(file_path).name}"
           Path(test_file).write_text(tests)
           
           return ToolResult(success=True, ...)
   ```

**Priority 2: Linting/Formatting (3h)**
3. **Linter Tool (1h 30min)**
   ```python
   class PylintTool(BaseTool):
       """Run pylint on file"""
       async def execute(self, file_path: str):
           result = subprocess.run(
               ["pylint", file_path],
               capture_output=True
           )
           return ToolResult(...)
   ```

4. **Formatter Tool (1h 30min)**
   ```python
   class BlackFormatterTool(BaseTool):
       """Format code with black"""
       async def execute(self, file_path: str):
           result = subprocess.run(
               ["black", file_path],
               capture_output=True
           )
           return ToolResult(...)
   ```

**Priority 3: Git Advanced (3h)**
5. **Git Commit Tool (1h)**
6. **Git Branch Tool (1h)**
7. **Git Log Tool (1h)**

**Priority 4: LSP Basic (2h)**
8. **Go To Definition (AST-based) (2h)**
   ```python
   class GoToDefinitionTool(BaseTool):
       """Find definition of symbol using AST"""
       async def execute(self, symbol: str, file_path: str):
           # Use SemanticIndexer
           indexer = SemanticIndexer(root_path=".")
           results = indexer.find_symbol(symbol)
           
           if results:
               first = results[0]
               return ToolResult(
                   success=True,
                   data={
                       "file": first.file_path,
                       "line": first.line_number,
                       "type": first.type
                   }
               )
   ```

**Total New Tools:** 8-10 critical tools (28 → 38 tools)

---

### **WEEK 2 DELIVERABLES**

```
Parity Score:
  Before: 55% (Grade C)
  After:  65% (Grade C+)
  Gain:   +10 points

Tools:
  Before: 28 tools (23% coverage)
  After:  38 tools (32% coverage)
  Gain:   +10 tools (+9%)

Dogfooding:
  Issues Found: ~15-20
  Issues Fixed: Top 10
  UX Polish: Significant
  
Ready For:
  Private beta (10 users)
  Public demo
```

---

## 📅 WEEK 3-4: LSP + SEMANTIC SEARCH (40h)

*(Detailed breakdown available, truncated for space)*

**Week 3 Goal:** 65% → 72% (+7 points)
- Real LSP integration (python-lsp-server)
- Advanced refactoring tools
- Improved git integration

**Week 4 Goal:** 72% → 80% (+8 points)
- Semantic search with embeddings
- RAG-based code search
- Tool completion (40 → 60 tools)

---

## 🎯 SUCCESS METRICS

### **Progress Tracking:**

```
Week 1: 32% → 55% (+23) - INTEGRATION SPRINT ✅
Week 2: 55% → 65% (+10) - DOGFOODING + TOOLS
Week 3: 65% → 72% (+7)  - LSP + REFACTORING
Week 4: 72% → 80% (+8)  - SEMANTIC + POLISH

Final: 80% parity (Grade B)
```

### **Key Performance Indicators:**

| Metric | Baseline | Week 1 | Week 2 | Week 3 | Week 4 | Target |
|--------|----------|--------|--------|--------|--------|--------|
| Parity % | 32% | 55% | 65% | 72% | 80% | 80% |
| Grade | D+ | C | C+ | B- | B | B |
| Tools | 28 | 28 | 38 | 50 | 60 | 60 |
| Tests | 1002 | 1014 | 1030 | 1050 | 1070 | 1070+ |
| Coverage | 96.3% | 97% | 97.5% | 98% | 98% | 98%+ |
| Users | 0 | 0 | 10 | 50 | 100 | 100+ |

---

## 📊 TIMELINE SUMMARY

```
┌─────────────────────────────────────────────────────┐
│ INTEGRATION MASTER PLAN - 4 WEEKS TO 80% PARITY    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Week 1 (20h): INTEGRATION SPRINT    32% → 55%      │
│   Day 1-2: Palette + Tokens + Preview              │
│   Day 3:   Workflow + Animations                   │
│   Day 4-5: Dashboard + Testing                     │
│                                                     │
│ Week 2 (20h): DOGFOOD + TOOLS       55% → 65%      │
│   Day 6-7:  Dogfooding (fix issues)                │
│   Day 8-10: Add 10 critical tools                  │
│                                                     │
│ Week 3 (20h): LSP + REFACTORING     65% → 72%      │
│   Real LSP integration                             │
│   Refactoring tools                                │
│   Git advanced                                      │
│                                                     │
│ Week 4 (20h): SEMANTIC + POLISH     72% → 80%      │
│   Semantic search (RAG)                            │
│   Tool completion                                   │
│   Final polish                                      │
│                                                     │
│ RESULT: 80% Parity (Grade B) - COMPETITIVE         │
└─────────────────────────────────────────────────────┘
```

---

## ✅ NEXT STEPS

**IMMEDIATE (Next 4 hours):**

1. **Start Task 1.1** - Command Palette Integration (2h)
2. **Start Task 1.2** - Token Tracking Integration (2h)

**Command to Execute:**
```bash
cd /media/juan/DATA/projects/GEMINI-CLI-2/qwen-dev-cli
git checkout -b feature/integration-sprint-week1
# Start implementing Task 1.1 Step 1.1.1
```

**Files to Modify First:**
1. `qwen_dev_cli/tui/input_enhanced.py` (add Ctrl+K keybinding)
2. `qwen_dev_cli/shell.py` (handle palette trigger)

**Expected Completion:** Week 1 complete by 2025-11-25

---

**Plan Created:** 2025-11-20 18:00 UTC  
**Author:** Gemini-Vértice MAXIMUS  
**Status:** READY TO EXECUTE  
**First Task:** Task 1.1 - Command Palette Integration
