#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 10:33:23 2020

@author: Dani
"""
import path
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping

import pandas as pd

import sklearn
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from matplotlib import pyplot as plt
#%matplotlib inline
#%config InlineBackend.figure_format='retina'

file_path = path.Path(__file__).parent / "../ANN/FinalDatasetPrepared.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file)

# Split into input (X) and output (y) variables
X = df[["Latitude", "Longitude", "WaitingCount", "MooredCount", "type", "built", "dwt", "loa", "beam", "draughtMeters"]]
y= df[["FullWaitTime"]]

# Split into input training and test data and output training and test data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

#
X_train = preprocessing.scale(X_train)
X_test = preprocessing.scale(X_test)

LR = [0.001,0.01]

for i in LR:
    #Defines linear regression model and its structure
    model = Sequential()
    model.add(Dense(30, input_shape=(10,), activation='relu'))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(1,))

    
    #Compiles model
    model.compile(Adam(lr=i), 'mean_squared_error')
    
    #Fits model
    history = model.fit(X_train, y_train, epochs = 2000, validation_split = 0.1,verbose = 0)
    history_dict=history.history
    
    #Plots model's training cost/loss and model's validation split cost/loss
    loss_values = history_dict['loss']
    val_loss_values=history_dict['val_loss']
    plt.figure()
    plt.plot(loss_values,'b',label='training loss')
    plt.plot(val_loss_values,'r',label='val training loss')
    
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Calculates and prints r2 score of training and testing data
    print("The R2 score on the Train set is:\t{:0.3f}".format(r2_score(y_train, y_train_pred)))
    print("The R2 score on the Test set is:\t{:0.3f}".format(r2_score(y_test, y_test_pred)))

    plt.figure()    
    plt.plot(y_train, y_train_pred,'*r')
    plt.plot(y_test, y_test_pred, '*g')