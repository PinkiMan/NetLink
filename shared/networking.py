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
Filename: networking.py
Directory: shared/
"""

import asyncio

from shared.classes import Message, Address

class Networking:
    def __init__(self):
        self.ENCODING = 'utf-8'
        self.HEADER_SIZE = 1024
        self.DISCONNECT = '!DISCONNECT!'
        self.MAX_RETRIES = 5
        self.MESSAGE_PART_SPLITTER = '|||'
        self.USERS_SPLITTER = '!!!'

        self.reader:asyncio.StreamReader = None
        self.writer:asyncio.StreamWriter = None
        self.server_address:Address = None

    async def send_message(self, message: Message, writer: asyncio.StreamWriter) -> None:
        """ sends message  """
        msg = message.serialize(self.ENCODING)
        # TODO: add rsa hashing
        writer.write(msg)   # queue send to server
        await writer.drain()    # send queue

    async def receive_message(self) -> Message:
        """ receives message from client """
        data = await self.reader.readline()
        if not data:
            return Message.empty_message()
        # TODO: add rsa hashing
        msg = Message.deserialize(data, self.ENCODING)
        return msg

    async def connect(self):
        """Connect to the server"""
        self.reader, self.writer = await asyncio.open_connection(
            self.server_address.ip, self.server_address.port
        )  # open connection to server

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()



if __name__ == '__main__':
    pass
