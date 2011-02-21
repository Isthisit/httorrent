from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from models import Torrent
from forms import AddTorrentForm
import utils

def index(request):
    torrent_list = Torrent.all()
    return render_to_response('httorrent/index.html', {'torrent_list': torrent_list})

@csrf_protect
def add_torrent(request):
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        form = AddTorrentForm(request.POST, request.FILES)
        if form.is_valid():
            utils.handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('../')
    else:
        form = AddTorrentForm()

    c.update({'form': form})
    return render_to_response('httorrent/add_torrent.html', c)
