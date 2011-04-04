#!/usr/bin/env python

import xmlrpclib
from connection_manager import Connection

c = Connection('http://192.168.0.1/RPC2')

def filter_bytes(count, unit):
    factor = 1
    if unit == "KiB":
        factor = 1024.0
    elif unit == "MiB":
        factor = 1024.0 * 1024
    elif unit == "GiB":
        factor = 1024.0 * 1024 * 1024
    elif unit == "KB":
        factor = 1000.0
    elif unit == "MB":
        factor = 1000000.0
    elif unit == "GB":
        factor = 1000000000.0

    return format(count / factor, '.2f')

class RTorrentRpcObject(object):
    server = c.rpc
    _attrs = {}

    def __init__(self):
        self._cache = {}

    def __getattr__(self, name):
        unit = None
        if len(name) > 4 and name[-1] == 'B':
            if name[-3:] in ('_GB', '_MB', '_KB'):
                unit = name[-2:]
                name = name[:-3]
            elif name[-4:] in ('_GiB', '_MiB', '_KiB'):
                unit = name[-3:]
                name = name[:-4]
        
        if self._attrs.has_key(name):
            rpc_attr = self._attrs[name]
            if self._cache.has_key(rpc_attr):
                value = self._cache[rpc_attr]
            else:
                value = self.rpc_call(rpc_attr)
                self.set_cache(rpc_attr, value)

            if unit is not None:
                return filter_bytes(value, unit)
            else:
                return value
        else:
            return self.__dict__[name]

    def set_cache(self, attr_value, value):
        self._cache[attr_value] = value

    def pop_cache(self, attr_name):
        if self._cache.has_key(self._attrs[attr_name]):
            self._cache.pop(self._attrs[attr_name])

class RTorrentRpcContainer(list):
    server = c.rpc

    def __init__(self, member_type, *args):
        self.member_type = member_type

        list.__init__(self, *args)

    def get(self, *names):
        rpcs = [self.member_type._attrs[name] for name in names]
        values_list = self.rpc_multicall(rpcs)

        for i, values in enumerate(values_list):
            for rpc, value in zip(rpcs, values):
                try:
                    self[i].set_cache(rpc, value)
                except IndexError:
                    self.append(self.member_type(*self.get_args(i)))
                    self[i].set_cache(rpc, value)

class File(RTorrentRpcObject):
    _attrs = {
        'path': 'f.get_path',
        'size': 'f.get_size_bytes',
        'completed_chunks': 'f.get_completed_chunks', 
        }

    def rpc_call(self, method):
        return self.server.__getattr__(method)(self.torrent.key, self.index)
    
    def __init__(self, torrent, index):
        self.torrent = torrent
        self.index = index
        RTorrentRpcObject.__init__(self)

    def get_completed(self, units="KiB"):
        value = int(self.completed_chunks) * float(self.torrent.chunk_size)
        if value > self.size:
            value = self.size
        return filter_bytes(value, units)

class FileList(RTorrentRpcContainer):

    def __init__(self, torrent, *args):
        self.torrent = torrent
        RTorrentRpcContainer.__init__(self, File, *args)

    def rpc_multicall(self, rpcs):
        rpc_args = [r + "=" for r in rpcs]
        return self.server.f.multicall(self.torrent.key, 'default', *rpc_args)

    def get_args(self, index):
        return (self.torrent, index)

class Torrent(RTorrentRpcObject):
    server=c.rpc
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
    
    def __init__(self, key):
        self.key = key
        #self.update()
        self.files = FileList(self)
        RTorrentRpcObject.__init__(self)

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
    server=c.rpc
    _attrs = {
        'up_rate': 'get_upload_rate',
        'down_rate': 'get_download_rate',
        }

    def rpc_call(self, method):
        return self.server.__getattr__(method)()

    def __init__(self):
        RTorrentRpcObject.__init__(self)
        self.torrents = {}
        self.update()

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
            self.torrents[h] = Torrent(h)
        
        for t in self.torrents.itervalues():
            t.update()

