import unittest
from unittest.mock import patch

import pandas as pd

from src import monitor


class TestMonitorGitSync(unittest.TestCase):
    @patch.dict("src.monitor.os.environ", {"GITHUB_ACTIONS": "true"})
    @patch("src.monitor.SMTP_SENDER", "sender@example.com")
    @patch("src.monitor.SMTP_PASSWORD", "test-password")
    @patch("src.monitor.ALERT_RECIPIENTS", ["recipient@example.com"])
    @patch("src.monitor.threading.Thread")
    @patch("src.monitor.smtplib.SMTP_SSL")
    def test_cloud_email_completes_without_background_thread(self, mock_smtp, mock_thread):
        monitor.send_email("XST HIGH vs XQQ", 70.0, 60.0, 15.4)

        server = mock_smtp.return_value.__enter__.return_value
        server.login.assert_called_once_with("sender@example.com", "test-password")
        server.sendmail.assert_called_once()
        mock_smtp.return_value.__exit__.assert_called_once()
        mock_thread.assert_not_called()

    @patch.dict("src.monitor.os.environ", {"GITHUB_ACTIONS": ""})
    @patch("src.monitor.SMTP_SENDER", "sender@example.com")
    @patch("src.monitor.SMTP_PASSWORD", "test-password")
    @patch("src.monitor.ALERT_RECIPIENTS", ["recipient@example.com"])
    @patch("src.monitor.threading.Thread")
    @patch("src.monitor.smtplib.SMTP_SSL")
    def test_local_email_still_uses_background_thread(self, mock_smtp, mock_thread):
        monitor.send_email("XST HIGH vs XQQ", 70.0, 60.0, 15.4)

        mock_thread.return_value.start.assert_called_once()
        mock_smtp.assert_not_called()

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
