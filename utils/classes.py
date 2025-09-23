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
Filename: utils.py
Directory: utils/
"""

import json
import asyncio

class User:
    def __init__(self, username: str):
        self.username = username

class Address:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"

class Message:
    def __init__(self, msg_type, sender=None, target=None, text=None, filename=None, filesize=None, filehash=None):
        self.msg_type = msg_type       # "broadcast", "private", "file_offer", "file_data", "reaction", "refused_connection", "auth_response", "auth_request"
        self.sender = sender
        self.target = target
        self.text = text
        self.filename = filename
        self.filesize = filesize
        self.filehash = filehash

    def serialize(self) -> bytes:
        return (json.dumps(self.__dict__) + "\n").encode()

    @staticmethod
    def deserialize(data):
        obj = json.loads(data)
        return Message(**obj)

class Networking:
    def __init__(self):
        pass

    @staticmethod
    async def send_message(message: Message, writer: asyncio.StreamWriter) -> None:
        """ sends message to client """
        msg = message.serialize()
        # TODO: add rsa hashing
        writer.write(msg)
        await writer.drain()

    @staticmethod
    async def receive_message(reader: asyncio.StreamReader) -> Message | bool:
        """ receives message from client """
        data = await reader.readline()
        if not data:
            return False
        # TODO: add rsa hashing
        msg = Message.deserialize(data.decode())
        return msg

if __name__ == '__main__':
    pass
