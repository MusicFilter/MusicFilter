from datetime import datetime
from random import shuffle

class Artist:
    
    """
    self.id
    self.name
    """
    
    """
    Constructor
    """
    def __init__(self, id):
        # init fields
        self.id = id
        self.name = ''

        # populate fields from BD
        self.fetch()
        
    """
    toString
    """
    def __str__(self):
        return 'Artist[id={0}, name={1}]'.format(self.id, self.name)
    
    """
    Populate fields from DB
    """
    def fetch(self):
        # TODO
        pass
    

class Genre:
    
    """
    self.id
    self.name
    """
    
    """
    Constructor
    """
    def __init__(self, id):
        # init fields
        self.id = id
        self.name = ''

        # populate fields from BD
        self.fetch()
        
    """
    toString
    """
    def __str__(self):
        return 'Genre[id={0}, name={1}]'.format(self.id, self.name)
    
    """
    Don't fetch video list!
    """
    def fetch(self):
        # TODO
        pass
    

class Country:
    
    """
    self.id
    self.name
    """
    
    """
    Constructor
    """
    def __init__(self, id):
        # init fields
        self.id = id
        self.name = ''

        # populate fields from BD
        self.fetch()
        
    """
    toString
    """
    def __str__(self):
        return 'Country[id={0}, name={1}]'.format(self.id, self.name)
    
    """
    Populate fields from DB
    """
    def fetch(self):
        # TODO
        pass
    

class Playlist:

    """
    Playlist object
    self.id = [int] playlist_id from DB
    self.hits = [int] total_hits from DB
    self.createdOn = [datetime] creation date from DB
    self.video_list = [list] of [string] youtube video id
    self.name = [string] playlist's name
    self.elapsed = [string] how much time passed since creation
    self.is_live
    self.is_cover
    self.is_with_lyrics
    self.artists
    self.genres
    self.countries
    self.decades
    """

    """
    Constructor
    """
    def __init__(self, id):
        # init fields
        self.id = id
        self.hits = 0
        self.createdOn = datetime(2000, 1, 1)
        self.video_list = []
        self.name = ''
        self.artists = []
        self.decades = []
        self.countries = []
        self.genres = []
        self.is_live = False
        self.is_cover = False
        self.is_with_lyrics = False

        self.elapsed = 0

        # populate fields from BD
        self.fetch()

    """
    toString
    """
    def __str__(self):
        return 'Playlist[id={0}, hits={1}, createdOn={2}]'.format(self.id, self.hits, self.createdOn)

    """
    Populate fields from DB
    Don't fetch video list!
    """
    def fetch(self):
        # TODO
        pass

    """
    Fetch video list
    """
    def fetch_video_list(self):
        # TODO
        pass
    
    def getDescription(self):
        
        props = ""
        artists = ""
        genres = ""
        countries = ""
        decades = ""
        
        if self.is_live:
            props += "live, "
            
        if self.is_cover:
            props += "cover version, "
            
        if self.is_with_lyrics:
            props += "lyrics included, "
            
        if props != "":
            props = props[:-2]
        
        for artist in self.artists:
            artists += artist + ", "
            
        if artists != "":
            artists = "by " + artists
                        
        for genre in self.genres:
            genres += genre + ", "
            
        if genres != "":
            genres = "of type " + genres
            
        for decade in self.decades:
            decades += decade + ", " 
            
        if decades != "":
            decades = "from " + decades
            
        for country in self.countries:
            countries += country + ", "
        
        if countries != "":
            countries = "from " + countries[:-2]    
            
        return 'Listening to {0} videos {1} {2} {3} {4} !'.format(props, genres, artists, decades, countries)

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

    def reshuffle(self):
        shuffle(self.video_list)
