#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 19:08:28 2020

@author: Dani
"""

import path

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

import pandas as pd

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from matplotlib import pyplot as plt
#%matplotlib inline
#%config InlineBackend.figure_format='retina'

file_path = path.Path(__file__).parent / "../GeneratedDataset/FinalDatasetWorldWide.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file)

# Split into input (X) and output (y) variables
X = df[["Latitude", "Longitude", "built", "dwt", "loa", "beam", "draughtMeters"]]
y= df[["WaitTime"]]

# Split into input training and test data and output training and test data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

#
X_train = preprocessing.scale(X_train)
X_test = preprocessing.scale(X_test)

LR = [0.001,0.01]

for i in LR:
    #Defines linear regression model and its structure
    model = Sequential()
    model.add(Dense(500, input_shape=(7,), activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(1,))

    
    #Compiles model
    model.compile(Adam(lr=i), 'mean_squared_error')
    
    #Fits model
    history = model.fit(X_train, y_train, epochs = 100, validation_split = 0.1,verbose = 0)
    history_dict=history.history
    
    #Plots model's training cost/loss and model's validation split cost/loss
    loss_values = history_dict['loss']
    val_loss_values=history_dict['val_loss']
    plt.figure()
    plt.plot(loss_values,'b',label='training loss')
    plt.plot(val_loss_values,'r',label='val training loss')
    
    train_mse = model.evaluate(X_train, y_train, verbose=0)
    test_mse = model.evaluate(X_test, y_test, verbose=0)
    print('Train: %.3f, Test: %.3f' % (train_mse, test_mse))
   
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculates and prints r2 score of training and testing data
    print("The R2 score on the Train set is:\t{:0.3f}".format(r2_score(y_train, y_train_pred)))
    print("The R2 score on the Test set is:\t{:0.3f}".format(r2_score(y_test, y_test_pred)))

    plt.figure()    
    #plt.plot(y_train, y_train_pred,'*r')
    plt.plot(y_test, y_test_pred, '*g')
    
df_prediction = pd.DataFrame(data=X_test[0:,0:],
                             index=[i for i in range(X_test.shape[0])],
                             columns=['f'+str(i) for i in range(X_test.shape[1])])
predictions = model.predict_on_batch(X_test)
df_prediction["Actual SailTime"] = y_test.reset_index(drop=True)
df_prediction["Predicted SailTime"] = predictions
df_prediction.to_csv("../PredictedWaitTime.csv")