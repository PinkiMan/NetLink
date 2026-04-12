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
Filename: classes.py
Directory: src/shared/
"""

import json
import asyncio

class User:
    def __init__(self, username:str=None):
        self.username = username
        self.reader = None
        self.writer = None

    def serialize(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def deserialize(data:str):
        obj = json.loads(data)
        return User(**obj)

class Users:
    def __init__(self):
        self.users = []

    def __iter__(self):
        return iter(self.users)

    def append(self, user:User) -> None:
        self.users.append(user)

    def pop(self, index:int) -> User:
        return self.users.pop(index)

    def index(self, item:User) -> int:
        return self.users.index(item)

class Address:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"

class Message:
    def __init__(self, msg_type, sender=None, target=None, text=None, filename=None, file_size=None, filehash=None, content=None, content_type=None, msg_id=None, timestamp=None, file_data=None, is_last_chunk=None, chunk_index=None):
        self.msg_type = msg_type       # "broadcast", "private", "file_offer", "file_data", "reaction", "refused_connection", "auth_response", "auth_request"
        self.msg_id = msg_id
        self.timestamp = timestamp

        self.sender = sender
        self.target = target

        self.content = content  # text/file_data
        self.content_type = content_type    #text/file
        self.text = text

        self.filename = filename
        self.file_size = file_size
        self.file_data = file_data
        self.is_last_chunk = is_last_chunk
        self.filehash = filehash
        self.chunk_index = chunk_index


    def serialize(self, encoding) -> bytes:
        return (json.dumps(self.__dict__) + "\n").encode(encoding)

    @staticmethod
    def deserialize(data, encoding):
        obj = json.loads(data.decode(encoding))
        return Message(**obj)

    def __str__(self):
        return f"{self.msg_type}:{self.sender}->{self.target}:{self.text}"

    @staticmethod
    def empty_message():
        return Message(msg_type=None)

    def is_none(self) -> bool:
        return self.msg_type is None


if __name__ == '__main__':
    pass
