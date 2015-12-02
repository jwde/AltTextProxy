import sys
import os
import posixpath
from SocketServer import ThreadingMixIn
import threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
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
import jsinject

injector = None

def Error(msg):
    print "Error: ", msg
    sys.exit(1)

# takes in an image tag <img ... > and injects a script to add alt text if it is missing
def ImgAlt(img_tag, baseurl):
    global injector
    src_attr_search = re.search(r"src\s*=\s*(['\"])(.*?)\1", img_tag)
    alt_attr_search = re.search(r"alt\s*=\s*(['\"]).+\1", img_tag)
    if not src_attr_search or alt_attr_search:
        return img_tag
    src = src_attr_search.group(2)
    new_img_tag = img_tag
    new_img_tag = re.sub(r"alt\s*=\s*(['\"]).*?\1", "", new_img_tag)
    class_attr_search = re.search(r"class\s*=\s*(['\"])(.*?)\1", img_tag)
    c, payload = injector.AltTextPayload(urljoin(baseurl, src))
    if class_attr_search:
        c += " " +  class_attr_search.group(2)
        re.sub(r"class\s*=\s*(['\"])(.*?)\1", "class='" + c + "'", new_img_tag)
    new_img_tag = new_img_tag[:-1] + " class = '" + c + "'>"
    new_img_tag += payload
    return new_img_tag

def SetFontSize(tag, percent):
    old_style_search = re.search(r"\s+style\s*=\s*(['\"])(.*?)\1", tag)
    old_style = ""
    if old_style_search:
        old_style += old_style_search.group(2)
    new_style = old_style + ("; font-size:" if not old_style == "" else "font-size:") + str(percent) + "%;"
    new_tag = re.sub(r"\s+style\s*=\s*(['\"])(.*?)\1", " ", tag)
    new_tag = new_tag[:-1] + " style='" + new_style + "'>"
    return new_tag

def EnlargeAnchorText(string):
    return re.sub(r"(<a\s+.*?>)", lambda a: SetFontSize(a.group(1), 200), string)

def AddAlt(string, baseurl):
    return re.sub(r"(<img.*?>)", lambda img: ImgAlt(img.group(1), baseurl), string)

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Proxy(BaseHTTPRequestHandler):
    def copyfile(self, source, outputfile, baseurl):
        source_string = source.read()
        with_alt = AddAlt(source_string, baseurl)
        enlarged_links = EnlargeAnchorText(with_alt)
        self.wfile.write(enlarged_links)

    def copyHTTPHeader(self, header, outputfile):
        outputfile.write("HTTP/1.1 " + str(header.status) + " " + str(header.reason) + "\n")
        for attr in header:
            if attr is not "status" and attr is not "reason":
                outputfile.write(str(attr) + ": " + str(header[attr]) + "\n")

    def do_GET(self):
        global injector
        class S:
            def __init__(self, **e):
                self.__dict__.update(e)
        iurl = injector.GetURL("")
        if iurl in self.path:
            uuid = re.sub(iurl, "", self.path)
            ret= "HTTP/1.1 200 OK\nAccess-Control-Allow-Origin: *\n\n" + injector.Retrieve(uuid)
            resp = S(read = lambda: ret)
        else:
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
    global injector
    if len(args) is not 2:
        Error("Usage: python %s <port #>" % args[0])
    try:
        port = int(args[1])
    except ValueError:
        Error("Port must be an integer")
    injector = jsinject.Injector()
    httpd = ThreadedHTTPServer(('localhost', port), Proxy)
    #httpd = HTTPServer(('localhost', port), Proxy)
    print "serving at port", port
    httpd.serve_forever()

if __name__ == "__main__":
    main(sys.argv)
