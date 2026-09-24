"""Isolated, black-box regression tests for the ai-mem command line interface."""

import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class CliFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace with ünicode"
        shutil.copytree(ROOT, self.workspace, ignore=shutil.ignore_patterns(".git", "projects", "GLOBAL.md", "PROJECTS.md", "__pycache__"))
        self.home = self.root / "home"
        self.home.mkdir()
        self.repo = self.root / "repo with spaces"
        self.repo.mkdir()
        self.git("init")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test User")
        (self.repo / "app.py").write_text("class Service:\n    pass\n\ndef useful():\n    return 1\n")
        self.git("add", "app.py")
        self.git("commit", "-m", "fixture")
        self.env = dict(os.environ, AI_WORKSPACE_DIR=str(self.workspace), HOME=str(self.home), PATH="/usr/bin:/bin")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=str(self.repo), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def cli(self, *args, input=None, cwd=None, timeout=15):
        return subprocess.run([str(self.workspace / "bin" / "ai-mem"), *args], cwd=str(cwd or self.repo), env=self.env,
                              input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)

    def init(self, slug="demo"):
        result = self.cli("init", slug)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.workspace / "projects" / slug


class AiMemCliTest(CliFixture):
    def test_installer_is_idempotent_and_preserves_existing_user_file(self):
        agents = self.home / "AGENTS.md"
        agents.write_text("existing rules\n")
        first = subprocess.run(["bash", "install.sh"], cwd=str(self.workspace), env=self.env, text=True, capture_output=True, timeout=15)
        second = subprocess.run(["bash", "install.sh"], cwd=str(self.workspace), env=self.env, text=True, capture_output=True, timeout=15)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(agents.read_text(), "existing rules\n")
        self.assertTrue((self.home / ".local" / "bin" / "ai-mem").is_symlink())
        self.assertTrue((self.workspace / "GLOBAL.md").is_file())
        self.assertTrue((self.workspace / "PROJECTS.md").is_file())

    def test_installer_preserves_broken_symlinks_and_existing_commands(self):
        broken = self.workspace / "GLOBAL.md"
        broken.symlink_to(self.root / "missing-target")
        command = self.home / ".local" / "bin" / "ai-mem"
        command.parent.mkdir(parents=True)
        command.write_text("user command\n")
        result = subprocess.run(["bash", "install.sh"], cwd=str(self.workspace), env=self.env, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(broken.is_symlink())
        self.assertEqual(command.read_text(), "user command\n")
        self.assertIn("preserved", result.stdout)

    def test_full_workflow_and_prompt_privacy_boundary(self):
        project = self.init()
        (project / "PROJECT.md").write_text("## Data classification\n\n- Default: `local-only`\nsecret=super-secret-value\n")
        (project / "CURRENT.md").write_text("# Current\npassword: fake-password\n")
        (project / "DECISIONS.md").write_text("Bearer abcdefghijklmnopqrstuvwxyz012345\n")
        status = self.cli("status")
        self.assertEqual(status.returncode, 0)
        self.assertIn("REGISTERED & ACTIVE", status.stdout)
        prompt = self.cli("prompt", "--tier", "1")
        self.assertEqual(prompt.returncode, 0)
        self.assertNotIn("fake-password", prompt.stdout)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz012345", prompt.stdout)
        cloud = self.cli("prompt", "--route", "cloud")
        self.assertEqual(cloud.returncode, 3)
        self.assertIn("cannot be emitted", cloud.stderr)
        (project / "PROJECT.md").write_text("## Data classification\n\n- Default: `cloud-approved`\n- Approved cloud providers/models: voyager\n")
        unapproved = self.cli("prompt", "--route", "cloud", "--provider", "other")
        self.assertEqual(unapproved.returncode, 3)
        approved = self.cli("prompt", "--route", "cloud", "--provider", "voyager")
        self.assertEqual(approved.returncode, 0, approved.stderr)
        saved = self.cli("save", input="Agent Name\nModel/X\nTask ../ strange | name\n")
        self.assertEqual(saved.returncode, 0, saved.stderr)
        session = next((project / "sessions").glob("*.md"))
        self.assertNotIn("/", session.name)
        self.assertEqual(session.stat().st_mode & 0o077, 0)
        log = self.cli("log", "-n", "1")
        self.assertEqual(log.returncode, 0)
        self.assertIn("Task:", log.stdout)

    def test_init_is_safe_and_repeatable(self):
        bad = self.cli("init", "../escape")
        self.assertEqual(bad.returncode, 2)
        self.assertFalse((self.root / "escape").exists())
        self.init("safe-project")
        duplicate = self.cli("init", "safe-project")
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn("already exists", duplicate.stdout)
        missing = self.cli("init")
        self.assertEqual(missing.returncode, 2)

    def test_inject_all_preserves_existing_files_and_is_idempotent(self):
        self.init()
        existing = self.repo / "CLAUDE.md"
        existing.write_text("do not replace\n")
        first = self.cli("inject", "all")
        second = self.cli("inject", "all")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(existing.read_text(), "do not replace\n")
        for path in [self.repo / ".cursor/rules/agent-memory.mdc", self.repo / ".aider.conf.yml", self.repo / ".github/copilot-instructions.md"]:
            self.assertTrue(path.is_file())
        self.assertIn("Skipped existing file", second.stdout)
        invalid = self.cli("inject", "unknown")
        self.assertEqual(invalid.returncode, 2)

    def test_map_does_not_execute_or_follow_symlinks(self):
        project = self.init()
        (self.repo / "bad.py").write_text("not valid python(")
        outside = self.root / "outside.py"
        outside.write_text("raise RuntimeError('must not execute')\n")
        (self.repo / "linked.py").symlink_to(outside)
        result = self.cli("map")
        self.assertEqual(result.returncode, 0, result.stderr)
        architecture = (project / "ARCHITECTURE.md").read_text()
        self.assertIn("Service", architecture)
        self.assertNotIn("linked.py", architecture)
        self.assertFalse((self.repo / "must-not-execute").exists())
        (project / "ARCHITECTURE.md").unlink()
        (project / "ARCHITECTURE.md").symlink_to(outside)
        blocked = self.cli("map")
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("symlink", blocked.stderr)

    def test_lock_ownership_and_concurrent_different_workstreams(self):
        project = self.init()
        env_a = dict(self.env, AI_MEM_OWNER="owner-a")
        env_b = dict(self.env, AI_MEM_OWNER="owner-b")
        command_a = [str(self.workspace / "bin" / "ai-mem"), "lock", "alpha"]
        command_b = [str(self.workspace / "bin" / "ai-mem"), "lock", "beta"]
        first = subprocess.Popen(command_a, cwd=str(self.repo), env=env_a, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.Popen(command_b, cwd=str(self.repo), env=env_b, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(first.communicate(timeout=15)[0].count("Registered"), 1)
        self.assertEqual(second.communicate(timeout=15)[0].count("Registered"), 1)
        current = (project / "CURRENT.md").read_text()
        self.assertIn("| alpha |", current)
        self.assertIn("| beta |", current)
        foreign = self.cli("unlock", "alpha", "--owner", "owner-b")
        self.assertEqual(foreign.returncode, 1)
        self.assertIn("belongs to", foreign.stderr)
        self.assertIn("| alpha |", (project / "CURRENT.md").read_text())
        owner = self.cli("unlock", "alpha", "--owner", "owner-a")
        self.assertEqual(owner.returncode, 0)
        self.assertNotIn("| alpha |", (project / "CURRENT.md").read_text())

    def test_same_workstream_contention_has_one_winner(self):
        project = self.init()
        commands = []
        for owner in ("owner-a", "owner-b"):
            commands.append(subprocess.Popen([str(self.workspace / "bin" / "ai-mem"), "lock", "same"], cwd=str(self.repo),
                                             env=dict(self.env, AI_MEM_OWNER=owner), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        results = [process.communicate(timeout=15) for process in commands]
        exits = [process.returncode for process in commands]
        self.assertEqual(sorted(exits), [0, 1], results)
        rows = [line for line in (project / "CURRENT.md").read_text().splitlines() if line.startswith("| same |")]
        self.assertEqual(len(rows), 1)

    def test_compact_preserves_contents_and_rejects_bad_arguments(self):
        project = self.init()
        sessions = project / "sessions"
        expected = {}
        for name in ("20240101-a.md", "20240102-b.md", "20240103-c.md"):
            content = "# {}\ncanary=not-a-secret\n".format(name)
            (sessions / name).write_text(content)
            expected[name] = hashlib.sha256(content.encode()).hexdigest()
        compact = self.cli("compact", "--keep", "1")
        self.assertEqual(compact.returncode, 0, compact.stderr)
        self.assertEqual(len(list(sessions.glob("*.md"))), 1)
        archived = list((sessions / "archive").glob("*.md"))
        self.assertEqual(len(archived), 2)
        for path in list(sessions.glob("*.md")) + archived:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected[path.name])
        negative = self.cli("compact", "--keep", "-1")
        self.assertEqual(negative.returncode, 2)
        collision = sessions / "archive" / "20240103-c.md"
        collision.write_text("do not replace")
        (sessions / "20240100-d.md").write_text("new")
        before = (sessions / "20240100-d.md").read_bytes()
        blocked = self.cli("compact", "--keep", "0")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertEqual((sessions / "20240100-d.md").read_bytes(), before)

    def test_malformed_arguments_and_unregistered_commands_fail_cleanly(self):
        for args in [("prompt", "--tier", "9"), ("log", "-n", "nope"), ("lock",), ("nonsense",)]:
            result = self.cli(*args)
            self.assertEqual(result.returncode, 2, (args, result.stdout, result.stderr))
            self.assertNotIn("Traceback", result.stderr)
        doctor = self.cli("doctor")
        self.assertEqual(doctor.returncode, 0)
        self.assertIn("Diagnostic complete", doctor.stdout)


if __name__ == "__main__":
    unittest.main()
