import pandas as pd
import requests
from datetime import datetime
import time
import sqlite3
import logging
import pytz

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
RUN_SQL = True
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

SQL_CONNECTION = "/var/data/nba_win.db"


def get_scores(logger):
    logger.info('Getting live scores')
    games = None
    clean_games = []
    i = 0
    date_now = str(datetime.now(pytz.timezone('US/Central')).year) + str(
        datetime.now(pytz.timezone('US/Central')).month) + str(datetime.now(pytz.timezone('US/Central')).day - i)
    url = 'http://data.nba.net/data/10s/prod/v2/' + date_now + '/scoreboard.json'
    r = requests.get(url=url)
    if r.ok:
        games = r.json().get('games', None)

    if games:
        for g in games:
            clean_game = {'status': g['statusNum'],
                          'game_activated': g['isGameActivated'],
                          'current_period': g['period']['current'],
                          'isHalftime': g['period']['isHalftime'],
                          'vTeam': g['vTeam']['triCode'],
                          'hTeam': g['hTeam']['triCode'],
                          'vTeamScore': g['vTeam']['score'],
                          'hTeamScore': g['hTeam']['score']
                          }
            print(clean_game)
            clean_games.append(clean_game)

    return pd.DataFrame(clean_games)


def main():
    logging.basicConfig()

    logger = logging.getLogger('nba-scores-api')
    logging.getLogger().setLevel(logging.INFO)

    while True:
        scores = get_scores(logger)
        scores['hUser'] = scores['hTeam'].map(TEAMS).map(PLAYERS)
        scores['vUser'] = scores['vTeam'].map(TEAMS).map(PLAYERS)

        if RUN_SQL is True:
            conn = sqlite3.connect(SQL_CONNECTION)
            scores.to_sql('scores', con=conn, if_exists='replace')
            logger.info('successfully wrote to db')
        logger.info('Sleep for 4 Minutes')
        time.sleep(4 * 60)


if __name__ == "__main__":
    main()
