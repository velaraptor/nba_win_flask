from modeling.models import ModelingWins
import os
import pandas as pd
import requests
from pandas.io.json import json_normalize
import sqlite3
import logging
import time
import numpy as np
import json

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


def get_env():
    sql_connection = os.getenv('SQL_CONNECTION')
    time_value = os.getenv('NBA_MODEL_TIME')
    return {'SQL_CONNECTION': sql_connection, 'TIME': int(time_value)}


def get_predictions(networks, w, len_output, len_input, new_season_wins):
    new_season_predict = []
    for i in range(0, len(new_season_wins)):
        predictions = networks[0](np.array([
            (new_season_wins.iloc[i].values / w[:len_input]).astype('float32')]))[0] * w[len_input:len_output+len_input]
        prediction_array = predictions.data
        final_predictions = predictions.data[-1]
        predict_array = [new_season_wins.iloc[i].name, final_predictions, prediction_array.tolist()]
        new_season_predict.append(predict_array)
    return new_season_predict


def main():

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('nba-ml-model')
    logging.getLogger().setLevel(logging.INFO)
    env = get_env()
    time.sleep(200)
    # ns = pd.read_csv('new_season.csv')
    conn = sqlite3.connect(env['SQL_CONNECTION'])
    # ns.to_sql('history_standings', con=conn, if_exists='replace')

    history = pd.read_csv('history.csv')
    # get team names
    url = 'http://data.nba.net/'
    meta = None
    teams = None
    r = requests.get(url=url)
    if r.ok:
        meta = r.json()
    else:
        logger.warning('Could not find meta NBA data')
        logger.error(str(r.ok))
    if meta:
        teams = json_normalize(meta['sports_content']['teams']['team'])
        teams = teams[teams['is_nba_team']==True]
        teams = teams[['team_abbrev', 'team_id', 'team_nickname']]
        history = history.merge(teams, left_on='teamId', right_on='team_id')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history_standings WHERE year >= 2018')
    new_season = cursor.fetchall()
    new_season = pd.DataFrame(new_season, columns=[field[0] for field in cursor.description])
    new_season = new_season.merge(teams, left_on='teamId', right_on='team_id')

    # if meta:
    #     new_season = new_season.merge(teams, left_on='teamId', right_on='team_id')
    new_season.set_index(pd.DatetimeIndex(new_season['timestamp']), inplace=True)
    new_season_wins = new_season.groupby(['team_abbrev']).resample("7D").agg({'win': np.median}).unstack()
    logging.info(new_season_wins)
    proportion = new_season_wins.shape[1]
    random_forest = ModelingWins(history, logger, proportion)
    rfqr, w_rf, predictions_df_rf = random_forest.run_random_forest()
    neural_network = ModelingWins(history, logger, proportion)
    networks, w_n, predictions_df_nn, len_input, len_output = neural_network.run_dtw_nn(5, 50, 0.9)

    # get new data from sql and service
    # run predictions
    # get signal and two predictions and write to db
    nn_predictions_live = get_predictions(networks, w_n, len_output, len_input, new_season_wins)
    logger.info(nn_predictions_live)

    nn_predictions_live_df = pd.DataFrame(nn_predictions_live, columns=['team', 'predictions', 'array'])
    nn_predictions_live_df['array'] = nn_predictions_live_df['array'].apply(json.dumps)
    nn_predictions_live_df['user'] = nn_predictions_live_df['team'].map(TEAMS).map(PLAYERS)
    logger.info('NN Predictions')
    logger.info(nn_predictions_live_df.groupby('user')['predictions'].sum().astype(int).sort_values(ascending=False))

    y_mean = rfqr.predict(new_season_wins.iloc[:, 0:2].values)
    y_high = rfqr.predict(new_season_wins.iloc[:, 0:2].values, 85)
    y_low = rfqr.predict(new_season_wins.iloc[:, 0:2].values, 15)

    new_season_wins['high'] = y_high * w_rf[-1]
    new_season_wins['low'] = y_low * w_rf[-1]
    new_season_wins['point'] = y_mean * w_rf[-1]
    new_season_wins['team'] = new_season_wins.index
    new_season_wins['user'] = new_season_wins['team'].map(TEAMS).map(PLAYERS)
    logger.info('RF Predictions')
    logger.info(new_season_wins.groupby('user')['high'].sum().astype(int).sort_values(ascending=False))
    logger.info(new_season_wins.groupby('user')['low'].sum().astype(int).sort_values(ascending=False))
    logger.info(new_season_wins.groupby('user')['point'].sum().astype(int).sort_values(ascending=False))

    full_predictions = nn_predictions_live_df.merge(new_season_wins, left_on='team', right_on='team')
    full_predictions.columns = ['team', 'predictions', 'array', 'user', 'win',
                                'timestamp', 'high', 'low', 'point', 'user2']
    full_predictions.to_sql('ml_predictions', con=conn, if_exists='replace')
    conn.close()
    time.sleep(60 * 60 * env['TIME'])


if __name__ == "__main__":
    main()
