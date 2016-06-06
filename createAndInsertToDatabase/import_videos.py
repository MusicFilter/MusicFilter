import json
import requests
import time
from collections import Counter
from requests.exceptions import ConnectionError

from apiclient.discovery import build
from apiclient.errors import HttpError

from demo_addingFromAPI import *

DEVELOPER_KEY = "AIzaSyCUyZXok3rrT88dpo2FEPY7hripKOmdRVQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

QUOTA_EXCEEDED_ERROR = 403
QUOTA_EXCEEDED_WAIT = 600

CONNECTION_ERROR_WAIT = 60

WDQS_PREFIXES = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wikibase: <http://wikiba.se/ontology#>

"""

# P31: instance of
# P106: occupation
# P279: subclass of
# P646: Freebase ID
# Q177220: singer
# Q215380: band
# Q488205: singer-songwriter
SELECT_ARTISTS_WITH_SINGLE_FREEBASE_ID = WDQS_PREFIXES + """
    SELECT ?item WHERE {
        ?item wdt:P646 ?freebaseId .
        { SELECT DISTINCT ?item WHERE {
            { ?item wdt:P106 wd:Q177220 . }
            UNION
            { ?item wdt:P106 wd:Q488205 . }
            UNION
            { ?item wdt:P31 wd:Q215380. }
            UNION
            { ?item wdt:P31 ?bandType.
              ?bandType wdt:P279 wd:Q215380. }
          }
        }
    }
    GROUP BY ?item
    HAVING (COUNT(?freebaseId) = 1)
"""

# P175: performer
# P31: instance of
# Q482994: album
# Q209939: live album
# Q222910: compilation album
SELECT_ALBUMS_BY_PERFORMER = WDQS_PREFIXES + """
    SELECT DISTINCT ?item WHERE {
        ?item wdt:P175 wd:Q%d .
        { ?item wdt:P31 wd:Q482994 . }
        UNION
        { ?item wdt:P31 wd:Q209939 . }
        MINUS
        { ?item wdt:P31 wd:Q222910 . }
    }
