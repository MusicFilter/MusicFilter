#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import MySQLdb as mdb

warnings.filterwarnings("ignore", "unknown table.*")

con = mdb.connect('localhost', 'root', 'yaelushamitush2428', 'musicfilter')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET FOREIGN_KEY_CHECKS=0")

cur.execute("DROP TABLE IF EXISTS VIDEO")
cur.execute("DROP TABLE IF EXISTS SONG")
cur.execute("DROP TABLE IF EXISTS ARTIST")
cur.execute("DROP TABLE IF EXISTS GENRE")
cur.execute("DROP TABLE IF EXISTS PLAYLIST")
cur.execute("DROP TABLE IF EXISTS PLAYLIST_TO_VIDEO")

create_video_table = """CREATE TABLE VIDEO(
						youtube_id CHAR(11) PRIMARY KEY,
						title CHAR(30),
						description CHAR(100),
						song_id INT,
						length INT,
						is_cover BOOLEAN,
						is_live BOOLEAN,
						FOREIGN KEY (song_id)
							REFERENCES  SONG(song_id)
							ON DELETE CASCADE)"""

cur.execute(create_video_table)

create_song_table = """CREATE TABLE SONG(
						song_id INT PRIMARY KEY,
						song_name CHAR(30),
						artist_id INT,
						year YEAR,
						genre_id INT,
						FOREIGN KEY (artist_id)
							REFERENCES  ARTIST(artist_id)
							ON DELETE CASCADE,
						FOREIGN KEY (genre_id)
							REFERENCES  GENRE(genre_id)
							ON DELETE CASCADE)"""

cur.execute(create_song_table)

create_artist_table = """CREATE TABLE ARTIST(
						artist_id INT PRIMARY KEY,
						artist_name CHAR(30),
						country CHAR(15),
						gender CHAR(1))"""

cur.execute(create_artist_table)

create_genre_table = """CREATE TABLE GENRE(
						genre_id INT PRIMARY KEY,
						parent_genre_id INT,
						genre_name CHAR(15),
						FOREIGN KEY (parent_genre_id)
							REFERENCES GENRE(genre_id)
							ON DELETE CASCADE)"""

cur.execute(create_genre_table)

create_playlist_table = """CREATE TABLE PLAYLIST(
						playlist_id INT PRIMARY KEY AUTO_INCREMENT,
						playlist_name CHAR(30),
						creation_date TIMESTAMP,
						description CHAR(100),
						play_count INT)"""

cur.execute(create_playlist_table)

create_playlistToVideo_table = """CREATE TABLE PLAYLIST_TO_VIDEO(
						playlist_id INT,
						video_id CHAR(11),
						PRIMARY KEY (playlist_id, video_id),
						FOREIGN KEY (video_id)
							REFERENCES  VIDEO(youtube_id)
							ON DELETE CASCADE,
						FOREIGN KEY (playlist_id)
							REFERENCES  PLAYLIST(playlist_id)
							ON DELETE CASCADE)"""

cur.execute(create_playlistToVideo_table)

con.close()







# with con:

# 	cur = con.cursor(mdb.cursors.DictCursor)
# 	cur.execute("SELECT *")

# 	rows = cur.fetchall()

# 	for row in rows:
# 		print row["Id"], row["Name"]
