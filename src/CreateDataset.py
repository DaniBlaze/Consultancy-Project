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
file_path = path.Path(__file__).parent / "../OriginalDataset/B_light.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file, names=["Imo", "RecievedTime", "Latitude", "Longitude", "NavStatus", "Status"])
    df["RecievedTime"] = pd.to_datetime(df["RecievedTime"])

def filter_based_on_lat_long(df, red_lat_min, red_lat_max, red_long_min, red_long_max, green_lat_min, green_lat_max, green_long_min, green_long_max):
    zone_red_green_query = np.where(((df["Latitude"] >= red_lat_min) & (df["Latitude"] <= red_lat_max) & (df["Longitude"] >= red_long_min) & (df["Longitude"] <= red_long_max)) 
                          | ((df["Latitude"] >= green_lat_min) & (df["Latitude"] <= green_lat_max) & (df["Longitude"] >= green_long_min) & (df["Longitude"] <= green_long_max)))
    return df.loc[zone_red_green_query]

def append_default_value_to_count_lists(underway_count, waiting_count, moored_count, finished_count, other_count, future_count):
    underway_count.append(0)
    waiting_count.append(0)
    moored_count.append(0)
    finished_count.append(0)
    other_count.append(0)
    future_count.append(0)

def add_latest_nav_status_to_count(latest_nav_status, row_index, underway_count, waiting_count, moored_count, finished_count, other_count, future_count):
    if latest_nav_status == 0:
        underway_count[row_index] = underway_count[row_index] + 1
    elif latest_nav_status == 1:
        waiting_count[row_index] = waiting_count[row_index] + 1
    elif latest_nav_status == 5:
        moored_count[row_index] = moored_count[row_index] + 1
    elif latest_nav_status == 99:
        finished_count[row_index] = finished_count[row_index] + 1
    elif latest_nav_status == -1:
        future_count[row_index] = future_count[row_index] + 1
    else:
        other_count[row_index] = other_count[row_index] + 1

def find_latest_nav_status(imo_observations, datetime):
    latestEntry = None
    imo_observations = imo_observations.reset_index(drop=True)
    for observation in imo_observations.itertuples():
        if observation.RecievedTime <= datetime:
            if latestEntry is None:
                latestEntry = observation
            elif latestEntry.RecievedTime <= observation.RecievedTime:
                if (observation.Index == len(imo_observations) - 1) & (observation.NavStatus == 5):
                    return 99 # Last status we know is moored and we interpret it as finished/moving out of the port
                latestEntry = observation
    if latestEntry is None:
        return -1
    else:
        return latestEntry.NavStatus

def add_counts_to_df(df, underway_count, waiting_count, moored_count, finished_count, other_count, future_count):
    df['UnderwayCount'] = underway_count
    df['WaitingCount'] = waiting_count
    df['MooredCount'] = moored_count
    df['FinishedCount'] = finished_count
    df['OtherCount'] = other_count
    df['FutureCount'] = future_count
    
def genereate_dataframe_with_all_current_nav_status_count(df):
    df_group_by_boat_id = df.groupby(["Imo"])
    underway_count = []
    waiting_count = []
    moored_count = []
    finished_count = []
    other_count = []
    future_count = []
    df = df.reset_index(drop=True)
    print(len(df))
    for row in df.itertuples():
        print(row.Index)
        append_default_value_to_count_lists(underway_count, waiting_count, moored_count, finished_count, other_count, future_count)
        for imo, imo_observations in df_group_by_boat_id:
            latest_nav_status = find_latest_nav_status(imo_observations, row.RecievedTime)
            add_latest_nav_status_to_count(latest_nav_status, row.Index, underway_count, waiting_count, moored_count, finished_count, other_count, future_count)
    add_counts_to_df(df, underway_count, waiting_count, moored_count, finished_count, other_count, future_count)
    return df
            

df = filter_based_on_lat_long(df, -20.2003, -20.0359, 118.4100, 118.7464, -20.3546, -20.3076, 118.5445, 118.6084)
df.to_csv("../GeneratedDataset/PortHedlandRedAndGreenZone.csv")

df = genereate_dataframe_with_all_current_nav_status_count(df)
df.to_csv("../GeneratedDataset/PortHedlandWithCount.csv")
