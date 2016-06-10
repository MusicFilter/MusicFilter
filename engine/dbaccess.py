from django.db import connection
import objects

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
SELECT id, name
FROM  artist
WHERE name LIKE %<search>%
LIMIT 50
"""
def getArtists(search):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM artist WHERE name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT id, name
FROM country
WHERE name LIKE %<search>%
LIMIT 50
"""
def getCountries(search):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM country WHERE name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT id, name
FROM  genre
WHERE name LIKE %<search>%
LIMIT 50
"""
def getGenres(search):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM genre WHERE name LIKE %s LIMIT 50", [search])

        # fetch results
        return dictfetchall(cursor)



"""
@fetchall
SELECT id, name, creation_date, play_count
FROM playlist
ORDER BY play_count
DESC LIMIT <count>
"""
def getTrending(count):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT id, name, creation_date, play_count FROM playlist ORDER BY play_count DESC LIMIT %s", [count])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT id, name, creation_date, play_count
FROM playlist
ORDER BY creation_date
DESC LIMIT <count>
"""
def getNewest(count):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT id, name, creation_date, play_count FROM playlist ORDER BY creation_date DESC LIMIT %s", [count])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT video_id
FROM playlist_video
WHERE playlist_id = <playlist_id>
"""
def getPlaylistVideos(playlist_id):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT video_id FROM playlist_video WHERE playlist_id = %s LIMIT 100", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchall
SELECT id, name
FROM playlist
WHERE name = <playlist_name>
"""
def getPlaylistsByName(playlist_name):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT id, name FROM playlist WHERE name LIKE %s", [playlist_name])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchone
SELECT *
FROM playlist
WHERE id = <playlist_id>
"""
def getPlaylistById(playlist_id):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT * FROM playlist WHERE id = %s LIMIT 1", [playlist_id])

        # fetch results
        return dictfetchone(cursor)


"""
@update
UPDATE playlist SET play_count = play_count + 1
WHERE id = <playlist_id>
"""
def incrementHitCount(playlist_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE playlist SET play_count = play_count + 1 WHERE id = %s", [playlist_id])


"""
Loads videos using the given playlist
@fetchall
RANDOMIZEQUERY
"""
def loadVideos(playlist, mode=objects.LOAD_FROM_TABLE):

    if mode == objects.LOAD_FROM_TABLE:
        # reload playlist from DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT video_id FROM playlist_video WHERE playlist_id = %s LIMIT 100", [playlist.id])
            return cursor.fetchall()

    select_data = []

    # Prepare user input
    genreslist = [int(x[0]) for x in playlist.genres]
    countrieslist = [int(x[0]) for x in playlist.countries]
    artistslist = [int(x[0]) for x in playlist.artists]
    decadeslist = [int(x) for x in playlist.decades]
    string_freetext = '%' + playlist.text + '%'

    # Here comes a big composite query that first generates new videos according to filter
    # Then it deletes current videos from playlist
    # Then it connects new video ids to the playlist
    with connection.cursor() as cursor:

        cursor.execute("SET @a = 0;")

        frompart = ['video']
        wherepart = []

        # filtered_videos_selectless = """
            # FROM video, artist, country, artist_genre, genre
            # WHERE video.artist_id = artist.id
            # \tAND artist_genre.artist_id = artist.id
            # \tAND artist_genre.genre_id = genre.id\n"""

        # conditional appends for genre, countries, artists, decades, freetext
        if len(genreslist) > 0:
            frompart.extend(['artist_genre', 'artist', 'genre'])
            where = "genre.id IN (%s)\n" % ', '.join('%s' for i in xrange(len(genreslist)))
            where_join1 = "artist.id = artist_genre.artist_id\n"
            where_join2 = "genre.id = artist_genre.genre_id\n"
            wherepart.append(where)
            wherepart.append(where_join1)
            wherepart.append(where_join2)
            #filtered_videos_selectless += "\t\tAND genre.id IN (%s)\n" % ', '.join('%s' for i in xrange(len(genreslist)))
            select_data.extend(genreslist)

        if len(countrieslist) > 0:
            frompart.append('artist')
            where = "artist.country_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(countrieslist)))
            wherepart.append(where)
            #filtered_videos_selectless += "\t\tAND artist.country_id IN (%s)\n" % ', '.join('%s' for i in xrange(len(countrieslist)))
            select_data.extend(countrieslist)

        if len(artistslist) > 0:
            frompart.append('artist')
            where = "artist.id IN (%s)\n" % ', '.join('%s' for i in xrange(len(artistslist)))
            wherepart.append(where)
            #filtered_videos_selectless += "\t\tAND artist.id IN (%s)\n" % ', '.join('%s' for i in xrange(len(artistslist)))
            select_data.extend(artistslist)

        if len(decadeslist) > 0:
            frompart.append('artist')
            where = "artist.dominant_decade IN (%s)\n" % ', '.join('%s' for i in xrange(len(decadeslist)))
            wherepart.append(where)
            #filtered_videos_selectless += "\t\tAND artist.dominant_decade IN (%s)\n" % ', '.join('%s' for i in xrange(len(decadeslist)))
            select_data.extend(decadeslist)
            
        # If we reached here and wherepart is not empty, it means there was a filter from artist table
        if len(wherepart) > 0:
            where = "video.artist_id = artist.id\n"
            wherepart.append(where)

        if len(playlist.text) > 0:
            wherepart.append("(video.title LIKE %s OR video.description LIKE %s)")
            #filtered_videos_selectless += "\t\tAND (video.title LIKE %s OR video.description LIKE %s)\n"
            select_data.extend([string_freetext, string_freetext])

        wherepart.extend([
            'video.is_live = %s',
            'video.is_cover = %s',
            'video.is_with_lyrics = %s'
        ])
        select_data.extend([playlist.live, playlist.cover, playlist.withlyrics])

        fromstring = ', '.join(list(set(frompart)))
        wherestring = '\n\tAND '.join(wherepart)

        # assemble inner query
        count_query = 'SET @videonum = (SELECT COUNT(*) FROM {0} WHERE {1});'.format(fromstring, wherestring)

        # construct main query
        header = "SELECT DISTINCT filtered_videos.id id FROM"
        filtered_videos_select = "SELECT @a:=@a+1 AS num, video.id AS id"
        footer = """
            WHERE filtered_videos.num IN   (SELECT *
                                            FROM    (SELECT FLOOR((@videonum * RAND()) + 1) AS num
                                                     FROM video
                                                     LIMIT 1000)
                                            AS random)
            LIMIT 100;
        """

        # assemble main query
        main_query = '{0} ({1} FROM {2} WHERE {3}) as filtered_videos {4}'.format(
            header, filtered_videos_select, fromstring, wherestring, footer
        )

        # execute queries
        cursor.execute(count_query, select_data)
        cursor.execute(main_query, select_data)

        # fetch results
        return cursor.fetchall()


