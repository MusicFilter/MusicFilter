#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import MySQLdb as mdb
from password import *

warnings.filterwarnings("ignore", "unknown table.*")

con = mdb.connect('localhost', 'root', getPassword(), 'musicfilter', use_unicode=True, charset='utf8')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")


getMostPopularArtist =\
"""
SELECT artist_name
FROM Artist
WHERE Artist_id in
         (SELECT artist_id
             FROM PLAYLIST_ARTIST
             GROUP BY artist_id
             HAVING count(playlist_id) >= 
			(SELECT max(popularity)
			FROM
			    (SELECT count(playlist_id) as popularity
			    FROM PLAYLIST_ARTIST
			    GROUP BY artist_id
			    ) as countPlaylistsPerArtist
			)
	)
"""


##getMostPopularGenre =\
##"""
##SELECT genre_name
##FROM genre
##WHERE genre_id in
##         (SELECT genre_id
##             FROM PLAYLIST_GENRE
##             GROUP BY genre_id
##             HAVING count(playlist_id) >= 
##			(SELECT max(popularity)
##			FROM
##			    (SELECT count(playlist_id) as popularity
##			    FROM PLAYLIST_GENRE
##			    GROUP BY genre_id
##			    ) as countPlaylistsPerGenre
##			)
##	)
##"""

getMostPopularCountry =\
"""
SELECT country_name
FROM country
WHERE country.country_id in

    (SELECT Artist.country_id
        FROM
            ARTIST, 
            (SELECT artist_id as aIdBlaBla, count(playlist_id) as numPlaylistArtistAppearsInBlaBla
            FROM PLAYLIST_ARTIST
            GROUP BY artist_id
            ) as countPlaylistsPerArtistBlaBla
        WHERE ARTIST.artist_id = aIdBlaBla
        GROUP BY Artist.country_id
        HAVING sum(numPlaylistArtistAppearsInBlaBla) >= 

        
          (SELECT max(countryPopularity)
          FROM
              (SELECT sum(numPlaylistArtistAppearsIn) as countryPopularity
              FROM
                  ARTIST, 
                  (SELECT artist_id as aId, count(playlist_id) as numPlaylistArtistAppearsIn
                  FROM PLAYLIST_ARTIST
                  GROUP BY artist_id
                  ) as countPlaylistsPerArtist
              WHERE ARTIST.artist_id = aId
              GROUP BY Artist.country_id
              ) as CountryPopularityTable
          )
    )
         
"""


      
###subquery calcs: for each artist: how mayn playlists
###is he in
###id    p.id    decade     popularity
###zztop p1,p2    80's      2(appears in 2 playlists)  
###acdc 
###after GROUP BY decade:
####decade   id     p.id      pop
####80's     zz     p1,p2     2
####         jovi   p1,p3,p4  3
####70's     led ze p2        1
####         stones p5,p7     2
##

getMostPopularDecade =\
"""
SELECT Artist.dominant_decade
        FROM
            ARTIST, 
            (SELECT artist_id as aIdBlaBla, count(playlist_id) as numPlaylistArtistAppearsInBlaBla
            FROM PLAYLIST_ARTIST
            GROUP BY artist_id
            ) as countPlaylistsPerArtistBlaBla
        WHERE ARTIST.artist_id = aIdBlaBla
        GROUP BY Artist.dominant_decade
        HAVING sum(numPlaylistArtistAppearsInBlaBla) >= 

        
          (SELECT max(decadePopularity)
          FROM
              (SELECT Artist.artist_id , sum(numPlaylistArtistAppearsIn) as decadePopularity, Artist.dominant_decade
              FROM
                  ARTIST, 
                  (SELECT artist_id as aId, count(playlist_id) as numPlaylistArtistAppearsIn
                  FROM PLAYLIST_ARTIST
                  GROUP BY artist_id
                  ) as countPlaylistsPerArtist
              WHERE ARTIST.artist_id = aId
              GROUP BY Artist.dominant_decade
              ) as DecadePopularityTable
          )
"""



cur.execute(getMostPopularArtist)
result = cur.fetchall()
for row in result:
  print row['artist_name']


##cur.execute(getMostPopularGenre)
##result = cur.fetchall()
##for row in result:
##  print row['genre_name']
##
##  
cur.execute(getMostPopularDecade)
result = cur.fetchall()
for row in result:
  print row['dominant_decade']

  
cur.execute(getMostPopularCountry)
result = cur.fetchall()
for row in result:
  print row['country_name']

con.commit()
