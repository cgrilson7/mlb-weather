from bs4 import BeautifulSoup
import requests
import csv
import re
import datetime
from dateutil.parser import parse
from dateutil.tz import gettz
import numpy as np
from tqdm import tqdm
import pandas as pd

tzinfos = {"ET": gettz("America/New_York")}
URL = "https://www.baseball-reference.com/"

def _url(path):
    if re.search(f"^{URL}", path):
        return URL
    else:
        return URL + path

def get_season_soup(year):
    season_text = requests.get(_url("leagues/MLB/" + str(year) + "-schedule.shtml")).text
    return BeautifulSoup(season_text, features='html.parser')

def get_all_hrefs(soup, text='Boxscore'):
    links = soup.find_all('a', href=True, text=text)
    return [link['href'] for link in links]

def get_game_soup(game_href):
    game_text = requests.get(_url(game_href)).text
    return BeautifulSoup(game_text,features='html.parser')

def get_linescore(game_soup):
    linescore = game_soup.find('table', {'class': 'linescore'})
    return linescore

def get_linescore_df(linescore):
    
    table_headers = linescore.find_all('th')[1:]
    headers_cleaned = [re.search("((\d+|[RHE]))", th.prettify()).group(1) if re.search("((\d+|[RHE]))", th.prettify()) else 'Team' for th in table_headers]
    
    table_rows = linescore.find_all('tr')
    rows_cleaned = []
    
    for tr in table_rows:
        table_data = tr.find_all('td')[1:] # skip first column
        row = [tr.text.strip() for tr in table_data if tr.text.strip()] # 
        if row:
            rows_cleaned.append(row)

    # Create data frame from cleaned rows and assign headers_cleaned as column names 
    df = pd.DataFrame(rows_cleaned, columns = headers_cleaned)

    # Convert columns to numeric (except for Team names)
    int_cols = df.columns.drop('Team')
    df[int_cols] = df[int_cols].apply(pd.to_numeric, errors='coerce')

    return df

def get_scorebox(game_soup):
    scorebox = game_soup.find('div', { 'class': 'scorebox_meta' })
    return scorebox

def parse_scorebox(scorebox):
    pass

def get_start_end_venue(scorebox):
    divs = scorebox.find_all('div')
    time, venue, duration, date = None, None, None, None
    for div in divs:
        if (div.text.startswith('Start Time: ')):
            time = div.text[12:]
        elif (div.text.startswith('Venue: ')):
            venue = div.text[7:]
        elif (div.text.startswith('Game Duration: ')):
            duration = div.text[15:]
        elif (div.text.startswith('Monday')):
            date = div.text[8:]
        elif (div.text.startswith('Tuesday')):
            date = div.text[9:]
        elif (div.text.startswith('Wednesday')):
            date = div.text[11:]
        elif (div.text.startswith('Thursday')):
            date = div.text[10:]
        elif (div.text.startswith('Friday')):
            date = div.text[8:]
        elif (div.text.startswith('Saturday')):
            date = div.text[10:]
        elif (div.text.startswith('Sunday')):
            date = div.text[8:]
    if (time == None or date == None or venue == None or duration == None):
        print(link)
    parsed_date = parse(date + ' ' + time, tzinfos=tzinfos)
    colon_index = duration.index(':')
    hours = duration[0:colon_index]
    minutes = duration[colon_index + 1:]
    end_date = parsed_date + datetime.timedelta(minutes=int(minutes),hours=int(hours))
    return [parsed_date, end_date, venue]

def scrape_season(year):
    links = get_soup_hrefs(get_season_soup(year))
    box_scores = []
    for link in tqdm(links):
        box = parse_box_score(link)
        box_scores.append(box)
    return box_scores