# ⚡ INTEGRATION WEEK 1 - QUICK START GUIDE
> **Fast-Track Integration Sprint: 4h to +23 points**  
> **Date:** 2025-11-20  
> **Goal:** Connect 6 existing features that are offline  
> **Impact:** 32% → 55% parity in 1 week

---

## 🎯 THE SITUATION

### What We Discovered:
```
✅ Code EXISTS:    33,446 lines, 21 TUI components
✅ Tests PASS:     96.3% coverage, 1002 tests
❌ Integration:    67% of components NOT connected
❌ User sees:      Only 33% of implemented features

Result: 32% parity (Grade D+)
```

### What's Offline (Already Built, Just Not Connected):
1. **Command Palette** (300 lines) - Ctrl+K does nothing
2. **Token Tracking** (528 lines) - Developed yesterday, not integrated
3. **Inline Preview** (400 lines) - User doesn't see diffs
4. **Workflow Visualizer** (700 lines) - Imported but never used
5. **Animations** (200 lines) - Dead code
6. **Dashboard** (200 lines) - Not integrated

---

## 🚀 WEEK 1 PLAN (20 HOURS)

### Day-by-Day Breakdown:

#### **DAY 1 (4h): Palette + Tokens**
```
Task 1.1: Command Palette (2h)
  ├─ Add Ctrl+K keybinding (30min)
  ├─ Handle palette in shell loop (1h)
  ├─ Register 15 commands (30min)
  
Task 1.2: Token Tracking (2h)
  ├─ Initialize ContextEngine (15min)
  ├─ Hook into LLM streaming (45min)
  ├─ Display token panel (30min)
  └─ Add /tokens command (15min)
```

#### **DAY 2 (4h): Preview + Workflow**
```
Task 1.3: Inline Preview (2.5h)
  ├─ Add preview hook in WriteFileTool (45min)
  ├─ Create interactive preview (45min)
  ├─ Pass console to tools (30min)
  └─ Add /nopreview mode (15min)
  
Task 1.4: Workflow Visualizer (1.5h)
  ├─ Add workflow steps (30min)
  ├─ Display workflow (30min)
  └─ Add /workflow command (15min)
```

#### **DAY 3 (4h): Animations + Dashboard**
```
Task 1.5: Animations (2h)
  ├─ Replace static prints (1h)
  ├─ Animate status transitions (45min)
  └─ Add loading animations (15min)
  
Task 1.6: Dashboard (2h)
  ├─ Initialize dashboard (30min)
  ├─ Display dashboard (45min)
  ├─ Add to welcome (15min)
  └─ Add /dash command (15min)
```

#### **DAY 4-5 (8h): Testing + Polish**
```
Task 1.7: Integration Testing (4h)
  ├─ Palette tests (1h)
  ├─ Token tests (1h)
  ├─ Preview tests (1h)
  └─ Workflow tests (1h)
  
Task 1.8: Polish (4h)
  ├─ Error handling (1h)
  ├─ Performance optimization (1h)
  ├─ Documentation (1h)
  └─ User testing (1h)
```

---

## 💻 IMMEDIATE FIRST STEPS (30 MINUTES)

### Step 1: Create Branch (2min)
```bash
cd /media/juan/DATA/projects/GEMINI-CLI-2/qwen-dev-cli
git checkout -b feature/integration-sprint-week1
```

### Step 2: Add Ctrl+K Keybinding (10min)

**File:** `qwen_dev_cli/tui/input_enhanced.py`

Add after line 156:
```python
from prompt_toolkit.key_binding import KeyBindings

self.kb = KeyBindings()

@self.kb.add('c-k')  # Ctrl+K
async def _(event):
    """Open command palette"""
    event.app.exit(result="__PALETTE__")

# Update PromptSession (line 156):
self.session: PromptSession[str] = PromptSession(
    # ... existing params ...
    key_bindings=self.kb,  # ADD THIS LINE
)
```

### Step 3: Test Keybinding (5min)
```bash
# Run shell
python -m qwen_dev_cli

# Press Ctrl+K
# Expected: Input returns "__PALETTE__"
```

### Step 4: Handle Palette Trigger (10min)

**File:** `qwen_dev_cli/shell.py`

Add after line 969 (in `async def run()` loop):
```python
user_input = await self.enhanced_input.prompt_async()

# ADD THIS:
if user_input == "__PALETTE__":
    self.console.print("[cyan]Ctrl+K pressed - Palette coming soon![/cyan]")
    continue  # For now, just acknowledge
```

### Step 5: Verify It Works (3min)
```bash
# Run shell
python -m qwen_dev_cli

# Press Ctrl+K
# Expected: "Ctrl+K pressed - Palette coming soon!"
```

**✅ If this works, you're ready for the full integration!**

---

## 📋 FULL TASK LIST (Checklist)

### Task 1.1: Command Palette (2h)
- [ ] Step 1.1.1: Add keybinding handler (30min)
- [ ] Step 1.1.2: Handle palette in shell loop (1h)
- [ ] Step 1.1.3: Test (30min)
- [ ] **Acceptance:** Ctrl+K opens palette with fuzzy search

### Task 1.2: Token Tracking (2h)
- [ ] Step 1.2.1: Initialize ContextEngine (15min)
- [ ] Step 1.2.2: Hook into LLM streaming (45min)
- [ ] Step 1.2.3: Display token panel (30min)
- [ ] Step 1.2.4: Add /tokens command (15min)
- [ ] Step 1.2.5: Test (15min)
- [ ] **Acceptance:** Token panel shows after each LLM response

