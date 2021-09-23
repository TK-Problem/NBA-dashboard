from dash import dcc
from dash import html


# navigation bar
def nav_bar():
    menu = html.Div(
        [
            dcc.Link(
                "Player-Games",
                href="/player-games",
                className="tab first",
            ),
            dcc.Link(
                "Team-Games",
                href="/team-games",
                className="tab",
            ),
        ],
        className="row all-tabs",
    )
    return menu
