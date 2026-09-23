# Model Routing and Privacy Policy

Last reviewed: 2026-09-10

## Principles

- Memory belongs to projects, not models or providers.
- Retrieval and privacy filtering happen before model access.
- Local storage does not imply local processing: content placed in a cloud prompt
  has left the local machine.
- Route by task policy and measurable validation, never by model confidence alone.
- Scientific computation belongs in reproducible software; models may help plan,
  explain, or review it but do not replace numerical validation.

## Data classifications

| Classification | Model access policy |
|---|---|
| `local-only` | Local inference only; stop or queue if unavailable |
| `cloud-approved` | Only providers/models explicitly approved in `PROJECT.md` |
| `public` | Any configured provider, subject to budget and source policy |

No silent downgrade from `local-only` to cloud is permitted. Unknown
classification defaults to `local-only`.

## Starting routes

| Work | Preferred route | Required validation |
|---|---|---|
| Exact lookup | Search tools, no model | Inspect source |
| Retrieval ranking | Local retrieval model | Retrieval evaluation |
| Handoff drafting | Small local model or current agent | Preserve source paths |
| Difficult architecture/debugging | Approved capable model | Tests and code review |
| Restricted research interpretation | Local model | Evidence and human review |
| Fitting/statistics/simulation | Scientific software | Reproducible checks |

An optional gateway may enforce provider allowlists, budgets, routing, and audit
metadata for custom applications. Existing CLIs retain their native agent loops
unless their documented connection mechanism is deliberately configured.

## ASU RC Voyager (`openai.rc.asu.edu`)

Configured 2026-09-20 as a direct-script offload route (`bin/voyager`, see
`INTEGRATIONS.md` phase 4b), introduced to reduce token spend on the primary
Claude Code session. It is ASU RC-operated infrastructure, but from this
framework's perspective it is a **network call to an external host**, not
local inference (phase 3) — it does not by itself satisfy `local-only`.

- Default treatment: `cloud-approved`/`public` work only (ad hoc drafting,
  bulk text processing, routine coding subtasks not tied to a registered
  project's restricted data).
- A project's `local-only` data may only be routed to Voyager once that
  project's `PROJECT.md` explicitly records Voyager under "Approved cloud
  providers/models." No silent downgrade for any project that hasn't.
- Approved 2026-09-20 (data stays within ASU RC custody, which resolves the
  third-party-exfiltration concern this rule mainly guards against):
  `hydride-perovskite-screening`, `antiperovskite-vasp`,
  `perovskite-dft-repo`, `mse511`, `gridsense`, `litgpt`.
- Explicitly NOT approved: `cspbcl3-mcnp` — Rolston-lab ARO grant, MCNP
  proton-transport work. Institutional ownership of Voyager does not
  satisfy export-control (ITAR/EAR) certification requirements, which are
  about access-control certification, not data locality. Requires
  PI/export-control sign-off before revisiting.
- The primary Claude Code session decides per task whether to delegate to
  Voyager or handle it directly; it is not a transparent proxy for the
  session's own reasoning.

