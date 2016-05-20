#!/usr/bin/python
# -*- coding: utf-8 -*-

#import warnings
import MySQLdb as mdb

con = mdb.connect('localhost', 'root', 'yaelushamitush2428', 'musicfilter')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET FOREIGN_KEY_CHECKS=0")

def isSongExists(songId):
    cur.execute(
    """SELECT song_id
       FROM song
       WHERE song_id = %s""", (songId,))

    msg = cur.fetchone()
    if not msg:
        return False
    return True
    
    

def isArtistExists(artistId):
    cur.execute(
    """SELECT artist_id
       FROM artist
       WHERE artist_id = %s""", (artistId,))

    msg = cur.fetchone()
    if not msg:
        return False
    return True

def isGenreExists(genreId):
    cur.execute(
    """SELECT genre_id
       FROM genre
       WHERE genre_id = %s""", (genreId,))

    msg = cur.fetchone()
    if not msg:
        return False
    return True

def insertVideo(VideoDict):
    if isSongExists(VideoDict['song_id']) == False:
        cur.execute(
            """INSERT INTO video (youtube_id, title, description, song_id,
                                    length, is_cover, is_live)
                VALUES (%s, %s, %s, %s, %s, %s, %s);""",(VideoDict['youtube_id'], VideoDict['title'], VideoDict['description'],VideoDict['song_id'], VideoDict['length'], VideoDict['is_cover'], VideoDict['is_live'])
            )
        con.commit()

        

##def insertSong(SongDict,cursor):
##
##
##def insertArtist(ArtistDict,cursor):
##
##
##def insertGenre(GenreDict,cursor):

    

