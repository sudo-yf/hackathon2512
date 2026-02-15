from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    gui_model: str
    gui_api_base: str
    gui_api_key: str
    code_model: str
    code_api_base: str
    code_api_key: str

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            gui_model=os.getenv("GUIAgent_MODEL", ""),
            gui_api_base=os.getenv("GUIAgent_API_BASE", ""),
            gui_api_key=os.getenv("GUIAgent_API_KEY", ""),
            code_model=os.getenv("CodeAgent_MODEL", ""),
            code_api_base=os.getenv("CodeAgent_API_BASE", ""),
            code_api_key=os.getenv("CodeAgent_API_KEY", ""),
        )

    def missing_required(self) -> list[str]:
        required = {
            "GUIAgent_MODEL": self.gui_model,
            "GUIAgent_API_KEY": self.gui_api_key,
            "CodeAgent_MODEL": self.code_model,
            "CodeAgent_API_KEY": self.code_api_key,
        }
        return [name for name, value in required.items() if not value]
