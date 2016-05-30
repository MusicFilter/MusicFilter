from django.shortcuts import render
from engine import backendInterface
from engine.objects import Playlist

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

    # playlist not found
    if p == -1:
        context = {
            'playlist': playlist404
        }

    # valid playlist
    else:
        context = {
            'playlist': p,
            'description' : p.getDescription(),
            'action': action
        }

    return render(request, 'player.html', context)


"""
Generator
"""
def generator(request):
    if request.method == 'POST':
        
        playlist = backendInterface.genratePlaylist(
            name=request.POST.get('name'),
            genres=request.POST.getlist('genre'),
            countries=request.POST.getlist('country'),
            decades=request.POST.getlist('decade'),
            artists=request.POST.getlist('artist'),
            freetext=request.POST.get('text'),
            live=request.POST.get('live'),
            cover=request.POST.get('cover'),
            withlyrics=request.POST.get('withlyrics')
        )
        print request.POST

    context = {
        'playlist_id': playlist.id
    }

    return render(request, 'loader.html', context)
