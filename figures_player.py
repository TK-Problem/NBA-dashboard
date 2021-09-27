import plotly.express as px


def mp_vs_pts(df):
    """

    :param df: pandas DataFrame
    :return:
    """
    # filter out games where he did not play
    df = df.loc[df.MP.apply(lambda x: True if len(x.split(":")) == 2 else False)].reset_index(drop=True)
    df['MP'] = df['MP'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
    df['MP'] = df['MP'].astype(float).round(1)
    df['PTS'] = df['PTS'].astype(int)

    return px.scatter(df, x="MP", y="PTS")


fig_dict = {'Minutes played vs points scored.': mp_vs_pts}
