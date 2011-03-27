import xmlrpclib
import settings
import os

def connect():
    return xmlrpclib.Server(settings.rtorrent_rpc)

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

def handle_uploaded_file(file_object):
    destination = open(os.path.join(settings.torrent_dir, file_object.name), 'wb+')
    for chunk in file_object.chunks():
        destination.write(chunk)
    destination.close()

def _get_rpc_methods():
    s = connect()
    return s.system.listMethods()

