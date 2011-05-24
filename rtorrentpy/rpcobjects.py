#!/usr/bin/env python
# -*- coding: ascii -*-

from util import filter_bytes

class RTorrentRpcObject(object):
    _attrs = {}

    def __init__(self, server):
        self.server = server
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
        return self._cache.pop(self._attrs[attr_name], None)

class RTorrentRpcContainer(list):

    def __init__(self, member_type, server, *args):
        self.member_type = member_type
        self.server = server

        list.__init__(self, *args)

    def get(self, *names):
        rpcs = [self.member_type._attrs[name] for name in names]
        values_list = self.rpc_multicall(rpcs)

        for i, values in enumerate(values_list):
            for rpc, value in zip(rpcs, values):
                try:
                    self[i].set_cache(rpc, value)
                except IndexError:
                    self.append(self.member_type(*self.get_args(i), server=self.server))
                    self[i].set_cache(rpc, value)

