"""Persona resolution and debate wiring tests."""

import asyncio

import pytest

from parliament import personas as personas_mod
from parliament.core.types import Bill, Member, Response
from parliament.personas import (
    BUILTIN_PERSONAS,
    available_personas,
    persona_system,
    resolve_persona,
)
from parliament.procedures.debate import run_debate
from parliament.procedures.first_reading import run_first_reading
from parliament.providers.mock import MockProvider


# ---------- resolution ----------


def test_builtin_personas_resolve():
    for name in BUILTIN_PERSONAS:
        assert resolve_persona(name)


def test_unknown_persona_raises_with_known_names():
    with pytest.raises(ValueError) as exc:
        resolve_persona("does-not-exist")
    assert "pragmatist" in str(exc.value)


def test_user_persona_file_resolves(monkeypatch, tmp_path):
    monkeypatch.setattr(personas_mod, "PERSONAS_DIR", tmp_path)
    (tmp_path / "greybeard.md").write_text("You have seen it all before.")

    assert resolve_persona("greybeard") == "You have seen it all before."
    assert available_personas()["greybeard"] == str(tmp_path / "greybeard.md")


def test_empty_user_persona_file_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(personas_mod, "PERSONAS_DIR", tmp_path)
    (tmp_path / "empty.md").write_text("   \n")

    with pytest.raises(ValueError, match="empty"):
        resolve_persona("empty")


def test_builtin_wins_over_user_file(monkeypatch, tmp_path):
    monkeypatch.setattr(personas_mod, "PERSONAS_DIR", tmp_path)
    (tmp_path / "pragmatist.md").write_text("shadowed")

    assert resolve_persona("pragmatist") == BUILTIN_PERSONAS["pragmatist"]


def test_persona_system_empty_means_none():
    assert persona_system("") is None
    assert persona_system("pragmatist") == BUILTIN_PERSONAS["pragmatist"]


# ---------- config wiring ----------


def test_config_member_persona_is_wired():
    from parliament.config import build_parliament_from_config

    config = {
        "parliament": {
            "members": [
                {"name": "A", "provider": "mock", "model": "mock-v1",
                 "persona": "security-skeptic"},
                {"name": "B", "provider": "mock", "model": "mock-v2"},
            ]
        },
        "providers": {},
    }
    members, _ = build_parliament_from_config(config)
    assert members[0].persona == "security-skeptic"
    assert members[1].persona == ""


def test_config_unknown_persona_fails_at_build_time():
    from parliament.config import build_parliament_from_config

    config = {
        "parliament": {
            "members": [
                {"name": "A", "provider": "mock", "model": "mock-v1",
                 "persona": "nope"},
            ]
        },
        "providers": {},
    }
    with pytest.raises(ValueError, match="nope"):
        build_parliament_from_config(config)


# ---------- procedures pass the persona as system prompt ----------


class _RecordingProvider(MockProvider):
    def __init__(self):
        super().__init__(model="mock-v1", latency_ms=0)
        self.systems: list[str | None] = []

    async def generate(self, prompt: str, system: str | None = None) -> str:
        self.systems.append(system)
        return await super().generate(prompt, system)


def _members():
    return [
        Member(name="Alpha", provider_name="mock", model="mock-v1",
               persona="devils-advocate"),
        Member(name="Beta", provider_name="mock", model="mock-v1"),
    ]


def test_first_reading_uses_member_persona():
    members = _members()
    providers = {"Alpha": _RecordingProvider(), "Beta": _RecordingProvider()}

    asyncio.run(
        run_first_reading(Bill(content="q?"), members, providers, lambda e: None)
    )

    assert providers["Alpha"].systems == [BUILTIN_PERSONAS["devils-advocate"]]
    assert providers["Beta"].systems == [None]


def test_debate_uses_member_persona():
    members = _members()
    providers = {"Alpha": _RecordingProvider(), "Beta": _RecordingProvider()}
    first_reading = [
        Response(member_name="Alpha", content="a", phase="first_reading"),
        Response(member_name="Beta", content="b", phase="first_reading"),
    ]

    asyncio.run(
        run_debate(Bill(content="q?"), members, providers, first_reading, lambda e: None)
    )

    assert providers["Alpha"].systems == [BUILTIN_PERSONAS["devils-advocate"]]
    assert providers["Beta"].systems == [None]


# ---------- CLI ----------


def test_personas_command_lists_builtins():
    from click.testing import CliRunner

    from parliament import cli

    result = CliRunner().invoke(cli.main, ["personas"])

    assert result.exit_code == 0, result.output
    assert "pragmatist" in result.output
    assert "security-skeptic" in result.output
