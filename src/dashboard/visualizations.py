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
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                       vertical_spacing=0.02,
                       subplot_titles=(f'{symbol} Candlestick', 'RSI and MACD', 'Stochastic Oscillator', 'Combined Signals'),
                       row_heights=[0.5, 0.15, 0.15, 0.2])

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 increasing_line_color='#26a69a', # Green for increasing
                                 decreasing_line_color='#ef5350', # Red for decreasing
                                 name='Candlestick'),
                  row=1, col=1)

    # Moving Averages
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_20'], name='SMA 20', line=dict(color='#2196f3', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_50'], name='SMA 50', line=dict(color='#ff9800', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema_20'], name='EMA 20', line=dict(color='#9c27b0', width=1)), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['upper_band'], name='Upper Band', line=dict(color='#4caf50', width=1, dash='dash')),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['middle_band'], name='Middle Band', line=dict(color='#ffeb3b', width=1)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['lower_band'], name='Lower Band', line=dict(color='#f44336', width=1, dash='dash')),
                  row=1, col=1)

    # Buy Signals (SMA Crossover)
    buy_signals_sma = df[df['buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_sma.index,
        y=buy_signals_sma['close'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='#4caf50'), # Green
        name='SMA Buy Signal',
        showlegend=True
    ), row=1, col=1)

    # Sell Signals (SMA Crossover)
    sell_signals_sma = df[df['sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_sma.index,
        y=sell_signals_sma['close'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='#f44336'), # Red
        name='SMA Sell Signal',
        showlegend=True
    ), row=1, col=1)

    # Buy Signals (Bollinger Bands)
    buy_signals_bb = df[df['bb_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_bb.index,
        y=buy_signals_bb['close'],
        mode='markers',
        marker=dict(symbol='circle', size=10, color='#2196f3', line=dict(width=2, color='#1976d2')),
        name='BB Buy Signal',
        showlegend=True
    ), row=1, col=1)

    # Sell Signals (Bollinger Bands)
    sell_signals_bb = df[df['bb_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_bb.index,
        y=sell_signals_bb['close'],
        mode='markers',
        marker=dict(symbol='x', size=10, color='#ff9800', line=dict(width=2, color='#f57c00')),
        name='BB Sell Signal',
        showlegend=True
    ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], name='RSI', line=dict(color='#673ab7', width=1)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # Buy Signals (RSI)
    buy_signals_rsi = df[df['rsi_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_rsi.index,
        y=buy_signals_rsi['rsi'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='#4caf50'), # Green
        name='RSI Buy Signal',
        showlegend=True
    ), row=2, col=1)

    # Sell Signals (RSI)
    sell_signals_rsi = df[df['rsi_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_rsi.index,
        y=sell_signals_rsi['rsi'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='#f44336'), # Red
        name='RSI Sell Signal',
        showlegend=True
    ), row=2, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD', line=dict(color='#009688', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], name='Signal Line', line=dict(color='#ffc107', width=1)), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['macd_histogram'], name='MACD Histogram', marker_color='#9e9e9e'), row=2, col=1)

    # Buy Signals (MACD)
    buy_signals_macd = df[df['macd_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_macd.index,
        y=buy_signals_macd['macd'],
        mode='markers',
        marker=dict(symbol='circle', size=10, color='#4caf50'), # Green
        name='MACD Buy Signal',
        showlegend=True
    ), row=2, col=1)

    # Sell Signals (MACD)
    sell_signals_macd = df[df['macd_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_macd.index,
        y=sell_signals_macd['macd'],
        mode='markers',
        marker=dict(symbol='x', size=10, color='#f44336'), # Red
        name='MACD Sell Signal',
        showlegend=True
    ), row=2, col=1)

    # Stochastic Oscillator
    fig.add_trace(go.Scatter(x=df.index, y=df['%K'], name='%K', line=dict(color='#03a9f4', width=1)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['%D'], name='%D', line=dict(color='#ff5722', width=1)), row=3, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="green", row=3, col=1)

    # Buy Signals (Stochastic Oscillator)
    buy_signals_stoch = df[df['stoch_buy_signal']]
    fig.add_trace(go.Scatter(
        x=buy_signals_stoch.index,
        y=buy_signals_stoch['%K'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='#4caf50'), # Green
        name='Stoch Buy Signal',
        showlegend=True
    ), row=3, col=1)

    # Sell Signals (Stochastic Oscillator)
    sell_signals_stoch = df[df['stoch_sell_signal']]
    fig.add_trace(go.Scatter(
        x=sell_signals_stoch.index,
        y=sell_signals_stoch['%K'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='#f44336'), # Red
        name='Stoch Sell Signal',
        showlegend=True
    ), row=3, col=1)

    # Combined Signals
    fig.add_trace(go.Scatter(
        x=df.index[df['strong_buy_signal']],
        y=df['close'][df['strong_buy_signal']],
        mode='markers',
        marker=dict(symbol='star', size=12, color='#00c853'), # Dark Green
        name='Strong Buy',
        showlegend=True
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index[df['strong_sell_signal']],
        y=df['close'][df['strong_sell_signal']],
        mode='markers',
        marker=dict(symbol='star', size=12, color='#d50000'), # Dark Red
        name='Strong Sell',
        showlegend=True
    ), row=1, col=1)

    fig.update_layout(
        title=f'{symbol} Stock Analysis',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        template='plotly_white', # Use a clean white template
        hovermode='x unified',
        height=900 # Set overall figure height
    )

    return fig