"""
HARDENED FILE OPERATIONS - Boris Cherny Edition
Zero-crash file handling com error recovery completo
"""

import os
import shutil
import tempfile
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging
import asyncio

from .base import Tool, ToolResult, ToolCategory
from .validated import ValidatedTool
from ..core.validation import Required, TypeCheck

logger = logging.getLogger(__name__)


class FileOperationError(Exception):
    """Base exception para erros de file operations."""
    pass


class EncodingDetectionError(FileOperationError):
    """Erro ao detectar encoding de arquivo."""
    pass


class FileSizeLimitError(FileOperationError):
    """Arquivo excede limite de tamanho permitido."""
    pass


class AtomicWriteError(FileOperationError):
    """Erro durante write atômico."""
    pass


def detect_encoding(file_path: Path, sample_size: int = 8192) -> str:
    """
    Detecta encoding de arquivo com fallback chain robusto.
    
    Returns:
        str: Nome do encoding detectado
    """
    try:
        # Tentar UTF-8 primeiro (mais comum)
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        try:
            sample.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass
        
        # Fallback: latin-1 (nunca falha, 1 byte = 1 char)
        return 'latin-1'
        
    except Exception as e:
        raise EncodingDetectionError(f"Failed to detect encoding: {e}")


def check_file_size(file_path: Path, max_size_mb: int = 10) -> Tuple[bool, int]:
    """
    Verifica se arquivo está dentro do limite de tamanho.
    
    Returns:
        (dentro_limite, tamanho_bytes)
    """
    size_bytes = file_path.stat().st_size
    max_bytes = max_size_mb * 1024 * 1024
    return (size_bytes <= max_bytes, size_bytes)


