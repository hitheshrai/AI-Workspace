# Testing

## Requirements

- Python 3.8+ for the test suite (the runtime CLI remains compatible with Python
  3.6+).
- Git and a POSIX shell (`bash`) on PATH.
- Linux or another POSIX system that provides `fcntl.flock` for concurrency tests.

The suite uses only the Python standard library. It copies the checkout to a
temporary directory, creates synthetic Git repositories and fake home
directories, and never reads real project memory or credentials.

## Run locally

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile bin/ai-mem bin/voyager
bash -n install.sh bin/init-project-memory
git diff --check
```

## What is exercised

- Installer idempotence, user-file preservation, broken symlinks, and existing
  command preservation.
- Every `ai-mem` command via subprocess: `doctor`, `status`, `init`, `inject`,
  `map`, `lock`, `unlock`, `prompt`, `log`, `save`, and `compact`.
- Invalid arguments, unregistered repositories, invalid Python, symlinks,
  malformed numeric input, duplicate initialization, save permissions, and
  compaction collisions.
- Concurrent independent processes for same- and different-workstream locking.
- Prompt secret redaction and local-only / cloud-approved route policy.

GitHub Actions runs the suite on Python 3.8 and 3.12. CI configuration is
included but has not been executed by this audit.