### Task 1.3: Inline Preview (2.5h)
- [ ] Step 1.3.1: Add preview hook (45min)
- [ ] Step 1.3.2: Interactive preview method (45min)
- [ ] Step 1.3.3: Pass console to tools (30min)
- [ ] Step 1.3.4: Add /nopreview mode (15min)
- [ ] Step 1.3.5: Test (15min)
- [ ] **Acceptance:** Preview shows before file edits

### Task 1.4: Workflow Visualizer (1.5h)
- [ ] Step 1.4.1: Add workflow steps (30min)
- [ ] Step 1.4.2: Display workflow (30min)
- [ ] Step 1.4.3: Add /workflow command (15min)
- [ ] Step 1.4.4: Test (15min)
- [ ] **Acceptance:** Workflow shows during operations

### Task 1.5: Animations (2h)
- [ ] Step 1.5.1: Replace static prints (1h)
- [ ] Step 1.5.2: Animate status transitions (45min)
- [ ] Step 1.5.3: Add loading animations (15min)
- [ ] Step 1.5.4: Test (15min)
- [ ] **Acceptance:** Smooth fade-in/fade-out

### Task 1.6: Dashboard (2h)
- [ ] Step 1.6.1: Initialize dashboard (30min)
- [ ] Step 1.6.2: Display dashboard (45min)
- [ ] Step 1.6.3: Add to welcome (15min)
- [ ] Step 1.6.4: Add /dash command (15min)
- [ ] Step 1.6.5: Test (15min)
- [ ] **Acceptance:** Dashboard shows real-time metrics

### Task 1.7: Testing (4h)
- [ ] Palette integration tests (1h)
- [ ] Token tracking tests (1h)
- [ ] Preview tests (1h)
- [ ] Workflow + animation tests (1h)
- [ ] **Acceptance:** 12+ tests passing

### Task 1.8: Polish (4h)
- [ ] Error handling (1h)
- [ ] Performance optimization (1h)
- [ ] Documentation (1h)
- [ ] User testing (1h)
- [ ] **Acceptance:** No regressions, docs updated

---

## 🎯 SUCCESS CRITERIA (Week 1)

### Functional Requirements:
- [x] Ctrl+K opens command palette
- [x] Token usage displays after LLM responses
- [x] Inline preview shows before file edits
- [x] Workflow visualizer tracks operations
- [x] Animations are smooth (no lag)
- [x] Dashboard shows real-time metrics

### Technical Requirements:
- [x] 12+ integration tests passing
- [x] No performance regression (<5% slowdown)
- [x] Coverage maintained (96.3%+)
- [x] No critical bugs

### Documentation:
- [x] README updated with new features
- [x] /help updated with new commands
- [x] GIFs/screenshots created

---

## 📊 EXPECTED RESULTS

### Parity Progress:
```
Before: 32% (Grade D+)
After:  55% (Grade C)
Gain:   +23 points
```

### Features:
```
Integrated: 6/6 (100%)
  ✅ Command Palette
  ✅ Token Tracking
  ✅ Inline Preview
  ✅ Workflow Visualizer
  ✅ Animations
  ✅ Dashboard
```

### Tests:
```
Before: 1002 tests
After:  1014+ tests
New:    12+ integration tests
```

---

## ⚡ GETTING HELP

### Quick Reference:
- **Full Plan:** [INTEGRATION_MASTER_PLAN.md](INTEGRATION_MASTER_PLAN.md)
- **Code Audit:** [BRUTAL_HONEST_AUDIT_REAL.md](BRUTAL_HONEST_AUDIT_REAL.md)
- **Project Plan:** [MASTER_PLAN.md](planning/MASTER_PLAN.md)

### Files You'll Modify:
1. `qwen_dev_cli/shell.py` (main integration point)
2. `qwen_dev_cli/tui/input_enhanced.py` (Ctrl+K binding)
3. `qwen_dev_cli/tools/file_ops.py` (preview hooks)
4. `qwen_dev_cli/core/llm.py` (token tracking)

### Key Imports Already Available:
```python
# Already in shell.py:
from .tui.components.workflow_visualizer import WorkflowVisualizer, StepStatus
from .tui.components.execution_timeline import ExecutionTimeline

# Need to add:
from .tui.components.palette import create_default_palette, CommandPalette
from .tui.components.context_awareness import ContextAwarenessEngine
from .tui.components.preview import EditPreview
from .tui.components.dashboard import SystemDashboard
from .tui.animations import smooth_animator, Animator
```

---

## 🚦 STATUS TRACKING

**Current Status:** ⚪ NOT STARTED

**Progress Tracking:**
- [ ] **Day 1** (4h): Palette + Tokens
- [ ] **Day 2** (4h): Preview + Workflow
- [ ] **Day 3** (4h): Animations + Dashboard
- [ ] **Day 4-5** (8h): Testing + Polish

**Completion Date Target:** 2025-11-25

---

## ✅ READY TO START?

**First command:**
```bash
git checkout -b feature/integration-sprint-week1
```

**First file to edit:**
```bash
vim qwen_dev_cli/tui/input_enhanced.py
# Add Ctrl+K keybinding (see Step 2 above)
```

**First test:**
```bash
python -m qwen_dev_cli
# Press Ctrl+K, should see "__PALETTE__"
```

---

**Good luck! 🚀**

**Created:** 2025-11-20 18:15 UTC  
**Author:** Gemini-Vértice MAXIMUS  
**Status:** READY TO EXECUTE
