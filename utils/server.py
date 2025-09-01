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

import asyncio

"""
Project: NetLink
Filename: server.py
Directory: utils/
"""

import socket
import threading

from classes import Address, Colors, Message
from networking import ClientHandler

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


    async def start(self):
        server = await asyncio.start_server(
            self.handle_client,
            self.address.ip,
            self.address.port,
            limit=self.connections_limit
        )

        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Server is listening on", self.address)
        while True:
            self.__accept_client()

    def __accept_client(self):
        client_socket, client_address = self.socket.accept()
        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Client connected: {client_address}")

        new_client = ClientHandler(client_socket, client_address, self.messages, self.clients)
        self.clients.append(new_client)

        init_message = new_client.receive_message()
        new_client.username = init_message.message_str

        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Client connected has username: {new_client.username}")

        thread = threading.Thread(target=new_client.main)
        thread.start()

    def __str__(self):
        string_data = ''

        string_data += f"{Colors.Fg.green}ONLINE{Colors.reset}\n=============================\n"
        for client in self.clients:
            string_data += f"{client.username}"

        return string_data

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        new_client = BaseConnection(reader, writer, server_side=True)
        self.clients.append(new_client)

        # přijmeme úvodní zprávu s uživatelským jménem
        init_message = await new_client.receive_message()
        if init_message:
            new_client.username = init_message.message_str
            print(f"[INFO] Client connected with username: {new_client.username}")

        try:
            while new_client.connected:
                message = await new_client.receive_message()
                if message is None:
                    break
                print(f"[INFO] Message received from {new_client.username}: {message.message_str}")
                self.messages.append(message)
                await self.broadcast(message, sender=new_client)
        finally:
            await new_client.close()
            self.clients.remove(new_client)
            print(f"[INFO] Client {new_client.username} disconnected")


if __name__ == '__main__':
    serv = Server()
    serv.start()
