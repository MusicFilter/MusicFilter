from datetime import datetime
from random import shuffle

POSTDICT = 1
DB_ENTRY = 2
LOAD_FROM_TABLE = 1
LOAD_FROM_RANDOMIZEQUERY = 2

class Playlist:

    """
    Playlist object
    self.id = [int] id from DB
    self.hits = [int] play_count from DB
    self.createdOn = [datetime] creation date from DB
    self.video_list = [list] of [string] youtube video id
    self.name = [string] playlist's name
    self.elapsed = [string] how much time passed since creation
    """

    """
    Constructor
    """
    def __init__(self):
        # init fields
        self.id = -1
        self.hits = 0
        self.createdOn = None
        self.video_list = []
        self.name = None
        self.description = None
        self.elapsed = 0

        # filters
        self.artists = None
        self.genres = None
        self.decades = None
        self.countries = None
        self.text = ''
        self.cover = None
        self.live = None
        self.withlyrics = None

    """
    toString
    """
    def __str__(self):
        return 'Playlist[id={0}, hits={1}, createdOn={2}, name={3}, desc={4}, elapsed={5}, video_list={6}]'.format(
            self.id, self.hits, self.createdOn, self.name, self.description, self.elapsed, self.video_list
        )

    def printFilters(self):
        print 'Filters:\nArtists:{0}\nGenres:{1}\nDecades:{2}\nCountries:{3}\nText:{4}\nCover:{5}\nLive:{6}\nLyrics:{7}'.format(
            self.artists, self.genres, self.decades, self.countries, self.text, self.cover, self.live, self.withlyrics
        )
    

    """
    Get elapsed time since creation
    """
    def getElapsed(self):
        e = datetime.now() - self.createdOn

        # resolution
        if e.days != 0:
            self.elapsed = '{0}d ago'.format(e.days)

        elif e.seconds > 3600:
            self.elapsed = '{0}h ago'.format(int(round(e.seconds / float(3600), 0)))

        elif e.seconds > 60:
            self.elapsed = '{0}m ago'.format(int(round(e.seconds / float(60), 0)))

        elif e.seconds > 0:
            self.elapsed = '{0}s ago'.format(e.seconds)

    """
    Reshuffle video list
    """
    def reshuffle(self):
        shuffle(self.video_list)


"""
Create playlist object from playlist DB entry (2) or postdict (1)
"""
def playlistFactory(p_entry, type):
    p = Playlist()

    if type == DB_ENTRY:
        p.id = p_entry['id']
        p.name = p_entry['name']
        p.createdOn = p_entry['creation_date']
        p.description = p_entry['description']
        p.hits = p_entry['play_count']
        p.cover = p_entry['is_cover']
        p.live = p_entry['is_live']
        p.withlyrics = p_entry['is_with_lyrics']
        p.text = p_entry['free_text']

    elif type == POSTDICT:
        p.artists = p_entry['artists']
        p.countries = p_entry['countries']
        p.decades = p_entry['decades']
        p.genres = p_entry['genres']
        p.name = p_entry['name']
        p.createdOn = datetime.now()
        p.text = p_entry['text']
        p.cover = p_entry['cover']
        p.live = p_entry['live']
        p.withlyrics = p_entry['withlyrics']

    return p