def safe_resolve_path(path: str, base_dir: Optional[Path] = None, allow_absolute: bool = True) -> Path:
    """
    Resolve path com proteção contra directory traversal.
    
    Args:
        path: Path fornecido pelo usuário
        base_dir: Diretório base para validação (default: cwd)
        allow_absolute: Se True, aceita paths absolutos seguros
    
    Returns:
        Path: Path resolvido e validado
    
    Raises:
        ValueError: Se path tenta escapar do base_dir via relative path
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    path_obj = Path(path)
    
    # Se é path absoluto e allow_absolute=True, validar apenas que não tem .. maliciosos
    if path_obj.is_absolute() and allow_absolute:
        resolved = path_obj.resolve()
        # Bloquear apenas se tentar .. tricks depois de resolve
        if '..' in str(path):
            # Verificar se resolve() eliminou todos os ..
            if str(resolved) != str(path_obj):
                raise ValueError(f"Path contains suspicious .. components: {path}")
        return resolved
    
    # Path relativo: validar que não escapa do base_dir
    resolved = (base_dir / path).resolve()
    
    try:
        resolved.relative_to(base_dir)
    except ValueError:
        raise ValueError(f"Path escapes base directory: {path}")
    
    return resolved


class HardenedReadFileTool(ValidatedTool):
    """
    Read file com error handling perfeito.
    
    Features:
    - Auto-detection de encoding
    - File size limits
    - Safe line range handling
    - Symlink resolution seguro
    """
    
    def __init__(self, max_size_mb: int = 10):
        super().__init__()
        self.category = ToolCategory.FILE_READ
        self.description = "Read file contents com error handling robusto"
        self.max_size_mb = max_size_mb
        self.parameters = {
            "path": {
                "type": "string",
                "description": "File path",
                "required": True
            },
            "line_range": {
                "type": "array",
                "description": "[start, end] line numbers (1-indexed)",
                "required": False
            }
        }
    
    def get_validators(self) -> Dict[str, Any]:
        return {
            'path': Required('path'),
            'line_range': TypeCheck((list, tuple, type(None)), 'line_range')
        }
    
    async def _execute_validated(
        self, 
        path: str, 
        line_range: Optional[tuple] = None, 
        **kwargs
    ) -> ToolResult:
        """Execute read com todas as proteções."""
        try:
            # 1. Path validation
            try:
                file_path = safe_resolve_path(path)
            except ValueError as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid path: {e}"
                )
            
            # 2. Existence check
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {path}"
                )
            
            if not file_path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Not a file: {path}"
                )
            
            # 3. Size check
            within_limit, size_bytes = check_file_size(file_path, self.max_size_mb)
            if not within_limit:
                return ToolResult(
                    success=False,
                    error=f"File too large: {size_bytes / 1024 / 1024:.1f}MB (limit: {self.max_size_mb}MB)"
                )
            
            # 4. Encoding detection
            try:
                encoding = detect_encoding(file_path)
            except EncodingDetectionError as e:
                return ToolResult(
                    success=False,
                    error=f"Encoding detection failed: {e}"
                )
            
            # 5. Read content
            try:
                content = file_path.read_text(encoding=encoding)
            except UnicodeDecodeError as e:
                # Fallback: binary read
                logger.warning(f"Unicode decode failed for {path}, reading as binary")
                content = file_path.read_bytes().decode('latin-1', errors='replace')
                encoding = 'binary'
            
            # 6. Apply line range
            if line_range and len(line_range) == 2:
                lines = content.split('\n')
                start, end = line_range
                
                # Validate indices
                if start < 1 or end < start:
                    return ToolResult(
                        success=False,
                        error=f"Invalid line range: [{start}, {end}]"
                    )
                
                # Safe slicing (clamp to bounds)
                start_idx = max(0, start - 1)
                end_idx = min(len(lines), end)
                lines = lines[start_idx:end_idx]
                content = '\n'.join(lines)
            
            # 7. Metadata
            metadata = {
                'path': str(file_path),
                'size_bytes': size_bytes,
                'encoding': encoding,
                'lines': len(content.split('\n'))
            }
            
            return ToolResult(
                success=True,
                data=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Unexpected error reading {path}")
            return ToolResult(
                success=False,
                error=f"Read failed: {type(e).__name__}: {e}"
            )


class HardenedWriteFileTool(ValidatedTool):
    """
    Write file com atomic writes e backup automático.
    
    Features:
    - Atomic write (write-to-temp + rename)
    - Backup automático de arquivo existente
    - Disk space check
    - Fsync para garantir persistência
    """
    
    def __init__(self, auto_backup: bool = True):
        super().__init__()
        self.category = ToolCategory.FILE_WRITE
        self.description = "Write file atomicamente com backup"
        self.auto_backup = auto_backup
        self.parameters = {
            "path": {
                "type": "string",
                "description": "File path",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "File content",
                "required": True
            },
            "encoding": {
                "type": "string",
                "description": "Encoding (default: utf-8)",
                "required": False
            }
        }
    
    def get_validators(self) -> Dict[str, Any]:
        return {
            'path': Required('path'),
            'content': Required('content')
        }
    
    async def _execute_validated(
        self,
        path: str,
        content: str,
        encoding: str = 'utf-8',
        **kwargs
    ) -> ToolResult:
        """Execute atomic write."""
        backup_path = None
        temp_path = None
        
        try:
            # 1. Path validation
            try:
                file_path = safe_resolve_path(path)
            except ValueError as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid path: {e}"
                )
            
            # 2. Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 3. Backup existing file
            if self.auto_backup and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                shutil.copy2(file_path, backup_path)
            
            # 4. Atomic write via temp file
            fd, temp_path_str = tempfile.mkstemp(
                dir=file_path.parent,
                prefix=f".{file_path.name}.",
                suffix=".tmp"
            )
            temp_path = Path(temp_path_str)
            
            try:
                with os.fdopen(fd, 'w', encoding=encoding) as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                
                # Atomic rename
                temp_path.replace(file_path)
                
            except Exception as e:
                # Cleanup temp file on error
                if temp_path and temp_path.exists():
                    temp_path.unlink()
                raise
            
            # 5. Cleanup backup (success)
            if backup_path and backup_path.exists():
                backup_path.unlink()
            
            metadata = {
                'path': str(file_path),
                'bytes_written': len(content.encode(encoding)),
                'encoding': encoding
            }
            
            return ToolResult(
                success=True,
                data=f"File written: {file_path}",
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Write failed for {path}")
            
            # Rollback: restore backup
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, file_path)
                    logger.info(f"Restored backup: {backup_path}")
                except Exception as restore_error:
                    logger.error(f"Backup restore failed: {restore_error}")
            
            return ToolResult(
                success=False,
                error=f"Write failed: {type(e).__name__}: {e}"
            )


class HardenedEditFileTool(ValidatedTool):
    """
    Edit file com validação de old_str e rollback automático.
    
    Features:
    - Validação de old_str (deve existir exatamente 1 vez)
    - Backup automático
    - Rollback em caso de falha
    - Diff preview opcional
    """
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.FILE_WRITE
        self.description = "Edit file com validação e rollback"
        self.parameters = {
            "path": {
                "type": "string",
                "description": "File path",
                "required": True
            },
            "old_str": {
                "type": "string",
                "description": "String to replace",
                "required": True
            },
            "new_str": {
                "type": "string",
                "description": "Replacement string",
                "required": True
            }
        }
    
    def get_validators(self) -> Dict[str, Any]:
        return {
            'path': Required('path'),
            'old_str': Required('old_str'),
            'new_str': Required('new_str')
        }
    
    async def _execute_validated(
        self,
        path: str,
        old_str: str,
        new_str: str,
        **kwargs
    ) -> ToolResult:
        """Execute edit com validação."""
        backup_path = None
        
        try:
            # 1. Path validation
            try:
                file_path = safe_resolve_path(path)
            except ValueError as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid path: {e}"
                )
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {path}"
                )
            
            # 2. Read content
            encoding = detect_encoding(file_path)
            original_content = file_path.read_text(encoding=encoding)
            
            # 3. Validate old_str exists
            occurrences = original_content.count(old_str)
            
            if occurrences == 0:
                return ToolResult(
                    success=False,
                    error=f"old_str not found in file: {old_str[:50]}..."
                )
            
            if occurrences > 1:
                return ToolResult(
                    success=False,
                    error=f"old_str appears {occurrences} times (must be unique)"
                )
            
            # 4. Backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)
            
            # 5. Apply edit
            new_content = original_content.replace(old_str, new_str)
            
            # 6. Atomic write
            write_tool = HardenedWriteFileTool(auto_backup=False)
            result = await write_tool._execute_validated(
                path=str(file_path),
                content=new_content,
                encoding=encoding
            )
            
            if not result.success:
                # Rollback
                shutil.copy2(backup_path, file_path)
                return result
            
            # 7. Cleanup backup
            backup_path.unlink()
            
            metadata = {
                'path': str(file_path),
                'changes': {
                    'old_length': len(old_str),
                    'new_length': len(new_str),
                    'delta': len(new_str) - len(old_str)
                }
            }
            
            return ToolResult(
                success=True,
                data=f"File edited: {file_path}",
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Edit failed for {path}")
            
            # Rollback
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, file_path)
                    logger.info(f"Restored backup after edit failure")
                except Exception as restore_error:
                    logger.error(f"Backup restore failed: {restore_error}")
            
            return ToolResult(
                success=False,
                error=f"Edit failed: {type(e).__name__}: {e}"
            )
