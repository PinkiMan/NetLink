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

"""
Project: NetLink
Filename: main.py
Directory: /
"""

import time

from utils.logging_config import setup_logging
from utils.connection import Client, Server


if __name__ == '__main__':

    setup_logging()

    if input("server: [y/n]") == 'y':
        print("server")

        serv = Server()
        serv.start()
    else:
        print("client")

        client = Client()

        while True:
            client.send_str(input('>'))
            # client.send_str('cauky')
            # time.sleep(1)

