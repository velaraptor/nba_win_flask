import numpy as np
from chainer import Chain
import chainer.functions as F
import chainer.links as L

from sdtw.chainer_func import SoftDTWLoss


def split_time_series(X_tr, X_te, proportion=0.6):
    len_ts = X_tr.shape[1]
    len_input = int(proportion)
    len_output = len_ts - len_input

    return np.float32(X_tr[:, :len_input]), \
        np.float32(X_tr[:, len_input:]), \
        np.float32(X_te[:, :len_input]), \
        np.float32(X_te[:, len_input:])


class MLP(Chain):
    def __init__(self, len_input, len_output, activation="tanh", n_units=50):
        self.activation = activation

        super(MLP, self).__init__(
            mid = L.Linear(len_input, n_units),
            out = L.Linear(n_units, len_output),
        )

    def __call__(self, x):
        # Given the current observation, predict the rest.
        xx = self.mid(x)
        func = getattr(F, self.activation)
        h = func(xx)
        y = self.out(h)
        return y


class Objective(Chain):
    def __init__(self, predictor, loss="euclidean", gamma=1.0):
        self.loss = loss
        self.gamma = gamma
        super(Objective, self).__init__(predictor=predictor)

    def __call__(self, x, t):
        y = self.predictor(x)

        if self.loss == "euclidean":
            return F.mean_squared_error(y, t)

        elif self.loss == "sdtw":
            loss = 0
            for i in range(y.shape[0]):
                y_i = F.reshape(y[i], (-1,1))
                t_i = F.reshape(t[i], (-1,1))
                loss += SoftDTWLoss(self.gamma)(y_i, t_i)
            return loss

        else:
            raise ValueError("Unknown loss")



