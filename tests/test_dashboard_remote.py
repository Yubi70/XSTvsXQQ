import json
import base64
import struct
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

    def test_live_delta_follows_current_holding_and_refreshes_orientation(self):
        self.responses[github_data.STATE_PATH] = json.dumps({**STATE, "holding": "XQQ"})
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        live = app.tabs[0]
        self.assertEqual(next(metric.value for metric in live.metric if metric.label == "Delta %"), "-5.70%")
        recent = live.dataframe[0].value
        self.assertEqual(recent.iloc[0]["Delta_%"], "-5.70%")
        self.assertEqual(recent.iloc[0]["Delta_$"], "$-4.00")
        chart = json.loads(live.get("plotly_chart")[0].proto.spec)
        y = chart["data"][0]["y"]
        if isinstance(y, dict):
            values = struct.unpack("<2d", base64.b64decode(y["bdata"]))
        else:
            values = tuple(y)
        self.assertEqual(values, (-2.9, -5.7))
        self.assertIn("XQQ - XST", chart["layout"]["yaxis"]["title"]["text"])
        self.assertEqual(
            [shape["y0"] for shape in chart["layout"]["shapes"]], [7, 0]
        )
        self.responses[github_data.STATE_PATH] = json.dumps(STATE)
        next(button for button in app.button if button.label == "Refresh from GitHub").click()
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(next(metric.value for metric in app.tabs[0].metric if metric.label == "Delta %"), "+5.70%")

    def test_live_signal_uses_current_holding_not_old_recorded_alert(self):
        self.responses[github_data.LOG_PATH] = (
            "Timestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal\n"
            "2026-10-20 10:30:00 EDT,60,80,-20,-28.6,XQQ HIGH vs XST\n"
        )
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.tabs[0].error)
        self.responses[github_data.STATE_PATH] = json.dumps({**STATE, "holding": "XQQ"})
        next(button for button in app.button if button.label == "Refresh from GitHub").click()
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("XQQ HIGH vs XST" in error.value for error in app.tabs[0].error))

    def test_xqq_daily_delta_tendency_is_inverted(self):
        self.responses[github_data.STATE_PATH] = json.dumps({**STATE, "holding": "XQQ"})
        self.responses[github_data.LOG_PATH] = (
            "Timestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal\n"
            "2026-10-19 16:00:00 EDT,70,68,2,2.9,\n"
            "2026-10-20 10:30:00 EDT,72,68,4,5.7,\n"
        )
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        tendency = next(item.value for item in app.tabs[0].markdown if "Day delta tendency" in item.value)
        self.assertIn("Down (-2.80 pts", tendency)

    def test_history_retains_old_switch_and_exact_trade_cash_difference(self):
        self.responses[github_data.STATE_PATH] = json.dumps({
            **STATE,
            "switch_history": [
                {
                    "switched_at": "2026-04-24",
                    "sold_ticker": "XQQ", "sold_price": 68.29,
                    "bought_ticker": "XST", "bought_price": 62.86,
                },
                {
                    "switched_at": "2026-11-05 11:30:00",
                    "sold_ticker": "XST", "sold_quantity": 7000, "sold_price": 69.23,
                    "bought_ticker": "XQQ", "bought_quantity": 7400, "bought_price": 65.53,
                },
            ],
        })
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        tab = next(tab for tab in app.tabs if tab.label == "Switch History")
        history = tab.dataframe[0].value
        self.assertEqual(len(history), 2)
        latest = history.iloc[0]
        self.assertEqual(latest["Switch time (Toronto)"], "2026-11-05 11:30:00")
        self.assertEqual(latest["Sold"], "XST")
        self.assertEqual(latest["Shares sold"], 7000)
        self.assertEqual(latest["Sale price (CAD)"], 69.23)
        self.assertEqual(latest["Sale proceeds (CAD)"], 484610)
        self.assertEqual(latest["Bought"], "XQQ")
        self.assertEqual(latest["Shares bought"], 7400)
        self.assertEqual(latest["Buy price (CAD)"], 65.53)
        self.assertEqual(latest["Purchase cost (CAD)"], 484922)
        self.assertEqual(latest["Cash added (CAD)"], 312)
        self.assertEqual(history.iloc[1]["Switch time (Toronto)"], "2026-04-24")
        self.assertTrue(history.iloc[1][["Shares sold", "Shares bought", "Cash added (CAD)"]].isna().all())

    def test_history_without_records_shows_empty_state(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        tab = next(tab for tab in app.tabs if tab.label == "Switch History")
        self.assertFalse(tab.dataframe)
        self.assertTrue(any("No switch history" in info.value for info in tab.info))

    def test_history_comparison_shows_four_equal_capital_strategies(self):
        from tests.test_switch_comparison import HISTORY
        self.responses[github_data.STATE_PATH] = json.dumps({
            **STATE, "switch_history": HISTORY,
        })
        self.responses[github_data.LOG_PATH] = (
            "Timestamp,Price_XST,Price_XQQ,Delta_$,Delta_%,Signal\n"
            "2026-11-05 11:35:00 EST,70,66,4,5.9,\n"
        )
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        tab = next(tab for tab in app.tabs if tab.label == "Switch History")
        self.assertFalse(tab.error)
        markup = next(item.value for item in tab.markdown if 'id="switch-comparison-table"' in item.value)
        for strategy in ("Your switches", "XQQ only", "XST only", "50% XQQ / 50% XST"):
            self.assertIn(f"<td>{strategy}</td>", markup)
        for column in ("Strategy", "Initial XQQ", "Initial XST", "Value", "Gain / loss", "Return", "Switch advantage"):
            self.assertIn(f"<th>{column}</th>", markup)
        self.assertIn(f"${10000 * 66 / HISTORY[0]['sold_price']:,.2f}", markup)
        self.assertIn("$+0.00 (+0.00%)", markup)
        self.assertNotIn("(CAD)", markup)
        self.assertIn("table-layout:fixed", markup)
        self.assertTrue(any("hypothetical 10,000 CAD" in caption.value for caption in tab.caption))

    def test_new_switch_waits_for_post_trade_quotes(self):
        self.responses[github_data.STATE_PATH] = json.dumps({
            **STATE,
            "holding": "XQQ",
            "cost_basis": {"XST": 69.23, "XQQ": 65.53},
            "last_switch_date": "2026-10-20",
            "last_switch_at": "2026-10-20 11:30:00",
            "approx_amount_cad": 484922,
        })
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertNotIn("Switched return", {metric.label for metric in app.metric})
        self.assertTrue(any("Waiting for price observations" in info.value for info in app.info))
        self.responses[github_data.LOG_PATH] += (
            "2026-10-20 11:35:00 EDT,69.23,65.53,3.7,5.49,\n"
        )
        next(button for button in app.button if button.label == "Refresh from GitHub").click()
        app.run(timeout=30)
        self.assertFalse(app.exception)
        metrics = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(metrics["Switched return"], "+0.00%")
        self.assertEqual(metrics["No-switch return"], "+0.00%")
        self.assertEqual(metrics["Switch edge ($)"], "$+0.00")
        comparison = next(
            chart for element in app.get("plotly_chart")
            if (chart := json.loads(element.proto.spec))["data"][0].get("name") == "Switched (XQQ)"
        )
        for trace in comparison["data"]:
            self.assertEqual(len(trace["x"]), 1)
            self.assertIn("11:35:00", trace["x"][0])

    def test_invalid_history_keeps_repair_link_in_history_tab(self):
        self.responses[github_data.STATE_PATH] = json.dumps({**STATE, "switch_history": {}})
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        tab = next(tab for tab in app.tabs if tab.label == "Switch History")
        self.assertTrue(any("switch_history" in error.value for error in tab.error))
        self.assertTrue(tab.get("link_button"))

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

    def test_xut_research_tab_shows_both_cad_pairs_and_selectors(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        tab = next(tab for tab in app.tabs if tab.label == "ETF Research")
        self.assertFalse(tab.error)
        markup = "\n".join(item.value for item in tab.markdown)
        self.assertIn("research-pilot-summary", markup)
        self.assertIn("research-reference-summary", markup)
        self.assertIn("XUT.TO/XQQ.TO", markup)
        self.assertIn("XUT only", markup)
        self.assertIn("XST only", markup)
        self.assertNotIn("USD", markup)
        self.assertNotIn("Staples only", markup)
        self.assertTrue(any("different share denominations" in item.value.lower() for item in tab.warning))
        app.selectbox(key="research_years").select(2)
        app.selectbox(key="research_threshold").select(5)
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(next(tab for tab in app.tabs if tab.label == "ETF Research").error)
        self.assertEqual(len(app.get("plotly_chart")), len({chart.proto.id for chart in app.get("plotly_chart")}))

    def test_missing_research_snapshot_does_not_break_other_tabs(self):
        with patch("src.research_dashboard.load_snapshot", side_effect=ValueError("Research snapshot missing")):
            app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        tab = next(tab for tab in app.tabs if tab.label == "ETF Research")
        self.assertEqual(tab.error[0].value, "Research snapshot missing")
        self.assertTrue(app.tabs[0].metric)

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
