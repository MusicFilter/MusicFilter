from dummyDB import dummy_db
from engine.dummyDB import artist_db

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
:param: [int] playlist id
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
"""
def incrementHitCount(playlist_id):

    # commit to DB playlist.id + 1

    # dummy DB
    p = getPlaylistById(playlist_id)
    p.hits += 1

