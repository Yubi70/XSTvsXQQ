import csv
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from src import monitor


def toronto_time(text):
    return monitor.MARKET_TZ.localize(datetime.fromisoformat(text))


class TestSessionBoundaries(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.log = Path(directory.name) / "monitor_log.csv"
        self.clients = {ticker: Mock() for ticker in monitor.TICKERS}
        for patcher in (
            patch("src.monitor.LOG_PATH", str(self.log)),
            patch("src.monitor.SESSION_LOOKBACK_DAYS", 0),
            patch("src.monitor.yf.Ticker", side_effect=self.clients.__getitem__),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.set_daily("2026-10-20")

    def set_daily(self, day, utc_index=False):
        index = pd.DatetimeIndex([pd.Timestamp(day, tz="America/Toronto")])
        if utc_index:
            index = index.tz_convert("UTC")
        for ticker, opening, closing in (("XST.TO", 70.1234, 75.5678), ("XQQ.TO", 80.12, 85.56)):
            self.clients[ticker].history.return_value = pd.DataFrame(
                {"Open": [opening], "Close": [closing]}, index=index
            )

    def rows(self):
        with self.log.open(newline="", encoding="utf-8-sig") as source:
            return list(csv.DictReader(source))

    def test_delayed_run_records_actual_daily_open_and_close_not_current_quote(self):
        with patch("src.monitor.fetch_prices") as live, patch(
            "src.monitor.send_email"
        ) as email, patch("src.monitor.load_state") as load, patch("src.monitor.save_state") as save:
            monitor.record_session_boundaries(toronto_time("2026-10-20 17:10"))
        rows = self.rows()
        self.assertEqual([row["Timestamp"] for row in rows], [
            "2026-10-20 09:30:00 EDT", "2026-10-20 16:00:00 EDT",
        ])
        self.assertEqual([row["Observation"] for row in rows], ["OPEN", "CLOSE"])
        self.assertEqual([float(row["Price_XST"]) for row in rows], [70.1234, 75.5678])
        self.assertEqual([float(row["Price_XQQ"]) for row in rows], [80.12, 85.56])
        self.assertTrue(all(row["Signal"] == "" for row in rows))
        for mocked in (live, email, load, save):
            mocked.assert_not_called()
        for client in self.clients.values():
            client.history.assert_called_once_with(
                start="2026-10-20", end="2026-10-21", interval="1d",
                auto_adjust=False, actions=False, timeout=30, raise_errors=True,
            )

    def test_open_and_close_are_never_recorded_before_available(self):
        for clock, expected in (("09:29", []), ("10:10", ["OPEN"]), ("16:14", ["OPEN"]), ("16:15", ["OPEN", "CLOSE"])):
            with self.subTest(clock=clock):
                if self.log.exists():
                    self.log.unlink()
                monitor.record_session_boundaries(toronto_time("2026-10-20 " + clock))
                self.assertEqual(
                    [row["Observation"] for row in self.rows()] if self.log.exists() else [],
                    expected,
                )

    def test_missing_boundaries_are_recovered_the_next_morning(self):
        with patch("src.monitor.SESSION_LOOKBACK_DAYS", 1):
            monitor.record_session_boundaries(toronto_time("2026-10-21 08:00"))
        self.assertEqual([row["Timestamp"] for row in self.rows()], [
            "2026-10-20 09:30:00 EDT", "2026-10-20 16:00:00 EDT",
        ])

    def test_holidays_and_weekends_have_no_invented_observations(self):
        for day in ("2026-10-12", "2026-10-24", "2025-12-25"):
            with self.subTest(day=day):
                monitor.record_session_boundaries(toronto_time(day + " 17:00"))
                self.assertFalse(self.log.exists())
        for client in self.clients.values():
            client.history.assert_not_called()

    def test_early_close_uses_actual_exchange_close(self):
        self.set_daily("2025-12-24")
        monitor.record_session_boundaries(toronto_time("2025-12-24 13:15"))
        self.assertEqual([row["Timestamp"] for row in self.rows()], [
            "2025-12-24 09:30:00 EST", "2025-12-24 13:00:00 EST",
        ])

    def test_session_labels_follow_toronto_time_across_dst_and_utc_data(self):
        for day, timezone in (("2026-07-14", "EDT"), ("2026-12-15", "EST")):
            with self.subTest(day=day):
                if self.log.exists():
                    self.log.unlink()
                self.set_daily(day, utc_index=True)
                monitor.record_session_boundaries(toronto_time(day + " 16:30"))
                self.assertEqual([row["Timestamp"] for row in self.rows()], [
                    f"{day} 09:30:00 {timezone}", f"{day} 16:00:00 {timezone}",
                ])

    def test_partial_yahoo_data_is_reported_and_repaired_on_retry(self):
        self.clients["XQQ.TO"].history.return_value.loc[:, "Close"] = float("nan")
        with self.assertRaisesRegex(ValueError, "XQQ.TO 2026-10-20 CLOSE"):
            monitor.record_session_boundaries(toronto_time("2026-10-20 17:00"))
        self.assertEqual([row["Observation"] for row in self.rows()], ["OPEN"])
        self.set_daily("2026-10-20")
        monitor.record_session_boundaries(toronto_time("2026-10-20 17:00"))
        self.assertEqual([row["Observation"] for row in self.rows()], ["OPEN", "CLOSE"])

    def test_empty_or_invalid_yahoo_response_never_fabricates_prices(self):
        for response in (pd.DataFrame(), pd.DataFrame({"Close": [70.0]})):
            with self.subTest(response=response):
                self.clients["XST.TO"].history.return_value = response
                with self.assertRaisesRegex(ValueError, "no daily Open/Close"):
                    monitor.record_session_boundaries(toronto_time("2026-10-20 17:00"))
                self.assertFalse(self.log.exists())

    def test_idempotent_recovery_preserves_live_rows_and_alerts_at_same_timestamp(self):
        legacy = (
            "\ufeffTimestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal\n"
            "2026-10-20 09:30:00 EDT,90.0,60.0,30.0,40.0,XST HIGH vs XQQ\n"
            "2026-10-20 10:10:00 EDT,72.0,68.0,4.0,5.7,\n"
        )
        self.log.write_text(legacy, encoding="utf-8")
        now = toronto_time("2026-10-20 17:00")
        monitor.record_session_boundaries(now)
        first = self.log.read_bytes()
        monitor.record_session_boundaries(now)
        self.assertEqual(self.log.read_bytes(), first)
        rows = self.rows()
        self.assertEqual(len(rows), 4)
        live = [row for row in rows if row["Observation"] == "LIVE"]
        self.assertEqual(len(live), 2)
        self.assertEqual(live[0]["Signal"], "XST HIGH vs XQQ")
        self.assertEqual(live[0]["Price_XST"], "90.0")
        self.assertEqual(len([row for row in rows if row["Observation"] == "OPEN"]), 1)

    def test_later_provider_correction_updates_boundary_without_duplicate(self):
        monitor.record_session_boundaries(toronto_time("2026-10-20 17:00"))
        self.clients["XST.TO"].history.return_value.loc[:, "Close"] = 76.25
        monitor.record_session_boundaries(toronto_time("2026-10-20 18:15"))
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(float(rows[-1]["Price_XST"]), 76.25)

    def test_complete_boundaries_skip_yahoo_until_daily_correction_check(self):
        monitor.record_session_boundaries(toronto_time("2026-10-20 17:00"))
        for client in self.clients.values():
            client.history.assert_called_once()

        monitor.record_session_boundaries(toronto_time("2026-10-20 17:30"))
        for client in self.clients.values():
            client.history.assert_called_once()

        monitor.record_session_boundaries(toronto_time("2026-10-20 18:15"))
        for client in self.clients.values():
            self.assertEqual(client.history.call_count, 2)

    def test_live_append_upgrades_legacy_header_without_losing_data(self):
        self.log.write_text(
            "\ufeffTimestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal\n"
            "2026-10-19 10:10:00 EDT,70.0,68.0,2.0,2.9,\n", encoding="utf-8"
        )
        row = {
            "Timestamp": "2026-10-20 10:10:00 EDT",
            **monitor.compute_delta({"XST.TO": 72.0, "XQQ.TO": 68.0}),
        }
        monitor.write_log(row)
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(list(rows[0]), monitor.LOG_FIELDS)
        self.assertTrue(all(row["Observation"] == "LIVE" and None not in row for row in rows))

    def test_malformed_existing_log_is_not_overwritten(self):
        text = "Timestamp,Price_XST\ninvalid,1\n"
        self.log.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unrecognized monitor log"):
            monitor.record_session_boundaries(toronto_time("2026-10-20 17:00"))
        self.assertEqual(self.log.read_text(encoding="utf-8"), text)

    @patch.dict("src.monitor.os.environ", {"GITHUB_ACTIONS": "true"})
    @patch("sys.argv", ["monitor.py", "--session-boundaries"])
    @patch("src.monitor.record_session_boundaries")
    @patch("src.monitor.run_check")
    def test_cli_boundary_mode_never_runs_live_alert_logic(self, live, boundaries):
        monitor.main()
        boundaries.assert_called_once_with()
        live.assert_not_called()

    def test_naive_clock_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            monitor.record_session_boundaries(datetime(2026, 10, 20, 17))


if __name__ == "__main__":
    unittest.main()
