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

    def do_POST(self):
        content_type, params = cgi.parse_header(self.headers.getheader('content-type'))
        if content_type == 'multipart/form-data':
            pvars = cgi.parse_multipart(self.rfile, params)
        elif content_type == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            pvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            pvars = {}
        resp = urllib.urlopen(self.path)
        self.copyfile(resp, self.wfile)



httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
print "serving at port", PORT
httpd.serve_forever()
