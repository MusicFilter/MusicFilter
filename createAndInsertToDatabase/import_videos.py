import json
import requests
from collections import Counter

from apiclient.discovery import build

DEVELOPER_KEY = "AIzaSyCUyZXok3rrT88dpo2FEPY7hripKOmdRVQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

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
SELECT_ARTISTS_WITH_SINGLE_FREEBASE_ID = WDQS_PREFIXES + """
    SELECT ?item WHERE {
        ?item wdt:P646 ?freebaseId .
        { SELECT DISTINCT ?item WHERE {
            { ?item wdt:P106 wd:Q177220 . }
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

ARTIST_TYPE_BAND = 'B'
ARTIST_TYPE_SOLO = 'S'

VIDEOS_PER_ARTIST = 2

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

def wikidata_label(entity):
    return entity['labels']['en']['value']

def wikidata_string_values(entity, property):
    return [value['mainsnak']['datavalue']['value'] for value in entity['claims'].get(property, [])]

def wikidata_item_values(entity, property):
    return [value['mainsnak']['datavalue']['value']['numeric-id'] for value in entity['claims'].get(property, [])]

def wikidata_time_values(entity, property):
    return [value['mainsnak']['datavalue']['value']['time'] for value in entity['claims'].get(property, [])]

def wikidata_entity_url_to_id(entity_url):
    return int(entity_url[len("http://www.wikidata.org/entity/Q"):])

def wikidata_entity_string_to_id(entity_string):
    return int(entity_string[len("Q"):])

def youtube_video(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    # videos_list_response = youtube.videos().list(part="id,snippet,contentDetails,topicDetails", id=video_id).execute()
    videos_list_response = youtube.videos().list(part="id,contentDetails", id=video_id).execute()

    if not videos_list_response["items"]:
        raise Exception("Video '%s' was not found." % video_id)

    return videos_list_response["items"][0]

def youtube_search_by_topic(topic_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    search_list_response = youtube.search().list(part="snippet",
                                                 maxResults=VIDEOS_PER_ARTIST,
                                                 order="viewCount",
                                                 topicId=topic_id,
                                                 type="video",
                                                 videoCategoryId=10,
                                                 videoEmbeddable="true"
                                                 ).execute()

    return search_list_response.get("items", [])

def artist_videos(artist):
    artist_wikidata_id = wikidata_entity_string_to_id(artist['id'])
    artist_freebase_id = wikidata_string_values(artist, PROP_FREEBASE_ID)[0]

    search_results = youtube_search_by_topic(artist_freebase_id)

    videos = []
    for search_result in search_results:
        video_id = search_result['id']['videoId']

        video = youtube_video(video_id)

        video_details = {}
        video_details['youtube_id'] = video_id
        video_details['title'] = search_result["snippet"]["title"]
        video_details['description'] = search_result["snippet"]["description"]
        video_details['duration'] = video["contentDetails"]["duration"]
        video_details['is_cover'] = "Y" if ("cover" in search_result["snippet"]["title"].lower() or "cover" in search_result["snippet"]["description"].lower()) else "N"
        video_details['is_live'] = "Y" if ("live" in search_result["snippet"]["title"].lower() or "cover" in search_result["snippet"]["description"].lower()) else "N"
        video_details['artist_id'] = artist_wikidata_id

        videos.append(video_details)

    return videos

def genre_id_to_top_genre_id(genre_id):
    genre = wikidata_entity(genre_id)
    parent_genre_ids = wikidata_item_values(genre, PROP_SUBCLASS_OF)
    if ((not parent_genre_ids) or (ID_MUSIC in parent_genre_ids)
        or (ID_MUSICAL_WORK in parent_genre_ids) or (ID_POPULAR_MUSIC in parent_genre_ids)):
        return genre_id
    else:
        # Music genres have at most a single parent, so we simply use parent_genre_ids[0].
        return genre_id_to_top_genre_id(parent_genre_ids[0])

def artist_genres(artist):
    genres = []

    genre_ids = wikidata_item_values(artist, PROP_GENRE)

    top_genre_ids = [genre_id_to_top_genre_id(genre_id) for genre_id in genre_ids]
    top_genre_ids = list(set(top_genre_ids))

    for top_genre_id in top_genre_ids:
        genres.append({'genre_id': top_genre_id,
                       'name': wikidata_label(wikidata_entity(top_genre_id))})

    return genres

def artist_type(artist):
    if ID_HUMAN in wikidata_item_values(artist, PROP_INSTANCE_OF):
        return ARTIST_TYPE_SOLO
    else:
        return ARTIST_TYPE_BAND

def artist_country(artist):
    if artist_type(artist) == ARTIST_TYPE_SOLO:
        location_property = PROP_PLACE_OF_BIRTH
    else:
        location_property = PROP_LOCATION_OF_FORMATION

    location_list = wikidata_item_values(artist, location_property)
    if not location_list:
        return None

    location = wikidata_entity(location_list[0])

    country_list = wikidata_item_values(location, PROP_COUNTRY)
    if not country_list:
        return None

    country = wikidata_entity(country_list[0])

    return wikidata_label(country)

def artist_decade(artist):
    artist_id = wikidata_entity_string_to_id(artist['id'])

    response = wdqs_query(SELECT_ALBUMS_BY_PERFORMER % artist_id)

    years = []
    for item in response['results']['bindings']:
        wikidata_id = wikidata_entity_url_to_id(item['item']['value'])
        entity = wikidata_entity(wikidata_id)
        publication_dates = wikidata_time_values(entity, PROP_PUBLICATION_DATE)
        years.extend([int(publication_date[1:5]) for publication_date in publication_dates])

    if not years:
        return None

    decades = [year / 10 * 10 for year in years]
    return Counter(decades).most_common(1)[0][0]

def get_artist_details(artist_id):
    artist_details = {}

    artist = wikidata_entity(artist_id)

    artist_details['artist_id'] = artist_id
    artist_details['name'] = wikidata_label(artist)
    artist_details['country'] = artist_country(artist)
    artist_details['type'] = artist_type(artist)
    artist_details['decade'] = artist_decade(artist)
    artist_details['genres'] = artist_genres(artist)
    artist_details['videos'] = artist_videos(artist)

    return artist_details

def select_artists():
    # Search for singers and bands with a "Freebase ID" property.
    response = wdqs_query(SELECT_ARTISTS_WITH_SINGLE_FREEBASE_ID)

    artists = []
    for artist in response['results']['bindings']:
        artists.append(wikidata_entity_url_to_id(artist['item']['value']))
    return artists

def build_database():
    artist_ids = select_artists()

    for artist_id in artist_ids:
        artist_details = get_artist_details(artist_id)
