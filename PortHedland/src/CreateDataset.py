#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import path 
import numpy as np

# Red and green zone
red_lat_min = -20.2003
red_lat_max = -19.8000
red_long_min = 118.3000
red_long_max = 118.7464
green_lat_min = -20.3546 
green_lat_max = -20.3076
green_long_min = 118.5445
green_long_max = 118.6084
  
# Reading csv-file using a relative path, based on the folder structure of the github project
file_path = path.Path(__file__).parent / "../../OriginalDataset/B.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file, names=["Imo", "RecievedTime", "Latitude", "Longitude", "NavStatus", "Status"])
    df["RecievedTime"] = pd.to_datetime(df["RecievedTime"])
    print(len(df.groupby(["Imo"])))

def filter_based_on_lat_long(df):
    zone_red_green_query = np.where(((df["Latitude"] >= red_lat_min) & (df["Latitude"] <= red_lat_max) & (df["Longitude"] >= red_long_min) & (df["Longitude"] <= red_long_max)) 
                          | ((df["Latitude"] >= green_lat_min) & (df["Latitude"] <= green_lat_max) & (df["Longitude"] >= green_long_min) & (df["Longitude"] <= green_long_max)))
    return df.loc[zone_red_green_query]

def append_to_wait_lists(first_waiting_entry, latest_moored_entry, first_wait_imo_observations, first_wait_received_time_observations, first_wait_latitude_observations, first_wait_longitude_observations, first_wait_nav_status, full_wait_time):
    first_wait_imo_observations.append(first_waiting_entry.Imo)
    first_wait_received_time_observations.append(first_waiting_entry.RecievedTime)
    first_wait_latitude_observations.append(first_waiting_entry.Latitude)
    first_wait_longitude_observations.append(first_waiting_entry.Longitude)
    first_wait_nav_status.append(first_waiting_entry.NavStatus)
    full_wait_time.append(latest_moored_entry.RecievedTime - first_waiting_entry.RecievedTime)
    
def generate_df_with_first_wait_observation_and_full_waiting_time_per_vessel(df_group_by_boat_id):
    first_wait_imo_observations = []
    first_wait_received_time_observations = []
    first_wait_latitude_observations = []
    first_wait_longitude_observations = []
    first_wait_nav_status = []
    full_wait_time = []
    for imo, imo_observations in df_group_by_boat_id:
        first_waiting_entry = None
        latest_moored_entry = None
        for observation in imo_observations.itertuples():
            # If this observation is anchor/wait, but the latest_moored_entry is not empty, then this is a new anchor/wait process.
            if (observation.NavStatus == 1 or 'anchorage' in observation.Status) and (latest_moored_entry is not None and first_waiting_entry is not None):
                # We have a new anchor observation on the same boat. Update lists and reset entry variables
                append_to_wait_lists(first_waiting_entry, latest_moored_entry, first_wait_imo_observations, first_wait_received_time_observations, first_wait_latitude_observations, first_wait_longitude_observations, first_wait_nav_status, full_wait_time)
                first_waiting_entry = None
                latest_moored_entry = None
            if (observation.NavStatus == 1 or 'anchorage' in observation.Status) and first_waiting_entry is None:
                first_waiting_entry = observation                
            elif (observation.NavStatus == 5 or 'moored' in observation.Status) and latest_moored_entry is None and first_waiting_entry is not None:
                latest_moored_entry = observation
        if (latest_moored_entry is not None) and (first_waiting_entry is not None):
            append_to_wait_lists(first_waiting_entry, latest_moored_entry, first_wait_imo_observations, first_wait_received_time_observations, first_wait_latitude_observations, first_wait_longitude_observations, first_wait_nav_status, full_wait_time)
    combined_list = [first_wait_imo_observations, first_wait_received_time_observations, first_wait_latitude_observations, first_wait_longitude_observations, first_wait_nav_status, full_wait_time]
    return pd.DataFrame(combined_list, index=['Imo', 'RecievedTime', 'Latitude', 'Longitude', 'NavStatus', 'FullWaitTime']).T
           
def append_default_value_to_count_lists(underway_count, waiting_count, moored_count, finished_count, other_count):
    underway_count.append(0)
    waiting_count.append(0)
    moored_count.append(0)
    finished_count.append(0)
    other_count.append(0)

