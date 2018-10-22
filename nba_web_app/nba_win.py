from flask import Flask, render_template
import sqlite3
import pandas as pd

SQL_CONNECTION = "/var/data/nba_win.db"
# SQL_CONNECTION_local = "/Users/velaraptor/Desktop/nba_win.db"
pd.set_option('display.max_colwidth', -1)

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


def path_to_image_html(path):
    return '<img src="' + path + '"  width="100" height="100" />'


def path_to_more_stats_html(path):
    return '<a href="/gaes_teams/' + path + '">' + path + '</a>'


def make_row_bold(path):
    return '<b><font color="#46b957">' + str(path) + '</font></b>'


@app.route("/")
def main():
    conn = sqlite3.connect(SQL_CONNECTION)
    cursor = conn.cursor()
    cursor.execute('SELECT usr, win, loss, win_percentage, weighted_rank, raw_rank FROM standings')
    scores = cursor.fetchall()
    scores = pd.DataFrame(scores, columns=['Player', 'Wins', 'Losses', 'Win PCT', 'Weighted Rank', 'Raw Rank'])
    cursor.execute('SELECT timestamp FROM standings')
    recent_date = cursor.fetchone()[0]
    recent_date = pd.to_datetime(recent_date)
    recent_date = 'Data recent as of ' + str(recent_date.strftime('%c'))

    team_images = get_team_images()
    scores = scores.merge(team_images, left_on='Player', right_on='Player')
    return render_template('view.html',
                           tables=[scores.to_html(index=False, classes=['table table-hover', 'table-light'],
                                                  formatters=dict(Team1=path_to_image_html,
                                                                  Team2=path_to_image_html,
                                                                  Team3=path_to_image_html,
                                                                  Player=path_to_more_stats_html,
                                                                  Wins=make_row_bold),
                                                  escape=False, justify='center', border=3), ],
                           recent_date=recent_date)


@app.route('/gaes_teams/<variable>', methods=['GET'])
def get_team_records(variable):
    conn = sqlite3.connect(SQL_CONNECTION)
    cursor = conn.cursor()

    cursor.execute('SELECT win, loss, win_percentage, weighted_rank, raw_rank FROM standings WHERE usr =\'%s\'' %
                   variable)
    agg_scores = cursor.fetchall()
    agg_scores = pd.DataFrame(agg_scores, columns=['Wins', 'Losses', 'Win PCT', 'Weighted Rank', 'Raw Rank'])

    cursor.execute('SELECT win, loss, team_nickname FROM standings_raw_single WHERE usr=\'%s\'' % variable)
    by_team_scores = cursor.fetchall()
    by_team_scores = pd.DataFrame(by_team_scores, columns=['Wins', 'Losses', ' Team Name'])
    team_images = get_team_images()
    team_images = team_images[team_images['Player']==variable]
    team_1 = str(team_images['Team1'].values[0])
    team_2 = str(team_images['Team2'].values[0])
    team_3 = str(team_images['Team3'].values[0])
    rank = int(agg_scores['Raw Rank'].values[0])
    return render_template("team.html", team_table=[by_team_scores.to_html(index=False, classes=['table table-hover',
                                                                                                 'table-light'],
                                                                           escape=False, justify='center', border=3), ],
                           agg_table=[agg_scores.to_html(index=False, classes=['table table-hover', 'table-light'],
                                                         escape=False,
                                                         justify='center', border=3), ],
                           name=variable, team_1=team_1, team_2=team_2, team_3=team_3, rank=rank)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
