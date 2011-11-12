#!/usr/bin/env python
#
# Usage: http://localhost:40808/?swap_css=<local.css>
#

import SocketServer
import urllib

from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse
from cgi import parse_qs

PORT = 40808
URL_PREFIX = "http://www.aftenposten.no"

CSS_SWAP = []

class ApProxy(SimpleHTTPRequestHandler):

    def filter_path(self):
        for prefix in ("/resources", "/external", "/js"):
            if self.path.startswith(prefix):
                return True
        return False

    def do_GET(self):
        if self.filter_path():
            self.send_response(404, "File not found")
            self.send_header("Content-Type", self.error_content_type)
            self.send_header('Connection', 'close')
            self.end_headers()
            return

        query = parse_qs(urlparse(self.path).query)
        if "swap_css" in query:
            CSS_SWAP.append(query["swap_css"][0])

        if self.path.startswith("/css") and len(CSS_SWAP):
            self.path = "/%s" % CSS_SWAP.pop()
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
    try:
        httpd = ThreadedTCPServer(("", PORT), ApProxy)
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
        httpd.shutdown()
