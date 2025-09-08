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
import os
import hashlib

from classes import Address, Message


class Client:
    def __init__(self, server_address: Address, name: str):
        self.server_address = server_address
        self.name = name
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.server_address.ip, self.server_address.port
        )
        self.writer.write((self.name + "\n").encode())
        await self.writer.drain()
        print(f"Connected as {self.name}")

    async def listen(self):
        while True:
            data = await self.reader.readline()
            if not data:
                print("Server closed connection", file=sys.stderr)
                break
            msg = Message.deserialize(data.decode())

            if msg.type == "broadcast":
                print(f"[{msg.sender}]: {msg.text}")

            elif msg.type == "private":
                print(f"[PM from {msg.sender}]: {msg.text}")

            elif msg.type == "file_offer":
                answer = input(f"Chceš přijmout soubor {msg.filename} ({msg.filesize} bytes) od {msg.sender}? [y/n]: ").strip().lower()
                if answer == "y":
                    confirm = Message(type_="file_data", sender=self.name, filename=msg.filename)
                    self.writer.write(confirm.serialize())
                    await self.writer.drain()
                else:
                    # odmítnutí lze případně implementovat
                    pass

            elif msg.type == "file_data":
                size = msg.filesize
                data_bytes = await self.reader.readexactly(size)
                await self.reader.readline()  # --FILEEND--
                received_hash = hashlib.sha256(data_bytes).hexdigest()
                if received_hash != msg.filehash:
                    print(f"⚠️ Soubor {msg.filename} je poškozen!")
                else:
                    save_path = f"download_{msg.filename}"
                    with open(save_path, "wb") as f:
                        f.write(data_bytes)
                    print(f"📥 Soubor {msg.filename} uložen jako {save_path} (hash OK)")

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
                    file_msg = Message(type_="file_offer", sender=self.name, target=target,
                                       filename=os.path.basename(path), filesize=filesize)
                    self.writer.write(file_msg.serialize())
                    await self.writer.drain()
                    with open(path, "rb") as f:
                        while chunk := f.read(4096):
                            self.writer.write(chunk)
                            await self.writer.drain()
                    self.writer.write(b"ENDFILE\n")
                    await self.writer.drain()
                    print(f"📤 Poslal soubor {path} uživateli {target}")

            elif msg_input.startswith("/msg "):
                parts = msg_input.split(" ", 2)
                if len(parts) == 3:
                    target, text = parts[1], parts[2]
                    msg = Message(type_="private", sender=self.name, target=target, text=text)
                    self.writer.write(msg.serialize())
                    await self.writer.drain()

            else:
                msg = Message(type_="broadcast", sender=self.name, text=msg_input)
                self.writer.write(msg.serialize())
                await self.writer.drain()

    async def run(self):
        await self.connect()
        listen_task = asyncio.create_task(self.listen())
        send_task = asyncio.create_task(self.send())
        done, pending = await asyncio.wait([listen_task, send_task],
                                           return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        self.writer.close()
        await self.writer.wait_closed()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <name>")
        sys.exit(1)
    name = sys.argv[1]
    server_address = Address("127.0.0.1", 8888)
    client = Client(server_address, name)
    asyncio.run(client.run())
