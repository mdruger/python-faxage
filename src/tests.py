import unittest, cgi, time
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from faxage import fax, provision

LOCAL_SERVER_ADDR = 'localhost'
LOCAL_SERVER_PORT = 8008
FAX_NO = '555-555-5555'

class TestHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            print 'parsing form...'
            form = cgi.FieldStorage(
                fp          = self.rfile,
                headers     = self.headers,
                environ     = {
                    'REQUEST_METHOD':       'POST',
                    'CONTENT_TYPE':         self.headers['Content-Type'],
                }
            )
            operation = form.getvalue('operation')
            handler = getattr(self, 'handle_' + operation, None)
            if handler and callable(handler):
                handler(form)
        except Exception, e:
            print 'error:', str(e)
            self.send_error(500, str(e))

    def handle_sendfax(self, form):
        print 'hander called...'
        self.send_response(200)
        self.end_headers()
        for key in form.keys():
            value = form.getvalue(key)
            self.wfile.write('%s=%s\n' % (name, value))

class TestHTTPServer(HTTPServer, Thread):
    def __init__(self, address):
        Thread.__init__(self)
        HTTPServer.__init__(self, address, TestHTTPHandler)
        self.start()

    def run(self):
        self.serve_forever()

class TestFaxClient(unittest.TestCase):
    def setUp(self):
        self.client = fax.FaxClient('company', 'username', 'password', use_ssl=False, host=LOCAL_SERVER_ADDR, port=LOCAL_SERVER_PORT)

    def testSendFax(self):
        self.client.send_fax(FAX_NO, 'test.pdf')

    def testSendFaxWithFileObj(self):
        with file('test.pdf', 'r') as faxfile:
            self.client.send_fax(FAX_NO, 'fax1.pdf', file_obj=faxfile)

if __name__ == '__main__':
    print 'starting webserver...'
    server = TestHTTPServer((LOCAL_SERVER_ADDR, LOCAL_SERVER_PORT))
    try:
        unittest.main()
    except SystemExit:
        pass
    print 'stopping webserver...'
    time.sleep(1) # not sure why this is needed, but it is...
    server.shutdown()
