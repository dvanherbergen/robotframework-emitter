import json
import time
from websocket import create_connection

""" 
Transmit all test execution events to a given target server. 
"""
class RFEmitter:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, targetUrl, identifier):
        print('\n## Opening WS connection to %s' % targetUrl)
        self.ws = create_connection(targetUrl)


    def start_suite(self, name, attrs):
        self.send('start_suite', attrs, name)


    def start_test(self, name, attrs):
        self.send('start_test', attrs, name)


    def start_keyword(self, name, attrs):
        self.send('start_keyword', attrs, name)


    def log_message(self, message):
        #self.send('log_message', message)
        return

    def end_keyword(self, name, attrs):
        self.send('end_keyword', attrs, name)


    def end_test(self, name, attrs):
        self.send('end_test', attrs, name)


    def end_suite(self, name, attrs):
        self.send('end_suite', attrs, name)


    def close(self):
        print('\n## Closing WS connection.')
        # leave a little time for the server to finish reading the data.
        time.sleep(0.3)
        self.ws.close()


    def toUTCFormat(self, date):
        print("Converting %s" % date)
        millis = date[-4:]
        utcNoMillis = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.mktime(time.strptime(date[:-4], "%Y%m%d %H:%M:%S"))))
        return utcNoMillis + millis + "Z"

    def send(self, msgType, dict, name = None):
        dict['msgType'] = msgType
        
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
        print("\n## Sending : \n %s" % data)
        self.ws.send(data)