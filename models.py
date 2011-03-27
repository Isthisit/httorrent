#from django.db import models
import utils
import xmlrpclib

class File(object):
    server=None
    
    def __init__(self, key, index, path, size, completed):
        self.torrent_key = key
        self.index = index
        self.path = path
        self.size = size
        self.completed = completed
        if self.completed > self.size:
            self.completed = self.size

    def update(self, name):
        pass

    sizeMiB = property(fget=lambda self : utils.filter_bytes(self.size, "MiB"))
    completedMiB = property(fget=lambda self : utils.filter_bytes(self.completed, "MiB"))

class Torrent(object):
    server=None
    
    def __init__(self, key):
        if self.server is None:
            self.server = utils.connect()
        self.key = key
        self.update(key)

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

    sizeMiB = property(fget=lambda self : utils.filter_bytes(self.size, "MiB"))
    completedMiB = property(fget=lambda self : utils.filter_bytes(self.completed, "MiB"))
    down_rateKiB = property(fget=lambda self : utils.filter_bytes(self.down_rate, "KiB"))
    up_rateKiB = property(fget=lambda self : utils.filter_bytes(self.up_rate, "KiB"))

    @classmethod
    def all(cls):
        if cls.server is None:
            cls.server = utils.connect()

        return [Torrent(key) for key in cls.server.download_list('')]

    def all_files(self):
        files = enumerate(self.server.f.multicall(self.key, 'default', 'f.get_path=', 'f.get_size_bytes=', 'f.get_completed_chunks='))
        self.files = [File(self.key, f[0], f[1][0], f[1][1], f[1][2] * self.chunk_size) for f in files]
        return self.files

    def __unicode__(self):
        return self.name

    #def __del__(self):
    #    server.close()

class RTorrent(object):
    server=None

    def __init__(self):
        if self.server is None:
            self.server = utils.connect()
        self.update()

    def update(self):
        multicall = xmlrpclib.MultiCall(self.server)
        multicall.get_upload_rate()
        multicall.get_download_rate()
        result = tuple(multicall())

        self.up_rate = result[0]
        self.down_rate = result[1]

    down_rateKiB = property(fget=lambda self : utils.filter_bytes(self.down_rate, "KiB"))
    up_rateKiB = property(fget=lambda self : utils.filter_bytes(self.up_rate, "KiB"))


