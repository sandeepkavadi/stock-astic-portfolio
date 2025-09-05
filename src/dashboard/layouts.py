from dash import dcc, html, dash_table
from src.trading.schwab_api import get_positions, get_long_term_holdings # Import get_long_term_holdings

def portfolio_performance_layout():
    positions = get_positions()
    long_term_holdings = get_long_term_holdings() or {}

    # Calculate profit/loss for each position
    for p in positions:
        p['cost_basis'] = p['quantity'] * p.get('average_price', 0)
        p['profit_loss'] = p['market_value'] - p['cost_basis']

    # Sort positions by market_value in descending order
    positions = sorted(positions, key=lambda x: x.get('market_value', 0), reverse=True)

    total_market_value = sum(p.get('market_value', 0) for p in positions)
    total_cost_basis = sum(p.get('cost_basis', 0) for p in positions)
    total_profit_loss = sum(p.get('profit_loss', 0) for p in positions)

    return html.Div([
        html.H3('Portfolio Performance', style={'textAlign': 'center', 'margin-bottom': '20px'}),
        html.Div([
            html.H4(f'Total Market Value: ${total_market_value:,.2f}', style={'textAlign': 'center'}),
            html.H4(f'Total Cost Basis: ${total_cost_basis:,.2f}', style={'textAlign': 'center'}),
            html.H4(f'Total Profit/Loss: ${total_profit_loss:,.2f}', style={'textAlign': 'center', 'color': 'green' if total_profit_loss >= 0 else 'red'}),
        ], style={'margin-bottom': '20px'}),
        dash_table.DataTable(
            id='positions-table',
            columns=[
                {'name': 'Account ID', 'id': 'account_id'}, # New column for Account ID
                {'name': 'Symbol', 'id': 'symbol'},
                {'name': 'Quantity', 'id': 'quantity'},
                {'name': 'Average Price', 'id': 'average_price', 'type': 'numeric', 'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
                {'name': 'Current Price', 'id': 'current_price', 'type': 'numeric', 'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
                {'name': 'Cost Basis', 'id': 'cost_basis', 'type': 'numeric', 'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
                {'name': 'Market Value', 'id': 'market_value', 'type': 'numeric', 'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
                {'name': 'Profit/Loss', 'id': 'profit_loss', 'type': 'numeric', 'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
                {'name': 'As of', 'id': 'as_of_timestamp'},
            ],
            data=positions,
            style_table={'height': '400px', 'overflowY': 'auto', 'width': '95%', 'margin': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'profit_loss',
                             'filter_query': '{profit_loss} < 0'},
                    'color': 'red'
                },
                {
                    'if': {'column_id': 'profit_loss',
                             'filter_query': '{profit_loss} >= 0'},
                    'color': 'green'
                }
            ]
        ),
        html.Div([
            html.H4('Long-Term Holdings (for Tax Implications)', style={'textAlign': 'center', 'margin-top': '30px'}),
            dash_table.DataTable(
                id='long-term-holdings-table',
                columns=[
                    {'name': 'Symbol', 'id': 'symbol'},
                    {'name': 'Long-Term Quantity', 'id': 'long_term_quantity'},
                ],
                data=[{'symbol': s, 'long_term_quantity': q} for s, q in long_term_holdings.items()],
                style_table={'height': '200px', 'overflowY': 'auto', 'width': '80%', 'margin': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '5px'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            ),
            html.P('Note: This is a simplified calculation based on transaction dates and does not account for complex accounting methods (e.g., FIFO/LIFO) or wash sales.', style={'textAlign': 'center', 'fontStyle': 'italic', 'margin-top': '10px'})
        ])
    ], style={'padding': '20px'})

def watchlist_layout():
    return html.Div([
        html.H3('Watchlist', style={'textAlign': 'center', 'margin-bottom': '20px'}),
        html.Div([
            dcc.Input(id='new-stock-input', type='text', placeholder='Enter stock symbol', style={'margin-right': '10px', 'width': '150px'}),
            html.Button('Add to Watchlist', id='add-stock-button', n_clicks=0, style={'margin-right': '10px'}),
            html.Button('Remove from Watchlist', id='remove-stock-button', n_clicks=0),
        ], style={'textAlign': 'center', 'margin-bottom': '10px'}),
        html.Div(id='watchlist-feedback', style={'color': 'red', 'margin-top': '5px', 'textAlign': 'center'}),
        html.Div(id='watchlist-output', style={'margin-bottom': '20px', 'textAlign': 'center'}),
        dcc.Dropdown(id='stock-input', placeholder='Select a stock', style={'width': '50%', 'margin': 'auto', 'margin-bottom': '20px'}), # Changed to Dropdown
        dcc.Graph(id='stock-graph', style={'height': '800px'}) # Increased graph height
    ], style={'padding': '20px'})