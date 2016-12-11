import json
import time
import requests
import sys
import socket
import hashlib

""" 
Transmit all test execution events to a given target server. 
"""
class emitter:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, suiteId, targetHost, persist):
        self.hostname = socket.gethostname().split('.')[0]
        self.url = targetHost + "/tf/v1/events/" + self.hostname
        self.persist = persist
        self.keywordLevel = 0
        self.suiteId = suiteId
        self.runId = ""
        self.groupIds = []
        self.testId = ""

    def calculate_id(self, path):
        hash_object = hashlib.md5(path)
        return hash_object.hexdigest()

    def removeFirstElement(self, name):
        return name[name.index('.')+1:]

    def toUTCFormat(self, date):
        millis = date[-4:]
        utcNoMillis = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.mktime(time.strptime(date[:-4], "%Y%m%d %H:%M:%S"))))
        return utcNoMillis + millis + "Z"

    def post(self, url, msg):
        headers = {'content-type': 'application/json'}

        if self.suiteId != "":
            msg['suiteId'] = self.suiteId
        if self.runId != "":
            msg['runId'] = self.runId
        if len(self.groupIds) > 0:
            msg['groupId'] = self.removeFirstElement(self.groupIds[-1])
        if self.testId != "":
            msg['testId'] = self.testId

        data = json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': ')) 
        print("\n## Sending to %s : \n %s " % (url, data))
        result = requests.post(url, data, headers=headers)
        if result.status_code <> 200 :
            print("Error during upload: %s" % result.text)
            # TODO fail here...
        return result


    """
    This method is called at the start of every RF suite.
    For persistent test runs, we use the first start suite to allocate a new run id.
    For transient tests executions, we ignore suites.
    """
    def start_suite(self, name, attrs):
        if len(attrs['id'].split("-")) == 1:
            # top level suite
            if self.persist:
                msg = {}
                msg['startTime'] = self.toUTCFormat(attrs['starttime'])
                msg['tests'] = attrs['totaltests']
                result = self.post(self.url + "/startRun", msg)
                print("Received %s" % result)
                self.runId = str(result.json()['id'])
                print("Starting run #%s." % self.runId)
        else:
            self.groupIds.append(attrs['longname'])

    """
    This method is called at the completion of every RF suite.
    For persistent test runs, use the completion of the last suite to signal that
    the run has completed.
    For transient tests executions, we ignore suites.
    """
    def end_suite(self, name, attrs):
        if len(attrs['id'].split("-")) == 1:
            # only mark the run as completed when the top level suite is completed.
            if self.persist:
                msg = {}
                msg['endTime'] = self.toUTCFormat(attrs['endtime'])
                self.post(self.url + "/stopRun", msg)
                print("Stopping run #%s." % self.runId)
        else:
            self.groupIds.pop()


    def start_test(self, name, attrs):
        self.testId = self.calculate_id(attrs['longname'])
        msg = {}
        msg['startTime'] = self.toUTCFormat(attrs['starttime'])
        longname = attrs['longname']
        msg['name'] = longname[len(self.groupIds[-1])+1:]
        msg['tags'] = attrs['tags']
        msg['wip'] = (attrs['critical'] <> "yes")
        msg['doc'] = attrs['doc']
        msg['template'] = attrs['template']
        self.post(self.url + "/startTest", msg)

    def end_test(self, name, attrs):
        msg = {}
        msg['endTime'] = self.toUTCFormat(attrs['endtime'])
        msg['status'] = attrs['status']
        self.post(self.url + "/stopTest", msg)
        self.testId = ""

    def start_keyword(self, name, attrs):
        msg = {}
        msg['startTime'] = self.toUTCFormat(attrs['starttime'])
        msg['level'] = self.keywordLevel
        msg['name'] = attrs['kwname']
        msg['library'] = attrs['libname']
        msg['type'] = attrs['type']
        msg['doc'] = attrs['doc']
        msg['arguments'] = attrs['args']
        self.post(self.url + "/startKeyword", msg)
        self.keywordLevel = self.keywordLevel + 1


    def end_keyword(self, name, attrs):
        self.keywordLevel = self.keywordLevel - 1
        msg = {}
        msg['name'] = attrs['kwname']
        msg['level'] = self.keywordLevel
        msg['endTime'] = self.toUTCFormat(attrs['endtime'])
        msg['status'] = attrs['status']
        msg['type'] = attrs['type']
        self.post(self.url + "/stopKeyword", msg)


    def log_message(self, attrs):
        msg = {}
        msg['message'] = attrs['message']
        msg['level'] = attrs['level']
        msg['timestamp'] = self.toUTCFormat(attrs['timestamp'])
        msg['html'] = attrs['html']
        self.post(self.url + "/logMessage", msg)


