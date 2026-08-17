# LLM Parliament

[![PyPI version](https://img.shields.io/pypi/v/llm-parliament.svg)](https://pypi.org/project/llm-parliament/)
[![Python](https://img.shields.io/pypi/pyversions/llm-parliament.svg)](https://pypi.org/project/llm-parliament/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

**Three AI models debate your question, then tell you where they disagreed.**

One model gives you one answer, stated with equal confidence whether it's
certain or guessing. Parliament runs three models through a structured debate
and shows you the part a single answer hides: **the split.**

---

## What you actually get

Ask a question with real trade-offs, and the verdict looks like this:

```text
╭─────────────── Parliament Verdict ────────────────╮
│ Should we migrate our REST API to GraphQL?        │
╰───────────────────────────────────────────────────╯

╭─────────────────── ℹ Consensus ───────────────────╮
│ All three agree the current REST endpoints are    │
│ over-fetching badly on mobile, and that this is   │
│ a real cost worth fixing.                         │
╰───────────────────────────────────────────────────╯
╭───────────────────── ⚖ Split ─────────────────────╮
│ Claude and Gemini favour a full migration.        │
│ GPT dissents: with a 4-person team and no prior   │
│ GraphQL experience, it argues the N+1 and caching │
│ problems will cost more than the over-fetching    │
│ they're meant to solve.                           │
╰───────────────────────────────────────────────────╯
╭───────────────────── ! Risks ─────────────────────╮
│ - Resolver N+1 queries without DataLoader         │
│ - CDN caching no longer works on a single POST    │
│ - Team has no GraphQL production experience       │
╰───────────────────────────────────────────────────╯
╭──────────────── ✓ Recommendation ─────────────────╮
│ Don't migrate wholesale. Add a GraphQL gateway in │
│ front of the three worst-offending mobile         │
│ endpoints, measure for a quarter, then decide.    │
╰───────────────────────────────────────────────────╯
```

> *Illustrative example of the output format.*

**That ⚖ Split panel is the whole point.** A single model would have picked one
of those positions and presented it as the answer. Here you can see that the
recommendation was contested, who contested it, and on what grounds — which is
exactly the information you need to decide whether to trust it.

Built on multi-agent debate, a technique shown to improve AI accuracy by 7–15%
in research (Liang et al. 2023, Chen et al. 2023). The process runs in three
phases: **First Reading** (each model answers independently), **Debate** (each
model critiques the others), **Division** (a Speaker synthesises the verdict).

## Quick Start

```bash
pipx install llm-parliament
parliament doctor
parliament              # opens the TUI
```

The mock parliament runs out of the box with zero setup — useful for seeing the
format, though the mock models produce placeholder text, not real analysis.

**For a real debate, one API key is enough.** Parliament seats three members,
but they don't need to come from three different companies:

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # or OPENAI_API_KEY, or GOOGLE_API_KEY
parliament doctor                      # wizard detects the key, seats three models
```

With one key, the wizard seats three models from that provider at different
capability tiers. With two or three keys, you get cross-provider debate — which
produces more genuine disagreement, since models from the same lab tend to share
blind spots. With Ollama, it costs nothing at all. See
[Choosing your models](#choosing-your-models).

## When to use it

Parliament is a deliberation tool, not a throughput tool.

| Good fit | Poor fit |
|---|---|
| Architecture and design trade-offs | Quick lookups and factual questions |
| "Should we adopt X?" decisions | Drafting, summarising, rewriting |
| Reviewing a plan for blind spots | Anything with one obvious answer |
| Choices that are expensive to reverse | High-volume automated calls |

**Rule of thumb:** if being wrong costs more than an hour of your time, it's
worth a debate. Otherwise ask one model.

## Installation

The recommended way is **pipx** — it installs the tool into an isolated
environment but exposes `parliament` globally on your PATH.

| Platform | One-time prereq | Install |
|---|---|---|
| Linux | `sudo apt install pipx && pipx ensurepath` | `pipx install llm-parliament` |
| macOS | `brew install pipx && pipx ensurepath` | `pipx install llm-parliament` |
| Windows | `python -m pip install --user pipx`<br>`python -m pipx ensurepath` | `pipx install llm-parliament` |

Restart your shell after `ensurepath`, then verify with `parliament doctor`.

<details>
<summary>Full per-platform commands</summary>

**Linux**

```bash
sudo apt install pipx          # or `pacman -S python-pipx`, `dnf install pipx`
pipx ensurepath
# Restart your shell.
pipx install llm-parliament
parliament doctor
```

**macOS**

```bash
brew install pipx
pipx ensurepath
# Restart your shell.
pipx install llm-parliament
parliament doctor
```

**Windows (PowerShell)**

```powershell
# 1. Install Python 3.11+ from python.org — check "Add Python to PATH".
# 2. Install pipx:
python -m pip install --user pipx
python -m pipx ensurepath
# 3. Close and reopen Windows Terminal (recommended) or PowerShell.
pipx install llm-parliament
parliament doctor
```

</details>

**Notes:**

- All cloud provider SDKs (Anthropic, Google, OpenAI) are bundled. No extras needed.
- Ollama (for local models) is a separate native daemon — install from <https://ollama.com> if you want local models. The `parliament doctor` command tells you what's detected.
- On Windows, the install pulls in `windows-curses` automatically so the TUI works out of the box. Windows Terminal is recommended over `cmd.exe` (better VT/UTF-8 support); legacy `cmd.exe` is supported.
- Keys are stored in the OS native credential store (Windows Credential Manager, macOS Keychain, GNOME Keyring) via `parliament keys set`. Falls back to `~/.parliament/keys.env` if no keyring is available.

## Verify your install

```bash
parliament doctor
```

You'll see something like:

```text
Environment
  ✓ Python 3.12.5 (>=3.11 required)
  ✓ Curses available
  ✓ Terminal: 142x38
  ✓ Config: ~/.parliament/config.yaml (initialized)

Providers
  ✓ Anthropic SDK         ℹ ANTHROPIC_API_KEY not set
  ✓ Google SDK            ℹ GOOGLE_API_KEY not set
  ✓ OpenAI SDK            ℹ OPENAI_API_KEY not set
  ℹ Ollama: not reachable at http://localhost:11434

Next steps
  - Add cloud keys:   parliament keys set <provider> <key>
  - Local models?     Install Ollama from https://ollama.com, then `ollama pull llama3.1`
  - Run the TUI:      parliament
```

Exit code is `0` if the install is functional (regardless of whether you
have keys/Ollama configured), or `1` if something is broken (e.g. Python
too old).

## Choosing your models

**You do not need three providers.** Pick whichever row matches what you already
have — the first-run wizard detects your situation and proposes the right one
automatically.

| You have | You get | Cost per debate |
|---|---|---|
| Nothing | Mock parliament — placeholder text, format only | $0 |
| **One cloud key** | Three models from that provider, tiered | ~$0.02–0.10 |
| Two or three cloud keys | Cross-provider debate — the most genuine disagreement | ~$0.04–0.30 |
| Ollama, 8 GB+ RAM | Three local models, fully private | $0 |
| One cloud key + Ollama | One strong cloud Speaker, two cheap local members | ~$0.01–0.03 |

Cross-provider debate is the best version of this tool — three models from
different labs disagree more usefully than three from one. But a single-provider
house still works, and it's the fastest way to try it properly.

### Configuration

Your personal config lives at `~/.parliament/config.yaml` (or
`%USERPROFILE%\.parliament\config.yaml` on Windows) — outside the repo, so
your settings never end up in git.

On first run (triggered by `parliament doctor`, `parliament ask`, or launching
the TUI), a setup wizard runs automatically. It detects your API keys, local
Ollama models, and available RAM, then proposes a matching preset:

```text
Welcome to Parliament. No config found - let's set one up.

Detected:
  ✓ ANTHROPIC_API_KEY (configured)
  ℹ OPENAI_API_KEY (not set)
  ✓ GOOGLE_API_KEY (configured)
  ℹ Ollama: not reachable
  System RAM: 16 GB

Proposed preset: cloud-anthropic-google (Anthropic + Google)
  - Claude (anthropic / claude-sonnet-4-6)
  - Claude-Haiku (anthropic / claude-haiku-4-5-20251001)
  - Gemini (google / gemini-2.5-flash)

Use these defaults? [Y/n]:
```

Confirm with `Y` and the config is written. If no keys or Ollama are detected,
you get a working mock preset — no setup needed to verify the install. Edit
members later via the TUI (`parliament`) or directly in the file.

### Cloud keys

**Easiest path** — export your keys in your shell profile before the first run
and the wizard picks them up automatically:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
parliament doctor   # wizard fires, detects keys, writes a matching preset
```

**After first run** — add or change keys at any time:

```bash
parliament keys set anthropic sk-ant-...
parliament keys set google ...
parliament keys set openai sk-...

parliament keys list
parliament keys migrate   # move existing keys.env entries to the OS keyring
parliament keys remove openai
```

Keys are saved to the OS native credential store. Then edit members via the
TUI (`parliament`) or directly in `~/.parliament/config.yaml`:

```yaml
parliament:
  members:
    - name: Claude
      provider: anthropic
      model: claude-sonnet-4-6
    - name: Gemini
      provider: google
      model: gemini-2.5-flash
```

You can also export `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and
`GOOGLE_API_KEY` directly in your environment instead of using the keyring.

### Local models (Ollama)

Ollama runs LLMs locally — free, private, no API keys.

1. Install Ollama from <https://ollama.com> and start the daemon.
2. Pull a model:
   ```bash
   ollama pull llama3.1
   ```
3. Edit `~/.parliament/config.yaml` (or use the TUI) to add an Ollama member:
   ```yaml
   parliament:
     members:
       - name: Llama
         provider: ollama
         model: llama3.1
   providers:
     ollama:
       base_url: http://localhost:11434/v1
   ```
4. Run `parliament` to start a debate.

> **Note:** All providers default to no timeout (`timeout: null`), so a
> slow local model on modest hardware won't be cut off. If you want a
> hard limit, set `timeout: 600.0` on the relevant `providers.<name>`
> block.

## What it costs

A debate is **7 API calls** — 3 First Reading, 3 Debate, 1 Division — against 1
for a single-model question. In absolute terms that's cents, not dollars:

| Setup | Per debate |
|-------|------|
| Single GPT-4o (for comparison) | ~$0.02 |
| Parliament — 3× cheap (Haiku + Flash-Lite + GPT-4o-mini) | ~$0.04–0.06 |
| Parliament — 3× mid-tier (Sonnet + GPT-4o + Flash) | ~$0.15–0.30 |
| Parliament — local Ollama models | $0.00 |

Two ways to keep it low: **mix tiers** — one strong model as Speaker for the
Division, two fast cheap ones for First Reading and Debate, which the wizard
does by default and which lands close to a single mid-tier call. Or **go local**
— Ollama members cost nothing but electricity.

Use `parliament ask "..." --mock` to explore the format at zero cost.

## CLI Usage

```bash
# Check that the install is healthy
parliament doctor

# Use mock providers for fast local testing
parliament ask "Is this architecture too complex?" --mock

# Show the full transcript before the verdict (post-hoc dump)
parliament ask "Which queue should we use?" --verbose

# Hide the live debate panels and only print the final verdict
parliament ask "Quick check?" --no-show-debate

# Choose the Speaker for the final synthesis
parliament ask "What are the main risks?" --speaker Claude

# Show configured members
parliament members

# Open the full TUI dashboard
parliament

# Open the TUI with mock providers, no Ollama/API keys needed
parliament --mock

# Browse the same dashboard with a specific config
parliament tui --config /path/to/custom-config.yaml
```

### Live debate view

By default, `parliament ask` and the curses TUI render the debate live: a
panel pops in for each member as their analysis lands, and stage headers mark
the transitions through First Reading → Debate → Division. This makes it
obvious *which* model is currently working and *what* they said.

The view is toggleable via three precedence-ordered sources:

| Precedence | Source | Example |
| --- | --- | --- |
| 1 (highest) | CLI flag | `parliament ask "..." --no-show-debate` |
| 2 | Environment variable | `PARLIAMENT_SHOW_DEBATE=0 parliament ask "..."` |
| 3 | YAML config | `display:\n  show_debate: false` |
| 4 (default) | Built-in | live view is **on** |

`--show-debate` controls whether the live panels appear during the run.

### Hansard detail levels

Every debate is saved as a Markdown file in `~/.parliament/hansards/`. By
default, both the post-run terminal output and the saved `.md` file contain the
four-part Speaker synthesis (Consensus, Split, Risks, Recommendation) — no LLM
transcripts. Older runs that included the full debate text by default are now
opt-in via `--hansard=full`.

Four levels:

| Level | Includes | Roughly |
|---|---|---|
| `minimal` | Recommendation only | one paragraph — "just tell me what to do" |
| `verdict` | Full four-part synthesis | **default** — concise but complete |
| `archive` | + YAML frontmatter + session footer | searchable in Obsidian, no walls of text |
| `full` | + First Reading + Debate transcripts | today's full record (≈ what `--verbose` used to print) |

Set the level via three precedence-ordered sources:

| Precedence | Source | Example |
| --- | --- | --- |
| 1 (highest) | CLI flag | `parliament ask "..." --hansard archive` |
| 2 | Environment variable | `PARLIAMENT_HANSARD_LEVEL=full parliament ask "..."` |
| 3 | YAML config | `hansard:\n  level: archive` |
| 4 (default) | Built-in | `verdict` |

`--verbose` continues to work; it's an alias for `--hansard=full`.
The level applies to the saved `.md` file **and** the post-run terminal
output. The live in-flight debate view is independent — toggle it
separately with `--show-debate` / `--no-show-debate`.

### TUI controls

```text
Type                Edit the question field
Enter               Run debate when question is focused
Tab                 Switch between question and members
Up/down or j/k      Move through models
Enter               Open selected member settings when members are focused
s                   Open settings when members are focused; save result from verdict screen
e                   Edit the selected member from the detail view
Left/backspace/Esc  Return from settings to dashboard
Ctrl+U              Clear the question field
Ctrl+S              Save member edits
q                   Quit when focused on members/settings
Ctrl+Q              Quit from anywhere
```

The TUI settings screen lets you set the local directory used for saved
Hansard Markdown responses. By default, saved responses go to
`~/.parliament/hansards`.

Member editing stays inside the TUI. The editor lets you change `Name`,
`Provider`, `Model`, and `Base URL`, while `Tier`, `Role`, and API key status
remain derived and read-only. Model pickers include supported presets plus a
`Custom model` escape hatch.

Inside the member editor, `Enter` opens provider/model pickers when those
fields are focused and saves the edit when the base URL field is focused.

## Contributing

> 👋 **This is my GitHub and developer debut!**
> `llm-parliament` is the first project I've shipped publicly. I built it to learn,
> and I'd genuinely love your help making it better.
>
> Feedback, bug reports, feature ideas, code review, and pull requests are **very
> welcome** — no contribution is too small. If something feels confusing, doesn't
> install, breaks on your terminal, or could be more polished, please
> [open an issue](https://github.com/elarmuzik1993/llm-parliament/issues/new) or
> say hi in [Discussions](https://github.com/elarmuzik1993/llm-parliament/discussions).
>
> Stars also help me see what's resonating. Thanks for taking a look. 🙏

Good first stops: the [open issues](https://github.com/elarmuzik1993/llm-parliament/issues)
labelled `help wanted`, and [CONTRIBUTING.md](CONTRIBUTING.md) for the
test-and-lint gate. [AGENTS.md](AGENTS.md) is the architecture source of truth —
read it before touching the code.

## Development

Clone the repo and create a virtual environment.

Linux / macOS:

```bash
git clone https://github.com/elarmuzik1993/llm-parliament.git
cd llm-parliament

python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[all,dev]"
```

Windows (PowerShell):

```powershell
git clone https://github.com/elarmuzik1993/llm-parliament.git
cd llm-parliament

python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[all,dev]"
```

(In `cmd.exe`, use `.venv\Scripts\activate.bat` instead.)

Run the test suite:

```bash
python -m pytest
```

Run Ruff:

```bash
ruff check .
```

Try the CLI without external services:

```bash
parliament ask "What should we test first?" --mock
```

## Project Layout

```text
src/parliament/
  cli.py                  Click CLI (parliament ask / doctor / keys / members / tui / update)
  commands.py             Slash commands (/help, /update, /doctor, /history, /copy, …)
  config.py               YAML config loading, key management, resolve_* precedence helpers
  doctor.py               Health-check logic (Python, curses, terminal, providers, Ollama)
  model_catalog.py        Provider model presets + tier data for pickers
  tui.py                  Curses TUI — all screens, key handling, main loop
  core/                   Parliament orchestrator, dataclasses, ProgressEvent
  procedures/             First Reading, Debate, and Division phases
  providers/              Adapters for Ollama, OpenAI, Anthropic, Google, plus Mock
  render/                 HansardLevel + terminal/markdown renderers + live CLI/TUI views
tests/                    Pytest suite (pytest-asyncio)
scripts/
  diagnose-render.py      Render diagnostic — colors + spinner debugging
config.example.yaml       Default config template (fallback if first-run wizard fails)
config.cloud.yaml         Cloud-only example (Anthropic + Google + OpenAI)
config.mixed.yaml         Mixed example (Ollama + cloud)
AGENTS.md                 Contributor source-of-truth (architecture, conventions)
CHANGELOG.md              Release history (Keep-a-Changelog)
RELEASING.md              PyPI release procedure
```

See [CHANGELOG.md](CHANGELOG.md) for the release history.

## Disclaimer

LLM Parliament is an orchestration framework. It coordinates multiple AI models
to provide structured debate and synthesis. Users are responsible for complying
with the Terms of Service and Usage Policies of their respective LLM providers
(e.g., Ollama, OpenAI, Anthropic, Google). This tool does not bypass safety filters or
usage restrictions of the underlying models.

## Privacy

LLM Parliament is a local tool with no telemetry, analytics, or remote
reporting of any kind. The author receives no data from your usage.

**What leaves your machine and where it goes:**

| Traffic | Destination | When |
|---------|-------------|------|
| Your debate question + LLM responses | Your configured providers only (Anthropic / OpenAI / Google / Ollama) | During a debate |
| Model list request (for TUI picker) | Same provider API, using your key | When you open the member picker |
| Ollama reachability probe | `localhost:11434` — never leaves the machine | On `parliament doctor` and first-run wizard |

**What never leaves your machine:**

- API keys — stored in the OS keyring or `~/.parliament/keys.env`, never
  logged or included in any output
- Saved Hansard files — written to `~/.parliament/hansards/` locally only
- Config — `~/.parliament/config.yaml` is read locally, never transmitted

You can verify this by inspecting the source: all outbound calls are in
`src/parliament/providers/` (debate traffic to your providers) and
`src/parliament/model_catalog.py` (model list fetches to your providers).
There are no other network calls in the codebase.

## License

AGPLv3
