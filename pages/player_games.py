from dash import dcc, no_update, html
from dash.dependencies import Input, Output
from dash import dash_table

import dash_bootstrap_components as dbc

from app import app
from utils import navbar, footer, html_2_table

import pandas as pd
import requests
from bs4 import BeautifulSoup

# player ids and year range when they were in the league
df_ids = pd.read_csv('data/player_ids.csv', index_col=0)
# DataFrame to store information about all games in reg. season and play-offs
df_reg_games = pd.DataFrame()
df_po_games = pd.DataFrame()
# DataFrame to store information about average stats in regular season and play-offs
df_reg_s = pd.DataFrame()
df_po_s = pd.DataFrame()
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

    # table with regular season stats
    table_rs = soup.find('table', {'id': 'per_game'})
    df_rs = html_2_table(table_rs)
    # table with play-off stats
    table_po = soup.find('table', {'id': 'playoffs_per_game'})
    df_po = html_2_table(table_po)

    return df_rs, df_po, player_photo_src, player_name, mk_text


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


# data selection card
card_data = dbc.Card([
    dbc.CardBody([
        html.H4('Data selection', className="card-title"),

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
    ])
])

# player info card
card_p_info = dbc.Fade(
    dbc.Card([
        dbc.Row([

            dbc.Col(html.Img(id='player-photo', src=''), align="center", sm=3),

            dbc.Col([
                html.H4(children="", id="card-title-player-name", className="card-title"),
                dcc.Markdown(children="", id='player-text-info')
            ], sm=7),
        ], justify="center"),
    ]),
    id="card-title-player-info-fade",
    is_in=False,
    appear=False
)

# player season stats card
card_p_seasons = dbc.Fade(
    dbc.Card([dbc.Tabs([

        html.H4("Regular Season stats", className="card-title"),

        dbc.Tab(
            dash_table.DataTable(
                id='player-reg-season-games-table',
                columns=[],
                data=[{}],
                page_size=5),
            label='Regular season game-logs'),

        dbc.Tab(
            dash_table.DataTable(
                id='player-po-games-table',
                columns=[],
                data=[{}],
                page_size=5),
            label='Play-off game-logs')
        ])
    ]),
    id="card-player-reg-season-games-table-fade",
    is_in=False,
    appear=False
)

# game-log card
game_log_tabs = dbc.Tabs([

    dbc.Tab([
        html.H4(id='games-logs-table-name', className="card-title"),
        dash_table.DataTable(
            id='games-logs-table',
            data=[{}],
            columns=[],
            style_table={'overflowX': 'auto'},
            style_cell={
                    'minWidth': '30px', 'width': '60px', 'maxWidth': '120px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
            },
            page_size=20)],
            label='Regular season game-logs'),
    # dbc.Tab(tab_po, label='Play-off game-logs')
])


layout = html.Div([
    navbar,

    # data selection
    dbc.Container([

        dbc.Row([
            # selecting data- player name, season
            dbc.Col(card_data, width=12, lg=4),

            # player info
            dbc.Col(card_p_info, width=12, lg=4),

            # season stats
            dbc.Col(card_p_seasons, width=12, lg=4),
        ]),

        dbc.Row(dbc.Col(game_log_tabs, width=12))

    ], fluid=True),

    footer
])


@app.callback([
    Output(component_id='player-years-drop', component_property='options'),
    Output(component_id='player-reg-season-games-table', component_property='columns'),
    Output(component_id='player-reg-season-games-table', component_property='data'),
    Output(component_id='player-po-games-table', component_property='columns'),
    Output(component_id='player-po-games-table', component_property='data'),
    Output(component_id='player-photo', component_property='src'),
    Output(component_id='card-title-player-name', component_property='children'),
    Output(component_id='player-text-info', component_property='children'),
    Output(component_id='card-title-player-info-fade', component_property='is_in'),
    Output(component_id='card-player-reg-season-games-table-fade', component_property='is_in')
],
    Input(component_id='player-id-drop', component_property='value'))
def update_year_dropdown(player_id):
    """
    Returns year range, e.g. from 1991 to 1997, for year drop down menu
    :param player_id: string
    :return: list with dictionary inside, e.g.
    [{'label': 1991-1992, 'value': 1991-1992}, {'label': 1992-1993, 'value': 1992-1993}]
    """
    global df_ids, df_reg_s, df_po_s

    # if invalid name inputted apply no changes
    if player_id == 'player_id':
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    else:
        # regular season game stats
        df_reg_s, df_po_s, player_photo_src, player_name, mk_text = get_season_stats(player_id)

        # seasons played for dropdown menu
        season = [{'label': _, 'value': _} for _ in df_reg_s.Season]

        # return only specific columns
        col_names = ['Season', 'G', 'MP', 'PTS']

        # regular season avg. stats
        if len(df_reg_s) > 0:
            table_data_reg = df_reg_s[col_names].to_dict('records')
        else:
            table_data_reg = [{}]

        # play-off season avg. stats
        if len(df_po_s) > 0:
            table_data_po = df_po_s[col_names].to_dict('records')
        else:
            table_data_po = [{}]

        col_names = [{"name": i, "id": i} for i in col_names]

        return season, col_names, table_data_reg, col_names, table_data_po, player_photo_src, player_name, mk_text, True, True


@app.callback(
    [Output(component_id='games-logs-table', component_property='columns'),
     Output(component_id='games-logs-table', component_property='data'),
     Output(component_id='games-logs-table-name', component_property='children')],
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
    global df_reg_games, df_po_games, df_ids

    if player_id != 'player_id' and season != 'year':

        url = f"https://www.basketball-reference.com/players/a/{player_id}/gamelog/{int(season.split('-')[0])+1}"

        try:
            # read all tables in the page
            tables = pd.read_html(url)
            # return only reg. season game logs
            df_reg_games = clean_df(tables[-1])

            # create dictionary for table and list with column names
            table_data = df_reg_games.to_dict('records')

            # print(df_games.columns)
            col_names = [{"name": i, "id": i} for i in df_reg_games.columns]

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
