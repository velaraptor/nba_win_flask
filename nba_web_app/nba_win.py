from flask import Flask, render_template
import sqlite3
import pandas as pd
import os
from bokeh.models import ColumnDataSource, HoverTool
import ast
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
pd.set_option('display.max_colwidth', -1)

GAME_STATUS = {
    1: "Has not began",
    2: 'In progress',
    3: 'FINAL'
}

PLAYERS = {0: 'Chris',
           1: 'Luke',
           2: 'Dennis',
           3: 'Noe',
           4: 'Marc',
           5: 'Ryne',
           6: 'Dom',
           7: 'Jason',
           8: 'Nick',
           9: 'Luis'
           }
TEAMS = {'TOR': 0, 'PHX': 0, 'IND': 0,
         'GSW': 1, 'DET': 1, 'ORL': 1,
         'BOS': 2, 'CHA': 2, 'SAC': 2,
         'NOP': 3, 'PHI': 3, 'CLE': 3,
         'MEM': 4, 'MIL': 4, 'ATL': 4,
         'HOU': 5, 'MIA': 5, 'NYK': 5,
         'UTA': 6, 'DEN': 6, 'CHI': 6,
         'LAL': 7, 'MIN': 7, 'BKN': 7,
         'SAS': 8, 'POR': 8, 'LAC': 8,
         'OKC': 9, 'WAS': 9, 'DAL': 9
         }

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


def get_team_images():
    df = pd.DataFrame({'Images': ['http://a.espncdn.com/i/teamlogos/nba/500/bos.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/lal.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/gsw.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/utah.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/okc.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/ind.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/hou.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/dal.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/phi.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/mil.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/orl.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/mia.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/cle.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/min.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/den.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/por.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/mem.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/was.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/tor.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/nyk.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/bkn.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/no.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/phx.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/atl.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/cha.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/sac.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/det.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/chi.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/lac.png',
                                  'http://a.espncdn.com/i/teamlogos/nba/500/sas.png'
                                  ], 'Abr': ['BOS', 'LAL', 'GSW', 'UTA', 'OKC', 'IND', 'HOU',
                                             'DAL', 'PHI', 'MIL', 'ORL', 'MIA', 'CLE', 'MIN',
                                             'DEN', 'POR', 'MEM', 'WAS', 'TOR', 'NYK', 'BKN',
                                             'NOP', 'PHX', 'ATL', 'CHA', 'SAC', 'DET', 'CHI', 'LAC', 'SAS']})
    df['users'] = df['Abr'].map(TEAMS).map(PLAYERS)
    images = df.groupby('users')['Images'].apply(' '.join).reset_index()
    imag = images['Images'].str.split(expand=True)

    imag['users'] = images['users']
    imag.columns = ['Team1', 'Team2', 'Team3', 'Player']
    return imag


def get_sql_connection():
    return os.getenv('SQL_CONNECTION')


def path_to_image_html(path):
    return '<center><img src="' + path + '"  width="100" height="100" /></center>'


def path_to_more_stats_html(path):
    return '<center><font size=5><a href="/gaes_teams/' + path + '">' + path + '</a></font></center>'


def center_font_size(path):
    return '<font size=5><center>' + str(path) + '</font></font></center>'


def losses(path):
    return '<b><font color="#AEA79F"><font size=5><center>' + str(path) + '</font></font></center></b>'


def make_row_bold(path):
    return '<b><font color="#46b957"><font size=5><center>' + str(path) + '</font></font></center></b>'


@app.route("/")
def main():
    conn = sqlite3.connect(get_sql_connection())
    cursor = conn.cursor()
    cursor.execute('SELECT usr, win, loss, win_percentage, weighted_rank, raw_rank FROM'
                   ' standings ORDER BY win DESC, win_percentage DESC')
    scores = cursor.fetchall()
    scores = pd.DataFrame(scores, columns=['Player', 'Wins', 'Losses', 'Win PCT', 'Weighted Rank', 'Raw Rank'])
    scores['Win PCT'] = round(scores['Win PCT'], 2)
    cursor.execute('SELECT timestamp FROM standings')
    recent_date = cursor.fetchone()[0]
    recent_date = pd.to_datetime(recent_date)
    recent_date = 'Data recent as of ' + str(recent_date.strftime('%c'))

    team_images = get_team_images()
    scores = scores.merge(team_images, left_on='Player', right_on='Player')

    cursor.execute('SELECT * FROM scores')
    scores_live = cursor.fetchall()
    scores_live = pd.DataFrame(scores_live, columns=[field[0] for field in cursor.description])
    scores_live = scores_live[['hUser', 'vUser', 'vTeamScore', 'vTeam', 'status', 'hTeamScore', 'hTeam',
                               'game_activated', 'current_period', 'clock']]

    scores_live['game'] = scores_live['hUser'] + ' (' + scores_live['hTeam'] + ') - <b>' + \
        scores_live['hTeamScore'] + '</b> <br> ' + scores_live['vUser'] + \
        ' (' + scores_live['vTeam'] + ') - <b>' + scores_live['vTeamScore'] + '</b>'
    scores_live['status'] = scores_live['status'].map(GAME_STATUS)

    scores_live = scores_live[['game', 'current_period', 'status', 'clock']]
    scores_live.columns = ['Game', 'Current Period', 'Status', 'Time Left']
    scores_live.loc[scores_live['Current Period'] >= 5, 'Current Period'] = 'OT'
    return render_template('view.html',
                           tables=[scores.to_html(index=False, classes=['table table-hover', 'table-light'],
                                                  formatters={'Team1': path_to_image_html,
                                                              'Team2': path_to_image_html,
                                                              'Team3': path_to_image_html,
                                                              'Player': path_to_more_stats_html,
                                                              'Wins': make_row_bold,
                                                              'Losses': losses,
                                                              'Win PCT': center_font_size,
                                                              'Weighted Rank': center_font_size,
                                                              'Raw Rank': center_font_size},
                                                  escape=False,
                                                  table_id='wins',
                                                  justify='center',
                                                  border=3).replace('<th>', '<th class = "table-info">'), ],
                           recent_date=recent_date,
                           scores_live=[scores_live.to_html(index=False, classes=['table table-hover', 'table-light'],
                                                            escape=False,
                                                            justify='center',
                                                            table_id='live_scores',
                                                            border=3).replace('<th>', '<th class = "table-info">'), ])


