"""Free-model interface.

No model is required: the stub agents are deterministic and the default.
A free model may be plugged in later through :class:`LLMClient`, using
free APIs only, with keys in env vars only (see ``config.py``). The model
is never the guardrail — the trace logger in ``trace.py`` rejects
uncited claims whatever the model says.
"""

from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        """Return a completion for ``prompt``. Raise on failure."""
        ...


class StubLLM:
    """Deterministic stand-in: returns no completion.

    The stub agents do not call a model at all; they work from the
    synthetic case data with explicit rules. This class exists so the
    pipeline has a model slot to fill later without changing its shape.
    """

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        raise NotImplementedError(
            "Stub mode uses no model. Plug a free model in through "
            "LLMClient (src/llm.py) or keep the stub agents."
        )


class FreeModelLLM:
    """Placeholder for a free-model backend (to be wired by Allen).

    Implement ``complete`` against a free API of Allen's choice, through
    his existing free-API process. Do not hard-code an endpoint, a model
    name that costs money, or any key. If the model returns a claim, the
    caller must still attach evidence IDs before the trace logger
    accepts it.
    """

    def __init__(self, model: str = "", base_url: str = "", api_key: str = ""):
        if not model:
            raise ValueError("FreeModelLLM requires LLM_MODEL to be set")
        self.model = model
        self.base_url = base_url
        self._api_key = api_key  # held in memory only, never logged

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        raise NotImplementedError(
            "FreeModelLLM is not wired yet. Implement complete() against "
            "a free API, or use StubLLM (the default)."
        )
