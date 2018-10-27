import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import sqlite3
import logging
import pytz
import os

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


def get_env():
    sql_connection = os.getenv('SQL_CONNECTION')
    time_value = os.getenv('LIVE_SCORE_TIME')
    return {'SQL_CONNECTION': sql_connection, 'TIME': int(time_value)}


def get_scores(logger):
    logger.info('Getting live scores')
    games = None
    clean_games = []
    i = 0
    date_now = datetime.now(pytz.timezone('US/Pacific')) - timedelta(days=i)
    date_now = str(date_now.year) + str(date_now.strftime("%m")) + str(date_now.strftime("%d"))
    url = 'http://data.nba.net/data/10s/prod/v2/' + date_now + '/scoreboard.json'
    r = requests.get(url=url)
    if r.ok:
        games = r.json().get('games', None)
    else:
        logging.warning('Could not find meta NBA data')
        logging.warning(str(r.ok))

    if games:
        for g in games:
            clean_game = {'status': g['statusNum'],
                          'game_activated': g['isGameActivated'],
                          'current_period': g['period']['current'],
                          'isHalftime': g['period']['isHalftime'],
                          'vTeam': g['vTeam']['triCode'],
                          'hTeam': g['hTeam']['triCode'],
                          'vTeamScore': g['vTeam']['score'],
                          'hTeamScore': g['hTeam']['score'],
                          'clock': g['clock']
                          }
            print(clean_game)
            clean_games.append(clean_game)

    return pd.DataFrame(clean_games)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('nba-scores-api')
    logging.getLogger().setLevel(logging.INFO)
    env = get_env()
    while True:
        scores = get_scores(logger)
        scores['hUser'] = scores['hTeam'].map(TEAMS).map(PLAYERS)
        scores['vUser'] = scores['vTeam'].map(TEAMS).map(PLAYERS)

        if RUN_SQL is True:
            conn = sqlite3.connect(env['SQL_CONNECTION'])
            scores.to_sql('scores', con=conn, if_exists='replace')
            logger.info('successfully wrote to db')

        logger.info('Sleeping for ' + str(env['TIME']) + ' minutes....')
        time.sleep(60 * env['TIME'])


if __name__ == "__main__":
    main()
