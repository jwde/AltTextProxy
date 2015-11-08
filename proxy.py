import os
import posixpath
import SocketServer
import BaseHTTPServer
import urllib
import urllib2
from urlparse import urljoin
import requests
from httplib import HTTPConnection
import httplib2
import cgi
import shutil
import mimetypes
from StringIO import StringIO
import re

PORT = 9101

def GetAltText(image_path):
    return "image at" + image_path

# takes in an image tag <img ... > and adds alt text if it is missing
def ImgAlt(img_tag, baseurl):
    src_attr_search = re.search(r"src\s*=\s*(['\"])(.*?)\1", img_tag)
    src = src_attr_search.group(2)
    new_img_tag = img_tag
    if not re.search(r"alt\s*=\s*(['\"]).*?\1", img_tag):
        new_img_tag = new_img_tag[:-1] + " alt='" + GetAltText(urljoin(baseurl, src)) + "'>"
    return new_img_tag

def AddAlt(string, baseurl):
#    return re.sub(r"(<img(?!.*?alt=(['\"]).*?\2)[^>]*)(>)", lambda match: match.group(1) + " alt='" + GetAltText("") + "' " + match.group(3), string)
    return re.sub(r"(<img.*?>)", lambda img: ImgAlt(img.group(1), baseurl), string)

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):
    def copyfile(self, source, outputfile, baseurl):
        source_string = source.read()
        with_alt = AddAlt(source_string, baseurl)
        self.wfile.write(with_alt)

    def copyHTTPHeader(self, header, outputfile):
        outputfile.write("HTTP/1.1 " + str(header.status) + " " + str(header.reason) + "\n")
        for attr in header:
            if attr is not "status" and attr is not "reason":
                outputfile.write(str(attr) + ": " + str(header[attr]) + "\n")

#    def copyHTTPBody(self, body, outputfile):

    def do_GET(self):
        resp = urllib.urlopen(self.path)
        self.copyfile(resp, self.wfile, self.path)

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
        self.copyfile(resp, self.wfile, self.path)



httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
print "serving at port", PORT
httpd.serve_forever()
