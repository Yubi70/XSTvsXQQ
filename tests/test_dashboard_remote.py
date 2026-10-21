import json
import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from src import github_data


ROOT = Path(__file__).resolve().parents[1]
LOG = (
    "Timestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal\n"
    "2026-10-20 10:00:00 EDT,70.0,68.0,2.0,2.9,\n"
    "2026-10-20 10:30:00 EDT,72.0,68.0,4.0,5.7,\n"
)
STATE = {
    "holding": "XST",
    "cost_basis": {"XST": 62.86, "XQQ": 66.14},
    "last_switch_date": "2026-04-24",
    "approx_amount_cad": 10000,
}


class TestRemoteDashboard(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        self.responses = {
            github_data.LOG_PATH: LOG,
            github_data.STATE_PATH: json.dumps(STATE),
        }
        self.reader = patch("src.github_data.read_text", side_effect=self.responses.__getitem__)
        self.mock_read = self.reader.start()
        self.addCleanup(self.reader.stop)
        with patch.object(sys, "path", [str(ROOT / "src"), *sys.path]):
            direct_data = importlib.import_module("github_data")
        self.direct_reader = patch.object(
            direct_data, "read_text", side_effect=self.responses.__getitem__
        )
        self.direct_reader.start()
        self.addCleanup(self.direct_reader.stop)
        self.addCleanup(st.cache_data.clear)

    def test_all_cloud_entrypoints_rerender_and_offer_only_github_editing(self):
        before = (ROOT / github_data.STATE_PATH).read_bytes()
        for entrypoint in ("app.py", "streamlit_app.py", "src/dashboard.py"):
            with self.subTest(entrypoint=entrypoint):
                app = AppTest.from_file(str(ROOT / entrypoint)).run(timeout=30)
                self.assertFalse(app.exception)
                self.assertFalse(app.error)
                self.assertEqual(app.title[0].value, "XST vs XQQ Live Monitor")
                self.assertFalse(app.get("form"))
                links = app.get("link_button")
                self.assertTrue(any(link.proto.url == github_data.STATE_EDIT_URL for link in links))
                app.run(timeout=30)
                self.assertFalse(app.exception)
                self.assertEqual(app.title[0].value, "XST vs XQQ Live Monitor")
        self.assertEqual((ROOT / github_data.STATE_PATH).read_bytes(), before)
        self.mock_read.assert_any_call(github_data.LOG_PATH)
        self.mock_read.assert_any_call(github_data.STATE_PATH)

    def test_refresh_reloads_remote_state_and_log(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.mock_read.reset_mock()
        self.responses[github_data.LOG_PATH] = LOG.replace("72.0,68.0", "75.0,68.0")
        next(button for button in app.button if button.label == "Refresh from GitHub").click()
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.mock_read.assert_any_call(github_data.LOG_PATH)
        self.mock_read.assert_any_call(github_data.STATE_PATH)
        self.assertTrue(any("75.00" in str(metric.value) for metric in app.metric))

    def test_network_failure_displays_an_error_instead_of_stale_local_data(self):
        self.mock_read.side_effect = github_data.RemoteDataError("GitHub is unavailable")
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertIn("GitHub is unavailable", app.error[0].value)
        self.assertFalse(app.metric)

    def test_invalid_remote_state_displays_error_and_keeps_repair_link(self):
        self.responses[github_data.STATE_PATH] = "{invalid json"
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("not valid JSON" in error.value for error in app.error))
        self.assertTrue(app.get("link_button"))

    def test_invalid_remote_log_displays_error(self):
        self.responses[github_data.LOG_PATH] = "wrong,columns\n1,2\n"
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertIn("missing columns", app.error[0].value)

    def test_boundary_rows_and_live_signals_at_same_time_are_both_preserved(self):
        self.responses[github_data.LOG_PATH] = (
            "Timestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal,Observation\n"
            "2026-10-20 09:30:00 EDT,90.0,60.0,30.0,40.0,XST HIGH vs XQQ,LIVE\n"
            "2026-10-20 09:30:00 EDT,70.0,68.0,2.0,2.9,,OPEN\n"
            "2026-10-20 16:00:00 EDT,72.0,68.0,4.0,5.7,,CLOSE\n"
        )
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        recent = app.dataframe[0].value
        self.assertEqual(len(recent), 3)
        self.assertEqual(set(recent["Observation"]), {"LIVE", "OPEN", "CLOSE"})
        self.assertTrue(any("XST HIGH vs XQQ" == signal for signal in recent["Signal"].dropna()))


if __name__ == "__main__":
    unittest.main()
