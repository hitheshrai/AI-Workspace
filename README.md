# AI-Workspace: Multi-Model Agent Memory & Workflow System

A lightweight, vendor-agnostic, file-based memory and workflow coordination system for AI coding agents (Claude Code, Gemini CLI / Antigravity, Cursor, Aider, Ollama, and custom LLM scripts).

## Core Philosophy

1. **Vendor-Neutral & Portable**: Uses standard Markdown files and POSIX conventions. No database or background daemon required.
2. **Decoupled Architecture**: Code stays in its native Git repositories; memory stays organized in this central hub.
3. **Multi-Model Support**: Allows frontier cloud models (Claude, GPT, Gemini) and local models (DeepSeek, Llama, Qwen via Ollama/vLLM) to collaborate on the same projects without losing context.
4. **Verification Over Handoff**: Memory is treated as a briefing, not proof. Code, Git, tests, and primary data are always authoritative.

---

## Quickstart: Setup on Any Device (1 Command)

```bash
git clone https://github.com/hitheshrai/AI-Workspace.git ~/AI-Workspace
cd ~/AI-Workspace
./install.sh
```

The installer will:
* Verify Python 3.
* Initialize local `GLOBAL.md` and `PROJECTS.md` if not already present.
* Install universal `~/AGENTS.md` instructions into your home directory.
* Symlink the `ai-mem` CLI tool into `~/.local/bin/`.

Verify everything with:
```bash
ai-mem doctor
```

---

## Daily Workflow with Any Model

### 1. Register a project repository
Navigate into your code repository and run:
```bash
cd /path/to/my-repo
ai-mem init my-project
```
This automatically scaffolds `projects/my-project/` and registers it in `PROJECTS.md`.

### 2. Auto-Inject IDE & Tool Rules
Generate configuration pointers for your preferred tools inside your code repository:
```bash
ai-mem inject all        # Generates rules for Cursor, Aider, Claude, and GitHub Copilot
# Or specifically:
ai-mem inject cursor     # Generates .cursor/rules/agent-memory.mdc
ai-mem inject aider      # Generates .aider.conf.yml
ai-mem inject claude     # Generates CLAUDE.md
ai-mem inject copilot    # Generates .github/copilot-instructions.md
```

### 3. Running Any Model

* **With Cursor / Windsurf / Cline**:
  The editor automatically reads the generated rule and links directly to the project's `CURRENT.md`.
* **With Local Models via Ollama (DeepSeek / Qwen / Llama)**:
  Use tiered context budgeting to fit your model's context window:
  ```bash
  # Tier 1 (Frontier / Reasoning): Full charter + current state + decisions
  ai-mem prompt --tier 1
  
  # Tier 2 (Mid-Weight 32B/70B): Scope + current state
  (ai-mem prompt --tier 2 && echo "Task: fix issue #42") | ollama run qwen2.5-coder:32b
  
  # Tier 3 (Fast / Edge 7B/14B): Immediate state only (<500 tokens)
  (ai-mem prompt --tier 3 && echo "Task: write unit tests") | ollama run deepseek-coder:6.7b
  ```
* **With Claude Code / Gemini CLI**:
  Start the CLI in your repository; it automatically picks up `~/AGENTS.md` and `CURRENT.md`.

### 4. Viewing Past Session Handoffs
Review recent sessions and model contributions right from your terminal:
```bash
ai-mem log -n 5
```

### 5. Ending a Session
Instruct your agent to *"Save the session"* or run:
```bash
ai-mem save
```
This interactively drafts a structured session record capturing the Git commit, branch, actions taken, verification results, and next steps.

---

## `ai-mem` CLI Reference

| Command | Purpose |
|---|---|
| `ai-mem doctor` | Runs workspace health check (paths, registry syntax, current repo alignment). |
| `ai-mem status` | Displays active repository Git status and memory alignment side by side. |
| `ai-mem init <slug>` | Scaffolds and registers memory for the current repository in one step. |
| `ai-mem inject <tool>` | Injects tool configurations (`cursor`, `aider`, `claude`, `copilot`, `all`). |
| `ai-mem prompt [--tier N]` | Generates tiered context prompt (`--tier 1|2|3`) for piping into any LLM. |
| `ai-mem log [-n N]` | Displays a clean summary table of the last $N$ sessions for the active repo. |
| `ai-mem save` | Interactively scaffolds a dated session handoff in `projects/<slug>/sessions/`. |

---

## Directory Layout

```text
AI-Workspace/
├── install.sh              # One-command universal installer
├── README.md               # This guide
├── GLOBAL.md.example       # Template for machine-level environment rules
├── PROJECTS.md.example     # Template project mapping registry
├── RETRIEVAL.md            # Context budget & search policy
├── MODEL_ROUTING.md        # Data privacy & model routing guide
├── INTEGRATIONS.md         # Optional integration roadmap
├── bin/
│   ├── ai-mem              # Zero-dependency Python CLI (doctor, prompt, save, log, inject, init)
│   └── init-project-memory # Shell script to scaffold new project memory
└── templates/              # Standard templates for project files
    ├── AGENTS.md           # Universal instructions for home directory
    ├── PROJECT.md          # Project charter & data classification
    ├── CURRENT.md          # Live status & next actions
    ├── DECISIONS.md        # Append-only architectural log
    ├── EXPERIMENTS.md      # Append-only run/benchmark log
    └── SESSION_HANDOFF.md  # Template for session handoff records
```
