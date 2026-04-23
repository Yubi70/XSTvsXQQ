import unittest
import pandas as pd
import os
from src.compare_prices import load_data, main

class TestComparePrices(unittest.TestCase):
    def setUp(self):
        self.xst_path = os.path.join(os.path.dirname(__file__), '../src/XST Historical Data (1).csv')
        self.xqq_path = os.path.join(os.path.dirname(__file__), '../src/XQQ Historical Data (1).csv')

    def test_load_data(self):
        df = load_data(self.xst_path)
        self.assertIn('Date', df.columns)
        self.assertIn('Price', df.columns)
        self.assertFalse(df.empty)

    def test_delta_calculation(self):
        xst = load_data(self.xst_path)
        xqq = load_data(self.xqq_path)
        merged = pd.merge(xst, xqq, on='Date', suffixes=('_XST', '_XQQ'))
        merged['Delta %'] = ((merged['Price_XST'] - merged['Price_XQQ']).abs() / merged['Price_XQQ']) * 100
        self.assertIn('Delta %', merged.columns)
        self.assertTrue((merged['Delta %'] >= 0).all())

    def test_signal_assignment(self):
        xst = load_data(self.xst_path)
        xqq = load_data(self.xqq_path)
        merged = pd.merge(xst, xqq, on='Date', suffixes=('_XST', '_XQQ'))
        merged['Delta %'] = ((merged['Price_XST'] - merged['Price_XQQ']).abs() / merged['Price_XQQ']) * 100
        threshold = merged['Delta %'].quantile(0.95)
        merged['Signal'] = merged['Delta %'].apply(lambda x: 'Sell High, Buy Low' if x >= threshold else '')
        self.assertIn('Signal', merged.columns)
        self.assertTrue(merged['Signal'].isin(['', 'Sell High, Buy Low']).all())

if __name__ == '__main__':
    unittest.main()
