import requests
import pyodbc
from datetime import datetime

# Instagram Graph API credentials
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
IG_USER_ID = 'YOUR_IG_USER_ID'
API_VERSION = 'v19.0'

# SQL Server connection details
SQL_SERVER = 'your_server'
SQL_DATABASE = 'MyDataBase'
SQL_USERNAME = 'PhillipLowe'
SQL_PASSWORD = '123GreeN23!!'

# SQL Server connection string
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};'
    f'UID={SQL_USERNAME};PWD={SQL_PASSWORD}'
)

# Create tables if they don't exist
def create_tables(cursor):
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'IG_Comments')
        CREATE TABLE IG_Comments (
            id NVARCHAR(100),
            text NVARCHAR(MAX),
            timestamp DATETIME
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'IG_Insights')
        CREATE TABLE IG_Insights (
            metric NVARCHAR(100),
            value INT,
            end_time DATETIME
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'IG_Media')
        CREATE TABLE IG_Media (
            id NVARCHAR(100),
            caption NVARCHAR(MAX),
            media_type NVARCHAR(50),
            media_url NVARCHAR(MAX),
            timestamp DATETIME
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'IG_Users')
        CREATE TABLE IG_Users (
            id NVARCHAR(100),
            username NVARCHAR(100),
            followers_count INT,
            follows_count INT,
            media_count INT
        )
    """)

# Fetch media items
def fetch_media():
    url = f'https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}/media'
    params = {'fields': 'id,caption,media_type,media_url,timestamp', 'access_token': ACCESS_TOKEN}
    response = requests.get(url, params=params)
    return response.json().get('data', [])

# Fetch comments for each media item
def fetch_comments(media_id):
    url = f'https://graph.facebook.com/{API_VERSION}/{media_id}/comments'
    params = {'fields': 'id,text,timestamp', 'access_token': ACCESS_TOKEN}
    response = requests.get(url, params=params)
    return response.json().get('data', [])

# Fetch insights
def fetch_insights():
    metrics = ['impressions', 'reach', 'profile_views', 'follower_count']
    url = f'https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}/insights'
    params = {'metric': ','.join(metrics), 'period': 'day', 'access_token': ACCESS_TOKEN}
    response = requests.get(url, params=params)
    return response.json().get('data', [])

# Fetch user info
def fetch_user_info():
    url = f'https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}'
    params = {'fields': 'id,username,followers_count,follows_count,media_count', 'access_token': ACCESS_TOKEN}
    response = requests.get(url, params=params)
    return response.json()

# Insert data into SQL Server
def insert_data():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    create_tables(cursor)

    # Insert media
    media_items = fetch_media()
    for media in media_items:
        cursor.execute("""
            INSERT INTO IG_Media (id, caption, media_type, media_url, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, media['id'], media.get('caption', ''), media['media_type'], media['media_url'], media['timestamp'])

        # Insert comments for each media
        comments = fetch_comments(media['id'])
        for comment in comments:
            cursor.execute("""
                INSERT INTO IG_Comments (id, text, timestamp)
                VALUES (?, ?, ?)
            """, comment['id'], comment.get('text', ''), comment['timestamp'])

    # Insert insights
    insights = fetch_insights()
    for insight in insights:
        for value_entry in insight.get('values', []):
            cursor.execute("""
                INSERT INTO IG_Insights (metric, value, end_time)
                VALUES (?, ?, ?)
            """, insight['name'], value_entry.get('value', 0), value_entry.get('end_time', datetime.now().isoformat()))

    # Insert user info
    user_info = fetch_user_info()
    cursor.execute("""
        INSERT INTO IG_Users (id, username, followers_count, follows_count, media_count)
        VALUES (?, ?, ?, ?, ?)
   