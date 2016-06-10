from django.shortcuts import render
from django.http import HttpResponse
from engine import backendInterface
from engine.objects import Playlist
import json
import subprocess
import os

"""
Homepage
"""
def home(request):

    top_artist, top_genre, top_decade, top_country = backendInterface.getTopHits()

    # check if DB update is running
    psaux = subprocess.Popen(["ps aux | grep import_data"], stdout=subprocess.PIPE, shell=True).communicate()[0]
    psaux = psaux.split('\n')

    if len(psaux) < 4:
        psaux = False
    else:
        psaux = True

    context = {
        'trending':     backendInterface.getTrending(),
        'newest':       backendInterface.getNewest(),
        'top_artist':   top_artist,
        'top_genre':    top_genre,
        'top_decade':   top_decade,
        'top_country':  top_country,
        'is_updating':  psaux
    }

    return render(request, 'index.html', context)



"""
Player
"""
def player(request, playlist_id, action=None):

    p = backendInterface.getPlaylistById(playlist_id)

    # playlist not found
    if p == -1:
        
        # 'playlist not found'
        playlist404 = Playlist(-1, None, None, None, None)
        playlist404.name = 'Playlist Not Found'
        playlist404.description = 'Oops, we\'re sorry, but we couldn\'t find the playlist you were looking for...'
        playlist404.video_list = []
    
        context = {
            'playlist': playlist404
        }

    # valid playlist
    else:
            
        if action == 'reshuffle':
            p.video_list = backendInterface.loadVideos(p, commit=False)
            p.reshuffle()
            
        elif action == 'refresh':
            p.video_list = backendInterface.loadVideos(p, commit=True)
    
        # update hit count
        else:
            backendInterface.incrementHitCount(playlist_id)
            p.hits += 1
            p.video_list = backendInterface.loadVideos(p, commit=False)

        context = {
            'playlist': p,
            'action': action
        }

    return render(request, 'player.html', context)


"""
Generator
"""
def generator(request):

    playlist = None

    if request.method == 'POST':

        postdict = {}

        # get data from post request
        postdict['name'] = request.POST.get('name')
        postdict['text'] = request.POST.get('text')
        
        artists = []
        for artist in request.POST.getlist('artist'):
            artists.append(tuple(artist.split(':')))
        postdict['artists'] = artists
            
        genres = []
        for genre in request.POST.getlist('genre'):
            genres.append(tuple(genre.split(':')))
        postdict['genres'] = genres
            
        countries = []
        for country in request.POST.getlist('country'):
            countries.append(tuple(country.split(':')))
        postdict['countries'] = countries
        
        decades = []
        for decade in request.POST.getlist('decade'):
            #decades.append(tuple(decade.split(':')))
            decades.append(decade[:-1])
        postdict['decades'] = decades
              
        if (request.POST.get('live') == 'on'):
            postdict['live'] = 1
        else:
            postdict['live'] = 0

        if (request.POST.get('cover') == 'on'):
            postdict['cover'] = 1
        else:
            postdict['cover'] = 0

        if (request.POST.get('withlyrics') == 'on'):
            postdict['withlyrics'] = 1
        else:
            postdict['withlyrics'] = 0
        
        playlist = backendInterface.genratePlaylist(postdict)

        context = {
            'playlist_id': playlist.id,
            'redirect': 'player/',
            'message': 'Generating Your Playlist',
            'timeout': 3
        }

    # update DB
    else:
        context = {
            'message': 'Updating DB...',
            'submessage': 'Taking you back home',
            'timeout': 3
        }

        # run update script
        update_db_path = os.path.join(os.getcwd(), 'create_db', 'import_data.py')
        subprocess.Popen(["python", update_db_path, "-db"])

    return render(request, 'loader.html', context)



"""
AJAX CHANNELS
"""


"""
AJAX that retrieves artists
"""
def artists(request):
    search = request.GET.get('q')
    artists = []

    if search:
        artists = backendInterface.getArtists(search)

    return HttpResponse(
        json.dumps(artists),
        content_type="application/json"
    )


"""
AJAX that retrieves countries
"""
def countries(request):
    search = request.GET.get('q')
    countries = []

    if search:
        countries = backendInterface.getCountries(search)

    return HttpResponse(
        json.dumps(countries),
        content_type="application/json"
    )


"""
AJAX that retrieves genres
"""
def genres(request):
    search = request.GET.get('q')
    genres = []

    if search:
        genres = backendInterface.getGenres(search)

    return HttpResponse(
        json.dumps(genres),
        content_type="application/json"
    )


"""
AJAX for getting playlist by name
"""
def find(request):
    search = request.GET.get('q')
    playlists = []

    if search:
        playlists = backendInterface.getPlaylistsByName(search)

    return HttpResponse(
        json.dumps(playlists),
        content_type="application/json"
    )
    
"""
AJAX for checking if name exists
"""
def checkName(request):
    search = request.GET.get('name')
    exists = False

    if search:
        if backendInterface.getPlaylistsByName(search, False):
            exists = True

    return HttpResponse(
        json.dumps(exists),
        content_type="application/json"
    )