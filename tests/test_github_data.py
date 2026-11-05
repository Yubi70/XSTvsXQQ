import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from src import github_data


class TestGitHubData(unittest.TestCase):
    @patch("src.github_data.urlopen")
    def test_reads_main_with_timeout_and_decodes_bom(self, open_url):
        response = open_url.return_value.__enter__.return_value
        response.read.return_value = b"\xef\xbb\xbfTimestamp,Price_XST\n"
        self.assertEqual(github_data.read_text(github_data.LOG_PATH), "Timestamp,Price_XST\n")
        request = open_url.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://raw.githubusercontent.com/Yubi70/XSTvsXQQ/main/src/monitor_log.csv",
        )
        self.assertEqual(open_url.call_args.kwargs["timeout"], 20)

    @patch("src.github_data.urlopen")
    def test_remote_failures_are_explicit(self, open_url):
        for error in (
            HTTPError("https://example.test", 404, "Not found", None, None),
            URLError("network unavailable"),
            TimeoutError("timeout"),
        ):
            with self.subTest(error=error):
                open_url.side_effect = error
                with self.assertRaises(github_data.RemoteDataError):
                    github_data.read_text(github_data.LOG_PATH)

    @patch("src.github_data.read_text")
    def test_valid_state_and_metadata_are_preserved(self, read):
        state = {
            "holding": "XST",
            "cost_basis": {"XST": 62.86, "XQQ": None},
            "last_switch_date": "2026-04-24",
            "approx_amount_cad": 10000,
        }
        read.return_value = json.dumps(state)
        self.assertEqual(github_data.read_position_state(), state)
        read.assert_called_once_with(github_data.STATE_PATH)

    @patch("src.github_data.read_text")
    def test_invalid_state_does_not_fall_back_to_local_data(self, read):
        texts = [
            "{bad json",
            "[]",
            '{"holding": "OTHER", "cost_basis": {}}',
            '{"holding": "XST", "cost_basis": []}',
            '{"holding": "XST", "cost_basis": {"XST": 0}}',
            '{"holding": "XST", "cost_basis": {"XST": "invalid"}}',
            '{"holding": "XST", "cost_basis": {"XST": NaN}}',
            '{"holding": "XST", "cost_basis": {"XST": true}}',
            '{"holding": "XST", "cost_basis": {}, "approx_amount_cad": -1}',
            '{"holding": "XST", "cost_basis": {}, "last_switch_date": "bad date"}',
        ]
        for text in texts:
            with self.subTest(text=text):
                read.return_value = text
                with self.assertRaises(github_data.RemoteDataError):
                    github_data.read_position_state()

    def test_browser_editor_targets_online_main(self):
        self.assertEqual(
            github_data.STATE_EDIT_URL,
            "https://github.com/Yubi70/XSTvsXQQ/edit/main/src/position_state.json",
        )

    def test_switch_history_preserves_known_and_unknown_quantities(self):
        state = {
            "holding": "XQQ",
            "cost_basis": {"XST": 69.23, "XQQ": 65.53},
            "last_switch_at": "2026-11-05 11:30:00",
            "switch_history": [
                {
                    "switched_at": "2026-04-24",
                    "sold_ticker": "XQQ", "sold_price": 68.29,
                    "bought_ticker": "XST", "bought_price": 62.86,
                },
                {
                    "switched_at": "2026-11-05 11:30:00",
                    "sold_ticker": "XST", "sold_price": 69.23, "sold_quantity": 7000,
                    "bought_ticker": "XQQ", "bought_price": 65.53, "bought_quantity": 7400,
                },
            ],
        }
        self.assertEqual(github_data.validate_position_state(state), state)

    @patch("src.github_data.read_text")
    def test_invalid_history_displays_explicit_data_error(self, read):
        trade = {
            "switched_at": "2026-11-05 11:30:00",
            "sold_ticker": "XST", "sold_price": 69.23, "sold_quantity": 7000,
            "bought_ticker": "XQQ", "bought_price": 65.53, "bought_quantity": 7400,
        }
        histories = [None, {}, [None]]
        for field, value in (
            ("switched_at", None), ("switched_at", "invalid"),
            ("switched_at", "2026-11-05 11:30:00+00:00"),
            ("sold_ticker", "OTHER"), ("bought_ticker", "XST"),
            ("sold_price", None), ("bought_price", -1),
            ("sold_quantity", True), ("bought_quantity", float("nan")),
            ("sold_quantity", "7000"), ("bought_quantity", 0),
        ):
            histories.append([{**trade, field: value}])
        for history in histories:
            with self.subTest(history=history):
                read.return_value = json.dumps({
                    "holding": "XQQ", "cost_basis": {}, "switch_history": history,
                })
                with self.assertRaisesRegex(github_data.RemoteDataError, "switch_history"):
                    github_data.read_position_state()


if __name__ == "__main__":
    unittest.main()
