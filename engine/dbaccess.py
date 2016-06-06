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
SELECT artist_id id, artist_name name
FROM  artist
WHERE artist_name LIKE %<search>%
LIMIT 50
"""
def getArtists(search):
    with connection.cursor() as cursor:
        cursor.execute("SELECT artist_id id, artist_name name FROM artist WHERE artist_name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT country_id id, country_name name
FROM country
WHERE country_name LIKE %<search>%
LIMIT 50
"""
def getCountries(search):
    with connection.cursor() as cursor:
        cursor.execute("SELECT country_id id, country_name name FROM country WHERE country_name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT genre_id id, genre_name name
FROM  genre
WHERE genre_name LIKE %<search>%
LIMIT 50
"""
def getGenres(search):
    with connection.cursor() as cursor:
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
@update
UPDATE playlist SET play_count = play_count + 1
WHERE playlist_id = <playlist_id>
"""
def incrementHitCount(playlist_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE playlist SET play_count = play_count + 1 WHERE playlist_id = %s", [playlist_id])


"""
Loads videos using the given playlist
@fetchall
MONSTERQUERY
"""
def loadVideos(p):

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
        if len(p.genres) > 0:
            filtered_videos_selectless += "\t\tAND genre.genre_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(p.genres)))
            select_data.extend(p.genres)

        if len(p.countries) > 0:
            filtered_videos_selectless += "\t\tAND artist.country_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(p.countries)))
            select_data.extend(p.countries)

        if len(p.artists) > 0:
            filtered_videos_selectless += "\t\tAND artist.artist_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(p.artists)))
            select_data.extend(p.artists)

        if len(p.decades) > 0:
            filtered_videos_selectless += "\t\tAND artist.dominant_decade IN (%s)\n" % ', '.join('%s' for i in xrange(len(p.decades)))
            select_data.extend(p.decades)

        if len(p.text) > 0:
            filtered_videos_selectless += "\t\tAND (video.title LIKE %s OR video.description LIKE %s)\n"
            select_data.extend([p.text, p.text])

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

        select_data.extend([p.live, p.cover, p.withlyrics])

        # execute query
        cursor.execute(count_query, select_data)
        cursor.execute(main_query, select_data)

        # fetch results
        return dictfetchall(cursor)


"""
@update
Update video list by playlist_id

Part1 deletes current videos associated to playlist_id
Part2 inserts given video_ids to DB
"""
def updateVideoList(playlist_id, video_ids):
    with connection.cursor() as cursor:
        insert_data = [playlist_id]

        # part1
        update_command = """DELETE FROM playlist_to_video
               WHERE playlist_id = %s;
               """

        # part2 - concatenate all rows to one query
        for video_id in video_ids:
            update_command += """INSERT INTO playlist_to_video
                    (playlist_id, video_id)
                    VALUES (%s, %s);
                    """

            insert_data.extend((playlist_id, video_id))

        # execute query
        cursor.execute(update_command, insert_data)


"""
1. Insert to playlist table
@update
INSERT INTO playlist
(playlist_name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
VALUES (<p.name>, now, <p.desc>, 0, <p.live>, <p.cover>, <p.withlyrics>, <p.text>)

2. Retrieve playlist ID

3. Insert playlist's filters
3.1 artists filter
@update
INSERT INTO playlist_artist
(playlist_id, artist_id)
VALUES (LAST_INSERT_ID(), <artist_id>)

3.2 countries filter
@update
INSERT INTO playlist_country
(playlist_id, country_id)
VALUES (LAST_INSERT_ID(), <country_id>)

3.3 genres filter
@update
INSERT INTO playlist_genre
(playlist_id, genre_id)
VALUES (LAST_INSERT_ID(), <genre_id>);

3.4 decades filter
@update
INSERT INTO playlist_decade
(playlist_id, decade)
VALUES (LAST_INSERT_ID(), <decade_id>);
"""
def createPlaylist(p):
    with connection.cursor() as cursor:

        # Q1
        insert_command = """INSERT INTO playlist
                (playlist_name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        insert_data = [p.name, time.strftime('%Y-%m-%d %H:%M:%S'), p.desc, 0, p.live, p.cover, p.withlyrics, p.freetext]
        cursor.execute(insert_command, insert_data)

        # retrieve playlist ID
        playlist_id = cursor.lastrowid

        # Q3.1
        for artist in p.artists:
            insert_command = """INSERT INTO playlist_artist
                    (playlist_id, artist_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [artist[0]])

        # Q3.2
        for country in p.countries:
            insert_command = """INSERT INTO playlist_country
                    (playlist_id, country_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [country[0]])

        # Q3.3
        for genre in p.genres:
            insert_command = """INSERT INTO playlist_genre
                    (playlist_id, genre_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [genre[0]])

        # Q3.4
        for decade in p.decades:
            insert_command = """INSERT INTO playlist_decade
                    (playlist_id, decade)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [decade[0]])

        return playlist_id






