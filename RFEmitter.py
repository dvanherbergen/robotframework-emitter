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


    def end_test(self, name, attrs):
        self.send('end_test', attrs, name)


    def end_suite(self, name, attrs):
        self.send('end_suite', attrs, name)


    def message(self, message):
        self.send('log_message', message)


    def log_message(self, message):
        self.send('log_message', message)


    def close(self):
        print('\n## Closing WS connection.')
        # leave a little time for the server to finish reading the data.
        time.sleep(0.3)
        self.ws.close()


    def send(self, msgType, dict, name = None):
        dict['msgType'] = msgType
        if name is not None:
            dict['name'] = name
        data = json.dumps(dict, sort_keys=True, indent=4, separators=(',', ': ')) 
        print("\n## Sending : \n %s" % data)
        self.ws.send(data)