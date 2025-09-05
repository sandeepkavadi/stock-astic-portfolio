from dash import dcc, html, dash_table
from src.trading.schwab import get_positions

def portfolio_performance_layout():
    positions = get_positions()

    total_market_value = sum(p.get('market_value', 0) for p in positions)

    return html.Div([
        html.H3('Portfolio Performance'),
        html.Div([
            html.H4(f'Total Market Value: ${total_market_value:,.2f}'),
        ], style={'margin-bottom': '20px'}),
        dash_table.DataTable(
            id='positions-table',
            columns=[
                {'name': 'Symbol', 'id': 'symbol'},
                {'name': 'Quantity', 'id': 'quantity'},
                {'name': 'Market Value', 'id': 'market_value'},
            ],
            data=positions,
        )
    ])

def watchlist_layout():
    return html.Div([
        html.H3('Watchlist'),
        html.Div([
            dcc.Input(id='new-stock-input', type='text', placeholder='Enter stock symbol'),
            html.Button('Add to Watchlist', id='add-stock-button', n_clicks=0),
            html.Button('Remove from Watchlist', id='remove-stock-button', n_clicks=0),
        ]),
        html.Div(id='watchlist-feedback', style={'color': 'red', 'margin-top': '5px'}),
        html.Div(id='watchlist-output'),
        dcc.Dropdown(id='stock-input', placeholder='Select a stock'), # Changed to Dropdown
        dcc.Graph(id='stock-graph')
    ])