import unittest
from pathlib import Path


class TestStreamlitEntrypoint(unittest.TestCase):
    def test_streamlit_cloud_entrypoints_exist(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "app.py").exists(), "Expected Streamlit Cloud entrypoint app.py")
        self.assertTrue((root / "streamlit_app.py").exists(), "Expected Streamlit entrypoint streamlit_app.py")


if __name__ == "__main__":
    unittest.main()
