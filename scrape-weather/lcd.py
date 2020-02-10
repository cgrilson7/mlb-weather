import pandas as pd

LCD_STATIONS_URL = "https://www.ncdc.noaa.gov/homr/file/lcd-stations.txt"


def read_stations():
    """
    Reads a fixed-width .txt table from https://www.ncdc.noaa.gov/homr/file/lcd-stations.txt
    with LCD station metadata. 

    Table specifications found here: https://www.ncdc.noaa.gov/homr/file/LCD_Table.txt

    Returns:
    A Pandas DataFrame object.
    """
    colnames = ['WBAN_ID', 'TRANSMITTAL_ID', 'TRANSMITTAL_ID_TYPE', 'CALL_SIGN', 'FAA_ID', 'WMO_ID', 'NWSLI_ID', 'COOP_ID', 'GHCND_ID', 'CITY',
                'LOCATION', 'LOCATION_AREA', 'STATE_PROV', 'FIPS_COUNTRY_CODE', 'NWS_REGION', 'LAT_DEC', 'LON_DEC', 'ELEV_GROUND', 'ELEV_GROUND_UNIT', 'UTC_OFFSET']
    colspecs = [(0, 5), (6, 16), (17, 37), (38, 48), (49, 52), (53, 58), (59, 67), (68, 74), (75, 86), (87, 137), (138, 198),
                (199, 224), (225, 227), (228, 230), (231, 241), (242, 251), (252, 262), (263, 269), (270, 276), (277, 280)]

    df = pd.read_fwf(LCD_STATIONS_URL, names=colnames,
                     colspecs=colspecs, dtype=str)
    df[['LAT_DEC', 'LON_DEC', 'ELEV_GROUND', 'UTC_OFFSET']] = df[[
        'LAT_DEC', 'LON_DEC', 'ELEV_GROUND', 'UTC_OFFSET']].apply(pd.to_numeric)
    return df
