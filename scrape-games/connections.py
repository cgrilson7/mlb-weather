import mysql.connector
from os import getenv
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
    host=getenv('MYSQL_HOST'),
    port=3306,
    user=getenv('MYSQL_USER'),
    password=getenv('MYSQL_PASS'),
    database="mlbweather")

    return connection

