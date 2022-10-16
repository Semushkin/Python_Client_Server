
import unittest
from client import validation, create_message
from common.variables import PRESENCE, ANSWER, RESPONSE, ERROR, TEXT, ACTION


class TestClient(unittest.TestCase):

    def test_validation_success(self):
        data = validation({RESPONSE: 200, ANSWER: 'test'})
        self.assertEqual(data, '200: test')

    def test_validation_failed(self):
        data = validation({RESPONSE: 77, ERROR: 'Bad Request'})
        self.assertEqual(data, '400: Bad Request')

    def test_create_massages(self):
        text = create_message('test')
        self.assertEqual(text, {ACTION: PRESENCE, TEXT: 'test'})
