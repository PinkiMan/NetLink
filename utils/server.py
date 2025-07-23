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
Filename: server.py
Directory: utils/
"""

import socket
import threading
import time
import logging
import sys

from classes import Address, Colors
from client import Client

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
        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} __init_socket(): socket initialized")

        #thread = threading.Thread(target=self.__printing)
        #thread.start()

    def __printing(self):
        last_message = ''
        while True:
            data = str(self)
            if last_message != data:
                print(data)
                last_message = data
            #time.sleep(1)


    def start(self):
        self.socket.listen(self.connections_limit)
        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Server is listening on", self.address)
        while True:
            self.__accept_client()

    def __accept_client(self):
        client_socket, client_address = self.socket.accept()
        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Client connected: {client_address}")

        new_client = Client(client_socket, client_address, self.messages)
        self.clients.append(new_client)

        init_message = new_client.receive_message()
        new_client.username = init_message.message_str

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Client connected has username: {new_client.username}")

        thread = threading.Thread(target=new_client.server_main)
        thread.start()

    def __str__(self):
        string_data = ''

        string_data += f"{Colors.Fg.green}ONLINE{Colors.reset}\n=============================\n"
        for client in self.clients:
            string_data += f"{client.username}"

        return string_data

if __name__ == '__main__':
    serv = Server()
    serv.start()
