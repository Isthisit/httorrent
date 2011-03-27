from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf

from django.utils import simplejson

from rtorrentpy.models import Torrent, RTorrent
from forms import AddTorrentForm
import utils

def index(request):
    if request.method == 'POST':
        form = AddTorrentForm(request.POST, request.FILES)
        if form.is_valid():
            utils.handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('.')
        else:
            return HttpResponseRedirect('.')
    else:
        torrent = request.GET.has_key('torrent')
        if torrent:
            response_dict = {}
            rtorrent = RTorrent()
            torrent_list = Torrent.all()
            response_dict.update({'upload_rate': format(rtorrent.up_rateKiB, ".2f"),
                                  'download_rate': format(rtorrent.down_rateKiB, ".2f"),
                                  'torrents': {}})
            for torrent in torrent_list:
                torrent_dict = {'hash': torrent.hash,
                                'name': torrent.name, 
                                'size': format(torrent.sizeMiB, ".2f"),
                                'completed': format(torrent.completedMiB, ".2f"),
                                'up_rate': format(torrent.up_rateKiB, ".2f"),
                                'down_rate': format(torrent.down_rateKiB, ".2f")}
                response_dict['torrents'].update({torrent.hash: torrent_dict})
            return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
        else:
            form = AddTorrentForm()
            return render_to_response('httorrent/index.html', {'form': form})

@csrf_protect
def add_torrent(request):
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        form = AddTorrentForm(request.POST, request.FILES)
        if form.is_valid():
            utils.handle_uploaded_file(request.FILES['file'])
            return None
            #return HttpResponseRedirect('../')
    else:
        form = AddTorrentForm()

    c.update({'form': form})
    return render_to_response('httorrent/add_torrent.html', c)

def torrent_detail(request, torrent_hash):
    torrent = Torrent(torrent_hash)
    files = torrent.all_files()
    return render_to_response('httorrent/torrent_detail.html', {'torrent': torrent, 'files': files})

def ajax_example(request):
    if not request.POST:
        return render_to_response('httorrent/ajax_example.html', {})
    xhr = request.GET.has_key('xhr')
    response_dict = {}
    name = request.POST.get('name', False)
    total = request.POST.get('total', False)
    response_dict.update({'name': name, 'total': total})
    if total:
        try:
            total = int(total)
        except:
            total = False
    if name and total and int(total) == 10:
        response_dict.update({'success': True})
    else:
        response_dict.update({'errors': {}})
        if not name:
            response_dict['errors'].update({'name': 'This field is required'})
        if not total and total is not False:
            response_dict['errors'].update({'total': 'This field is required'})
        elif int(total) != 10:
            response_dict['errors'].update({'total': 'Incorrect total'})
    if xhr:
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

    return render_to_response('httorrent/ajax_example.html', response_dict)
