import xmlrpclib

def connect():
    return xmlrpclib.Server('http://192.168.0.1/RPC2')

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
    print "got file %s" % file_object


