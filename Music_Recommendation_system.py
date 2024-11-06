import requests
import base64
import pandas as pd
import spotipy
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity 
from spotipy.oauth2 import SpotifyOAuth

# Replace with your own Client ID and Client Secret
client_id='**********'           # Enter the client ID
client_secret='***********'      # Enter the client secret passsword

# Base64 encode the client id and client secret
client_credentials=f"{client_id}:{client_secret}"
client_credentials_base64=base64.b64encode(client_credentials.encode())

# Request the access token
token_url='https://accounts.spotify.com/api/token'
headers={'Authorization': f'Basic {client_credentials_base64.decode()}'}
data={'grant_type': 'client_credentials'}
response=requests.post(token_url,data=data,headers=headers)
if response.status_code==200:
    access_token=response.json()['access_token']
    print("Access token obtained successfully")
else:
    print("Error obtaining access token")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    

def get_playlist(playlist_id,access_token):
    # Setup Spotify with the access token
    sp=spotipy.Spotify(auth=access_token)
    # Get the tracks from the playlist
    playlist_tracks=sp.playlist_tracks(playlist_id,fields='items(track(id,name,artists,album(id,name)))')
    
    # Extract information and store in a list of dictionaries
    music_data=[]
    for info in playlist_tracks['items']:
        track=info['track']
        track_id=track['id']
        track_name=track['name']
        artists=','.join([artist['name'] for artist in track['artists']])
        album_id=track['album']['id']
        album_name=track['album']['name']
        
        # Get audio features for the track
        audio_features=sp.audio_features(track_id)[0] if track_id != 'Not available' else None
        
        # Get release date of the album
        try:
            album_info=sp.album(album_id) if album_info != 'Not available' else None
            release_date=album_info['release_date'] if album_info else None
        except:
            release_date=None
            
            # Get popularity of the track
        try:
            track_info=sp.track(track_id) if track_info != 'Not available' else None
            popularity=track_info['popularity'] if track_info else None
        except:
            popularity=None
    
        # Add track information TO DataFrame
        data={
            'track_id': track_id,
            'track_name': track_name,
            'artists': artists,
            'album_name': album_name,
            'album_id': album_id,
            'release_date': release_date,
            'popularity': popularity,
            'danceability': audio_features['danceability'] if audio_features else None,
            'energy': audio_features['energy'] if audio_features else None,
            'key': audio_features['key'] if audio_features else None,
            'loudness': audio_features['loudness'] if audio_features else None,
            'mode': audio_features['mode'] if audio_features else None,
            'speechiness': audio_features['speechiness'] if audio_features else None,
            'acousticness': audio_features['acousticness'] if audio_features else None,
            'instrumentalness': audio_features['instrumentalness'] if audio_features else None,
            'liveness': audio_features['liveness'] if audio_features else None,
            'valence': audio_features['valence'] if audio_features else None,
            'tempo': audio_features['tempo'] if audio_features else None,
            'duration_ms': audio_features['duration_ms'] if audio_features else None,
        }
        music_data.append(data)
    # Create the DataFrame
    df = pd.DataFrame(music_data)
    return df

playlist_id='3cEYpjA9oz9GiPac4AsH4n'       # Enter the playlist ID available on API
music_df=get_playlist(playlist_id, access_token)
print(music_df)

data=music_df

# Function to get Popular songs
def get_popular_recommendations(input_song_name, num_recommendations=5):
    if input_song_name not in music_df['track_name'].values:
        print(f"'{input_song_name}' not found in the dataset. Please enter valid song name.")
        return
    content_based_rec=content_based_recommendations(input_song_name,num_recommendations)
    popularity_score=music_df.loc[music_df['track_name'] == input_song_name,'popularity'].values[0]

    new_entry = pd.DataFrame({
        'track_name':[input_song_name],
        'artists':[music_df.loc[music_df['track_name'] == input_song_name,'artists'].values[0]],
        'album_name':[music_df.loc[music_df['track_name'] == input_song_name,'album_name'].values[0]],
        'release_date':[music_df.loc[music_df['track_name'] == input_song_name,'release_date'].values[0]],
        })
    
    get_popular_recommendations = pd.concat([content_based_rec,new_entry])
    get_popular_recommendations = get_popular_recommendations.sort_values(by='popularity',ascending=False)
    get_popular_recommendations = get_popular_recommendations[get_popular_recommendations['track_name'] != input_song_name]
    return get_popular_recommendations

# Function to calculate weighted popularity scores based on release date
def calculate_weighted_popularity(release_date):
    if release_date is None:
        return
    # Convert release date to datetime object
    release_date = datetime.strptime(release_date, "%Y-%m-%d")
    
    # Calculate the time spanbetween release date and today's date
    time_span=datetime.now() - release_date
    
    # Calculate the weighted popularity score based on time span
    weight = 1/(time_span.days+1)
    return weight

# Normalize the music features using Min-Max scaling
scaler = MinMaxScaler()
music_features = music_df[['danceability','energy','key','loudness','mode','speechiness','acousticness',
                           'instrumentalness','liveness','valence','tempo']].values
music_features_scaled = scaler.fit_transform(music_features)

# Function to get content-based recommendation based on music features
def content_based_recommendations(input_song_name,num_recommendations=5):
    if input_song_name not in music_df['track_name'].values:
        print(f"'{input_song_name}' not found in the dataset. Please enter valid song name.")
        return
    
    # Get the index of the input song in the music DataFrame
    input_song_index = music_df[music_df['track_name'] == input_song_name].index[0]
    
    # Calculate the similarity scores based on music features (cosine similarity)
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]],music_features_scaled)
    
    # Get the indices of the most similar songs
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]
    
    # Get the names of the most similar songs based on content-based filtering
    content_based_recommendations = music_df.iloc[similar_song_indices][['track_name','artists','album_name','release_date','popularity']]
    
    return content_based_recommendations

# Function to get Hybrid recommendations based on release_date
def hybrid_recommendations(input_song_name,num_recommendations=5,alpha=0.5):
    if input_song_name not in music_df['track_name'].values:
        print(f"'{input_song_name}' not found in the dataset. Please enter valid song name.")
        return
    content_based_rec=content_based_recommendations(input_song_name,num_recommendations)
    popularity_score=music_df.loc[music_df['track_name'] == input_song_name,'popularity'].values[0]
    weighted_popularity_score=popularity_score*calculate_weighted_popularity(
        music_df.loc[music_df['track_name'] == input_song_name,'release_date'].values[0])
    
    new_entry = pd.DataFrame({
        'track_name':[input_song_name],
        'artists':[music_df.loc[music_df['track_name'] == input_song_name,'artists'].values[0]],
        'album_name':[music_df.loc[music_df['track_name'] == input_song_name,'album_name'].values[0]],
        'release_date':[music_df.loc[music_df['track_name'] == input_song_name,'release_date'].values[0]],
        'popularity':[weighted_popularity_score]
        })
    
    hybrid_recommendations = pd.concat([content_based_rec,new_entry],ignore_text=True)
    hybrid_recommendations = hybrid_recommendations.sort_values(by='popularity',ascending=False)
    hybrid_recommendations = hybrid_recommendations[hybrid_recommendations['track_name'] != input_song_name]
    return hybrid_recommendations

input_song_name = "You Are So Beautiful"
recommendation = hybrid_recommendations(input_song_name,num_recommendations=5)
print(f"Hybrid recommended songs for '{input_song_name}': ")
print(recommendation)
print()

recommendations = get_popular_recommendations(input_song_name,num_recommendations=5)
print("Popular recommended songs for '{input_song_name}': ")
print(recommendations)
