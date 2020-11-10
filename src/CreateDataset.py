#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:12:48 2020

@author: Dani
"""

import pandas as pd
import path 
import numpy as np

# Reading csv-file using a relative path, based on the folder structure of the github project
file_path = path.Path(__file__).parent / "../OriginalDataset/B.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file, names=["Imo", "RecievedTime", "Latitude", "Longitude", "NavStatus", "Status"]) 

def filter_based_on_lat_long(df, red_lat_min, red_lat_max, red_long_min, red_long_max, green_lat_min, green_lat_max, green_long_min, green_long_max):
    zone_red_green_query = np.where(((df["Latitude"] >= red_lat_min) & (df["Latitude"] <= red_lat_max) & (df["Longitude"] >= red_long_min) & (df["Longitude"] <= red_long_max)) 
                          | ((df["Latitude"] >= green_lat_min) & (df["Latitude"] <= green_lat_max) & (df["Longitude"] >= green_long_min) & (df["Longitude"] <= green_long_max)))
    return df.loc[zone_red_green_query]

def find_latest_nav_status(imo_observations, datetime):
    latestEntry = None
    for observation in imo_observations:
        if observation["RecievedTime"] <= datetime:
            if latestEntry == None:
                latestEntry = observation
            elif latestEntry["RecievedTime"] > observation["RecievedTime"]:
                latestEntry = observation
    if latestEntry == None:
        return -1
    else:
        return latestEntry["NavStatus"]
    
def groupByStuff(df):
    group_by_boat_id = df.groupby(["Imo"])
    for index, row in df.iterrows():
        for imo, imo_observations in group_by_boat_id:
            print(find_latest_nav_status(imo_observations, row["RecievedTime"]))

df = filter_based_on_lat_long(df, -20.2003, -20.0359, 118.4100, 118.7464, -20.3546, -20.3076, 118.5445, 118.6084)
df.to_csv("../GeneratedDataset/PortHedlandRedAndGreenZone.csv")

groupByStuff(df)