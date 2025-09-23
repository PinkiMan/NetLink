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

from utils.classes import Address, Message, Networking


class Client(Networking):
    def __init__(self, server_address: Address, username: str=None, password: str=None):
        super().__init__()
        self.server_address = server_address
        self.username = username
        self.password = password
        self.reader = None
        self.writer = None

    async def connect(self):
        """Connect to the server"""
        self.reader, self.writer = await asyncio.open_connection(
            self.server_address.ip, self.server_address.port
        )   # open connection to server

        msg = Message(msg_type='auth_request', sender=self.username, target=None, text=self.username)
        await self.send_message(message=msg, writer=self.writer) # REWORK to User not only username

        print(f"Connected as {self.username}")

    async def listen(self):
        while True:
            msg = await self.receive_message(self.reader)
            if msg is None:
                break

            if msg.msg_type == "broadcast":
                print(f"[{msg.sender}]: {msg.text}")

            elif msg.msg_type == "private":
                print(f"[PM from {msg.sender}]: {msg.text}")

            elif msg.msg_type == "refused_connection":
                print(f"[SERVER]: {msg.text}")
                break

            elif msg.msg_type == "file_offer":
                await self.receive_file_offer(msg)

            elif msg.msg_type == "file_data":
                await self.receive_file_data(msg)

    async def receive_file_offer(self, msg: Message):
        answer = input(
            f"Do you want to accept file {msg.filename} ({msg.filesize} bytes) from {msg.sender}? [y/n]: ").strip().lower()
        if answer == "y":
            confirm = Message(msg_type="file_data", sender=self.username, filename=msg.filename)
            self.writer.write(confirm.serialize(self.ENCODING))
            await self.writer.drain()
        else:
            # TODO: implement decline of file
            pass

    async def receive_file_data(self, msg: Message):
        size = msg.filesize
        data_bytes = await self.reader.readexactly(size)
        await self.reader.readline()  # --FILEEND--
        received_hash = hashlib.sha256(data_bytes).hexdigest()
        if received_hash != msg.filehash:
            print(f"File {msg.filename} is damaged!")
        else:
            save_path = f"download_{msg.filename}"
            with open(save_path, "wb") as f:
                f.write(data_bytes)
            print(f"File {msg.filename} is saved {save_path} (hash OK)")

    async def send(self):
        loop = asyncio.get_running_loop()
        while True:
            msg_input = await loop.run_in_executor(None, sys.stdin.readline)
            if not msg_input:
                break
            msg_input = msg_input.strip()

            if msg_input.startswith("/sendfileto "):
                _, target, path = msg_input.split(" ", 2)
                if os.path.isfile(path):
                    filesize = os.path.getsize(path)
                    file_msg = Message(msg_type="file_offer", sender=self.username, target=target,
                                       filename=os.path.basename(path), filesize=filesize)
                    self.writer.write(file_msg.serialize(self.ENCODING))
                    await self.writer.drain()
                    with open(path, "rb") as f:
                        while chunk := f.read(4096):
                            self.writer.write(chunk)
                            await self.writer.drain()
                    self.writer.write(b"ENDFILE\n")
                    await self.writer.drain()
                    print(f"Send file {path} to user {target}")

            elif msg_input.startswith("/msg "):
                parts = msg_input.split(" ", 2)
                if len(parts) == 3:
                    target, text = parts[1], parts[2]
                    msg = Message(msg_type="private", sender=self.username, target=target, text=text)
                    await self.send_message(message=msg, writer=self.writer)
            else:
                msg = Message(msg_type="broadcast", sender=self.username, text=msg_input)
                print(msg.text)
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
