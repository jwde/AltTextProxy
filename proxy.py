import sys
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
import mrisa
import json
import string

def Error(msg):
    print "Error: ", msg
    sys.exit(1)

def GetAltText(image_path):
    reverse_image_scrape = json.loads(mrisa.mrisa_main(image_path))
    description = reverse_image_scrape['description'][0]
    description = re.sub("\"", r'&#34;', description)
    description = re.sub("\'", r'&#39;', description)
    description = re.sub("<", r'&lt;', description)
    description = re.sub(">", r'&gt;', description)
    return filter(lambda c: c in string.printable, description)


# takes in an image tag <img ... > and adds alt text if it is missing
def ImgAlt(img_tag, baseurl):
    src_attr_search = re.search(r"src\s*=\s*(['\"])(.*?)\1", img_tag)
    src = src_attr_search.group(2)
    new_img_tag = img_tag
    if not re.search(r"alt\s*=\s*(['\"]).*?\1", img_tag):
        new_img_tag = new_img_tag[:-1] + " alt=\"" + GetAltText(urljoin(baseurl, src)) + "\">"
    return new_img_tag

def AddAlt(string, baseurl):
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

    def do_PUT(self):
        length = int(self.headers.getheader('content-length'))
        content = self.rfile.read(length)
        resp = urllib.urlopen(self.path)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.copyfile(resp, self.wfile)


def main(args):
    if len(args) is not 2:
        Error("Usage: python %s <port #>" % args[0])
    try:
        port = int(args[1])
    except ValueError:
        Error("Port must be an integer")
    httpd = SocketServer.ForkingTCPServer(('', port), Proxy)
    print "serving at port", port
    httpd.serve_forever()

if __name__ == "__main__":
    main(sys.argv)