"""
@update
Update video list by playlist_id

Part1 deletes current videos associated to playlist_id
Part2 inserts given video_ids to DB
"""
def updateVideoList(playlist_id, video_ids):
    with connection.cursor() as cursor:
        # part1
        delete_command = """DELETE FROM playlist_video
               WHERE playlist_id = %s;
               """

        # execute query
        cursor.execute(delete_command, [playlist_id])

        # part2 - concatenate all rows to one query
        if video_ids:
            insert_command = "INSERT INTO playlist_video (playlist_id, video_id) VALUES "
            values = []
            insert_data = []
            for video_id in video_ids:
                values.append("(%s, %s)")
                insert_data.extend((playlist_id, video_id))
            insert_command += ", ".join(values)

            # execute query
            cursor.execute(insert_command, insert_data)


"""
1. Insert to playlist table
@update
INSERT INTO playlist
(name, is_live, is_cover, is_with_lyrics, free_text)
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
(playlist_id, decade_id)
VALUES (LAST_INSERT_ID(), <decade_id>);
"""
def createPlaylist(p):
    with connection.cursor() as cursor:

        # Q1
        insert_command = """INSERT INTO playlist
                (name, is_live, is_cover, is_with_lyrics, free_text)
                VALUES (%s, %s, %s, %s, %s);
        """

        insert_data = [p.name, p.live, p.cover, p.withlyrics, p.text]
        cursor.execute(insert_command, insert_data)

        # retrieve playlist ID
        playlist_id = cursor.lastrowid

        # Q3.1
        if p.artists:
            insert_command = "INSERT INTO playlist_artist (playlist_id, artist_id) VALUES "
            values = []
            insert_data = []
            for artist in p.artists:
                values.append("(LAST_INSERT_ID(), %s)")
                insert_data.append(artist[0])
            insert_command += ", ".join(values)
            cursor.execute(insert_command, insert_data)

        # Q3.2
        if p.countries:
            insert_command = "INSERT INTO playlist_country (playlist_id, country_id) VALUES "
            values = []
            insert_data = []
            for country in p.countries:
                values.append("(LAST_INSERT_ID(), %s)")
                insert_data.append(country[0])
            insert_command += ", ".join(values)
            cursor.execute(insert_command, insert_data)

        # Q3.3
        if p.genres:
            insert_command = "INSERT INTO playlist_genre (playlist_id, genre_id) VALUES "
            values = []
            insert_data = []
            for genre in p.genres:
                values.append("(LAST_INSERT_ID(), %s)")
                insert_data.append(genre[0])
            insert_command += ", ".join(values)
            cursor.execute(insert_command, insert_data)

        # Q3.4
        if p.decades:
            insert_command = "INSERT INTO playlist_decade (playlist_id, decade_id) VALUES "
            values = []
            insert_data = []
            for decade in p.decades:
                values.append("(LAST_INSERT_ID(), %s)")
                insert_data.append(decade)
            insert_command += ", ".join(values)
            cursor.execute(insert_command, insert_data)

        return playlist_id


