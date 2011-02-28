#from django.db import models
import utils
import xmlrpclib

class Torrent(object):
    server=None
    
    def __init__(self, key):
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
        result = tuple(multicall())

        self.hash = result[0]
        self.name = result[1]
        self.size = result[15] * result[17]
        self.completed = result[16] * result[17]
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

    def __unicode__(self):
        return self.name

    #def __del__(self):
    #    server.close()


