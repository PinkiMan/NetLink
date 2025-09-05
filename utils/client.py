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

"""
Project: NetLink
Filename: client.py
Directory: utils/
"""

import asyncio
import sys
from classes import Address

class Client:
    def __init__(self, server_address:Address, ):
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
    server_address = Address("127.0.0.1", 8888)
    client = Client(server_address, )
    asyncio.run(client.run())
