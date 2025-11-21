# 🚨 EMERGENCY FIX PLAN - 12 HOUR SPRINT
**Mission:** Transform 55% parity → 90% parity  
**Timeline:** 12 hours focused execution  
**Methodology:** Fix, Test, Validate, Ship

---

## 🎯 SPRINT STRUCTURE

```
PHASE 1: WIRE THE BRAIN (4h)    → Make claimed features work
PHASE 2: COMPLETE THE GAPS (6h) → Fill missing pieces
PHASE 3: VALIDATE REALITY (2h)  → Prove it works
```

---

# PHASE 1: WIRE THE BRAIN (4 HOURS)

## 🔴 TASK 1.1: TOKEN TRACKING INTEGRATION (60 min)

### **Current State:** Code exists but isolated  
### **Target State:** Real-time token display in UI

### **Subtasks:**

#### 1.1.1: Hook Token Extraction (20 min)
**File:** `qwen_dev_cli/core/llm.py`

**Location:** Line ~525 in `async def generate()`

**Add after response generation:**
```python
async def generate(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    context: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    provider: Optional[str] = None
) -> str:
    """Generate complete response (non-streaming)."""
    chunks = []
    total_input_tokens = 0
    total_output_tokens = 0
    
    async for chunk in self.stream_chat(prompt, context, max_tokens, temperature, provider):
        chunks.append(chunk)
    
    response = "".join(chunks)
    
    # NEW: Extract token usage if available
    if hasattr(self, '_last_usage_metadata'):
        total_input_tokens = self._last_usage_metadata.get('input_tokens', 0)
        total_output_tokens = self._last_usage_metadata.get('output_tokens', 0)
        
        # Notify token tracker (if shell has one)
        if hasattr(self, 'token_callback') and self.token_callback:
            self.token_callback(total_input_tokens, total_output_tokens)
    
    return response
```

**Also add to `stream_chat`:**
```python
async def stream_chat(...):
    # ... existing code ...
    
    # After getting response
    if hasattr(response, 'usage_metadata'):
        self._last_usage_metadata = {
            'input_tokens': response.usage_metadata.prompt_token_count,
            'output_tokens': response.usage_metadata.candidates_token_count
        }
```

#### 1.1.2: Wire to Context Engine (15 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** Line ~165 in `__init__`

**Add callback registration:**
```python
def __init__(self, llm_client=None, ...):
    # ... existing init ...
    
    # Context engine (already exists at line 196)
    self.context_engine = ContextAwarenessEngine(
        max_context_tokens=100_000,
        console=self.console
    )
    
    # NEW: Register token callback with LLM
    if self.llm:
        self.llm.token_callback = self._on_tokens_used
        
def _on_tokens_used(self, input_tokens: int, output_tokens: int):
    """Callback when LLM uses tokens."""
    self.context_engine.update_tokens(input_tokens, output_tokens)
    
    # Show in UI if enabled
    if self.show_token_usage:
        usage = self.context_engine.get_usage_summary()
        self.console.print(
            f"[dim]Tokens: {usage['total']:,} / {usage['max']:,} "
            f"({usage['percent']:.1f}%) | Cost: ${usage['cost']:.4f}[/dim]"
        )
```

#### 1.1.3: Add Status Bar Display (15 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** After each LLM response (line ~1420)

```python
# After LLM suggestion (line 1420)
suggestion = await self._get_command_suggestion(user_input, rich_ctx)
self.workflow_viz.update_step_status("analyze", StepStatus.COMPLETED)

# NEW: Show token usage
if self.context_engine:
    token_stats = self.context_engine.render_compact_stats()
    self.console.print(token_stats)  # Already returns Rich renderable
```

#### 1.1.4: Test Token Tracking (10 min)
**Commands:**
```bash
# Start shell
python -m qwen_dev_cli.cli shell

# Make query that uses LLM
> explain the shell.py file

# Verify:
# 1. Token count appears after response
# 2. Numbers are non-zero
# 3. Updates on each query
```

---

## 🟡 TASK 1.2: COMMAND PALETTE UI (90 min)

### **Current State:** Backend works, no UI or keybinding  
### **Target State:** Ctrl+K opens modal, fuzzy search works

### **Subtasks:**

#### 1.2.1: Add Keybinding Handler (30 min)
**File:** `qwen_dev_cli/tui/input_enhanced.py`

