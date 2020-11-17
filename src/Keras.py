#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 13:43:45 2020

@author: Dani
"""

# mlp for regression with mse loss function
import pandas as pd
import path
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import SGD
from matplotlib import pyplot
from keras import utils
from sklearn.metrics import r2_score

file_path = path.Path(__file__).parent / "../ANN/FinalDatasetPreparedAndNormalized.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file)

df_input = df[["f0", "f1", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10"]]
df_output = df["f2"]

X = df_input.to_numpy()
y = df_output.to_numpy()

# split into train and test
# Split into input training and test data and output training and test data
trainX, testX, trainy, testy = train_test_split(X, y, test_size=0.2)

# define model
model = Sequential()
model.add(Dense(25, input_dim=10, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(25, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(25, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(25, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(1, activation='linear'))
opt = SGD(lr=0.001, momentum=0.09)
model.compile(loss='mean_squared_error', optimizer=opt)
utils.plot_model(model, to_file = "../ANN/network.png", show_shapes=True)
# fit model
history = model.fit(trainX, trainy, validation_data=(testX, testy), epochs=2000, verbose=0)

# evaluate the model
train_mse = model.evaluate(trainX, trainy, verbose=0)
test_mse = model.evaluate(testX, testy, verbose=0)
print('Train: %.3f, Test: %.3f' % (train_mse, test_mse))

# plot loss during training
pyplot.title('Loss / Mean Squared Error')
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

y_train_pred = model.predict(trainX)
y_test_pred = model.predict(testX)

# Calculates and prints r2 score of training and testing data
print("The R2 score on the Train set is:\t{:0.3f}".format(r2_score(trainy, y_train_pred)))
print("The R2 score on the Test set is:\t{:0.3f}".format(r2_score(testy, y_test_pred)))

pyplot.figure()    
pyplot.plot(trainy, y_train_pred,'*r')
pyplot.plot(testy, y_test_pred, '*g')






