from django.shortcuts import render
from engine import backendInterface
from engine.objects import Playlist, Artist, Genre, Country, FilterObject

"""
Homepage
"""
def home(request):

    top_artist, top_genre, top_decade, top_country = backendInterface.getTopHits()

    context = {
        'trending':     backendInterface.getTrending(),
        'newest':       backendInterface.getNewest(),
        'countries':    backendInterface.getCountries(),
        'artists':      backendInterface.getArtists(),
        'genres':       backendInterface.getGenres(),
        'top_artist':   top_artist,
        'top_genre':    top_genre,
        'top_decade':   top_decade,
        'top_country':  top_country
    }

    return render(request, 'index.html', context)


"""
Player
"""
def player(request, playlist_id, action=None):

    # 'playlist not found'
    playlist404 = Playlist(-1)
    playlist404.name = 'Playlist Not Found'
    playlist404.video_list = []

    p = backendInterface.getPlaylistById(playlist_id)

    if action == 'reshuffle':
        p.reshuffle()
        
    elif action == 'refresh':
        backendInterface.reloadVideos(p)

    # update hit count
    else:
        backendInterface.incrementHitCount(playlist_id)
        p.hits += 1

    # playlist not found
    if p == -1:
        context = {
            'playlist': playlist404
        }

    # valid playlist
    else:
        context = {
            'playlist': p,
            'action': action
        }

    return render(request, 'player.html', context)


"""
Generator
"""
def generator(request):
    if request.method == 'POST':
        
        artists = []
        for artist in request.POST.getlist('artist'):
            artists.append(FilterObject(tuple(artist.split(':'))))
            
        genres = []
        for genre in request.POST.getlist('genre'):
            genres.append(FilterObject(tuple(genre.split(':'))))
            
        countries = []
        for country in request.POST.getlist('country'):
            countries.append(FilterObject(tuple(country.split(':'))))
            
        decades = []
        for decade in request.POST.getlist('decades'):
            decades.append(FilterObject(tuple(decade.split(':'))))
              
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
            name=request.POST.get('name'),
            genres,countries,decades,artists,
            freetext=request.POST.get('text'),
            live,cover,withlyrics
        )

    context = {
        'playlist_id': playlist.id
    }

    return render(request, 'loader.html', context)
