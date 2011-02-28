from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf

from django.utils import simplejson

from models import Torrent
from forms import AddTorrentForm
import utils

def index(request):
    response_dict = {}
    xhr = request.GET.has_key('xhr')
    torrent = request.GET.has_key('torrent')
    torrent_list = Torrent.all()
    if xhr:
        response_dict.update({'count': len(torrent_list), 'success': True})
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    if torrent:
        for torrent in torrent_list:
            torrent_dict = {'name': torrent.name, 
                            'size': str(torrent.sizeMiB),
                            'completed': str(torrent.completedMiB),
                            'up_rate': str(torrent.up_rateKiB),
                            'down_rate': str(torrent.down_rateKiB)}
            response_dict.update({torrent.hash: torrent_dict})
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    else:
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
