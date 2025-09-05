import requests
import pandas as pd
from io import StringIO
import yfinance as yf
import os
from datetime import datetime, timedelta
import json # Import json module
from src.config import get_alpha_vantage_api_key

CACHE_DIR = 'cache'

def get_daily_data(symbol: str, api_key: str) -> pd.DataFrame:
    """
    Fetches daily time series data for a given stock symbol, trying Alpha Vantage first,
    then falling back to yfinance if Alpha Vantage fails. Uses a local cache.

    Args:
        symbol: The stock symbol (e.g., 'AAPL').
        api_key: Your Alpha Vantage API key.

    Returns:
        A pandas DataFrame with the daily time series data.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_file = os.path.join(CACHE_DIR, f'{symbol}.csv')

    # Try loading from cache first
    if os.path.exists(cache_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_mod_time < timedelta(hours=24):
            print(f"Loading data for {symbol} from cache.")
            try:
                df = pd.read_csv(cache_file, index_col='timestamp', parse_dates=True)
                # Basic validation: check if 'close' column exists
                if 'close' in df.columns:
                    return df
                else:
                    print(f"Cached data for {symbol} is invalid (missing 'close' column). Re-fetching.")
            except Exception as e:
                print(f"Error reading from cache for {symbol}: {e}. Re-fetching data.")
                # If cache read fails, proceed to fetch new data

    df = pd.DataFrame() # Initialize empty DataFrame

    # Try Alpha Vantage
    try:
        print(f"Fetching data for {symbol} from Alpha Vantage API.")
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&datatype=csv'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Check for Alpha Vantage API error messages in the response text
        # This is crucial to prevent parsing JSON errors as CSV
        if response.text.startswith('{') and response.text.endswith('}'):
            try:
                json_data = json.loads(response.text)
                if "Error Message" in json_data or "Information" in json_data:
                    raise ValueError(f"Alpha Vantage API error: {json_data}")
                # If it's JSON but not a known error, it might be valid data in JSON format
                # For TIME_SERIES_DAILY, we expect CSV, so treat unexpected JSON as error
                raise ValueError(f"Alpha Vantage returned unexpected JSON: {json_data}")
            except json.JSONDecodeError:
                # Not valid JSON, proceed as CSV
                pass

        csv_file = StringIO(response.text)
        df = pd.read_csv(csv_file)
        
        # Alpha Vantage specific column renaming
        column_mapping = {
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume',
            'timestamp': 'timestamp'
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        print(f"Successfully fetched data for {symbol} from Alpha Vantage.")

    except Exception as e:
        print(f"Alpha Vantage failed for {symbol}: {e}. Falling back to yfinance...")

    # Fallback to yfinance if Alpha Vantage failed or returned empty data
    if df.empty:
        try:
            print(f"Attempting to fetch data for {symbol} from yfinance...")
            df = yf.download(symbol, period="1y") # Download 1 year of data
            if df.empty:
                raise ValueError("yfinance returned empty data.")

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns.values] # Take only the first element of the tuple

            # Rename columns to match expected format (lowercase)
            df.columns = [col.lower() for col in df.columns]
            df = df.rename(columns={'adj close': 'close'}) # Adjust 'adj close' to 'close'
            
            # Ensure 'timestamp' is the index
            df.index.name = 'timestamp'
            df.index = pd.to_datetime(df.index)

            print(f"Successfully fetched data for {symbol} from yfinance.")

        except Exception as e:
            print(f"yfinance failed for {symbol}: {e}.")
            df = pd.DataFrame() # Ensure df is empty on failure

    # Save to cache if data was successfully fetched from either source and is valid
    if not df.empty and 'close' in df.columns:
        with open(cache_file, 'w') as f:
            df.to_csv(f, index=True) # Save the processed DataFrame to CSV, with index

    return df

if __name__ == '__main__':
    api_key = get_alpha_vantage_api_key()
    symbol = 'MSFT'
    
    if not api_key:
        print("Alpha Vantage API key not found. Please create a .ALPHA_VANTAGE_KEY.txt file or set the ALPHA_VANTAGE_API_KEY environment variable.")
    
    daily_data = get_daily_data(symbol, api_key)
    if not daily_data.empty:
        print(f"Successfully fetched data for {symbol}")
        print(daily_data.head())
    else:
        print(f"Failed to fetch data for {symbol} from both sources.")