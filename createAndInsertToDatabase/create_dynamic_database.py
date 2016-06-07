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

cur.execute("DROP TABLE IF EXISTS playlist_video")
cur.execute("DROP TABLE IF EXISTS playlist_artist")
cur.execute("DROP TABLE IF EXISTS playlist_genre")
cur.execute("DROP TABLE IF EXISTS playlist_country")
cur.execute("DROP TABLE IF EXISTS playlist_decade")
cur.execute("DROP TABLE IF EXISTS playlist")

cur.execute("ALTER DATABASE musicfilter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

create_playlist_table = """
                        CREATE TABLE playlist (
                            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                            name VARCHAR(60) NOT NULL,
                            creation_date TIMESTAMP NOT NULL,
                            description VARCHAR(1000) NOT NULL,
                            play_count INT UNSIGNED NOT NULL,
                            is_live BOOLEAN NOT NULL,
                            is_cover BOOLEAN NOT NULL,
                            is_with_lyrics BOOLEAN NOT NULL,
                            free_text VARCHAR(255),
                            PRIMARY KEY (id)
                        )
                        """

print dedent(create_playlist_table)

cur.execute(create_playlist_table)

create_playlist_video_table = """
                              CREATE TABLE playlist_video (
                                  playlist_id INT UNSIGNED NOT NULL,
                                  video_id CHAR(11) NOT NULL,
                                  PRIMARY KEY (playlist_id, video_id),
                                  FOREIGN KEY (playlist_id)
                                      REFERENCES playlist(id)
                                      ON DELETE CASCADE
                                      ON UPDATE CASCADE,
                                  FOREIGN KEY (video_id)
                                      REFERENCES video(id)
                                      ON DELETE CASCADE
                                      ON UPDATE CASCADE
                              )
                              """

print dedent(create_playlist_video_table)

cur.execute(create_playlist_video_table)

create_playlist_artist_table = """
                               CREATE TABLE playlist_artist (
                                   playlist_id INT UNSIGNED NOT NULL,
                                   artist_id INT UNSIGNED NOT NULL,
                                   PRIMARY KEY (playlist_id, artist_id),
                                   FOREIGN KEY (playlist_id)
                                       REFERENCES playlist(id)
                                       ON DELETE CASCADE
                                       ON UPDATE CASCADE,
                                   FOREIGN KEY (artist_id)
                                       REFERENCES artist(id)
                                       ON DELETE CASCADE
                                       ON UPDATE CASCADE
                               )
                               """

print dedent(create_playlist_artist_table)

cur.execute(create_playlist_artist_table)

create_playlist_genre_table = """
                              CREATE TABLE playlist_genre (
                                  playlist_id INT UNSIGNED NOT NULL,
                                  genre_id INT UNSIGNED NOT NULL,
                                  PRIMARY KEY (playlist_id, genre_id),
                                  FOREIGN KEY (playlist_id)
                                      REFERENCES playlist(id)
                                      ON DELETE CASCADE
                                      ON UPDATE CASCADE,
                                  FOREIGN KEY (genre_id)
                                      REFERENCES genre(id)
                                      ON DELETE CASCADE
                                      ON UPDATE CASCADE
                              )
                              """

print dedent(create_playlist_genre_table)

cur.execute(create_playlist_genre_table)

create_playlist_country_table = """
                                CREATE TABLE playlist_country (
                                    playlist_id INT UNSIGNED NOT NULL,
                                    country_id INT UNSIGNED NOT NULL,
                                    PRIMARY KEY (playlist_id, country_id),
                                    FOREIGN KEY (playlist_id)
                                        REFERENCES playlist(id)
                                        ON DELETE CASCADE
                                        ON UPDATE CASCADE,
                                    FOREIGN KEY (country_id)
                                        REFERENCES country(id)
                                        ON DELETE CASCADE
                                        ON UPDATE CASCADE
                                )
                                """

print dedent(create_playlist_country_table)

cur.execute(create_playlist_country_table)

create_playlist_decade_table = """
                               CREATE TABLE playlist_decade (
                                   playlist_id INT UNSIGNED NOT NULL,
                                   decade_id INT UNSIGNED NOT NULL,
                                   PRIMARY KEY (playlist_id, decade_id),
                                   FOREIGN KEY (playlist_id)
                                       REFERENCES playlist(id)
                                       ON DELETE CASCADE
                                       ON UPDATE CASCADE
                               )
                               """

print dedent(create_playlist_decade_table)

cur.execute(create_playlist_decade_table)

con.close()
