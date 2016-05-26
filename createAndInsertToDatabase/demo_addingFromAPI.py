#!/usr/bin/python
# -*- coding: utf-8 -*-

#import warnings
import MySQLdb as mdb

con = mdb.connect('localhost', 'root', 'password', 'musicfilter')

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

def insertVideo(VideoDict, SongDict):
    if isSongExists(VideoDict['song_id']) == False:
        cur.execute(
            """INSERT INTO video (youtube_id, title, description, song_id,
                                    length, is_cover, is_live)
                VALUES (%s, %s, %s, %s, %s, %s, %s);""",(VideoDict['youtube_id'], VideoDict['title'], VideoDict['description'],VideoDict['song_id'], VideoDict['length'], VideoDict['is_cover'], VideoDict['is_live'])
            )
        con.commit()
        insertSong(SongDict)
        

def insertSong(SongDict, ArtistDict, GenreDict):
    cur.execute(
            """INSERT INTO song (song_id, song_name, artist_id, year,
                                    genre_id)
                VALUES (%s, %s, %s, %s, %s);""",(SongDict['song_id'],SongDict['song_name'], SongDict['artist_id'], SongDict['year'], SongDict['genre_id'])
            )
    con.commit()
    if isArtistExists(SongDict['artist_id']) == False:
        insertArtist(ArtistDict)
    if isGenreExists(SongDict['genre_id']) == False:
        insertGenre(GenreDict)
        


def insertArtist(ArtistDict):
    cur.execute(
            """INSERT INTO artist (artist_id, artist_name, country, gender)
                VALUES (%s, %s, %s, %s);""",(ArtistDict['artist_id'], ArtistDict['artist_name'], ArtistDict['country'], ArtistDict['gender'])
            )
    con.commit()


def insertGenre(GenreDict):
    cur.execute(
            """INSERT INTO genre (genre_id, parent_genre_id, genre_name)
                VALUES (%s, %s, %s);""",(GenreDict['genre_id'], GenreDict['parent_genre_id'], GenreDict['genre_name'])
            )
    con.commit()

def insertPlaylist(PlaylistDict):
    cur.execute(
            """INSERT INTO playlist (playlist_id, playlist_name, creation_date, description,
                                    play_count)
                VALUES (%s, %s, %s, %s, %s);""",(PlaylistDict['playlist_id'],PlaylistDict['playlist_name'], PlaylistDict['creation_date'], PlaylistDict['description'], PlaylistDict['play_count'])
            )
    con.commit()
    
    


    

