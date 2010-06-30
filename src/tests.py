import unittest, cgi, time
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from faxage import fax, provision

LOCAL_SERVER_ADDR = 'localhost'
LOCAL_SERVER_PORT = 8008
FAX_NO = '555-555-5555'
TEST_PDF_FILE = 'test.pdf'
TEST_COMPANY = 'company'
TEST_USERNAME = 'username'
TEST_PASSWORD = 'password'

class TestHTTPHandler(BaseHTTPRequestHandler):
    def log_message(*args):
        pass

    def send_faxage_error(self, errline):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(errline)

    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp          = self.rfile,
                headers     = self.headers,
                environ     = {
                    'REQUEST_METHOD':       'POST',
                    'CONTENT_TYPE':         self.headers['Content-Type'],
                }
            )
            #authenticate user:
            if form.getvalue('company') != TEST_COMPANY or \
               form.getvalue('username') != TEST_USERNAME or \
               form.getvalue('password') != TEST_PASSWORD:
                return self.send_faxage_error('ERR02: Login incorrect')
            #map request to an operation handler
            operation = form.getvalue('operation')
            handler = getattr(self, 'handle_' + operation, None)
            if handler and callable(handler):
                handler(form)
        except Exception, e:
            self.send_error(500, str(e))

    def handle_sendfax(self, form):
        if self.path != '/httpsfax.php':
            return self.send_error(404, 'File Not Found')
        self.send_response(200)
        self.end_headers()
        self.wfile.write('JOBID: 1234')

class TestHTTPServer(HTTPServer, Thread):
    def __init__(self, address):
        Thread.__init__(self)
        HTTPServer.__init__(self, address, TestHTTPHandler)
        self.start()

    def run(self):
        self.serve_forever()

class TestFaxClient(unittest.TestCase):
    def setUp(self):
        self.client = fax.FaxClient(
            TEST_COMPANY,
            TEST_USERNAME,
            TEST_PASSWORD,
            use_ssl     = False,
            host        = LOCAL_SERVER_ADDR,
            port        = LOCAL_SERVER_PORT
        )

    def testInvalidCredentials(self):
        badclient = fax.FaxClient(
            'badcompany',
            'badusername',
            'badpassword',
            use_ssl     = False,
            host        = LOCAL_SERVER_ADDR,
            port        = LOCAL_SERVER_PORT
        )
        try:
            badclient.send_fax(FAX_NO, TEST_PDF_FILE)
        except Exception, e:
            self.assertEqual(str(e), 'ERR02: Login incorrect')
        else:
            self.fail('Invalid credentials did not result in an error.')

    def testSendFax(self):
        self.client.send_fax(FAX_NO, TEST_PDF_FILE)

    def testSendFaxWithFileObj(self):
        with file(TEST_PDF_FILE, 'r') as faxfile:
            self.client.send_fax(FAX_NO, 'fax1.pdf', file_obj=faxfile)

if __name__ == '__main__':
    server = TestHTTPServer((LOCAL_SERVER_ADDR, LOCAL_SERVER_PORT))
    try:
        unittest.main()
    finally:
        time.sleep(1) # not sure why this is needed, but it is...
        server.shutdown()
