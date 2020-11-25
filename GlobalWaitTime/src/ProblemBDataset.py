#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 15:49:09 2020

@author: Dani
"""

import pandas as pd
import path 


# Red and green zone
green_lat_min = -36.0000
green_lat_max = -32.0000
green_long_min = 17.7000
green_long_max = 34.0000
  
# Reading csv-file using a relative path, based on the folder structure of the github project
file_path = path.Path(__file__).parent / "../../OriginalDataset/A.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file, names=["Imo", "RecievedTime", "Latitude", "Longitude", "NavStatus", "Status"])
    df["RecievedTime"] = pd.to_datetime(df["RecievedTime"])
        
def append_to_wait_lists(first_anchorage_entry, first_moored_entry, first_anchorage_imo_observations, first_anchorage_received_time_observations, first_moored_received_time_observations, first_anchorage_latitude_observations, first_anchorage_longitude_observations, first_anchorage_nav_status, full_wait_time):
    first_anchorage_imo_observations.append(first_anchorage_entry.Imo)
    first_anchorage_received_time_observations.append(first_anchorage_entry.RecievedTime)
    first_moored_received_time_observations.append(first_moored_entry.RecievedTime)
    first_anchorage_latitude_observations.append(first_anchorage_entry.Latitude)
    first_anchorage_longitude_observations.append(first_anchorage_entry.Longitude)
    first_anchorage_nav_status.append(first_anchorage_entry.NavStatus)
    full_wait_time.append((first_moored_entry.RecievedTime - first_anchorage_entry.RecievedTime).total_seconds()/3600)
    
def generate_df_with_first_anchorage_observation_and_full_wait_time_per_vessel(df_group_by_boat_id):
    first_anchorage_imo_observations = []
    first_anchorage_received_time_observations = []
    first_moored_received_time_observations = []
    first_anchorage_latitude_observations = []
    first_anchorage_longitude_observations = []
    first_anchorage_nav_status = []
    full_wait_time = []
    for imo, imo_observations in df_group_by_boat_id:
        first_anchorage_entry = None
        for observation in imo_observations.itertuples():
            if (observation.NavStatus == 1 and 'anchorage' in observation.Status) and first_anchorage_entry is None:            
                first_anchorage_entry = observation
            elif (observation.NavStatus == 5 and 'moored' in observation.Status) and first_anchorage_entry is not None:
                    append_to_wait_lists(first_anchorage_entry, observation, first_anchorage_imo_observations, first_anchorage_received_time_observations, first_moored_received_time_observations, first_anchorage_latitude_observations, first_anchorage_longitude_observations, first_anchorage_nav_status, full_wait_time)
                    first_anchorage_entry = None
    combined_list = [first_anchorage_imo_observations, first_anchorage_received_time_observations, first_moored_received_time_observations, first_anchorage_latitude_observations, first_anchorage_longitude_observations, first_anchorage_nav_status, full_wait_time]    
    return pd.DataFrame(combined_list, index=['Imo', 'RecievedTime', 'FinishedRecievedTime', 'Latitude', 'Longitude', 'NavStatus', 'WaitTime']).T
    
def generate_enhanced_dataset(df):
    # Sorting the dataset to ensure that the first moving is actually the first one for the given vessel, as there can be multiple start sailing processes for a 
    # given vessel in our dataset
    df = df.sort_values(["Imo", "RecievedTime"], ascending = (True, True))
    
    # Grouping observations per vessel (imo = id of vessel). Sorting is preserved.
    df_group_by_boat_id = df.groupby(["Imo"])
    
    # Generate a dataframe containing each new "firs moving observation in red zone to green zone (from the area of Kupang to Dampier)
    # Note: The same boat can have mutliple 'first-moving-observations' as the dataset expands for a long time
    df_wait_time = generate_df_with_first_anchorage_observation_and_full_wait_time_per_vessel(df_group_by_boat_id)
    
    print('All observations: ', len(df))
    print('Unique vessels: ', len(df_group_by_boat_id))
    print('Start-waiting-observations: ', len(df_wait_time))
    return df_wait_time 
    
# Generate dataset that holds only first-moving-observation, with its full sailing time
df = generate_enhanced_dataset(df)
df.to_csv("../GeneratedDataset/WorldWideWaitTime.csv")