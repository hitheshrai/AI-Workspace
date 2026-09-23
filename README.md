# AI-Workspace: Multi-Model Agent Memory & Workflow System

A lightweight, vendor-agnostic, file-based memory and workflow coordination system for AI coding agents (Claude Code, Gemini CLI / Antigravity, Cursor, Aider, Ollama, and custom LLM scripts).

## Core Philosophy

1. **Vendor-Neutral & Portable**: Uses standard Markdown files and POSIX conventions. No database or proprietary daemon required.
2. **Decoupled Architecture**: Code stays in its native Git repositories; memory stays organized in this central hub.
3. **Multi-Model Support**: Allows frontier cloud models (Claude, GPT, Gemini) and local models (DeepSeek, Llama, Qwen via Ollama/vLLM) to collaborate on the same projects without losing context.
4. **Verification Over Handoff**: Memory is treated as a briefing, not proof. Code, Git, tests, and data are always authoritative.

---

## Quickstart: Setup on a New Device

### 1. Clone this repository
```bash
git clone https://github.com/hitheshrai/AI-Workspace.git ~/AI-Workspace
cd ~/AI-Workspace
```

### 2. Initialize local configuration
```bash
# Copy starter environment and project registry templates
cp GLOBAL.md.example GLOBAL.md
cp PROJECTS.md.example PROJECTS.md

# Install universal agent rules to your home directory
cp templates/AGENTS.md ~/AGENTS.md

# (Optional) Add CLI tools to your PATH
mkdir -p ~/.local/bin
ln -s ~/AI-Workspace/bin/ai-mem ~/.local/bin/ai-mem
ln -s ~/AI-Workspace/bin/init-project-memory ~/.local/bin/init-project-memory
```

---

## Daily Workflow with Any Model

### 1. Register a project
To manage memory for a repository at `/path/to/my-repo`:
```bash
init-project-memory my-project /path/to/my-repo
```
Then add the mapping row to `~/AI-Workspace/PROJECTS.md`:
```markdown
| My Project | /path/to/my-repo | projects/my-project | Active |
```

### 2. Launching any Agent or Model
Navigate into your code repository (`cd /path/to/my-repo`).

* **With Cursor / Windsurf / Cline**:
  The agent automatically reads `~/AGENTS.md` and discovers the project's `CURRENT.md`.
* **With Local Models via Ollama (DeepSeek / Qwen / Llama)**:
  ```bash
  (ai-mem prompt --tier 2 && echo "Task: fix issue #42") | ollama run qwen2.5-coder:32b
  ```
* **With Claude Code / Gemini CLI**:
  Simply start the CLI inside your repository.

### 3. Ending a Session
Instruct your agent to *"Save the session"* or run:
```bash
ai-mem save
```
This records a structured, dated session log in `projects/<slug>/sessions/` capturing git commit, branch, actions taken, and next steps.

---

## Directory Layout

```text
AI-Workspace/
├── README.md               # This guide
├── GLOBAL.md.example       # Template for machine-level environment rules
├── PROJECTS.md.example     # Template project mapping registry
├── RETRIEVAL.md            # Context budget & search policy
├── MODEL_ROUTING.md        # Data privacy & model routing guide
├── INTEGRATIONS.md         # Optional integration roadmap
├── bin/
│   ├── ai-mem              # Zero-dependency Python CLI for context & sessions
│   └── init-project-memory # Shell script to scaffold new project memory
└── templates/              # Standard templates for project files
    ├── AGENTS.md           # Universal instructions for home directory
    ├── PROJECT.md          # Project charter & data classification
    ├── CURRENT.md          # Live status & next actions
    ├── DECISIONS.md        # Append-only architectural log
    ├── EXPERIMENTS.md      # Append-only run/benchmark log
    └── SESSION_HANDOFF.md  # Template for session handoff records
```
