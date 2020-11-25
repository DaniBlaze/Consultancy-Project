#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 13:43:45 2020

@author: Dani
"""
import pandas as pd
import path
from sklearn.preprocessing import MinMaxScaler


def set_numerical_value_for_vessel_type(df):
    for index in df.index:
        if df.loc[index, 'type'] == 'Bulk Carrier':
            df.loc[index, 'type'] = 1
        elif df.loc[index, 'type'] == 'Ore Carrier':
            df.loc[index, 'type'] = 2
        else:
            df.loc[index, 'type'] = 3
            
file_path = path.Path(__file__).parent / "../FinalDataset.csv"
with file_path.open() as dataset_file:
    df_final_dataset = pd.read_csv(dataset_file)
    set_numerical_value_for_vessel_type(df_final_dataset)
    df_final_dataset= df_final_dataset.iloc[: , [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 15]]
    df_final_dataset.to_csv("../ANN/FinalDatasetPrepared.csv", index=False)
    
file_path = path.Path(__file__).parent / "../ANN/FinalDatasetPrepared.csv"
with file_path.open() as dataset_file:
    df_to_be_normalized = pd.read_csv(dataset_file)

def normalize_dataset(df):
    scalar = MinMaxScaler()
    matrix = df.to_numpy()
    return scalar.fit_transform(matrix)

normalized = normalize_dataset(df_to_be_normalized)
print(normalized.shape)
df_prepared_and_normalized=pd.DataFrame(data=normalized[0:,0:],
                                        index=[i for i in range(normalized.shape[0])],
                                        columns=['f'+str(i) for i in range(normalized.shape[1])])
df_prepared_and_normalized.to_csv("../ANN/FinalDatasetPreparedAndNormalized.csv", index=False)
