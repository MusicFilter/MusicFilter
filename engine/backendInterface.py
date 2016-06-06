import time
from datetime import datetime
from engine.objects import Playlist
import dbaccess


"""
Get top trending playlists
Trending = maximal hit count
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getTrending(count=4):

    res = dbaccess.getTrending(count)
    trending = []
    
    for p in res:
        trending.append(
            Playlist(p['playlist_id'],p['playlist_name'], p['creation_date'],p['description'],p['play_count'])
        )
    
    return trending


"""
Get newest playlists
Newest = most recently added
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getNewest(count=4):

    res = dbaccess.getNewest(count)
    newest = []
    
    for item in res:
        playlist = Playlist(
            item['playlist_id'],item['playlist_name'], item['creation_date'],item['description'],item['play_count']
        )
        playlist.getElapsed()
        newest.append(playlist)
    
    return newest


"""
Get playlist videos by playlist_id
:returns: [videos] list of video ids connected to playlist
:param: playlist_id [int] playlist ID

def getPlaylistVideos(playlist_id):
    
    cur.execute(SELECT video_id
        FROM  playlist_to_video
        WHERE playlist_id = %s
        , (playlist_id,))
    videos = cur.fetchall()

    # undict
    return [x['video_id'] for x in videos]
"""

"""
Get playlist object by its playlist_name filed
:returns: [playlist] object or -1 if nothing was found
:param: playlist_name [int] playlist Name
"""
def getPlaylistByName(playlist_name):
    playlist = dbaccess.getPlaylistByName(playlist_name)

    if playlist is None:
        return -1
    
    p = Playlist(
        playlist['playlist_id'],playlist_name,playlist['creation_date'], playlist['description'],playlist['play_count']
    )

    p.video_list = dbaccess.getPlaylistVideos(p.id)
    
    return p
    

"""
Get playlist object by its playlist_id filed
:returns: [playlist] object or -1 if nothing was found
:param: playlist_id [int] playlist ID
"""
def getPlaylistById(playlist_id):

    playlist = dbaccess.getPlaylistById(playlist_id)

    if playlist is None:
        return -1
    
    p = Playlist(
        playlist_id, playlist['playlist_name'], playlist['creation_date'], playlist['description'],playlist['play_count']
    )

    p.video_list = dbaccess.getPlaylistVideos(p.id)
    
    return p


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

    desc = buildDescription(artists, genres, countries, decades, live, cover, withlyrics, freetext)

    # Create the playlist and connect it to all the tables
    playlist_id = dbaccess.createPlaylist(
        name=name,
        desc=desc,
        genres=genres,
        countries=countries,
        artists=artists,
        decades=decades,
        freetext=freetext,
        live=live,
        cover=cover,
        withlyrics=withlyrics
    )

    # Load videos by filter and set them in new playlist
    videos = loadVideos(playlist_id, genres, countries, artists, decades, freetext, live, cover, withlyrics)

    # Create new playlist object
    p = Playlist(
        playlist_id,
        date=datetime.now(),
        name=name,
        hits=0,
        desc=desc
    )

    return p


"""
Refresh video_list
"""
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
def loadVideos(playlist_id, genres, countries, artists, decades, freetext, live, cover, withlyrics):

    # Prepare user input
    genreslist = [int(x[0]) for x in genres]
    countrieslist = [int(x[0]) for x in countries]
    artistslist = [int(x[0]) for x in artists]
    decadeslist = [int(x[0]) for x in decades]
    string_freetext = '%' + freetext + '%'

    video_ids = dbaccess.loadVideos(
        playlist_id, genreslist, countrieslist, artistslist, decadeslist, string_freetext, live, cover, withlyrics
    )

    video_ids = [x['id'] for x in video_ids]
    
    # Create one big insert command to minimize I/O
    dbaccess.updateVideoList(playlist_id, video_ids)
    
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

    dbaccess.createPlaylist(name)
    
    # Create one big insert command to minimize I/O
    insert_command = """INSERT INTO playlist
        (playlist_name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
    desc = buildDescription(artists, genres, countries, decades, live, cover, withlyrics, freetext)
    insert_data = (name, time.strftime('%Y-%m-%d %H:%M:%S'), desc, 0, live, cover, withlyrics, freetext)
    
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
    string_freetext = ''
        
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
