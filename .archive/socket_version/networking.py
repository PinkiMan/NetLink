__author__ = "Pinkas Matěj - pinka"
__maintainer__ = "Pinkas Matěj - pinka"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "01/09/2025"
__date__ = "01/09/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

"""
Project: NetLink
Filename: networking.py
Directory: utils/
"""

import asyncio

from classes import Colors, Message
from config import HEADER_SIZE, ENCODING, USERS_SPLITTER

class BaseConnection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server_side: bool):
        self.reader = reader
        self.writer = writer
        self.server_side = server_side
        self.connected = True

    async def __receive_bytes(self, size: int = None) -> bytes | None:
        """ receives bytes from other side """
        if size is None:
            size = HEADER_SIZE
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        try:
            message_bytes = await self.reader.readexactly(size)
            return message_bytes
        except asyncio.IncompleteReadError:
            self.connected = False
            await self.close()
            return None

    async def receive_message(self) -> Message | None:
        """ receives Message object from other side """
        size_bytes = await self.__receive_bytes()

        if not size_bytes:
            return None
            #raise ValueError(f"message is None, length should be number")

        size_str = size_bytes.decode(ENCODING).strip()
        if size_str == '':
            return None
            #raise ValueError(f"message is '', length should be number")

        size_int = int(size_str)
        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Size received: {str(size_int)}")

        message_bytes = await self.__receive_bytes(size_int)
        if message_bytes is None:
            return None

        new_msg = Message()
        new_msg.from_bytes(message_bytes)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Bytes received: {new_msg.sender}->{new_msg.receiver}:{new_msg.message_str}")

        return new_msg

    async def send_message(self, message: Message) -> None:
        if message.sender is not None and not self.server_side:
            raise AttributeError(f"Sender is already set ({message.sender})")

        if not self.server_side:
            message.sender = self.username

        bytes_message = message.to_bytes()
        msg_length = len(bytes_message)
        send_length = str(msg_length).encode(ENCODING)
        send_length += b' ' * (HEADER_SIZE - len(send_length))

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} send_message(): {msg_length}")

        self.writer.write(send_length)
        await self.writer.drain()
        self.writer.write(bytes_message)
        await self.writer.drain()

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} send_message(): {message}")

    async def close(self):
        self.connected = False
        self.writer.close()
        await self.writer.wait_closed()

        print(f"Client disconnected")

class ClientHandler(BaseConnection):
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, pending_messages: list, clients: list):
        super().__init__(reader, writer, server_side=True)
        self.pending_messages = pending_messages
        self.clients = clients

    async def send_forward(self):
        while self.connected:
            for message in self.pending_messages:
                if message.receiver == self.username:
                    await self.send_message(message)
                    print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Sending to user {message}")
                    self.pending_messages.remove(message)

            await asyncio.sleep(0.1)

    async def main(self):
        # TODO: receive username

        asyncio.create_task(self.send_forward())

        while True:
            message = await self.receive_message()

            if message is None:
                await self.close()
                break

            print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} server_main: {message}")

            if message.message_str == 'CLIENTS':
                await self.send_message(self.get_online_clients())
            else:
                self.pending_messages.append(message)

            """for it in self.messages:
                if it[0] == self.existing_address:
                    self.send_str(it[1])"""

    def get_online_clients(self) -> Message:
        message = Message()
        message_str = ""
        message.sender = 'SERVER'
        message.receiver = self.username
        for client in self.clients:
            message_str += client.username + USERS_SPLITTER
            print('xd')
        message.set_from_str(message_str)
        return message


if __name__ == '__main__':
    pass