"""

ID_HUMAN = 5
ID_MUSIC = 638
ID_SONG = 7366
ID_MUSIC_GENRE = 188451
ID_POPULAR_MUSIC = 373342
ID_MUSICAL_WORK = 2188189

PROP_COUNTRY = 'P17'
PROP_PLACE_OF_BIRTH = 'P19'
PROP_INSTANCE_OF = 'P31'
PROP_GENRE = 'P136'
PROP_SUBCLASS_OF = 'P279'
PROP_PUBLICATION_DATE = 'P577'
PROP_FREEBASE_ID = 'P646'
PROP_LOCATION_OF_FORMATION = 'P740'

VIDEOS_PER_ARTIST = 8

WIKIDATA_ENTITIES = {}

def wdqs_query(query):
    service_url = "https://query.wikidata.org/sparql"
    r = requests.get(service_url, {'query': query, 'format': 'json'})
    return json.loads(r.text)

def wikidata_entity(wikidata_id):
    service_url = "https://www.wikidata.org/w/api.php"
    r = requests.get(service_url, {'action': 'wbgetentities',
                                   'ids': 'Q%d' % wikidata_id,
                                   'props': 'labels|descriptions|claims',
                                   'languages': 'en',
                                   'format': 'json'})
    return json.loads(r.text)['entities']['Q%d' % wikidata_id]

def memoized_wikidata_entity(wikidata_id):
    if wikidata_id not in WIKIDATA_ENTITIES:
        WIKIDATA_ENTITIES[wikidata_id] = wikidata_entity(wikidata_id)

    return WIKIDATA_ENTITIES[wikidata_id]

def wikidata_label(entity):
    return entity.get('labels', {}).get('en', {}).get('value')

def wikidata_values(entity, property, inner_key=None):
    values = []
    for claim in entity.get('claims', {}).get(property, []):
        if claim['mainsnak']['snaktype'] == 'value':
            value = claim['mainsnak']['datavalue']['value']
            if inner_key is not None:
                value = value[inner_key]
            values.append(value)
    return values

def wikidata_string_values(entity, property):
    return wikidata_values(entity, property)

def wikidata_item_values(entity, property):
    return wikidata_values(entity, property, 'numeric-id')

def wikidata_time_values(entity, property):
    return wikidata_values(entity, property, 'time')

def wikidata_entity_url_to_id(entity_url):
    return int(entity_url[len("http://www.wikidata.org/entity/Q"):])

def wikidata_entity_string_to_id(entity_string):
    return int(entity_string[len("Q"):])

def youtube_search_by_topic(topic_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_list_response = None
    while search_list_response is None:
        try:
            search_list_response = youtube.search().list(part="snippet",
                                                         maxResults=VIDEOS_PER_ARTIST,
                                                         order="viewCount",
                                                         topicId=topic_id,
                                                         type="video",
                                                         videoCategoryId=10,
                                                         videoEmbeddable="true"
                                                         ).execute()
        except HttpError as e:
            if e.resp.status == QUOTA_EXCEEDED_ERROR:
                time.sleep(QUOTA_EXCEEDED_WAIT)
            else:
                raise

    return search_list_response.get("items", [])

def artist_videos(artist):
    videos = []

    artist_wikidata_id = wikidata_entity_string_to_id(artist['id'])

    artist_freebase_ids = wikidata_string_values(artist, PROP_FREEBASE_ID)
    if not artist_freebase_ids:
        return videos

    artist_freebase_id = artist_freebase_ids[0]

    search_results = youtube_search_by_topic(artist_freebase_id)

    for search_result in search_results:
        video_details = {}
        video_details['video_id'] = search_result['id']['videoId']
        video_details['title'] = search_result["snippet"]["title"]
        video_details['description'] = search_result["snippet"]["description"]
        video_details['is_cover'] = int("cover" in search_result["snippet"]["title"].lower())
        video_details['is_live'] = int("live" in search_result["snippet"]["title"].lower())
        video_details['with_lyrics'] = int("lyrics" in search_result["snippet"]["title"].lower())
        video_details['artist_id'] = artist_wikidata_id

        videos.append(video_details)

    return videos

def genre_ids_to_top_genre_ids(genre_ids):
    top_genre_ids = []

    for genre_id in genre_ids:
        genre = memoized_wikidata_entity(genre_id)

        if ID_MUSIC_GENRE in wikidata_item_values(genre, PROP_INSTANCE_OF):
            parent_genre_ids = wikidata_item_values(genre, PROP_SUBCLASS_OF)
            if ((not parent_genre_ids) or (ID_MUSIC in parent_genre_ids)
                or (ID_MUSICAL_WORK in parent_genre_ids) or (ID_POPULAR_MUSIC in parent_genre_ids)):
                top_genre_ids.append(genre_id)
            else:
                top_genre_ids.extend(genre_ids_to_top_genre_ids(parent_genre_ids))

    return list(set(top_genre_ids))

def artist_genres(artist):
    genres = []

    genre_ids = wikidata_item_values(artist, PROP_GENRE)

    top_genre_ids = genre_ids_to_top_genre_ids(genre_ids)

    for top_genre_id in top_genre_ids:
        genres.append({'genre_id': top_genre_id,
                       'genre_name': wikidata_label(memoized_wikidata_entity(top_genre_id))})

    return genres

def artist_is_band(artist):
    return int(ID_HUMAN not in wikidata_item_values(artist, PROP_INSTANCE_OF))

def artist_country(artist):
    if artist_is_band(artist):
        location_property = PROP_LOCATION_OF_FORMATION
    else:
        location_property = PROP_PLACE_OF_BIRTH

    locations = wikidata_item_values(artist, location_property)
    if not locations:
        return None

    location = wikidata_entity(locations[0])

    countries = wikidata_item_values(location, PROP_COUNTRY)
    if not countries:
        return None

    country_id = countries[0]
    country = memoized_wikidata_entity(country_id)

    return {'country_id': country_id, 'country_name': wikidata_label(country)}

def artist_decade(artist):
    artist_id = wikidata_entity_string_to_id(artist['id'])

    response = wdqs_query(SELECT_ALBUMS_BY_PERFORMER % artist_id)

    years = []
    for item in response['results']['bindings']:
        wikidata_id = wikidata_entity_url_to_id(item['item']['value'])
        entity = wikidata_entity(wikidata_id)
        publication_date_years = [int(pub_date[1:5]) for pub_date in wikidata_time_values(entity, PROP_PUBLICATION_DATE)]
        years.extend([year for year in publication_date_years if year >= 1940])

    if not years:
        return None

    decades = [year / 10 * 10 for year in years]
    return Counter(decades).most_common(1)[0][0]

def get_artist_details(artist_id):
    artist_details = {}

    artist = wikidata_entity(artist_id)

    artist_details['country'] = artist_country(artist)
    artist_details['genres'] = artist_genres(artist)
    artist_details['videos'] = artist_videos(artist)

    artist_details['artist_id'] = artist_id
    artist_details['artist_name'] = wikidata_label(artist)
    artist_details['is_band'] = artist_is_band(artist)
    artist_details['dominant_decade'] = artist_decade(artist)
    if artist_details['country'] is not None:
        artist_details['country_id'] = artist_details['country']['country_id']
    else:
        artist_details['country_id'] = None

    return artist_details

def select_artists():
    # Search for singers and bands with a "Freebase ID" property.
    response = wdqs_query(SELECT_ARTISTS_WITH_SINGLE_FREEBASE_ID)

    artists = []
    for artist in response['results']['bindings']:
        artists.append(wikidata_entity_url_to_id(artist['item']['value']))

    return artists

def build_database(only_new_artists=True):
    print "Selecting artists...",
    artist_ids = select_artists()
    print "DONE"
    print

    if only_new_artists:
        cur.execute("SELECT artist_id FROM artist")
        artist_ids_from_db = [artist['artist_id'] for artist in cur.fetchall()]
        artist_ids = list(set(artist_ids) - set(artist_ids_from_db))

    for artist_id in artist_ids:
        print "Getting details for artist %d..." % artist_id,
        artist_details = None
        while artist_details is None:
            try:
                artist_details = get_artist_details(artist_id)
            except ConnectionError as e:
                time.sleep(CONNECTION_ERROR_WAIT)
        print "DONE"
        print "Inserting artist %d..." % artist_id,
        insertArtist(artist_details)
        print "DONE"
        if artist_details['country'] is not None:
            print "Inserting country %d..." % artist_details['country']['country_id'],
            insertCountry(artist_details['country'])
            print "DONE"
        for genre in artist_details['genres']:
            print "Inserting genre %d..." % genre['genre_id'],
            insertGenre(genre)
            print "DONE"
            print "Inserting artist-genre %d-%d..." % (artist_id, genre['genre_id']),
            insertArtistGenre({'artist_id': artist_id, 'genre_id': genre['genre_id']})
            print "DONE"
        for video in artist_details['videos']:
            print "Inserting video %s..." % video['video_id'],
            insertVideo(video)
            print "DONE"
        print

if __name__ == '__main__':
    try:
        build_database()
    except KeyboardInterrupt:
        pass
