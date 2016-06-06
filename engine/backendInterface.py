import time
from datetime import datetime
from engine.objects import Playlist
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
        playlist = Playlist()
        playlist.id = p['playlist_id']
        playlist.name = p['playlist_name']
        playlist.createdOn = p['creation_date']
        playlist.description = p['description']
        playlist.hits = p['play_count']

        trending.append(playlist)

    
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
def getPlaylistsByName(playlist_name):
    return dbaccess.getPlaylistsByName("%" + playlist_name + "%")


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
    
    p = Playlist(
        playlist_id, playlist['playlist_name'], playlist['creation_date'], playlist['description'],playlist['play_count']
    )

    p.video_list = dbaccess.getPlaylistVideos(p.id)
    
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
    playlist = Playlist()

    # populate playlist data from postdict
    playlist.artists = postdict['artists']
    playlist.countries = postdict['countries']
    playlist.decades = postdict['decades']
    playlist.genres = postdict['genres']
    playlist.name = postdict['name']
    playlist.createdOn = datetime.now()
    playlist.description = buildDescription(postdict)
    playlist.text = postdict['text']

    # Create the playlist and connect it to all the tables
    playlist.id = dbaccess.createPlaylist(playlist)

    # Load videos by filter and set them in new playlist
    playlist.video_list = loadVideos(playlist)

    return playlist


"""
Refresh video_list
"""
def reloadVideos(p):
    
    # First delete current videos that are connected to this playlist then load new videos
    new_videos = loadVideos(p.id, p.genres, p.countries, p.artists, p.decades, p.freetext, p.live, p.cover, p.withlyrics)
    p.video_list = new_videos


"""
Loads videos using the given playlist
:returns: [list] of [int] video ids
:param: [playlist]
"""
def loadVideos(playlist):

    # Prepare user input
    genreslist = [int(x[0]) for x in playlist.genres]
    countrieslist = [int(x[0]) for x in playlist.countries]
    artistslist = [int(x[0]) for x in playlist.artists]
    decadeslist = [int(x[0]) for x in playlist.decades]
    string_freetext = '%' + playlist.text + '%'

    # reload videos from DB
    video_ids = dbaccess.loadVideos(playlist)
    video_ids = [x['id'] for x in video_ids]
    
    # insert updated video list to DB
    dbaccess.updateVideoList(playlist.id, video_ids)
    
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


def buildDescription(postdict):
    
    props = ""
    
    if postdict['live']:
        props += "live, "
        
    if postdict['cover']:
        props += "cover versions, "
        
    if postdict['withlyrics']:
        props += "lyrics included, "
        
    if props != "":
        props = " " + props[:-2]
        
    string_genres = ', '.join(str(x[1]) for x in postdict['genres'])
    string_countries = ', '.join(str(x[1]) for x in postdict['countries'])
    string_artists = ', '.join(str(x[1]) for x in postdict['artists'])
    string_decades = ', '.join(str(x[1]) for x in postdict['decades'])
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
        string_freetext = " that have " + postdict['freetext'] + " in the title, "
        
    return 'Listening to {0}videos{1}{2}{3}{4}{5}!'.format(
             props, string_freetext, string_genres, string_artists, string_decades, string_countries)