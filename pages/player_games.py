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

    # get player stats
    player_info = soup.find('div', {"class": 'players'})

    # get image location
    try:
        player_photo_src = player_info.find('div', {'class': 'media-item'}).img['src']
    except AttributeError:
        player_photo_src = 'assets/face_placeholder.png'

    try:
        player_name = player_info.span.text
    except AttributeError:
        player_name = ''

    # get information about player
    mk_text = ""

    for attr in player_info.findAll('span'):
        try:
            # check if item has item property attribute
            attr_name = attr['itemprop']
            attr_value = attr.text.strip()
            # ignore attributes with no values
            if attr_value != '':
                mk_text += f"* {attr_name}: {attr_value} \n"
        except KeyError:
            pass

    # table element for regular season stats
    table = soup.find('div', {'id': 'all_per_game-playoffs_per_game'}).table

    col_names = [_.text for _ in table.thead.findAll('th')]
    table_data = [[_.text for _ in row] for row in table.findAll('tr', {'class': 'full_table'})]

    return pd.DataFrame(table_data, columns=col_names), player_photo_src, player_name, mk_text


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
            # selecting player
            dbc.Col(html.Div([

                html.H3('Data selection'),

                dcc.Dropdown(
                    id='player-id-drop',
                    options=id_dict,
                    value='player_id',
                    clearable=False,
                    placeholder="Select player"
                ),

                dcc.Dropdown(
                    id='player-years-drop',
                    options=[],
                    value='year',
                    clearable=False,
                    placeholder="Select player"
                ),
            ]), md=4),

            # player info
            dbc.Col([
                dbc.Row([

                    dbc.Col(html.Img(id='player-photo', src='')),

                    dbc.Col([
                        html.H4(children="player-name", id="card-title-player-name"),
                        dcc.Markdown(children="", id='player-text-info')
                    ]),
                ]),


            ], md=4),

            # season stats
            dbc.Col(html.Div([
                html.H3("Regular Season stats"),

                dash_table.DataTable(
                        id='player-reg-season-games-table',
                        columns=[],
                        data=[{}],
                        page_size=5
                        ),
            ]), md=4),
        ]),
    ], fluid=True),

    dbc.Row([
        html.H3(id='table-name'),

        dash_table.DataTable(
            id='games-logs-table',
            columns=[],
            data=[{}],
            page_size=20
            ),
    ]),

    footer
])


@app.callback(
    [Output(component_id='player-years-drop', component_property='options'),
     Output(component_id='player-reg-season-games-table', component_property='columns'),
     Output(component_id='player-reg-season-games-table', component_property='data'),
     Output(component_id='player-photo', component_property='src'),
     Output(component_id='card-title-player-name', component_property='children'),
     Output(component_id='player-text-info', component_property='children')],
    Input(component_id='player-id-drop', component_property='value'))
def update_year_dropdown(player_id):
    """
    Returns year range, e.g. from 1991 to 1997, for year drop down menu
    :param player_id: string
    :return: list with dictionary inside, e.g.
    [{'label': 1991-1992, 'value': 1991-1992}, {'label': 1992-1993, 'value': 1992-1993}]
    """
    global df_ids, df_reg_s
    if player_id == 'player_id':
        return no_update, no_update, no_update, no_update, no_update, no_update
    else:
        # regular season game stats
        df_reg_s, player_photo_src, player_name, mk_text = get_season_stats(player_id)

        # seasons played for dropdown menu
        season = [{'label': _, 'value': _} for _ in df_reg_s.Season]

        # return only specific columns
        col_names = ['Season', 'G', 'MP', 'PTS']

        # season avg. stats
        table_data = df_reg_s[col_names].to_dict('records')
        col_names = [{"name": i, "id": i} for i in col_names]

        return season, col_names, table_data, player_photo_src, player_name, mk_text


@app.callback(
    [Output(component_id='games-logs-table', component_property='columns'),
     Output(component_id='games-logs-table', component_property='data'),
     Output(component_id='table-name', component_property='children')],
    [Input(component_id='player-id-drop', component_property='value'),
     Input(component_id='player-years-drop', component_property='value')],
    prevent_initial_call=True
)
def update_game_log_table(player_id, season):
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
            # read all tables in the page
            tables = pd.read_html(url)
            # return only reg. season game logs
            df_games = clean_df(tables[-1])

            # create dictionary for table and list with column names
            table_data = df_games.to_dict('records')
            # print(df_games.columns)
            col_names = [{"name": i, "id": i} for i in df_games.columns]

            # return player name from df_ids DataFrame
            player_name = df_ids.loc[df_ids.Player_ID == player_id, 'Player_name'].values[0]

        except ValueError:
            print(f'{url} not loaded.')
            # no changes required if URL didn't load
            return no_update, no_update, no_update
        else:
            return col_names, table_data, f'{player_name} {season} regular season game-logs.'
    else:
        # no updates if input is not full
        return no_update, no_update, no_update
