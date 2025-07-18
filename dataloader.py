# dataloader.py

import pandas as pd
from dotenv import load_dotenv
import os

# Module-level cache
_cached_data = None

load_dotenv()

s3_csv_url = os.environ.get("S3_CSV_URL")
if not s3_csv_url:
    raise RuntimeError("S3_CSV_URL is not set in the environment.")

def load_data():
    """
    Load data from a CSV file, cache the result, and return the selected columns.

    Parameters:
    - cols (list of str): List of tickers to filter the DataFrame. If None, returns all.

    Returns:
    - pd.DataFrame: Pivoted DataFrame with Date as index and Ticker columns.
    """
    global _cached_data

    if _cached_data is None:

        # if possible load from local file, otherwise load from S3
        if os.path.exists('data\sp500.csv'):
            df = pd.read_csv('data\sp500.csv', parse_dates=['Date'])
        else:
            df = pd.read_csv(s3_csv_url, parse_dates=['Date'])
        
        # process dataset to usable form
        df = df.pivot_table(index='Date', columns='Ticker', values='Price Close')
        df.ffill() 

        # save in cache
        _cached_data = df
    else:
        df = _cached_data

    return df
