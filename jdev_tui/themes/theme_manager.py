"""
Theme Manager for JuanCS Dev-Code.

Provides dual theme system with:
- Claude Light: Inspired by Anthropic's warm design language
- Matrix Dark: Minimal cyberpunk with soft green (#1CA152)

Research sources:
- Textual Themes: https://textual.textualize.io/guide/design/
- Claude Brand: https://mobbin.com/colors/brand/claude
- Matrix Palette: https://www.schemecolor.com/matrix-code-green.php
"""

from enum import Enum
from pathlib import Path
from typing import Optional
import json

from textual.theme import Theme


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = "claude-light"
    DARK = "matrix-dark"


# =============================================================================
# THEME LIGHT - JuanCS Dev-Code Orange Theme
# =============================================================================
# Warm, professional aesthetic with orange/brown palette
# Primary: Dark Orange (#ff8c00) - JuanCS signature color
# Background: Pampas (#F4F3EE) - Soft, warm off-white

THEME_LIGHT = Theme(
    name="claude-light",
    primary="#ff8c00",      # Dark Orange - JuanCS primary
    secondary="#b8860b",    # Dark Goldenrod - Secondary accent
    accent="#ff6600",       # Orange - Action accent
    background="#F4F3EE",   # Pampas - Warm off-white
    surface="#FFFFFF",      # Pure white for cards/panels
    foreground="#1A1A1A",   # Near black for text
    success="#1DB954",      # Spotify green (universal)
    error="#DC3545",        # Bootstrap red (universal)
    warning="#F5A623",      # Amber
    dark=False,
    variables={
        # Text variations
        "text-muted": "#6B6B6B",
        "text-disabled": "#9CA3AF",

        # Border - Orange accent
        "border": "#E5E4E0",
        "border-hover": "#ff8c00",

        # Input styling - Orange cursor
        "input-cursor-foreground": "#ff8c00",
        "input-selection-background": "#ff8c0033",

        # Scrollbar - Orange accent
        "scrollbar": "#E5E4E0",
        "scrollbar-hover": "#ff8c00",

        # Footer - Orange keys
        "footer-key-foreground": "#ff8c00",
        "footer-description-foreground": "#6B6B6B",

        # Button
        "button-foreground": "#FFFFFF",

        # Panel/Surface
        "panel": "#FFFFFF",
        "panel-lighten-1": "#FAFAF9",
        "panel-darken-1": "#F5F5F4",

        # Code/Markdown inline code - Orange background
        "code-background": "#fff3e0",
        "code-foreground": "#cc4a0a",
    }
)


# =============================================================================
# THEME DARK - Matrix Cinematic
# =============================================================================
# Cyberpunk aesthetic with layered green hierarchy
#
# GREEN PALETTE (brightest to darkest):
#   - Neon Bright:  #39FF14  (highlights, important actions)
#   - Matrix Glow:  #00FF41  (primary text, active elements)
#   - Soft Green:   #1CA152  (standard text)
#   - Forest:       #0D5C2E  (muted/secondary)
#   - Dark Forest:  #0A3D1F  (disabled/background accents)
#
# Background: Pure Black (#000000) - Maximum contrast

THEME_DARK = Theme(
    name="matrix-dark",
    primary="#00FF41",      # Matrix Glow - Bright primary
    secondary="#1CA152",    # Soft Green - Secondary
    accent="#39FF14",       # Neon Bright - Highlights
    background="#000000",   # Pure Black
    surface="#050505",      # Near Black
    foreground="#1CA152",   # Soft Green - Main text (easier on eyes)
    success="#39FF14",      # Neon Bright for success
    error="#FF3131",        # Bright Red (visible on black)
    warning="#FFD700",      # Gold (more visible)
    dark=True,
    variables={
        # Text hierarchy (4 levels of green)
        "text": "#1CA152",              # Standard text
        "text-muted": "#0D5C2E",         # Muted/secondary
        "text-disabled": "#0A3D1F",      # Disabled

        # Border - subtle but visible
        "border": "#0D5C2E",
        "border-hover": "#00FF41",       # Bright on hover

        # Input styling - bright cursor
        "input-cursor-foreground": "#39FF14",
        "input-cursor-background": "#39FF14",
        "input-selection-background": "#00FF4133",

        # Scrollbar
        "scrollbar": "#0A3D1F",
        "scrollbar-hover": "#1CA152",

        # Footer - contrasting greens
        "footer-key-foreground": "#00FF41",      # Bright keys
        "footer-description-foreground": "#0D5C2E",

        # Button
        "button-foreground": "#000000",
        "button-background": "#00FF41",

        # Panel/Surface - subtle depth
        "panel": "#050505",
        "panel-lighten-1": "#0A0A0A",
        "panel-darken-1": "#000000",

        # Links and highlights
        "link": "#00FF41",
        "link-hover": "#39FF14",
    }
)


# =============================================================================
# THEME MANAGER
# =============================================================================

class ThemeManager:
    """
    Manages theme preferences with persistence.

    Stores preference in ~/.jdev_tui/config.json
    """

    CONFIG_DIR = Path.home() / ".jdev_tui"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    DEFAULT_THEME = ThemeMode.DARK

    @classmethod
    def get_theme_preference(cls) -> str:
        """Load saved theme preference or return default."""
        try:
            if cls.CONFIG_FILE.exists():
                config = json.loads(cls.CONFIG_FILE.read_text())
                return config.get("theme", cls.DEFAULT_THEME.value)
        except (json.JSONDecodeError, IOError):
            pass
        return cls.DEFAULT_THEME.value

    @classmethod
    def save_theme_preference(cls, theme_name: str) -> None:
        """Save theme preference to config file."""
        try:
            cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # Load existing config or create new
            config = {}
            if cls.CONFIG_FILE.exists():
                try:
                    config = json.loads(cls.CONFIG_FILE.read_text())
                except json.JSONDecodeError:
                    pass

            config["theme"] = theme_name
            cls.CONFIG_FILE.write_text(json.dumps(config, indent=2))
        except IOError:
            pass  # Silent fail - theme preference is non-critical

    @classmethod
    def toggle_theme(cls, current_theme: str) -> str:
        """
        Toggle between light and dark themes.

        Returns the new theme name.
        """
        if current_theme == ThemeMode.LIGHT.value:
            new_theme = ThemeMode.DARK.value
        else:
            new_theme = ThemeMode.LIGHT.value

        cls.save_theme_preference(new_theme)
        return new_theme

    @classmethod
    def get_available_themes(cls) -> list[Theme]:
        """Return list of all available themes."""
        return [THEME_LIGHT, THEME_DARK]

    @classmethod
    def get_theme_by_name(cls, name: str) -> Optional[Theme]:
        """Get theme object by name."""
        themes = {
            ThemeMode.LIGHT.value: THEME_LIGHT,
            ThemeMode.DARK.value: THEME_DARK,
        }
        return themes.get(name)
