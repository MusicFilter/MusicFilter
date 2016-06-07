from django.db import connection
import time
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
SELECT id, name, creation_date, description, play_count
FROM playlist
ORDER BY play_count
DESC LIMIT <count>
"""
def getTrending(count):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT id, name, creation_date, description, play_count FROM playlist ORDER BY play_count DESC LIMIT %s", [count])

        # fetch results
        return dictfetchall(cursor)


"""
@fetchall
SELECT id, name, creation_date, description, play_count
FROM playlist
ORDER BY creation_date
DESC LIMIT <count>
"""
def getNewest(count):
    with connection.cursor() as cursor:

        # execute queries
        cursor.execute("SELECT id, name, creation_date, description, play_count FROM playlist ORDER BY creation_date DESC LIMIT %s", [count])

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
        cursor.execute("SELECT video_id FROM playlist_video WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchone
SELECT id, creation_date, description, play_count
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
        cursor.execute("SELECT * FROM playlist WHERE id = %s", [playlist_id])

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
MONSTERQUERY
"""
def loadVideos(playlist, mode=objects.LOAD_FROM_TABLE):

    if mode == objects.LOAD_FROM_TABLE:
        # reload playlist from DB
        print 'loading from playlist_video table'
        with connection.cursor() as cursor:
            cursor.execute("SELECT video_id FROM playlist_video WHERE playlist_id = %s", [playlist.id])
            return cursor.fetchall()

    select_data = []
    print 'loading from monsterquery'

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
                                                     LIMIT 110)
                                            AS random)
            LIMIT 100;
        """

        # assemble main query
        main_query = '{0} ({1} FROM {2} WHERE {3}) as filtered_videos {4}'.format(
            header, filtered_videos_select, fromstring, wherestring, footer
        )

        # assemble monster query
        query = '{0} {1}'.format(count_query, main_query)
        
        print query
        print frompart
        print fromstring

        # execute query
        try:
            cursor.execute(count_query, select_data)
        except Exception as e:
            print e
            print cursor._last_executed

        try:
            cursor.execute(main_query, select_data)
        except Exception as e:
            print e
            print cursor._last_executed

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
        insert_data = [playlist_id]

        # part1
        update_command = """DELETE FROM playlist_video
               WHERE playlist_id = %s;
               """

        # part2 - concatenate all rows to one query
        for video_id in video_ids:
            update_command += """INSERT INTO playlist_video
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
(name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
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
                (name, creation_date, description, play_count, is_live, is_cover, is_with_lyrics, free_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        insert_data = [p.name, time.strftime('%Y-%m-%d %H:%M:%S'), p.description, 0, p.live, p.cover, p.withlyrics, p.text]
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
                    (playlist_id, decade_id)
                    VALUES (LAST_INSERT_ID(), %s);
                    """
            cursor.execute(insert_command, [decade])

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
SELECT artist_id
FROM playlist_artist
WHERE playlist_id = <playlist_id>
"""
def getFilterArtists(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT artist_id FROM playlist_artist WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchall
SELECT country_id
FROM playlist_country
WHERE playlist_id = <playlist_id>
"""
def getFilterCountries(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT country_id FROM playlist_country WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return cursor.fetchall()


"""
@fetchall
SELECT genre_id
FROM playlist_genre
WHERE playlist_id = <playlist_id>
"""
def getFilterGenres(playlist_id):
    with connection.cursor() as cursor:

        # execute query
        cursor.execute("SELECT genre_id FROM playlist_genre WHERE playlist_id = %s", [playlist_id])

        # fetch results
        return cursor.fetchall()
