from models import ModelingWins
import os
import pandas as pd
import requests
from pandas.io.json import json_normalize
import sqlite3
import logging


def get_env():
    sql_connection = os.getenv('SQL_CONNECTION')
    time_value = os.getenv('NBA_WIN_TIME')
    return {'SQL_CONNECTION': sql_connection, 'TIME': int(time_value)}


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('nba-ml-model')
    logging.getLogger().setLevel(logging.INFO)
    env = get_env()
    conn = sqlite3.connect(env['SQL_CONNECTION'])

    history = pd.read_csv('history.csv')
    # get team names
    url = 'http://data.nba.net/'
    meta = None
    r = requests.get(url=url)
    if r.ok:
        meta = r.json()
    else:
        logger.warning('Could not find meta NBA data')
        logger.error(str(r.ok))
    if meta:
        teams = json_normalize(meta['sports_content']['teams']['team'])
        teams = teams[teams['is_nba_team'] == True]
        teams = teams[['team_abbrev', 'team_id', 'team_nickname']]
        history = history.merge(teams, left_on='teamId', right_on='team_id')

    proportion = 2
    random_forest = ModelingWins(history, logger, proportion)
    rfqr, w_rf, predictions_df_rf = random_forest.run_random_forest()
    neural_network = ModelingWins(history, logger, proportion)
    networks, w_n, predictions_df_nn = neural_network.run_dtw_nn(5, 50, 0.9)

    # get new data from sql and service
    # run predictions
    # get signal and two predictions and write to db


if __name__ == "__main__":
    main()
