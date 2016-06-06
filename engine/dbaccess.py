from django.db import connection
import time

"""
Helper function to replace fetchall output with [dict]
"""
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


"""
Helper function to replace fetchone output with [dict]
"""
def dictfetchone(cursor):
    "Return requested row from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))


"""
@fetchall
SELECT artist_id id, artist_name name"
FROM artist
"""
def getArtists(search):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT artist_id id, artist_name name FROM artist WHERE artist_name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT country_id id, country_name name
FROM country
"""
def getCountries(search):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT country_id id, country_name name FROM country WHERE country_name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT genre_id id, genre_name name
FROM genre
"""
def getGenres(search):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT genre_id id, genre_name name FROM genre WHERE genre_name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT playlist_id, playlist_name, creation_date, description, play_count
FROM playlist
ORDER BY play_count
DESC LIMIT <count>
"""
def getTrending(count):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT playlist_id, playlist_name, creation_date, description, play_count FROM playlist ORDER BY play_count DESC LIMIT %s", [count])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT playlist_id, playlist_name, creation_date, description, play_count
FROM playlist
ORDER BY creation_date
DESC LIMIT <count>
"""
def getNewest(count):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT playlist_id, playlist_name, creation_date, description, play_count FROM playlist ORDER BY creation_date DESC LIMIT %s", [count])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT video_id
FROM playlist_to_video
WHERE playlist_id = <playlist_id>
"""
def getPlaylistVideos(playlist_id):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT video_id FROM  playlist_to_video WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchone
SELECT playlist_id, creation_date, description, play_count
FROM playlist
WHERE playlist_name = <playlist_name>
"""
def getPlaylistsByName(playlist_name):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT playlist_id, creation_date, description, play_count FROM playlist WHERE playlist_name LIKE %s", [playlist_name])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchone
SELECT playlist_name, creation_date, description, play_count
FROM playlist
WHERE playlist_id = <playlist_id>
"""
def getPlaylistById(playlist_id):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT playlist_name, creation_date, description, play_count FROM playlist WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return dictfetchone(cursor)


"""
@commit
UPDATE playlist SET play_count = play_count + 1
WHERE playlist_id = <playlist_id>
"""
def incrementHitCount(playlist_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE playlist SET play_count = play_count + 1 WHERE playlist_id = %s", [playlist_id])


"""
@fetchall
Loads videos using the given filter parameters
:returns: [playlist]
:param: id [int] playlist id
:param: genres [list] of [int] genres ID
:param: countries [list] of [int] country ID
:param: artists [list] of [int] artists ID
:param: decades [list] of [int] decades ID
:param: freetext [string] free text
"""
def loadVideos(id, genres, countries, artists, decades, freetext, live, cover, withlyrics):

    select_data = []

    # Here comes a big composite query that first generates new videos according to filter
    # Then it deletes current videos from playlist
    # Then it connects new video ids to the playlist
    with connection.cursor() as cursor:

        filtered_videos_select = "SELECT @a:=@a+1 AS num, video.video_id AS id"
        filtered_videos_count_select = "SET @videonum = (SELECT COUNT(*)"

        filtered_videos_selectless = """
            FROM video, artist, country, artist_genre, genre
            WHERE video.artist_id = artist.artist_id
            \tAND artist_genre.artist_id = artist.artist_id
            \tAND artist_genre.genre_id = genre.genre_id\n"""

        # conditional appends for genre, countries, artists, decades, freetext
        if len(genres) > 0:
            filtered_videos_selectless += "\t\tAND genre.genre_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(genres)))
            select_data.extend(genres)

        if len(countries) > 0:
            filtered_videos_selectless += "\t\tAND artist.country_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(countries)))
            select_data.extend(countries)

        if len(artists) > 0:
            filtered_videos_selectless += "\t\tAND artist.artist_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(artists)))
            select_data.extend(artists)

        if len(decades) > 0:
            filtered_videos_selectless += "\t\tAND artist.dominant_decade IN (%s)\n" % ', '.join('%s' for i in xrange(len(decades)))
            select_data.extend(decades)

        if len(freetext) > 0:
            filtered_videos_selectless += "\t\tAND (video.title LIKE %s OR video.description LIKE %s)\n"
            select_data.extend([freetext, freetext])

        filtered_videos_selectless += """\t\tAND video.is_live = %s
            \tAND video.is_cover = %s
            \tAND video.with_lyrics = %s
        """

        # assemble inner query
        count_query = filtered_videos_count_select + filtered_videos_selectless + ');'

        header = "SELECT DISTINCT filtered_videos.id id FROM"
        footer = """
            WHERE filtered_videos.num IN   (SELECT *
                                            FROM    (SELECT FLOOR(((@videonum) + 1) * RAND()) num
                                                     FROM video
                                                     LIMIT 110)
                                            random)
            LIMIT 100;
        """

        # assemble main query
        main_query = '{0} ({1} {2}) as filtered_videos {3}'.format(header, filtered_videos_select, filtered_videos_selectless, footer)
        query = '{0} {1}'.format(count_query, main_query)

        select_data.extend([live, cover, withlyrics])

        # execute query
        cursor.execute(count_query, select_data)
        cursor.execute(main_query, select_data)

        # fetch results
        return dictfetchall(cursor)


"""
@commit
Update video list by playlist_id
"""
def updateVideoList(playlist_id, video_ids):
    with connection.cursor() as cursor:
        insert_data = [playlist_id]

        update_command = """DELETE FROM playlist_to_video
               WHERE playlist_id = %s;
               """

        # concatenate all rows to one query
        for video_id in video_ids:
            update_command += """INSERT INTO playlist_to_video
                    (playlist_id, video_id)
                    VALUES (%s, %s);
                    """

            insert_data.extend((playlist_id, video_id))

        # execute query
        cursor.execute(update_command, insert_data)

def createPlaylist(name, desc, live, cover, withlyrics, freetext, artists, countries, genres, decades):
    with connection.cursor() as cursor:

        # Create one big insert command to minimize I/O
        insert_command = """INSERT INTO playlist
                (playlist_name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """

        insert_data = [name, time.strftime('%Y-%m-%d %H:%M:%S'), desc, 0, live, cover, withlyrics, freetext]
        cursor.execute(insert_command, insert_data)
        playlist_id = cursor.lastrowid

        for artist in artists:
            insert_command = """INSERT INTO playlist_artist
                    (playlist_id, artist_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [artist[0]])

        for country in countries:
            insert_command = """INSERT INTO playlist_country
                    (playlist_id, country_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [country[0]])

        for genre in genres:
            insert_command = """INSERT INTO playlist_genre
                    (playlist_id, genre_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [genre[0]])

        for decade in decades:
            insert_command = """INSERT INTO playlist_decade
                    (playlist_id, decade_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [decade[0]])

        return playlist_id






