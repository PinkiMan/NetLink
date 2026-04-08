from __future__ import annotations

__author__ = "Pinkas Matěj"
__maintainer__ = "Pinkas Matěj"
__email__ = "pinkas.matej@gmail.com"
__created__ = "01/04/2026"
__date__ = "01/04/2026"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""
__credits__ = []

"""
Project: NetLink
Filename: main.py
Directory: src/server/
"""

import asyncio

from src.shared.networking import Networking
from src.shared.classes import Address, User, Message

SERVER_NAME = "MAIN_SERVER"

class Server(Networking):
    def __init__(self, server_address: Address):
        super().__init__(server_address)
        self.server_address = server_address
        self.clients = {}  # name -> {"reader": reader, "writer": writer}
        self.server = None

        self.AUTH_CLIENTS_ONLY =False

    async def auth_client(self, reader: asyncio.StreamReader) -> str|None:
        if self.AUTH_CLIENTS_ONLY:
            return None     # TODO: add authentication for user
        else:
            msg = await self.receive_message(reader)
            name = msg.sender
            return name

    async def handle_client(self, reader, writer):
        user = await self.auth_client(reader=reader)
        name = user

        # refuse client if it has no name or name already in connected clients
        if not name or name in self.clients:
            message = Message(msg_type='auth_response', text="Invalid or duplicate name. Connection closed.")
            await self.send_message(message, writer)

            await self.close(writer)
            return
        else:
            message = Message(msg_type='auth_response', text="Connection established.")
            await self.send_message(message, writer)
            print("Connection accepted")

        self.clients[name] = {"reader": reader, "writer": writer}
        await self.broadcast(Message(msg_type="broadcast", text=f"*** {name} has joined the chat ***", sender=SERVER_NAME), exclude=name)

        print(f"*** {name} has joined the chat ***")

        try:
            while True:
                msg = await self.receive_message(reader)
                if msg.is_none():
                    break

                if msg.msg_type == "broadcast":     #broadcating messages to all clients
                    await self.broadcast(msg, exclude=msg.sender)

                elif msg.msg_type == "list_users":
                    pass

                elif msg.msg_type == "ping":
                    new_msg = Message(msg_type="pong", sender=SERVER_NAME)
                    await self.send_message(message=new_msg, writer=self.clients[msg.sender]["writer"])

                elif msg.msg_type == "group":
                    pass


        finally:
            if name in self.clients:
                del self.clients[name]
                await self.broadcast(Message(msg_type="broadcast", text=f"*** {name} has left the chat ***", sender=SERVER_NAME))
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, msg, exclude=None):
        """ broadcast a message to all clients """
        for user, client in list(self.clients.items()):
            if user != exclude:
                try:
                    await self.send_message(message=msg, writer=client["writer"])
                except Exception as e:
                    print(f"Error in sending to {user}: {e}")
                    del self.clients[user]

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, host=self.server_address.ip, port=self.server_address.port
        )

        if self.server.sockets[0].getsockname() != (self.server_address.ip, self.server_address.port):
            raise ConnectionError(f"Could not establish connection on address {self.server_address.ip}:{self.server_address.port} instead of {self.server.sockets[0].getsockname()[0]}:{self.server.sockets[0].getsockname()[1]}")

        print(f"Server started on address {self.server_address.ip}:{self.server_address.port}")

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        # broadcast to all clients about server shutdown
        shutdown_msg = Message(msg_type="broadcast", sender=SERVER_NAME, text="*** Server shutting down ***")
        await self.broadcast(shutdown_msg)

        print("Stopping server...")
        self.server.close()
        await self.server.wait_closed()

        # close all client connections
        for name, client in list(self.clients.items()):
            writer = client["writer"]
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Error in closing client {name}: {e}")
        self.clients.clear()
        print("Server stopped cleanly.")

if __name__ == "__main__":
    server = Server(Address("10.144.130.28", 8888))

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down...")
        asyncio.run(server.stop())