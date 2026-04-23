import pandas as pd
import os

# File paths
xst_path = os.path.join(os.path.dirname(__file__), 'XST Historical Data (1).csv')
xqq_path = os.path.join(os.path.dirname(__file__), 'XQQ Historical Data (1).csv')
output_path = os.path.join(os.path.dirname(__file__), 'delta_signals.csv')

def load_data(path):
    df = pd.read_csv(path)
    df = df[['Date', 'Price']].copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    return df

def main():
    xst = load_data(xst_path)
    xqq = load_data(xqq_path)
    # Merge on Date
    merged = pd.merge(xst, xqq, on='Date', suffixes=('_XST', '_XQQ'))
    # Calculate absolute percentage delta
    merged['Delta %'] = ((merged['Price_XST'] - merged['Price_XQQ']).abs() / merged['Price_XQQ']) * 100
    # Determine 95th percentile threshold
    threshold = merged['Delta %'].quantile(0.95)
    merged['Signal'] = merged['Delta %'].apply(lambda x: 'Sell High, Buy Low' if x >= threshold else '')
    # Output
    merged[['Date', 'Price_XST', 'Price_XQQ', 'Delta %', 'Signal']].to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    print(merged[['Date', 'Price_XST', 'Price_XQQ', 'Delta %', 'Signal']].head())

if __name__ == '__main__':
    main()
