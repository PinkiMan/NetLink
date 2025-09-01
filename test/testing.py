import unittest
from utils.connection import Client, Server, Message


class Connection(unittest.TestCase):
    """def test_server_client_receive(self):

        server = Server()
        client_1 = Client()
        client_2 = Client()




        self.assertEqual(True, False)"""

    def test_message_eq_1(self):
        server = Server()
        server.start()

        client_1 = Client(username='username_1')
        client_2 = Client(username='username_2')

        testing_string = 'abcdef'

        new_msg.set_from_str(new_string)
        new_msg.receiver = receiver
        client.send_message(new_msg)

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
