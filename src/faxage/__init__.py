import os, os.path, httplib, urllib

HOST = "www.faxage.com"
HTTP_PORT = 80
HTTPS_PORT = 443

def handle_error(resp, ok_status=()):
    if resp.status != 200:
        raise Exception(resp.reason)
    status = resp.read(5)
    if status not in ok_status:
        if status.startswith('ERR'):
            status += resp.read()
            raise Exception(status)
    return status

class APIClient(object):
    def __init__(self, company, username, password, use_ssl=True, host=None, port=None):
        self.company = company
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.host = host or HOST
        if port is None and use_ssl:
            self.port = HTTPS_PORT
        elif port is None:
            self.port = HTTP_PORT
        else:
            self.port = port

    def send_post(self, operation, arguments={}):
        parameters = {
            #API call and authentication:
            'username':             self.username,
            'company':              self.company,
            'password':             self.password,
            'operation':            operation,
        }
        parameters.update(arguments)

        payload = []
        for key, value in parameters.items():
            if isinstance(value, (list, tuple)):
                for subvalue in value:
                    item = '%s=%s' % (key, urllib.quote(subvalue))
                    payload.append(item)
            else:
                item = '%s=%s' % (key, urllib.quote(value))
                payload.append(item)
        #get the size of all our payload items.
        payload_length = sum(map(len, payload))
        # account for & between items.
        payload_length += len(payload) - 1

        if self.use_ssl:
            conn = httplib.HTTPSConnection(self.host, self.port)
        else:
            conn = httplib.HTTPConnection(self.host, self.port)
        conn.putrequest("POST", self.URL)

        conn.connect()
        conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
        conn.putheader('Content-Length', payload_length)
        conn.endheaders()
        conn.send('&'.join(payload))
        return conn.getresponse()
