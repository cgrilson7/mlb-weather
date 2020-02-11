from bs4 import BeautifulSoup
import requests
import csv
import re
import datetime
from dateutil.parser import parse
from dateutil.tz import gettz
import numpy as np
from tqdm import tqdm

tzinfos = {"ET": gettz("America/New_York")}

def scrape_box_score(link):
    game_text = requests.get('https://www.baseball-reference.com' + link['href']).text
    game_soup = BeautifulSoup(game_text,features='html.parser')
    scorebox = game_soup.find('div', { 'class': 'scorebox_meta' })
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
    season_text = requests.get("https://www.baseball-reference.com/leagues/MLB/" + year + "-schedule.shtml").text
    season_soup = BeautifulSoup(season_text, features='html.parser')
    links = season_soup.find_all('a', href=True, text='Boxscore')
    box_scores = []
    for link in tqdm(links):
        box = parse_box_score(link)
        box_scores.append(box)
    return box_scores

