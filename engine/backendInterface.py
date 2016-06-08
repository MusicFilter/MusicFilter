import time
from datetime import datetime
from engine import objects
import dbaccess


"""
Get all artists from DB
"""
def getArtists(search):
    return dbaccess.getArtists("%" + search + "%")


"""
Get all distinct countries from DB
"""
def getCountries(search):
    return dbaccess.getCountries("%" + search + "%")


"""
Get all distinct genres from DB
"""
def getGenres(search):
    return dbaccess.getGenres("%" + search + "%")


"""
Get top trending playlists
Trending = maximal hit count
:returns: [list] of [playlist] objects
:param: count [int] - how many entries to return (def. is 4)
"""
def getTrending(count=4):

    res = dbaccess.getTrending(count)
    trending = []

    # create playlist objects
    for p in res:
        trending.append(getPlaylistById(p['id']))
    
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
    
    for p in res:
        playlist = getPlaylistById(p['id'])
        playlist.getElapsed()
        newest.append(playlist)
    
    return newest


"""
Get playlist object by its playlist_name filed
:returns: [playlist] object or -1 if nothing was found
:param: playlist_name [int] playlist Name
"""
def getPlaylistsByName(playlist_name):
    playlist = dbaccess.getPlaylistsByName("%" + playlist_name + "%")
    return playlist


def incrementHitCount(playlist_id):
    dbaccess.incrementHitCount(playlist_id)
    

"""
Get playlist object by its playlist_id filed
:returns: [playlist] object or -1 if nothing was found
:param: playlist_id [int] playlist ID
"""
def getPlaylistById(playlist_id):
    playlist = dbaccess.getPlaylistById(playlist_id)

    if playlist is None:
        return -1

    p = objects.playlistFactory(playlist, type=objects.DB_ENTRY)
    updateFilters(p)
    
    return p





"""
Create a playlist using the given [postdict]
:returns: [playlist]
:param: [postdict]
    name [string] of the playlist
    genres [list] of [int] genres ID
    countries [list] of [int] country ID
    artists [list] of [int] artists ID
    decades [list] of [int] decades ID
    freetext [string] free text
    live [int]
    cover [int]
    withlyrics [int]
    text [string]
"""
def genratePlaylist(postdict):
    print 'generating a playlist from the following postdict:\n{0}'.format(postdict)

    # create a new playlist object
    playlist = objects.playlistFactory(postdict, type=objects.POSTDICT)
    playlist.description = buildDescription(postdict)

    # Create the playlist and connect it to all the tables
    playlist.id = dbaccess.createPlaylist(playlist)

    # Load videos by filter and set them in new playlist
    playlist.video_list = loadVideos(playlist, commit=True)

    return playlist


"""
Loads videos using the given playlist
:returns: [list] of [int] video ids
:param: [playlist] object
:param: [boolean] commit to DB
"""
def loadVideos(playlist, commit):

    if commit:
        # reload videos from DB
        video_ids = dbaccess.loadVideos(playlist, mode=objects.LOAD_FROM_MONSTERQUERY)
        video_ids = [x[0] for x in video_ids]

        # insert updated video list to DB
        dbaccess.updateVideoList(playlist.id, video_ids)

    else:
        video_ids = dbaccess.loadVideos(playlist)
        video_ids = [x[0] for x in video_ids]
    
    return video_ids


"""
Returns most popular items
:returns: [tuple] of [string] - top_artist, top_genre, top_decade, top_country
"""
def getTopHits():

    # get results from DB
    res = dbaccess.getTopArtist()
    top_artist = '' if res is None else res[0]

    res = dbaccess.getTopGenre()
    top_genre = '' if res is None else res[0]

    res = dbaccess.getTopDecade()
    top_decade = '' if res is None else res[0]

    res = dbaccess.getTopCountry()
    top_country = '' if res is None else res[0]

    return top_artist, top_genre, top_decade, top_country


def buildDescription(postdict):
    
    props = ""
    
    if postdict['live']:
        props += "live, "
        
    if postdict['cover']:
        props += "cover versions, "
        
    if postdict['withyrics']:
        props += "lyrics included, "
        
    if props != "":
        props = " " + props[:-2]
        
    string_genres = ', '.join(str(x[1]) for x in postdict['genres'])
    string_countries = ', '.join(str(x[1]) for x in postdict['countries'])
    string_artists = ', '.join(str(x[1]) for x in postdict['artists'])
    string_decades = ', '.join(str(x) + 's' for x in postdict['decades'])
    string_freetext = ''
        
    if string_artists != "":
        string_artists = " by " + string_artists
        
    if string_genres != "":
        string_genres = " of type " + string_genres
        
    if string_decades != "":
        string_decades = " from the " + string_decades
    
    if string_countries != "":
        string_countries = " from " + string_countries
        
    if postdict['text'] != "":
        string_freetext = " that have " + postdict['text'] + " in the title "
        
    return 'Listening to {0} videos{1}{2}{3}{4}{5}!'.format(
             props, string_freetext, string_genres, string_artists, string_decades, string_countries)


"""
Update [playlist] object filters from DB
"""
def updateFilters(playlist):
    playlist.artists = dbaccess.getFilterArtists(playlist.id)
    playlist.countries = dbaccess.getFilterCountries(playlist.id)
    playlist.genres = dbaccess.getFilterGenres(playlist.id)
    playlist.decades = dbaccess.getFilterDecades(playlist.id)
