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

import argparse
import asyncio
import logging
import threading

from utils.server import Server
from utils.classes import Address
from utils.client import Client
from utils.visuals import Visuals

SERVER_IP = '10.144.130.28'
SERVER_PORT = 8888

def parser_setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NetLink is program made for sending messages and files over internet")

    parser.add_argument(
        "--mode",
        choices=["server", "client"],
        required=True,
        help="run mode: server or client"
    )

    parser.add_argument("--username", help="username (used with password)")
    parser.add_argument("--password", help="password (used with username)")
    parser.add_argument("--ascii", action="store_true", help="run with ASCII visuals")
    parser.add_argument("--gui", action="store_true", help="run with GUI")

    return parser.parse_args()

def run_server_headless():
    server = Server(Address(SERVER_IP, SERVER_PORT))
    asyncio.run(server.start())

def run_server_ascii():
    pass

def run_client_headless(username=None, password=None):
    client = Client(Address(SERVER_IP, SERVER_PORT), username, password)



    asyncio.run(client.run())

def run_client_ascii(username=None, password=None):
    client = Client(Address(SERVER_IP, SERVER_PORT), username=username, password=password)

    def runner():
        asyncio.run(client.run())

    thread = threading.Thread(target=runner, daemon=True).start()

    vis = Visuals(client)
    #vis.print_logo()
    vis.main()

def run_client_gui():
    pass

def arguments_evaluation(args):
    if args.mode == "server":
        print("Running NetLink Server...")
        if args.username or args.password:
            print(" -> Ignoring username/password (not used in server mode)")

        if args.ascii:
            print(" -> ASCII visuals")
            run_server_ascii()
        else:
            print(" -> Headless mode")
            run_server_headless()

    elif args.mode == "client":
        print("Running NetLink Client...")
        if args.username or args.password:
            if not (args.username and args.password):
                raise ValueError("username and password must by used both")
            else:
                print(f" -> Connecting as {args.username}")
        else:
            print(" -> Anonymous mode")

        if args.ascii and args.gui:
            raise ValueError("ASCII and GUI modes cannot be used simultaneously")

        elif args.ascii:
            print(" -> ASCII visuals")
            run_client_ascii(username=args.username, password=args.password)
        elif args.gui:
            print(" -> GUI visuals")
            run_client_gui()
        else:
            print(" -> Headless mode")
            run_client_headless(username=args.username, password=args.password)

def setup_logging():    # TODO: use logging in project
    logging.basicConfig(
        filename='data/app.log',
        filemode='w',
        level=logging.DEBUG,
        #format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        format="%(levelname)s - %(name)s - %(message)s",
    )

if __name__ == '__main__':
    arguments = parser_setup()
    arguments_evaluation(args=arguments)


