from dash import dcc, no_update, html
from dash.dependencies import Input, Output
from dash import dash_table

import dash_bootstrap_components as dbc

from app import app
from utils import navbar, footer
from br_scraper import get_gamelogs, get_season_stats

import pandas as pd


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
            placeholder="Select season"
            ),
    ])
])

# player info card
card_p_info = dbc.Card([
        dbc.Row([

            dbc.Col(html.Img(id='player-photo', src=''), align="center", sm=3),

            dbc.Col([
                html.H4(children="", id="card-title-player-name", className="card-title"),
                dcc.Markdown(children="", id='player-text-info')
            ], sm=7),
        ], justify="center"),
    ])

# player season stats card
card_p_seasons = dbc.Card([

        dbc.Tabs([
            dbc.Tab(
                dash_table.DataTable(
                    id='player-reg-season-games-table',
                    columns=[],
                    data=[{}],
                    page_size=5),
                label='Regular season avg. stats'),

            dbc.Tab(
                dash_table.DataTable(
                    id='player-po-games-table',
                    columns=[],
                    data=[{}],
                    page_size=5),
                label='Play-off avg. stats')
            ])
    ])

# game-log card
game_log_tabs = dbc.Tabs([

    dbc.Tab([
        dash_table.DataTable(
            id='reg_s_game-logs-table',
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

    dbc.Tab([
        dash_table.DataTable(
            id='po_game-logs-table',
            data=[{}],
            columns=[],
            style_table={'overflowX': 'auto'},
            style_cell={
                    'minWidth': '30px', 'width': '60px', 'maxWidth': '120px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
            },
            page_size=20)],
            label='Play-offs game-logs'),
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
    Output(component_id='player-photo', component_property='src'),
    Output(component_id='card-title-player-name', component_property='children'),
    Output(component_id='player-text-info', component_property='children'),
    Output(component_id='player-reg-season-games-table', component_property='columns'),
    Output(component_id='player-reg-season-games-table', component_property='data'),
    Output(component_id='player-po-games-table', component_property='columns'),
    Output(component_id='player-po-games-table', component_property='data')
],
    Input(component_id='player-id-drop', component_property='value'))
def update_year_dropdown(player_id):
    global df_reg_s, df_po_s
    """
    Returns year range, e.g. from 1991 to 1997, for year drop down menu
    :param player_id: string
    :return:
        * list with dictionary inside, e.g.
        [{'label': 1991-1992, 'value': 1991-1992}, {'label': 1992-1993, 'value': 1992-1993}],
        * string, url link to image source,
        * string, player name,
        * string, extra info about player as markdown text,
        * list,
        * list,
        * list,
        * list,
    """
    global df_reg_s, df_po_s

    # if invalid name inputted apply no changes
    if player_id == 'player_id':
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    else:
        # regular season game stats
        df_reg_s, df_po_s, player_info = get_season_stats(player_id)

        # extract values
        player_photo_src = player_info[0]
        player_name = player_info[1]
        mk_text = player_info[2]

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

        # format column names for dash
        col_names = [{"name": i, "id": i} for i in col_names]

        # seasons played for dropdown menu
        season = [{'label': _, 'value': _} for _ in df_reg_s.Season]

        return season, player_photo_src, player_name, mk_text, col_names, table_data_reg, col_names, table_data_po


@app.callback([
    Output(component_id='reg_s_game-logs-table', component_property='columns'),
    Output(component_id='reg_s_game-logs-table', component_property='data'),
    Output(component_id='po_game-logs-table', component_property='columns'),
    Output(component_id='po_game-logs-table', component_property='data')
],
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
        # get reg. season and playoff (if available) game logs
        df_reg_games = get_gamelogs(player_id, int(season.split('-')[0])+1)
        df_po_games = get_gamelogs(player_id, int(season.split('-')[0])+1, True)

        # create dictionary for table and list with column names
        table_data_rs = df_reg_games.to_dict('records')
        col_names_rs = [{"name": i, "id": i} for i in df_reg_games.columns]

        # create dictionary for table and list with column names
        table_data_po = df_po_games.to_dict('records')
        col_names_po = [{"name": i, "id": i} for i in df_po_games.columns]

        return col_names_rs, table_data_rs, col_names_po, table_data_po
    else:
        # no updates if input is not full
        return no_update, no_update, no_update, no_update
