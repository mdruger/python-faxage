import os, os.path, httplib, urllib

HOST = "www.faxage.com"

def handle_error(resp):
    if resp.startswith('ERR'):
        raise Exception(resp)

class APIClient(object):
    def __init__(self, url, company, username, password):
        self.company = company
        self.username = username
        self.password = password

    def send_post(operation, arguments={}):
        url = OPERATION_URLS.get(operation)
        parameters = {
            #API call and authentication:
            'username':             self.username,
            'company':              self.company,
            'password':             self.password,
            'operation':            operation,
        }
        parameters.update(arguments)

        payload_length = 0
        payload = []
        for key, value in parameters.items():
            item = '%s=%s' % (key, urllib.quote(value))
            payload.append(item)
            payload_length += len(item)
        # account for & between items.
        payload_length += len(payload) - 1

        conn = httplib.HTTPSConnection(HOST)
        conn.putrequest("POST", url)

        conn.connect()
        conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
        conn.putheader('Content-Length', payload_length)
        conn.endheaders()
        conn.send('&'.join(payload))
        resp = conn.getresponse()
        return resp.read()
