"""
WorkflowHandler - Workflow and Squad Commands.

SCALE & SUSTAIN Phase 1.2 - CC Reduction.

Handles: /workflow, /workflow list, /workflow run, /squad

Author: JuanCS Dev
Date: 2025-11-26
"""

from typing import TYPE_CHECKING

from .dispatcher import CommandResult

if TYPE_CHECKING:
    from jdev_cli.shell_main import InteractiveShell


class WorkflowHandler:
    """Handler for workflow and squad commands."""

    def __init__(self, shell: 'InteractiveShell'):
        """Initialize with shell reference."""
        self.shell = shell
        self.console = shell.console

    async def handle_workflow_status(self, cmd: str) -> CommandResult:
        """Handle /workflow command - show current workflow."""
        if self.shell.workflow_viz.current_workflow:
            viz = self.shell.workflow_viz.render_workflow()
            self.console.print(viz)
        else:
            self.console.print("[dim]No active workflow. Execute a command to see workflow.[/dim]")
        return CommandResult.ok()

    async def handle_workflow_list(self, cmd: str) -> CommandResult:
        """Handle /workflow list command."""
        self.shell._palette_list_workflows()
        return CommandResult.ok()

    async def handle_workflow_run(self, cmd: str) -> CommandResult:
        """Handle /workflow run <name> command."""
        workflow_name = cmd[14:].strip()  # Remove "/workflow run "

        from ..orchestration.workflows import WorkflowLibrary
        lib = WorkflowLibrary()
        workflow = lib.get_workflow(workflow_name)

        if not workflow:
            return CommandResult.error(f"[red]Workflow '{workflow_name}' not found[/red]")

        self.console.print(f"\n[bold blue]🚀 Starting Workflow:[/bold blue] {workflow.name}")
        self.console.print(f"[dim]{workflow.description}[/dim]\n")

        self.console.print("\n[bold green]📋 Execution Plan:[/bold green]")
        for i, step in enumerate(workflow.steps, 1):
            self.console.print(f"{i}. [cyan]{step.agent.upper()}[/cyan]: {step.description}")

        # Execute
        try:
            # Construct request from workflow
            request = f"Execute workflow '{workflow.name}': {workflow.description}\n\nSteps:\n"
            for step in workflow.steps:
                request += f"- {step.name}: {step.description}\n"

            with self.console.status(f"[bold green]Running Workflow {workflow_name}...[/bold green]"):
                result = await self.shell.squad.execute_workflow(request)
            self.console.print(self.shell.squad.get_phase_summary(result))
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")

        return CommandResult.ok()

    async def handle_squad(self, cmd: str) -> CommandResult:
        """Handle /squad <request> command."""
        request = cmd[7:].strip()  # Remove "/squad "

        if not request:
            return CommandResult.error("[red]Usage: /squad <mission description>[/red]")

        self.console.print(f"\n[bold blue]🤖 DevSquad Mission:[/bold blue] {request}\n")

        try:
            with self.console.status("[bold green]DevSquad Active...[/bold green]"):
                result = await self.shell.squad.execute_workflow(request)
            self.console.print(self.shell.squad.get_phase_summary(result))
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")

        return CommandResult.ok()
