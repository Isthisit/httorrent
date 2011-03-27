import xmlrpclib
import os

class Connection(object):
    rpc = None
    _uri = None

    def __init__(self, uri=None, ignore_empty_uri=False):
        if ignore_empty_uri:
            return
        elif uri is None and self._uri is not None:
            return
        else:
            self.uri = uri

    def set_uri(self, uri):
        if Connection.rpc is not None:
            Connection.rpc.close()

        Connection.rpc = xmlrpclib.Server(uri)
        Connection._uri = uri

    uri = property(fset=set_uri, fget=lambda self : self._uri)
        

