__author__ = "Pinkas Matěj - Pinki"
__maintainer__ = "Pinkas Matěj - Pinki"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "09/06/2025"
__date__ = "09/06/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

import socket
import threading
import time
import logging
import sys

"""
Project: NetLink
Filename: connection.py
Directory: utils/
"""

logger = logging.getLogger(__name__)

ENCODING = 'utf-8'
HEADER_SIZE = 1024
DISCONNECT = '!DISCONNECT!'


class Address:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"


class User:
    def __init__(self, ip, port, username):
        self.address = Address(ip, port)
        self.username = username


class Message:
    def __init__(self, ):
        self.message_bytes = None
        self.message_str = None
        self.sender = None
        self.receiver = None

    def set_from_bytes(self, message_bytes):
        self.message_bytes = message_bytes
        self.message_str = self.message_bytes.decode(ENCODING)

    def set_from_str(self, message_str):
        self.message_str = message_str
        self.message_bytes = self.message_str.encode(ENCODING)

    def __str__(self):
        return self.message_str

    def __eq__(self, other):
        if other is None:
            if self.message_bytes is None:
                return True
            else:
                return False
        elif type(other) is str:
            if self.message_str == other:
                return True
            else:
                return False
        else:
            raise NotImplementedError(f"Message.__eq__ is not implemented for type={type(other)} data={other}")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __int__(self):
        return int(self.message_str)

    def to_bytes(self):
        return f"{self.message_str}|||{self.sender}|||{self.receiver}".encode(ENCODING)

    def from_bytes(self, bytes_data):
        sting_data = bytes_data.decode(ENCODING)
        self.message_str, self.sender, self.receiver = sting_data.split('|||')


class Client:
    def __init__(self, existing_socket=None, existing_address=None, messages=None, users=None):
        self.server_address = Address('127.0.0.1', 5001)

        if existing_socket is not None:
            self.socket = existing_socket
        else:
            self.__connect_to_server()

        self.connected = None

        self.existing_address = existing_address

        if messages is None:
            self.messages = []
        else:
            self.messages = messages

        if users is None:
            self.users = []
        else:
            self.users = users

    def __connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_address.ip, self.server_address.port))
        self.connected = True

        # TODO: send username

    def __receive_bytes(self, size: int = None) -> bytes:
        if size is None:
            size = HEADER_SIZE
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        message_bytes = self.socket.recv(size)

        if message_bytes is None:
            self.connected = False
            logger.debug(f"Client.__receive(): message_bytes is None")
            self.close()

        return message_bytes

    def __receive_message(self, size=None) -> Message:
        message_bytes = self.__receive_bytes(size=size)

        message = Message()
        message.from_bytes(message_bytes)

        logger.info(f"Client.__receive(): message={message}")

        return message

    def receive(self) -> Message:
        length = self.__receive_message()  # receive (int) len of incoming message

        if length == None:
            raise ValueError(f"message is None, length should be number")

        length_int = int(length)
        message = self.__receive_message(length_int)

        return message


    def __send_bytes(self, message: bytes):
        pass

    def send_str(self, message_str):
        message = str(message_str).encode(ENCODING)
        msg_length = len(message)
        send_length = str(msg_length).encode(ENCODING)
        send_length += b' ' * (HEADER_SIZE - len(send_length))

        self.socket.send(send_length)
        self.socket.send(message)
        print(f"[DEBUG] send_str(): {message}")

    def receive_message(self) -> Message:
        size_bytes = self.__receive_bytes()

        if size_bytes == None:
            raise ValueError(f"message is None, length should be number")

        size_str = size_bytes.decode(ENCODING)

        if size_str == '':
            raise ValueError(f"message is '', length should be number")

        size_int = int(size_str)

        message_bytes = self.__receive_bytes(size_int)

        new_msg = Message()
        new_msg.from_bytes(message_bytes)

        logger.info(f"Client.__receive(): message={new_msg.message_str}")

        return new_msg


    def send_message(self, message: Message):
        bytes_message = message.to_bytes()
        msg_length = len(bytes_message)
        send_length = str(msg_length).encode(ENCODING)
        send_length += b' ' * (HEADER_SIZE - len(send_length))

        self.socket.send(send_length)
        self.socket.send(bytes_message)
        print(f"[DEBUG] send_message(): {message}")

    def server_main(self):
        # TODO: receive username
        while True:
            message = self.receive_message()
            if message is not None:
                print(f"{message.sender}->{message.receiver}:{message.message_str}")
                #self.messages.append(())
            else:
                self.close()

            """for it in self.messages:
                if it[0] == self.existing_address:
                    self.send_str(it[1])"""

    def close(self):
        self.socket.close()

        exit()


class Server:
    def __init__(self):
        self.socket = None
        self.address = None
        self.connections_limit = None

        self.address = Address('127.0.0.1', 5001)
        self.connections_limit = 10

        self.socket = None

        self.clients = []
        self.messages = []

        self.users = []

        self.__init_socket()

    def __init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address.ip, self.address.port))

    def start(self):
        self.socket.listen(self.connections_limit)
        print('[LISTENING] Server is listening on', self.address)
        while True:
            self.__accept_client()

    def __accept_client(self):
        client_socket, client_address = self.socket.accept()
        print(f"[INFO] Client connected: {client_address}")

        new_client = Client(client_socket, client_address, self.messages)
        self.clients.append(new_client)

        thread = threading.Thread(target=new_client.server_main)
        thread.start()








if __name__ == '__main__':
    style = sys.argv[1]

    if style == 'server':
        print("server")

        serv = Server()
        serv.start()
    elif style == 'client':
        print("client")

        client = Client()

        while True:
            new_msg = Message()
            new_msg.sender=sys.argv[2]
            new_msg.set_from_str(input('>'))
            client.send_message(new_msg)



    """server = Server()
    server.start()"""

    """if input("server: [y/n]") == 'y':
        print("server")

        serv = Server()
        serv.start()
    else:
        print("client")

        client = Client()

        while True:
            client.send_str(input('>'))
            #client.send_str('cauky')
            #time.sleep(1)"""

