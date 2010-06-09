import os, os.path, optparse, httplib, urllib, base64

HOST = "www.faxage.com"

def send_fax(document, username, company, password, recip_fax, recip_name='', sender_name='', sender_phone=''):
    fax_data = file(document, 'r').read()
    fax_data_b64 = base64.b64encode(fax_data)

    document_name = os.path.basename(document)

    parameters = {
        #API call and authentication:
        'host':                 HOST,
        'username':             username,
        'company':              company,
        'password':             password,
        'operation':            'sendfax',
        #fax information:
        'faxfilenames[]':       document_name,
        'faxfiledata[]':        fax_data_b64,
        #recipient information:
        'faxno':                recip_fax,
        'recipname':            recip_name,
        #sender information:
        'tagname':              sender_name,
        'tagnumber':            sender_phone,
    }

    payload_length = 0
    payload = []
    for key, value in parameters.items():
        item = '%s=%s' % (key, urllib.quote(value))
        payload.append(item)
        payload_length += len(item)
    # account for & between items.
    payload_length += len(payload) - 1

    conn = httplib.HTTPSConnection(HOST)
    conn.putrequest("POST", '/httpsfax.php')

    conn.connect()
    conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
    conn.putheader('Content-Length', payload_length)
    conn.endheaders()
    conn.send('&'.join(payload))
    resp = conn.getresponse()

    print 'Response...'
    print resp.read()

if __name__ == '__main__':
    parser = optparse.OptionParser(prog="example", description="Send a fax via FAXAGE using python.")
    parser.add_option("-a", "--document", help="The document to fax.")
    parser.add_option("-u", "--username", help="The FAXAGE API username.")
    parser.add_option("-c", "--company", help="The FAXAGE API company.")
    parser.add_option("-p", "--password", help="The FAXAGE API password.")
    parser.add_option("-r", "--recipient", help="The fax number to send the document to.")
    parser.add_option("-d", "--debug", action="store_true", help="Break into debugger before the interesting bits.")

    (options, args) = parser.parse_args()

    if not options.document:
        parser.error('You must supply a document to fax using the --document argument.')
    if not options.username or not options.company or not options.password:
        parser.error('You must supply a username, company and password using to access the FAXAGE API.')
    if not options.recipient:
        parser.error('You must supply a fax number using the --recipient argument.')

    if options.debug:
        import pdb; pdb.set_trace()

    send_fax(options.document, options.username, options.company, options.password, options.recipient)