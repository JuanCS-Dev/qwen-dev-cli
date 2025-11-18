#!/usr/bin/env python3
"""
Danger Detector - Visual warnings for dangerous commands.

Inspired by:
- rm-safety: Educational warnings before destructive operations
- GitHub: Branch protection warnings
- sudo: Elevation prompts with consequences
"""

import re
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class DangerLevel(Enum):
    """Danger levels for commands."""
    SAFE = 0          # ls, pwd, echo
    CAUTION = 1       # cp, mv, git commit
    DANGEROUS = 2     # rm, chmod 777
    CRITICAL = 3      # rm -rf /, dd, mkfs, fork bomb


@dataclass
class DangerWarning:
    """Warning information for dangerous command."""
    level: DangerLevel
    command: str
    risk_description: str
    consequences: List[str]
    requires_double_confirm: bool
    educational_tip: Optional[str] = None
    safer_alternative: Optional[str] = None


class DangerDetector:
    """Detect dangerous commands and provide visual warnings."""
    
    def __init__(self):
        self.patterns = self._build_danger_patterns()
    
    def _build_danger_patterns(self) -> Dict[str, DangerWarning]:
        """Build patterns for dangerous commands."""
        return {
            # CRITICAL - Can destroy system
            'rm_rf_root': DangerWarning(
                level=DangerLevel.CRITICAL,
                command='rm -rf /',
                risk_description="WILL DELETE ENTIRE SYSTEM",
                consequences=[
                    "💀 All files will be permanently deleted",
                    "💀 System will become unbootable",
                    "💀 No recovery possible without backups",
                    "💀 This is IRREVERSIBLE"
                ],
                requires_double_confirm=True,
                educational_tip="This command is NEVER what you want. Use specific paths.",
                safer_alternative="rm -rf /path/to/specific/directory"
            ),
            
            'dd_disk': DangerWarning(
                level=DangerLevel.CRITICAL,
                command='dd',
                risk_description="CAN DESTROY DATA PERMANENTLY",
                consequences=[
                    "⚠️  Can overwrite entire disks",
                    "⚠️  Wrong parameters = data loss",
                    "⚠️  No undo after execution",
                    "⚠️  Triple-check if= and of= parameters"
                ],
                requires_double_confirm=True,
                educational_tip="dd is a low-level tool. One typo can destroy your disk.",
                safer_alternative="Use higher-level tools like rsync or cp"
            ),
            
            'mkfs': DangerWarning(
                level=DangerLevel.CRITICAL,
                command='mkfs',
                risk_description="WILL FORMAT DISK",
                consequences=[
                    "💥 All data on disk will be erased",
                    "💥 Format is irreversible",
                    "💥 Verify device path multiple times"
                ],
                requires_double_confirm=True,
                educational_tip="mkfs creates a new filesystem, erasing all existing data.",
                safer_alternative="Backup data first, then format"
            ),
            
            'fork_bomb': DangerWarning(
                level=DangerLevel.CRITICAL,
                command=':(){ :|:& };:',
                risk_description="FORK BOMB - WILL CRASH SYSTEM",
                consequences=[
                    "💣 Will spawn infinite processes",
                    "💣 System will freeze/crash",
                    "💣 Requires hard reboot",
                    "💣 Can cause data loss"
                ],
                requires_double_confirm=True,
                educational_tip="This is malicious code. Never run it.",
                safer_alternative="DON'T RUN THIS"
            ),
            
            # DANGEROUS - High risk
            'chmod_777_recursive': DangerWarning(
                level=DangerLevel.DANGEROUS,
                command='chmod 777 -R',
                risk_description="MAJOR SECURITY RISK",
                consequences=[
                    "🔓 Anyone can read/write/execute",
                    "🔓 Malware can modify files",
                    "🔓 SSH may refuse to work",
                    "🔓 System becomes vulnerable"
                ],
                requires_double_confirm=True,
                educational_tip="777 permissions are almost never correct.",
                safer_alternative="chmod 755 or chmod 644 (specific permissions)"
            ),
            
            'rm_rf': DangerWarning(
                level=DangerLevel.DANGEROUS,
                command='rm -rf',
                risk_description="PERMANENT DELETION",
                consequences=[
                    "🗑️  Files deleted permanently (no trash)",
                    "🗑️  Cannot be recovered",
                    "🗑️  Double-check the path"
                ],
                requires_double_confirm=False,
                educational_tip="rm -rf is immediate. Consider using 'mv to trash' first.",
                safer_alternative="mv files to ~/.trash or use 'trash-cli'"
            ),
            
            'sudo_rm': DangerWarning(
                level=DangerLevel.DANGEROUS,
                command='sudo rm',
                risk_description="DELETING WITH ELEVATED PRIVILEGES",
                consequences=[
                    "⚡ Can delete system files",
                    "⚡ May break system",
                    "⚡ Very careful with paths"
                ],
                requires_double_confirm=False,
                educational_tip="sudo + rm = very dangerous combo. Verify path carefully.",
                safer_alternative="Don't use sudo unless absolutely necessary"
            ),
            
            # CAUTION - Medium risk
            'git_force_push': DangerWarning(
                level=DangerLevel.CAUTION,
                command='git push -f',
                risk_description="WILL OVERWRITE REMOTE HISTORY",
                consequences=[
                    "📝 Rewrites git history",
                    "📝 Can cause data loss for others",
                    "📝 Team members may lose work"
                ],
                requires_double_confirm=False,
                educational_tip="Force push rewrites history. Coordinate with team first.",
                safer_alternative="git push --force-with-lease (safer)"
            ),
            
            'git_reset_hard': DangerWarning(
                level=DangerLevel.CAUTION,
                command='git reset --hard',
                risk_description="WILL DISCARD UNCOMMITTED CHANGES",
                consequences=[
                    "📝 Uncommitted work will be lost",
                    "📝 Cannot be recovered",
                    "📝 Stash changes first if unsure"
                ],
                requires_double_confirm=False,
                educational_tip="Hard reset discards all local changes.",
                safer_alternative="git stash (saves changes)"
            ),
        }
    
    def analyze(self, command: str) -> Optional[DangerWarning]:
        """Analyze command and return danger warning if applicable."""
        cmd_lower = command.lower().strip()
        
        # Check for critical patterns first
        
        # Fork bomb
        if ':(){' in cmd_lower or ':|:&' in cmd_lower:
            return self.patterns['fork_bomb']
        
        # rm -rf /
        if re.search(r'rm\s+.*-rf.*\s+/[^/\w]|rm\s+.*-rf.*\s+/$', cmd_lower):
            return self.patterns['rm_rf_root']
        
        # dd with disk devices
        if 'dd' in cmd_lower and ('/dev/sd' in cmd_lower or '/dev/nvme' in cmd_lower):
            return self.patterns['dd_disk']
        
        # mkfs
        if cmd_lower.startswith('mkfs') or ' mkfs' in cmd_lower:
            return self.patterns['mkfs']
        
        # chmod 777 recursive
        if 'chmod' in cmd_lower and '777' in cmd_lower and ('-R' in command or '-r' in cmd_lower):
            return self.patterns['chmod_777_recursive']
        
        # rm -rf (any path)
        if 'rm' in cmd_lower and '-rf' in cmd_lower.replace(' ', ''):
            return self.patterns['rm_rf']
        
        # sudo rm
        if cmd_lower.startswith('sudo') and 'rm' in cmd_lower:
            return self.patterns['sudo_rm']
        
        # git force push
        if 'git' in cmd_lower and 'push' in cmd_lower and ('-f' in cmd_lower or '--force' in cmd_lower):
            return self.patterns['git_force_push']
        
        # git reset --hard
        if 'git' in cmd_lower and 'reset' in cmd_lower and '--hard' in cmd_lower:
            return self.patterns['git_reset_hard']
        
        return None
    
    def get_visual_warning(self, warning: DangerWarning) -> str:
        """Generate rich visual warning text."""
        from rich.panel import Panel
        from rich.text import Text
        from rich import box
        
        # Color based on danger level
        colors = {
            DangerLevel.CRITICAL: ("red", "💀"),
            DangerLevel.DANGEROUS: ("red", "⚠️"),
            DangerLevel.CAUTION: ("yellow", "⚡"),
            DangerLevel.SAFE: ("green", "✓"),
        }
        
        color, emoji = colors[warning.level]
        
        # Build warning text
        lines = []
        lines.append(f"\n[bold {color}]{emoji} {warning.level.name} {emoji}[/bold {color}]")
        lines.append(f"[bold]{warning.risk_description}[/bold]")
        lines.append("")
        lines.append("[bold]Consequences:[/bold]")
        for consequence in warning.consequences:
            lines.append(f"  {consequence}")
        
        if warning.educational_tip:
            lines.append("")
            lines.append(f"[dim]💡 Tip: {warning.educational_tip}[/dim]")
        
        if warning.safer_alternative:
            lines.append("")
            lines.append(f"[green]✓ Safer: {warning.safer_alternative}[/green]")
        
        text = "\n".join(lines)
        
        # Create panel
        panel = Panel(
            text,
            title=f"[bold {color}]⚠️  DANGER WARNING ⚠️[/bold {color}]",
            border_style=color,
            box=box.DOUBLE if warning.level == DangerLevel.CRITICAL else box.HEAVY
        )
        
        return panel
    
    def format_confirmation_prompt(self, warning: DangerWarning, command: str) -> str:
        """Format confirmation prompt based on danger level."""
        if warning.level == DangerLevel.CRITICAL:
            return f"[bold red]Type the command to confirm: [/bold red]"
        elif warning.requires_double_confirm:
            return f"[bold yellow]Type 'YES' (uppercase) to confirm: [/bold yellow]"
        else:
            return "[yellow]Execute? [y/N] [/yellow]"
    
    def validate_confirmation(self, warning: DangerWarning, user_input: str, command: str) -> bool:
        """Validate user confirmation based on danger level."""
        if warning.level == DangerLevel.CRITICAL:
            # Must type exact command
            return user_input.strip() == command.strip()
        elif warning.requires_double_confirm:
            # Must type YES in uppercase
            return user_input.strip() == "YES"
        else:
            # Standard y/n
            return user_input.lower() in ['y', 'yes']


# Global detector instance
danger_detector = DangerDetector()
