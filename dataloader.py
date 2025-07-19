import pandas as pd
from dotenv import load_dotenv
import os

# Module-level cache for multiple datasets
_cached_data = {}

load_dotenv()

s3_url = os.environ.get("S3_URL")
if not s3_url:
    raise RuntimeError("S3_URL is not set in the environment.")

def load_data(name: str):
    """
    Load data from a CSV file, cache the result, and return the selected columns.

    Parameters:
    - name: str, 'sp500_close' or 'sp500_meta'

    Returns:
    - pd.DataFrame: Pivoted DataFrame with Date as index and Ticker columns.
    """
    assert name in ['sp500_close', 'sp500_meta'], "name should be in ['sp500_close', 'sp500_meta']"

    if name not in _cached_data:
        path = f'data/{name}.csv'
        # Read from disk
        if os.path.exists(path):
            df = pd.read_csv(path)
        # Read from S3
        else:
            df = pd.read_csv(os.path.join(s3_url, f'{name}.csv'))
            df.to_csv(path, index=False)

        # Preprocessing
        if name == 'sp500_close':
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.pivot_table(index='Date', columns='Ticker', values='Price Close')
        elif name == 'sp500_meta':
            df = df.set_index('Instrument').T
        
        _cached_data[name] = df

    return _cached_data[name]