def update_count_lists(imo_observations, received_time_of_given_wait_event, row_index, underway_count, waiting_count, moored_count, finished_count, other_count):
    latest_observation = None
    finished_counter = 0
    imo_observations = imo_observations.reset_index(drop=True)
    for observation in imo_observations.itertuples():
        if observation.RecievedTime <= received_time_of_given_wait_event:
            latest_observation = observation
            # If we are at the last observation
            if (observation.Index == len(imo_observations) - 1):
                if observation.NavStatus == 5 or 'moored' in observation.Status:
                    finished_counter = finished_counter + 1
                # The last observation, for the entire this-boat-observation-list, should not affect the count (would affect the count forever if we did not set it to None)
                latest_observation = None
            elif observation.NavStatus == 5 or 'moored' in observation.Status:
                next_observation = imo_observations.loc[observation.Index + 1, :]
                # The vessel could be finished (last moored for this docking process)
                if (next_observation.NavStatus != 5 and 'moored' not in next_observation.Status):
                    finished_counter = finished_counter + 1
                    latest_observation = None
        else:
            break
    
    finished_count[row_index] = finished_count[row_index] + finished_counter
    if latest_observation is not None:
        if latest_observation.NavStatus == 5 or 'moored' in latest_observation.Status:
            moored_count[row_index] = moored_count[row_index] + 1
        elif latest_observation.NavStatus == 1 or 'anchorage' in latest_observation.Status:
            waiting_count[row_index] = waiting_count[row_index] + 1
        elif latest_observation.NavStatus == 0 or 'moving' in latest_observation.Status:
            underway_count[row_index] = underway_count[row_index] + 1
        else:
            other_count[row_index] = other_count[row_index] + 1
        
def add_count_to_df(df, underway_count, waiting_count, moored_count, finished_count, other_count):
    df['UnderwayCount'] = underway_count
    df['WaitingCount'] = waiting_count
    df['MooredCount'] = moored_count
    df['OtherCount'] = other_count
    df['FinishedCount'] = finished_count
    
def generate_enhanced_dataset(df):
    # Sorting the dataset to ensure that the first anchor/wait is actually the first one for the given vessel, as there can be multiple docking processes for a 
    # given vessel in our dataset
    df = df.sort_values(["Imo", "RecievedTime"], ascending = (True, True))
    
    # Grouping observations per vessel (imo = id of vessel). Sorting is preserved.
    df_group_by_boat_id = df.groupby(["Imo"])
    
    # Generate a dataframe containing each new 'Start-waiting-observation' with the wait time it took for the given vessel to first wait and then become moored.
    # Note: The same boat can have mutliple 'Start-waiting-observations' as the dataset expands for a long time
    df_first_waiting_observations_with_full_wait_time = generate_df_with_first_wait_observation_and_full_waiting_time_per_vessel(df_group_by_boat_id)

    # Keep track of each vessel state for each 'Start-waiting observation':
    underway_count = []
    waiting_count = []
    moored_count = []
    finished_count = []
    other_count = []
    
    print('All observations: ', len(df))
    print('Unique vessels: ', len(df_group_by_boat_id))
    print('Start-waiting observations: ', len(df_first_waiting_observations_with_full_wait_time))
    return df_first_waiting_observations_with_full_wait_time
    # Loop through each 'Start-waiting-observation' event
    for row in df_first_waiting_observations_with_full_wait_time.itertuples():
        print(row.Index)
        append_default_value_to_count_lists(underway_count, waiting_count, moored_count, finished_count, other_count)
        
        # For each 'Start-waiting-observation' event we need to find the state of every other vessel within this 'Start-waiting-observation' ReceivedTime.
        # This will give us how many vessels are waiting and moored at this exact time.
        for imo, imo_observations in df_group_by_boat_id:
            update_count_lists(imo_observations, row.RecievedTime, row.Index, underway_count, waiting_count, moored_count, finished_count, other_count)
    add_count_to_df(df_first_waiting_observations_with_full_wait_time, underway_count, waiting_count, moored_count, finished_count, other_count)
    return df_first_waiting_observations_with_full_wait_time

# Find all observations within red and green zone
df = filter_based_on_lat_long(df)
df.to_csv("../GeneratedDataset/PortHedlandRedAndGreenZone.csv")

# Generate dataset that holds only first-waiting-observation, with its full wait time and the state of all other vessels.
df = generate_enhanced_dataset(df)
df.to_csv("../GeneratedDataset/PortHedlandWithCount.csv")
