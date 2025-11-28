"""
RefactorHandler - Refactoring Commands.

SCALE & SUSTAIN Phase 1.2 - CC Reduction.

Handles: /refactor rename, /refactor imports

Author: JuanCS Dev
Date: 2025-11-26
"""

from pathlib import Path
from typing import TYPE_CHECKING

from .dispatcher import CommandResult

if TYPE_CHECKING:
    from jdev_cli.shell_main import InteractiveShell


class RefactorHandler:
    """Handler for refactoring commands."""

    def __init__(self, shell: 'InteractiveShell'):
        """Initialize with shell reference."""
        self.shell = shell
        self.console = shell.console

    async def handle_rename(self, cmd: str) -> CommandResult:
        """Handle /refactor rename <file> <old> <new> command."""
        args = cmd[17:].strip().split()  # Remove "/refactor rename "

        if len(args) < 3:
            return CommandResult.error("[red]Usage: /refactor rename <file> <old_name> <new_name>[/red]")

        file_path = Path(args[0])
        old_name = args[1]
        new_name = args[2]

        if not file_path.exists():
            return CommandResult.error(f"[red]File not found: {file_path}[/red]")

        result = self.shell.refactoring_engine.rename_symbol(file_path, old_name, new_name)

        if result.success:
            self.console.print(f"[green]✓ {result.message}[/green]")
            self.console.print(f"[dim]{result.changes_preview}[/dim]")
        else:
            self.console.print(f"[red]✗ {result.message}: {result.error}[/red]")

        return CommandResult.ok()

    async def handle_imports(self, cmd: str) -> CommandResult:
        """Handle /refactor imports <file> command."""
        file_arg = cmd[18:].strip()  # Remove "/refactor imports "

        if not file_arg:
            return CommandResult.error("[red]Usage: /refactor imports <file>[/red]")

        file_path = Path(file_arg)

        if not file_path.exists():
            return CommandResult.error(f"[red]File not found: {file_path}[/red]")

        result = self.shell.refactoring_engine.organize_imports(file_path)

        if result.success:
            self.console.print(f"[green]✓ {result.message}[/green]")
        else:
            self.console.print(f"[red]✗ {result.message}: {result.error}[/red]")

        return CommandResult.ok()
