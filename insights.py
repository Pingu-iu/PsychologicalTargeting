import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import json 
import requests
from datetime import timedelta, datetime

import os
from dotenv import load_dotenv
import numpy as np 

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


from collections import defaultdict


# Get Access tokens and app ids
load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

AD_ACCOUNT_ID = os.getenv('ACCOUNT_ID')
API_VERSION = "v21.0"  

# Set up the base URL
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

############################################################################################################
# 
# Functions to retrieve data from the Facebook Marketing API
#
############################################################################################################
def get_stat_per_day(adset_id, start_date, end_date, access_token=ACCESS_TOKEN, stat='impressions'):
    url = BASE_URL+f"/{adset_id}/insights"

    params = {
        'access_token': access_token, 
        'time_range': json.dumps({
            'since': start_date,
            'until': end_date
        }),
        'fields': stat,
        'time_increment': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        insights_data = response.json().get('data', [])
        return insights_data if insights_data else None
    else:
        print(f"Error fetching insights for ad set {adset_id}: {response.status_code}")
        print(response.json())
        return None 

def get_adset_total_stat(adset_id, access_token=ACCESS_TOKEN, stat='reach'):
    url = BASE_URL+f"/{adset_id}/insights"
    params = {
        'access_token': access_token,
        'fields': stat,
        'date_preset': 'maximum'
        
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        insights_data = response.json().get('data', [])
        return insights_data if insights_data else None
    else:
        print(f"Error fetching insights for ad set {adset_id}: {response.status_code}")
        return None
    
# Function to make a request for a single day's hourly data
def get_hourly_stat_for_day(day, adset_id, access_token, stat='impressions'):
    url =  url = BASE_URL+f"/{adset_id}/insights"
    params = {
        'fields': stat,
        'time_range': json.dumps({
            'since': day,
            'until': day
        }),
        'time_increment': 1,
        'breakdowns': 'hourly_stats_aggregated_by_advertiser_time_zone',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error retrieving data for {day}: {response.status_code}, {response.text}")
        return []
    
def get_hourly_stat(start_date, end_date, adset_id, access_token=ACCESS_TOKEN, stat='impressions'): 
    all = []
    # Loop through each day in the date range and request hourly data
    current_date = start_date
    while current_date <= end_date:
        day_str = current_date.strftime('%Y-%m-%d')
        daily_data = get_hourly_stat_for_day(day=day_str, adset_id=adset_id, access_token=ACCESS_TOKEN, stat=stat)
        all +=daily_data  
        # Move to the next day
        current_date += timedelta(days=1)   
    return all 
    
# Retrieves gender breakdown by hour for a given ad
def get_stat_by_breakdown(ad_id, access_token=ACCESS_TOKEN, stat='reach', breakdown='gender,age'):
    url =  url = BASE_URL+f"/{ad_id}/insights"
    params = {
        'access_token': access_token,
        'fields': stat,  
        'breakdowns': breakdown,
        'time_increment': 1,  
        'date_preset': 'maximum' 
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error retrieving data: {response.status_code}, {response.text}")
        return []

def get_ad_study(ad_study_id, access_token=ACCESS_TOKEN):
    url = BASE_URL + f"/{ad_study_id}/cells"
    params = {
        'access_token': access_token, 
        'fields': 'name',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error retrieving ad study data: {response.status_code}, {response.text}")
        return []
############################################################################################################
# 
# Functions to extract data for plotting from the Facebook Marketing API response 
#
############################################################################################################

def extract_hourly_stat(ad_data_list, stat='impressions'):
    all_timestamps = set()
    for ad_data in ad_data_list:
        for entry in ad_data:    
            timestamp = pd.to_datetime(entry['date_start'] + ' ' + entry['hourly_stats_aggregated_by_advertiser_time_zone'].split(' - ')[0])
            all_timestamps.add(timestamp)
    all_timestamps = sorted(list(all_timestamps))
    
    dfs = [] # List to store dataframes
    for ad_index, ad_data in enumerate(ad_data_list):
        df = pd.DataFrame(ad_data)
        df['timestamp'] = pd.to_datetime(df['date_start'] + ' ' + df['hourly_stats_aggregated_by_advertiser_time_zone'].str.split(' - ').str[0])
        df = df.set_index('timestamp')
        df = df[[stat]] # Keep only impressions
        df[stat] = df['impressions'].astype(int) # Convert to integer
        df = df.reindex(all_timestamps, fill_value=0)
        dfs.append(df) # append this dataframes
    return dfs

def extract_hourly_actions(ad_data_list):
    all_timestamps = set()
    for ad_data in ad_data_list:
        for entry in ad_data:
            if 'hourly_stats_aggregated_by_advertiser_time_zone' in entry:
                timestamp = pd.to_datetime(
                    entry['date_start'] + ' ' + entry['hourly_stats_aggregated_by_advertiser_time_zone'].split(' - ')[0]
                )
                all_timestamps.add(timestamp)
    all_timestamps = sorted(list(all_timestamps))
    
    dfs = []
    for ad_index, ad_data in enumerate(ad_data_list):
        hourly_data = []
        for entry in ad_data:
            hour_range = entry.get('hourly_stats_aggregated_by_advertiser_time_zone')
            if hour_range:
                actions = entry.get('actions', [])
                total_actions = sum(int(action['value']) for action in actions)/3
                timestamp = pd.to_datetime(entry['date_start'] + ' ' + hour_range.split(' - ')[0])
                hourly_data.append({'timestamp': timestamp, 'actions': total_actions})
        
        df = pd.DataFrame(hourly_data)
        df = df.set_index('timestamp')
        df = df.reindex(all_timestamps, fill_value=0)  # Fill missing hours with 0
        dfs.append(df)

    return dfs 


def extract_full_hourly_data(impressions_breakdown, actions_breakdown, spend_breakdown, ctr_breakdown, bids):
    impressions_1 , impressions_2 = extract_hourly_stat(impressions_breakdown, stat='impressions')
    actions_1, actions_2 = extract_hourly_actions(actions_breakdown)
    spend_1, spend_2 = extract_hourly_stat(spend_breakdown, stat='spend')
    ctr_1, ctr_2 = extract_hourly_stat(ctr_breakdown, stat='ctr')
    bids_1, bids_2 = pd.Series([bids[0] for i in range(0, len(impressions_1))], name='bid', index=impressions_1.index), pd.Series([bids[1] for i in range(0, len(impressions_2))], name='bid', index=impressions_2.index)
    
    # merge all the data into one dataframe with various columns
    merged_df_1 = impressions_1.merge(actions_1, on='timestamp').merge(spend_1, on='timestamp').merge(ctr_1, on='timestamp').merge(bids_1, on='timestamp')
    merged_df_2 = impressions_2.merge(actions_2, on='timestamp').merge(spend_2, on='timestamp').merge(ctr_2, on='timestamp').merge(bids_2, on='timestamp')

    return merged_df_1, merged_df_2

############################################################################################################
# 
# Functions to Plot comparative data for two or more adsets
# 
############################################################################################################  
    
def plot_hourly_stat(ad_data_list, legends, title, stat='impressions'):
    
    dfs = extract_hourly_stat(ad_data_list, stat=stat)

    for i, df in enumerate(dfs):
        plt.plot(df.index, df[stat], label=legends[i])

    plt.xlabel('Hour')
    plt.ylabel(stat.capitalize())
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45, ha='right') # Rotate x-axis labels
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.show()

def plot_hourly_actions(ad_data_list, legends, title):
    all_timestamps = set()
    for ad_data in ad_data_list:
        for entry in ad_data:
            if 'hourly_stats_aggregated_by_advertiser_time_zone' in entry:
                timestamp = pd.to_datetime(
                    entry['date_start'] + ' ' + entry['hourly_stats_aggregated_by_advertiser_time_zone'].split(' - ')[0]
                )
                all_timestamps.add(timestamp)
    all_timestamps = sorted(list(all_timestamps))
    
    dfs = []
    for ad_index, ad_data in enumerate(ad_data_list):
        hourly_data = []
        for entry in ad_data:
            hour_range = entry.get('hourly_stats_aggregated_by_advertiser_time_zone')
            if hour_range:
                actions = entry.get('actions', [])
                total_actions = sum(int(action['value']) for action in actions)/3
                timestamp = pd.to_datetime(entry['date_start'] + ' ' + hour_range.split(' - ')[0])
                hourly_data.append({'timestamp': timestamp, 'actions': total_actions})
        
        df = pd.DataFrame(hourly_data)
        df = df.set_index('timestamp')
        df = df.reindex(all_timestamps, fill_value=0)  # Fill missing hours with 0
        dfs.append(df)

    for i, df in enumerate(dfs):
        plt.plot(df.index, df['actions'], linestyle='-', label=legends[i])

    plt.xlabel('Hour')
    plt.ylabel('Total Actions')
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    

def plot_age_breakdown(ads_data, ad_names):
    # Aggregate impressions by ad and age category
    ad_results = []
    all_ages = set()
    for ad_index, ad in enumerate(ads_data):
        impressions_by_age = defaultdict(int)
        for record in ad:
            age = record['age']
            impressions = int(record['impressions'])
            impressions_by_age[age] += impressions
            all_ages.add(age)
        ad_results.append((ad_names[ad_index], impressions_by_age))
        
    # Ensure consistent order of age categories
    all_ages = sorted(all_ages)

    # Plot each ad's results as grouped bars
    x = np.arange(len(all_ages))  # the label locations
    bar_width = 0.2

    plt.figure(figsize=(12, 8))
    for i, (ad_name, impressions_by_age) in enumerate(ad_results):
        impressions = [impressions_by_age.get(age, 0) for age in all_ages]
        plt.bar(x + i * bar_width, impressions, bar_width, label=ad_name)

    plt.xlabel('Age Category')
    plt.ylabel('Total Impressions')
    plt.title('Total Impressions per Age Category for Each Ad')
    plt.xticks(x + bar_width * (len(ad_results) - 1) / 2, all_ages, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()  


