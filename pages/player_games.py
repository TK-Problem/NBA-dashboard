from dash import dcc, no_update, html
from dash.dependencies import Input, Output
from dash import dash_table

import dash_bootstrap_components as dbc

from app import app
from utils import navbar, footer

import pandas as pd
import requests
from bs4 import BeautifulSoup

# player ids and year range when they were in the league
df_ids = pd.read_csv('data/player_ids.csv', index_col=0)
# DataFrame to store information about all games in specific season
df_games = pd.DataFrame()
# DataFrame to store information about average stats in regular season
df_reg_s = pd.DataFrame()
# generate player id dictionary for dropdown list
id_dict = [{'label': _[0], 'value': _[1]} for _ in df_ids.values]


def get_season_stats(player_id):
    """
    Returns regular season stats
    :param player_id: string, e.g. mcgeeja01
    :return:
    """
    # generate request url
    url = f'https://www.basketball-reference.com/players/{player_id[0]}/{player_id}.html'

    # request
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # table element for regular season stats
    table = soup.find('div', {'id': 'all_per_game-playoffs_per_game'}).table

    col_names = [_.text for _ in table.thead.findAll('th')]
    table_data = [[_.text for _ in row] for row in table.findAll('tr', {'class': 'full_table'})]

    return pd.DataFrame(table_data, columns=col_names)


# helper functions
def clean_df(df):
    """
    Cleans input DataFrame:
        * exclude rows with column names
        * rename columns
        * create new feature which tells by how many points game was won/lost
        * new feature, boolean outcome: game won or lost
        * new feature where game was played: home or away
    :param df: pandas DataFrame
    :return: pandas DataFrame
    """
    # remove empty rows
    df = df[df.G != 'G'][df.columns[2:]].reset_index(drop=True)
    # rename columns
    df = df.rename(columns={'Unnamed: 5': 'Side', 'Unnamed: 7': 'Outcome'})
    # calculate result, W for wins, L for lost
    df['Result'] = df['Outcome'].apply(lambda x: x.split('(')[1][:-1])
    # create new feature with game result, + means game was won, - lost by X points
    df['Outcome'] = df['Outcome'].apply(lambda x: x.split('(')[0])
    # create column where the game was played for specific player
    df['Side'] = df['Side'].fillna('Away').replace('@', 'Home')

    return df


layout = html.Div([
    navbar,

    # data selection
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div([
                html.Label('Player Games'),

                dcc.Dropdown(
                    id='player-id-drop',
                    options=id_dict,
                    value='player_id',
                    clearable=False,
                    placeholder="Select player"
                ),

                html.Label('Select season'),

                dcc.Dropdown(
                    id='player-years-drop',
                    options=[],
                    value='year',
                    clearable=False,
                    placeholder="Select player"
                ),
            ]), md=4),

            dbc.Col(html.Div("Player info"), md=4),

            dbc.Col(html.Div([
                html.Label("Regular Season stats"),

                dash_table.DataTable(
                        id='player-reg-season-games-table',
                        columns=[],
                        data=[{}],
                        page_size=5
                        ),
            ]), md=4),
        ]),
    ], fluid=True),

    html.Div(id='table-name'),

    dash_table.DataTable(
        id='games-logs-table',
        columns=[],
        data=[{}],
        page_size=20
        ),
    footer
])


@app.callback(
    [Output('player-years-drop', 'options'),
     Output('player-reg-season-games-table', 'columns'),
     Output('player-reg-season-games-table', 'data')],
    Input('player-id-drop', 'value'))
def update_year_dropdown(player_id):
    """
    Returns year range, e.g. from 1991 to 1997, for year drop down menu
    :param player_id: string
    :return: list with dictionary inside, e.g.
    [{'label': 1991-1992, 'value': 1991-1992}, {'label': 1992-1993, 'value': 1992-1993}]
    """
    global df_ids, df_reg_s
    if player_id == 'player_id':
        return no_update, no_update, no_update
    else:
        df_reg_s = get_season_stats(player_id)

        # seasons played
        season = [{'label': _, 'value': _} for _ in df_reg_s.Season]

        # season avg. stats
        col_names = [{"name": i, "id": i} for i in df_reg_s.columns]
        table_data = df_reg_s.to_dict('records')
        return season, col_names, table_data


@app.callback(
    [Output('games-logs-table', 'columns'),
     Output('games-logs-table', 'data'),
     Output('table-name', 'children')],
    [Input('player-id-drop', 'value'),
     Input('player-years-drop', 'value')],
    prevent_initial_call=True
)
def update_table(player_id, season):
    """
    Loads player's game for specific season as pandas DataFrame
    :param player_id: string,
    :param season: int
    :return: column names, table data for 'games-table' object and table title for text object
    """
    global df_games, df_ids
    if player_id != 'player_id' and season != 'year':

        url = f"https://www.basketball-reference.com/players/a/{player_id}/gamelog/{int(season.split('-')[0])+1}"

        try:
            tables = pd.read_html(url)
            df_games = clean_df(tables[-1])
            table_data = df_games.to_dict('records')
            col_names = [{"name": i, "id": i} for i in df_games.columns]
            player_name = df_ids.loc[df_ids.Player_ID == player_id, 'Player_name'].values[0]
        except ValueError:
            print(f'{url} not loaded.')
            return no_update, no_update, no_update
        else:
            return col_names, table_data, f'{player_name} {season} regular season game-logs.'
    else:
        return no_update, no_update, no_update
