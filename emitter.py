import json
import time
import requests
import sys
import socket
import hashlib

""" 
Transmit all test execution events to a given target server. 
"""
class Emitter:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, suiteId, targetHost, keep):
        self.url = targetHost + "/tf/v1/suites/" + suiteId + "/runs"
        self.hostname = socket.gethostname().split('.')[0]
        self.persist = keep
        self.runId = '0'
        self.keywordLevel = 0

    def calculate_id(self, path):
        hash_object = hashlib.md5(path)
        return hash_object.hexdigest()

    def post(self, url, msg):
        headers = {'content-type': 'application/json'}
        data = json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': ')) 
        print("\n## Sending to %s : \n %s " % (url, data))
        result = requests.post(url, data, headers=headers)
        if result.status_code <> 200 :
            print("Error during upload: %s" % result.text)
            # TODO fail here...
        return result

    def put(self, url, msg):
        headers = {'content-type': 'application/json'}
        data = json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': ')) 
        print("\n## Sending to %s : \n %s " % (url, data))
        result = requests.put(url, data, headers=headers)
        if result.status_code <> 200 :
            print("Error during upload: %s" % result.text)
            # TODO fail here...

    """
    This method is called at the start of every RF suite.
    For persistent test runs, we use the first start suite to allocate a new run id.
    For transient tests executions, we ignore suites.
    """
    def start_suite(self, name, attrs):
        if self.persist:
            if self.runId == '0':
                msg = {}
                msg['startTime'] = self.toUTCFormat(attrs['starttime'])
                msg['tests'] = attrs['totaltests']
                result = self.post(self.url, msg)
                self.runId = result.json()['id']
                print("Starting run #%s." % self.runId)

    """
    This method is called at the completion of every RF suite.
    For persistent test runs, use the completion of the last suite to signal that
    the run has completed.
    For transient tests executions, we ignore suites.
    """
    def end_suite(self, name, attrs):
        if self.persist:
            # only mark the run as completed when the top level suite is completed.
            if len(attrs['id'].split("-")) == 1:
                msg = {}
                msg['endTime'] = self.toUTCFormat(attrs['endtime'])
                self.put(self.url + "/" + self.runId, msg)


    def start_test(self, name, attrs):

        self.testId = calculate_id(attrs['source'])
        msg = {}
        msg['startTime'] = self.toUTCFormat(attrs['starttime'])
        msg['longname'] = attrs['longname']
        msg['tags'] = attrs['tags']
        msg['wip'] = (attrs['critical'] <> "yes")
        msg['doc'] = attrs['doc']
        msg['template'] = attrs['template']
        self.put(self.url + "/" + self.runId + "/tests/" + self.testId, msg)

    def end_test(self, name, attrs):
        msg = {}
        msg['endTime'] = self.toUTCFormat(attrs['endtime'])
        msg['status'] = attrs['status']
        self.post(self.url + "/" + self.runId + "/tests/" + self.testId, msg)


    def start_keyword(self, name, attrs):
        msg = {}
        msg['startTime'] = self.toUTCFormat(attrs['starttime'])
        msg['level'] = self.keywordLevel
        msg['name'] = attrs['name']
        msg['library'] = attrs['library']
        msg['type'] = attrs['type']
        msg['doc'] = attrs['doc']
        msg['arguments'] = attrs['arguments']
        self.post(self.url + "/" + self.runId + "/tests/" + self.testId + "/keywords", msg)
        self.keywordLevel = self.keywordLevel + 1


    def end_keyword(self, name, attrs):
        self.keywordLevel = self.keywordLevel - 1
        msg = {}
        msg['name'] = attrs['name']
        msg['level'] = self.keywordLevel
        msg['endTime'] = self.toUTCFormat(attrs['endtime'])
        msg['status'] = attrs['status']
        self.post(self.url + "/" + self.runId + "/tests/" + self.testId + "/keywords", msg)


    def log_message(self, message):
        msg = {}
        msg['message'] = attrs['message']
        msg['level'] = attrs['level']
        msg['timestamp'] = self.toUTCFormat(attrs['level'])
        msg['html'] = attrs['html']
        self.post(self.url + "/" + self.runId + "/tests/" + self.testId + "/logs", msg)


    def toUTCFormat(self, date):
        millis = date[-4:]
        utcNoMillis = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.mktime(time.strptime(date[:-4], "%Y%m%d %H:%M:%S"))))
        return utcNoMillis + millis + "Z"
