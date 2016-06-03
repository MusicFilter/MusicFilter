import MySQLdb as mdb
import time
from datetime import datetime
from engine.objects import Playlist
from password import *
from test.test_support import temp_cwd

# Read connection details from properties
con = mdb.connect('localhost', 'root', getPassword(), 'musicfilter')
cur = con.cursor(mdb.cursors.DictCursor)

"""
Get all countries from DB
"""
def getArtists():
    
    # Return all artists from the DB to populate the list
    #return sorted(artist_db, key=lambda x: x.name, reverse=False)

    cur.execute("""SELECT artist_id id, artist_name name
        FROM  artist""")
    return cur.fetchall()


"""
Get all distinct countries from DB
"""
def getCountries():
    
    # select alphabetically sorted distinct countries from DB...
    #return sorted(['United States', 'United Kingdom', 'Ireland', 'Australia', 'Canada'])
    
    cur.execute("""SELECT country_id id, country_name name
        FROM  country""")
    return cur.fetchall()


"""
Get all distinct genres from DB
"""
def getGenres():
    
    # select alphabetically sorted distinct countries from DB...
    #return sorted(['Rock', 'Blues', 'Pop', 'Alternative Rock', 'Pop Rock', 'Gospel', 'Shoegaze', 'Punk Rock', 'Britpop'])
    
    cur.execute("""SELECT genre_id id, genre_name name
        FROM  genre""")
    return cur.fetchall()

"""
Get top trending playlists
Trending = maximal hit count
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getTrending(count=4):

    # call to DB should return a list of length 'count'
    # containing [playlist] object that have maximal hits, sorted descending

    cur.execute("""SELECT playlist_id, playlist_name, creation_date, description, play_count  
        FROM  playlist
        ORDER BY play_count DESC
        LIMIT %s""", (count,))
    res = cur.fetchall()
    trending = []
    
    for p in res:
        trending.append(Playlist(p['playlist_id'],p['playlist_name'],
                p['creation_date'],p['description'],p['play_count']))
        
    
    return trending

    # dummy db
    #return sorted(dummy_db, key=lambda x: x.hits, reverse=True)[0:count]

"""
Get newest playlists
Newest = most recently added
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getNewest(count=4):

    # call to DB should return a list of length 'count'
    # containing [playlist] object that have their createdOn field closest to now

    cur.execute("""SELECT playlist_id, playlist_name, creation_date, description, play_count  
        FROM  playlist
        ORDER BY creation_date DESC
        LIMIT %s""", (count,))
    res = cur.fetchall()
    newest = []
    
    for item in res:
        playlist = Playlist(item['playlist_id'],item['playlist_name'],
                item['creation_date'],item['description'],item['play_count'])
        playlist.getElapsed()
        newest.append(playlist)
    
    return newest

    # dummy db
    #for p in dummy_db:
    #    p.getElapsed()
    #return sorted(dummy_db, key=lambda x: x.createdOn, reverse=True)[0:count]



"""
Get playlist videos by playlist_id
:returns: [videos] list of video ids connected to playlist
:param: playlist_id [int] playlist ID
"""
def getPlaylistVideos(playlist_id):
    
    cur.execute("""SELECT video_id
        FROM  playlist_to_video
        WHERE playlist_id = %s
        """, (playlist_id,))
    videos = cur.fetchall()
    return [x['video_id'] for x in videos]

"""
Get playlist object by its playlist_name filed
:returns: [playlist] object or -1 if nothing was found
:param: playlist_name [int] playlist Name
"""
def getPlaylistByName(playlist_name):

    cur.execute("""SELECT playlist_id, creation_date, description, play_count 
        FROM playlist 
        WHERE playlist_name = %s
        """, (playlist_name,))
    playlist = cur.fetchone()
    
    if playlist is None:
        return -1
    
    p = Playlist(playlist['playlist_id'],playlist_name,playlist['creation_date'],
                 playlist['description'],playlist['play_count'])
    p.video_list = getPlaylistVideos(p.id)
    
    return p
    

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
    #for p in dummy_db:
    #    if p.id == int(playlist_id):
    #        return p

    #return -1


    cur.execute("""SELECT playlist_name, creation_date, description, play_count 
        FROM playlist 
        WHERE playlist_id = %s
        """, (playlist_id,))
    playlist = cur.fetchone()
    
    if playlist is None:
        return -1
    
    p = Playlist(playlist_id, playlist['playlist_name'], playlist['creation_date'],
                playlist['description'],playlist['play_count'])
    p.video_list = getPlaylistVideos(p.id)
    
    return p


"""
Update hit count to DB after watching the playlist
:param: playlist_id [int] playlist ID
"""
def incrementHitCount(playlist_id):

    # commit to DB playlist.id + 1

    # dummy DB
    #p = getPlaylistById(playlist_id)
    #p.hits += 1
    
    cur.execute("""UPDATE playlist
        SET play_count = play_count + 1
        WHERE playlist_id = %s""", (playlist_id,))
    con.commit()
    
    pass


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
    # Create new playlist object
    p = Playlist(id)
    p.name = name;
    p.video_list = videos
    p.createdOn = datetime.now()
    
    return p

