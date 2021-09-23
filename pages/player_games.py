from dash import dcc, no_update, html
from dash.dependencies import Input, Output
from dash import dash_table

from app import app
from utils import navbar, footer

import pandas as pd


# player ids and year range when they were in the league
df_ids = pd.read_csv('data/player_ids.csv', index_col=0)
# dataframe to store information about all games in specific season
df_games = pd.DataFrame()
# generate player id dictionary for dropdown list
id_dict = [{'label': _[0], 'value': _[1]} for _ in df_ids.values]


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

    html.H3('Player Games'),

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

    html.Div(id='table-name'),

    dash_table.DataTable(
        id='games-table',
        columns=[],
        data=[{}],
        page_size=20
    ),
    footer
])


@app.callback(
    Output('player-years-drop', 'options'),
    Input('player-id-drop', 'value'))
def update_year_dropdown(player_id):
    """
    Returns year range, e.g. from 1991 to 1997, for year drop down menu
    :param player_id: string
    :return: list with dictionary inside, e.g.
    [{'label': 1991, 'value': 1991}, {'label': 1992, 'value': 1992}]
    """
    global df_ids
    if player_id == 'player_id':
        return no_update
    else:
        years = df_ids.loc[df_ids.Player_ID == player_id][['Season_start', 'Season_end']].values.tolist()[0]
        return [{'label': _, 'value': _} for _ in range(years[0], years[1] + 1)]


@app.callback(
    [Output('games-table', 'columns'),
     Output('games-table', 'data'),
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
        url = f"https://www.basketball-reference.com/players/a/{player_id}/gamelog/{season}"
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
            return col_names, table_data, f'{player_name} {season}-{season + 1}.'
    else:
        return no_update, no_update, no_update
