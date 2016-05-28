#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'root', 'password', 'musicfilter')

cur = con.cursor(mdb.cursors.DictCursor)

def updatePlaylistHits(playlistId):
    cur.execute("""UPDATE PLAYLIST
                   SET play_count = play_count + 1
                   WHERE playlist_id = %s""",(playlistId,))
    con.commit()
