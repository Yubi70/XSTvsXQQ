import unittest

from src.switch_comparison import compare_since_first_switch


HISTORY = [
    {
        "switched_at": "2026-04-24", "sold_ticker": "XQQ",
        "sold_quantity": 6650, "sold_price": 439806 / 6650,
        "bought_ticker": "XST", "bought_quantity": 7000, "bought_price": 62.86,
    },
    {
        "switched_at": "2026-11-05 11:30:00", "sold_ticker": "XST",
        "sold_quantity": 7000, "sold_price": 69.23,
        "bought_ticker": "XQQ", "bought_quantity": 7400, "bought_price": 65.53,
    },
]


class TestSwitchComparison(unittest.TestCase):
    def test_initial_prices_match_each_strategy_at_the_first_switch(self):
        rows = compare_since_first_switch(HISTORY[::-1], {"XST": 70, "XQQ": 66})
        xqq_entry = 439806 / 6650
        expected = [(None, 62.86), (xqq_entry, None), (None, 62.86), (xqq_entry, 62.86)]
        for row, (xqq, xst) in zip(rows, expected):
            self.assertEqual(row["Initial XQQ price (CAD)"], xqq)
            self.assertEqual(row["Initial XST price (CAD)"], xst)

    def test_exact_equal_capital_results_and_cash_neutrality(self):
        prices = {"XST": 70, "XQQ": 66}
        rows = compare_since_first_switch(HISTORY[::-1], prices)
        switched = 439806 * (69.23 / 62.86) * (66 / 65.53)
        xqq = 6650 * 66
        xst = 439806 / 62.86 * 70
        for row, expected in zip(rows, (switched, xqq, xst, (xqq + xst) / 2)):
            self.assertEqual(row["Starting capital (CAD)"], 439806)
            self.assertAlmostEqual(row["Current value (CAD)"], expected)
            self.assertAlmostEqual(row["Gain / loss (CAD)"], expected - 439806)
            self.assertAlmostEqual(row["Return (%)"], (expected / 439806 - 1) * 100)
            self.assertAlmostEqual(row["Switching advantage (CAD)"], switched - expected)
        changed = [{**trade, "bought_quantity": 1000000} for trade in HISTORY]
        self.assertEqual(compare_since_first_switch(changed, prices), rows)

    def test_one_switch_starts_with_equal_capital(self):
        first = HISTORY[0]
        rows = compare_since_first_switch([first], {"XST": 62.86, "XQQ": first["sold_price"]})
        for row in rows:
            self.assertAlmostEqual(row["Current value (CAD)"], 439806)
            self.assertAlmostEqual(row["Return (%)"], 0)

    def test_missing_and_discontinuous_history_and_bad_quotes_are_explicit(self):
        bad_histories = [
            [], [{**HISTORY[0], "sold_quantity": None}],
            [HISTORY[0], {**HISTORY[1], "sold_ticker": "XQQ"}],
        ]
        for history in bad_histories:
            with self.subTest(history=history), self.assertRaises(ValueError):
                compare_since_first_switch(history, {"XST": 70, "XQQ": 66})
        for price in (0, -1, float("nan")):
            with self.subTest(price=price), self.assertRaises(ValueError):
                compare_since_first_switch(HISTORY, {"XST": price, "XQQ": 66})
