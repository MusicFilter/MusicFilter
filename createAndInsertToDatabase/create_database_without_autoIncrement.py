#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import MySQLdb as mdb
from password import *

warnings.filterwarnings("ignore", "unknown table.*")

con = mdb.connect('localhost', 'root', getPassword(), 'musicfilter', use_unicode=True, charset='utf8')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")

cur.execute("SET FOREIGN_KEY_CHECKS=0")

cur.execute("DROP TABLE IF EXISTS VIDEO")
cur.execute("DROP TABLE IF EXISTS SONG")
cur.execute("DROP TABLE IF EXISTS ARTIST")
cur.execute("DROP TABLE IF EXISTS GENRE")
cur.execute("DROP TABLE IF EXISTS ARTIST_GENRE")
cur.execute("DROP TABLE IF EXISTS COUNTRY")

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

create_country_table = """CREATE TABLE COUNTRY(
						country_id INT PRIMARY KEY,
						country_name CHAR(60))"""

cur.execute(create_country_table)

con.close()
>>>>>>> refs/remotes/origin/master
