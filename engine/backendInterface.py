from dummyDB import dummy_db, getRandomPlaylist
from engine.dummyDB import artist_db
import MySQLdb as mdb
import time    
from engine.objects import Playlist

# Read connection details from properties
con = mdb.connect('localhost', 'root', 'password', 'musicfilter')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET FOREIGN_KEY_CHECKS=0")

"""
Get all countries from DB
"""
def getArtists():
    
    # Return all artists from the DB to populate the list
    return sorted(artist_db, key=lambda x: x.name, reverse=False)


"""
Get all distinct countries from DB
"""
def getCountries():
    
    # select alphabetically sorted distinct countries from DB...
    return sorted(['United States', 'United Kingdom', 'Ireland', 'Australia', 'Canada'])


"""
Get all distinct genres from DB
"""
def getGenres():
    
    # select alphabetically sorted distinct countries from DB...
    return sorted(['Rock', 'Blues', 'Pop', 'Alternative Rock', 'Pop Rock', 'Gospel', 'Shoegaze', 'Punk Rock', 'Britpop'])

"""
Get top trending playlists
Trending = maximal hit count
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getTrending(count=4):

    # call to DB should return a list of length 'count'
    # containing [playlist] object that have maximal hits, sorted descending

    # dummy db
    return sorted(dummy_db, key=lambda x: x.hits, reverse=True)[0:count]

"""
Get newest playlists
Newest = most recently added
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getNewest(count=4):

    # call to DB should return a list of length 'count'
    # containing [playlist] object that have their createdOn field closest to now

    # dummy db
    for p in dummy_db:
        p.getElapsed()
    return sorted(dummy_db, key=lambda x: x.createdOn, reverse=True)[0:count]


"""
Get playlist object by its playlist_id filed
:returns: [playlist] object or -1 if nothing was found
:param: playlist_id [int] playlist ID
"""
def getPlaylistById(playlist_id):

    # call DB to get the playlist entry corresponding to playlist_id
    # create a playlist object to this playlist entry
    # return the playlist object

    # dummy DB
    for p in dummy_db:
        if p.id == int(playlist_id):
            return p

    return -1


"""
Update hit count to DB after watching the playlist
:param: playlist_id [int] playlist ID
"""
def incrementHitCount(playlist_id):

    # commit to DB playlist.id + 1

    # dummy DB
    p = getPlaylistById(playlist_id)
    p.hits += 1


"""
Create a playlist using the given filter parameters
:returns: [playlist]
:param] name [string] of the playlist
:param: genres [list] of [int] genres ID
:param: countries [list] of [int] country ID
:param: artists [list] of [int] artists ID
:param: decades [list] of [int] decades ID
:param: freetext [string] free text
"""
def genratePlaylist(name, genres, countries, artists, decades, freetext, live, cover, withlyrics):

    # implement logic to create customized playlist by the given parameters
    # run as a seperate process to allow preloader

    # the id should come from DB
    #id = getRandomPlaylist().id
    
    # dummyDB
    print 'generating a playlist from the following parameters:\n' \
          'Genres: {0}\n' \
          'Countries: {1}\n' \
          'Artists: {2}\n' \
          'Decades: {3}\n' \
          'Freetext: {4}\n' \
          'Live: {5}\n' \
          'Cover: {6}\n' \
          'With Lyrics: {7}\n' \
          .format(genres, countries, artists, decades, freetext, live, cover, withlyrics)

    # Create the playlist and connect it to all the tables
    id = createPlaylist(name, genres, countries, artists, decades, freetext, live, cover, withlyrics)          
    # Load videos by filter and set them in new playlist
    videos = loadVideos(id, genres, countries, artists, decades, freetext, live, cover, withlyrics)
    
    return id

def reloadVideos(p):
    
    # First delete current videos that are connected to this playlist then load new videos
    newVideos = loadVideos(p.id, p.genres, p.countries, p.artists, p.decades, p.freetext, p.live, p.cover, p.withlyrics)
    p.video_list = newVideos

