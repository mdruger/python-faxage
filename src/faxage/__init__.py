import os, os.path, httplib, urllib

HOST = "www.faxage.com"

def handle_error(resp, ok_status=[]):
    status = resp.read(5)
    for ok in ok_status:
        if status == ok:
            break
    else:
        if status.startswith('ERR'):
            raise Exception(resp)
    return status

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

        conn = httplib.HTTPSConnection(HOST)
        conn.putrequest("POST", url)

        conn.connect()
        conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
        conn.endheaders()
        for i, name, value in enumerate(parameters.items()):
            if i != 0:
                conn.send('&')
            conn.send('%s=' % name)
            if callable(value):
                while True:
                    data = value()
                    if not data:
                        break
                    conn.send(urllib.quote(data))
            else:
                conn.send(urllib.quote(value))
        return conn.getresponse()
