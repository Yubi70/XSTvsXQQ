import unittest
from pathlib import Path


class TestStreamlitEntrypoint(unittest.TestCase):
    def test_cloud_workflow_persists_prices_and_position_state(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/monitor.yml").read_text(encoding="utf-8")
        self.assertIn("git add -- src/monitor_log.csv", workflow)
        self.assertIn("git add -f -- src/position_state.json", workflow)
        self.assertIn("git diff --cached --quiet", workflow)
        self.assertIn("python -m src.monitor --once", workflow)

    def test_devcontainer_does_not_launch_local_dashboard(self):
        root = Path(__file__).resolve().parents[1]
        config = (root / ".devcontainer/devcontainer.json").read_text(encoding="utf-8")
        self.assertNotIn("postAttachCommand", config)
        self.assertNotIn("openPreview", config)

    def test_streamlit_cloud_entrypoints_exist(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "app.py").exists(), "Expected Streamlit Cloud entrypoint app.py")
        self.assertTrue((root / "streamlit_app.py").exists(), "Expected Streamlit entrypoint streamlit_app.py")


if __name__ == "__main__":
    unittest.main()
