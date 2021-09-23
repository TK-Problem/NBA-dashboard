import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Player-Games", href="/player-games")),
        dbc.NavItem(dbc.NavLink("Team-Games", href="/team-games")),
    ],
    className='navbar navbar-expand-lg navbar-dark bg-primary',
    brand="NBA-dashboard",
    color="primary",
    dark=True,
)


footer = html.Footer(
    dbc.Row(
        dbc.Col(
            html.Div("Footer text place holder",
                     style={'textAlign': 'center'}),
            width={"size": 6, "offset": 3},
        )
    ),
    className='card text-white bg-primary mb-3'
)