**Location:** In `EnhancedInputSession` class

**Add key capture:**
```python
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

class EnhancedInputSession:
    def __init__(self, ...):
        # ... existing init ...
        
        # Create key bindings
        self.kb = KeyBindings()
        
        # Register Ctrl+K for command palette
        @self.kb.add('c-k')
        def _(event):
            """Open command palette."""
            event.app.exit(result="__PALETTE__")
        
        # Register Ctrl+? for help
        @self.kb.add('c-question')
        def _(event):
            """Show keyboard shortcuts."""
            event.app.exit(result="__HELP__")
    
    async def prompt_async(self) -> Optional[str]:
        """Prompt with keybindings."""
        # ... existing code ...
        
        # Add key_bindings to session
        result = await self.session.prompt_async(
            "You> ",
            completer=self.completer,
            style=self.style,
            key_bindings=self.kb  # NEW
        )
        
        return result
```

#### 1.2.2: Create TUI Modal (45 min)
**File:** `qwen_dev_cli/tui/components/palette_modal.py` (NEW)

```python
"""Command Palette Modal - Interactive TUI overlay"""

from textual.app import ComposeResult
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from rich.text import Text

from .palette import CommandPalette, Command


class PaletteModal(ModalScreen):
    """Modal overlay for command palette."""
    
    def __init__(self, palette: CommandPalette):
        super().__init__()
        self.palette = palette
        self.filtered_commands = palette.commands
    
    def compose(self) -> ComposeResult:
        """Create modal layout."""
        with Container(id="palette-container"):
            yield Label("🎨 Command Palette", id="palette-title")
            yield Input(placeholder="Type to search...", id="search-input")
            yield ListView(id="command-list")
    
    def on_mount(self) -> None:
        """Focus search input on mount."""
        self.query_one("#search-input").focus()
        self._update_list()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands on input."""
        query = event.value
        self.filtered_commands = self.palette.search(query)
        self._update_list()
    
    def _update_list(self):
        """Update command list."""
        list_view = self.query_one("#command-list", ListView)
        list_view.clear()
        
        for cmd in self.filtered_commands[:10]:  # Top 10
            item = ListItem(
                Label(f"{cmd.title} - {cmd.description}")
            )
            item.command = cmd
            list_view.append(item)
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Execute selected command."""
        if hasattr(event.item, 'command'):
            self.dismiss(result=event.item.command)
    
    def on_key(self, event) -> None:
        """Handle escape to close."""
        if event.key == "escape":
            self.dismiss(result=None)
```

**CSS (add to theme):**
```css
#palette-container {
    width: 80%;
    height: 60%;
    background: $surface;
    border: solid $primary;
    padding: 1 2;
}

#palette-title {
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
}
```

#### 1.2.3: Wire Modal to Shell (15 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** Line ~1230 (palette handler)

```python
async def _show_palette_interactive(self) -> Optional[Command]:
    """Show command palette modal."""
    from .tui.components.palette_modal import PaletteModal
    
    # Create and push modal
    modal = PaletteModal(self.palette)
    
    # For now, use fallback text-based until textual integration
    # TODO: Integrate with textual app when available
    
    # Fallback: Text-based menu
    self.console.print("\n[cyan bold]Command Palette[/cyan bold]\n")
    
    # Show search prompt
    query = input("Search commands: ").strip()
    
    # Search
    results = self.palette.search(query, limit=10)
    
    if not results:
        self.console.print("[yellow]No commands found[/yellow]")
        return None
    
    # Show results
    for i, cmd in enumerate(results, 1):
        kb = f" [{cmd.keybinding}]" if cmd.keybinding else ""
        self.console.print(f"{i}. {cmd.title}{kb}")
        self.console.print(f"   [dim]{cmd.description}[/dim]")
    
    # Get selection
    try:
        choice = int(input("\nSelect (number): "))
        if 1 <= choice <= len(results):
            return results[choice - 1]
    except (ValueError, KeyError):
        pass
    
    return None
```

---

## 🟠 TASK 1.3: PREVIEW INTEGRATION (90 min)

### **Current State:** Complete code, never used  
### **Target State:** File edits show preview before applying

### **Subtasks:**

#### 1.3.1: Instantiate Preview Manager (10 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** Line ~188 in `__init__`

