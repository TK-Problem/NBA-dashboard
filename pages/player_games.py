from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from utils import navbar, footer

layout = html.Div([
    navbar,
    html.H3('Player Games'),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    footer
])


@app.callback(
    Output(component_id='app-1-display-value', component_property='children'),
    Input(component_id='app-1-dropdown', component_property='value'))
def display_value(value):
    return 'You have selected "{}"'.format(value)
