import requests
import os
import pandas as pd

# NCDC web services documentation here:
# https://www.ncdc.noaa.gov/cdo-web/webservices/v2

HEADER = {'token':os.environ['NCDC_TOKEN']}
URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"
ENDPOINTS = ['datasets', 'datacategories', 'datatypes', 'locationcategories', 'locations', 'stations', 'data']
DATASET_IDS = ['GHCND', 'GSOM', 'GSOY', 'NEXRAD2', 'NEXRAD3', 'NORMAL_ANN', 'NORMAL_DLY', 'NORMAL_HLY', 'NORMAL_MLY', 'PRECIP_15', 'PRECIP_HLY']
VALID_PARAMS = ['datatypeid', 'locationid', 'stationid', 'startdate', 'enddate', 'units', 'sortfield', 'sortorder', 'limit', 'offset', 'includemetadata']

def _url(path):
    return URL + path

def get_endpoint(endpoint=None, payload=None):
    """
    This is the base GET function. It sends a GET request to the base URL with the user-supplied ENDPOINT appended, with an optional params payload.

    Args:
    required
        - endpoint      (str): 
    optional
        - payload (dict or str): Key-value pairs for acceptable parameters (VALID_PARAMS) to include in the GET request. 
                                 If str passed, must be in the form "&param1=value1&param2=value2"

    Returns:
    `Response` object, with status:
        - <Response [200]> if successful 
        - <Response [404]> or other <Response [status code]> if unsuccessful 

    """

    payload_str = ""
    if type(payload) is dict:
        payload_str = "&".join("%s=%s" % (k,v) for k,v in payload.items())
    elif type(payload) is str:
        payload_str = payload
    
    return requests.get(_url(endpoint), headers=HEADER, params=payload_str)


def get_datasets_df():
    """
    Fetches a list of available datasets from https://www.ncdc.noaa.gov/cdo-web/api/v2/datasets	

    Returns:
    Pandas DataFrame with description of available datasets.

    """

    response = get_endpoint("datasets").json()
    results = response['results']
    return pd.DataFrame(results) 


def get_dataset_info(dataset_id=None):
    if dataset_id in DATASET_IDS:
        return get_endpoint(f"datasets/{dataset_id}")
    else:
        print("Invalid dataset ID. Please use one of the following: '" + "', '".join(DATASET_IDS) + "'")


def get_data(payload={'datasetid':'NORMAL_HLY'}):
    """
    This function actually fetches the data. 

    Args:
    payload (dict or str): Key-value pairs for acceptable parameters (VALID_PARAMS) to include in the GET request. 
                                 If str passed, must be in the form "&param1=value1&param2=value2"

    Returns:
    `Response` object, with status:
        - <Response [200]> if successful 
        - <Response [404]> or other <Response [status code]> if unsuccessful 

    """

    """
    payload_str = ""
    if type(payload) is dict:
        payload['datasetid'] = dataset_id
        payload_str = "&".join("%s=%s" % (k,v) for k,v in payload.items())
    elif type(payload) is str:
        payload_str = f"datasetid={dataset_id}&{payload}"
    """

    return get_endpoint("data", payload)

