import os
import sys
from textwrap import dedent

import django
from django.db import connection

# Use musicfilter's Django settings, just for the database connection settings (host, user, password, port, db_name, charset).
# Note: This won't work if the script is invoked using execfile.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicfilter.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

def main():
    with connection.cursor() as cur:
        cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")

        cur.execute("ALTER DATABASE musicfilter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

        cur.execute("DROP TABLE IF EXISTS playlist_video")
        cur.execute("DROP TABLE IF EXISTS playlist_artist")
        cur.execute("DROP TABLE IF EXISTS playlist_genre")
        cur.execute("DROP TABLE IF EXISTS playlist_country")
        cur.execute("DROP TABLE IF EXISTS playlist_decade")
        cur.execute("DROP TABLE IF EXISTS playlist")
        cur.execute("DROP TABLE IF EXISTS artist_genre")
        cur.execute("DROP TABLE IF EXISTS video")
        cur.execute("DROP TABLE IF EXISTS artist")
        cur.execute("DROP TABLE IF EXISTS genre")
        cur.execute("DROP TABLE IF EXISTS country")

        create_country_table = """
                               CREATE TABLE country (
                                   id INT UNSIGNED NOT NULL,
                                   name VARCHAR(60),
                                   PRIMARY KEY (id)
                               )
                               """

        print dedent(create_country_table)

        cur.execute(create_country_table)

        create_genre_table = """
                             CREATE TABLE genre(
                                 id INT UNSIGNED NOT NULL,
                                 name VARCHAR(60),
                                 PRIMARY KEY (id)
                             )
                             """

        print dedent(create_genre_table)

        cur.execute(create_genre_table)

        create_artist_table = """
                              CREATE TABLE artist (
                                  id INT UNSIGNED NOT NULL,
                                  name VARCHAR(255),
                                  dominant_decade YEAR,
                                  country_id INT UNSIGNED,
                                  PRIMARY KEY (id),
                                  FOREIGN KEY (country_id)
                                      REFERENCES country(id)
                                      ON DELETE SET NULL
                                      ON UPDATE CASCADE
                              )
                              """

        print dedent(create_artist_table)

        cur.execute(create_artist_table)

        create_video_table = """
                             CREATE TABLE video (
                                 id CHAR(11) NOT NULL,
                                 title VARCHAR(255) NOT NULL,
                                 description VARCHAR(255) NOT NULL,
                                 artist_id INT UNSIGNED,
                                 is_cover BOOLEAN NOT NULL,
                                 is_live BOOLEAN NOT NULL,
                                 is_with_lyrics BOOLEAN NOT NULL,
                                 PRIMARY KEY (id),
                                 FOREIGN KEY (artist_id)
                                     REFERENCES artist(id)
                                     ON DELETE SET NULL
                                     ON UPDATE CASCADE
                             )
                             """

        print dedent(create_video_table)

        cur.execute(create_video_table)

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

if __name__ == '__main__':
    main()
