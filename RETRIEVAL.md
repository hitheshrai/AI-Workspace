# Retrieval Policy

Last reviewed: 2026-09-10

## Search order

1. Read `AGENTS.md`, the registered `PROJECT.md`, and concise `CURRENT.md`.
2. Use exact filename, symbol, or keyword search before a generative model.
3. Search decisions, experiments, and session handoffs; retrieve only the most
   relevant passages with their source paths.
4. Inspect repository files and Git to verify what actually exists.
5. Use a code graph only when relationships are materially difficult to recover
   from targeted source inspection.

## Initial context allowances

These are starting limits, not hard correctness limits:

- Project orientation: 500–1,000 tokens.
- Retrieved evidence: 1,000–3,000 tokens.
- Default retrieval: top 3 passages, about 1,000 tokens total.
- Raw transcripts: never automatically loaded.
- Full graph reports and whole experiment logs: load only for a justified review.

Expand context when evidence is incomplete. Track retrieval, indexing,
summarization, retries, and final-model use together when measuring cost.

## Context packet

Every assembled packet should identify the project, task, session, repository
revision, data classification, constraints, selected evidence, and source paths.
Hidden reasoning and native chat history are not portable memory.

