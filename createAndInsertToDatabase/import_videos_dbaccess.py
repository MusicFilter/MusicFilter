from django.db import connection

def insert_video(video):
    query = """
            INSERT INTO video (id, title, description, artist_id, is_cover, is_live, is_with_lyrics)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """

    with connection.cursor() as cur:
        cur.execute(query, (video['id'], video['title'], video['description'], video['artist_id'],
                            video['is_cover'], video['is_live'], video['is_with_lyrics']))
        
def insert_artist(artist):
    query = """
            INSERT INTO artist (id, name, dominant_decade, country_id)
            VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """

    with connection.cursor() as cur:
        cur.execute(query, (artist['id'], artist['name'], artist['dominant_decade'],artist['country_id']))

def insert_genre(genre):
    query = """
            INSERT INTO genre (id, name)
            VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """

    with connection.cursor() as cur:
        cur.execute(query, (genre['id'], genre['name']))

def insert_artist_genre(artist_genre):
    query = """
            INSERT INTO artist_genre (artist_id, genre_id)
            VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE artist_id=artist_id, genre_id=genre_id
            """

    with connection.cursor() as cur:
        cur.execute(query, (artist_genre['artist_id'], artist_genre['genre_id']))

def insert_country(country):
    query = """
            INSERT INTO country (id, name)
            VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """

    with connection.cursor() as cur:
        cur.execute(query, (country['id'], country['name']))

def initial_commands():
    with connection.cursor() as cur:
        cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
