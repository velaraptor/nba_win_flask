from datetime import datetime, timedelta
import requests
import pandas as pd
from pandas.io.json import json_normalize
import logging
import sqlite3
import os
import time


def get_env():
    sql_connection = os.getenv('SQL_CONNECTION', '/Users/velaraptor/Desktop/nba_win.db')
    time_value = os.getenv('RAW_STANDINGS_TIME', 0)
    return {'SQL_CONNECTION': sql_connection, 'TIME': int(time_value)}


def get_standings(logger):
    logger.info('Getting standings')
    i = 0
    start_date = datetime.strptime('10/28/2014', '"%m/%d/%Y"')
    date_now = str(start_date.year) + str(start_date.month) + str(start_date.day + i)
    url = 'http://data.nba.net/data/10s/prod/v1/' + date_now + '/standings_all.json'
    r = requests.get(url=url)
    if r.ok:
        i += 1
        logger.info('going back ' + str(i) + ' day')
        date_now = str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day - i)
        url = 'http://data.nba.net/data/10s/prod/v1/' + date_now + '/standings_all.json'
        r = requests.get(url=url)

    standings = r.json()
    return standings


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('nba-win-api')
    logging.getLogger().setLevel(logging.INFO)
    env = get_env()
    logger.info('Getting standings')
    sleep_time = 20
    # check if table is not empty 
    for i in range(0, 300):
        start_date = datetime.strptime('10/16/2018', '%m/%d/%Y') + timedelta(days=i)
        if start_date == datetime.now():
            sleep_time = 60 * 60 * 24
            logger.info('Same day')

        logger.info('Data current as of: ' + str(start_date))
        date_now = str(start_date.year) + str(start_date.strftime("%m")) + str(start_date.strftime("%d"))
        logger.info(date_now)
        url = 'http://data.nba.net/data/10s/prod/v1/' + date_now + '/standings_all.json'
        try:
            r = requests.get(url=url)
            standings = r.json()
        except requests.exceptions.Timeout:
            time.sleep(60 * 60)
            continue
        except requests.exceptions.TooManyRedirects:
            time.sleep(60 * 60)
            continue
        except requests.exceptions.RequestException as e:
            logger.warning(e)
            time.sleep(60 * 60)
            continue

        year = standings["league"]['standard']['seasonYear']
        status_id = standings["league"]['standard']['seasonStageId']
        standings = standings["league"]['standard']['teams']

        standings = json_normalize(standings)
        standings = standings[['win', 'loss', 'teamId']]
        standings['teamId'] = standings['teamId'].astype(int)
        standings['win'] = standings['win'].astype(int)
        standings['loss'] = standings['loss'].astype(int)
        standings.loc[:, 'timestamp'] = start_date
        standings['timestamp'] = pd.to_datetime(standings['timestamp'])
        standings.loc[:, 'year'] = year
        standings.loc[:, 'status_id'] = status_id
        logger.info(standings)

        conn = sqlite3.connect(env['SQL_CONNECTION'])
        if i > 0:
            standings.to_sql('history_standings', con=conn, if_exists='append')
        else:
            standings.to_sql('history_standings', con=conn, if_exists='replace')
            logger.info('New table written')
        logger.info('successfully wrote to db')
        conn.close()
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
