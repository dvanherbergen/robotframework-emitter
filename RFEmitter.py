import json
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
        self.send('start_suite', name, attrs)


    def start_test(self, name, attrs):
        self.send('start_test', name, attrs)


    def start_keyword(self, name, attrs):
        self.send('start_keyword', name, attrs)


    def end_test(self, name, attrs):
        self.send('end_test', name, attrs)


    def end_suite(self, name, attrs):
        self.send('end_suite', name, attrs)


    def close(self):
        print('\n## Closing WS connection.')
        self.ws.close()


    def send(self, msgType, name, attrs):
        attrs['msgType'] = msgType
        attrs['name'] = name
        data = json.dumps(attrs, sort_keys=True, indent=4, separators=(',', ': ')) 
        print("\n## Sending : \n %s" % data)
        self.ws.send(data)
