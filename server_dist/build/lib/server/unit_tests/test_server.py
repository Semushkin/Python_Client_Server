import unittest
from server_dist.server.serverapp import validation
from server_dist.server.common.variables import ACTION, PRESENCE, RESPONSE, ERROR, ANSWER


class TestServer(unittest.TestCase):
    def test_validation_success(self):
        data = validation({ACTION: PRESENCE})
        self.assertEqual(data, {RESPONSE: 200, ANSWER: 'Hello Client'})

    def test_validation_failed(self):
        data = validation('sfds')
        self.assertEqual(data, {RESPONSE: 400, ERROR: 'Bad Request'})
