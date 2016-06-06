from django.shortcuts import render
from django.http import HttpResponse
from engine import backendInterface
from engine.objects import Playlist
import json


"""
Homepage
"""
def home(request):

    top_artist, top_genre, top_decade, top_country = backendInterface.getTopHits()

    context = {
        'trending':     backendInterface.getTrending(),
        'newest':       backendInterface.getNewest(),
        'top_artist':   top_artist,
        'top_genre':    top_genre,
        'top_decade':   top_decade,
        'top_country':  top_country
    }

    return render(request, 'index.html', context)


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
            p.reshuffle()
            
        elif action == 'refresh':
            backendInterface.reloadVideos(p)
    
        # update hit count
        else:
            backendInterface.incrementHitCount(playlist_id)
            p.hits += 1

        context = {
            'playlist': p,
            'action': action
        }

        print p.video_list

    return render(request, 'player.html', context)


"""
Generator
"""
def generator(request):

    playlist = None

    if request.method == 'POST':

        name = request.POST.get('name')
        freetext = request.POST.get('text')
        
        artists = []
        for artist in request.POST.getlist('artist'):
            artists.append(tuple(artist.split(':')))
            
        genres = []
        for genre in request.POST.getlist('genre'):
            genres.append(tuple(genre.split(':')))
            
        countries = []
        for country in request.POST.getlist('country'):
            countries.append(tuple(country.split(':')))
        
        decades = []
        for decade in request.POST.getlist('decade'):
            decades.append(tuple(decade.split(':')))
              
        if (request.POST.get('live') == 'on'):
            live = 1
        else:
            live = 0
        if (request.POST.get('cover') == 'on'):
            cover = 1
        else:
            cover = 0
        if (request.POST.get('withlyrics') == 'on'):
            withlyrics = 1
        else:
            withlyrics = 0
        
        playlist = backendInterface.genratePlaylist(
            name,genres,countries,artists,decades,freetext,live,cover,withlyrics 
        )

    context = {
        'playlist_id': playlist.id
    }

    return render(request, 'loader.html', context)
