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
import sys
import threading

from utils.logging_config import setup_logging
from utils.connection import Client, Server, Message

from utils.ClientWindow_v2 import *

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


    """style = sys.argv[1]

    if style == 'server':

        while True:
            print("server starting")

            serv = Server()
            thread = threading.Thread(target=serv.start)
            thread.start()
            while True:
                data = input("")
                if data == 'restart':
                    thread.join()
                    break


    elif style == 'client':
        print("client")

        client = Client(username=sys.argv[2])

        receiver = None
        while True:

            new_string = input('>')

            if new_string.startswith('send to '):
                receiver = new_string.split('send to ')[-1]
                new_string = ''
            else:
                new_msg = Message()
                new_msg.set_from_str(new_string)
                new_msg.receiver = receiver
                client.send_message(new_msg)
                new_string = ''
    """