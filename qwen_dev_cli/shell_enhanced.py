"""
Enhanced Interactive Shell with Cursor-level Intelligence.

Integrates all TUI components and intelligence features:
- Context-aware autocomplete
- File tree sidebar
- Toast notifications
- Context pills
- Semantic codebase indexing
- Smart suggestions

"I can do all things through him who strengthens me."
- Philippians 4:13

Created: 2025-11-19 00:50 UTC
"""

import asyncio
import os
from typing import Optional, Dict, Any
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.shortcuts import CompleteStyle

from rich.console import Console
from rich.live import Live

from .shell import InteractiveShell
from .tui.components import (
    ContextAwareCompleter,
    SmartAutoSuggest,
    FileTree,
    PillBar,
    ToastManager,
    create_completer
)
from .tui.theme import COLORS
from .tui.styles import get_rich_theme


class EnhancedShell(InteractiveShell):
    """
    Enhanced interactive shell with Cursor-level features.
    
    New capabilities:
    - Context-aware autocomplete
    - File tree sidebar (optional)
    - Toast notifications
    - Context pills showing active files
    - Smart inline suggestions
    """
    
    def __init__(self, llm_client=None, session_id: Optional[str] = None, show_sidebar: bool = False):
        # Initialize base shell
        super().__init__(llm_client, session_id)
        
        # Enhanced components
        self.show_sidebar = show_sidebar
        self.pill_bar = PillBar(self.console)
        self.toast_manager = ToastManager(self.console, max_toasts=3)
        
        # File tree (optional sidebar)
        self.file_tree: Optional[FileTree] = None
        if self.show_sidebar:
            self.file_tree = FileTree(
                root_path=Path.cwd(),
                console=self.console,
                max_depth=3,
                show_hidden=False
            )
            self.file_tree.build_tree()
        
        # Enhanced autocomplete
        self.completer = create_completer(
            tools_registry=self.registry,
            indexer=self.indexer,
            recent_tracker=self.recent_files
        )
        
        # Smart auto-suggest
        history_file = Path.home() / ".qwen_shell_history"
        self.auto_suggest = SmartAutoSuggest(
            history=FileHistory(str(history_file)),
            indexer=self.indexer
        )
        
        # Recreate prompt session with enhanced features
        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=self.completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
            enable_history_search=True,
            key_bindings=self._create_key_bindings()
        )
        
        # Track context pills
        self._update_context_pills()
    
    def _create_key_bindings(self) -> KeyBindings:
        """Create custom key bindings."""
        kb = KeyBindings()
        
        # Ctrl+T: Toggle file tree
        @kb.add('c-t')
        def toggle_tree(event):
            """Toggle file tree sidebar."""
            self.show_sidebar = not self.show_sidebar
            if self.show_sidebar and not self.file_tree:
                self.file_tree = FileTree(
                    root_path=Path.cwd(),
                    console=self.console,
                    max_depth=3
                )
                self.file_tree.build_tree()
            self.toast_manager.show(
                f"File tree {'enabled' if self.show_sidebar else 'disabled'}",
                title="View"
            )
        
        # Ctrl+R: Refresh indexer
        @kb.add('c-r')
        def refresh_indexer(event):
            """Refresh semantic indexer."""
            self.toast_manager.show("Refreshing codebase index...", title="Indexer")
            # Trigger async refresh
            asyncio.create_task(self._refresh_indexer())
        
        # Ctrl+K: Show command palette (future)
        @kb.add('c-k')
        def show_palette(event):
            """Show command palette."""
            self.toast_manager.show("Command palette coming soon!", title="Feature")
        
        return kb
    
    async def _refresh_indexer(self):
        """Refresh semantic indexer asynchronously."""
        try:
            await self.indexer.index_codebase_async()
            self.indexer.save_cache()
            self.toast_manager.show(
                f"Indexed {self.indexer.get_stats()['total_files']} files",
                title="✅ Indexer Complete"
            )
        except Exception as e:
            self.toast_manager.show(
                f"Failed: {str(e)}",
                title="❌ Indexer Error"
            )
    
    def _update_context_pills(self):
        """Update context pills based on current session."""
        # Clear existing
        self.pill_bar.clear()
        
        # Add recently modified files
        for file_path in list(self.context.modified_files)[:5]:
            from .tui.components import create_file_pill
            self.pill_bar.add(
                text=Path(file_path).name,
                type=create_file_pill(file_path).type,
                metadata={"path": file_path}
            )
        
        # Add recently read files
        for file_path in list(self.context.read_files)[:3]:
            if file_path not in self.context.modified_files:
                from .tui.components import create_file_pill
                self.pill_bar.add(
                    text=Path(file_path).name,
                    type=create_file_pill(file_path).type,
                    metadata={"path": file_path, "readonly": True}
                )
    
    async def run(self):
        """Run enhanced shell with sidebar support."""
        self.console.print(f"\n[bold {COLORS['primary']}]🚀 Qwen Dev CLI - Enhanced Shell[/]")
        self.console.print(f"[dim {COLORS['muted']}]Type 'help' for available commands, 'exit' to quit[/]\n")
        
        # Show keyboard shortcuts
        shortcuts = [
            ("Ctrl+T", "Toggle file tree"),
            ("Ctrl+R", "Refresh indexer"),
            ("Ctrl+K", "Command palette"),
            ("Tab", "Autocomplete"),
            ("Ctrl+C", "Cancel")
        ]
        
        self.console.print("[bold]Shortcuts:[/]")
        for key, desc in shortcuts:
            self.console.print(f"  [bold {COLORS['accent']}]{key}[/]: {desc}")
        self.console.print()
        
        # Initialize indexer if not done
        if not self._indexer_initialized:
            self.toast_manager.show("Initializing codebase indexer...", title="Startup")
            await self._initialize_indexer()
        
        # Main loop
        while True:
            try:
                # Render context pills if any
                pills_view = self.pill_bar.render()
                if pills_view:
                    self.console.print(pills_view)
                
                # Render file tree if enabled
                if self.show_sidebar and self.file_tree:
                    tree_panel = self.file_tree.render()
                    self.console.print(tree_panel)
                
                # Get user input with enhanced prompt
                user_input = await self._get_input_async()
                
                if not user_input or not user_input.strip():
                    continue
                
                if user_input.strip().lower() in ['exit', 'quit', 'q']:
                    self.toast_manager.show("Goodbye! 👋", title="Shell")
                    break
                
                # Process input
                await self._process_input(user_input)
                
                # Update context pills
                self._update_context_pills()
                
            except KeyboardInterrupt:
                self.console.print(f"\n[{COLORS['warning']}]Interrupted[/]")
                continue
            except EOFError:
                break
        
        # Cleanup
        self.file_watcher.stop()
        self.toast_manager.stop()
        self.console.print(f"\n[{COLORS['success']}]✅ Shell closed gracefully[/]")
    
    async def _get_input_async(self) -> str:
        """Get user input with enhanced prompt."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            prompt_text = f"[{COLORS['accent']}]❯[/] "
            return await loop.run_in_executor(
                None,
                lambda: self.session.prompt(prompt_text)
            )
        except Exception as e:
            return ""
    
    async def _initialize_indexer(self):
        """Initialize semantic indexer."""
        try:
            # Create progress toast
            toast = self.toast_manager.show_progress(
                "Scanning files...",
                title="Indexer",
                progress=0.0
            )
            
            # Index with progress updates
            stats = await self.indexer.index_codebase_async(
                on_progress=lambda p, msg: self.toast_manager.update_progress(
                    toast.id, p, msg
                )
            )
            
            # Dismiss progress toast
            self.toast_manager.dismiss(toast.id)
            
            # Show success
            self.toast_manager.show(
                f"Indexed {stats['total_files']} files, {stats['total_symbols']} symbols",
                title="✅ Indexer Ready"
            )
            
            self._indexer_initialized = True
            
        except Exception as e:
            self.toast_manager.show(
                f"Failed to initialize: {str(e)}",
                title="❌ Indexer Error"
            )
    
    async def _process_input(self, user_input: str):
        """Process user input with enhanced feedback."""
        # Show processing toast
        processing_toast = self.toast_manager.show_progress(
            "Thinking...",
            title="🤔 AI",
            progress=0.0
        )
        
        try:
            # Get biblical wisdom while thinking
            from .tui.biblical_wisdom import get_random_wisdom
            wisdom = get_random_wisdom()
            self.console.print(f"\n[dim italic {COLORS['muted']}]💭 {wisdom['text']}[/]")
            self.console.print(f"[dim {COLORS['muted']}]   — {wisdom['reference']}[/]\n")
            
            # Process with base shell
            response = await self._process_user_input(user_input)
            
            # Dismiss processing toast
            self.toast_manager.dismiss(processing_toast.id)
            
            # Show completion toast
            self.toast_manager.show(
                "Processing complete",
                title="✅ Done"
            )
            
            # Display response
            self.console.print()
            
        except Exception as e:
            self.toast_manager.dismiss(processing_toast.id)
            self.toast_manager.show(
                str(e),
                title="❌ Error"
            )
            raise


def create_enhanced_shell(
    llm_client=None,
    session_id: Optional[str] = None,
    show_sidebar: bool = False
) -> EnhancedShell:
    """Create enhanced shell instance."""
    return EnhancedShell(
        llm_client=llm_client,
        session_id=session_id,
        show_sidebar=show_sidebar
    )
