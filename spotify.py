import config
import csv
import filters
import glob
import json
import os
import spotipy
import spotipy.util as util
import sys
from song_datum import SongDatum

track_ids = []      # The tracks currently in the playlist
song_data = []      # The SongDatum objects from the CSVs
search_ids = []     # The track IDs obtained from using the records in `song_data` to search

scope = 'playlist-modify-private'

'''
Gets the tracks in the user's playlist.
'''
def get_tracks_in_playlist(sp, user_id):
    print("Getting tracks in playlist...")

    done = False
    offset = 0
    count = 0

    while not done:
        # Get 100 tracks at a time, until empty
        chunk = sp.user_playlist_tracks(user_id, config.spotify_playlist_id, limit=100, offset=offset)
        items = json.loads(json.dumps(chunk))["items"]

        if len(items) == 0:
            done = True

        for item in items:
            # Get ID of song, use to track against search query
            track_id = item["track"]["id"]
            track_ids.append(track_id)
            count += 1

        offset += 100

    print("Playlist contains {} tracks".format(count))

'''
Gets a list of tracks across all CSVs in the directory.
'''
def read_csvs():
    print("Reading CSV...")
    files = glob.glob("*.csv")
    if len(files) > 0:
        for file in files:
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count != 0: # Ignore the header
                        song_datum = SongDatum(row[0], row[1])
                        song_data.append(song_datum)
                    line_count += 1
        return 1
    else:
        print("No CSVs found in directory!")
        return 0

'''
Queries the Spotify API for the top result based on the song data.
'''
def search_tracks(sp):
    print("Searching tracks from radio...")
    for song in song_data:
        res = sp.search(q=song.title + " " + song.artist, limit=1)
        items = res["tracks"]["items"]
        if len(items) > 0:
            index = 0

            # Get the first track without any of the filter keywords in either the track name or the artists field
            # Try the first five results or until the list of results is exhausted, whichever is less
            while (index < 5 and index < len(items)):
                # If we already have the track, don't bother iterating over the list
                track_id = items[index]["id"]

                if track_id in search_ids:
                    break

                bad_record = False
                name = items[index]["name"]
                artists = items[index]["artists"]

                # `artists` is an array so make sure none of them have a filter word
                for artist in artists:
                    artist_name = artist["name"]
                    if any(x in name.lower() for x in filters.tracks) == True or any(x in artist_name.lower() for x in filters.tracks) == True:
                        bad_record = True
                        break

                # If the track name or any artists contain the filtered name, move on
                # Otherwise, add the track and break
                if bad_record == False:
                    search_ids.append(track_id)
                    break
                else:
                    index += 1

'''
Adds the searched tracks to the user's playlist.
'''
def add_to_playlist(sp, user_id):
    print("Adding tracks to playlist...")

    # Remove all instances of the track IDs the user already has in their playlist
    track_ids_to_add = [x for x in search_ids if x not in track_ids]

    if len(track_ids_to_add) > 0:
        # Add the new tracks to the playlist
        sp.user_playlist_add_tracks(user_id, config.spotify_playlist_id, track_ids_to_add)
        print("Added {} tracks to playlist".format(len(track_ids_to_add)))
    else:
        print("Nothing to add!")

'''
Deletes the CSVs.
'''
def clean_up():
    print("Cleaning up...")
    for file in glob.glob("*.csv"):
        os.remove(file)

token = util.prompt_for_user_token(config.spotify_username, scope, client_id=config.spotify_client_id, client_secret=config.spotify_client_secret, redirect_uri=config.spotify_redirect_uri)

if token:
    if read_csvs() > 0:
        sp = spotipy.Spotify(auth=token)
        user_id = json.loads(json.dumps(sp.current_user()))["id"]
        get_tracks_in_playlist(sp, user_id)
        search_tracks(sp)
        add_to_playlist(sp, user_id)
        clean_up()

else:
    print "Can't get token for", username

print("\nDone.")
