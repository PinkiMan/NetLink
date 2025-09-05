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
        self.address = Address('127.0.0.1', 5001)
        self.connections_limit = 10

        self.clients = []
        self.messages = []
        self.users = []


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

        async with server:
            await server.serve_forever()

    def __str__(self):
        string_data = ''

        string_data += f"{Colors.Fg.green}ONLINE{Colors.reset}\n=============================\n"
        for client in self.clients:
            string_data += f"{client.username}"

        return string_data

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        new_client = ClientHandler(reader, writer, self.messages, self.clients)
        self.clients.append(new_client)

        # první zpráva od klienta = username
        init_message = await new_client.receive_message()
        if init_message:
            new_client.username = init_message.message_str
            print(f"{Colors.Fg.green}[INFO]{Colors.reset} Client connected has username: {new_client.username}")

        try:
            await new_client.main()
        finally:
            await new_client.close()
            if new_client in self.clients:
                self.clients.remove(new_client)
            print(f"{Colors.Fg.green}[INFO]{Colors.reset} Client {getattr(new_client, 'username', '?')} disconnected")


if __name__ == '__main__':
    serv = Server()
    asyncio.run(serv.start())
