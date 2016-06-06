import time
from datetime import datetime
from engine.objects import Playlist
import dbaccess


"""
Get all artists from DB
"""
def getArtists(search):
    return dbaccess.getArtists(search)

"""
Get all distinct countries from DB
"""
def getCountries(search):
    return dbaccess.getCountries(search)


"""
Get all distinct genres from DB
"""
def getGenres(search):
    return dbaccess.getGenres(search)


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


def incrementHitCount(playlist_id):
    dbaccess.incrementHitCount(playlist_id)
