import json
from turtle import right
import numpy as np
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pandas.core.api import DataFrame

dir = './data/'
write_file = './appended_data.json'
# number of rows to fetch
number_of_rows = 10
data = []
supported_modes = ['stats','listen_time_plot','top_artists']

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
    print(int(listen_time["mins_played"].sum()))

    print(f'\nTop {number_of_rows} artists (count of songs played by artist): ')
    print(listen_time['artist'].value_counts().head(number_of_rows).to_string(header=False,index=True))

    min_by_artist = df.groupby('artist')['mins_played'].sum().astype(int)

    print('\nMinutes played per artist')
    print(min_by_artist.sort_values(ascending=False).head(number_of_rows).to_string(header=False,index=True))
    
    min_by_song = df.groupby('track').aggregate(
        {'artist':'first',
            'mins_played':'sum'}
    )

    min_by_song['mins_played'] = min_by_song['mins_played'].astype(int)

    print('\nMinutes played per song')
    print(min_by_song.sort_values(by='mins_played',ascending=False).head(number_of_rows).to_string(header=False,index=True))

def fav_artist_by_year(df:DataFrame):
    yearly = df.groupby(['year','artist'],as_index=False)['mins_played'].sum()
    yearly['rank'] = yearly.groupby(['year'])['mins_played'].rank('dense',ascending=False)
    top = yearly[yearly['rank'] <= number_of_rows].reset_index(drop=True)

    color_map = {artist: plt.cm.viridis(i/len(top['artist'].unique())) for i, artist in enumerate(top['artist'].unique())}

    fig,ax = plt.subplots(figsize=(20,.95*number_of_rows),facecolor='#023d42')


    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.yaxis.set_ticks([])
    
    ax.set_facecolor('#023d42')
    ax.set_xticks(top['year'])
    ax.set_xticklabels(top['year'],color='white')

    plt.ylim(-1,number_of_rows+2)
    plt.subplots_adjust(left=0,right=1)
    plt.title(f'Top {number_of_rows} artists since {top["year"].min()}',color='white') 

    for year,data in top.groupby('year'):
        for i,value in data.sort_values(by='rank').iterrows():
            artist = value['artist']
            if ' 'in artist:
                artist = '\n'.join(str(artist).split(' '))
            rank = int(value['rank'])
            ax.text(year,rank,artist,color='white',ha='center',va='center')
            ax.scatter(year,rank,label=i,color=color_map[value['artist']],marker='o')

    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()

def listen_time_by_year(df:DataFrame):
    yearly =df.groupby(df['year'])['mins_played'].sum()
    _,ax = plt.subplots()
    yearly.plot(kind='bar',title='Minutes played by year',ylabel='Minutes played',xlabel='year')
    for i,v in enumerate(yearly):
        ax.text(i,v,str(int(v)),ha='center',va='bottom')
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
    # TODO: mins_played is float64, make it an int for easier visualization 
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
        case 'listen_time_plot':
            listen_time_by_year(df)
        case 'top_artists':
            fav_artist_by_year(df)
        case s:
            print(f'Unknown option {s}, available options are: \n{" ".join(supported_modes)}')
            print_stats(df)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Spotify JSON data analyser script')

    parser.add_argument('-d', type=str,help='Specifies a folder containing unziped Spotify data (defaults to ./data/)')
    parser.add_argument('-n',type=int,help='Specified number of rows to show')

    parser.add_argument('mode',nargs='?',default='stats',help=f'supported modes: {" ".join(supported_modes)}, defaults to stats')

    args = parser.parse_args()

    if args.d:
        # change default dir
        dir = args.d

    if args.n:
        number_of_rows = args.n

    main(args.mode)

