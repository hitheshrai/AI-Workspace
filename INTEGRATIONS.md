# Integration Roadmap

Last reviewed: 2026-09-10

Optional tools are introduced one layer at a time and evaluated before broader
deployment.

| Phase | Capability | Candidate | State |
|---|---|---|---|
| 1 | Authoritative memory and handoffs | Markdown + Git | Implemented; Git initialization optional |
| 2 | Cross-project Markdown retrieval | QMD | Proposed; not installed |
| 3 | Local inference | Ollama or evaluated alternative | Proposed; not configured |
| 4 | Custom-app model gateway | LiteLLM or evaluated alternative | Proposed; not configured |
| 4b | Direct-script model offload (no gateway/allowlist/budget layer) | ASU RC Voyager (`openai.rc.asu.edu`, OpenAI-compatible) | Configured 2026-09-20: `bin/voyager` CLI (stdlib-only), used ad hoc to offload token-cheap work from the primary Claude Code session. Auto-mode network classifier allowlisted for this host. Not a substitute for phase 4 — no allowlist/budget/audit enforcement. See `MODEL_ROUTING.md` for data-classification constraints. |
| 5 | Large-codebase relationships | Graphify | Selective pilot only |
| 6 | Automatic capture | AgentMemory | Later isolated pilot only |

## Acceptance checks

- Installation source and version are reviewed and pinned where practical.
- Indexing remains local for `local-only` projects.
- Indexes can be rebuilt from authoritative files.
- Retrieved passages retain source paths.
- A local-service outage cannot trigger cloud fallback.
- Retrieval quality and cost per correctly completed task are measured.
- Automatic capture excludes secrets, restricted data, and noisy tool output.

Do not deploy overlapping retrieval/capture systems simultaneously during the
first pilot.

