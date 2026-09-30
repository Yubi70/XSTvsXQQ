import unittest

import pandas as pd

from src.refresh_price_history import merge_history


class TestMergeHistory(unittest.TestCase):
    def test_appends_new_dates_and_preserves_existing_values(self):
        existing = pd.DataFrame(
            {
                "Date": ["2026-09-30", "2026-09-29"],
                "Price": [63.0, 63.5],
                "Open": [63.0, 63.5],
                "High": [63.0, 63.5],
                "Low": [63.0, 63.5],
                "Vol.": [100, 200],
                "Change %": [None, None],
            }
        )
        refreshed = pd.DataFrame(
            {
                "Date": ["2026-10-01", "2026-09-30"],
                "Price": [64.0, 63.7],
                "Open": [64.0, 63.7],
                "High": [64.0, 63.7],
                "Low": [64.0, 63.7],
                "Vol.": [300, 400],
                "Change %": [None, None],
            }
        )

        result = merge_history(existing, refreshed)

        self.assertEqual(result["Date"].tolist(), ["2026-10-01", "2026-09-30", "2026-09-29"])
        self.assertEqual(result.loc[result["Date"] == "2026-09-30", "Price"].iloc[0], 63.0)

    def test_rejects_older_yahoo_history(self):
        existing = pd.DataFrame({"Date": ["2026-09-30"], "Price": [63.0]})
        refreshed = pd.DataFrame({"Date": ["2026-09-29"], "Price": [63.5]})

        with self.assertRaises(ValueError):
            merge_history(existing, refreshed)


if __name__ == "__main__":
    unittest.main()