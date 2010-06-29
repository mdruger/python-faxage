import time, base64
from datetime import timedelta, datetime
from faxage import APIClient, handle_error

FAX_URL = '/httpsfax.php'

def make_delta(str):
    h, m, s = str.split(':')
    return timedelta(hours=h, minutes=m, seconds=s)

def make_time(str):
    return datetime(*time.strptime(str, "%Y-%m-%d %H:%M:%S")[0:5])

class SendJobStatus(object):
    def __init__(self, jobid, commid, destname, destnum, shortstatus, longstatus, sendtime, completetime, xmittime, pagecount):
        self.jobid = jobid
        self.commid = commid
        self.destname = destname
        self.destnum = destnum
        self.shortstatus = shortstatus
        self.longstatus = longstatus
        self.sendtime = sendtime
        self.completetime = completetime
        self.xmittime = xmittime
        self.pagecount = pagecount

class RecvJobStatus(object):
    def __init__(self, jobid, recvdate, starttime, CID, DNIS, filename):
        self.jobid = jobid
        self.recvdate = recvdate
        self.starttime = starttime
        self.CID = CID
        self.DNIS = DNIS
        self.filename = filename

class FaxClient(APIClient):
    def __init__(self, company, username, password):
        super(FaxClient, self).__init__(FAX_URL, company, username, password)

    def send_fax(self, recip_fax, recip_name='', sender_name='', sender_phone='', file_name=None, file_obj=None):
        if file_name:
            file_obj = file(file_name, 'r')
        if not file_obj:
            raise Exception('Please provide file_name or file_obj!')
        def chunk_fax_data():
            fax_chunk = file_obj.read(8*1024)
            return base64.b64encode(fax_chunk)
        document_name = os.path.basename(document)
        resp = self.send_post('sendfax', {
            'faxfilenames[]':           document_name,
            'faxfiledata[]':            chunk_fax_data,
            'faxno':                    recip_fax,
            'recipname':                recip_name,
            'tagname':                  sender_name,
            'tagnumber':                sender_phone,
        })
        data = handle_error(resp)
        data += resp.read()
        ignore, jobid = data.split(':')
        return int(jobid.strip())

    def send_status(self, *jobids):
        results = []
        jobid_list = ','.join(jobids)
        resp = self.send_post('status', {
            'jobids[]':                 jobid_list,
            'pagecount':                '1',
        })
        data = handle_error(resp, ok_status=('ERR06',))
        if data.startswith('ERR06'):
            return results
        data += resp.read()
        for line in data.splitlines():
            # jobid, commid, destname, destnum, shortstatus, longstatus, sendtime, completetime, xmittime, pagecount
            record = line.split('\t')
            results.append(
                SendJobStatus(
                    int(record[0]),
                    int(record[1]),
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    make_time(record[6]),
                    make_time(record[7]),
                    make_delta(record[8]),
                    int(record[9]),
                )
            )
        return results

    def send_delete(self, *jobids):
        for jobid in jobids:
            resp = self.send_post('clear', {
                'jobid':                jobid
            })
            handle_error(resp)

    def recv_status(self):
        results = []
        resp = self.send_post('listfax', {
            'filename':                 '1',
            'starttime':                '1',
        })
        data = handle_error(resp, ok_status=('ERR11', ))
        if data.startswith('ERR11'):
            return results
        data += resp.read()
        for line in data.splitlines():
            # recvid, recvdate, starttime, CID, DNIS, filename
            record = line.split('\t')
            results.append(
                RecvJobStatus(
                    int(record[0]),
                    make_date(record[1]),
                    make_date(record[2]),
                    record[2],
                    record[3],
                    record[4],
                )
            )
        return results

    def recv_fax(self, jobid, file_obj=None, file_name=None):
        if file_name:
            file_obj = open('file_name', 'w')
        if not file_obj:
            raise Exception('Please provide file_name or file_obj!')
        resp = self.send_post('getfax', {
            'faxid':                    jobid,
        })
        data = handle_error(resp)
        cont_disp = resp.getheader('content-disposition', False)
        while True:
            file_obj.write(data)
            data = resp.read(8*1024)
            if not data:
                break;

    def recv_delete(self, *jobids):
        for jobid in jobids:
            resp = self.send_post('delfax', {
                'faxid':                jobid,
            })
            handle_error(resp)

    def recv_cancel(self, *jobids):
        for jobid in jobids:
            resp = self.send_post('stopfax', {
                'faxid':                jobid,
            })
            handle_error(resp)

    def line_disable(self, *dids):
        for did in dids:
            resp = self.send_post('disabledid', {
                'didnumber':            did,
            })
            handle_error(resp)

    def line_enable(self, *dids):
        for did in dids:
            resp = self.send_post('enabledid', {
                'didnumber':            did,
            })
            handle_error(resp)
