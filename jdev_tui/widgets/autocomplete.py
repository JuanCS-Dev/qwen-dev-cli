"""
Autocomplete Dropdown Widget.

Fuzzy autocomplete dropdown for commands and tools.
Shows suggestions as user types, with fuzzy matching.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Static


class AutocompleteDropdown(VerticalScroll):
    """
    Fuzzy autocomplete dropdown for commands and tools.

    Shows suggestions as user types, with fuzzy matching.
    """

    DEFAULT_CSS = """
    AutocompleteDropdown {
        layer: autocomplete;
        background: $surface;
        border: round $primary;
        padding: 0;
        max-height: 16;
        min-height: 1;
        width: 100%;
        display: none;
        scrollbar-size: 0 0;
    }

    AutocompleteDropdown.visible {
        display: block;
    }

    AutocompleteDropdown .item {
        padding: 0 1;
        height: 1;
        color: $foreground;
    }

    AutocompleteDropdown .item.selected {
        background: $secondary;
    }

    AutocompleteDropdown .item-command {
        color: #b84700;
    }

    AutocompleteDropdown .item-tool {
        color: #b84700;
    }

    AutocompleteDropdown .item-file {
        color: #8b4513;
    }

    AutocompleteDropdown .item-desc {
        color: #6b5200;
    }
    """

    selected_index: reactive[int] = reactive(0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items: List[Dict] = []
        self._item_widgets: List[Static] = []

    def show_completions(self, completions: List[Dict]) -> None:
        """Show completion items."""
        self.items = completions
        self.selected_index = 0

        # Clear existing
        for widget in self._item_widgets:
            widget.remove()
        self._item_widgets.clear()

        if not completions:
            self.remove_class("visible")
            return

        # Add items
        for i, item in enumerate(completions[:15]):  # Max 15 items
            item_type = item.get("type", "tool")

            # Use display from item if available
            if "display" in item:
                text = item["display"]
            else:
                icon = "⚡" if item_type == "command" else "🔧"
                text = f"{icon} {item['text']}"

            # Add description if available
            if desc := item.get("description"):
                text += f" [dim]{desc}[/dim]"

            # Set CSS class based on type
            type_class = f"item-{item_type}" if item_type in ("command", "tool", "file") else "item-tool"
            classes = f"item {type_class}"
            if i == 0:
                classes += " selected"

            widget = Static(text, classes=classes)
            self._item_widgets.append(widget)
            self.mount(widget)

        self.add_class("visible")

    def hide(self) -> None:
        """Hide dropdown."""
        self.remove_class("visible")
        for widget in self._item_widgets:
            widget.remove()
        self._item_widgets.clear()
        self.items = []

    def move_selection(self, delta: int) -> None:
        """Move selection up/down."""
        if not self.items:
            return

        # Update old selection
        if self._item_widgets and 0 <= self.selected_index < len(self._item_widgets):
            self._item_widgets[self.selected_index].remove_class("selected")

        # Calculate new index
        self.selected_index = (self.selected_index + delta) % len(self.items)

        # Update new selection
        if self._item_widgets and 0 <= self.selected_index < len(self._item_widgets):
            self._item_widgets[self.selected_index].add_class("selected")

    def get_selected(self) -> Optional[str]:
        """Get selected completion text."""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]["text"]
        return None
