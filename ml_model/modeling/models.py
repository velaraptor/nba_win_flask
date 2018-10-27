import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from skgarden import RandomForestQuantileRegressor
from modeling.soft_dtw import split_time_series
from modeling.soft_dtw import MLP, Objective
from chainer import training
from chainer import iterators, optimizers
from chainer.datasets import tuple_dataset


class ModelingWins:
    def __init__(self, train_data, logger, proportion):
        self.__df_train = train_data
        self.__proportion = proportion
        self.__test_size = 0.05
        self.__logging = logger
        self.__model = None

    def prep_train_data(self):
        history = self.__df_train
        history.set_index(pd.DatetimeIndex(history['timestamp']), inplace=True)

        his = history.groupby('year')
        history_groups = [his.get_group(x) for x in his.groups]
        values_list = []
        for group in history_groups:
            values = group.groupby(['team_abbrev']).resample("7D").agg({'win': np.median}).unstack()
            values_list.append(pd.DataFrame(values.values))

        values = pd.concat(values_list).iloc[:, 0:25]
        values.reset_index(inplace=True, drop=True)
        w1 = np.sqrt(sum(values.values ** 2))
        x_norm_win = values / w1
        return x_norm_win, w1

    def run_random_forest(self):
        x_norm2, w = self.prep_train_data()
        x_train, x_test = train_test_split(x_norm2, test_size=self.__test_size)
        x_tr = x_train.values
        x_te = x_test.values
        x_tr, y_tr, x_te, y_te = split_time_series(x_tr, x_te, self.__proportion)

        train_y = []
        for y in y_tr:
            train_y.append(y[-1])

        rfqr = RandomForestQuantileRegressor(random_state=0, min_samples_split=2, n_estimators=100, criterion='mae')
        rfqr.fit(x_tr, train_y)

        test_y = []
        for y in y_te:
            test_y.append(np.float(y[-1]))

        y_mean_test = rfqr.predict(x_te)
        y_high_test = rfqr.predict(x_te, 85)
        y_low_test = rfqr.predict(x_te, 15)

        test_predictions = pd.DataFrame({'high': y_high_test * w[-1],
                                         'low': y_low_test * w[-1],
                                         'point': y_mean_test * w[-1],
                                         'actual': np.array(test_y) * w[-1]})
        test_predictions['id'] = np.arange(0, len(test_predictions))
        self.__logging.info(test_predictions)
        self.__model = rfqr
        return rfqr, w, test_predictions

    @staticmethod
    def train(network, loss, X_tr, Y_tr, X_te, Y_te, n_epochs=30, gamma=1):
        model = Objective(network, loss=loss, gamma=gamma)

        # optimizer = optimizers.SGD()
        optimizer = optimizers.Adam()
        optimizer.setup(model)

        train = tuple_dataset.TupleDataset(X_tr, Y_tr)
        test = tuple_dataset.TupleDataset(X_te, Y_te)

        train_iter = iterators.SerialIterator(train, batch_size=1, shuffle=True)
        test_iter = iterators.SerialIterator(test, batch_size=1, repeat=False,
                                             shuffle=False)
        updater = training.StandardUpdater(train_iter, optimizer)
        trainer = training.Trainer(updater, (n_epochs, 'epoch'))

        trainer.run()

    def run_dtw_nn(self, n_units, n_epochs, gamma):
        x_norm2, w = self.prep_train_data()
        x_train, x_test = train_test_split(x_norm2, test_size=self.__test_size)

        warm_start = True
        X_tr = x_train.values
        X_te = x_test.values

        X_tr, Y_tr, X_te, Y_te = split_time_series(X_tr, X_te, self.__proportion)

        len_input = X_tr.shape[1]
        len_output = Y_tr.shape[1]

        networks = [MLP(len_input, len_output, n_units=n_units), ]
        losses = ["sdtw", ]

        for i in range(len(networks)):
            if warm_start and i >= 1:
                # Warm-start with Euclidean-case solution
                networks[i].mid = copy.deepcopy(networks[0].mid)
                networks[i].out = copy.deepcopy(networks[0].out)

            self.train(networks[i], losses[i], X_tr, Y_tr, X_te, Y_te, n_epochs=n_epochs, gamma=gamma)

        error_list = []
        predictions = []
        actuals = []
        for i in range(X_te.shape[0]):
            error = networks[0](np.array([X_te[i]]))[0] * w[len_input:len_output + len_input] - \
                    Y_te[i] * w[len_input:len_output + len_input]
            prediction = networks[0](np.array([X_te[i]]))[0] * w[len_input:len_output + len_input]
            actual = Y_te[i] * w[len_input:len_output + len_input]
            actuals.append(actual.data[-1])
            predictions.append(prediction.data[-1])
            self.__logging.info(np.round(error.data, 2))
            error_list.append(np.median(error.data))
        predictions_df = pd.DataFrame({'predictions': predictions, 'actual': actuals})
        self.__logging.info(predictions_df)

        return networks, w, predictions_df, len_input, len_output
