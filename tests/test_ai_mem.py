import contextlib
import io
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "bin" / "ai-mem"
ai_mem = SourceFileLoader("ai_mem", str(SCRIPT)).load_module()


class AiMemTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.old_workspace = ai_mem.WORKSPACE
        ai_mem.WORKSPACE = self.workspace
        ai_mem.get_git_info = lambda cwd=None: (self.repo, "abc123", "main")

    def tearDown(self):
        ai_mem.WORKSPACE = self.old_workspace
        self.tempdir.cleanup()

    def register(self, rows):
        (self.workspace / "PROJECTS.md").write_text(
            "| Project | Repository path | Memory directory | State |\n"
            "|---|---|---|---|\n" + "".join(rows)
        )

    def test_resolve_project_prefers_longest_matching_path(self):
        nested = self.repo / "nested"
        nested.mkdir()
        self.register([
            "| Root | `{}` | `projects/root` | Active |\n".format(self.repo),
            "| Nested | `{}` | `projects/nested` | Active |\n".format(nested),
        ])
        self.assertEqual(ai_mem.resolve_project(nested / "src"), self.workspace / "projects/nested")

    def test_lock_writes_valid_table_and_unlock_is_exact(self):
        project = self.workspace / "projects" / "demo"
        project.mkdir(parents=True)
        current = project / "CURRENT.md"
        current.write_text(
            "# Current State\n\n## Active workstreams\n"
            "| Workstream | Session ID | Agent/model | Branch/worktree | Scope | Status |\n"
            "|---|---|---|---|---|---|\n"
            "| None | — | — | — | — | — |\n"
        )
        self.register(["| Demo | `{}` | `projects/demo` | Active |\n".format(self.repo)])

        with contextlib.redirect_stdout(io.StringIO()):
            ai_mem.cmd_lock("api", agent="agent")
        content = current.read_text()
        self.assertIn("| api | — | agent | main | active work | In-Progress |", content)
        self.assertNotIn("| None |", content)
        self.assertEqual(content.index("|---|"), content.index("| Workstream") + len("| Workstream | Session ID | Agent/model | Branch/worktree | Scope | Status |\n"))

        with contextlib.redirect_stdout(io.StringIO()):
            ai_mem.cmd_unlock("ap", owner="agent")
        self.assertIn("| api |", current.read_text())
        with contextlib.redirect_stdout(io.StringIO()):
            ai_mem.cmd_unlock("api", owner="agent")
        self.assertNotIn("| api |", current.read_text())

    def test_init_rejects_path_traversal_slug(self):
        with self.assertRaises(SystemExit) as error:
            ai_mem.cmd_init("../outside")
        self.assertEqual(error.exception.code, 2)
        self.assertFalse((self.root / "outside").exists())

    def test_integration_writer_never_overwrites_existing_file(self):
        target = self.root / "CLAUDE.md"
        target.write_text("user instructions\n")
        with contextlib.redirect_stdout(io.StringIO()):
            written = ai_mem.write_integration_file(target, "managed instructions\n")
        self.assertFalse(written)
        self.assertEqual(target.read_text(), "user instructions\n")


if __name__ == "__main__":
    unittest.main()
