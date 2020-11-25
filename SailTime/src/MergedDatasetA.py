#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 16:41:01 2020

@author: Dani
"""

import pandas as pd
import path 

  
# Reading csv-file using a relative path, based on the folder structure of the github project
file_path = path.Path(__file__).parent / "../GeneratedDataset/CapeSabang.csv"
with file_path.open() as dataset_file:
    df_port_hedland = pd.read_csv(dataset_file)
    df_port_hedland["RecievedTime"] = pd.to_datetime(df_port_hedland["RecievedTime"])

file_path = path.Path(__file__).parent / "../../OriginalDataset/vessel_db.csv"
with file_path.open() as dataset_file:
    df_static = pd.read_csv(dataset_file)

# Merged port hedland with static file
merged = pd.merge(df_port_hedland, df_static, on='Imo')
merged.to_csv("../GeneratedDataset/MergedCapeSabangAndStatic.csv")
drop_columns = [0, 1, 6, 8, 9, 14, 15, 16, 17, 18, 19, 21, 22]
merged.drop(merged.columns[drop_columns], axis=1, inplace=True)
merged.to_csv("../GeneratedDataset/FinalDatasetA.csv")
