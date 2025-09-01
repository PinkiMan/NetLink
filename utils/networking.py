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
    def __init__(self, socket_connection, server_side):
        self.socket = socket_connection
        self.server_side = server_side

    async def __receive_bytes(self, size: int = None) -> bytes:
        """ receives bytes from other side """
        if size is None:
            size = HEADER_SIZE
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        message_bytes = self.socket.recv(size)

        if message_bytes is None:
            self.connected = False
            self.close()

        return message_bytes

    def receive_message(self) -> Message | None:
        """ receives Message object from other side """
        size_bytes = self.__receive_bytes()

        if size_bytes == None:
            return None
            #raise ValueError(f"message is None, length should be number")
        size_str = size_bytes.decode(ENCODING)

        if size_str == '':
            return None
            #raise ValueError(f"message is '', length should be number")

        size_int = int(size_str)
        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Size received: {str(size_int)}")

        message_bytes = self.__receive_bytes(size_int)

        new_msg = Message()
        new_msg.from_bytes(message_bytes)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Bytes received: {new_msg.sender}->{new_msg.receiver}:{new_msg.message_str}")

        return new_msg

    def send_message(self, message: Message) -> None:
        if message.sender is not None and self.server_side is False:
            raise AttributeError(f"Sender is already set ({message.sender})")

        if not self.server_side:
            message.sender = self.username

        bytes_message = message.to_bytes()
        msg_length = len(bytes_message)
        send_length = str(msg_length).encode(ENCODING)
        send_length += b' ' * (HEADER_SIZE - len(send_length))

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} send_message(): {msg_length}")

        self.socket.send(send_length)
        self.socket.send(bytes_message)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} send_message(): {message}")

    def close(self):
        self.socket.close()

        print(f"Client disconnected:{self.server_address.port}")

class ClientHandler(BaseConnection):
    def __init__(self, client_socket, client_address, pending_messages, clients):
        super().__init__(client_socket, True)
        self.client_socket = client_socket
        self.client_address = client_address
        self.pending_messages = pending_messages
        self.clients = clients

    async def __send_forward(self):
        while True:
            for message in self.pending_messages:
                if message.receiver == self.username:
                    self.send_message(message)
                    print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Sending to user {message}")
                    self.pending_messages.remove(message)

    def main(self):
        # TODO: receive username

        thread = threading.Thread(target=self.__send_forward)
        thread.start()

        while True:
            message = self.receive_message()
            if message is not None:
                print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} server_main: {message}")
                # self.messages.append(())

                if message.message_str == 'CLIENTS':
                    self.send_message(self.get_online_clients())
                else:
                    self.pending_messages.append(message)
            else:
                self.close()
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
