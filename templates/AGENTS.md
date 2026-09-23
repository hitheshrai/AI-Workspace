# Shared Agent Instructions

These rules apply to AI coding agents operating across workspaces.

## Memory workflow
1. Read `~/AI-Workspace/GLOBAL.md`.
2. Find the current repository in `~/AI-Workspace/PROJECTS.md`.
3. If registered, read its `PROJECT.md` and `CURRENT.md` in the listed memory directory. Load `DECISIONS.md`, `EXPERIMENTS.md`, or session logs only when relevant.
4. Treat memory as a handoff, not proof. Verify claims against code, Git, tests, and data before acting.

If a repository contains a local `AGENTS.md` or `CLAUDE.md`, follow it in addition to this file.

## Before ending substantial work
- Create a unique, dated session record from the session template for meaningful work. Never overwrite another session's handoff.
- Update `CURRENT.md` only when you are the designated consolidator or the sole active workstream.
- Record durable choices in `DECISIONS.md` and meaningful runs/benchmarks in `EXPERIMENTS.md`.
- Keep `CURRENT.md` concise; archive stale detail in session records.

## Safety and coordination
- Git, code, and tested artifacts are authoritative; memory does not replace them.
- Never store secrets, passwords, API tokens, or restricted personal data in agent memory.
- For concurrent agents, register active workstreams in `CURRENT.md` and avoid editing overlapping files.
