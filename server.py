#!/usr/bin/env python
# -*- coding: ascii -*-

import os.path

import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import simplejson

from rtorrentpy import models

rt = models.RTorrent('http://192.168.0.1/RPC2')
torrent_folder = "/mnt/high_speed/public/New/"
title = "Doorstop Torrents"

class HTTorrent(object):
    
    @cherrypy.expose
    def index(self, **kwargs):
        if kwargs.has_key('torrent'):
            response_dict = {}
            rt.update()
            response_dict.update({'upload_rate': rt.get_upload_rate(),
                                  'download_rate': rt.get_download_rate(),
                                  'torrents': {}})
            for torrent in rt.torrents.itervalues():
                torrent_dict = {'hash': torrent.hash,
                                'name': torrent.name, 
                                'size': torrent.size_MiB,
                                'completed': torrent.completed_MiB, 
                                'percent': torrent.percent,
                                'up_rate': torrent.up_rate_KiB,
                                'down_rate': torrent.down_rate_KiB,}
                response_dict['torrents'].update({torrent.hash: torrent_dict})
            return simplejson.dumps(response_dict)
        else:
            return Template(filename="index.html").render(title=title)

    @cherrypy.expose
    def upload(self, torrent_file):
        dest = file(torrent_folder + torrent_file.filename, "w")
        dest.write(torrent_file.file.read(100000))
        dest.close()
        torrent_file.file.close()
        raise cherrypy.HTTPRedirect("/httorrent")

    @cherrypy.expose
    def details(self, torrent_hash):
        if not rt.torrents.has_key(torrent_hash):
            return "Oops!"
        else:
            torrent = rt.torrents[torrent_hash]
            files = torrent.all_files()
            return Template(filename="torrent_detail.html").render(torrent=torrent, files=files)


cherrypy.tree.mount(HTTorrent(), "/httorrent", config="site.conf")

