__author__ = "Pinkas Matěj - pinka"
__maintainer__ = "Pinkas Matěj - pinka"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "02/09/2025"
__date__ = "02/09/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

import sys

"""
Project: NetLink
Filename: asynchronous.py
Directory: utils/
"""

import asyncio

from classes import Address


class Message:
    def __init__(self):
        pass

class Server:
    def __init__(self, server_address: Address):
        self.server_address = server_address
        self.clients = {}

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"New client from {addr}")

        # první zpráva od klienta = jméno
        writer.write(b"Enter your name:\n")
        await writer.drain()
        name = (await reader.readline()).decode().strip()

        if not name or name in self.clients:
            writer.write(b"Invalid or duplicate name. Connection closed.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        self.clients[name] = writer
        print(f"Client registered: {name}")

        # oznámíme ostatním, že se připojil
        await self.broadcast(f"*** {name} has joined the chat ***", exclude=writer)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = data.decode().strip()

                if message == "/list":
                    # seznam všech uživatelů
                    user_list = ", ".join(self.clients.keys())
                    writer.write(f"Connected users: {user_list}\n".encode())
                    await writer.drain()

                elif message.startswith("@"):
                    # soukromá zpráva
                    try:
                        target, msg = message[1:].split(" ", 1)
                        if target in self.clients:
                            self.clients[target].write(
                                f"[private from {name}]: {msg}\n".encode()
                            )
                            await self.clients[target].drain()
                        else:
                            writer.write(f"User {target} not found.\n".encode())
                            await writer.drain()
                    except ValueError:
                        writer.write(b"Invalid private message format. Use: @username message\n")
                        await writer.drain()
                else:
                    # broadcast
                    await self.broadcast(f"[{name}]: {message}", exclude=writer)

        except asyncio.CancelledError:
            pass
        finally:
            print(f"Client disconnected: {name}")
            del self.clients[name]
            writer.close()
            await writer.wait_closed()
            await self.broadcast(f"*** {name} has left the chat ***")

    async def broadcast(self, message, exclude=None):
        """Pošle zprávu všem klientům (kromě exclude)."""
        for user, client in self.clients.items():
            if client != exclude:
                client.write(f"{message}\n".encode())
                await client.drain()

    async def start(self):
        """Spustí server."""
        self.server = await asyncio.start_server(
            self.handle_client, self.server_address.ip, self.server_address.port
        )
        addr = self.server.sockets[0].getsockname()
        print(f"Server running on {addr}")

        async with self.server:
            await self.server.serve_forever()

class Client:
    def __init__(self, server_address:Address):
        self.server_address = server_address
        self.reader = None
        self.writer = None

    async def connect(self):
        """Připojí klienta k serveru."""
        self.reader, self.writer = await asyncio.open_connection(self.server_address.ip, self.server_address.port)
        print(f"Connected to {self.server_address.ip}:{self.server_address.port}", file=sys.stderr)

    async def listen(self):
        """Čte zprávy ze serveru a posílá je na stdout."""
        while True:
            data = await self.reader.readline()
            if not data:
                print("Server closed connection", file=sys.stderr)
                break
            sys.stdout.write(data.decode())
            sys.stdout.flush()

    async def send(self):
        """Čte zprávy ze stdin a posílá je na server."""
        loop = asyncio.get_running_loop()
        while True:
            msg = await loop.run_in_executor(None, sys.stdin.readline)
            if not msg:
                break
            self.writer.write(msg.encode())
            await self.writer.drain()

    async def run(self):
        """Spustí klienta: poslouchání + posílání."""
        await self.connect()
        listen_task = asyncio.create_task(self.listen())
        send_task = asyncio.create_task(self.send())

        done, pending = await asyncio.wait(
            [listen_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        self.writer.close()
        await self.writer.wait_closed()


if __name__ == '__main__':
    typ = sys.argv[1]

    server_address = Address("127.0.0.1", 8888)

    if typ == 's':
        server = Server(server_address)
        asyncio.run(server.start())
    else:
        client = Client(server_address)
        asyncio.run(client.run())