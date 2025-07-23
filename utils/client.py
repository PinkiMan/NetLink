__author__ = "Pinkas Matěj - pinka"
__maintainer__ = "Pinkas Matěj - pinka"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "20/07/2025"
__date__ = "20/07/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

"""
Project: NetLink
Filename: client.py
Directory: utils/
"""

import socket
import threading
import time
import logging
import sys

from utils.classes import Address, Message, Colors
from utils.config import MAX_RETRIES, HEADER_SIZE, ENCODING

class Client:
    def __init__(self, existing_socket=None, existing_address=None, messages:list=None, users=None, username=None):
        self.server_address = Address('127.0.0.1', 5001)
        self.server_side = False

        if username is not None:
            self.username = username
        else:
            self.username = 'NONE'

        if existing_socket is not None:
            self.socket = existing_socket
            self.server_side = True
        else:
            self.__connect_to_server()

        self.connected = None

        self.existing_address = existing_address

        if messages is None:
            self.messages : list = []
        else:
            self.messages : list = messages

        if users is None:
            self.users = []
        else:
            self.users = users


    def __async_receive(self):
        while True:
            message = self.receive_message()
            print(f"{message}")

    def __connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for index in range(MAX_RETRIES):    # TODO: Rework retry connect
            try:
                self.socket.connect((self.server_address.ip, self.server_address.port))
                break
            except Exception as error:
                print(f"ERROR: {error}")
                if error is not ConnectionRefusedError:
                    print(error)
                elif error is ConnectionRefusedError and index+1 == MAX_RETRIES:
                    raise ConnectionRefusedError(f"ERROR: '{error}'")


        self.connected = True

        init_message = Message()
        init_message.set_from_str(self.username)
        self.send_message(init_message)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} __connect_to_server: Connected to server")

        thread = threading.Thread(target=self.__async_receive)
        thread.start()

    def __receive_bytes(self, size: int = None) -> bytes:
        """ receives bytes from other side """
        if size is None:
            size = HEADER_SIZE
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        message_bytes = self.socket.recv(size)

        if message_bytes is None:
            self.connected = False
            self.close()

        return message_bytes

    def __send_bytes(self, message: bytes):
        pass

    def receive_message(self) -> Message | None:
        """ receives Message object from other side """
        size_bytes = self.__receive_bytes()

        if size_bytes == None:
            return None
            #raise ValueError(f"message is None, length should be number")
        size_str = size_bytes.decode(ENCODING)

        if size_str == '':
            return None
            #raise ValueError(f"message is '', length should be number")

        size_int = int(size_str)
        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Size received: {str(size_int)}")

        message_bytes = self.__receive_bytes(size_int)

        new_msg = Message()
        new_msg.from_bytes(message_bytes)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Bytes received: {new_msg.sender}->{new_msg.receiver}:{new_msg.message_str}")

        return new_msg

    def send_message(self, message: Message) -> None:
        if message.sender is not None and self.server_side is False:
            raise AttributeError(f"Sender is already set ({message.sender})")

        if not self.server_side:
            message.sender = self.username

        bytes_message = message.to_bytes()
        msg_length = len(bytes_message)
        send_length = str(msg_length).encode(ENCODING)
        send_length += b' ' * (HEADER_SIZE - len(send_length))

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} send_message(): {msg_length}")

        self.socket.send(send_length)
        self.socket.send(bytes_message)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} send_message(): {message}")

    def __send_forward(self):
        while True:
            for message in self.messages:
                if message.receiver == self.username:
                    self.send_message(message)
                    print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Sending to user {message}")
                    self.messages.remove(message)

    def server_main(self):
        # TODO: receive username
        thread = threading.Thread(target=self.__send_forward)
        thread.start()

        while True:
            message = self.receive_message()
            if message is not None:
                print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} server_main: {message}")
                #self.messages.append(())

                self.messages.append(message)
            else:
                self.close()

            """for it in self.messages:
                if it[0] == self.existing_address:
                    self.send_str(it[1])"""

    def close(self):
        self.socket.close()

        print(f"Client disconnected:{self.server_address.port}")

        exit()

if __name__ == '__main__':
    pass
