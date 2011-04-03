import xmlrpclib
import os

class Connection:
    __shared_state = {}

    def __init__(self, uri=None, ignore_empty_uri=False):
        self.__dict__ = self.__shared_state 

        if uri is not None:
            self.set_uri(uri)

    def set_uri(self, uri):
        if self.__shared_state.has_key('rpc'):
            rpc = self.__shared_state.pop('rpc')
            del(rpc)

        self.__shared_state['_uri'] = uri
        rpc = xmlrpclib.Server(uri)
        self.__shared_state['rpc'] = rpc
        self.__dict__ = self.__shared_state

