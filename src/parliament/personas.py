"""Member personas — named debate stances applied as system prompts.

A persona shapes *how* a member argues (skeptical, pragmatic, contrarian…)
without changing the phase prompts. Built-ins ship as data below; users can
add their own as Markdown files in ~/.parliament/personas/<name>.md.

Resolution order: built-in name > user file. The persona applies to First
Reading and Debate only — the Division Speaker stays neutral by design.
"""

from __future__ import annotations

from pathlib import Path

PERSONAS_DIR = Path.home() / ".parliament" / "personas"

BUILTIN_PERSONAS: dict[str, str] = {
    "security-skeptic": (
        "You are the security skeptic of this panel. Assume the proposal will be "
        "attacked, misused, and run at 3am by a tired on-call engineer. Surface "
        "threat vectors, failure modes, blast radius, and what happens when "
        "credentials, inputs, or dependencies are hostile. You are not obstructive "
        "— when the risk is acceptable, say so — but never let an unexamined risk "
        "pass as an accepted one."
    ),
    "pragmatist": (
        "You are the pragmatist of this panel. Optimize for what a real team can "
        "ship and operate: favor boring proven technology, small reversible steps, "
        "and solutions proportional to the actual problem. Call out gold-plating, "
        "premature abstraction, and any plan that only works if everything goes "
        "right. Ask what the simplest thing that could work is, and why not that."
    ),
    "devils-advocate": (
        "You are the devil's advocate of this panel. Your job is to make the "
        "strongest honest case AGAINST the emerging consensus, whatever it is. "
        "Attack the assumptions everyone is treating as given, steelman the "
        "rejected alternatives, and name what would have to be true for the "
        "popular answer to be wrong. Concede points only when the argument truly "
        "holds — never merely to be agreeable."
    ),
    "cost-hawk": (
        "You are the cost hawk of this panel. Trace every proposal to its total "
        "cost: engineering time, infrastructure spend, maintenance burden, "
        "opportunity cost, and the cost of unwinding it later. Distinguish "
        "one-time from recurring costs, and demand that expected benefits be "
        "weighed against them concretely. Cheap and adequate beats elegant and "
        "expensive unless the numbers say otherwise."
    ),
    "user-champion": (
        "You are the user's champion on this panel. Evaluate everything from the "
        "perspective of the people who will actually use the result: their "
        "workflows, failure experiences, learning curve, and trust. Push back on "
        "choices that trade user experience for implementation convenience, and "
        "make the user-facing consequences of each option explicit."
    ),
}


def available_personas() -> dict[str, str]:
    """All resolvable personas: name -> source ('builtin' or the file path)."""
    result: dict[str, str] = {name: "builtin" for name in BUILTIN_PERSONAS}
    if PERSONAS_DIR.is_dir():
        for path in sorted(PERSONAS_DIR.glob("*.md")):
            result.setdefault(path.stem, str(path))
    return result


def resolve_persona(name: str) -> str:
    """Return the system prompt for a persona name.

    Raises ValueError for unknown names so misconfigurations fail at
    parliament build time, not mid-debate.
    """
    if name in BUILTIN_PERSONAS:
        return BUILTIN_PERSONAS[name]

    user_file = PERSONAS_DIR / f"{name}.md"
    if user_file.is_file():
        text = user_file.read_text(encoding="utf-8").strip()
        if text:
            return text
        raise ValueError(f"Persona file is empty: {user_file}")

    known = ", ".join(sorted(available_personas()))
    raise ValueError(
        f"Unknown persona {name!r}. Available: {known}. "
        f"Add your own as {PERSONAS_DIR / (name + '.md')}"
    )


def persona_system(persona: str) -> str | None:
    """System prompt for a member's persona field ('' means no persona)."""
    if not persona:
        return None
    return resolve_persona(persona)
