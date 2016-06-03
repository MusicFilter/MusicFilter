#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import MySQLdb as mdb

warnings.filterwarnings("ignore", "unknown table.*")

con = mdb.connect('localhost', 'root', 'password', 'musicfilter', use_unicode=True, charset='utf8')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")

cur.execute("SET FOREIGN_KEY_CHECKS=0")

cur.execute("DROP TABLE IF EXISTS VIDEO")
cur.execute("DROP TABLE IF EXISTS SONG")
cur.execute("DROP TABLE IF EXISTS ARTIST")
cur.execute("DROP TABLE IF EXISTS GENRE")
cur.execute("DROP TABLE IF EXISTS ARTIST_GENRE")
cur.execute("DROP TABLE IF EXISTS PLAYLIST")
cur.execute("DROP TABLE IF EXISTS PLAYLIST_TO_VIDEO")
cur.execute("DROP TABLE IF EXISTS COUNTRY")
cur.execute("DROP TABLE IF EXISTS PLAYLIST_ARTIST")
cur.execute("DROP TABLE IF EXISTS PLAYLIST_GENRE")
cur.execute("DROP TABLE IF EXISTS PLAYLIST_COUNTRY")

cur.execute("ALTER DATABASE musicfilter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

create_video_table = """CREATE TABLE VIDEO(
						video_id CHAR(11) PRIMARY KEY,
						title CHAR(255),
						description TEXT,
						artist_id INT,
						is_cover BOOLEAN,
						is_live BOOLEAN,
						with_lyrics BOOLEAN,
						FOREIGN KEY (artist_id)
							REFERENCES  ARTIST(artist_id)
							ON DELETE CASCADE)"""

cur.execute(create_video_table)

create_artist_table = """CREATE TABLE ARTIST(
						artist_id INT PRIMARY KEY,
						artist_name CHAR(255),
						dominant_decade INT,
						country_id INT,
						is_band BOOLEAN,
						FOREIGN KEY (country_id)
							REFERENCES  COUNTRY(country_id)
							ON DELETE CASCADE)"""

cur.execute(create_artist_table)

create_genre_table = """CREATE TABLE GENRE(
						genre_id INT PRIMARY KEY,
						genre_name CHAR(60))"""

cur.execute(create_genre_table)

create_artistGenre_table = """CREATE TABLE ARTIST_GENRE(
						artist_id INT,
						genre_id INT,
						PRIMARY KEY (artist_id, genre_id))"""

cur.execute(create_artistGenre_table)

create_playlist_table = """CREATE TABLE PLAYLIST(
						playlist_id INT PRIMARY KEY AUTO_INCREMENT,
						playlist_name CHAR(30),
						creation_date TIMESTAMP,
						description CHAR(100),
						play_count INT,
						is_live BOOLEAN,
						is_cover BOOLEAN,
						is_with_lyrics BOOLEAN,
						free_text CHAR(100))"""

cur.execute(create_playlist_table)

create_playlistToVideo_table = """CREATE TABLE PLAYLIST_TO_VIDEO(
						playlist_id INT,
						video_id CHAR(11),
						PRIMARY KEY (playlist_id, video_id),
						FOREIGN KEY (video_id)
							REFERENCES  VIDEO(video_id)
							ON DELETE CASCADE,
						FOREIGN KEY (playlist_id)
							REFERENCES  PLAYLIST(playlist_id)
							ON DELETE CASCADE)"""

cur.execute(create_playlistToVideo_table)

create_country_table = """CREATE TABLE COUNTRY(
						country_id INT PRIMARY KEY,
						country_name CHAR(60))"""

cur.execute(create_country_table)

create_playlistArtist_table = """CREATE TABLE PLAYLIST_ARTIST(
						playlist_id INT,
						artist_id INT,
						FOREIGN KEY (artist_id)
							REFERENCES  ARTIST(artist_id)
							ON DELETE CASCADE)"""

cur.execute(create_playlistArtist_table)

create_playlistGenre_table = """CREATE TABLE PLAYLIST_GENRE(
						playlist_id INT,
						genre_id INT,
						FOREIGN KEY (genre_id)
							REFERENCES  GENRE(genre_id)
							ON DELETE CASCADE)"""

cur.execute(create_playlistGenre_table)

create_playlistCountry_table = """CREATE TABLE PLAYLIST_COUNTRY(
						playlist_id INT,
						country_id INT,
						FOREIGN KEY (country_id)
							REFERENCES  COUNTRY(country_id)
							ON DELETE CASCADE)"""

cur.execute(create_playlistCountry_table)

con.close()







# with con:

# 	cur = con.cursor(mdb.cursors.DictCursor)
# 	cur.execute("SELECT *")

# 	rows = cur.fetchall()

# 	for row in rows:
# 		print row["Id"], row["Name"]
