import socket
import unittest
import threading
from utils.connection import Client, Server, Message


class Connection(unittest.TestCase):
    """def test_server_client_receive(self):

        server = Server()
        client_1 = Client()
        client_2 = Client()




        self.assertEqual(True, False)"""

    def test_message_eq_1(self):
        testing_string = 'abcdef'

        message = Message()
        message.message_str = testing_string
        self.assertEqual(message == testing_string, True)

    def test_message_eq_2(self):
        testing_string = 'abcdef'

        message = Message()
        message.message_str = testing_string + 'g'
        self.assertEqual(message == testing_string, False)

    def test_message_eq_3(self):
        message = Message(None)

        self.assertEqual(message == None, True)

    def test_message_ne_1(self):
        testing_string = 'abcdef'

        message = Message()
        message.message_str = testing_string + 'g'
        self.assertEqual(message != testing_string, True)

    def test_message_ne_2(self):
        testing_string = 'abcdef'

        message = Message()
        message.message_str = testing_string
        self.assertEqual(message != testing_string, False)

    def test_message_ne_3(self):
        testing_string = 'abcdef'

        message = Message(bytes(testing_string, 'utf-8'))

        self.assertEqual(message != None, True)


if __name__ == '__main__':
    unittest.main()
