import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_stock_data(df: pd.DataFrame, symbol: str):
    """
    Plots the stock data with technical indicators and trade signals.

    Args:
        df: A pandas DataFrame with price data, technical indicators, and 'buy_signal'/'sell_signal' columns.
        symbol: The stock symbol.
        
    Returns:
        A plotly figure.
    """
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                       vertical_spacing=0.02,
                       subplot_titles=(f'{symbol} Candlestick', 'RSI and MACD', 'Stochastic Oscillator'),
                       row_heights=[0.6, 0.2, 0.2])

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='Candlestick'),
                  row=1, col=1)

    # Moving Averages
    for col in df.columns:
        if 'sma' in col or 'ema' in col:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['upper_band'], name='Upper Band', line=dict(color='rgba(0,0,255,0.5)')),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['middle_band'], name='Middle Band', line=dict(color='rgba(0,0,255,0.5)')),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['lower_band'], name='Lower Band', line=dict(color='rgba(0,0,255,0.5)')),
                  row=1, col=1)

    # Buy Signals (SMA Crossover)
    buy_signals_sma = df[df['buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_sma.index,
        y=buy_signals_sma['close'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='green'),
        name='SMA Buy Signal',
        showlegend=True
    ), row=1, col=1)

    # Sell Signals (SMA Crossover)
    sell_signals_sma = df[df['sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_sma.index,
        y=sell_signals_sma['close'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='red'),
        name='SMA Sell Signal',
        showlegend=True
    ), row=1, col=1)

    # Buy Signals (Bollinger Bands)
    buy_signals_bb = df[df['bb_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_bb.index,
        y=buy_signals_bb['close'],
        mode='markers',
        marker=dict(symbol='circle', size=10, color='purple', line=dict(width=2, color='DarkSlateGrey')),
        name='BB Buy Signal',
        showlegend=True
    ), row=1, col=1)

    # Sell Signals (Bollinger Bands)
    sell_signals_bb = df[df['bb_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_bb.index,
        y=sell_signals_bb['close'],
        mode='markers',
        marker=dict(symbol='x', size=10, color='brown', line=dict(width=2, color='DarkSlateGrey')),
        name='BB Sell Signal',
        showlegend=True
    ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], name='RSI'), row=2, col=1)

    # Buy Signals (RSI)
    buy_signals_rsi = df[df['rsi_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_rsi.index,
        y=buy_signals_rsi['rsi'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='blue'),
        name='RSI Buy Signal',
        showlegend=True
    ), row=2, col=1)

    # Sell Signals (RSI)
    sell_signals_rsi = df[df['rsi_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_rsi.index,
        y=sell_signals_rsi['rsi'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='orange'),
        name='RSI Sell Signal',
        showlegend=True
    ), row=2, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], name='Signal Line'), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['macd_histogram'], name='MACD Histogram'), row=2, col=1)

    # Buy Signals (MACD)
    buy_signals_macd = df[df['macd_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_macd.index,
        y=buy_signals_macd['macd'],
        mode='markers',
        marker=dict(symbol='circle', size=10, color='purple'),
        name='MACD Buy Signal',
        showlegend=True
    ), row=2, col=1)

    # Sell Signals (MACD)
    sell_signals_macd = df[df['macd_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_macd.index,
        y=sell_signals_macd['macd'],
        mode='markers',
        marker=dict(symbol='x', size=10, color='brown'),
        name='MACD Sell Signal',
        showlegend=True
    ), row=2, col=1)

    # Stochastic Oscillator
    fig.add_trace(go.Scatter(x=df.index, y=df['%K'], name='%K'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['%D'], name='%D'), row=3, col=1)

    # Buy Signals (Stochastic Oscillator)
    buy_signals_stoch = df[df['stoch_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_stoch.index,
        y=buy_signals_stoch['%K'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='cyan'),
        name='Stoch Buy Signal',
        showlegend=True
    ), row=3, col=1)

    # Sell Signals (Stochastic Oscillator)
    sell_signals_stoch = df[df['stoch_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_stoch.index,
        y=sell_signals_stoch['%K'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='magenta'),
        name='Stoch Sell Signal',
        showlegend=True
    ), row=3, col=1)

    fig.update_layout(
        title=f'{symbol} Stock Analysis',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False
    )

    return fig