"""
Loads videos using the given filter parameters
:returns: [playlist]
:param: id [int] playlist id
:param: genres [list] of [int] genres ID
:param: countries [list] of [int] country ID
:param: artists [list] of [int] artists ID
:param: decades [list] of [int] decades ID
:param: freetext [string] free text
"""
def loadVideos(id, genres, countries, artists, decades, freetext, live, cover, withlyrics):
    
    # Prepare user input
    string_genres = ', '.join(str(x) for x in genres)
    string_countries = ', '.join(str(x) for x in countries)
    string_artists = ', '.join(str(x) for x in artists)
    string_decades = ', '.join(str(x) for x in decades)
    if (live == 'on'):
        string_live = 1
    else:
        string_live = 0
    if (cover == 'on'):
        string_cover = 1
    else:
        string_cover = 0
    if (withlyrics == 'on'):
        string_withlyrics = 1
    else:
        string_withlyrics = 0
        
    select_data = ()
    
    # Here comes a big composite query that first generates new videos according to filter
    # Then it deletes current videos from playlist
    # Then it connects new video ids to the playlist
    
    select_command = """
    SELECT DISTINCT filtered_videos.id
    FROM   (SELECT     @a:=@a+1 AS num, video.video_id AS id
            FROM     video, artist, country, artist_genre, genre
            WHERE     video.artist_id = artist.artist_id AND
                    artist_genre.artist_id = artist.artist_id AND
                    artist_genre.genre_id = genre.genre_id AND 
    """
                    
    if (len(genres) > 0):
        select_command += "genre.genre_id IN (%s) AND \n"
        select_data = select_data + (string_genres,)
        
    if (len(countries) > 0):
        select_command += "artist.country_id IN (%s) AND \n"
        select_data = select_data + (string_countries,)
        
    if (len(artists) > 0):
        select_command += "artist.artist_id IN (%s) AND \n"
        select_data = select_data + (string_artists,)
        
    if (len(decades) > 0):
        select_command += "artist.dominant_decade IN (%s) AND \n"
        select_data = select_data + (string_decades,)
        
    if (len(freetext) > 0):
        select_command += "(video.title LIKE '%%s%' OR video.description LIKE '%%s%') AND \n"
        select_data = select_data + (freetext, freetext,)

    select_command += """          
                    video.is_live = %s AND
                    video.is_cover = %s AND
                    video.with_lyrics = %s) as filtered_videos
    WHERE     filtered_videos.num IN (SELECT     * 
                                    FROM     (SELECT FLOOR(((SELECT COUNT(*)
                                                            FROM     video, artist, country, artist_genre, genre
                                                            WHERE     video.artist_id = artist.artist_id AND
                                                                    artist_genre.artist_id = artist.artist_id AND
                                                                    artist_genre.genre_id = genre.genre_id AND
                                                                    """
                                                                    
    select_data = select_data + (string_live, string_cover, string_withlyrics,)
                                                                    
    if (len(genres) > 0):
        select_command += "genre.genre_id IN (%s) AND \n"
        select_data = select_data + (string_genres,)
        
    if (len(countries) > 0):
        select_command += "artist.country_id IN (%s) AND \n"
        select_data = select_data + (string_countries,)
        
    if (len(artists) > 0):
        select_command += "artist.artist_id IN (%s) AND \n"
        select_data = select_data + (string_artists,)
        
    if (len(decades) > 0):
        select_command += "artist.dominant_decade IN (%s) AND \n"
        select_data = select_data + (string_decades,)
        
    if (len(freetext) > 0):
        select_command += "(video.title LIKE '%%s%' OR video.description LIKE '%%s%') AND \n"
        select_data = select_data + (freetext, freetext,)

    select_command += """   
                                                                    video.is_live = %s AND
                                                                    video.is_cover = %s AND
                                                                    video.with_lyrics = %s) + 1) * RAND()) num
                                            FROM video
                                            LIMIT 110) random)
    LIMIT 100"""
    
    select_data = select_data + (string_live, string_cover, string_withlyrics,)
    
    cur.execute(select_command, select_data)
    video_ids = cur.fetchall()
    
    # Create one big insert command to minimize I/O
    insert_data = (id)
    update_command = """DELETE FROM playlist_to_video
       WHERE playlist_id = %s; 
       """
       
    for video_id in video_ids:
        update_command += """INSERT INTO playlist_to_video
           VALUES (%s, %s);
           """
        insert_data = insert_data + (id, video_id,)
    
    cur.execute(update_command, insert_data)
    con.commit()
    
    return video_ids 

"""
Creates a new playlist in the DB
:returns: [int] playlist id
:param: name [string] of the playlist
:param: genres [list] of [int] genres ID
:param: countries [list] of [int] country ID
:param: artists [list] of [int] artists ID
:param: decades [list] of [int] decades ID
:param: freetext [string] free text

"""
def createPlaylist(name, genres, countries, artists, decades, freetext, live, cover, withlyrics):
    
    # Here comes a query that inserts a new playlist
    # Then connects the playlist to artist table
    # Then connects the playlist to genre table
    # Then connects the playlist to country table
    # Then connects the playlist to decades
    
    # This id should be auto increment!
    playlist_id = 1
    
    # Create one big insert command to minimize I/O
    insert_command = """INSERT INTO playlist
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
    if (live == 'on'):
        string_live = 1
    else:
        string_live = 0
    if (cover == 'on'):
        string_cover = 1
    else:
        string_cover = 0
    if (withlyrics == 'on'):
        string_withlyrics = 1
    else:
        string_withlyrics = 0
        
    # What to do with description ??
    insert_data = (playlist_id, name, time.strftime('%Y-%m-%d %H:%M:%S'), "", 0, string_live, string_cover, string_withlyrics, freetext)
    
    for artist_id in artists:
        insert_command += """INSERT INTO playlist_artist
            VALUES (%s, %s);
            """
        insert_data = insert_data + (playlist_id, artist_id,)
    
    for country_id in countries:
        insert_command += """INSERT INTO playlist_country
            VALUES (%s, %s);
            """
        insert_data = insert_data + (playlist_id, country_id,)
    
    for genre_id in genres:
        insert_command += """INSERT INTO playlist_genre
            VALUES (%s, %s);
            """
        insert_data = insert_data + (playlist_id, genre_id,)    
    
    for decade_id in decades:
        insert_command += """INSERT INTO playlist_decade
            VALUES (%s, %s);
            """
        insert_data = insert_data + (playlist_id, decade_id,) 
    
    cur.execute(insert_command, insert_data)
    con.commit()
    
    return playlist_id

"""
Query DB if the requested playlist exists
:returns: [boolean]
:param: [int] playlist ID
"""
def isPlaylistExists(playlist_id):

    # query the DB if the playlist exists

    # dummyDB
    return True


"""
Returns most popular items
:returns: [tuple] of [string] - top_artist, top_genre, top_decade, top_country
"""
def getTopHits():

    # get results from DB

    # dummy DB
    top_artist = 'Dedi Dadon'
    top_genre = 'Classical Indie Pop Rock'
    top_decade = '1950s'
    top_country = 'Portugal'

    return top_artist, top_genre, top_decade, top_country
