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
Filename: headless_client.py
Directory: scripts/
"""

import asyncio
import sys

#from src.client.main import Client
from src.client.headless import Client
from src.shared.classes import Address

if __name__ == '__main__':
    username = sys.argv[1]
    addr = Address("10.144.130.28", 8888)
    #addr = Address("10.0.1.126", 8888)
    clt = Client(addr, username)
    asyncio.run(clt.run())