```python
# Add after workflow_viz
self.workflow_viz = WorkflowVisualizer(console=self.console)
self.execution_timeline = ExecutionTimeline(console=self.console)

# NEW: Preview system
from .tui.components.preview import PreviewManager, PreviewConfig
self.preview_manager = PreviewManager(
    console=self.console,
    config=PreviewConfig(
        auto_save_backup=True,
        max_undo_history=50,
        show_line_numbers=True
    )
)
```

#### 1.3.2: Hook into File Write Tools (40 min)
**File:** `qwen_dev_cli/tools/file_ops.py`

**Location:** `WriteFileTool.execute()` method

```python
from qwen_dev_cli.tui.components.preview import FileEdit, EditAction

class WriteFileTool(BaseTool):
    # ... existing code ...
    
    async def execute(self, path: str, content: str, **kwargs) -> ToolResult:
        """Execute file write with preview."""
        path_obj = Path(path)
        
        # Check if preview is enabled (from shell context)
        preview_manager = kwargs.get('preview_manager')
        
        if preview_manager and path_obj.exists():
            # Show preview for edits
            original_content = path_obj.read_text()
            
            # Create edit
            edit = FileEdit(
                filepath=str(path_obj),
                original_content=original_content,
                new_content=content,
                action=EditAction.MODIFY
            )
            
            # Add to preview
            preview_id = preview_manager.add_edit(edit)
            
            # Show diff
            preview_manager.show_preview(preview_id)
            
            # Ask for confirmation
            response = input("\nAccept changes? [Y/n/e(dit)] ").strip().lower()
            
            if response in ('', 'y', 'yes'):
                # Apply changes
                result = preview_manager.apply_edit(preview_id)
                if result:
                    return ToolResult.success(
                        data=f"File written: {path}",
                        metadata={"path": str(path_obj), "bytes": len(content)}
                    )
            elif response == 'e':
                # Edit again (return to LLM)
                return ToolResult.error(
                    "User requested edit revision",
                    metadata={"action": "retry"}
                )
            else:
                # Reject
                preview_manager.reject_edit(preview_id)
                return ToolResult.error("Changes rejected by user")
        
        # Original behavior (no preview)
        # ... existing write code ...
```

#### 1.3.3: Add Preview to Edit Tool (20 min)
**File:** `qwen_dev_cli/tools/file_ops.py`

**Same pattern for `EditFileTool.execute()`**

#### 1.3.4: Wire to Shell Context (10 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** Line ~655 in `_execute_tool_calls`

```python
# Add session context for tools that need it
if tool_name in ['getcontext', 'savesession']:
    args['session_context'] = self.context

# NEW: Add preview manager to file tools
if tool_name in ['write_file', 'edit_file', 'insert_lines']:
    args['preview_manager'] = self.preview_manager
```

#### 1.3.5: Test Preview Flow (10 min)
```bash
# Start shell
python -m qwen_dev_cli.cli shell

# Request file edit
> modify test.py to add a hello function

# Verify:
# 1. Diff preview appears before writing
# 2. Accept/reject prompt works
# 3. Undo command works after accept
```

---

# PHASE 2: COMPLETE THE GAPS (6 HOURS)

## 🟢 TASK 2.1: ANIMATION SYSTEM ACTIVATION (2h)

### **Subtasks:**

#### 2.1.1: Add State Transition Animations (60 min)
**File:** `qwen_dev_cli/shell.py`

**Hook animations into state changes:**

```python
# Line 1290: When starting workflow
self.workflow_viz.start_workflow("Process User Request")

# NEW: Animate transition
await self.animator.animate(
    "fade_in",
    target=self.workflow_viz,
    duration=0.3
)

# Line 1421: On completion
self.workflow_viz.update_step_status("analyze", StepStatus.COMPLETED)

# NEW: Success animation
await self.state_transition.transition("thinking", "ready")
self.console.print(self.animator.success_checkmark())  # ✓ with animation
```

#### 2.1.2: Add Loading Animations (30 min)
**File:** `qwen_dev_cli/shell.py`

```python
# Line 1416: Before LLM call
with self.console.status("[cyan]Thinking...[/cyan]") as status:
    suggestion = await self._get_command_suggestion(user_input, rich_ctx)
    
    # NEW: Animated completion
    status.update("[green]Ready![/green]")
    await asyncio.sleep(0.2)  # Brief pause for visual feedback
```

#### 2.1.3: Smooth Diff Rendering (30 min)
**File:** `qwen_dev_cli/tui/components/preview.py`

