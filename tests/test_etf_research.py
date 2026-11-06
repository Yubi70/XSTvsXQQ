import hashlib
import json
import math
import shutil
import statistics
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src import etf_research as research
from src.research_dashboard import load_snapshot


ROOT = Path(__file__).resolve().parents[1]


def pair_frame(staples, nasdaq):
    return pd.DataFrame({
        "Date": pd.date_range("2026-10-01", periods=len(staples), freq="B"),
        "Close_staples": staples, "Close_nasdaq": nasdaq,
    })


def daily_frame():
    return pd.DataFrame({
        "Date": pd.date_range("2026-11-03", periods=3),
        "Open": [100, 103, 101], "High": [102, 106, 103], "Low": [99, 102, 99],
        "Close": [101, 105, 100], "Adj Close": [100, 104, 100],
        "Volume": [100, 200, 300], "Dividends": [0, 0, 1], "Stock Splits": [0, 2, 0],
    })


class TestResearchBacktest(unittest.TestCase):
    def test_signed_thresholds_and_no_redundant_switches(self):
        for threshold in (3, 5):
            frame = pair_frame([100, 100 + threshold, 120, 100 - threshold, 90], [100] * 5)
            curve, switches = research.backtest(frame, "S", "N", threshold)
            self.assertEqual(list(switches["From"]), ["S", "N"])
            self.assertEqual(list(switches["To"]), ["N", "S"])
            self.assertEqual(list(switches["Premium %"]), [threshold, -threshold])
            self.assertEqual(list(curve["Holding"]), ["S", "N", "N", "S", "S"])

    def test_same_close_does_not_apply_new_holding_retroactively(self):
        frame = pair_frame([100, 103, 110, 95, 100], [100, 100, 105, 100, 110])
        curve, switches = research.backtest(frame, "S", "N", 3)
        expected = [10000, 10300, 10815, 10300, 10300 * 100 / 95]
        for actual, value in zip(curve["Switching"], expected):
            self.assertAlmostEqual(actual, value)
        self.assertEqual(list(switches["Date"]), [frame["Date"][1], frame["Date"][3]])
        self.assertAlmostEqual(curve["50/50"].iloc[-1], 10500)

    def test_initial_close_switch_and_no_switch_cases(self):
        curve, switches = research.backtest(pair_frame([103, 120, 130], [100, 110, 120]), "S", "N", 3)
        self.assertEqual(len(switches), 1)
        self.assertEqual(curve["Switching"].iloc[0], 10000)
        self.assertAlmostEqual(curve["Switching"].iloc[-1], 12000)
        curve, switches = research.backtest(pair_frame([80, 81, 82], [100, 101, 102]), "S", "N", 3)
        self.assertTrue(switches.empty)
        self.assertEqual(list(switches.columns), research.SWITCH_COLUMNS)
        pd.testing.assert_series_equal(curve["Switching"], curve["Staples only"], check_names=False)

    def test_risk_metrics_and_invalid_inputs(self):
        dates = pd.Series(pd.date_range("2025-01-01", periods=3, freq="180D"))
        result = research.performance(pd.Series([10000, 8000, 12000]), dates)
        self.assertAlmostEqual(result["Return %"], 20)
        self.assertAlmostEqual(result["Max drawdown %"], -20)
        self.assertGreater(result["Annual volatility %"], 0)
        for threshold in (0, -3, float("nan")):
            with self.assertRaises(ValueError):
                research.backtest(pair_frame([100, 101], [100, 102]), "S", "N", threshold)
        with self.assertRaises(ValueError):
            research.backtest(pair_frame([100, 0], [100, 102]), "S", "N", 3)
        with self.assertRaises(ValueError):
            research.align_pair(
                pd.DataFrame({"Date": [1], "Close": [100]}),
                pd.DataFrame({"Date": [2], "Close": [100]}),
            )

    def test_download_validation_and_split_metadata(self):
        frame = daily_frame()
        start, cutoff = pd.Timestamp("2026-11-03"), pd.Timestamp("2026-11-05")
        for bad in (
            frame.iloc[0:0],
            pd.concat([frame, frame.iloc[:1]]),
            frame.assign(Close=[101, float("nan"), 100]),
            frame.assign(Volume=[100, -1, 200]),
            frame.assign(High=[90, 106, 103]),
            frame.assign(Date=pd.date_range("2026-11-04", periods=3)),
        ):
            with self.subTest(shape=bad.shape), self.assertRaises(ValueError):
                research.validate_history(bad, start, cutoff)
        metadata = research.quality_metadata("XLP", frame, start, cutoff)
        self.assertEqual(metadata["split_events"], [{"date": "2026-11-04", "ratio": 2}])
        self.assertEqual(metadata["missing_sessions"], [])
        self.assertEqual(metadata["mean_share_volume_30"], 200)
        with patch("src.etf_research.yf.Ticker") as ticker:
            provider = frame.set_index("Date")
            provider.index = provider.index.tz_localize("America/New_York")
            ticker.return_value.history.return_value = provider
            actual = research.download_history("XLP", start, cutoff)
            self.assertEqual(actual["Date"].iloc[-1], cutoff)
            self.assertFalse(ticker.return_value.history.call_args.kwargs["auto_adjust"])
            ticker.return_value.history.return_value = provider.iloc[:0]
            with self.assertRaises(ValueError):
                research.download_history("XLP", start, cutoff)

    def test_cutoff_excludes_unfinished_session(self):
        self.assertEqual(
            research.completed_cutoff(pd.Timestamp("2026-11-06 12:00", tz="UTC")),
            pd.Timestamp("2026-11-05"),
        )
        self.assertEqual(
            research.completed_cutoff(pd.Timestamp("2026-11-06 22:00", tz="UTC")),
            pd.Timestamp("2026-11-06"),
        )


