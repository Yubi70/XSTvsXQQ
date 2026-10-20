import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestMonitorWorkflow(unittest.TestCase):
    def test_persists_log_without_state(self):
        self.check_persistence(log_changed=True)

    def test_persists_log_and_new_ignored_state(self):
        self.check_persistence(log_changed=True, state_changed=True)

    def test_persists_new_ignored_state_without_log_change(self):
        self.check_persistence(state_changed=True)

    def test_persists_tracked_state_without_log_change(self):
        self.check_persistence(state_changed=True, state_tracked=True)

    def test_no_changes_does_not_create_commit(self):
        self.check_persistence()

    def check_persistence(
        self, log_changed=False, state_changed=False, state_tracked=False
    ):
        workflow = (ROOT / ".github/workflows/monitor.yml").read_text(encoding="utf-8")
        script = textwrap.dedent(
            workflow.split("      - name: Commit and push updated logs\n", 1)[1]
            .split("        run: |\n", 1)[1]
        )

        with tempfile.TemporaryDirectory() as directory:
            remote = Path(directory) / "remote.git"
            repo = Path(directory) / "repo"
            repo.mkdir()

            def git(*args):
                return subprocess.run(
                    ["git", *args],
                    cwd=repo,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()

            git("init", "--bare", str(remote))
            git("init", "--initial-branch=main", ".")
            git("config", "user.name", "Workflow Test")
            git("config", "user.email", "workflow-test@example.com")
            git("config", "commit.gpgsign", "false")
            (repo / ".gitignore").write_text(
                (ROOT / ".gitignore").read_text(encoding="utf-8"), encoding="utf-8"
            )
            (repo / "src").mkdir()
            log = repo / "src/monitor_log.csv"
            state = repo / "src/position_state.json"
            log.write_text("Timestamp,Price_XST,Price_XQQ\n", encoding="utf-8")
            git("add", ".")
            if state_tracked:
                state.write_text('{"holding": "XST"}\n', encoding="utf-8")
                git("add", "-f", "--", "src/position_state.json")
            git("commit", "-m", "Initial data")
            git("remote", "add", "origin", str(remote))
            git("push", "-u", "origin", "main")
            initial_commit = git("rev-parse", "HEAD")

            if log_changed:
                with log.open("a", encoding="utf-8") as output:
                    output.write("2026-10-20 14:15:33,68.26,71.79\n")
            if state_changed:
                state.write_text('{"holding": "XQQ"}\n', encoding="utf-8")
            (repo / "unrelated.txt").write_text("Do not commit\n", encoding="utf-8")

            result = subprocess.run(
                ["bash", "-e", "-c", script],
                cwd=repo,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            head = git("rev-parse", "HEAD")
            self.assertEqual(head, git("--git-dir", str(remote), "rev-parse", "main"))
            self.assertEqual(head != initial_commit, log_changed or state_changed)
            self.assertEqual(
                git("--git-dir", str(remote), "show", "main:src/monitor_log.csv"),
                log.read_text(encoding="utf-8").strip(),
            )
            if state_changed:
                self.assertEqual(
                    git("--git-dir", str(remote), "show", "main:src/position_state.json"),
                    state.read_text(encoding="utf-8").strip(),
                )
            self.assertEqual(git("status", "--porcelain"), "?? unrelated.txt")


if __name__ == "__main__":
    unittest.main()
