"""
MemoryManager - Persistent Memory (MEMORY.md).

Extracted from Bridge as part of SCALE & SUSTAIN Phase 1.1.

Manages:
- MEMORY.md file operations
- Scoped memory (project/global)
- Note persistence

Author: JuanCS Dev
Date: 2025-11-26
"""

import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from jdev_tui.core.interfaces import IMemoryManager


class MemoryManager(IMemoryManager):
    """
    Persistent memory manager using MEMORY.md files.

    Implements IMemoryManager interface for:
    - Reading/writing memory files
    - Project and global scope support
    - Note appending with timestamps
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        global_dir: Optional[Path] = None
    ):
        """
        Initialize MemoryManager.

        Args:
            project_dir: Project directory. Defaults to cwd.
            global_dir: Global config directory. Defaults to ~/.config/juancs.
        """
        self._project_dir = project_dir or Path.cwd()
        self._global_dir = global_dir or (Path.home() / ".config" / "juancs")

    def _get_memory_file(self, scope: str = "project") -> Path:
        """
        Get memory file path for given scope.

        Args:
            scope: "project" or "global".

        Returns:
            Path to MEMORY.md file.
        """
        if scope == "global":
            self._global_dir.mkdir(parents=True, exist_ok=True)
            return self._global_dir / "MEMORY.md"
        else:
            return self._project_dir / "MEMORY.md"

    def read_memory(self, scope: str = "project") -> Dict[str, Any]:
        """
        Read memory from MEMORY.md file.

        Args:
            scope: "project" or "global".

        Returns:
            Dictionary with content and metadata.
        """
        memory_file = self._get_memory_file(scope)

        if not memory_file.exists():
            return {
                "success": True,
                "content": "",
                "exists": False,
                "file": str(memory_file),
                "scope": scope
            }

        try:
            content = memory_file.read_text()
            return {
                "success": True,
                "content": content,
                "exists": True,
                "file": str(memory_file),
                "scope": scope,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file": str(memory_file)
            }

    def write_memory(
        self,
        content: str,
        scope: str = "project",
        append: bool = False
    ) -> Dict[str, Any]:
        """
        Write to MEMORY.md file.

        Args:
            content: Content to write.
            scope: "project" or "global".
            append: If True, append to existing content.

        Returns:
            Dictionary with success status.
        """
        memory_file = self._get_memory_file(scope)

        try:
            if append and memory_file.exists():
                existing = memory_file.read_text()
                content = existing + "\n" + content

            memory_file.write_text(content)

            return {
                "success": True,
                "message": f"Memory {'appended to' if append else 'written to'} {memory_file}",
                "file": str(memory_file),
                "scope": scope
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def remember(self, note: str, scope: str = "project") -> Dict[str, Any]:
        """
        Add a timestamped note to memory.

        Args:
            note: Note content.
            scope: "project" or "global".

        Returns:
            Dictionary with success status.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted = f"\n## Note ({timestamp})\n{note}\n"
        return self.write_memory(formatted, scope=scope, append=True)

    def clear_memory(self, scope: str = "project") -> Dict[str, Any]:
        """
        Clear memory file.

        Args:
            scope: "project" or "global".

        Returns:
            Dictionary with success status.
        """
        memory_file = self._get_memory_file(scope)

        try:
            if memory_file.exists():
                memory_file.unlink()
            return {
                "success": True,
                "message": f"Memory cleared: {memory_file}",
                "scope": scope
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_memory_stats(self, scope: str = "project") -> Dict[str, Any]:
        """
        Get memory file statistics.

        Args:
            scope: "project" or "global".

        Returns:
            Dictionary with file statistics.
        """
        memory_file = self._get_memory_file(scope)

        if not memory_file.exists():
            return {
                "exists": False,
                "scope": scope,
                "file": str(memory_file)
            }

        try:
            content = memory_file.read_text()
            lines = content.split("\n")
            notes = len([l for l in lines if l.startswith("## Note")])

            return {
                "exists": True,
                "scope": scope,
                "file": str(memory_file),
                "size": len(content),
                "lines": len(lines),
                "notes": notes
            }
        except Exception as e:
            return {
                "exists": True,
                "error": str(e),
                "scope": scope
            }
