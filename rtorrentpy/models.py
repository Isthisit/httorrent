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

    return count / factor

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
        'completed': 'f.get_completed_chunks', 
        }

    def rpc_call(self, method):
        return self.server.__getattr__(method)(self.torrent_key, self.index)
    
    def __init__(self, key, index):
        self.torrent_key = key
        self.index = index
        RTorrentRpcObject.__init__(self)

    def update(self, name):
        pass

    sizeMiB = property(fget=lambda self : filter_bytes(self.size, "MiB"))
    completedMiB = property(fget=lambda self : filter_bytes(self.completed, "MiB"))

class FileList(RTorrentRpcContainer):

    def __init__(self, torrent_key, *args):
        self.torrent_key = torrent_key
        RTorrentRpcContainer.__init__(self, File, *args)

    def rpc_multicall(self, rpcs):
        rpc_args = [r + "=" for r in rpcs]
        return self.server.f.multicall(self.torrent_key, 'default', *rpc_args)

    def get_args(self, index):
        return (self.torrent_key, index)

class Torrent(object):
    server=c.rpc
    
    def __init__(self, key):
        self.key = key
        self.update(key)
        self.files = FileList(key)

    def update(self, key):
        multicall = xmlrpclib.MultiCall(self.server)
        multicall.d.get_hash(key)                # 0
        multicall.d.get_name(key)                # 1
        multicall.d.get_message(key)             # 2
        multicall.d.get_directory(key)           # 3
        multicall.d.get_ratio(key)               # 4
        multicall.d.get_peer_exchange(key)       # 5
        multicall.d.get_peers_complete(key)      # 6
        multicall.d.get_peers_connected(key)     # 7
        multicall.d.get_peers_not_connected(key) # 8
        multicall.d.get_priority(key)            # 9
        multicall.d.get_creation_date(key)       # 10
        multicall.d.is_open(key)                 # 11
        multicall.d.is_active(key)               # 12
        multicall.d.get_complete(key)            # 13
        multicall.d.get_up_total(key)            # 14
        multicall.d.get_size_chunks(key)         # 15
        multicall.d.get_completed_chunks(key)    # 16
        multicall.d.get_chunk_size(key)          # 17
        multicall.d.get_down_rate(key)           # 18
        multicall.d.get_up_rate(key)             # 19
        multicall.d.get_completed_bytes(key)     # 20
        result = tuple(multicall())

        self.hash = result[0]
        self.name = result[1]
        self.chunk_size = result[17]
        self.size = result[15] * self.chunk_size
        self.completed = result[20]
        self.down_rate = result[18]
        self.up_rate = result[19]
        self.open = (result[11] == 1)
        self.active = (result[12] == 1)

    sizeMiB = property(fget=lambda self : filter_bytes(self.size, "MiB"))
    completedMiB = property(fget=lambda self : filter_bytes(self.completed, "MiB"))
    down_rateKiB = property(fget=lambda self : filter_bytes(self.down_rate, "KiB"))
    up_rateKiB = property(fget=lambda self : filter_bytes(self.up_rate, "KiB"))

    @classmethod
    def all(cls):
        return [Torrent(key) for key in cls.server.download_list('')]

    def all_files(self):
        self.files.get('path', 'size', 'completed')
        return self.files

    def __unicode__(self):
        return self.name


class RTorrent(object):
    server=c.rpc

    def __init__(self):
        self.update()

    def update(self):
        multicall = xmlrpclib.MultiCall(self.server)
        multicall.get_upload_rate()
        multicall.get_download_rate()
        result = tuple(multicall())

        self.up_rate = result[0]
        self.down_rate = result[1]

    down_rateKiB = property(fget=lambda self : filter_bytes(self.down_rate, "KiB"))
    up_rateKiB = property(fget=lambda self : filter_bytes(self.up_rate, "KiB"))


