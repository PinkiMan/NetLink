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

from classes import Address, Message, Colors
from config import MAX_RETRIES, USERS_SPLITTER
from networking import BaseConnection

class Client(BaseConnection):
    def __init__(self, username, server_address):
        self.username = username
        self.server_address = server_address
        self.server_side = False

        self.pause = False

        self.__connect_to_server()

        super().__init__(self.socket, self.server_side)

    def __async_receive(self):
        while True:
            if not self.pause:
                message = self.receive_message()
                print(f"{message}")

    def __connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.settimeout(1.0)

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
        init_message.receiver = 'SERVER'
        self.send_message(init_message)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} __connect_to_server: Connected to server")

        self.thread = threading.Thread(target=self.__async_receive)
        self.thread.start()

    def get_users(self):
        self.pause = True

        message = Message()
        message.message_str = "CLIENTS"
        message.receiver = 'SERVER'
        self.send_message(message)

        message = self.receive_message()
        for client_username in message.message_str.split(USERS_SPLITTER):
            print(client_username)

        self.pause = False

if __name__ == '__main__':
    username = input("Username: ")
    server_address = Address('127.0.0.1', 5001)
    client = Client(username, server_address)

    while True:
        client.get_users()
        end_user = input("End user: ")

        if end_user == "exit":
            break
        else:
            while True:
                message = input("zadej zprávu: ")
                if message == 'close':
                    break
                else:
                    mess = Message()
                    mess.message_str = message
                    client.send_message(mess)
