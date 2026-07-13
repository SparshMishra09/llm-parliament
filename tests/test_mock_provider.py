"""MockProvider behavior tests."""

from parliament.providers.mock import MockProvider, _default_latency_ms


def test_default_latency_is_50ms(monkeypatch):
    monkeypatch.delenv("PARLIAMENT_MOCK_LATENCY_MS", raising=False)
    assert MockProvider()._latency_ms == 50


def test_env_var_overrides_default_latency(monkeypatch):
    monkeypatch.setenv("PARLIAMENT_MOCK_LATENCY_MS", "1500")
    assert MockProvider()._latency_ms == 1500


def test_explicit_latency_wins_over_env(monkeypatch):
    monkeypatch.setenv("PARLIAMENT_MOCK_LATENCY_MS", "1500")
    assert MockProvider(latency_ms=0)._latency_ms == 0


def test_invalid_env_value_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("PARLIAMENT_MOCK_LATENCY_MS", "fast")
    assert _default_latency_ms() == 50


def test_negative_env_value_clamps_to_zero(monkeypatch):
    monkeypatch.setenv("PARLIAMENT_MOCK_LATENCY_MS", "-100")
    assert _default_latency_ms() == 0
