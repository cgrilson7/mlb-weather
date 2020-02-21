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
import mysql.connector
from connections import get_connection

tzinfos = {"ET": gettz("America/New_York")}
URL = "https://www.baseball-reference.com/"

def _url(path):
    if re.search(f"^{URL}", path):
        return path
    else:
        return URL + path

def get_season_soup(year):
    season_text = requests.get(_url("leagues/MLB/" + str(year) + "-schedule.shtml")).text
    return BeautifulSoup(season_text, features='html.parser')

def get_all_urls(soup, text='Boxscore'):
    links = soup.find_all('a', href=True, text=text)
    return [link['href'] for link in links]

def get_game_soup(game_url):
    game_text = requests.get(_url(game_url)).text
    return BeautifulSoup(game_text,features='html.parser')

def get_linescore(game_soup):
    linescore = game_soup.find('table', {'class': 'linescore'})
    return linescore

def parse_linescore(linescore):
    table_headers = linescore.find_all('th')[1:]
    headers_cleaned = [re.search("((\d+|[RHE]))", th.prettify()).group(1) if re.search("((\d+|[RHE]))", th.prettify()) else 'Team' for th in table_headers]
    
    table_rows = linescore.find_all('tr')
    rows_cleaned = []
    
    for tr in table_rows:
        table_data = tr.find_all('td')[1:] # skip first column
        row = [tr.text.strip() for tr in table_data if tr.text.strip()] # 
        if row:
            rows_cleaned.append(row)
    
    return [headers_cleaned, rows_cleaned]

def linescore_to_df(linescore):
    
    table_headers = linescore.find_all('th')[1:] # skip column containing logos & winning/losing pitchers 
    headers_cleaned = [re.search("((\d+|[RHE]))", th.prettify()).group(1) if re.search("((\d+|[RHE]))", th.prettify()) else 'Team' for th in table_headers]
    
    table_rows = linescore.find_all('tr')
    rows_cleaned = []
    
    for tr in table_rows:
        table_data = tr.find_all('td')[1:] # skip column containing logos & winning/losing pitchers 
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
    divs = scorebox.find_all('div')
    start_time, venue, duration, date = None, None, None, None
    for div in divs:
        if (div.text.startswith('Start Time: ')):
            start_time = div.text[12:]
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
    if (start_time == None or date == None or venue == None or duration == None):
        return []
    else:
        colon_index = duration.index(':')
        hours = int(duration[0:colon_index])
        minutes = int(duration[colon_index + 1:])
        start_datetime, end_datetime = None, None
        if re.search("Local", start_time): # if this line looks like "Start Time: 6:08 p.m. Local"
            start_datetime, end_datetime = None, None
        else: # 
            start_datetime = parse(date + ' ' + start_time, tzinfos=tzinfos)
            end_datetime = start_datetime + datetime.timedelta(minutes,hours)
        return [date, start_time, start_datetime, end_datetime, hours, minutes, venue]

def scrape_game(game_url, write_to_db = True):

    game_soup = get_game_soup(game_url)

    linescore = get_linescore(game_soup)
    linescore_parsed = parse_linescore(linescore)

    away = linescore_parsed[1][0][0]
    home = linescore_parsed[1][1][0]
    
    away_score = int(linescore_parsed[1][0][-3])
    home_score = int(linescore_parsed[1][1][-3])

    scorebox = get_scorebox(game_soup)
    scorebox_parsed = parse_scorebox(scorebox)

    out = [game_url, away, home, away_score, home_score, *scorebox_parsed]

    if write_to_db:
        connection = get_connection()
        cursor = connection.cursor()
        insert_statement = "INSERT IGNORE INTO boxscores (game_url, away_full, home_full, away_score, home_score, start_date, start_time, start_datetime, end_datetime, duration_hh, duration_mm, venue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_statement, out)
        connection.commit()
        print(cursor.rowcount, "records inserted.")
        return out

    else:    
        return out

def scrape_season(year, write_to_db = True):
    season_results = []
    season_soup = get_season_soup(year)

    game_urls = get_all_urls(season_soup)

    for game_url in tqdm(game_urls):

        season_results.append(scrape_game(game_url, False))

    if write_to_db:
        connection = get_connection()
        cursor = connection.cursor()
        insert_statement = "INSERT IGNORE INTO boxscores (game_url, away_full, home_full, away_score, home_score, start_date, start_time, start_datetime, end_datetime, duration_hh, duration_mm, venue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(insert_statement, season_results)
        connection.commit()
        print(cursor.rowcount, "records inserted.")
        return season_results

    else:    
        return season_results