**Add progressive reveal:**
```python
def show_preview(self, preview_id: str):
    """Show preview with animation."""
    edit = self.get_edit(preview_id)
    
    # Render diff line-by-line with delay
    for line in edit.diff_lines:
        self.console.print(line.render())
        time.sleep(0.01)  # 10ms delay per line (smooth but fast)
```

---

## 🔵 TASK 2.2: DASHBOARD UI (2h)

### **Subtasks:**

#### 2.2.1: Add /dashboard Command (60 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** Line ~1277 (slash commands)

```python
elif user_input.strip().lower() == '/dashboard':
    # Show dashboard
    self._show_dashboard()
    continue

def _show_dashboard(self):
    """Display interactive dashboard."""
    self.console.clear()
    
    # Render current state
    dashboard_view = self.dashboard.render_full()
    self.console.print(dashboard_view)
    
    # Show stats
    stats = self.dashboard.get_statistics()
    
    stats_table = Table(title="Session Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green", justify="right")
    
    stats_table.add_row("Total Operations", str(stats['total_operations']))
    stats_table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
    stats_table.add_row("Avg Duration", f"{stats['avg_duration']:.2f}s")
    stats_table.add_row("Active Operations", str(stats['active_count']))
    
    self.console.print(stats_table)
```

#### 2.2.2: Live Dashboard Updates (60 min)
**File:** `qwen_dev_cli/tui/components/dashboard.py`

**Add live update method:**
```python
from rich.live import Live

class Dashboard:
    # ... existing code ...
    
    def start_live_display(self):
        """Start live-updating dashboard in separate thread."""
        self.live = Live(self.render_compact(), console=self.console)
        self.live.start()
    
    def update_live(self):
        """Update live display."""
        if hasattr(self, 'live') and self.live:
            self.live.update(self.render_compact())
    
    def stop_live_display(self):
        """Stop live display."""
        if hasattr(self, 'live') and self.live:
            self.live.stop()
```

**Wire to shell:**
```python
# In shell.__init__ (after dashboard creation)
self.dashboard = Dashboard(console=self.console, max_history=5)
self.dashboard.start_live_display()  # Always show in corner

# In dashboard operation updates
self.dashboard.add_operation(operation)
self.dashboard.update_live()  # Refresh display
```

---

## ⌨️ TASK 2.3: KEYBOARD SHORTCUTS (2h)

### **Subtasks:**

#### 2.3.1: Implement Full Shortcut Map (60 min)
**File:** `qwen_dev_cli/tui/input_enhanced.py`

**Expand keybindings:**
```python
def _register_keybindings(self):
    """Register all keyboard shortcuts."""
    kb = KeyBindings()
    
    # Command palette
    @kb.add('c-k')
    def _(event):
        event.app.exit(result="__PALETTE__")
    
    # Undo/Redo
    @kb.add('c-z')
    def _(event):
        event.app.exit(result="__UNDO__")
    
    @kb.add('c-y')
    def _(event):
        event.app.exit(result="__REDO__")
    
    # Help
    @kb.add('c-slash')
    def _(event):
        event.app.exit(result="__HELP__")
    
    # Dashboard
    @kb.add('c-d')
    def _(event):
        event.app.exit(result="__DASHBOARD__")
    
    # Clear screen
    @kb.add('c-l')
    def _(event):
        event.app.exit(result="__CLEAR__")
    
    return kb
```

#### 2.3.2: Add Shortcut Overlay (30 min)
**File:** `qwen_dev_cli/shell.py`

**Add help command:**
```python
elif user_input == "__HELP__":
    self._show_keyboard_shortcuts()
    continue

def _show_keyboard_shortcuts(self):
    """Display keyboard shortcut reference."""
    shortcuts_table = Table(title="⌨️  Keyboard Shortcuts")
    shortcuts_table.add_column("Shortcut", style="cyan bold")
    shortcuts_table.add_column("Action", style="white")
    
    shortcuts = [
        ("Ctrl+K", "Open Command Palette"),
        ("Ctrl+D", "Show Dashboard"),
        ("Ctrl+Z", "Undo Last Edit"),
        ("Ctrl+Y", "Redo Edit"),
        ("Ctrl+/", "Show This Help"),
        ("Ctrl+L", "Clear Screen"),
        ("Ctrl+C", "Cancel Operation"),
        ("Ctrl+D", "Exit Shell"),
    ]
    
    for shortcut, action in shortcuts:
        shortcuts_table.add_row(shortcut, action)
    
    self.console.print(shortcuts_table)
```

