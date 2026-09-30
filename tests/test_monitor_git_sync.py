import unittest
import json
import os
import tempfile
from unittest.mock import patch

import pandas as pd

from src import monitor


class TestMonitorGitSync(unittest.TestCase):
    def test_actions_restores_holding_without_committing_cost_basis(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = os.path.join(directory, "position_state.json")
            holding_path = os.path.join(directory, "monitor_holding.json")
            with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}), \
                    patch.object(monitor, "STATE_PATH", state_path), \
                    patch.object(monitor, "HOLDING_PATH", holding_path), \
                    patch.object(monitor, "ENV_COST_XST", 62.15):
                monitor.save_state({"holding": "XST", "cost_basis": {"XST": 62.15, "XQQ": 74.18}})
                with open(holding_path, encoding="utf-8") as f:
                    self.assertEqual(json.load(f), {"holding": "XST"})

                os.remove(state_path)
                restored = monitor.load_state()
                self.assertEqual(restored["holding"], "XST")
                self.assertEqual(restored["cost_basis"]["XST"], 62.15)
                with open(holding_path, encoding="utf-8") as f:
                    self.assertEqual(json.load(f), {"holding": "XST"})

    @patch("src.monitor.subprocess.run")
    def test_get_changed_sync_paths_includes_state_and_log(self, mock_run):
        mock_run.return_value.stdout = (
            " M src/monitor_log.csv\n"
            "M  src/position_state.json\n"
            "?? src/monitor_git_sync.log\n"
        )

        changed = monitor.get_changed_sync_paths()

        self.assertEqual(
            set(changed),
            {"src/monitor_log.csv", "src/position_state.json"},
        )

    @patch("src.monitor.yf.download")
    def test_fetch_prices_retries_when_one_ticker_is_missing(self, mock_download):
        first_response = pd.DataFrame(
            {
                ("Close", "XST.TO"): [None],
                ("Close", "XQQ.TO"): [73.4],
            },
            index=[pd.Timestamp("2026-09-24 09:32:00-04:00")],
        )
        second_response = pd.DataFrame(
            {
                ("Close", "XST.TO"): [63.45],
                ("Close", "XQQ.TO"): [None],
            },
            index=[pd.Timestamp("2026-09-24 09:32:00-04:00")],
        )
        mock_download.side_effect = [first_response, second_response]

        prices = monitor.fetch_prices()

        self.assertEqual(prices["XQQ.TO"], 73.4)
        self.assertEqual(prices["XST.TO"], 63.45)
        self.assertEqual(mock_download.call_count, 2)


if __name__ == "__main__":
    unittest.main()
