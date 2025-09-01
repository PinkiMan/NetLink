__author__ = "Pinkas Matěj - Pinki"
__maintainer__ = "Pinkas Matěj - Pinki"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "09/06/2025"
__date__ = "09/06/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

import socket
import threading
import time
import logging
import sys

"""
Project: NetLink
Filename: connection.py
Directory: utils/
"""

logger = logging.getLogger(__name__)

ENCODING = 'utf-8'
HEADER_SIZE = 1024
DISCONNECT = '!DISCONNECT!'
MAX_RETRIES = 5

# TODO: Rework with asyncio instead of threading

class Address:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"


class User:
    def __init__(self, ip, port, username):
        self.address = Address(ip, port)
        self.username = username
        self.online = False


class Message:
    def __init__(self, ):
        self.message_bytes = None
        self.message_str = None
        self.sender = None
        self.receiver = None

    def set_from_bytes(self, message_bytes):
        self.message_bytes = message_bytes
        self.message_str = self.message_bytes.decode(ENCODING)

    def set_from_str(self, message_str):
        self.message_str = message_str
        self.message_bytes = self.message_str.encode(ENCODING)

    def __str__(self):
        return f"{self.sender}->{self.receiver}:{self.message_str}"

    def __eq__(self, other):
        if other is None:
            if self.message_bytes is None:
                return True
            else:
                return False
        elif type(other) is str:
            if self.message_str == other:
                return True
            else:
                return False
        else:
            raise NotImplementedError(f"Message.__eq__ is not implemented for type={type(other)} data={other}")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __int__(self):
        return int(self.message_str)

    def to_bytes(self):
        return f"{self.message_str}|||{self.sender}|||{self.receiver}".encode(ENCODING)

    def from_bytes(self, bytes_data):
        sting_data = bytes_data.decode(ENCODING)
        self.message_str, self.sender, self.receiver = sting_data.split('|||')


class Colors:
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class Fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        light_grey = '\033[37m'
        darkgrey = '\033[90m'
        light_red = '\033[91m'
        light_green = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        light_cyan = '\033[96m'

    class Bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        light_grey = '\033[47m'


class Client:
    def __init__(self, existing_socket=None, existing_address=None, messages:list=None, users=None, username=None):
        self.server_address = Address('127.0.0.1', 5001)
        self.server_side = False

        if username is not None:
            self.username = username
        else:
            self.username = 'NONE'

        if existing_socket is not None:
            self.socket = existing_socket
            self.server_side = True
        else:
            self.__connect_to_server()

        self.connected = None

        self.existing_address = existing_address

        if messages is None:
            self.messages : list = []
        else:
            self.messages : list = messages

        if users is None:
            self.users = []
        else:
            self.users = users


    def __async_receive(self):
        while True:
            message = self.receive_message()
            print(f"{message}")

    def __connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for index in range(MAX_RETRIES):    # TODO: Rework retry connect
            try:
                self.socket.connect((self.server_address.ip, self.server_address.port))
                break
            except Exception as error:
                print(f"ERROR: {error}")
                if error is not ConnectionRefusedError:
                    print(error)
                elif error is ConnectionRefusedError and index+1 == MAX_RETRIES:
                    raise ConnectionRefusedError(f"ERROR: '{error}'")


        self.connected = True

        init_message = Message()
        init_message.set_from_str(self.username)
        self.send_message(init_message)

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} __connect_to_server: Connected to server")

        thread = threading.Thread(target=self.__async_receive)
        thread.start()

    def __receive_bytes(self, size: int = None) -> bytes:
        """ receives bytes from other side """
        if size is None:
            size = HEADER_SIZE
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        message_bytes = self.socket.recv(size)

        if message_bytes is None:
            self.connected = False
            logger.debug(f"Client.__receive(): message_bytes is None")
            self.close()

        return message_bytes

    def __send_bytes(self, message: bytes):
        pass

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

        logger.info(f"Client.__receive(): message={new_msg.message_str}")

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

    def __send_forward(self):
        while True:
            for message in self.messages:
                if message.receiver == self.username:
                    self.send_message(message)
                    print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Sending to user {message}")
                    self.messages.remove(message)

    def server_main(self):
        # TODO: receive username
        thread = threading.Thread(target=self.__send_forward)
        thread.start()

        while True:
            message = self.receive_message()
            if message is not None:
                print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} server_main: {message}")
                #self.messages.append(())

                self.messages.append(message)
            else:
                self.close()

            """for it in self.messages:
                if it[0] == self.existing_address:
                    self.send_str(it[1])"""

    def close(self):
        self.socket.close()

        print(f"Client disconnected:{self.server_address.port}")

        exit()


class Server:
    def __init__(self):
        self.socket = None
        self.address = None
        self.connections_limit = None

        self.address = Address('127.0.0.1', 5001)
        self.connections_limit = 10

        self.socket = None

        self.clients = []
        self.messages = []

        self.users = []

        self.__init_socket()

    def __init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address.ip, self.address.port))
        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} __init_socket(): socket initialized")

        #thread = threading.Thread(target=self.__printing)
        #thread.start()

    def __printing(self):
        last_message = ''
        while True:
            data = str(self)
            if last_message != data:
                print(data)
                last_message = data
            #time.sleep(1)


    def start(self):
        self.socket.listen(self.connections_limit)
        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Server is listening on", self.address)
        while True:
            self.__accept_client()

    def __accept_client(self):
        client_socket, client_address = self.socket.accept()
        print(f"{Colors.Fg.green}[INFO]{Colors.reset} Client connected: {client_address}")

        new_client = Client(client_socket, client_address, self.messages)
        self.clients.append(new_client)

        init_message = new_client.receive_message()
        new_client.username = init_message.message_str

        print(f"{Colors.Fg.yellow}[DEBUG]{Colors.reset} Client connected has username: {new_client.username}")

        thread = threading.Thread(target=new_client.server_main)
        thread.start()

    def __str__(self):
        string_data = ''

        string_data += f"{Colors.Fg.green}ONLINE{Colors.reset}\n=============================\n"
        for client in self.clients:
            string_data += f"{client.username}"

        return string_data

if __name__ == '__main__':
    pass
