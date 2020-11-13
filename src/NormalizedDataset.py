#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 13:43:45 2020

@author: Dani
"""
import pandas as pd
import path 

file_path = path.Path(__file__).parent / "../FinalDataset.csv"
with file_path.open() as dataset_file:
    df_final_dataset = pd.read_csv(dataset_file)
    df_final_dataset.to_csv("../ANN/FinalDatasetWOHeader.csv", header=False)
    
file_path = path.Path(__file__).parent / "../ANN/FinalDatasetWOHeader.csv"
with file_path.open() as dataset_file:
    df_wo_head = pd.read_csv(dataset_file)
    df_normalized = df_wo_head.iloc[: , [6, 7, 8]]
    print(df_normalized.head())
    
# Find the min and max values for each column
def dataset_minmax(dataset):
    for column in zip(*dataset):
        print(column)
	#stats = [[min(column), max(column)] for column in zip(*dataset)]
	#return stats

# Rescale dataset columns to the range 0-1
def normalize_dataset(dataset, minmax):
	for row in dataset:
		for i in range(len(row)-1):
			row[i] = (row[i] - minmax[i][0]) / (minmax[i][1] - minmax[i][0])
            

stats = dataset_minmax(df_normalized)
print(stats)
