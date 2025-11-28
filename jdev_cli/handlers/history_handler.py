"""
HistoryHandler - History and Session Commands.

SCALE & SUSTAIN Phase 1.2 - CC Reduction.

Handles: /history, /stats, /sessions

Author: JuanCS Dev
Date: 2025-11-26
"""

from typing import TYPE_CHECKING

from rich.table import Table

from .dispatcher import CommandResult

if TYPE_CHECKING:
    from jdev_cli.shell_main import InteractiveShell


class HistoryHandler:
    """Handler for history and session commands."""

    def __init__(self, shell: 'InteractiveShell'):
        """Initialize with shell reference."""
        self.shell = shell
        self.console = shell.console

    async def handle_history(self, cmd: str) -> CommandResult:
        """Handle /history command."""
        entries = self.shell.cmd_history.get_recent(limit=20)
        if not entries:
            self.console.print("[dim]No command history yet.[/dim]")
            return CommandResult.ok()

        table = Table(title="Command History (Last 20)")
        table.add_column("#", style="dim", width=4)
        table.add_column("Time", style="cyan", width=10)
        table.add_column("Command", style="white")
        table.add_column("Status", style="green", width=8)
        table.add_column("Duration", style="yellow", width=10)

        for i, entry in enumerate(reversed(entries), 1):
            status = "✓ OK" if entry.success else "✗ FAIL"
            status_style = "green" if entry.success else "red"
            time_str = entry.timestamp.split('T')[1][:8]
            cmd_preview = entry.command[:60] + "..." if len(entry.command) > 60 else entry.command

            table.add_row(
                str(i),
                time_str,
                cmd_preview,
                f"[{status_style}]{status}[/{status_style}]",
                f"{entry.duration_ms}ms"
            )

        self.console.print(table)
        return CommandResult.ok()

    async def handle_stats(self, cmd: str) -> CommandResult:
        """Handle /stats command."""
        stats = self.shell.cmd_history.get_statistics(days=7)

        self.console.print("\n[bold cyan]📊 Command Statistics (Last 7 Days)[/bold cyan]\n")
        self.console.print(f"  Total commands: [bold]{stats['total_commands']}[/bold]")
        self.console.print(f"  Success rate:   [bold green]{stats['success_rate']}%[/bold green]")
        self.console.print(f"  Avg duration:   [yellow]{stats['avg_duration_ms']}ms[/yellow]")
        self.console.print(f"  Total tokens:   [cyan]{stats['total_tokens']:,}[/cyan]")

        if stats['top_commands']:
            self.console.print("\n[bold]Top Commands:[/bold]")
            for cmd_stat in stats['top_commands'][:5]:
                cmd_preview = cmd_stat['command'][:50]
                self.console.print(f"  • {cmd_preview}: [bold]{cmd_stat['count']}[/bold] times")

        return CommandResult.ok()

    async def handle_sessions(self, cmd: str) -> CommandResult:
        """Handle /sessions command."""
        sessions = self.shell.session_replay.list_sessions(limit=10)
        if not sessions:
            self.console.print("[dim]No previous sessions found.[/dim]")
            return CommandResult.ok()

        table = Table(title="Recent Sessions")
        table.add_column("Session ID", style="cyan")
        table.add_column("Start Time", style="yellow")
        table.add_column("Commands", style="white", width=10)
        table.add_column("Tokens", style="magenta", width=10)
        table.add_column("Files", style="green", width=8)

        for session in sessions:
            start_time = session['start_time'].split('T')[0]
            table.add_row(
                session['session_id'][:20] + "...",
                start_time,
                str(session['command_count']),
                f"{session['total_tokens']:,}",
                str(len(session['files_modified']))
            )

        self.console.print(table)
        return CommandResult.ok()
