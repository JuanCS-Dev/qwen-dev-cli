# CYBERPUNK UI IMPLEMENTATION PLAN
**Target**: Pixel-perfect replication of reference design using Tailwind CSS + Gradio 6

---

## VISUAL DECOMPOSITION

### Color Palette (Extracted from Reference)
```css
--cyber-bg-primary: #0A0E14;      /* Main background */
--cyber-bg-panel: #141922;         /* Panel background */
--cyber-accent-cyan: #00D9FF;      /* Primary accent */
--cyber-accent-cyan-glow: rgba(0, 217, 255, 0.3);
--cyber-text-primary: #E6E6E6;     /* Main text */
--cyber-text-secondary: #8A8A8A;   /* Muted text */
--cyber-border: rgba(0, 217, 255, 0.2);
--cyber-success: #10B981;          /* Green accents */
--cyber-warning: #F59E0B;          /* Orange/amber */
--cyber-info: #3B82F6;             /* Blue info */
```

### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│                    HEADER (GEMINI-CLI-2)                    │
├──────────┬──────────────────────────┬────────────────────────┤
│          │                          │                        │
│  FILE    │       MAIN PANEL         │   METRICS PANEL        │
│  TREE    │  ┌───────────────────┐   │  ┌─────────────────┐  │
│          │  │   User Prompt     │   │  │  Token Gauge    │  │
│  ├─src   │  └───────────────────┘   │  │     (75%)       │  │
│  │├main  │  ┌───────────────────┐   │  └─────────────────┘  │
│  ││.py   │  │                   │   │  ┌─────────────────┐  │
│  │├utils │  │   Code Block      │   │  │  Safety Index   │  │
│  │.docker│  │   (Syntax)        │   │  │  (Bar Chart)    │  │
│          │  │                   │   │  └─────────────────┘  │
│          │  └───────────────────┘   │  ┌─────────────────┐  │
│          │  ┌───────────────────┐   │  │ Model Status    │  │
│          │  │   Terminal Log    │   │  │ Environment     │  │
│          │  │   [INFO] Step 1   │   │  └─────────────────┘  │
│          │  │   [INFO] Step 2   │   │                        │
│          │  └───────────────────┘   │                        │
└──────────┴──────────────────────────┴────────────────────────┘
```

---

## TAILWIND CSS INTEGRATION STRATEGY

### 1. CDN Injection (Fastest Path)
Since Gradio 6 supports custom CSS/JS in `launch()`, inject Tailwind via CDN:

```python
TAILWIND_CDN = """
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          'cyber-bg': '#0A0E14',
          'cyber-panel': '#141922',
          'cyber-accent': '#00D9FF',
          'cyber-text': '#E6E6E6',
        },
        boxShadow: {
          'neon-cyan': '0 0 20px rgba(0, 217, 255, 0.5)',
          'neon-soft': '0 0 10px rgba(0, 217, 255, 0.3)',
        },
        animation: {
          'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        }
      }
    }
  }
</script>
"""
```

### 2. Custom CSS Layer (Cyberpunk Specifics)
```css
/* cyber_theme.css */
@layer components {
  /* Neon Borders */
  .cyber-border {
    @apply border border-cyber-accent/20 rounded-lg;
    box-shadow: 0 0 10px rgba(0, 217, 255, 0.1) inset;
  }
  
  /* Glowing Text */
  .cyber-glow {
    text-shadow: 0 0 10px rgba(0, 217, 255, 0.8);
  }
  
  /* Panel Glass Effect */
  .cyber-glass {
    @apply bg-cyber-panel/80 backdrop-blur-xl;
    border: 1px solid rgba(0, 217, 255, 0.15);
  }
  
  /* Animated Border */
  .cyber-border-animated {
    position: relative;
    background: linear-gradient(90deg, 
      transparent 0%,
      rgba(0, 217, 255, 0.4) 50%,
      transparent 100%
    );
    background-size: 200% 100%;
    animation: border-slide 3s linear infinite;
  }
  
  @keyframes border-slide {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
}
```

---

## COMPONENT BREAKDOWN

### A. File Tree Panel (Left Column)
**Gradio Component**: `gr.FileExplorer` + Custom CSS

```python
with gr.Column(scale=1, elem_classes="cyber-glass cyber-border"):
    gr.Markdown("### PROJECT-ALPHA", elem_classes="cyber-glow font-mono text-sm")
    
    file_explorer = gr.FileExplorer(
        root_dir=PROJECT_ROOT,
        glob="**/*",
        height=500,
        elem_classes="font-mono text-xs"
    )
```

**CSS Targeting**:
```css
/* Style the file tree icons */
.file-explorer .folder-icon::before {
  content: "📁";
  filter: hue-rotate(180deg); /* Blue tint */
}

.file-explorer .file-icon::before {
  content: "📄";
  filter: brightness(1.5);
}

/* Hover effect */
.file-explorer .item:hover {
  background: rgba(0, 217, 255, 0.1);
  border-left: 2px solid var(--cyber-accent);
}
```

---

### B. Main Panel (Center)
**Chat + Code Block + Terminal**

#### User Prompt Section
```python
with gr.Row(elem_classes="cyber-border-animated mb-4"):
    user_input = gr.Textbox(
        placeholder="User: generate a python script for a simple web server.",
        show_label=False,
        lines=2,
        elem_classes="bg-cyber-panel text-cyber-text font-sans"
    )
```

#### Code Block (Syntax Highlighted)
```python
code_output = gr.Code(
    language="python",
    value="",  # Streamed
    interactive=False,
    elem_classes="cyber-border shadow-neon-soft",
    lines=12
)
```

**Custom Syntax Theme** (Override Gradio's default):
```css
/* CodeMirror overrides for cyberpunk syntax */
.cm-editor {
  background: #0A0E14 !important;
  color: #E6E6E6 !important;
}

.cm-keyword { color: #FF79C6 !important; }  /* Pink for keywords */
.cm-string { color: #F1FA8C !important; }   /* Yellow strings */
.cm-comment { color: #6272A4 !important; }  /* Muted comments */
.cm-function { color: #50FA7B !important; } /* Green functions */
```

#### Terminal Log Section
```python
terminal_log = gr.Code(
    language="shell",
    value="[INFO] Building Docker image...\n[INFO] Step 1/5...",
    interactive=False,
    elem_classes="cyber-glass font-mono text-xs",
    lines=8
)
```

**Custom Styling**:
```css
/* Terminal-specific colors */
.terminal-log .log-info { color: #3B82F6; }      /* Blue */
.terminal-log .log-success { color: #10B981; }   /* Green */
.terminal-log .log-error { color: #EF4444; }     /* Red */
.terminal-log .log-warning { color: #F59E0B; }   /* Orange */

/* Blinking cursor */
.terminal-log::after {
  content: "█";
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}
```

---

### C. Metrics Panel (Right Column)

#### 1. Token Budget Gauge (Circular Progress)
**Implementation**: Custom HTML component via `gr.HTML`

```python
def render_gauge(percentage: float, label: str, max_value: str) -> str:
    """Render SVG circular gauge with Tailwind styling"""
    radius = 70
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100) * circumference
    
    return f"""
    <div class="flex flex-col items-center justify-center p-6 cyber-glass cyber-border">
        <h3 class="text-sm font-mono text-cyber-text mb-4">{label}</h3>
        <svg width="180" height="180" class="transform -rotate-90">
            <!-- Background circle -->
            <circle cx="90" cy="90" r="{radius}"
                    fill="none" stroke="rgba(0,217,255,0.1)" stroke-width="12"/>
            <!-- Progress circle -->
            <circle cx="90" cy="90" r="{radius}"
                    fill="none" stroke="#00D9FF" stroke-width="12"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    stroke-linecap="round"
                    class="animate-pulse-slow"
                    style="filter: drop-shadow(0 0 8px rgba(0,217,255,0.8))"/>
        </svg>
        <div class="absolute text-center">
            <p class="text-4xl font-bold text-cyber-accent cyber-glow">{percentage}%</p>
            <p class="text-xs text-cyber-text/60 mt-1">{label}</p>
            <p class="text-xs text-cyber-text/40 font-mono">{max_value}</p>
        </div>
    </div>
    """

# Usage in Gradio
token_gauge = gr.HTML(render_gauge(75, "Token Budget", "750,000/1M"))
```

#### 2. Safety Index Bar Chart
```python
def render_bar_chart(values: List[float], label: str) -> str:
    """Render horizontal bar chart for safety metrics"""
    bars_html = ""
    for i, val in enumerate(values):
        height_percent = (val / max(values)) * 100
        bars_html += f"""
        <div class="flex items-end" style="height: 60px;">
            <div class="w-3 bg-gradient-to-t from-cyber-warning to-cyber-accent rounded-t"
                 style="height: {height_percent}%"
                 onmouseover="this.style.filter='brightness(1.3)'"
                 onmouseout="this.style.filter='brightness(1)'">
            </div>
        </div>
        """
    
    return f"""
    <div class="cyber-glass cyber-border p-4">
        <h3 class="text-sm font-mono text-cyber-text mb-2">{label}</h3>
        <div class="flex gap-1 justify-between items-end h-20">
            {bars_html}
        </div>
        <p class="text-xs text-right text-cyber-text/60 mt-2 font-mono">46ms</p>
    </div>
    """

safety_chart = gr.HTML(render_bar_chart([0.6, 0.8, 0.9, 0.7, 0.85, 0.95], "Safety Index (CPI)"))
```

#### 3. Dual Status Gauges (Model + Environment)
```python
def render_dual_gauge(left_val: float, left_label: str, 
                     right_val: float, right_label: str) -> str:
    """Render two small circular gauges side-by-side"""
    def mini_gauge(val, label, color):
        return f"""
        <div class="flex flex-col items-center">
            <svg width="80" height="80" class="transform -rotate-90">
                <circle cx="40" cy="40" r="30"
                        fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="6"/>
                <circle cx="40" cy="40" r="30"
                        fill="none" stroke="{color}" stroke-width="6"
                        stroke-dasharray="{2*3.14*30}"
                        stroke-dashoffset="{2*3.14*30*(1-val/100)}"
                        stroke-linecap="round"/>
            </svg>
            <p class="text-xs font-mono text-cyber-text mt-2">{label}</p>
            <p class="text-lg font-bold" style="color:{color}">{val}%</p>
        </div>
        """
    
    return f"""
    <div class="cyber-glass cyber-border p-4 flex gap-4 justify-around">
        {mini_gauge(left_val, left_label, "#00D9FF")}
        {mini_gauge(right_val, right_label, "#F59E0B")}
    </div>
    """

status_gauges = gr.HTML(
    render_dual_gauge(100, "Model: Pro 1.5", 100, "Environment: Production")
)
```

---

## ANIMATION & INTERACTIONS

### 1. Real-time Streaming Effect
```python
async def stream_with_typewriter_effect(text: str):
    """Simulate terminal typing effect"""
    for i in range(0, len(text), 3):
        chunk = text[:i+3]
        yield gr.update(value=chunk + "█")  # Blinking cursor
        await asyncio.sleep(0.05)
    
    yield gr.update(value=text)  # Final without cursor
```

### 2. Border Glow on Activity
```css
/* Pulse border when streaming */
@keyframes border-pulse {
  0%, 100% { box-shadow: 0 0 10px rgba(0,217,255,0.3); }
  50% { box-shadow: 0 0 20px rgba(0,217,255,0.8); }
}

.streaming-active {
  animation: border-pulse 1.5s ease-in-out infinite;
}
```

### 3. Gauge Updates (Smooth Transitions)
```javascript
// Inject via gr.HTML in footer
<script>
  function updateGauge(elementId, newPercentage) {
    const circle = document.querySelector(`#${elementId} circle:last-child`);
    const circumference = 2 * Math.PI * 70;
    const offset = circumference - (newPercentage / 100) * circumference;
    
    circle.style.transition = 'stroke-dashoffset 0.5s ease-out';
    circle.style.strokeDashoffset = offset;
  }
</script>
```

---

## IMPLEMENTATION PHASES

### Phase 1: Structure (1 hour)
- [x] Set up 3-column layout with correct scales
- [x] Inject Tailwind CDN
- [x] Apply base cyber color palette

### Phase 2: Components (2 hours)
- [ ] File tree with custom icons and hover effects
- [ ] Code block with cyberpunk syntax theme
- [ ] Terminal log with colored output
- [ ] User input with animated border

### Phase 3: Metrics Panel (2 hours)
- [ ] Token budget circular gauge (SVG)
- [ ] Safety index bar chart
- [ ] Dual status gauges
- [ ] Real-time data binding

### Phase 4: Polish (1 hour)
- [ ] Smooth animations and transitions
- [ ] Hover effects and micro-interactions
- [ ] Loading states and spinners
- [ ] Responsive adjustments

### Phase 5: Integration (1 hour)
- [ ] Connect metrics to real CLI data
- [ ] Stream updates to gauges
- [ ] Test all interactions
- [ ] Performance optimization

---

## LAUNCH CONFIGURATION (Gradio 6)

```python
# In gradio_ui/app.py

from pathlib import Path

# Load custom CSS and JS
CYBER_CSS = Path("gradio_ui/cyber_theme.css").read_text()
CYBER_JS = Path("gradio_ui/cyber_interactions.js").read_text()

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    show_error=True,
    theme=None,  # We handle styling via CSS
    css=CYBER_CSS,
    js=CYBER_JS,
    allowed_paths=[str(PROJECT_ROOT)],  # For file explorer
    ssr_mode=False,  # Disable SSR for custom components
)
```

---

## EDGE CASES & FALLBACKS

### 1. No Tailwind CDN (Offline Mode)
- Include Tailwind standalone build in `static/`
- Fallback to inline critical CSS

### 2. Browser Compatibility
- Test backdrop-filter support (Safari 9+, Chrome 76+)
- Fallback to solid backgrounds for older browsers

### 3. Performance (Large Logs)
- Virtual scrolling for terminal output (&gt;10K lines)
- Debounce gauge updates (max 10Hz refresh)

---

## SUCCESS CRITERIA

✅ **Visual Parity**: 95%+ match to reference image  
✅ **Smooth Animations**: 60fps gauge updates  
✅ **Responsive**: Works on 1920x1080 minimum  
✅ **Real-time**: Metrics update with &lt;100ms latency  
✅ **Accessible**: Keyboard navigation works  

---

**END OF PLAN · READY FOR IMPLEMENTATION**
