import unittest
import requests
import httpretty
from emitter import Emitter


targetHost = "http://localhost"
suiteId = "test_suite"
apiPath = targetHost + "/tf/v1/suites/" + suiteId + "/runs"

class EmitterTest(unittest.TestCase):

    def setUp(self):
        httpretty.enable()
        self.emitter = Emitter(suiteId, targetHost, True)

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def get_full_dict(self):

        dict = {}
        dict['id'] = 's1'
        dict['longname'] = 'a-very-long-suite-name'
        dict['doc'] = 'this is where the suite documentation goes'
        dict['metadata'] = []
        dict['source'] = 'path_to_file'
        dict['suites'] = []
        dict['tests'] = []
        dict['totaltests'] = 17
        dict['starttime'] = "20161210 00:00:00.000"
        dict['endtime'] = "20161210 02:02:03.004"

        return dict

    def test_start_suite(self):

        httpretty.register_uri(httpretty.POST, apiPath, body='{ "id": 1}')
        
        self.emitter.start_suite("start_suite", self.get_full_dict())

        result = httpretty.last_request().parsed_body
        self.assertEqual(17, result['tests'], 17)
        self.assertEqual("2016-12-09T23:00:00.000Z", result['startTime'])
        self.assertEqual(2, len(result))

    def test_start_suite_is_ignored_if_not_persistent(self):

        self.emitter = Emitter(suiteId, targetHost, False)
        self.emitter.start_suite("start_suite", self.get_full_dict())
        # if a call was made, we would get an connection error here

    def test_end_suite(self):

        runId = "2"
        httpretty.register_uri(httpretty.PUT, apiPath + "/" + runId)
        
        self.emitter.runId = runId
        self.emitter.end_suite("end_suite", self.get_full_dict())

        result = httpretty.last_request().parsed_body
        self.assertEqual("2016-12-10T01:02:03.004Z", result['endTime'])
        self.assertEqual(1, len(result))

    def test_end_suite_is_ignored_if_not_persistent(self):

        self.emitter = Emitter(suiteId, targetHost, False)
        self.emitter.end_suite("end_suite", self.get_full_dict())
        # if a call was made, we would get an connection error here  




if __name__ == '__main__':
    unittest.main()