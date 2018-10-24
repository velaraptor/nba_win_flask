import pandas as pd
from pandas.io.json import json_normalize
import requests
from datetime import datetime
import time
import sqlite3
import logging
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
    time_value = os.getenv('NBA_WIN_TIME')
    return {'SQL_CONNECTION': sql_connection, 'TIME': int(time_value)}


def get_standings(logger):
    logger.info('Getting standings')
    i = 0
    date_now = str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day - i)
    url = 'http://data.nba.net/data/10s/prod/v1/' + date_now + '/standings_all.json'
    r = requests.get(url=url)
    while not r.ok:
        i += 1
        logger.info('going back ' + str(i) + ' day')
        date_now = str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day - i)
        url = 'http://data.nba.net/data/10s/prod/v1/' + date_now + '/standings_all.json'
        r = requests.get(url=url)

    standings = r.json()
    return standings


def main():
    logging.basicConfig()

    logger = logging.getLogger('nba-win-api')
    logging.getLogger().setLevel(logging.INFO)
    env = get_env()
    while True:
        standings = get_standings(logger)
        recent_date = standings['_internal'].get('pubDateTime', datetime.now())
        logger.info('Data current as of: ' + recent_date)
        standings = standings["league"]['standard']['teams']

        standings = json_normalize(standings)
        standings = standings[['win', 'loss', 'teamId']]
        standings['teamId'] = standings['teamId'].astype(int)
        standings['win'] = standings['win'].astype(int)
        standings['loss'] = standings['loss'].astype(int)

        url = 'http://data.nba.net/'
        r = requests.get(url=url)
        if r.ok:
            meta = r.json()
        else:
            logging.warning('Could not find meta NBA data')
            logging.warning(str(r.ok))
            continue

        teams = json_normalize(meta['sports_content']['teams']['team'])
        teams = teams[teams['is_nba_team']==True]
        teams = teams[['team_abbrev', 'team_id', 'team_nickname']]

        standings = standings.merge(teams, left_on='teamId', right_on='team_id')

        standings.loc[:, 'usr'] = standings['team_abbrev'].map(TEAMS).map(PLAYERS)

        standings_agg = standings.groupby('usr')[['win', 'loss']].sum().sort_values(ascending=False, by='win')
        standings_agg['win_percentage'] = standings_agg['win'] / (standings_agg['win'] + standings_agg['loss'])
        standings_agg['weighted_rank'] = standings_agg['win_percentage'].rank(ascending=False)
        standings_agg['raw_rank'] = standings_agg['win'].rank(ascending=False)
        standings_agg.loc[:, 'timestamp'] = recent_date
        standings_agg['timestamp'] = pd.to_datetime(standings_agg['timestamp'])
        standings_agg['user_name'] = standings_agg.index
        logger.info(standings_agg)
        if RUN_SQL is True:
            conn = sqlite3.connect(env['SQL_CONNECTION'])
            standings_agg.to_sql('standings', con=conn, if_exists='replace')
            logger.info('successfully wrote to db')
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp FROM standings_history')
            times = cursor.fetchall()
            if len(times) > 0:
                times = pd.to_datetime(pd.DataFrame(times)[0])
                if sum(standings_agg['timestamp'].isin(times)) == 0:
                    logger.info('wrote to standing_history table')
                    standings_agg.to_sql('standings_history', con=conn, if_exists='append')
            else:
                logger.info('new iteration putting data in standing_history')
                standings_agg.to_sql('standings_history', con=conn, if_exists='append')

        logger.info('Sleeping for ' + str(env['TIME']) + ' minutes....')
        time.sleep(60 * env['TIME'])


if __name__ == "__main__":
    main()
