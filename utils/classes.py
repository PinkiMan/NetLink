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
Filename: utils.py
Directory: utils/
"""

import json

class Address:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"

class Message:
    def __init__(self, msg_type, sender=None, target=None, text=None, filename=None, filesize=None, filehash=None):
        self.type = msg_type       # "broadcast", "private", "file_offer", "file_data", "reaction", "refused_connection", "auth_response", "auth_request"
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
        obj['msg_type'] = obj.pop('type')
        return Message(**obj)

if __name__ == '__main__':
    pass
