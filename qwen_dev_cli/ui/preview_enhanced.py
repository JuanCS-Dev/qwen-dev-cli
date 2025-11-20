"""Enhanced preview system with undo/redo and diff visualization."""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import difflib


@dataclass
class PreviewState:
    """Single preview state in undo stack."""
    timestamp: datetime
    content: str
    description: str
    file_path: Optional[str] = None


class PreviewUndoStack:
    """Undo/redo stack for preview changes."""
    
    def __init__(self, max_size: int = 20):
        """Initialize undo stack with maximum size."""
        self.max_size = max_size
        self.stack: List[PreviewState] = []
        self.current_index: int = -1
        
    def push(self, content: str, description: str = "", file_path: Optional[str] = None):
        """Add new state to stack."""
        # Remove any states after current index (they become invalid after new change)
        if self.current_index < len(self.stack) - 1:
            self.stack = self.stack[:self.current_index + 1]
            
        state = PreviewState(
            timestamp=datetime.now(),
            content=content,
            description=description,
            file_path=file_path
        )
        
        self.stack.append(state)
        
        # Limit stack size
        if len(self.stack) > self.max_size:
            self.stack.pop(0)
        else:
            self.current_index += 1
            
    def undo(self) -> Optional[PreviewState]:
        """Undo to previous state."""
        if self.can_undo():
            self.current_index -= 1
            return self.stack[self.current_index]
        return None
        
    def redo(self) -> Optional[PreviewState]:
        """Redo to next state."""
        if self.can_redo():
            self.current_index += 1
            return self.stack[self.current_index]
        return None
        
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.current_index > 0
        
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.current_index < len(self.stack) - 1
        
    def get_current(self) -> Optional[PreviewState]:
        """Get current state."""
        if 0 <= self.current_index < len(self.stack):
            return self.stack[self.current_index]
        return None
        
    def get_history(self) -> List[Dict]:
        """Get full history as serializable dict."""
        return [
            {
                "index": i,
                "timestamp": state.timestamp.isoformat(),
                "description": state.description,
                "file_path": state.file_path,
                "is_current": i == self.current_index
            }
            for i, state in enumerate(self.stack)
        ]


class DiffPreview:
    """Side-by-side diff preview with syntax highlighting."""
    
    @staticmethod
    def generate_unified_diff(original: str, modified: str, filename: str = "file") -> str:
        """Generate unified diff format."""
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=""
        )
        
        return "".join(diff)
        
    @staticmethod
    def generate_side_by_side(original: str, modified: str, width: int = 80) -> str:
        """Generate side-by-side diff view."""
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)
        result = []
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                for i in range(i1, i2):
                    result.append(f"  {original_lines[i][:width]:80} | {original_lines[i][:width]}")
            elif op == 'delete':
                for i in range(i1, i2):
                    result.append(f"- {original_lines[i][:width]:80} |")
            elif op == 'insert':
                for j in range(j1, j2):
                    result.append(f"+ {' ':80} | {modified_lines[j][:width]}")
            elif op == 'replace':
                max_len = max(i2 - i1, j2 - j1)
                for k in range(max_len):
                    left = original_lines[i1 + k][:width] if k < (i2 - i1) else ""
                    right = modified_lines[j1 + k][:width] if k < (j2 - j1) else ""
                    result.append(f"~ {left:80} | {right}")
                    
        return "\n".join(result)
        
    @staticmethod
    def get_change_stats(original: str, modified: str) -> Dict:
        """Calculate change statistics."""
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)
        
        additions = 0
        deletions = 0
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'delete':
                deletions += i2 - i1
            elif op == 'insert':
                additions += j2 - j1
            elif op == 'replace':
                deletions += i2 - i1
                additions += j2 - j1
                
        return {
            "additions": additions,
            "deletions": deletions,
            "total_changes": additions + deletions,
            "original_lines": len(original_lines),
            "modified_lines": len(modified_lines)
        }
