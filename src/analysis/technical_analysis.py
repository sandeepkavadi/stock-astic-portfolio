import pandas as pd

def calculate_sma(data: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculates the Simple Moving Average (SMA).

    The SMA is a calculation that takes the arithmetic mean of a given set of prices
    over a specific number of days in the past.

    Formula:
        SMA = (Sum of price, for n periods) / n

    Args:
        data: A pandas DataFrame with a 'close' column.
        window: The moving average window size.

    Returns:
        A new DataFrame with the SMA values.
    """
    data[f'sma_{window}'] = data['close'].rolling(window=window).mean()
    return data

def calculate_ema(data: pd.DataFrame, window: int) -> pd.DataFrame:
    """
    Calculates the Exponential Moving Average (EMA).

    The EMA is a type of moving average that places a greater weight and
    significance on the most recent data points.

    Formula:
        EMA = (Close - EMA_previous_day) * multiplier + EMA_previous_day
        where multiplier = 2 / (window + 1)

    Args:
        data: A pandas DataFrame with a 'close' column.
        window: The moving average window size.

    Returns:
        A new DataFrame with the EMA values.
    """
    data[f'ema_{window}'] = data['close'].ewm(span=window, adjust=False).mean()
    return data

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Calculates the Relative Strength Index (RSI).

    The RSI is a momentum indicator that measures the magnitude of recent price
    changes to evaluate overbought or oversold conditions.

    Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss

    Args:
        data: A pandas DataFrame with a 'close' column.
        window: The RSI window size.

    Returns:
        A new DataFrame with the RSI values.
    """
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    return data

def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """
    Calculates the Moving Average Convergence Divergence (MACD).

    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of a security’s price.

    Formula:
        MACD = 12-Period EMA - 26-Period EMA

    Args:
        data: A pandas DataFrame with a 'close' column.
        fast_period: The fast EMA period.
        slow_period: The slow EMA period.
        signal_period: The signal line EMA period.

    Returns:
        A new DataFrame with MACD, signal line, and histogram values.
    """
    data['macd_fast'] = data['close'].ewm(span=fast_period, adjust=False).mean()
    data['macd_slow'] = data['close'].ewm(span=slow_period, adjust=False).mean()
    data['macd'] = data['macd_fast'] - data['macd_slow']
    data['macd_signal'] = data['macd'].ewm(span=signal_period, adjust=False).mean()
    data['macd_histogram'] = data['macd'] - data['macd_signal']
    return data

def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std_dev: int = 2) -> pd.DataFrame:
    """
    Calculates Bollinger Bands.

    Bollinger Bands are a technical analysis tool defined by a set of lines
    plotted two standard deviations (positive and negative) away from a simple
    moving average of the security's price.

    Formula:
        Middle Band = n-period Simple Moving Average (SMA)
        Upper Band = Middle Band + (n-period Standard Deviation of Price x k)
        Lower Band = Middle Band - (n-period Standard Deviation of Price x k)
        where n = window, k = num_std_dev

    Args:
        data: A pandas DataFrame with a 'close' column.
        window: The look-back period for the moving average and standard deviation.
        num_std_dev: The number of standard deviations away from the SMA.

    Returns:
        A new DataFrame with 'middle_band', 'upper_band', and 'lower_band' columns.
    """
    data['middle_band'] = data['close'].rolling(window=window).mean()
    data['std_dev'] = data['close'].rolling(window=window).std()
    data['upper_band'] = data['middle_band'] + (data['std_dev'] * num_std_dev)
    data['lower_band'] = data['middle_band'] - (data['std_dev'] * num_std_dev)
    return data

def calculate_stochastic_oscillator(data: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
    """
    Calculates the Stochastic Oscillator (%K and %D lines).

    The Stochastic Oscillator is a momentum indicator comparing a particular
    closing price of a security to a range of its prices over a certain period of time.

    Formula:
        %K = ((Close - Lowest Low) / (Highest High - Lowest Low)) * 100
        %D = 3-period Simple Moving Average of %K

    Args:
        data: A pandas DataFrame with 'high', 'low', and 'close' columns.
        k_window: The look-back period for %K.
        d_window: The moving average period for %D.

    Returns:
        A new DataFrame with '%K' and '%D' columns.
    """
    data['lowest_low'] = data['low'].rolling(window=k_window).min()
    data['highest_high'] = data['high'].rolling(window=k_window).max()
    data['%K'] = ((data['close'] - data['lowest_low']) / (data['highest_high'] - data['lowest_low'])) * 100 # Corrected typo
    data['%D'] = data['%K'].rolling(window=d_window).mean()
    return data

if __name__ == '__main__':
    # Create a sample DataFrame for testing
    data = {
        'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
        'close': [100, 102, 101, 103, 105]
    }
    df = pd.DataFrame(data).set_index('timestamp')

    # Calculate indicators
    df = calculate_sma(df, 3)
    df = calculate_ema(df, 3)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger_bands(df)
    df = calculate_stochastic_oscillator(df)

    print("Technical Indicators:")
    print(df)