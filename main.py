import json
import math
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.api import DataFrame

dir = './data/'
write_file = './appended_data.json'
# number of rows to fetch
number_of_rows = 10
data = []


def read_files():
    """Helper function that reads folder for JSON files containing Spotify data and saves it to a global data array"""
    directory = os.fsencode(dir)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.endswith('.json'):

            with open(f'{dir}/{filename}') as fread:
                json_data = json.load(fread)
                data.extend(json_data)

def write_to_file():
    with open(write_file, 'w') as fwrite:
        fwrite.write(f'{data}')

def print_stats(df:DataFrame):
    # filter out 0ms of listen time
    listen_time = df.query('ms_played >0')
    print(f'Total listen time:')
    print(listen_time["mins_played"].sum())

    print(f'\nTop {number_of_rows} artists (count of songs played by artist): ')
    print(listen_time['artist'].value_counts().head(number_of_rows).to_string(header=False,index=True))

    min_by_artist = df.groupby('artist')[
        'mins_played'].sum()
    print('\n Minutes played per artist')
    print(min_by_artist.sort_values(ascending=False).head(number_of_rows).to_string(header=False,index=True))
    
    min_by_song = df.groupby('track').aggregate(
        {'artist':'first',
            'mins_played':'sum'}
    )
    print('\nMinutes played per song')
    print(min_by_song.sort_values(by='mins_played',ascending=False).head(number_of_rows).to_string(header=False,index=True))

#TODO: implement graph plotting func
def plot_graphs(df:DataFrame):

    # listen_time['master_metadata_album_artist_name'].value_counts().head(n).plot(kind='bar',title=f'top {n} artists of all time')
    # plt.show()
    pass

def artist_by_year_graph(df:DataFrame):
    yearly =df.groupby(df['year'])['mins_played'].sum()
    _,ax = plt.subplots()
    yearly.plot(kind='bar',title='Minutes played by year',ylabel='Minutes played',xlabel='year')
    for i,v in enumerate(yearly):
        ax.text(i,v,str(v),ha='center',va='bottom')
    plt.show()

def main(mode:str):
    if len(data) == 0:
        # if user specifies multiple flags, dont keep appending to data if it already contains values
        read_files()

    # global DataFrame that will be used by all functions
    df = pd.DataFrame(data)

    # converting 'ts' column to datetime
    df['ts'] = pd.to_datetime(df['ts'])
    datetime = df['ts'].dt
    df['year'] = datetime.year
    df['month'] = datetime.month
    df['mins_played'] = df['ms_played'] / 60000
    df['hours_played'] = df['mins_played'] / 60

    # renaming columns
    df.rename({
        'master_metadata_track_name':'track',
        'master_metadata_album_album_name':'album',
        'master_metadata_album_artist_name':'artist'
    },errors='raise',axis='columns',inplace=True)

    # TODO: add more modes 
    match mode:
        case 'stats':
            # INFO: Stats mode
            print_stats(df)
        case 'top-plot':
            artist_by_year_graph(df)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Spotify JSON data analyser script')
    parser.add_argument('-s',action='store_true',help='Runs script in Stats mode (this mode prints top songs/artists)')
    parser.add_argument('-t','--top-plot',action='store_true',help='plot top artists graph')

    parser.add_argument('-d', type=str,help='Specifies a folder containing unziped Spotify data (defaults to ./data/)')
    parser.add_argument('-n',type=int,help='Specified number of rows to show')

    args = parser.parse_args()

    if args.d:
        # change default dir
        dir = args.d

    if args.n:
        number_of_rows = args.n

    if args.s:
        main('stats')
        # using pass to accept multiple flags
        pass
    if args.top_plot :
        main('top-plot')
        pass


