#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 20:58:44 2020

@author: Dani
"""

import path
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from matplotlib import pyplot

file_path = path.Path(__file__).parent / "../ANN/FinalDatasetPrepared.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file)

# Split into input (X) and output (y) variables
X = df[["Latitude", "Longitude", "WaitingCount", "MooredCount", "type", "built", "dwt", "loa", "beam", "draughtMeters"]]
y= df[["FullWaitTime"]]
print(X)
print(y)

X = X.values
y= y.values

def baseline_model():
    model = Sequential()
    model.add(Dense(10, input_dim=10, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

# evaluate model
estimator = KerasRegressor(build_fn=baseline_model, epochs=100, batch_size=100, verbose=1)
kfold = KFold(n_splits=5)
results = cross_val_score(estimator, X, y, cv=kfold)
print("Baseline: %.2f (%.2f) MSE" % (results.mean(), results.std()))

pyplot.title('Loss / Mean Squared Error')
pyplot.plot(results, label='result')
pyplot.legend()
pyplot.show()

print(results)




    