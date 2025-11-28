"""
AuthenticationManager - API Key Management.

Extracted from Bridge as part of SCALE & SUSTAIN Phase 1.1.

Manages:
- API key storage (global/project)
- Multi-provider support
- Secure credential handling

Author: JuanCS Dev
Date: 2025-11-26
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from jdev_tui.core.interfaces import IAuthenticationManager


class AuthenticationManager(IAuthenticationManager):
    """
    API key authentication manager.

    Implements IAuthenticationManager interface for:
    - Login/logout operations
    - Multi-provider API key management
    - Secure credential storage
    """

    # Supported providers and their environment variables
    PROVIDERS = {
        "gemini": "GEMINI_API_KEY",
        "google": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "nebius": "NEBIUS_API_KEY",
        "groq": "GROQ_API_KEY",
    }

    # Security limits
    MAX_KEY_LENGTH = 500
    MIN_KEY_LENGTH = 10

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        global_dir: Optional[Path] = None
    ):
        """
        Initialize AuthenticationManager.

        Args:
            project_dir: Project directory for .env file.
            global_dir: Global config directory for credentials.json.
        """
        self._project_dir = project_dir or Path.cwd()
        self._global_dir = global_dir or (Path.home() / ".config" / "juancs")

    def _get_credentials_file(self) -> Path:
        """Get global credentials file path."""
        self._global_dir.mkdir(parents=True, exist_ok=True)
        return self._global_dir / "credentials.json"

    def _get_env_file(self) -> Path:
        """Get project .env file path."""
        return self._project_dir / ".env"

    def _validate_api_key(self, api_key: str) -> tuple[bool, Optional[str]]:
        """
        Validate API key format.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if len(api_key) < self.MIN_KEY_LENGTH:
            return False, "API key too short. Please provide a valid key."

        if len(api_key) > self.MAX_KEY_LENGTH:
            return False, f"API key too long (max {self.MAX_KEY_LENGTH} characters)"

        # Check for control characters (injection prevention)
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', api_key)
        if sanitized != api_key:
            return False, "API key contains invalid characters (newlines, control chars not allowed)"

        return True, None

    def login(
        self,
        provider: str = "gemini",
        api_key: Optional[str] = None,
        scope: str = "global"
    ) -> Dict[str, Any]:
        """
        Login/configure API key for a provider.

        Args:
            provider: Provider name (gemini, openai, etc.).
            api_key: API key to store.
            scope: "global" or "project".

        Returns:
            Dictionary with success status and details.
        """
        provider_lower = provider.lower()

        if provider_lower not in self.PROVIDERS:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}. Valid: {', '.join(self.PROVIDERS.keys())}"
            }

        env_var = self.PROVIDERS[provider_lower]

        # If no key provided, check environment
        if not api_key:
            existing = os.environ.get(env_var)
            if existing:
                return {
                    "success": True,
                    "message": f"Already logged in to {provider} (key from environment)",
                    "provider": provider,
                    "source": "environment"
                }
            return {
                "success": False,
                "error": f"No API key provided. Use: /login {provider} YOUR_API_KEY"
            }

        # Validate API key
        is_valid, error = self._validate_api_key(api_key)
        if not is_valid:
            return {"success": False, "error": error}

        try:
            if scope == "global":
                return self._save_global_key(provider, env_var, api_key)
            elif scope == "project":
                return self._save_project_key(provider, env_var, api_key)
            else:
                return {
                    "success": False,
                    "error": f"Invalid scope: {scope}. Use 'global' or 'project'"
                }
        except Exception as e:
            return {"success": False, "error": f"Login failed: {e}"}

    def _save_global_key(
        self,
        provider: str,
        env_var: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Save API key to global credentials file."""
        creds_file = self._get_credentials_file()

        creds = {}
        if creds_file.exists():
            try:
                creds = json.loads(creds_file.read_text())
            except json.JSONDecodeError:
                creds = {}

        creds[env_var] = api_key
        creds_file.write_text(json.dumps(creds, indent=2))
        creds_file.chmod(0o600)  # Secure permissions

        # Also set in environment for current session
        os.environ[env_var] = api_key

        return {
            "success": True,
            "message": f"Logged in to {provider} (global)",
            "provider": provider,
            "scope": "global",
            "file": str(creds_file)
        }

    def _save_project_key(
        self,
        provider: str,
        env_var: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Save API key to project .env file."""
        env_file = self._get_env_file()

        lines = []
        key_found = False

        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith(f"{env_var}="):
                    lines.append(f"{env_var}={api_key}")
                    key_found = True
                else:
                    lines.append(line)

        if not key_found:
            lines.append(f"{env_var}={api_key}")

        env_file.write_text("\n".join(lines) + "\n")

        # Set in environment for current session
        os.environ[env_var] = api_key

        return {
            "success": True,
            "message": f"Logged in to {provider} (project)",
            "provider": provider,
            "scope": "project",
            "file": str(env_file)
        }

    def logout(
        self,
        provider: Optional[str] = None,
        scope: str = "all"
    ) -> Dict[str, Any]:
        """
        Logout/remove API key for a provider.

        Args:
            provider: Provider name or None for all.
            scope: "global", "project", or "all".

        Returns:
            Dictionary with success status and removed keys.
        """
        removed = []

        try:
            # Determine which keys to remove
            if provider:
                provider_lower = provider.lower()
                if provider_lower not in self.PROVIDERS:
                    return {
                        "success": False,
                        "error": f"Unknown provider: {provider}"
                    }
                keys_to_remove = [self.PROVIDERS[provider_lower]]
            else:
                keys_to_remove = list(set(self.PROVIDERS.values()))

            # Remove from global credentials
            if scope in ("global", "all"):
                removed.extend(self._remove_global_keys(keys_to_remove))

            # Remove from project .env
            if scope in ("project", "all"):
                removed.extend(self._remove_project_keys(keys_to_remove))

            # Remove from current environment
            for key in keys_to_remove:
                if key in os.environ:
                    del os.environ[key]
                    if f"{key} (session)" not in removed:
                        removed.append(f"{key} (session)")

            if removed:
                return {
                    "success": True,
                    "message": f"Logged out: {', '.join(removed)}",
                    "removed": removed
                }
            else:
                return {
                    "success": True,
                    "message": "No credentials found to remove",
                    "removed": []
                }

        except Exception as e:
            return {"success": False, "error": f"Logout failed: {e}"}

    def _remove_global_keys(self, keys: List[str]) -> List[str]:
        """Remove keys from global credentials file."""
        removed = []
        creds_file = self._get_credentials_file()

        if creds_file.exists():
            try:
                creds = json.loads(creds_file.read_text())
                for key in keys:
                    if key in creds:
                        del creds[key]
                        removed.append(f"{key} (global)")
                creds_file.write_text(json.dumps(creds, indent=2))
            except Exception:
                pass

        return removed

    def _remove_project_keys(self, keys: List[str]) -> List[str]:
        """Remove keys from project .env file."""
        removed = []
        env_file = self._get_env_file()

        if env_file.exists():
            try:
                lines = []
                original = env_file.read_text().splitlines()

                for line in original:
                    should_keep = True
                    for key in keys:
                        if line.startswith(f"{key}="):
                            removed.append(f"{key} (project)")
                            should_keep = False
                            break
                    if should_keep:
                        lines.append(line)

                if len(lines) != len(original):
                    env_file.write_text("\n".join(lines) + "\n" if lines else "")
            except Exception:
                pass

        return removed

    def get_auth_status(self) -> Dict[str, Any]:
        """
        Get authentication status for all providers.

        Returns:
            Dictionary with provider status and sources.
        """
        # Check global credentials
        creds_file = self._get_credentials_file()
        global_creds = {}
        if creds_file.exists():
            try:
                global_creds = json.loads(creds_file.read_text())
            except Exception:
                pass

        # Check project .env
        env_file = self._get_env_file()
        project_creds = {}
        if env_file.exists():
            try:
                for line in env_file.read_text().splitlines():
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        project_creds[key.strip()] = value.strip()
            except Exception:
                pass

        # Build status for each provider
        status = {}
        unique_providers = {p: v for p, v in self.PROVIDERS.items() if p != "google"}

        for provider, env_var in unique_providers.items():
            sources = []
            if env_var in os.environ:
                sources.append("environment")
            if env_var in global_creds:
                sources.append("global")
            if env_var in project_creds:
                sources.append("project")

            status[provider] = {
                "logged_in": len(sources) > 0,
                "sources": sources,
                "env_var": env_var
            }

        return {
            "providers": status,
            "global_file": str(creds_file),
            "project_file": str(env_file)
        }

    def load_credentials(self) -> None:
        """Load credentials from global file into environment."""
        creds_file = self._get_credentials_file()
        if creds_file.exists():
            try:
                creds = json.loads(creds_file.read_text())
                for key, value in creds.items():
                    if key not in os.environ:
                        os.environ[key] = value
            except Exception:
                pass
