#!/usr/bin/env python
# -*- coding: ascii -*-

import xmlrpclib
from rpcobjects import RTorrentRpcObject, RTorrentRpcContainer
from util import filter_bytes

class File(RTorrentRpcObject):
    _attrs = {
        'path': 'f.get_path',
        'size': 'f.get_size_bytes',
        'completed_chunks': 'f.get_completed_chunks', 
        }

    def rpc_call(self, method):
        return self.server.__getattr__(method)(self.torrent.key, self.index)
    
    def __init__(self, torrent, index, *args, **kwargs):
        self.torrent = torrent
        self.index = index
        RTorrentRpcObject.__init__(self, *args, **kwargs)

    def get_completed(self, units="KiB"):
        value = int(self.completed_chunks) * float(self.torrent.chunk_size)
        if value > self.size:
            value = self.size
        return filter_bytes(value, units)

class FileList(RTorrentRpcContainer):

    def __init__(self, torrent, *args, **kwargs):
        self.torrent = torrent
        RTorrentRpcContainer.__init__(self, File, *args, **kwargs)

    def rpc_multicall(self, rpcs):
        rpc_args = [r + "=" for r in rpcs]
        return self.server.f.multicall(self.torrent.key, 'default', *rpc_args)

    def get_args(self, index):
        return (self.torrent, index)

class Torrent(RTorrentRpcObject):
    _attrs = {
        'hash': 'd.get_hash',
        'name': 'd.get_name',
        'chunk_size': 'd.get_chunk_size',
        'size_chunks': 'd.get_size_chunks',
        'completed': 'd.get_completed_bytes',
        'down_rate': 'd.get_down_rate',
        'up_rate': 'd.get_up_rate',
        'open': 'd.is_open',
        'active': 'd.is_active',
        }

    def rpc_call(self, method):
        return self.server.__getattr__(method)(self.key)
    
    def __init__(self, key, *args, **kwargs):
        RTorrentRpcObject.__init__(self, *args, **kwargs)
        self.key = key
        #self.update()
        self.files = FileList(self, self.server)

    def update(self):
        self.pop_cache('completed')
        self.pop_cache('open')
        self.pop_cache('active')
        self.pop_cache('down_rate')
        self.pop_cache('up_rate')

    size = property(fget=lambda self : self.size_chunks * self.chunk_size)
    size_MiB = property(fget=lambda self : filter_bytes(self.size, "MiB"))

    def all_files(self):
        self.files.get('path', 'size', 'completed_chunks')
        return self.files

    def __unicode__(self):
        return self.name


class RTorrent(RTorrentRpcObject):
    _attrs = {
        'up_rate': 'get_upload_rate',
        'down_rate': 'get_download_rate',
        }

    def rpc_call(self, method):
        return self.server.__getattr__(method)()

    def __init__(self, server_uri):
        self.server = xmlrpclib.Server(server_uri)
        RTorrentRpcObject.__init__(self, self.server)
        self.torrents = {}
        self.update()

    def get_download_rate(self):
        rate = 0.0
        for t in self.torrents.values():
            rate += float(t.down_rate_KiB)

        return str(rate)

    def get_upload_rate(self):
        rate = 0.0
        for t in self.torrents.values():
            rate += float(t.up_rate_KiB)

        return str(rate)

    def update(self):
        # clean out own cache
        self.pop_cache('up_rate')
        self.pop_cache('down_rate')

        # update member torrents
        hashes = self.server.download_list('')
        current = set(self.torrents.keys())
        new = set(hashes)
        added = new.difference(current)
        removed = current.difference(new)

        for h in removed:
            self.torrents.pop(h)
        for h in added:
            self.torrents[h] = Torrent(h, self.server)
        
        for t in self.torrents.itervalues():
            t.update()

