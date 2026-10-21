import unittest
import io
import json
import smtplib
import tempfile
from contextlib import redirect_stderr
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src import monitor


class TestMonitor(unittest.TestCase):
    @patch("src.monitor.SMTP_SENDER", "sender@example.com")
    @patch("src.monitor.SMTP_PASSWORD", "test-password")
    @patch("src.monitor.ALERT_RECIPIENTS", ["recipient@example.com"])
    @patch("src.monitor.smtplib.SMTP_SSL")
    def test_email_completes_before_returning(self, mock_smtp):
        monitor.send_email("XST HIGH vs XQQ", 70.0, 60.0, 15.4)

        mock_smtp.assert_called_once_with("smtp.gmail.com", 465, timeout=30)
        server = mock_smtp.return_value.__enter__.return_value
        server.login.assert_called_once_with("sender@example.com", "test-password")
        server.sendmail.assert_called_once()
        mock_smtp.return_value.__exit__.assert_called_once()

    @patch.dict("src.monitor.os.environ", {"GITHUB_ACTIONS": ""})
    @patch("sys.argv", ["monitor.py", "--once"])
    @patch("src.monitor.run_check")
    def test_local_execution_is_rejected_before_collection(self, check):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            monitor.main()
        self.assertEqual(error.exception.code, 2)
        check.assert_not_called()

    @patch.dict("src.monitor.os.environ", {"GITHUB_ACTIONS": "true"})
    @patch("src.monitor.run_check")
    def test_actions_execution_runs_exactly_once(self, check):
        for arguments in (["monitor.py"], ["monitor.py", "--once"]):
            with self.subTest(arguments=arguments), patch("sys.argv", arguments):
                check.reset_mock()
                monitor.main()
                check.assert_called_once_with()

    def test_collection_window(self):
        cases = [
            ("2026-10-21 09:29", False),
            ("2026-10-21 09:30", True),
            ("2026-10-21 15:59", True),
            ("2026-10-21 16:00", False),
            ("2026-10-21 16:02", False),
            ("2026-10-24 10:00", False),
            ("2026-10-12 10:00", False),
            ("2025-12-24 12:59", True),
            ("2025-12-24 13:00", False),
        ]
        for timestamp, expected in cases:
            now = monitor.MARKET_TZ.localize(datetime.strptime(timestamp, "%Y-%m-%d %H:%M"))
            with self.subTest(timestamp=timestamp), patch("src.monitor.datetime") as clock:
                clock.now.return_value = now
                self.assertEqual(monitor.is_within_collection_window(), expected)

    def test_corrupt_state_is_not_overwritten(self):
        for text in (
            '{bad json',
            '[]',
            '{"holding": "INVALID", "cost_basis": {}}',
            '{"holding": "XST", "cost_basis": {"XST": -1}}',
            '{"holding": "XST", "cost_basis": {"XST": NaN}}',
        ):
            with tempfile.TemporaryDirectory() as directory:
                state_path = Path(directory) / "position_state.json"
                state_path.write_text(text, encoding="utf-8")
                with patch("src.monitor.STATE_PATH", str(state_path)):
                    with self.assertRaises(ValueError):
                        monitor.load_state()
                self.assertEqual(state_path.read_text(encoding="utf-8"), text)

    @patch("src.monitor.is_within_collection_window", return_value=False)
    @patch("src.monitor.fetch_prices")
    @patch("src.monitor.write_log")
    def test_closed_market_does_not_fetch_or_write(self, write, fetch, window):
        monitor.run_check()
        fetch.assert_not_called()
        write.assert_not_called()

    @patch("src.monitor.is_within_collection_window", return_value=True)
    @patch("src.monitor.fetch_prices", return_value={"XST.TO": 80.0, "XQQ.TO": 60.0})
    @patch("src.monitor.send_email")
    def test_switch_preserves_browser_edited_metadata(self, email, prices, window):
        state = {
            "holding": "XST",
            "cost_basis": {"XST": 62.86, "XQQ": 66.14},
            "last_switch_date": "2026-04-24",
            "approx_amount_cad": 10000.0,
        }
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "position_state.json"
            log_path = Path(directory) / "monitor_log.csv"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            with patch("src.monitor.STATE_PATH", str(state_path)), patch(
                "src.monitor.LOG_PATH", str(log_path)
            ):
                monitor.run_check()
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["holding"], "XQQ")
            self.assertEqual(saved["cost_basis"], {"XST": 62.86, "XQQ": 60.0})
            self.assertEqual(saved["last_switch_date"], state["last_switch_date"])
            self.assertEqual(saved["approx_amount_cad"], state["approx_amount_cad"])
            self.assertEqual(len(log_path.read_text().splitlines()), 2)
            email.assert_called_once()

    @patch("src.monitor.SMTP_SENDER", "sender@example.com")
    @patch("src.monitor.SMTP_PASSWORD", "test-password")
    @patch("src.monitor.ALERT_RECIPIENTS", ["recipient@example.com"])
    @patch("src.monitor.smtplib.SMTP_SSL", side_effect=smtplib.SMTPException("mail unavailable"))
    def test_email_failure_is_visible_to_actions(self, smtp):
        with self.assertRaises(smtplib.SMTPException):
            monitor.send_email("XST HIGH vs XQQ", 70.0, 60.0, 15.4)

    @patch("src.monitor.is_within_collection_window", return_value=True)
    @patch("src.monitor.fetch_prices", return_value={"XST.TO": 80.0, "XQQ.TO": 60.0})
    @patch("src.monitor.send_email", side_effect=smtplib.SMTPException("mail unavailable"))
    @patch("src.monitor.load_state", return_value={"holding": "XST", "cost_basis": {}})
    @patch("src.monitor.write_log")
    @patch("src.monitor.save_state")
    def test_failed_alert_does_not_flip_position(self, save, write, load, email, prices, window):
        with self.assertRaises(smtplib.SMTPException):
            monitor.run_check()
        save.assert_not_called()
        self.assertEqual(load.return_value["holding"], "XST")

    def test_alert_direction_and_thresholds_are_unchanged(self):
        for holding, prices, expected in (
            ("XST", {"XST.TO": 80.0, "XQQ.TO": 60.0}, "XST HIGH vs XQQ"),
            ("XQQ", {"XST.TO": 80.0, "XQQ.TO": 60.0}, ""),
            ("XQQ", {"XST.TO": 60.0, "XQQ.TO": 80.0}, "XQQ HIGH vs XST"),
            ("XST", {"XST.TO": 60.0, "XQQ.TO": 80.0}, ""),
            ("XST", {"XST.TO": 70.0, "XQQ.TO": 70.0}, ""),
        ):
            with self.subTest(holding=holding, prices=prices):
                result = monitor.compute_delta(prices)
                self.assertEqual(monitor.filter_actionable_signal(result["Signal"], holding), expected)

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
