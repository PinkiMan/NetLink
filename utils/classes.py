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
    def __init__(self, username: str=None):
        self.username = username

    def serialize(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def deserialize(data:str):
        obj = json.loads(data)
        return User(**obj)

class Address:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"

class Message:
    def __init__(self, msg_type, sender=None, target=None, text=None, filename=None, file_size=None, filehash=None):
        self.msg_type = msg_type       # "broadcast", "private", "file_offer", "file_data", "reaction", "refused_connection", "auth_response", "auth_request"
        self.sender = sender
        self.target = target
        self.text = text
        self.filename = filename
        self.file_size = file_size
        self.filehash = filehash

    def serialize(self, encoding) -> bytes:
        return (json.dumps(self.__dict__) + "\n").encode(encoding)

    @staticmethod
    def deserialize(data, encoding):
        obj = json.loads(data.decode(encoding))
        return Message(**obj)

    def __str__(self):
        return f"{self.msg_type}:{self.sender}->{self.target}:{self.text}"

class Networking:
    def __init__(self):
        self.ENCODING = 'utf-8'
        self.HEADER_SIZE = 1024
        self.DISCONNECT = '!DISCONNECT!'
        self.MAX_RETRIES = 5
        self.MESSAGE_PART_SPLITTER = '|||'
        self.USERS_SPLITTER = '!!!'


    async def send_message(self, message: Message, writer: asyncio.StreamWriter) -> None:
        """ sends message  """
        msg = message.serialize(self.ENCODING)
        # TODO: add rsa hashing
        writer.write(msg)   # queue send to server
        await writer.drain()    # send queue

    async def receive_message(self, reader: asyncio.StreamReader) -> Message | bool:
        """ receives message from client """
        data = await reader.readline()
        if not data:
            return False
        # TODO: add rsa hashing
        msg = Message.deserialize(data, self.ENCODING)
        return msg

if __name__ == '__main__':
    pass
