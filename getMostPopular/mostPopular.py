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
SELECT name
FROM artist
WHERE id in
         (SELECT artist_id
             FROM playlist_artist
             GROUP BY artist_id
             HAVING count(playlist_id) >= 
			(SELECT max(popularity)
			FROM
			    (SELECT count(playlist_id) as popularity
			    FROM playlist_artist
			    GROUP BY artist_id
			    ) as countPlaylistsPerArtist
			)
	)
"""


getMostPopularGenre =\
"""
SELECT name
FROM genre
WHERE id in
          (SELECT genre_id
          FROM
              (SELECT artist_id, numPlaylistArtistAppearsInBlaBla, genre_id
              FROM artist_genre,
                  (SELECT artist_id as aIdBlaBla, count(playlist_id) as numPlaylistArtistAppearsInBlaBla
                  FROM playlist_artist
                  GROUP BY artist_id
                  ) as countPlaylistsPerArtistBlaBla
              WHERE aIdBlaBla = artist_genre.artist_id
              ) as whateverBlaBla
          GROUP BY genre_id    
          HAVING sum(numPlaylistArtistAppearsInBlaBla) >=
      
                    (SELECT max(genrePopularity)
                    FROM
                        (SELECT genre_id, sum(numPlaylistArtistAppearsIn) as genrePopularity
                        FROM
                          (SELECT artist_id, numPlaylistArtistAppearsIn, genre_id
                                  FROM artist_genre,
                                      (SELECT artist_id as aId, count(playlist_id) as numPlaylistArtistAppearsIn
                                      FROM playlist_artist
                                      GROUP BY artist_id
                                      ) as countPlaylistsPerArtist
                                  WHERE aId = artist_genre.artist_id
                          ) as whatever
                        GROUP BY genre_id    
                        ) as GenrePopularityTable
                    )
          )
"""


getMostPopularCountry =\
"""
SELECT name
FROM country
WHERE id in

    (SELECT artist.country_id
        FROM
            artist, 
            (SELECT artist_id as aIdBlaBla, count(playlist_id) as numPlaylistArtistAppearsInBlaBla
            FROM playlist_artist
            GROUP BY artist_id
            ) as countPlaylistsPerArtistBlaBla
        WHERE artist.id = aIdBlaBla
        GROUP BY artist.country_id
        HAVING sum(numPlaylistArtistAppearsInBlaBla) >= 

        
          (SELECT max(countryPopularity)
          FROM
              (SELECT sum(numPlaylistArtistAppearsIn) as countryPopularity
              FROM
                  artist, 
                  (SELECT artist_id as aId, count(playlist_id) as numPlaylistArtistAppearsIn
                  FROM playlist_artist
                  GROUP BY artist_id
                  ) as countPlaylistsPerArtist
              WHERE artist.id = aId
              GROUP BY artist.country_id
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
SELECT artist.dominant_decade
        FROM
            artist, 
            (SELECT artist_id as aIdBlaBla, count(playlist_id) as numPlaylistArtistAppearsInBlaBla
            FROM PLAYLIST_ARTIST
            GROUP BY artist_id
            ) as countPlaylistsPerArtistBlaBla
        WHERE artist.id = aIdBlaBla
        GROUP BY artist.dominant_decade
        HAVING sum(numPlaylistArtistAppearsInBlaBla) >= 

        
          (SELECT max(decadePopularity)
          FROM
              (SELECT artist.id , sum(numPlaylistArtistAppearsIn) as decadePopularity, artist.dominant_decade
              FROM
                  artist, 
                  (SELECT artist_id as aId, count(playlist_id) as numPlaylistArtistAppearsIn
                  FROM PLAYLIST_ARTIST
                  GROUP BY artist_id
                  ) as countPlaylistsPerArtist
              WHERE artist.id = aId
              GROUP BY artist.dominant_decade
              ) as DecadePopularityTable
          )
"""



cur.execute(getMostPopularArtist)
result = cur.fetchall()
for row in result:
  print row['name']


cur.execute(getMostPopularGenre)
result = cur.fetchall()
for row in result:
  print row['name']

  
cur.execute(getMostPopularDecade)
result = cur.fetchall()
for row in result:
  print row['dominant_decade']

  
cur.execute(getMostPopularCountry)
result = cur.fetchall()
for row in result:
  print row['name']

con.commit()
