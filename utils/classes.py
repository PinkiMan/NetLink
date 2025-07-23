__author__ = "Pinkas Matěj - pinka"
__maintainer__ = "Pinkas Matěj - pinka"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "21/07/2025"
__date__ = "21/07/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

"""
Project: NetLink
Filename: classes.py
Directory: utils/
"""

from utils.config import ENCODING

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

if __name__ == '__main__':
    pass
