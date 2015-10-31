import os
import posixpath
import SocketServer
import BaseHTTPServer
import urllib
import urllib2
import requests
from httplib import HTTPConnection
import httplib2
import cgi
import shutil
import mimetypes
from StringIO import StringIO

PORT = 9100

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def copyHTTPHeader(self, header, outputfile):
        outputfile.write("HTTP/1.1 " + str(header.status) + " " + str(header.reason) + "\n")
        for attr in header:
            if attr is not "status" and attr is not "reason":
                outputfile.write(str(attr) + ": " + str(header[attr]) + "\n")

#    def copyHTTPBody(self, body, outputfile):

    def do_GET(self):
        resp = urllib.urlopen(self.path)
        self.copyfile(resp, self.wfile)

    def do_HEAD(self):
        h = httplib2.Http()
        resp = h.request(self.path, "HEAD")
        self.copyHTTPHeader(resp[0], self.wfile)

    """
    implement other http methods
    """



httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
print "serving at port", PORT
httpd.serve_forever()
