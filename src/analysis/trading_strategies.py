import pandas as pd

def sma_crossover_strategy(df: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
    """
    Implements a Simple Moving Average (SMA) crossover strategy.

    Generates 'Buy' signals when the short-term SMA crosses above the long-term SMA,
    and 'Sell' signals when the short-term SMA crosses below the long-term SMA.

    Args:
        df: A pandas DataFrame with 'close' prices and calculated SMAs (e.g., 'sma_20', 'sma_50').
        short_window: The window size for the short-term SMA.
        long_window: The window size for the long-term SMA.

    Returns:
        A DataFrame with 'buy_signal' and 'sell_signal' columns (boolean).
    """
    df['short_sma'] = df[f'sma_{short_window}']
    df['long_sma'] = df[f'sma_{long_window}']

    # Generate signals
    df['buy_signal'] = (df['short_sma'].shift(1) < df['long_sma'].shift(1)) & \
                       (df['short_sma'] > df['long_sma'])
    df['sell_signal'] = (df['short_sma'].shift(1) > df['long_sma'].shift(1)) & \
                        (df['short_sma'] < df['long_sma'])

    return df

def rsi_strategy(df: pd.DataFrame, overbought_level: int = 70, oversold_level: int = 30) -> pd.DataFrame:
    """
    Implements an RSI (Relative Strength Index) strategy.

    Generates 'Buy' signals when RSI crosses below the oversold level,
    and 'Sell' signals when RSI crosses above the overbought level.

    Args:
        df: A pandas DataFrame with an 'rsi' column.
        overbought_level: The RSI level considered overbought.
        oversold_level: The RSI level considered oversold.

    Returns:
        A DataFrame with 'rsi_buy_signal' and 'rsi_sell_signal' columns (boolean).
    """
    df['rsi_buy_signal'] = (df['rsi'].shift(1) > oversold_level) & (df['rsi'] <= oversold_level)
    df['rsi_sell_signal'] = (df['rsi'].shift(1) < overbought_level) & (df['rsi'] >= overbought_level)
    return df

def macd_crossover_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Implements a MACD (Moving Average Convergence Divergence) crossover strategy.

    Generates 'Buy' signals when the MACD line crosses above the Signal line,
    and 'Sell' signals when the MACD line crosses below the Signal line.

    Args:
        df: A pandas DataFrame with 'macd' and 'macd_signal' columns.

    Returns:
        A DataFrame with 'macd_buy_signal' and 'macd_sell_signal' columns (boolean).
    """
    df['macd_buy_signal'] = (df['macd'].shift(1) < df['macd_signal'].shift(1)) & \
                            (df['macd'] > df['macd_signal'])
    df['macd_sell_signal'] = (df['macd'].shift(1) > df['macd_signal'].shift(1)) & \
                             (df['macd'] < df['macd_signal'])
    return df

def bollinger_bands_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Implements a Bollinger Bands strategy.

    Generates 'Buy' signals when the price crosses below the lower band,
    and 'Sell' signals when the price crosses above the upper band.

    Args:
        df: A pandas DataFrame with 'close', 'upper_band', and 'lower_band' columns.

    Returns:
        A DataFrame with 'bb_buy_signal' and 'bb_sell_signal' columns (boolean).
    """
    df['bb_buy_signal'] = (df['close'] < df['lower_band'])
    df['bb_sell_signal'] = (df['close'] > df['upper_band'])
    return df

def stochastic_oscillator_strategy(df: pd.DataFrame, overbought_level: int = 80, oversold_level: int = 20) -> pd.DataFrame:
    """
    Implements a Stochastic Oscillator strategy.

    Generates 'Buy' signals when %K crosses above %D, especially when both are below the oversold level,
    and 'Sell' signals when %K crosses below %D, especially when both are above the overbought level.

    Args:
        df: A pandas DataFrame with '%K' and '%D' columns.
        overbought_level: The level considered overbought.
        oversold_level: The level considered oversold.

    Returns:
        A DataFrame with 'stoch_buy_signal' and 'stoch_sell_signal' columns (boolean).
    """
    df['stoch_buy_signal'] = (df['%K'].shift(1) < df['%D'].shift(1)) & \
                             (df['%K'] > df['%D']) & \
                             (df['%K'] < oversold_level)
    df['stoch_sell_signal'] = (df['%K'].shift(1) > df['%D'].shift(1)) & \
                              (df['%K'] < df['%D']) & \
                              (df['%K'] > overbought_level)
    return df

def combine_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combines buy/sell signals from multiple strategies.

    A 'strong_buy_signal' is generated if at least two buy signals are present
    and no sell signals are present from any strategy.
    A 'strong_sell_signal' is generated if at least two sell signals are present
    and no buy signals are present from any strategy.

    Args:
        df: A pandas DataFrame containing individual strategy signals
            (e.g., 'buy_signal', 'sell_signal', 'rsi_buy_signal', etc.).

    Returns:
        A DataFrame with 'strong_buy_signal' and 'strong_sell_signal' columns (boolean).
    """
    # Initialize combined signals to False
    df['strong_buy_signal'] = False
    df['strong_sell_signal'] = False

    # Count buy and sell signals for each row
    buy_signal_columns = [col for col in df.columns if 'buy_signal' in col and col != 'strong_buy_signal']
    sell_signal_columns = [col for col in df.columns if 'sell_signal' in col and col != 'strong_sell_signal']

    df['buy_signal_count'] = df[buy_signal_columns].sum(axis=1)
    df['sell_signal_count'] = df[sell_signal_columns].sum(axis=1)

    # Define combination logic
    df['strong_buy_signal'] = (df['buy_signal_count'] >= 2) & (df['sell_signal_count'] == 0)
    df['strong_sell_signal'] = (df['sell_signal_count'] >= 2) & (df['buy_signal_count'] == 0)

    return df

if __name__ == '__main__':
    # Create a sample DataFrame for testing
    data = {
        'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                     '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'close': [100, 102, 101, 103, 105, 104, 106, 107, 105, 103],
        'high': [101, 103, 102, 104, 106, 105, 107, 108, 106, 104],
        'low': [99, 101, 100, 102, 104, 103, 105, 106, 104, 102]
    }
    df = pd.DataFrame(data).set_index('timestamp')

    # Calculate SMAs (assuming these are already calculated by technical_analysis)
    df['sma_2'] = df['close'].rolling(window=2).mean()
    df['sma_3'] = df['close'].rolling(window=3).mean()

    # Apply SMA strategy
    df = sma_crossover_strategy(df, short_window=2, long_window=3)

    # Calculate RSI (assuming this is already calculated by technical_analysis)
    # Dummy RSI for testing
    df['rsi'] = [50, 40, 35, 25, 28, 32, 60, 75, 72, 65]

    # Apply RSI strategy
    df = rsi_strategy(df)

    # Calculate MACD (assuming this is already calculated by technical_analysis)
    # Dummy MACD for testing
    df['macd'] = [1, 2, 3, 2, 1, 0, -1, -2, -3, -2]
    df['macd_signal'] = [0.5, 1.5, 2.5, 2.0, 1.0, 0.0, -0.5, -1.5, -2.5, -2.0]

    # Apply MACD strategy
    df = macd_crossover_strategy(df)

    # Calculate Bollinger Bands (assuming this is already calculated by technical_analysis)
    # Dummy Bollinger Bands for testing
    df['upper_band'] = [105, 107, 106, 108, 110, 109, 111, 112, 110, 108]
    df['lower_band'] = [95, 97, 96, 98, 100, 99, 101, 102, 100, 98]

    # Apply Bollinger Bands strategy
    df = bollinger_bands_strategy(df)

    # Calculate Stochastic Oscillator (assuming this is already calculated by technical_analysis)
    df['%K'] = [20, 30, 40, 50, 60, 70, 80, 90, 70, 60]
    df['%D'] = [25, 35, 45, 55, 65, 75, 85, 80, 70, 65]

    # Apply Stochastic Oscillator strategy
    df = stochastic_oscillator_strategy(df)

    # Combine signals
    df = combine_signals(df)

    print("SMA Crossover Signals:")
    print(df[['close', 'sma_2', 'sma_3', 'buy_signal', 'sell_signal']])
    print("\nRSI Signals:")
    print(df[['close', 'rsi', 'rsi_buy_signal', 'rsi_sell_signal']])
    print("\nMACD Signals:")
    print(df[['close', 'macd', 'macd_signal', 'macd_buy_signal', 'macd_sell_signal']])
    print("\nBollinger Bands Signals:")
    print(df[['close', 'upper_band', 'lower_band', 'bb_buy_signal', 'bb_sell_signal']])
    print("\nStochastic Oscillator Signals:")
    print(df[['close', '%K', '%D', 'stoch_buy_signal', 'stoch_sell_signal']])
    print("\nCombined Signals:")
    print(df[['close', 'buy_signal_count', 'sell_signal_count', 'strong_buy_signal', 'strong_sell_signal']])