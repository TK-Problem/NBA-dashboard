from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from app import server

from pages import player_games, team_games


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/player-games':
        return player_games.layout
    elif pathname == '/team-games':
        return team_games.layout
    else:
        return player_games.layout


if __name__ == '__main__':
    app.run_server(debug=True)
