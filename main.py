import json
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.api import DataFrame

DEFAULT_FILEPATH = './data/'
WRITE_FILE = './appended_data.json'
# number of rows to fetch
NUMBER_OF_ROWS =100

# change max rows before truncating
pd.set_option('display.max_rows', NUMBER_OF_ROWS)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_seq_items', None)

data = []


def read_files():
    directory = os.fsencode(DEFAULT_FILEPATH)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.endswith('.json'):

            with open(f'{DEFAULT_FILEPATH}/{filename}') as fread:
                json_data = json.load(fread)
                data.extend(json_data)

def write_to_file():
    with open(WRITE_FILE, 'w') as fwrite:
        fwrite.write(f'{data}')

def print_stats(df:DataFrame):
    # filter out 0ms of listen time
    listen_time = df.query('ms_played >0')
    print(f'Total listen time:')
    print(listen_time["mins_played"].sum())

    print(f'\nTop {NUMBER_OF_ROWS} artists: ')
    print(listen_time['master_metadata_album_artist_name'].value_counts().head(NUMBER_OF_ROWS).to_string(header=False,index=True))

    min_by_artist = df.groupby('master_metadata_album_artist_name')[
        'mins_played'].sum()
    print('\n Minutes played per artist')
    print(min_by_artist.sort_values(ascending=False).head(NUMBER_OF_ROWS).to_string(header=False,index=True))
    
    min_by_song = df.groupby('master_metadata_track_name').aggregate(
        {'master_metadata_album_artist_name':'first',
            'mins_played':'sum'}
    )
    print('\n Minutes played per song')
    print(min_by_song.sort_values(by='mins_played',ascending=False).head(NUMBER_OF_ROWS).to_string(header=False))


def main():
    read_files()
    df = pd.DataFrame(data)
    df['ts'] = pd.to_datetime(df['ts'])
    datetime = df['ts'].dt
    df['year'] = datetime.year
    df['month'] = datetime.month
    df['mins_played'] = df['ms_played'] / 60000
    df['hours_played'] = df['mins_played'] / 60

    print_stats(df)

if __name__ == '__main__':
    main()
