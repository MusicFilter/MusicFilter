#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'root', 'password', 'musicfilter', use_unicode=True, charset='utf8')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET FOREIGN_KEY_CHECKS=0")

def insertVideo(VideoDict):
    cur.execute(
        """INSERT INTO video (video_id, title, description, artist_id,
                                    is_cover, is_live, with_lyrics)
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE video_id=video_id;""",(VideoDict['video_id'], VideoDict['title'],
                VideoDict['description'],VideoDict['artist_id'], VideoDict['is_cover'], VideoDict['is_live'], VideoDict['with_lyrics'])
        )
    con.commit()
        
def insertArtist(ArtistDict):
    cur.execute(
        """INSERT INTO artist (artist_id, artist_name,dominant_decade,  country_id, is_band)
            VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE artist_id=artist_id;""",(ArtistDict['artist_id'],
            ArtistDict['artist_name'], ArtistDict['dominant_decade'],ArtistDict['country_id'], ArtistDict['is_band'])
    )
    con.commit()

def insertGenre(GenreDict):
    cur.execute(
        """INSERT INTO genre (genre_id, genre_name)
            VALUES (%s, %s) ON DUPLICATE KEY UPDATE genre_id=genre_id;""",(GenreDict['genre_id'], GenreDict['genre_name'])
    )
    con.commit()

def insertPlaylist(PlaylistDict):
    cur.execute(
            """INSERT INTO playlist (playlist_id, playlist_name,
                            creation_date, description,
                play_count, is_live, is_cover, is_with_lyrics, free_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",(PlaylistDict['playlist_id'],PlaylistDict['playlist_name'], PlaylistDict['creation_date'],PlaylistDict['description'], PlaylistDict['play_count'],PlaylistDict['is_live'],PlaylistDict['is_cover'],PlaylistDict['is_with_lyrics'],PlaylistDict['free_text'])
            )
    con.commit()

def insertArtistGenre(ArtistGenreDict):
    cur.execute(
        """INSERT INTO artist_genre (artist_id, genre_id)
            VALUES (%s, %s) ON DUPLICATE KEY UPDATE artist_id=artist_id, genre_id=genre_id;""",(ArtistGenreDict['artist_id'], ArtistGenreDict['genre_id'])
        )
    con.commit()

def insertCountry(CountryDict):
    cur.execute(
        """INSERT INTO country (country_id, country_name)
            VALUES (%s, %s) ON DUPLICATE KEY UPDATE country_id=country_id;""",(CountryDict['country_id'], CountryDict['country_name'])
    )
    con.commit()
