__author__ = "Pinkas Matěj"
__maintainer__ = "Pinkas Matěj"
__email__ = "pinkas.matej@gmail.com"
__created__ = "08/04/2026"
__date__ = "08/04/2026"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""
__credits__ = []

"""
Project: NetLink
Filename: headless_server.py
Directory: scripts/
"""

import asyncio

from src.server.main import Server
from src.shared.classes import Address

if __name__ == '__main__':
    server = Server(Address("127.0.0.1", 8888))

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down...")
        asyncio.run(server.stop())
