import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc # Added dcc
from src.data.market_data import get_daily_data
from src.analysis.technical_analysis import calculate_sma, calculate_ema, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_stochastic_oscillator
from src.analysis.trading_strategies import sma_crossover_strategy, rsi_strategy, macd_crossover_strategy, bollinger_bands_strategy, stochastic_oscillator_strategy
from src.dashboard.visualizations import plot_stock_data
from src.dashboard.layouts import portfolio_performance_layout, watchlist_layout
from src.config import get_alpha_vantage_api_key
from src.utils import read_watchlist, write_watchlist
from src.trading.schwab import get_positions # Import get_positions

def is_valid_symbol(symbol, api_key):
    try:
        # Try to fetch a small amount of data to validate the symbol
        df = get_daily_data(symbol, api_key)
        return not df.empty
    except Exception:
        return False

def register_callbacks(app):
    @app.callback(
        Output('stock-graph', 'figure'),
        Input('stock-input', 'value')
    )
    def update_graph(symbol):
        api_key = get_alpha_vantage_api_key()
        if not api_key:
            return {}

        df = get_daily_data(symbol, api_key)
        
        print("--- Debugging update_graph ---")
        print("DataFrame empty:", df.empty)
        print("DataFrame columns:", df.columns.tolist())
        print("DataFrame head:\n", df.head())
        print("--- End Debugging update_graph ---")

        df = calculate_sma(df, window=20)
        df = calculate_sma(df, window=50) # Calculate sma_50
        df = calculate_ema(df, window=20)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        df = calculate_bollinger_bands(df)
        df = calculate_stochastic_oscillator(df)
        
        # Apply trading strategies
        df = sma_crossover_strategy(df, short_window=20, long_window=50)
        df = rsi_strategy(df)
        df = macd_crossover_strategy(df)
        df = bollinger_bands_strategy(df)
        df = stochastic_oscillator_strategy(df)

        fig = plot_stock_data(df, symbol)
        return fig

    @app.callback(
        Output('tabs-content', 'children'),
        Input('tabs', 'value')
    )
    def render_content(tab):
        if tab == 'tab-watchlist':
            return watchlist_layout()
        elif tab == 'tab-portfolio':
            return portfolio_performance_layout()

    @app.callback(
        Output('watchlist-output', 'children'),
        Output('new-stock-input', 'value'), # Clear input after adding/removing
        Output('watchlist-feedback', 'children'), # Feedback message
        Input('add-stock-button', 'n_clicks'),
        Input('remove-stock-button', 'n_clicks'),
        State('new-stock-input', 'value'),
        prevent_initial_call=True
    )
    def update_watchlist(add_clicks, remove_clicks, new_stock_symbol):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        api_key = get_alpha_vantage_api_key()

        watchlist = read_watchlist()
        feedback_message = ""

        if button_id == 'add-stock-button' and new_stock_symbol:
            new_stock_symbol = new_stock_symbol.upper()
            if not api_key:
                feedback_message = "API key not found. Cannot validate symbol."
            elif not is_valid_symbol(new_stock_symbol, api_key):
                feedback_message = f'{new_stock_symbol} is not a valid stock symbol.'
            elif new_stock_symbol not in watchlist:
                watchlist.append(new_stock_symbol)
                write_watchlist(watchlist)
                feedback_message = f'{new_stock_symbol} added to watchlist.'
            else:
                feedback_message = f'{new_stock_symbol} is already in watchlist.'
        elif button_id == 'remove-stock-button' and new_stock_symbol:
            new_stock_symbol = new_stock_symbol.upper()
            if new_stock_symbol in watchlist:
                watchlist.remove(new_stock_symbol)
                write_watchlist(watchlist)
                feedback_message = f'{new_stock_symbol} removed from watchlist.'
            else:
                feedback_message = f'{new_stock_symbol} not found in watchlist.'
        
        return html.Ul([html.Li(stock) for stock in watchlist]), '', feedback_message

    # Callback to load initial watchlist when the app starts
    @app.callback(
        Output('watchlist-output', 'children', allow_duplicate=True),
        Input('tabs', 'value'),
        prevent_initial_call=True
    )
    def load_initial_watchlist(tab_value):
        if tab_value == 'tab-watchlist':
            watchlist = read_watchlist()
            return html.Ul([html.Li(stock) for stock in watchlist])
        raise dash.exceptions.PreventUpdate

    # Callback to update stock-input dropdown options
    @app.callback(
        Output('stock-input', 'options'),
        Output('stock-input', 'value'), # Set default selected value
        Input('watchlist-output', 'children'), # Trigger when watchlist changes
        Input('tabs', 'value') # Trigger when tab changes
    )
    def update_stock_dropdown_options(watchlist_children, tab_value):
        if tab_value != 'tab-watchlist':
            raise dash.exceptions.PreventUpdate

        watchlist_symbols = read_watchlist()
        portfolio_positions = get_positions()
        portfolio_symbols = [p['symbol'] for p in portfolio_positions]

        all_symbols = sorted(list(set(watchlist_symbols + portfolio_symbols)))
        options = [{'label': symbol, 'value': symbol} for symbol in all_symbols]

        # Set default value to the first symbol in the combined list, if any
        default_value = all_symbols[0] if all_symbols else None

        return options, default_value