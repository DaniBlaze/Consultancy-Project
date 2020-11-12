#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:12:48 2020

@author: Dani
"""

import pandas as pd
import path 

  
# Reading csv-file using a relative path, based on the folder structure of the github project
file_path = path.Path(__file__).parent / "../GeneratedDataset/PortHedlandWithCount.csv"
with file_path.open() as dataset_file:
    df_port_hedland = pd.read_csv(dataset_file)
    df_port_hedland["RecievedTime"] = pd.to_datetime(df_port_hedland["RecievedTime"])

file_path = path.Path(__file__).parent / "../OriginalDataset/vessel_db.csv"
with file_path.open() as dataset_file:
    df_static = pd.read_csv(dataset_file)

# Merged port hedland with static file
merged = pd.merge(df_port_hedland, df_static, on='Imo')
merged.to_csv("../GeneratedDataset/MergedPortHedlandAndStatic.csv")
drop_columns = [0, 7, 10, 11, 12, 18, 19, 22, 23, 25, 26]
merged.drop(merged.columns[drop_columns], axis=1, inplace=True)
merged.to_csv("../GeneratedDataset/FinalDataset.csv")
