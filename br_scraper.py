import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_gamelogs(player_id, season, playoffs=False):
    """

    :param player_id:
    :param season:
    :param playoffs:
    :return:
    """
    if playoffs:
        selector = 'div_pgl_basic_playoffs'
    else:
        selector = 'div_pgl_basic'

    url = 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fplayers%2Fa%2F'
    url += f'{player_id}%2Fgamelog%2F{season}%2F&div={selector}'

    # request
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.table

    if table:
        df_game_logs = pd.read_html(str(table))[0]
    else:
        df_game_logs = pd.DataFrame()

    return clean_df(df_game_logs)


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


# helper functions
def html_2_table_season_stats(table):
    """
    Read HTML code tor return DataFrame
    Input:
        table- bs4 element,
    Output:
        pandas DataFrame
    """
    try:
        col_names = [_.text for _ in table.thead.findAll('th')]
        table_data = [[_.text for _ in row] for row in table.findAll('tr', {'class': 'full_table'})]
    except AttributeError:
        return pd.DataFrame()
    else:
        return pd.DataFrame(table_data, columns=col_names)


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
    # if table_rs:
    #     df_rs = pd.read_html(str(table_rs))[0]
    #     df_rs = df_rs[~df_rs.Pos.isna()]
    # else:
    #     df_rs = pd.DataFrane()
    df_rs = html_2_table_season_stats(table_rs)

    # table with play-off stats
    table_po = soup.find('table', {'id': 'playoffs_per_game'})
    df_po = html_2_table_season_stats(table_po)

    # generate list for all info about player
    player_info = [player_photo_src, player_name, mk_text]

    return df_rs, df_po, player_info