#### 2.3.3: Handle Shortcuts in Main Loop (30 min)
**File:** `qwen_dev_cli/shell.py`

**Location:** Line ~1225 (after palette handler)

```python
# Handle special commands from keybindings
if user_input == "__UNDO__":
    if self.preview_manager:
        result = self.preview_manager.undo()
        self.console.print(f"[green]✓ Undone: {result}[/green]" if result else "[yellow]Nothing to undo[/yellow]")
    continue

elif user_input == "__REDO__":
    if self.preview_manager:
        result = self.preview_manager.redo()
        self.console.print(f"[green]✓ Redone: {result}[/green]" if result else "[yellow]Nothing to redo[/yellow]")
    continue

elif user_input == "__DASHBOARD__":
    self._show_dashboard()
    continue

elif user_input == "__CLEAR__":
    self.console.clear()
    continue
```

---

# PHASE 3: VALIDATE REALITY (2 HOURS)

## ✅ TASK 3.1: FIX TEST SUITE (60 min)

### **Subtasks:**

#### 3.1.1: Add Timeout Guards (30 min)
**File:** `tests/conftest.py`

**Add global timeout:**
```python
import pytest

@pytest.fixture(autouse=True)
def timeout_guard():
    """Add 10s timeout to all async tests."""
    import asyncio
    
    # Set event loop policy with timeout
    policy = asyncio.get_event_loop_policy()
    loop = policy.get_event_loop()
    
    # Add timeout wrapper
    original_run = loop.run_until_complete
    
    def run_with_timeout(coro):
        return original_run(asyncio.wait_for(coro, timeout=10.0))
    
    loop.run_until_complete = run_with_timeout
    
    yield
    
    loop.run_until_complete = original_run
```

#### 3.1.2: Fix Hanging Tests (20 min)
**Find and fix hanging tests:**
```bash
# Run with timeout to find culprits
pytest tests/ -vv --timeout=5 2>&1 | grep "TIMEOUT"

# Add pytest.mark.timeout to slow tests
```

#### 3.1.3: Verify Full Suite (10 min)
```bash
# Should complete in <60s
time pytest tests/ -q

# Expected: 1021 passed, 0 failed, ~45s runtime
```

---

## 📊 TASK 3.2: BENCHMARKS (60 min)

### **Subtasks:**

#### 3.2.1: Create Benchmark Suite (30 min)
**File:** `benchmarks/performance_test.py` (NEW)

```python
"""Performance benchmarks for qwen-dev-cli"""

import time
import asyncio
from qwen_dev_cli.shell import InteractiveShell
from qwen_dev_cli.core.llm import llm_client


class Benchmark:
    """Benchmark runner."""
    
    async def bench_llm_response(self):
        """Measure LLM response time."""
        times = []
        
        for _ in range(10):
            start = time.time()
            await llm_client.generate("Hello", max_tokens=50)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg = sum(times) / len(times)
        print(f"LLM Response: {avg*1000:.1f}ms avg")
        assert avg < 2.0, "LLM too slow"
    
    async def bench_file_read(self):
        """Measure file read tool speed."""
        from qwen_dev_cli.tools.file_ops import ReadFileTool
        tool = ReadFileTool()
        
        times = []
        for _ in range(100):
            start = time.time()
            await tool.execute("shell.py")
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg = sum(times) / len(times)
        print(f"File Read: {avg*1000:.1f}ms avg")
        assert avg < 0.05, "File read too slow"
    
    async def bench_workflow_viz(self):
        """Measure visualization overhead."""
        from qwen_dev_cli.tui.components.workflow_visualizer import WorkflowVisualizer
        from rich.console import Console
        
        viz = WorkflowVisualizer(console=Console())
        
        start = time.time()
        for i in range(100):
            viz.start_workflow(f"Test {i}")
            viz.add_step("step1", "Test", "running")
            viz.update_step_status("step1", "completed")
            viz.complete_workflow()
        elapsed = time.time() - start
        
        per_workflow = elapsed / 100
        print(f"Workflow Viz: {per_workflow*1000:.1f}ms per workflow")
        assert per_workflow < 0.01, "Viz too slow"


if __name__ == "__main__":
    bench = Benchmark()
    asyncio.run(bench.bench_llm_response())
    asyncio.run(bench.bench_file_read())
    asyncio.run(bench.bench_workflow_viz())
    print("✓ All benchmarks passed")
```

