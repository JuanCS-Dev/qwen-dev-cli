"""
StatusManager - System Health and Permissions.

Extracted from Bridge as part of SCALE & SUSTAIN Phase 1.1.

Manages:
- System health checks
- Permission settings
- Sandbox mode

Author: JuanCS Dev
Date: 2025-11-26
"""

from typing import Any, Callable, Dict, Optional

from jdev_tui.core.interfaces import IStatusManager


class StatusManager(IStatusManager):
    """
    System status and health manager.

    Implements IStatusManager interface for:
    - Health checks across components
    - Permission management
    - Sandbox mode control
    """

    def __init__(
        self,
        llm_checker: Optional[Callable[[], bool]] = None,
        tool_counter: Optional[Callable[[], int]] = None,
        agent_counter: Optional[Callable[[], int]] = None
    ):
        """
        Initialize StatusManager.

        Args:
            llm_checker: Callable that returns True if LLM is connected.
            tool_counter: Callable that returns tool count.
            agent_counter: Callable that returns agent count.
        """
        self._sandbox = False
        self._llm_checker = llm_checker
        self._tool_counter = tool_counter
        self._agent_counter = agent_counter

    def check_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Check system health for all components.

        Returns:
            Dictionary with health status for each component.
        """
        health = {}

        # Check LLM
        if self._llm_checker:
            is_connected = self._llm_checker()
            health["LLM"] = {
                "ok": is_connected,
                "message": "Connected" if is_connected else "Not connected"
            }
        else:
            health["LLM"] = {
                "ok": False,
                "message": "LLM checker not configured"
            }

        # Check tools
        if self._tool_counter:
            tool_count = self._tool_counter()
            health["Tools"] = {
                "ok": tool_count > 0,
                "message": f"{tool_count} tools loaded"
            }
        else:
            health["Tools"] = {
                "ok": False,
                "message": "Tool counter not configured"
            }

        # Check agents
        if self._agent_counter:
            agent_count = self._agent_counter()
            health["Agents"] = {
                "ok": agent_count > 0,
                "message": f"{agent_count} agents available"
            }
        else:
            health["Agents"] = {
                "ok": False,
                "message": "Agent counter not configured"
            }

        # Check sandbox status
        health["Sandbox"] = {
            "ok": True,
            "message": "Enabled" if self._sandbox else "Disabled"
        }

        return health

    def get_permissions(self) -> Dict[str, bool]:
        """
        Get current system permissions.

        Returns:
            Dictionary of permission flags.
        """
        return {
            "read_files": True,
            "write_files": not self._sandbox,
            "execute_commands": not self._sandbox,
            "network_access": True,
            "sandbox_mode": self._sandbox
        }

    def set_sandbox(self, enabled: bool) -> None:
        """
        Enable or disable sandbox mode.

        Args:
            enabled: True to enable sandbox mode.
        """
        self._sandbox = enabled

    def is_sandbox_enabled(self) -> bool:
        """
        Check if sandbox mode is enabled.

        Returns:
            True if sandbox mode is enabled.
        """
        return self._sandbox

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of system status."""
        health = self.check_health()
        all_ok = all(comp.get("ok", False) for comp in health.values())
        return {
            "healthy": all_ok,
            "components": len(health),
            "failed": [name for name, status in health.items() if not status.get("ok", False)],
            "sandbox": self._sandbox
        }
