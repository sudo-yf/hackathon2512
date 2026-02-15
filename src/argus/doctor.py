"""Runtime readiness checks for Argus Dual-Agent."""

from __future__ import annotations

import platform
from dataclasses import asdict, dataclass
from typing import Any

from .config import AgentConfig


@dataclass
class Check:
    name: str
    status: str
    detail: str


def run_doctor(config: AgentConfig) -> dict[str, Any]:
    checks: list[Check] = [
        _check_required_env(config),
        _check_api_bases(config),
        _check_platform(),
    ]
    return {
        "total": len(checks),
        "passed": sum(1 for c in checks if c.status == "pass"),
        "warned": sum(1 for c in checks if c.status == "warn"),
        "failed": sum(1 for c in checks if c.status == "fail"),
        "checks": [asdict(c) for c in checks],
    }


def _check_required_env(config: AgentConfig) -> Check:
    missing = config.missing_required()
    if missing:
        return Check("required_env", "fail", f"missing: {', '.join(missing)}")
    return Check("required_env", "pass", "all required env vars are configured")


def _check_api_bases(config: AgentConfig) -> Check:
    missing = []
    if not config.gui_api_base:
        missing.append("GUIAgent_API_BASE")
    if not config.code_api_base:
        missing.append("CodeAgent_API_BASE")
    if missing:
        return Check("api_base", "warn", f"not set: {', '.join(missing)} (will use provider default)")
    return Check("api_base", "pass", "all API base variables are configured")


def _check_platform() -> Check:
    system = platform.system().lower()
    if system != "windows":
        return Check("platform", "warn", f"current platform is {system}, GUI mode is Windows-priority")
    return Check("platform", "pass", "windows platform detected")

