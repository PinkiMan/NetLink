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
Directory: client/
"""

import asyncio

from shared.networking import Networking
from shared.classes import Message

class Client(Networking):
    def __init__(self):
        self.is_connection_closed = False
        self.username = "xd"
        self.messages = []

        super().__init__()

    async def connect_to_server(self):
        await self.connect()

        # Auth request

    async def listen(self):
        while not self.is_connection_closed:
            msg = await self.receive_message()
            print(msg)

    async def send(self):
        loop = asyncio.get_running_loop()
        while True:
            msg_input = await loop.run_in_executor(None, sys.stdin.readline)    # type: ignore[arg-type]
            if not msg_input:
                break
            msg_input = msg_input.strip()

            if msg_input.startswith("/msg "):
                parts = msg_input.split(" ", 2)
                if len(parts) == 3:
                    target, text = parts[1], parts[2]
                    msg = Message(msg_type="private", sender=self.username, target=target, text=text)
                    await self.send_message(message=msg, writer=self.writer)
                    self.messages.append(msg)
            elif msg_input == 'exit':
                exit(0)


    async def run(self):
        """ main runner of client """
        await self.connect_to_server()  # connects to server

        listen_task = asyncio.create_task(self.listen())  # starts thread of listening messages
        send_task = asyncio.create_task(self.send())  # starts thread of sending messages

        done, pending = await asyncio.wait([listen_task, send_task],
                                           return_when=asyncio.FIRST_COMPLETED)

        for task in pending:  # cancels all pending tasks
            task.cancel()

        self.writer.close()  # ends sending
        await self.writer.wait_closed()  # ends all


if __name__ == '__main__':
    clt = Client()
    clt.run()
