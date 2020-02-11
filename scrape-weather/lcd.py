import pandas as pd
import numpy as np
from math import radians

LCD_STATIONS_URL = "https://www.ncdc.noaa.gov/homr/file/lcd-stations.txt"


def get_stations_dataframe():
    """
    Reads a fixed-width .txt table from https://www.ncdc.noaa.gov/homr/file/lcd-stations.txt
    with LCD station metadata. 

    Table specifications found here: https://www.ncdc.noaa.gov/homr/file/LCD_Table.txt

    Returns:
    A Pandas DataFrame of the station metadata.
    """
    colnames = ['WBAN_ID', 'TRANSMITTAL_ID', 'TRANSMITTAL_ID_TYPE', 'CALL_SIGN', 'FAA_ID', 'WMO_ID', 'NWSLI_ID', 'COOP_ID', 'GHCND_ID', 'CITY',
                'LOCATION', 'LOCATION_AREA', 'STATE_PROV', 'FIPS_COUNTRY_CODE', 'NWS_REGION', 'LAT_DEC', 'LON_DEC', 'ELEV_GROUND', 'ELEV_GROUND_UNIT', 'UTC_OFFSET']
    # colspecs: list of tuples of field start/end positions
    colspecs = [(0, 5), (6, 16), (17, 37), (38, 48), (49, 52), (53, 58), (59, 67), (68, 74), (75, 86), (87, 137), (138, 198),
                (199, 224), (225, 227), (228, 230), (231, 241), (242, 251), (252, 262), (263, 269), (270, 276), (277, 280)]

    # read from URL, setting all dtypes to str
    df = pd.read_fwf(LCD_STATIONS_URL, names=colnames, colspecs=colspecs, dtype=str)

    # drop rows with NA in any of WMO_ID, WBAN_ID, LAT_DEC, LON_DEC
    df.dropna(subset=['WMO_ID', 'WBAN_ID', 'LAT_DEC', 'LON_DEC'], inplace=True)

    # Concatenate to create "LCD_ID", the identifier for station csv files on the LCD access page
    df['LCD_ID'] = df['WMO_ID'] + "0" + df['WBAN_ID']

    # Convert certain columns to numeric
    df[['LAT_DEC', 'LON_DEC', 'ELEV_GROUND', 'UTC_OFFSET']] = df[['LAT_DEC', 'LON_DEC', 'ELEV_GROUND', 'UTC_OFFSET']].apply(pd.to_numeric)

    return df

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between (lat1, lon1) and (lat2, lon2) using the haversine formula.
    Note: this method 

    Args:
    required
        - lat1, lon1, lat2, lon2 (float): the latitudes and longitudes of two points 

    Returns:
    km (float): the distance between the two specified points, in kilometers
    """
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 # difference between latitudes
    dlon = lon2 - lon1 # difference between longitudes
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    km = 6367 * c
    return km

def get_nearest_stations(stations_df, lat, lon, n=1):
    """
    Given a Pandas DataFrame of the LCD stations and their coordinates,
    calculates the haversine distance between the supplied point and all stations in the DataFrame,
    sorts by distance, and returns the 'n' nearest stations (as a subset of the DataFrame). 

    Args:
    required
        - stations_df (Pandas DataFrame): either the output of get_stations_dataframe() or a DataFrame with columns 'LAT_DEC' and 'LON_DEC'
        - lat (float): the latitude of the point of interest
        - lon (float): the longitutde of the point of interest

    optional
        - n (int): the number of nearest stations (rows) to return
    """
    # Vectorize haversine() on supplied coordinates and NumPy-ified lat, long columns in DataFrame
    stations_df['distance'] = haversine(lat, lon, stations_df['LAT_DEC'].to_numpy(), stations_df['LON_DEC'].to_numpy())
    # Order by distance (ascending)
    stations_df.sort_values(by=['distance'], inplace=True)
    # Return the top n rows
    return stations_df.head(n=n)

