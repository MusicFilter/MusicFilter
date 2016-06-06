#!/usr/bin/python
# -*- coding: utf-8 -*-

# import warnings
import MySQLdb as mdb
from password import *
from textwrap import dedent

# warnings.filterwarnings("ignore", "unknown table.*")

con = mdb.connect('localhost', 'root', getPassword(), 'musicfilter', use_unicode=True, charset='utf8')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")

# cur.execute("SET FOREIGN_KEY_CHECKS=0")

cur.execute("DROP TABLE IF EXISTS video")
cur.execute("DROP TABLE IF EXISTS song")
cur.execute("DROP TABLE IF EXISTS artist")
cur.execute("DROP TABLE IF EXISTS genre")
cur.execute("DROP TABLE IF EXISTS artist_genre")
cur.execute("DROP TABLE IF EXISTS country")

cur.execute("ALTER DATABASE musicfilter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

create_genre_table = """
                     CREATE TABLE genre(
                         id INT UNSIGNED NOT NULL,
                         name VARCHAR(60),
                         PRIMARY KEY (id)
                     )
                     """

print dedent(create_genre_table)

cur.execute(create_genre_table)

create_country_table = """
                       CREATE TABLE country (
                           id INT UNSIGNED NOT NULL,
                           name VARCHAR(60),
                           PRIMARY KEY (id)
                       )
                       """

print dedent(create_country_table)

cur.execute(create_country_table)

create_artist_table = """
                      CREATE TABLE artist (
                          id INT UNSIGNED NOT NULL,
                          name VARCHAR(255),
                          dominant_decade YEAR,
                          country_id INT UNSIGNED,
                          is_band BOOLEAN NOT NULL,
                          PRIMARY KEY (id),
                          FOREIGN KEY (country_id)
                              REFERENCES country(id)
                              ON DELETE SET NULL
                              ON UPDATE CASCADE
                      )
                      """

print dedent(create_artist_table)

cur.execute(create_artist_table)

create_artist_genre_table = """
                            CREATE TABLE artist_genre (
                                artist_id INT UNSIGNED NOT NULL,
                                genre_id INT UNSIGNED NOT NULL,
                                PRIMARY KEY (artist_id, genre_id),
                                FOREIGN KEY (artist_id)
                                    REFERENCES artist(id)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
                                FOREIGN KEY (genre_id)
                                    REFERENCES genre(id)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE
                            )
                            """

print dedent(create_artist_genre_table)

cur.execute(create_artist_genre_table)

create_video_table = """
                     CREATE TABLE video (
                         id CHAR(11) NOT NULL,
                         title VARCHAR(255) NOT NULL,
                         description VARCHAR(255) NOT NULL,
                         artist_id INT UNSIGNED,
                         is_cover BOOLEAN NOT NULL,
                         is_live BOOLEAN NOT NULL,
                         with_lyrics BOOLEAN NOT NULL,
                         PRIMARY KEY (id),
                         FOREIGN KEY (artist_id)
                             REFERENCES artist(id)
                             ON DELETE SET NULL
                             ON UPDATE CASCADE
                     )
                     """

print dedent(create_video_table)

cur.execute(create_video_table)

con.close()
