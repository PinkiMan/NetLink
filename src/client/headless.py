__author__ = "Pinkas Matěj"
__maintainer__ = "Pinkas Matěj"
__email__ = "pinkas.matej@gmail.com"
__created__ = "10/04/2026"
__date__ = "10/04/2026"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""
__credits__ = []

"""
Project: NetLink
Filename: headless.py
Directory: src/client/
"""

import sys
import asyncio

from src.shared.networking import Networking
from src.shared.classes import Message, Address

class Client(Networking):
    def __init__(self, address: Address, username):
        self.is_connection_closed = False
        self.username = username
        self.messages = []

        super().__init__(address)

    async def connect_to_server(self):
        await self.connect()

        # Auth request
        msg = Message(msg_type="aut_request", sender=self.username)
        await self.send_message(msg)
        msg = await self.receive_message()

        if msg.msg_type == "auth_response":
            if msg.text == "accepted":
                print("Connection established.")
            elif msg.msg_type == "refused":
                print("Connection rejected.")
                await self.close()

    async def listen(self):
        while not self.is_connection_closed:
            msg = await self.receive_message()
            if msg is None:
                continue

            """if msg.msg_type == "broadcast":
                print(msg)"""

            print(msg)

    async def send(self):
        loop = asyncio.get_running_loop()
        while True:
            msg_input = await loop.run_in_executor(None, sys.stdin.readline)    # type: ignore[arg-type]
            if not msg_input:
                break

            msg_input = msg_input.strip()

            #/dm <target user> <message>
            #/grp <target group> <message>
            #exit

            if msg_input.startswith("/msg "):
                parts = msg_input.split(" ", 2)
                if len(parts) == 3:
                    target, text = parts[1], parts[2]
                    msg = Message(msg_type="private", sender=self.username, target=target, text=text)
                    await self.send_message(message=msg)
                    self.messages.append(msg)

            elif msg_input.startswith("/dm"):
                command, target, data = msg_input.split(" ", 2)
                msg = Message(msg_type="direct_message", sender=self.username, target=target, content=data, content_type="text")
                await self.send_message(message=msg)
                self.messages.append(msg)

            elif msg_input == 'exit':
                msg = Message(msg_type="disconnect", sender=self.username)
                await self.send_message(message=msg)
                self.messages.append(msg)
                break

            else:
                msg = Message(msg_type="broadcast", sender=self.username, text=msg_input)
                await self.send_message(message=msg)


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
    pass
