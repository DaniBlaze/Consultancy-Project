#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 23:16:19 2020

@author: Dani
"""

import pandas as pd
import path 


# Red and green zone
red_lat_min = 0.5000
red_lat_max = 7.0000
red_long_min = 89.0000
red_long_max = 96.0000
green_lat_min = -36.0000
green_lat_max = -32.0000
green_long_min = 17.7000
green_long_max = 34.0000
  
# Reading csv-file using a relative path, based on the folder structure of the github project
file_path = path.Path(__file__).parent / "../../OriginalDataset/A.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file, names=["Imo", "RecievedTime", "Latitude", "Longitude", "NavStatus", "Status"])
    df["RecievedTime"] = pd.to_datetime(df["RecievedTime"])
    

def is_in_red_zone(latitude, longitude):
    return latitude >= red_lat_min and latitude <= red_lat_max and longitude >= red_long_min and longitude <= red_long_max 

def is_in_green_zone(latitude, longitude):
    return latitude >= green_lat_min and latitude <= green_lat_max and longitude >= green_long_min and longitude <= green_long_max 

def is_in_red_or_green_zone(latitude, longitude):
    return is_in_red_zone(latitude, longitude) or is_in_green_zone(latitude, longitude)
    
def append_to_move_lists(first_moving_entry, finished_moving_entry, first_move_imo_observations, first_move_received_time_observations, finished_moved_received_time_observation, first_move_latitude_observations, first_move_longitude_observations, first_move_nav_status, full_sail_time):
    first_move_imo_observations.append(first_moving_entry.Imo)
    first_move_received_time_observations.append(first_moving_entry.RecievedTime)
    finished_moved_received_time_observation.append(finished_moving_entry.RecievedTime)
    first_move_latitude_observations.append(first_moving_entry.Latitude)
    first_move_longitude_observations.append(first_moving_entry.Longitude)
    first_move_nav_status.append(first_moving_entry.NavStatus)
    full_sail_time.append((finished_moving_entry.RecievedTime - first_moving_entry.RecievedTime).total_seconds()/3600)
    
def generate_df_with_first_moving_observation_and_full_sailing_time_per_vessel(df_group_by_boat_id):
    first_move_imo_observations = []
    first_move_received_time_observations = []
    finished_moved_received_time_observation = []
    first_move_latitude_observations = []
    first_move_longitude_observations = []
    first_move_nav_status = []
    full_sail_time = []
    for imo, imo_observations in df_group_by_boat_id:
        first_moving_entry = None
        first_green = False
        first_red = False
        for observation in imo_observations.itertuples():
            # If this observation is not moving (underway), but the first_anchorage_entry is not empty, then this is a new moving/sail_time process.
            if (observation.NavStatus != 0 or 'moving' not in observation.Status) and first_moving_entry is not None:
                # We have a new moving observation on the same boat. Update lists and reset entry variables
                first_moving_entry = None
                first_green = False
                first_red = False
            elif (observation.NavStatus == 0 or 'moving' in observation.Status) and first_moving_entry is None and is_in_red_or_green_zone(observation.Latitude, observation.Longitude):            
                first_moving_entry = observation
                first_green = is_in_green_zone(observation.Latitude, observation.Longitude)
                first_red = is_in_red_zone(observation.Latitude, observation.Longitude)
            elif (observation.NavStatus == 0 or 'moving' in observation.Status) and first_moving_entry is not None and is_in_red_or_green_zone(observation.Latitude, observation.Longitude):
                if (is_in_green_zone(observation.Latitude, observation.Longitude) and first_red) or (is_in_red_zone(observation.Latitude, observation.Longitude) and first_green):
                    append_to_move_lists(first_moving_entry, observation, first_move_imo_observations, first_move_received_time_observations, finished_moved_received_time_observation, first_move_latitude_observations, first_move_longitude_observations, first_move_nav_status, full_sail_time)
                    first_moving_entry = None
                    first_green = False
                    first_red = False
    combined_list = [first_move_imo_observations, first_move_received_time_observations, finished_moved_received_time_observation, first_move_latitude_observations, first_move_longitude_observations, first_move_nav_status, full_sail_time]
    return pd.DataFrame(combined_list, index=['Imo', 'RecievedTime', 'FinishedRecievedTime', 'Latitude', 'Longitude', 'NavStatus', 'SailTime']).T
    
def generate_enhanced_dataset(df):
    # Sorting the dataset to ensure that the first moving is actually the first one for the given vessel, as there can be multiple start sailing processes for a 
    # given vessel in our dataset
    df = df.sort_values(["Imo", "RecievedTime"], ascending = (True, True))
    
    # Grouping observations per vessel (imo = id of vessel). Sorting is preserved.
    df_group_by_boat_id = df.groupby(["Imo"])
    
    # Generate a dataframe containing each new "firs moving observation in red zone to green zone (from the area of Kupang to Dampier)
    # Note: The same boat can have mutliple 'first-moving-observations' as the dataset expands for a long time
    df_sailing_time = generate_df_with_first_moving_observation_and_full_sailing_time_per_vessel(df_group_by_boat_id)
    
    print('All observations in red and green zone: ', len(df))
    print('Unique vessels: ', len(df_group_by_boat_id))
    print('Start-sailing-observations: ', len(df_sailing_time))
    return df_sailing_time 
    
# Generate dataset that holds only first-moving-observation, with its full sailing time
df = generate_enhanced_dataset(df)
df.to_csv("../GeneratedDataset/CapeSabang.csv")
