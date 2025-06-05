import json
import requests as req
import os
from dotenv import load_dotenv

load_dotenv('.env')

CLIENT_ID=os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')


if (CLIENT_ID or CLIENT_SECRET) == None:
    print(f'CLIENTID {CLIENT_ID}\nSECRET{CLIENT_SECRET}')
    raise Exception('CLIENT_ID or CLIENT_SECRET var not set!')

def get_token()->str:
    post= req.post('https://accounts.spotify.com/api/token',
                  {
                  'grant_type': 'client_credentials',
                  'client_id':CLIENT_ID,
                  'client_secret':CLIENT_SECRET
                  })
    return post.json()['access_token']

def get_artist_id(track_ids:str,token:str):
    """Gets artists id based on Track id (spotify doesn't have a direct track to artist id endpoint)"""

    ids = []
    try:
        
        get = req.get(f'https://api.spotify.com/v1/tracks?ids={track_ids}',
                      headers={
                      'Authorization':f'Bearer {token}'
                      })

        if get.status_code >400:
            raise Exception('400 HTTP code found!')

        res = get.json()

        for track in res['tracks']:
            for artist in track['artists']:
                obj :dict[str,str]= {
                    'artist_name':artist['name'],
                    'id':artist['id']
                }
                ids.append(obj)

    except Exception as e:
        print('an error occurred while getting artist id')
        raise e

    return ids

def fetch_artist_genre(artist_ids:str,token:str):
    """Helper function that fetches the genre(s) of specified artist"""
    genres = []

    try:
        get =  req.get(f'https://api.spotify.com/v1/artists?ids={artist_ids}',headers={'Authorization':f'Bearer {token}'})

        if get.status_code >400:
            raise Exception('400 HTTP code found!')

        res = get.json()

        for artist in res['artists']:
            genres.extend(artist['genres'])
    except Exception as e:
        print('An Error occurred on fetch_artist_genre func!')
        raise e

    return genres

