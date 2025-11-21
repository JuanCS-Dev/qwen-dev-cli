"""
Módulo de Componentes SVG/HTML para o Dashboard Cyberpunk.
Isola a lógica de visualização para manter o app.py limpo.
"""
from typing import List


def render_tailwind_header() -> str:
    """Injeta Tailwind e Configurações no Head"""
    return """
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
              'cyber-warning': '#F59E0B',
              'cyber-danger': '#EF4444',
            },
            fontFamily: {
              mono: ['JetBrains Mono', 'monospace'],
            }
          }
        }
      }
    </script>
    """


def render_gauge(percentage: float, label: str, max_value: str) -> str:
    """Renderiza um Gauge Circular SVG com brilho Neon"""
    radius = 60
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100) * circumference
    
    stroke_color = "#00D9FF"
    if percentage > 90:
        stroke_color = "#EF4444"  # Red warning
    elif percentage > 75:
        stroke_color = "#F59E0B"  # Orange warning
    
    return f"""
    <div class="flex flex-col items-center justify-center p-4 h-full">
        <div class="relative">
            <svg width="140" height="140" class="transform -rotate-90">
                <!-- Background circle -->
                <circle cx="70" cy="70" r="{radius}"
                        fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8"/>
                <!-- Progress circle -->
                <circle cx="70" cy="70" r="{radius}"
                        fill="none" stroke="{stroke_color}" stroke-width="8"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{offset}"
                        stroke-linecap="round"
                        class="transition-all duration-1000 ease-out"
                        style="filter: drop-shadow(0 0 8px {stroke_color}80)"/>
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-3xl font-bold text-white cyber-glow">{int(percentage)}%</span>
            </div>
        </div>
        <h3 class="text-xs font-mono text-cyber-text mt-2 tracking-widest">{label.upper()}</h3>
        <p class="text-[10px] text-gray-500 font-mono">{max_value}</p>
    </div>
    """


def render_bar_chart(values: List[float], label: str) -> str:
    """Renderiza gráfico de barras horizontal estilo equalizador"""
    bars_html = ""
    for val in values:
        height_percent = (val / 1.0) * 100  # Assumindo normalizado 0-1
        color_class = "bg-cyber-accent"
        if val < 0.5:
            color_class = "bg-cyber-warning"
        if val < 0.3:
            color_class = "bg-cyber-danger"
        
        bars_html += f"""
        <div class="flex items-end h-16 w-full mx-0.5 group">
            <div class="w-full {color_class} rounded-t opacity-60 group-hover:opacity-100 transition-all duration-300"
                 style="height: {height_percent}%; box-shadow: 0 0 10px {color_class}40;">
            </div>
        </div>
        """
    
    return f"""
    <div class="p-4 h-full flex flex-col justify-end">
        <div class="flex justify-between items-end mb-2">
            {bars_html}
        </div>
        <h3 class="text-xs font-mono text-cyber-text tracking-widest text-center">{label.upper()}</h3>
        <div class="flex justify-between text-[10px] text-gray-600 mt-1">
            <span>SAFE</span>
            <span>RISK</span>
        </div>
    </div>
    """


def render_dual_gauge(left_val: float, left_label: str, right_val: float, right_label: str) -> str:
    """Mini gauges lado a lado"""
    def mini_svg(val, color):
        circ = 2 * 3.14 * 20
        off = circ * (1 - val/100)
        return f"""
        <div class="relative w-12 h-12">
            <svg width="48" height="48" class="transform -rotate-90">
                <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="3"/>
                <circle cx="24" cy="24" r="20" fill="none" stroke="{color}" stroke-width="3"
                        stroke-dasharray="{circ}" stroke-dashoffset="{off}" stroke-linecap="round"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white">
                {int(val)}
            </div>
        </div>
        """
    
    return f"""
    <div class="flex justify-around items-center p-2 h-full">
        <div class="flex flex-col items-center">
            {mini_svg(left_val, "#00D9FF")}
            <span class="text-[10px] text-gray-400 mt-1">{left_label}</span>
        </div>
        <div class="w-px h-8 bg-gray-800"></div>
        <div class="flex flex-col items-center">
            {mini_svg(right_val, "#10B981")}
            <span class="text-[10px] text-gray-400 mt-1">{right_label}</span>
        </div>
    </div>
    """


def render_terminal_logs(logs: List[str]) -> str:
    """Formata logs para parecer terminal real"""
    html = '<div class="font-mono text-xs space-y-1 p-2">'
    for log in logs:
        color = "text-gray-400"
        if "[INFO]" in log:
            color = "text-blue-400"
        if "[SUCCESS]" in log:
            color = "text-green-400"
        if "[ERROR]" in log:
            color = "text-red-400"
        if "[WARN]" in log:
            color = "text-yellow-400"
        
        # Highlight timestamps
        parts = log.split(" - ", 1)
        if len(parts) == 2:
            html += f'<div><span class="text-gray-600">{parts[0]}</span> <span class="{color}">{parts[1]}</span></div>'
        else:
            html += f'<div class="{color}">{log}</div>'
    
    html += '<div><span class="text-cyber-accent">root@gemini-cli:~$</span> <span class="cursor-blink"></span></div>'
    html += '</div>'
    return html
