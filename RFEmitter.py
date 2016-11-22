import json
import time
import requests
import sys

""" 
Transmit all test execution events to a given target server. 
"""
class RFEmitter:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, targetHost, suiteId):
        result = requests.get(targetHost + "/tf/v1/suites/" + suiteId + "/nextId")
        if result.status_code == 200:
            self.url = targetHost + "/tf/v1/suites/" + suiteId + "/runs/" + result.text
        else :
            print("Upload service unavailable: %s" % result.text)
            sys.exit()

    def start_suite(self, name, attrs):
        self.send('start_suite', attrs, name)


    def start_test(self, name, attrs):
        self.send('start_test', attrs, name)


    def start_keyword(self, name, attrs):
        self.send('start_keyword', attrs, name)


    def log_message(self, message):
        self.send('log_message', message)

    def end_keyword(self, name, attrs):
        self.send('end_keyword', attrs, name)


    def end_test(self, name, attrs):
        self.send('end_test', attrs, name)


    def end_suite(self, name, attrs):
        self.send('end_suite', attrs, name)


    def toUTCFormat(self, date):
        millis = date[-4:]
        utcNoMillis = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.mktime(time.strptime(date[:-4], "%Y%m%d %H:%M:%S"))))
        return utcNoMillis + millis + "Z"

    def removeEntry(self, dict, name):
        if name in dict:
            del dict[name]

    def send(self, msgType, dict, name = None):
        dict['msgType'] = msgType
        
        # remove unused attributes
        self.removeEntry(dict, 'metadata')
        self.removeEntry(dict, 'source')
        self.removeEntry(dict, 'suites')
        self.removeEntry(dict, 'longname')
        self.removeEntry(dict, 'elapsedtime')       
        self.removeEntry(dict, 'statistics')  
        self.removeEntry(dict, 'tags')   
        self.removeEntry(dict, 'assign')

        # always include name
        if name is not None:
            dict['name'] = name
        
        # update timestamps to UTC format
        if 'starttime' in dict :
            dict['starttime'] = self.toUTCFormat(dict['starttime'])
        if 'endtime' in dict :
            dict['endtime'] = self.toUTCFormat(dict['endtime'])
        if 'timestamp' in dict :
            dict['timestamp'] = self.toUTCFormat(dict['timestamp'])

        # send the full dict
        data = json.dumps(dict, sort_keys=True, indent=4, separators=(',', ': ')) 
        print("\n## Sending to %s : \n %s " % (self.url, data))
        result = requests.post(self.url, data)
        if result.status_code <> 200 :
            print("Error during upload: %s" % result.text)
