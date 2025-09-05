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
import asyncio

from classes import Address, Message, Colors
from config import MAX_RETRIES, USERS_SPLITTER
from networking import BaseConnection

class Client(BaseConnection):
    def __init__(self, username: str, server_address: Address):
        self.username = username
        self.server_address = server_address
        self.server_side = False

        self.pause_event = asyncio.Event()
        self.pause_event.set()  # startujeme nepozastaveně

        self.connected = False
        self.reader = None
        self.writer = None


    async def connect(self):
        for _ in range(MAX_RETRIES):
            try:
                self.reader, self.writer = await asyncio.open_connection(
                    self.server_address.ip,
                    self.server_address.port
                )
                break
            except ConnectionRefusedError:
                await asyncio.sleep(1)
        else:
            raise ConnectionRefusedError("Max retries exceeded")

        self.connected = True
        super().__init__(self.reader, self.writer, server_side=False)

        # pošlu username serveru
        init_message = Message()
        init_message.set_from_str(self.username)
        init_message.receiver = 'SERVER'
        await self.send_message(init_message)

        print(f"[DEBUG] Connected to server as {self.username}")

        # spustíme příjem zpráv
        asyncio.create_task(self.async_receive())

    async def async_receive(self):
        while self.connected:
            await self.pause_event.wait()  # čeká, dokud není pauza
            message = await self.receive_message()
            if message:
                print(f"[RECV] {message.sender}: {message.message_str}")

    async def get_users(self):
        self.pause_event.clear()  # pauza přijímání

        message = Message()
        message.message_str = "CLIENTS"
        message.receiver = "SERVER"
        await self.send_message(message)

        response = await self.receive_message()
        if response:
            for client_username in response.message_str.split(USERS_SPLITTER):
                print(client_username)

        self.pause_event.set()  # obnovíme příjem

    async def send_text(self, receiver: str, text: str):
        message = Message()
        message.message_str = text
        message.receiver = receiver
        await self.send_message(message)



async def main():
    username = input("Username: ")
    server_address = Address('127.0.0.1', 5001)
    client = Client(username, server_address)
    await client.connect()

    while True:
        await client.get_users()
        end_user = input("End user: ")
        if end_user.lower() == "exit":
            break

        while True:
            text = input("Zadej zprávu (close pro konec): ")
            if text.lower() == "close":
                break
            await client.send_text(end_user, text)

if __name__ == '__main__':
    asyncio.run(main())
