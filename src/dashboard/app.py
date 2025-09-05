
import dash
from dash import dcc, html

from src.dashboard.callbacks import register_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1('Stock-astic Portfolio'),
    dcc.Tabs(id='tabs', value='tab-watchlist', children=[
        dcc.Tab(label='Watchlist', value='tab-watchlist'),
        dcc.Tab(label='Portfolio Performance', value='tab-portfolio'),
    ]),
    html.Div(id='tabs-content')
])

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8051)
