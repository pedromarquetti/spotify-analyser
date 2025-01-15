import json
from ntpath import isfile
import os
import argparse
from time import sleep
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from pandas.core.api import DataFrame

from helpers.fetch_genres import fetch_artist_genre, get_artist_id


dir = './data/'
write_file = './appended_data.json'
# number of rows to fetch
number_of_rows = 10
data = []
supported_modes = ['stats','listen_time_plot','top_artists','top_genre']

# setting global graphs
mpl.rcParams['xtick.color'] = 'white'
mpl.rcParams['text.color'] = 'white'
fig,ax = plt.subplots(figsize=(20,.95*number_of_rows),facecolor='#191414')
fig.subplots_adjust(left=0,right=1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks([])
ax.set_facecolor('#191414')

def add_text(x,y,text,ha='center',va='center'):
    """Helper function for adding text to graph"""
    ax.text(x,y,text,color='white',ha=ha,va=va)

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
    unique_artists = df['artist'].unique()
    # filter out 0ms of listen time
    listen_time = df.query('ms_played >0')
    print(f'Total listen time:')
    print(int(listen_time["mins_played"].sum()))

    print(f'\nYou listened to {len(unique_artists)} unique artists')
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

    ax.set_xticks(top['year'])

    plt.title(f'Top {number_of_rows} artists since {top["year"].min()}',color='white') 

    for year,data in top.groupby('year'):
        for i,value in data.sort_values(by='rank').iterrows():
            artist = value['artist']
            if ' 'in artist:
                artist = '\n'.join(str(artist).split(' '))
            rank = int(value['rank'])
            # ax.text(year,rank,artist,color='white',ha='center',va='center')
            add_text(year,rank,artist)
            ax.scatter(year,rank,label=i,color=color_map[value['artist']],marker='o')

    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()

def listen_time_by_year(df:DataFrame):
    yearly =df.groupby(df['year'])['mins_played'].sum()
    yearly.plot(kind='bar',title='Minutes played by year',ylabel='Minutes played',xlabel='year',color='#1ED760')
    for i,v in enumerate(yearly):
        add_text(i,v,str(int(v)),va='bottom')
    plt.show()

def top_genre(df:DataFrame):
    genres_df = pd.DataFrame()
    genres_list=[]

    track_id = df['track_id'].unique().tolist()

    track_id_groups = [track_id[i:i+50] for i in range(0,len(track_id),50)] # group of 50 track IDs

    if not os.path.isfile('genres.csv'):
        print('genres file not found!\nThis script will now fetch data from spotify (this will take a while), press Ctrl-C to cancel!')
        sleep(20)
        for track_id in track_id_groups:
            track_str = ','.join(track_id)
            print('getting artist ids...')
            artist_ids = get_artist_id(track_str)
            artist_id_group = [artist_ids[i:i+50] for i in range(0,len(artist_ids),50)]
            for artist_id in artist_id_group:
                artists_str = ','.join(artist_id)
                print('fetching genres...')
                genres = fetch_artist_genre(artists_str)
                genres_list.extend(genres)
        genres_df['genres'] = genres_list
        genres_df.to_csv('genres.csv')
    else:
        genres_df = pd.read_csv('genres.csv')

    print(genres_df['genres'].value_counts().head(number_of_rows))

def main(mode:str):
    if len(data) == 0:
        # if user specifies multiple flags, dont keep appending to data if it already contains values
        read_files()

    # global DataFrame that will be used by all functions
    music_df = pd.DataFrame(data)

    # converting 'ts' column to datetime
    music_df['ts'] = pd.to_datetime(music_df['ts'])
    datetime = music_df['ts'].dt
    music_df['year'] = datetime.year
    music_df['month'] = datetime.month
    # TODO: mins_played is float64, make it an int for easier visualization 
    music_df['mins_played'] = music_df['ms_played'] / 60000
    music_df['hours_played'] = music_df['mins_played'] / 60
    # get track ids 
    music_df['track_id'] = music_df['spotify_track_uri'].str.split(':').str[-1]

    # filtering Podcast episodes 
    music_df = music_df[music_df['track_id'].notna()]

    # renaming columns
    music_df.rename({
        'master_metadata_track_name':'track',
        'master_metadata_album_album_name':'album',
        'master_metadata_album_artist_name':'artist'
    },errors='raise',axis='columns',inplace=True)

    # TODO: add more modes 
    match mode:
        case 'stats':
            # INFO: Stats mode
            print_stats(music_df)
        case 'listen_time_plot':
            listen_time_by_year(music_df)
        case 'top_artists':
            fav_artist_by_year(music_df)
        case 'top_genre':
            top_genre(music_df)
        case s:
            print(f'Unknown option {s}, available options are: \n{" ".join(supported_modes)}')
            print_stats(music_df)

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