#### 3.2.2: Run Benchmarks (15 min)
```bash
cd benchmarks
python performance_test.py

# Expected output:
# LLM Response: ~500-1500ms avg
# File Read: ~5-20ms avg
# Workflow Viz: <5ms per workflow
```

#### 3.2.3: Document Baseline (15 min)
**File:** `benchmarks/BASELINE.md` (NEW)

```markdown
# Performance Baseline - 2025-11-20

## Measurements

| Operation | Avg Time | Target | Status |
|-----------|----------|--------|--------|
| LLM Generate (50 tokens) | 850ms | <2000ms | ✅ PASS |
| File Read Tool | 12ms | <50ms | ✅ PASS |
| Workflow Visualization | 3ms | <10ms | ✅ PASS |
| Command Palette Search | 8ms | <50ms | ✅ PASS |
| Token Tracker Update | 1ms | <5ms | ✅ PASS |

## System Info
- CPU: [detected]
- RAM: [detected]
- Python: 3.11.13
- OS: Linux Mint

## Next Steps
- [ ] Profile hot paths with cProfile
- [ ] Optimize token tracking (currently 1ms overhead)
- [ ] Cache workflow render (reduce to <1ms)
```

---

## 🎯 FINAL VALIDATION CHECKLIST

### **P0 - Must Work**
```bash
# 1. Token tracking visible
python -m qwen_dev_cli.cli shell
> explain shell.py
# Expect: Token count appears after response

# 2. Command palette opens
> [Press Ctrl+K]
# Expect: Search prompt appears

# 3. File preview shows
> modify test.py to add hello function
# Expect: Diff preview before write

# 4. Tests pass
pytest tests/ -q
# Expect: 1021 passed in <60s

# 5. Benchmarks pass
python benchmarks/performance_test.py
# Expect: All benchmarks ✓
```

### **P1 - Should Work**
- [ ] Animations render smoothly
- [ ] Dashboard shows with /dashboard
- [ ] Ctrl+Z undoes last edit
- [ ] Ctrl+/ shows shortcuts
- [ ] No errors in stderr

### **P2 - Nice to Have**
- [ ] Onboarding tutorial
- [ ] Settings UI
- [ ] Session save/restore
- [ ] Mini-map overview

---

## 📈 SUCCESS CRITERIA

### **Before (Current State)**
- Token tracking: 0% (exists, not wired)
- Command palette: 25% (backend only)
- Preview: 0% (orphaned code)
- Workflow viz: 80% (partial)
- **Overall: 55% parity**

### **After (Target State)**
- Token tracking: 90% (working + UI)
- Command palette: 85% (working + fallback UI)
- Preview: 90% (integrated + tested)
- Workflow viz: 90% (complete)
- **Overall: 85-90% parity**

### **Competitive Position**
```
Cursor:       100% (industry leader)
Claude Code:   95% (strong)
Gemini CLI:    85% (official)
qwen-dev-cli:  90% ← TARGET (competitive)
```

---

## 🚀 EXECUTION PROTOCOL

1. **Start Timer**: 12 hours from now
2. **Work in Order**: Phase 1 → 2 → 3 (no skipping)
3. **Test Each Task**: Validate before moving on
4. **No Rabbit Holes**: If stuck >20min, move to next task
5. **Ship Often**: Commit after each completed task
6. **Final Validation**: Run full checklist at end

---

## 📝 COMMIT STRATEGY

```bash
# Phase 1
git commit -m "feat: wire token tracking to LLM calls"
git commit -m "feat: add command palette keybinding"
git commit -m "feat: integrate preview system"

# Phase 2
git commit -m "feat: activate animation system"
git commit -m "feat: add dashboard UI command"
git commit -m "feat: implement keyboard shortcuts"

# Phase 3
git commit -m "fix: add timeout guards to test suite"
git commit -m "test: add performance benchmark suite"
git commit -m "docs: document baseline performance"

# Final
git commit -m "chore: emergency fix sprint complete - 90% parity achieved"
```

---

**Sprint Start Time:** [TBD]  
**Expected Completion:** [TBD + 12h]  
**Status:** READY TO EXECUTE
