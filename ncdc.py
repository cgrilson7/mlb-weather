import requests
import os
import pandas as pd

# NCDC web services documentation here:
# https://www.ncdc.noaa.gov/cdo-web/webservices/v2

HEADER = {'token':os.environ['NCDC_TOKEN']}
URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"
ENDPOINTS = ['datasets', 'datacategories', 'datatypes', 'locationcategories', 'locations', 'stations', 'data']
DATASET_IDS = ['GHCND', 'GSOM', 'GSOY', 'NEXRAD2', 'NEXRAD3', 'NORMAL_ANN', 'NORMAL_DLY', 'NORMAL_HLY', 'NORMAL_MLY', 'PRECIP_15', 'PRECIP_HLY']
PARAMETERS_NAMES = ['datatypeid', 'locationid', 'stationid', 'startdate', 'enddate', 'units', 'sortfield', 'sortorder', 'limit', 'offset', 'includemetadata']
PARAMETERS_DEFAULT_VALUES = [None, None, None, "2000-01-01T00:00:00", "2000-01-01T00:00:00", "metric", "mindate", 1000, None, False]

def _url(path):
    return URL + path

def get_endpoint(endpoint=None, payload=None):
    return requests.get(_url(endpoint), headers=HEADER, params=payload)

def get_datasets_df():
    response = get_endpoint("datasets").json()
    results = response['results']
    return pd.DataFrame(results) 

def get_dataset_info(dataset_id=None):
    if dataset_id in DATASET_IDS:
        return get_endpoint(f"datasets/{dataset_id}")
    else:
        print("Invalid dataset ID. Please use one of the following: '" + "', '".join(DATASET_IDS) + "'")

def get_data(dataset_id=None):
    pass