def reloadVideos(p):
    
    # First delete current videos that are connected to this playlist then load new videos
    new_videos = loadVideos(p.id, p.genres, p.countries, p.artists, p.decades, p.freetext, p.live, p.cover, p.withlyrics)
    p.video_list = new_videos

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
    string_genres = ', '.join(str(x[0]) for x in genres)
    string_countries = ', '.join(str(x[0]) for x in countries)
    string_artists = ', '.join(str(x[0]) for x in artists)
    string_decades = ', '.join(str(x[0]) for x in decades)
    string_freetext = '%' + freetext + '%'
        
    select_data = ()
    
    # Here comes a big composite query that first generates new videos according to filter
    # Then it deletes current videos from playlist
    # Then it connects new video ids to the playlist
    
    select_command = """
    SELECT DISTINCT filtered_videos.id id
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
        select_command += "(video.title LIKE %s OR video.description LIKE %s) AND \n"
        select_data = select_data + (string_freetext, string_freetext,)

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
                                                                    
    select_data = select_data + (live, cover, withlyrics,)
                                                                    
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
        select_command += "(video.title LIKE %s OR video.description LIKE %s) AND \n"
        select_data = select_data + (string_freetext, string_freetext,)

    select_command += """   
                                                                    video.is_live = %s AND
                                                                    video.is_cover = %s AND
                                                                    video.with_lyrics = %s) + 1) * RAND()) num
                                            FROM video
                                            LIMIT 110) random)
    LIMIT 100"""
    
    select_data = select_data + (live, cover, withlyrics,)
    
    cur.execute(select_command, select_data)
    video_ids = cur.fetchall()
    video_ids = [x['id'] for x in video_ids]
    
    # Create one big insert command to minimize I/O
    insert_data = (id)
    update_command = """DELETE FROM playlist_to_video
       WHERE playlist_id = %s; 
       """
       
    for video_id in video_ids:
        update_command += """INSERT INTO playlist_to_video
            (playlist_id, video_id)
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
    
    # Create one big insert command to minimize I/O
    insert_command = """INSERT INTO playlist
        (playlist_name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
    desc = buildDescription(artists, genres, countries, decades, live, cover, withlyrics, freetext)
    insert_data = (name, time.strftime('%Y-%m-%d %H:%M:%S'), desc, 0, live, cover, withlyrics, freetext)
    #cur.execute(insert_command, insert_data)
    #con.commit()
    
    #insert_command = ""
    #insert_data = ()
    
    for artist in artists:
        insert_command += """INSERT INTO playlist_artist
            (playlist_id, artist_id)
            VALUES (LAST_INSERT_ID(), %s);
            """
        insert_data = insert_data + (artist[0],)
    
    for country in countries:
        insert_command += """INSERT INTO playlist_country
            (playlist_id, country_id)
            VALUES (LAST_INSERT_ID(), %s);
            """
        insert_data = insert_data + (country[0],)
    
    for genre in genres:
        insert_command += """INSERT INTO playlist_genre
            (playlist_id, genre_id)
            VALUES (LAST_INSERT_ID(), %s);
            """
        insert_data = insert_data + (genre[0],)    
    
    for decade in decades:
        insert_command += """INSERT INTO playlist_decade
            (playlist_id, decade_id)
            VALUES (LAST_INSERT_ID(), %s);
            """
        insert_data = insert_data + (decade[0],) 
    
    print insert_command
    print insert_data
    
    cur.execute(insert_command, insert_data)
    con.commit()
    
    return cur.lastrowid

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


def buildDescription(artists, genres, countries, decades, live, cover, withlyrics, freetext):
    
    props = ""
    
    if live:
        props += "live, "
        
    if cover:
        props += "cover versions, "
        
    if withlyrics:
        props += "lyrics included, "
        
    if props != "":
        props = " " + props[:-2]
        
    string_genres = ', '.join(str(x[1]) for x in genres)
    string_countries = ', '.join(str(x[1]) for x in countries)
    string_artists = ', '.join(str(x[1]) for x in artists)
    string_decades = ', '.join(str(x[1]) for x in decades)
        
    if string_artists != "":
        string_artists = " by " + string_artists
        
    if string_genres != "":
        string_genres = " of type " + string_genres
        
    if string_decades != "":
        string_decades = " from the " + string_decades
    
    if string_countries != "":
        string_countries = " from " + string_countries
        
    if freetext != "":
        string_freetext = " that have " + freetext + " in the title, "
        
    return 'Listening to{0} videos{1}{2}{3}{4}{5}!'.format(
             props, string_freetext, string_genres, string_artists, string_decades, string_countries)