@app.route('/gaes_teams/<variable>', methods=['GET'])
def get_team_records(variable):
    conn = sqlite3.connect(get_sql_connection())
    cursor = conn.cursor()

    cursor.execute('SELECT win, loss, win_percentage, weighted_rank, raw_rank FROM standings WHERE usr =\'%s\'' %
                   variable)
    agg_scores = cursor.fetchall()
    agg_scores = pd.DataFrame(agg_scores, columns=['Wins', 'Losses', 'Win PCT', 'Weighted Rank', 'Raw Rank'])
    agg_scores['Win PCT'] = round(agg_scores['Win PCT'], 2)
    cursor.execute('SELECT win, loss, team_nickname FROM standings_raw_single WHERE usr=\'%s\'' % variable)
    by_team_scores = cursor.fetchall()
    by_team_scores = pd.DataFrame(by_team_scores, columns=['Wins', 'Losses', 'Team Name'])
    team_images = get_team_images()
    team_images = team_images[team_images['Player'] == variable]
    team_1 = str(team_images['Team1'].values[0])
    team_2 = str(team_images['Team2'].values[0])
    team_3 = str(team_images['Team3'].values[0])
    rank = int(agg_scores['Raw Rank'].values[0])
    return render_template("team.html", team_table=[by_team_scores.to_html(index=False, classes=['table table-hover',
                                                                                                 'table-light'],
                                                                           formatters={'Wins': make_row_bold,
                                                                                       'Losses': losses,
                                                                                       'Team Name': center_font_size},
                                                                           escape=False, justify='center', border=3
                                                                           ).replace('<th>',
                                                                                     '<th class = "table-info">'), ],
                           agg_table=[agg_scores.to_html(index=False, classes=['table table-hover', 'table-light'],
                                                         escape=False,
                                                         justify='center',
                                                         border=3).replace('<th>', '<th class = "table-info">'), ],
                           name=variable, team_1=team_1, team_2=team_2, team_3=team_3, rank=rank)


@app.route('/predictions')
def get_predictions():
    conn = sqlite3.connect(get_sql_connection())
    cursor = conn.cursor()
    cursor.execute('SELECT team, predictions, actual_array, array, high, point, low, user FROM ml_predictions')
    predictions = cursor.fetchall()
    predictions = pd.DataFrame(predictions, columns=[field[0] for field in cursor.description])

    user_predictions = pd.DataFrame(predictions.groupby('user')['predictions'].sum().sort_values(ascending=False))

    pp = predictions['actual_array'].apply(ast.literal_eval) + predictions['array'].apply(ast.literal_eval).values

    pp = pd.DataFrame([g for g in pp])
    x_values = pd.DataFrame([np.arange(1, pp.shape[1] + 1) for g in range(0, 30)])
    data = {'xs': x_values.values.tolist(),
            'ys': pp.values.tolist(),
            'labels': predictions['team'].values,
            'colors': ['#e21a37', '#000000', '#00611b', '#00848e', '#b00203', '#860038', '#006bb6', '#0e2240',
                       '#fa002c',
                       '#003399', '#cd212b', '#ffb517', '#ed174b', '#fdba33', '#5d76a9', '#98002e', '#00471b',
                       '#2b6291',
                       '#0c2340', '#f58426', '#002d62', '#0077c0', '#ef0022', '#e76221', '#cc0000', '#51388a',
                       '#959191', '#bd1b21',
                       '#f9a11e', '#cf142b']}

    source = ColumnDataSource(data)

    p = figure(plot_width=400, plot_height=400)
    p.toolbar.logo = None
    p.sizing_mode = 'stretch_both'
    p.multi_line(xs='xs', ys='ys', source=source, line_color='colors', line_width=2)
    p.add_tools(HoverTool(show_arrow=True, line_policy='nearest', tooltips=[('Team', '@labels'), ('Wins', '$y'), ('Week', '$x') ]))
    script, div = components(p)
    return render_template('plots.html',
                           tables=[predictions[['team', 'predictions', 'high', 'point', 'low', 'user']].to_html(index=False,
                                                       escape=False,justify='center',
                                                         border=3,
                                                       classes=['table table-hover', 'table-light']), ],
                           user_table=[user_predictions.to_html(justify='center',
                                                         border=3, escape=False, classes=['table table-hover', 'table-light']), ],
                           script=script, div=div)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
