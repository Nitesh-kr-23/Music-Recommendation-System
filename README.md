Music Recommendation System uses Spotify API, To collect real-time music data from Spotify,  we need a Spotify developer account to get our 
credentials (Client ID, Client Secret) from Spotify to access their data.

We need to have an access token.

The client ID and secret are combined in the client_credentials variable, separated by a colon (:). 

Then, this string is encoded using Base64 encoding to create a secure representation of the credentials.

We then proceed to request an access token from the Spotify API.

With the access token, the application can now make authorized requests to retrieve music data, such as tracks, albums, artists, and 
user information, which is fundamental for building a music recommendation system using the Spotify API and Python.

Define a function responsible for collecting music data from any playlist on Spotify using the Spotipy library.

The function uses the Spotipy client to fetch information about the tracks in the specified playlist (identified by its playlist_id).

The sp.playlist_tracks method retrieves the playlist tracks. The fields parameter is used to specify the specific track information that 
is required, such as track ID, name, artists, album ID, and album name.

The function uses the sp.audio_features method to fetch audio features for each track in the playlist.

These audio features include attributes like danceability, energy, key, loudness, speechiness, acousticness, instrumentalness, liveness, valence, 
tempo, etc. These audio features provide insights into the characteristics of each track.
The extracted information for all tracks is stored in the music_data list. 

The function then creates a DataFrame from the music_data list. The DataFrame organizes the music data in a tabular format, making it 
easier to analyze and work with the collected information.

It is important to recommend the latest releases. For this, we need to give more weight to the latest releases in the recommendations.
For this we create function hybrid_recommendation based on release date  and 
get_popular_recommendations based on popularity.

After creating function we can test the final function to generate music recommendations.

Hope, this will help you to understand the use of API to collect real time data and use it.
