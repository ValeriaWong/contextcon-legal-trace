"""Config: env vars only. No defaults that look like keys, no keys in code.

Loads a local ``.env`` file if present (simple KEY=VALUE parsing, no
third-party dependency). ``.env`` is git-ignored; ``.env.example`` holds
placeholders only.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

MEKO_MCP_URL = "https://mcp.mekodata.ai/mcp"  # verified in Meko docs
DEFAULT_DATAPACK = "legal-audit-synthetic"


def _load_dotenv(path: Path | None = None) -> None:
    path = path or Path(__file__).resolve().parent.parent / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Config:
    meko_api_key: str = ""
    meko_mcp_url: str = MEKO_MCP_URL
    meko_datapack: str = DEFAULT_DATAPACK
    backend: str = "stub"  # "stub" | "meko"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""


def load_config() -> Config:
    _load_dotenv()
    backend = os.environ.get("MEKO_BACKEND", "stub").strip().lower()
    if backend not in ("stub", "meko"):
        raise ValueError(f"MEKO_BACKEND must be 'stub' or 'meko', got {backend!r}")
    if backend == "meko" and not os.environ.get("MEKO_API_KEY"):
        raise ValueError(
            "MEKO_BACKEND=meko requires MEKO_API_KEY in .env. "
            "Create the key in the Meko portal (Settings > API Keys); "
            "never put a real key in a committed file."
        )
    return Config(
        meko_api_key=os.environ.get("MEKO_API_KEY", ""),
        meko_mcp_url=os.environ.get("MEKO_MCP_URL", MEKO_MCP_URL),
        meko_datapack=os.environ.get("MEKO_DATAPACK", DEFAULT_DATAPACK),
        backend=backend,
        llm_model=os.environ.get("LLM_MODEL", ""),
        llm_api_key=os.environ.get("LLM_API_KEY", ""),
        llm_base_url=os.environ.get("LLM_BASE_URL", ""),
    )
