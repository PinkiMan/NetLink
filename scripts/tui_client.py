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
Filename: tui_client.py
Directory: scripts/
"""

import asyncio
import sys

from src.shared.classes import Address
from src.client.app_tui import DiscordCloneTUI

if __name__ == '__main__':
    username = sys.argv[1]
    server_address = Address("127.0.0.1", 8888)
    #asyncio.run(clt.run())

    app = DiscordCloneTUI(address=server_address, username=username)
    app.run()
