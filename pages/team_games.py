from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from utils import navbar, footer

layout = html.Div([
    navbar,
    html.H3('Team Games'),
    dcc.Dropdown(
        id='app-2-dropdown',
        options=[
            {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-2-display-value'),
    dcc.Link('Go to App 1', href='/player-games'),
    footer
])


@app.callback(
    Output(component_id='app-2-display-value', component_property='children'),
    Input('app-2-dropdown', 'value'))
def display_value(value):
    return 'You have selected "{}"'.format(value)
