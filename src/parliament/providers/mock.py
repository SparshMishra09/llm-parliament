"""Mock provider — fake responses for testing. No API calls."""

from __future__ import annotations

import asyncio
import os

from parliament.providers.base import Provider


def _default_latency_ms() -> int:
    """Latency per mock call; PARLIAMENT_MOCK_LATENCY_MS overrides (demos, dev)."""
    raw = os.environ.get("PARLIAMENT_MOCK_LATENCY_MS", "")
    try:
        return max(0, int(raw))
    except ValueError:
        return 50


class MockProvider(Provider):
    name = "mock"

    def __init__(self, model: str = "mock-v1", latency_ms: int | None = None) -> None:
        self.model = model
        self._latency_ms = _default_latency_ms() if latency_ms is None else latency_ms

    async def generate(self, prompt: str, system: str | None = None) -> str:
        # Simulate realistic latency
        await asyncio.sleep(self._latency_ms / 1000)

        # Detect Speaker synthesis prompt by looking for the section headers instruction
        if "CONSENSUS" in prompt and "RECOMMENDATION" in prompt and "Speaker" in prompt:
            return self._mock_synthesis()
        return f"[Mock {self.model}] Analysis of: {prompt[:100]}..."

    def _mock_synthesis(self) -> str:
        return (
            "CONSENSUS:\nAll analysts agree on the core approach.\n\n"
            "SPLIT:\nMinor disagreement on implementation details.\n\n"
            "RISKS:\n- Integration complexity\n- Timeline pressure\n\n"
            "RECOMMENDATION:\nProceed with the majority approach."
        )
