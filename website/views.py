from django.shortcuts import render
from engine import backendInterface
from engine.objects import Playlist

"""
Homepage
"""
def home(request):

    context = {
        'trending':     backendInterface.getTrending(),
        'newest':       backendInterface.getNewest(),
        'countries':    backendInterface.getCountries(),
        'artists':      backendInterface.getArtists(),
        'genres':       backendInterface.getGenres()
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
            'action': action
        }

    return render(request, 'player.html', context)


"""
Generator
"""
def generator(request):
    if request.method == 'POST':
        generatedPlaylistID = backendInterface.genratePlaylist(
            genres=request.POST.get('genre'),
            countries=request.POST.get('country'),
            decades=request.POST.get('decade'),
            artists=request.POST.get('artist'),
            freetext=request.POST.get('text')
        )
        print request.POST

    context = {
        'playlist_id': generatedPlaylistID
    }

    return render(request, 'loader.html', context)
