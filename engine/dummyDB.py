from datetime import datetime
from objects import Playlist
from objects import Artist
import random

p1 = Playlist(1)
p1.hits = 10
p1.name = 'Best of Coldplay'
p1.createdOn = datetime(2016, 05, 24, 16, 33)
p1.video_list = ['BPNTC7uZYrI', 'YykjpeuMNEk', 'QtXby3twMmI']

p2 = Playlist(2)
p2.hits = 20
p2.name = 'Nirvana'
p2.createdOn = datetime(2016, 05, 24, 16, 37)
p2.video_list = ['hTWKbfoikeg', 'pkcJEvMcnEg', 'qv96yJYhk3M']

p3 = Playlist(3)
p3.hits = 3000
p3.name = 'Brittney!'
p3.createdOn = datetime(2016, 05, 24, 16, 40)
p3.video_list = ['CduA0TULnow', 'LOZuxwVk7TU']

p4 = Playlist(4)
p4.hits = 40
p4.name = 'GAGA!'
p4.createdOn = datetime(2016, 05, 24, 16, 42)
p4.video_list = ['bESGLojNYSo', 'niqrrmev4mA', 'd2smz_1L2_0']

p5 = Playlist(5)
p5.hits = 50
p5.name = 'Katie Perry'
p5.createdOn = datetime(2016, 05, 24, 16, 44)
p5.video_list = ['t5Sd5c4o9UM', 'QGJuMBdaqIw', 'CevxZvSJLk8']

p6 = Playlist(6)
p6.hits = 60
p6.name = 'Mumford & Sons'
p6.createdOn = datetime(2016, 05, 24, 16, 46)
p6.video_list = ['rGKfrgqWcv0', 'nMJUbZrNnA8', 'dW6SkvErFEE']

p7 = Playlist(7)
p7.hits = 70
p7.name = 'David Bowie'
p7.createdOn = datetime(2016, 05, 24, 16, 52)
p7.video_list = ['kszLwBaC4Sw', 'bsYp9q3QNaQ']

p8 = Playlist(8)
p8.hits = 80
p8.name = 'Elton John'
p8.createdOn = datetime(2016, 05, 24, 16, 53)
p8.video_list = ['NrLkTZrPZA4', 'ZHwVBirqD2s', 'hoskDZRLOCs']

p9 = Playlist(9)
p9.hits = 900
p9.name = 'God save the Queen'
p9.createdOn = datetime(2016, 05, 24, 16, 57)
p9.video_list = ['fJ9rUzIMcZQ', 'f4Mc-NYPHaQ', '-tJYN-eG1zk']

p10 = Playlist(10)
p10.hits = 100
p10.name = 'Bon Jovi'
p10.createdOn = datetime(2016, 05, 24, 16, 01)
p10.video_list = ['vx2u5uUu3DE', '9BMwcO6_hyA']

dummy_db = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]

a1 = Artist(1)
a1.name = 'The Beatles'
a1.country = 'United Kingdom'

a2 = Artist(2)
a2.name = 'Nick Cave'
a2.country = 'Australia'

a3 = Artist(3)
a3.name = 'Nirvana'
a3.country = 'United States'

a4 = Artist(4)
a4.name = 'U2'
a4.country = 'Ireland'

a5 = Artist(5)
a5.name = 'Metallica'
a5.country = 'United States'

a6 = Artist(6)
a6.name = 'R.E.M'
a6.country = 'United States'

a7 = Artist(7)
a7.name = 'The Who'
a7.country = 'United Kingdom'

artist_db = [a1, a2, a3, a4, a5, a6, a7]

def getRandomPlaylist():
    return random.choice(dummy_db)