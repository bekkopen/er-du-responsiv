#!/usr/bin/env python

from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
import urllib
import sys

PORT = 40808
URL_PREFIX = "http://www.aftenposten.no"

CSS_MOCK = None

class ApProxy(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/css"):
            self.path = "/%s" % CSS_MOCK
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
        else:
            url = URL_PREFIX + self.path
            f = urllib.urlopen(url)
            if f:
                self.copyfile(f, self.wfile)
                f.close()

    def log_request(self, code='-', size='-'):
        self.log_message('"%s" %s %s',
                         "GET %s" % self.path, str(code), str(size))


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s myfile.css" % sys.argv[0]
        sys.exit(1)

    CSS_MOCK = sys.argv[1]

    try:
        httpd = ThreadedTCPServer(("", PORT), ApProxy)
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
        httpd.shutdown()
