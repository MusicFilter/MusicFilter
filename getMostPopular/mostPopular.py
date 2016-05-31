##create_playlistArtist_table = """CREATE TABLE PLAYLIST_ARTIST(
##						playlist_id INT,
##						artist_id INT,
##						FOREIGN KEY (artist_id)
##							REFERENCES  ARTIST(artist_id)
##							ON DELETE CASCADE)"""

#first group by count(artist_id), then select max

#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import MySQLdb as mdb
from password import *

warnings.filterwarnings("ignore", "unknown table.*")

con = mdb.connect('localhost', 'root', getPassword(), 'musicfilter', use_unicode=True, charset='utf8')

cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")


###first group by count(artist_id), then select max
##getMostPopularArtist =\
##"""
##SELECT artist_name
##FROM Artist
##WHERE Artist_id in 
##        (SELECT artist_id
##        FROM (SELECT artist_id, count(playlist_id)
##             FROM PLAYLIST_ARTIST
##             GROUP BY artist_id
##             HAVING count(playlist_id) >= 
##			(SELECT max(popularity)
##			FROM
##			    (SELECT artist_id, count(playlist_id) as popularity
##			    FROM PLAYLIST_ARTIST
##			    GROUP BY artist_id
##			    ) as countPlaylistsPerArtist
##			)
##	    ) as maxIDsAndCounts
##	)
##"""

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

##getMostPopularCountry =\
##"""
##SELECT country_name
##FROM country
##WHERE country_id in
##         (SELECT country_id
##             FROM PLAYLIST_COUNTRY
##             GROUP BY country_id
##             HAVING count(playlist_id) >= 
##			(SELECT max(popularity)
##			FROM
##			    (SELECT count(playlist_id) as popularity
##			    FROM PLAYLIST_COUNTRY
##			    GROUP BY country_id
##			    ) as countPlaylistsPerCountry
##			)
##	)
##"""



#ron TODO: continue decade, not this version but the version in the bottom of the file

##getMostPopularDecade =\
##"""
##SELECT artist.dominant_decade
##FROM artist
##WHERE artist.dominant_decade in 
##        (SELECT decade
##             FROM PLAYLIST_DECADE
##             GROUP BY decade
##             HAVING count(playlist_id) >= 
##			(SELECT max(popularity)
##			FROM
##			    (SELECT count(playlist_id) as popularity
##			    FROM PLAYLIST_DECADE
##			    GROUP BY decade
##			    ) as countPlaylistsPerDecade
##			)
##	)
##"""




##smallQuery =\
##"""
##SELECT max(popularity)
##            FROM
##                (SELECT artist_id, count(playlist_id) as popularity
##                FROM PLAYLIST_ARTIST
##                GROUP BY artist_id
##                ) as countPlaylistsPerArtist
##
##"""
##
##
##tryoutQuery =\
##"""
##    SELECT chosenName
##    FROM
##        (SELECT artist.artist_name as chosenName
##        FROM artist
##        WHERE artist.artist_name = 'john'
##        ) as johhnyBoy
##"""
##
##moreComplex =\
##"""
##            SELECT artist_id, count(playlist_id)
##             FROM PLAYLIST_ARTIST
##             GROUP BY artist_id
##             HAVING count(playlist_id) >= 
##			(SELECT max(popularity)
##			FROM
##			    (SELECT artist_id, count(playlist_id) as popularity
##			    FROM PLAYLIST_ARTIST
##			    GROUP BY artist_id
##			    ) as countPlaylistsPerArtist
##			)
##"""


#cur.execute(moreComplex)  #works
#cur.execute(tryoutQuery)  #works

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
##cur.execute(getMostPopularDecade)
##result = cur.fetchall()
##for row in result:
##  print row['dominant_decade']
##
##  
##cur.execute(getMostPopularCountry)
##result = cur.fetchall()
##for row in result:
##  print row['country_name']

con.commit()



                  
###first, we need to count for each decade, how many
###appearances it has in a playlist.
###Then we need to sum it for all playlists.
###then, we take the maximum of all decades
##
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
##sumDecadeInPlaylist =
##"""
##SELECT #need to calculate max, and then select the decade with max by using having
##    decade, max(
##FROM
##    (SELECT decade, count(popularity) as popDecade
##
##    FROM
##        (SELECT
##            Artist.artist_id , popularity, Artist.decade
##        FROM
##            ARTIST, 
##            (SELECT artist_id as aId, count(playlist_id) as popularity
##            FROM
##                PLAYLIST_ARTIST
##            GROUP BY
##                artist_id)
##        WHERE
##            ARTIST.artist_id = aId )
##    GROUP BY decade)


