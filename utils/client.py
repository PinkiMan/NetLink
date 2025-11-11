__author__ = "Pinkas Matěj - Pinki"
__maintainer__ = "Pinkas Matěj - Pinki"
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
import os
import hashlib
import time

from utils.classes import Address, Message, Networking, User


class Client(Networking):
    def __init__(self, server_address: Address, username: str=None, password: str=None, headless: bool = True):
        super().__init__()
        self.server_address = server_address
        self.username = username
        self.password = password
        self.reader = None
        self.writer = None
        self.messages = []
        self.HEADLESS = headless
        self.start_time = 0
        self.server_ping = -1

        self.target = None

        self.non_chat_messages = []     # broadcast and /msg messages

    async def connect(self):
        """Connect to the server"""
        self.reader, self.writer = await asyncio.open_connection(
            self.server_address.ip, self.server_address.port
        )   # open connection to server

        msg = Message(msg_type='auth_request', sender=self.username, target=None, text=self.username)
        await self.send_message(message=msg, writer=self.writer) # REWORK to User not only username

        if self.HEADLESS:
            print(f"Connected as {self.username}")

    async def receive_message_handle(self):
        pass

    async def listen(self):
        while True:
            msg = await self.receive_message(self.reader)
            if msg is None:
                break

            if msg.msg_type in ['broadcast', 'private']:
                self.messages.append(msg)

            if msg.msg_type == "broadcast":

                if self.HEADLESS:
                    print(f"[{msg.sender}]: {msg.text}")

            elif msg.msg_type == "private":
                if self.HEADLESS:
                    print(f"[PM from {msg.sender}]: {msg.text}")

            elif msg.msg_type == "refused_connection":
                if self.HEADLESS:
                    print(f"[SERVER]: {msg.text}")
                break

            elif msg.msg_type == "file_offer":
                await self.receive_file_offer(msg)

            elif msg.msg_type == "file_data":
                await self.receive_file_data(msg)

            elif msg.msg_type == "pong":
                self.server_ping = int((time.process_time() - self.start_time) * 1000)


    async def receive_file_offer(self, msg: Message):
        answer = input(
            f"Do you want to accept file {msg.filename} ({msg.file_size} bytes) from {msg.sender}? [y/n]: ").strip().lower()
        if answer == "y":
            confirm = Message(msg_type="file_data", sender=self.username, filename=msg.filename)
            self.writer.write(confirm.serialize(self.ENCODING))
            await self.writer.drain()
        else:
            # TODO: implement decline of file
            pass

    async def receive_file_data(self, msg: Message):
        size = msg.file_size
        data_bytes = await self.reader.readexactly(size)
        await self.reader.readline()  # --FILEEND--
        received_hash = hashlib.sha256(data_bytes).hexdigest()
        if received_hash != msg.filehash:
            if self.HEADLESS:
                print(f"File {msg.filename} is damaged!")
        else:
            save_path = f"download_{msg.filename}"
            with open(save_path, "wb") as f:
                f.write(data_bytes)
            if self.HEADLESS:
                print(f"File {msg.filename} is saved {save_path} (hash OK)")

    async def ping(self):
        self.start_time = time.process_time()
        msg = Message(msg_type="ping", sender=self.username)
        await self.send_message(message=msg, writer=self.writer)

    async def send(self):
        loop = asyncio.get_running_loop()
        while True:
            msg_input = await loop.run_in_executor(None, sys.stdin.readline)    # type: ignore[arg-type]
            if not msg_input:
                break
            msg_input = msg_input.strip()

            await self.ping()

            if msg_input.startswith("/sendfileto "):
                _, target, path = msg_input.split(" ", 2)
                if os.path.isfile(path):
                    file_size = os.path.getsize(path)
                    file_msg = Message(msg_type="file_offer", sender=self.username, target=target,
                                       filename=os.path.basename(path), file_size=file_size)

                    await self.send_message(message=file_msg, writer=self.writer)

                    with open(path, "rb") as f:
                        while chunk := f.read(4096):
                            self.writer.write(chunk)
                            await self.writer.drain()
                    self.writer.write(b"ENDFILE\n")
                    await self.writer.drain()
                    if self.HEADLESS:
                        print(f"Send file {path} to user {target}")

            elif msg_input.startswith("/msg "):
                parts = msg_input.split(" ", 2)
                if len(parts) == 3:
                    target, text = parts[1], parts[2]
                    msg = Message(msg_type="private", sender=self.username, target=target, text=text)
                    await self.send_message(message=msg, writer=self.writer)
                    self.messages.append(msg)
            elif msg_input == 'exit':
                exit(0)
            elif msg_input == "ping":
                await self.ping()
            elif msg_input.startswith("/grp"):
                parts = msg_input.split(" ")
                self.target = parts[1]
                self.server_ping = parts[2]
            elif msg_input.startswith("/all"):
                parts = msg_input.split(" ", 2)
                msg = Message(msg_type="broadcast", sender=self.username, text=parts[1])
                await self.send_message(message=msg, writer=self.writer)
                self.messages.append(msg)
            else:
                msg = Message(msg_type="group", sender=self.username, text=msg_input)
                await self.send_message(message=msg, writer=self.writer)

    async def run(self):
        """ main runner of client """
        await self.connect() # connects to server

        listen_task = asyncio.create_task(self.listen())    # starts thread of listening messages
        send_task = asyncio.create_task(self.send())    # starts thread of sending messages

        done, pending = await asyncio.wait([listen_task, send_task],
                                           return_when=asyncio.FIRST_COMPLETED)

        for task in pending:    # cancels all pending tasks
            task.cancel()

        self.writer.close()     # ends sending
        await self.writer.wait_closed()     # ends all

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <name>")
        sys.exit(1)

    name = sys.argv[1]
    client = Client(Address("127.0.0.1", 8888), name)
    asyncio.run(client.run())
