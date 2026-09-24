# Reliability and Security Audit

Audit baseline: `49b0c3ad13930b2231f22c89d028550dac18b8c0`, Linux/aarch64,
Python 3.12.3. The baseline had uncommitted hardening changes to `README.md`,
`bin/ai-mem`, and `bin/voyager`; they were preserved and extended. All tests
use temporary workspaces, repositories, homes, and synthetic canary secrets.
No model API or external service was contacted.

## Fixed findings

| Severity | Finding | Reproduction / effect | Status |
|---|---|---|---|
| High | Lock updates could collide and corrupted the Markdown table. | Concurrent `lock` calls could lose rows; new row was inserted before the header. | Fixed with `flock`, atomic replacement, table-aware insertion, exact ownership, and subprocess contention tests. This coordinates only clients sharing one filesystem. |
| High | Initializer accepted path traversal slugs. | `ai-mem init ../outside` could write outside `projects/`. | Fixed with strict slugs and regression test. |
| High | Session creation could overwrite a same-second handoff. | Two saves sharing a timestamp used the same filename. | Fixed with a lock, exclusive create, suffixing, and mode `0600`. |
| High | Compaction could overwrite an existing archive target. | A collision silently replaced historical content. | Fixed by refusing all colliding batches before moving files; hashes are tested. |
| Medium | Prompt output did not enforce documented cloud classification. | A local-only project could be emitted for an explicitly requested cloud route. | Fixed: `--route cloud` fails closed; `cloud-approved` also requires an approved `--provider`. |
| Medium | Secret filtering was incomplete at prompt output. | Passwords, credential URLs, AWS-style keys, and private keys could cross a model boundary. | Expanded redaction at prompt and save boundaries; synthetic canaries tested. It is pattern-based, not a DLP guarantee. |
| Medium | Installer followed pre-existing/broken symlinks and replaced command links. | A user-controlled symlink could be written through; a command could be replaced. | Fixed: installer preserves existing files, symlinks, and commands. |
| Medium | CLI option errors raised Python tracebacks. | `log -n nope` and malformed options crashed. | Replaced ad hoc parsing with `argparse`; invalid input exits 2 cleanly. |
| Low | AST mapper followed file symlinks and directly rewrote its output. | It could read an external linked file or write through an output symlink. | Fixed: mapper skips symlink files, limits Python parsing to 1 MiB, refuses output symlinks, and writes atomically. |

## Demonstrated guarantees

- The tested commands preserve existing integration files, avoid path traversal,
  and keep archive content unchanged when compaction is refused.
- On one shared POSIX filesystem, concurrent lock writers retain distinct rows;
  same-workstream contention has one successful owner, and another owner cannot
  unlock it.
- `local-only` and unknown classifications fail closed for the explicit cloud
  prompt route. `cloud-approved` requires a listed provider.

## Important limits and remaining gaps

- File locks are advisory and only coordinate processes that use this CLI on
  the same filesystem. Separate clones/devices do **not** coordinate through
  Git; a distributed lease service or merge-aware workflow is required for that.
- The injected Cursor/Aider/Claude/Copilot files are pointers and instructions.
  This audit proves they are generated, not that an IDE or model honors them.
- Secret filtering is an allowlist of patterns, not a guarantee against every
  credential format or data leak. `.gitignore` also prevents neither deliberate
  adds nor previously tracked secrets.
- `bin/init-project-memory` is a separate shell helper: its macOS compatibility
  is unverified because it relies on GNU-style `sed -i`. Prefer `ai-mem init`
  until it is made portable and transaction-safe.
- Linux/Python 3.12 was exercised. macOS, WSL, Python 3.6/3.7, permission-fault
  injection, terminated-mid-write recovery, and multi-device Git locking were
  not executed in this environment.

## Result

Final local run: **14 passed, 0 failed, 0 skipped, 0 blocked**. CI is provided
but not run. See [TESTING.md](TESTING.md) for reproduction commands.
