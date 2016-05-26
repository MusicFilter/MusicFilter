from django.shortcuts import render
from engine import backendInterface
from engine.objects import Playlist

"""
Homepage
"""
def home(request):

    if request.method == 'POST':
        print 'POST!'

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
    backendInterface.incrementHitCount(playlist_id)

    if p == -1:
        # playlist not found
        context = {
            'playlist': playlist404
        }

    else:

        context = {
            'playlist': p,
            'action': action
        }

    return render(request, 'player.html', context)
