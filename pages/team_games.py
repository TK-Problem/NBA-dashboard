from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from utils import navbar, footer

layout = html.Div([
    navbar,
    html.Label('Team Games'),
    dcc.Dropdown(
        id='app-2-dropdown',
        options=[{'label': '{}'.format(i), 'value': i} for i in ['Team 1', 'Team 2', 'Team 3']]
    ),
    html.Div(id='app-2-display-value'),
    dcc.Link('Go to App 1', href='/player-games'),
    footer
])

