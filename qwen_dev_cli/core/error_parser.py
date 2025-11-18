#!/usr/bin/env python3
"""
Intelligent Error Parser - Parse common errors and suggest fixes.

Inspired by:
- GitHub Copilot: Contextual error analysis
- Cursor AI: Smart fix suggestions
- Claude Code: Educational explanations
"""

import re
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ErrorAnalysis:
    """Analyzed error with suggestions."""
    error_type: str
    original_message: str
    user_friendly: str
    suggestions: List[str]
    severity: str  # "low", "medium", "high", "critical"
    can_auto_fix: bool = False
    auto_fix_command: Optional[str] = None


class ErrorParser:
    """Parse command errors and suggest intelligent fixes."""
    
    def __init__(self):
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, Dict]:
        """Build error detection patterns."""
        return {
            # Permission errors
            'permission_denied': {
                'patterns': [
                    r'permission denied',
                    r'operation not permitted',
                    r'access denied',
                    r'cannot access',
                ],
                'severity': 'high',
                'handler': self._handle_permission_error
            },
            
            # Command not found
            'command_not_found': {
                'patterns': [
                    r'command not found',
                    r'not found',
                    r'no such command',
                    r'unknown command',
                ],
                'severity': 'medium',
                'handler': self._handle_command_not_found
            },
            
            # Network errors
            'network_error': {
                'patterns': [
                    r'connection refused',
                    r'connection timed out',
                    r'network is unreachable',
                    r'no route to host',
                    r'could not resolve host',
                ],
                'severity': 'medium',
                'handler': self._handle_network_error
            },
            
            # Disk errors
            'disk_full': {
                'patterns': [
                    r'no space left on device',
                    r'disk full',
                    r'quota exceeded',
                ],
                'severity': 'high',
                'handler': self._handle_disk_full
            },
            
            # File errors
            'file_not_found': {
                'patterns': [
                    r'no such file or directory',
                    r'cannot find',
                    r'does not exist',
                ],
                'severity': 'medium',
                'handler': self._handle_file_not_found
            },
            
            # Port errors
            'port_in_use': {
                'patterns': [
                    r'address already in use',
                    r'port.*already in use',
                    r'bind.*failed',
                ],
                'severity': 'medium',
                'handler': self._handle_port_in_use
            },
            
            # Timeout errors
            'timeout': {
                'patterns': [
                    r'timeout',
                    r'timed out',
                    r'operation took too long',
                ],
                'severity': 'medium',
                'handler': self._handle_timeout
            },
            
            # Syntax errors
            'syntax_error': {
                'patterns': [
                    r'syntax error',
                    r'unexpected.*token',
                    r'invalid syntax',
                ],
                'severity': 'low',
                'handler': self._handle_syntax_error
            },
            
            # Memory errors
            'out_of_memory': {
                'patterns': [
                    r'out of memory',
                    r'cannot allocate memory',
                    r'memory exhausted',
                ],
                'severity': 'critical',
                'handler': self._handle_out_of_memory
            },
        }
    
    def parse(self, error_output: str, command: str = "") -> ErrorAnalysis:
        """Parse error and return analysis with suggestions."""
        error_lower = error_output.lower()
        
        # Try to match known patterns
        for error_type, config in self.patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, error_lower):
                    return config['handler'](error_output, command)
        
        # Unknown error
        return self._handle_unknown_error(error_output, command)
    
    def _handle_permission_error(self, error: str, command: str) -> ErrorAnalysis:
        """Handle permission denied errors."""
        suggestions = []
        
        # Suggest sudo
        if command and not command.startswith('sudo'):
            suggestions.append(f"Try with sudo: sudo {command}")
        
        # Suggest checking file permissions
        suggestions.append("Check file permissions: ls -la <file>")
        
        # Suggest checking ownership
        suggestions.append("Check ownership: stat <file>")
        
        # If writing to system directory
        if '/usr/' in error or '/etc/' in error or '/sys/' in error:
            suggestions.append("This is a system directory - use sudo or change location")
        
        return ErrorAnalysis(
            error_type="Permission Denied",
            original_message=error,
            user_friendly="You don't have permission to perform this operation",
            suggestions=suggestions,
            severity="high",
            can_auto_fix=bool(command and not command.startswith('sudo')),
            auto_fix_command=f"sudo {command}" if command else None
        )
    
    def _handle_command_not_found(self, error: str, command: str) -> ErrorAnalysis:
        """Handle command not found errors."""
        # Extract command name
        cmd_match = re.search(r'(\w+).*not found', error)
        cmd_name = cmd_match.group(1) if cmd_match else command.split()[0] if command else "command"
        
        suggestions = []
        
        # Common package mappings
        install_map = {
            'git': 'apt install git',
            'curl': 'apt install curl',
            'wget': 'apt install wget',
            'npm': 'apt install npm',
            'python': 'apt install python3',
            'pip': 'apt install python3-pip',
            'docker': 'apt install docker.io',
            'node': 'apt install nodejs',
        }
        
        if cmd_name.lower() in install_map:
            suggestions.append(f"Install it: sudo {install_map[cmd_name.lower()]}")
        else:
            suggestions.append(f"Search for package: apt search {cmd_name}")
            suggestions.append(f"Install it: sudo apt install {cmd_name}")
        
        suggestions.append("Check if it's in PATH: echo $PATH")
        suggestions.append("Find the binary: which " + cmd_name)
        
        return ErrorAnalysis(
            error_type="Command Not Found",
            original_message=error,
            user_friendly=f"The command '{cmd_name}' is not installed",
            suggestions=suggestions,
            severity="medium"
        )
    
    def _handle_network_error(self, error: str, command: str) -> ErrorAnalysis:
        """Handle network errors."""
        suggestions = [
            "Check internet connection: ping 8.8.8.8",
            "Check DNS: nslookup google.com",
            "Check firewall: sudo ufw status",
            "Try with VPN disabled",
        ]
        
        if 'connection refused' in error.lower():
            suggestions.insert(0, "Service might not be running - check if it's started")
        
        return ErrorAnalysis(
            error_type="Network Error",
            original_message=error,
            user_friendly="Cannot connect to the network or server",
            suggestions=suggestions,
            severity="medium"
        )
    
    def _handle_disk_full(self, error: str, command: str) -> ErrorAnalysis:
        """Handle disk full errors."""
        suggestions = [
            "Check disk space: df -h",
            "Find large files: du -sh * | sort -h",
            "Clean package cache: sudo apt clean",
            "Remove old logs: sudo journalctl --vacuum-time=7d",
            "Find and remove large files: find . -type f -size +100M",
        ]
        
        return ErrorAnalysis(
            error_type="Disk Full",
            original_message=error,
            user_friendly="No space left on disk",
            suggestions=suggestions,
            severity="high",
            can_auto_fix=True,
            auto_fix_command="df -h && du -sh * | sort -h | tail -10"
        )
    
    def _handle_file_not_found(self, error: str, command: str) -> ErrorAnalysis:
        """Handle file not found errors."""
        # Try to extract filename
        file_match = re.search(r'[\'"]([^\'"]+)[\'"]', error)
        filename = file_match.group(1) if file_match else "file"
        
        suggestions = [
            f"Check if file exists: ls -la {filename}",
            "List current directory: ls -la",
            "Search for file: find . -name " + filename,
            "Check current directory: pwd",
        ]
        
        return ErrorAnalysis(
            error_type="File Not Found",
            original_message=error,
            user_friendly=f"Cannot find '{filename}'",
            suggestions=suggestions,
            severity="medium"
        )
    
    def _handle_port_in_use(self, error: str, command: str) -> ErrorAnalysis:
        """Handle port already in use errors."""
        # Try to extract port number
        port_match = re.search(r'port.*?(\d+)|(\d+).*port', error.lower())
        port = port_match.group(1) or port_match.group(2) if port_match else "PORT"
        
        suggestions = [
            f"Find process using port: sudo lsof -i :{port}",
            f"Kill process: sudo kill -9 $(lsof -t -i:{port})",
            "Use different port",
            "Stop the service: sudo systemctl stop <service>",
        ]
        
        return ErrorAnalysis(
            error_type="Port In Use",
            original_message=error,
            user_friendly=f"Port {port} is already being used by another process",
            suggestions=suggestions,
            severity="medium",
            can_auto_fix=True,
            auto_fix_command=f"sudo lsof -i :{port}"
        )
    
    def _handle_timeout(self, error: str, command: str) -> ErrorAnalysis:
        """Handle timeout errors."""
        suggestions = [
            "Increase timeout value",
            "Check internet connection: ping 8.8.8.8",
            "Try again - might be temporary",
            "Check if server is responding: curl -I <url>",
        ]
        
        return ErrorAnalysis(
            error_type="Timeout",
            original_message=error,
            user_friendly="Operation took too long and timed out",
            suggestions=suggestions,
            severity="medium"
        )
    
    def _handle_syntax_error(self, error: str, command: str) -> ErrorAnalysis:
        """Handle syntax errors."""
        suggestions = [
            "Check command syntax: <command> --help",
            "Read documentation: man <command>",
            "Check for typos",
            "Use quotes for strings with spaces",
        ]
        
        return ErrorAnalysis(
            error_type="Syntax Error",
            original_message=error,
            user_friendly="Command has incorrect syntax",
            suggestions=suggestions,
            severity="low"
        )
    
    def _handle_out_of_memory(self, error: str, command: str) -> ErrorAnalysis:
        """Handle out of memory errors."""
        suggestions = [
            "Check memory usage: free -h",
            "Check running processes: ps aux --sort=-%mem | head -10",
            "Kill memory-heavy processes: kill <PID>",
            "Close unnecessary programs",
            "Increase swap space",
        ]
        
        return ErrorAnalysis(
            error_type="Out of Memory",
            original_message=error,
            user_friendly="System ran out of memory",
            suggestions=suggestions,
            severity="critical"
        )
    
    def _handle_unknown_error(self, error: str, command: str) -> ErrorAnalysis:
        """Handle unknown errors."""
        suggestions = [
            "Read the full error message carefully",
            "Search online: google the error",
            "Check logs: journalctl -xe",
            "Try command with verbose flag: <command> -v",
        ]
        
        return ErrorAnalysis(
            error_type="Unknown Error",
            original_message=error,
            user_friendly="An unexpected error occurred",
            suggestions=suggestions,
            severity="medium"
        )


# Global parser instance
error_parser = ErrorParser()