class TestResearchArtifacts(unittest.TestCase):
    def test_real_snapshot_hashes_schemas_and_independent_share_ledger(self):
        manifest, texts, summary = load_snapshot(ROOT)
        self.assertEqual(set(manifest["funds"]), set(research.FUNDS))
        self.assertEqual(len(summary), 32)
        for ticker in research.FUNDS:
            history = pd.read_csv(ROOT / "src" / research.history_name(ticker))
            self.assertEqual(list(history.columns), research.HISTORY_COLUMNS)
            self.assertGreaterEqual(len(history), 1000)
            self.assertLessEqual(history["Date"].max(), manifest["cutoff"])
        for staples, nasdaq, _ in research.PAIRS:
            for years in (5, 2):
                for threshold in (3, 5):
                    key = f"{staples.replace('.', '_')}_{nasdaq.replace('.', '_')}_{years}y_{threshold}pct"
                    curve = pd.read_csv(ROOT / f"src/etf_research_{key}_curve.csv")
                    switches = pd.read_csv(ROOT / f"src/etf_research_{key}_switches.csv")
                    self.assertEqual(list(curve.columns), research.CURVE_COLUMNS)
                    self.assertEqual(list(switches.columns), research.SWITCH_COLUMNS)
                    # Independent share ledger: execute trades, not compounded-return helper.
                    held_staples = True
                    shares = 10000 / curve["Staples close"].iloc[0]
                    expected_dates = []
                    for row in curve.to_dict("records"):
                        current_price = row["Staples close"] if held_staples else row["Nasdaq close"]
                        self.assertAlmostEqual(shares * current_price, row["Switching"], places=6)
                        premium = (row["Staples close"] - row["Nasdaq close"]) / row["Nasdaq close"] * 100
                        change = (held_staples and premium >= threshold) or (not held_staples and premium <= -threshold)
                        if change:
                            next_price = row["Nasdaq close"] if held_staples else row["Staples close"]
                            shares = shares * current_price / next_price
                            held_staples = not held_staples
                            expected_dates.append(row["Date"])
                    self.assertEqual(expected_dates, list(switches["Date"]))
                    selected = summary[(summary["Pair"] == f"{staples}/{nasdaq}")
                                       & (summary["Years"] == years) & (summary["Threshold"] == threshold)]
                    elapsed_years = (pd.Timestamp(curve["Date"].iloc[-1]) - pd.Timestamp(curve["Date"].iloc[0])).days / 365.25
                    for record in selected.to_dict("records"):
                        values = curve[record["Strategy"]].tolist()
                        peak, drawdown = values[0], 0
                        for value in values:
                            peak = max(peak, value)
                            drawdown = min(drawdown, value / peak - 1)
                        returns = [right / left - 1 for left, right in zip(values, values[1:])]
                        self.assertAlmostEqual(record["Final value"], values[-1], places=6)
                        self.assertAlmostEqual(record["Return %"], (values[-1] / 10000 - 1) * 100)
                        self.assertAlmostEqual(record["CAGR %"], ((values[-1] / 10000) ** (1 / elapsed_years) - 1) * 100)
                        self.assertAlmostEqual(record["Max drawdown %"], drawdown * 100)
                        self.assertAlmostEqual(record["Annual volatility %"], statistics.stdev(returns) * math.sqrt(252) * 100)
                        self.assertAlmostEqual(
                            record["Excess vs 50/50 (pp)"],
                            (values[-1] - curve["50/50"].iloc[-1]) / 100,
                        )
                        self.assertEqual(record["Switches"], len(expected_dates) if record["Strategy"] == "Switching" else 0)
                    if staples == "XLP":
                        self.assertEqual(len(switches), 0)
        self.assertIn("no XLP/QQQ switches", texts["docs/etf_replacement_research.md"])

    def test_missing_and_inconsistent_snapshot_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "Cannot load"):
                load_snapshot(root)
            (root / "src").mkdir()
            manifest = json.loads((ROOT / "src/etf_research_manifest.json").read_text())
            (root / "src/etf_research_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                load_snapshot(root)

    def test_workflow_explicitly_persists_every_research_artifact(self):
        workflow = (ROOT / ".github/workflows/historical-data.yml").read_text()
        self.assertIn("python -m src.etf_research", workflow)
        manifest = json.loads((ROOT / "src/etf_research_manifest.json").read_text())
        for path in [*manifest["sha256"], "src/etf_research_manifest.json"]:
            self.assertIn(path, workflow)

    def test_corrupt_but_rehashed_artifacts_fail_before_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            manifest = json.loads((ROOT / "src/etf_research_manifest.json").read_text())
            for relative in manifest["sha256"]:
                shutil.copyfile(ROOT / relative, root / relative)
            for relative, replacement, message in (
                ("src/etf_research_summary.csv", "XLP/QQQ", "summary scenarios"),
                ("src/etf_research_XLP_QQQ_5y_3pct_curve.csv", "Date,Close\n", "curve schema"),
                ("docs/etf_replacement_research.md", "Missing assessment\n", "report sections"),
            ):
                original = (root / relative).read_text()
                text = original.replace("XLP/QQQ", "Wrong/Pair") if replacement == "XLP/QQQ" else replacement
                (root / relative).write_text(text)
                manifest["sha256"][relative] = hashlib.sha256(text.encode()).hexdigest()
                (root / "src/etf_research_manifest.json").write_text(json.dumps(manifest))
                with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, message):
                    load_snapshot(root)
                (root / relative).write_text(original)
                manifest["sha256"][relative] = hashlib.sha256(original.encode()).hexdigest()
            manifest["samples"][0]["pair"] = "Unknown"
            (root / "src/etf_research_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "sample metadata"):
                load_snapshot(root)

    def test_prepare_failure_cannot_publish_partial_batch(self):
        with patch("src.etf_research.download_history", side_effect=ValueError("provider unavailable")), patch(
            "src.etf_research.publish_outputs"
        ) as publish, patch("sys.argv", ["etf_research.py"]):
            with self.assertRaisesRegex(ValueError, "provider unavailable"):
                research.main()
            publish.assert_not_called()

    def test_publication_hashes_use_exact_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            outputs = {"src/example.csv": "Date,Close\n2026-11-05,100\n"}
            research.publish_outputs(outputs, root)
            data = (root / "src/example.csv").read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), hashlib.sha256(outputs["src/example.csv"].encode()).hexdigest())
