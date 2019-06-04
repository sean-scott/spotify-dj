# Spotify DJ
Let the radio DJ do the work of making your Spotify playlist.

Spotify DJ parses a list of recently-played tracks from your radio station of choice, compares them against your target Spotify playlist, and adds the missing links.

_Note: Your radio station mileage may vary. Currently, this only supports stations hosted through Securenet Systems_

# Prerequisites
[Spotipy](https://github.com/plamere/spotipy) - A Spotify Web API client for Python
```
pip install spotipy
```

# Setup
1. Populate the fields in `config.py`, including a radio station that uses the `streamdb3web.securenetsystems.net` domain for hosting their playlist history

2. Run `python scraper.py` to generate a CSV of the last number of songs played on the station. This can be run by your own cron job in the background as often as you want. This application supports batch and singular operations, altogether.

    *THIS APPLICATION SUPPORTS BATCH AND SINGULAR OPERATIONS*

    _If you understood that reference, let me know._

3. Run `python spotify.py` to read all of the CSVs generated from the aforementioned job. This will check your playlist for songs in the lists that don't exist and add them. It will then delete the CSVs to keep down the bloat.

-----

As hinted at above, you can wrap these in scheduled jobs on your machine to hit the APIs periodically and continually populate your Spotify playlist. These radio station track histories tend not to be infinite nor permanent, so it would be advisable to run the `scraper` job as often as every 30 minutes, perhaps, and the `spotify` job could be run every few hours.

Good luck, we're all counting on you.
