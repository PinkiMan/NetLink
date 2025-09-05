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
    def __init__(self, sender, receiver, content, content_type, filename):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.content_type = content_type
        self.filename = filename

if __name__ == '__main__':
    pass
