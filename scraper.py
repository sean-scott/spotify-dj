import config
import csv
import datetime
import requests
import xml.etree.ElementTree as ET
from song_datum import SongDatum

'''
Retrieves the raw XML from the server.
'''
def get_xml():
    # Get the data and parse it
    res = requests.get(config.radio_history_url)
    return ET.fromstring(res.content)

'''
Parses an XML Element and returns a list of Titles and Artists.
'''
def parse_xml(tree):
    song_data = []
    # `song` elements contain child elements such as `title`, `artist`, etc.
    for child in tree.iter("song"):

        title = ""
        artist = ""

        for song in child.iter("*"):
            if song.tag == "title":
                title = song.text
            if song.tag == "artist":
                artist = song.text

        songDatum = SongDatum(title, artist)
        song_data.append(songDatum)
    
    return song_data

'''
Generates a CSV of song data and writes to disk.
'''
def generate_csv(song_data):
    # Get current timestamp to track the file
    current_dt = datetime.datetime.now()
    timestamp = str(current_dt.year) + str(current_dt.month).zfill(2) + str(current_dt.day).zfill(2) + "_" + str(current_dt.hour).zfill(2) + str(current_dt.minute).zfill(2) + str(current_dt.second).zfill(2)

    with open('songdata_' + timestamp + '.csv', 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Title', 'Artist'])

        for song in song_data:
            # Prevent commas from getting into the CSV
            song.title = song.title.replace(',', '')
            song.artist = song.artist.replace(',', '')

            # Write the row to file
            filewriter.writerow([song.title, song.artist])


xml = get_xml()
song_data = parse_xml(xml)
generate_csv(song_data)