"""
@fetchall
SELECT decade_id
FROM playlist_decade
WHERE playlist_id = <playlist_id>
"""
def getFilterDecades(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT decade_id FROM playlist_decade WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchall
SELECT id, name
FROM playlist_artist, artist
WHERE playlist_id = <playlist_id> AND artist_id = id
"""
def getFilterArtists(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT id, name FROM playlist_artist, artist WHERE playlist_id = %s AND artist_id = id", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchall
SELECT id, name
FROM playlist_country, country
WHERE playlist_id = <playlist_id> AND country_id = id
"""
def getFilterCountries(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT id, name FROM playlist_country, country WHERE playlist_id = %s AND country_id = id", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchall
SELECT id, name
FROM playlist_genre, genre
WHERE playlist_id = <playlist_id> AND genre_id = id
"""
def getFilterGenres(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT id, name FROM playlist_genre, genre WHERE playlist_id = %s AND genre_id = id", [playlist_id])

        # fetch results
        return cursor.fetchall()

"""
@fetchone
SELECT name
FROM artist
WHERE id = (
    SELECT artist_id
    FROM playlist_artist
    GROUP BY artist_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
"""
def getTopArtist():
    with connection.cursor() as cursor:
        # execute query
        cursor.execute("SELECT name FROM artist WHERE id = (SELECT artist_id FROM playlist_artist GROUP BY artist_id ORDER BY COUNT(*) DESC LIMIT 1)")

        # fetch results
        return cursor.fetchone()

"""
@fetchone
SELECT name
FROM genre
WHERE id = (
    SELECT genre_id
    FROM playlist_genre
    GROUP BY genre_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
"""
def getTopGenre():
    with connection.cursor() as cursor:
        # execute query
        cursor.execute("SELECT name FROM genre WHERE id = (SELECT genre_id FROM playlist_genre GROUP BY genre_id ORDER BY COUNT(*) DESC LIMIT 1)")

        # fetch results
        return cursor.fetchone()

"""
@fetchone
SELECT decade_id
FROM playlist_decade
GROUP BY decade_id
ORDER BY COUNT(*) DESC
LIMIT 1
"""
def getTopDecade():
    with connection.cursor() as cursor:
        # execute query
        cursor.execute("SELECT decade_id FROM playlist_decade GROUP BY decade_id ORDER BY COUNT(*) DESC LIMIT 1")

        # fetch results
        return cursor.fetchone()

"""
@fetchone
SELECT name
FROM country
WHERE id = (
    SELECT country_id
    FROM playlist_country
    GROUP BY country_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
"""
def getTopCountry():
    with connection.cursor() as cursor:
        # execute query
        cursor.execute("SELECT name FROM country WHERE id = (SELECT country_id FROM playlist_country GROUP BY country_id ORDER BY COUNT(*) DESC LIMIT 1)")

        # fetch results
        return cursor.fetchone()
