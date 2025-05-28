import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd 
import requests

import os
from dotenv import load_dotenv


# Get Access tokens and app ids
load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

AD_ACCOUNT_ID = os.getenv('ACCOUNT_ID')
API_VERSION = "v21.0"  

# Set up the base URL
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def get_campaigns_by_name(name_filter, account_id=AD_ACCOUNT_ID, access_token=ACCESS_TOKEN):
    # Function to get campaign by name (filtering)
    base_url = BASE_URL + f"/{account_id}/campaigns"
    params = {
        "fields": "name,id,start_time",
        "filtering": f'[{{"field":"name","operator":"CONTAIN","value":"{name_filter}"}}]',
        "access_token": access_token
    }
    all_campaign_ids, all_campaign_names, all_start_times = [], [], []

    while True:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()

        # Collect campaign IDs from this page
        all_campaign_ids.extend([campaign["id"] for campaign in data.get("data", [])])
        all_campaign_names.extend([campaign["name"] for campaign in data.get("data", [])])
        all_start_times.extend([campaign["start_time"] for campaign in data.get("data", [])])
        
        # Check for next page
        paging = data.get("paging", {})
        next_page = paging.get("next")
        if not next_page:
            break

        # Update URL for the next page
        base_url = next_page
        params = None  # Parameters are already included in the next page URL
    df = pd.DataFrame({"campaign_id": all_campaign_ids, "campaign_name": all_campaign_names, "start_time": all_start_times})
    return df 

def get_adsets_by_campaign_id(campaign_id, access_token=ACCESS_TOKEN):
    # Function to get the adsets ids and names for a given campaign
    base_url = BASE_URL + f"/{campaign_id}/adsets"
    
    params = {
        "fields": "name,id",
        "access_token": access_token
    }
    # put result in list of dictionaries
    all_adset = []
    while True:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")

        data = response.json()
        all_adset.extend(data.get("data", []))
        
        # Check for next page
        paging = data.get("paging", {})
        next_page = paging.get("next")
        if not next_page:
            break

        # Update URL for the next page
        base_url = next_page
        params = None  # Parameters are already included in the next page URL
        
    return all_adset

######################################################################################

def get_custom_audience_size(audience_id, access_token=ACCESS_TOKEN):
    # Function to get the custom audience
    base_url = BASE_URL + f"/{audience_id}"
    params = {
        "fields": "approximate_count_lower_bound,approximate_count_upper_bound",
        "access_token": access_token
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    else :
        data = response.json()
        return data


def get_ad_level_data(ad_id, access_token=ACCESS_TOKEN):
    url = f"{BASE_URL}/{ad_id}/insights"
    params = {
        'access_token': access_token,
        'fields':'ad_id,ad_name,actions,impressions,spend,reach,cpm,cpc,ctr',
        'level': 'ad', 
        'date_preset' : 'maximum'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error fetching ad level data for ad {ad_id}: {response.status_code}")
        print(response.json())
        return None
