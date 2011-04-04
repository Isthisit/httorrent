#!/usr/bin/env python

import os.path

import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import simplejson

from rtorrentpy import models, connection_manager

rt = models.RTorrent()

class HTTorrent(object):
    
    @cherrypy.expose
    def index(self, **kwargs):
        if kwargs.has_key('torrent'):
            response_dict = {}
            rt.update()
            response_dict.update({'upload_rate': rt.up_rate_KiB,
                                  'download_rate': rt.down_rate_KiB,
                                  'torrents': {}})
            for torrent in rt.torrents.itervalues():
                torrent_dict = {'hash': torrent.hash,
                                'name': torrent.name, 
                                'size': torrent.size_MiB,
                                'completed': torrent.completed_MiB,
                                'up_rate': torrent.up_rate_KiB,
                                'down_rate': torrent.down_rate_KiB,}
                response_dict['torrents'].update({torrent.hash: torrent_dict})
            return simplejson.dumps(response_dict)
        else:
            return Template(filename="index.html").render()

    @cherrypy.expose
    def upload(self, torrent_file):
        print torrent_file.filename

    @cherrypy.expose
    def details(self, torrent_hash):
        if not rt.torrents.has_key(torrent_hash):
            return "Oops!"
        else:
            torrent = rt.torrents[torrent_hash]
            files = torrent.all_files()
            return Template(filename="torrent_detail.html").render(torrent=torrent, files=files)


cherrypy.tree.mount(HTTorrent(), "/httorrent", config="site.conf")

