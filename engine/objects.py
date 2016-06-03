from datetime import datetime
from random import shuffle

class Playlist:

    """
    Playlist object
    self.id = [int] playlist_id from DB
    self.hits = [int] total_hits from DB
    self.createdOn = [datetime] creation date from DB
    self.video_list = [list] of [string] youtube video id
    self.name = [string] playlist's name
    self.elapsed = [string] how much time passed since creation
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
        self.description = ''
        self.elapsed = 0

    """
    toString
    """
    def __str__(self):
        return 'Playlist[id={0}, hits={1}, createdOn={2}]'.format(self.id, self.hits, self.createdOn)
    

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
