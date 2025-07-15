__author__ = "Pinkas Matěj - Pinki"
__maintainer__ = "Pinkas Matěj - Pinki"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "13/06/2025"
__date__ = "13/06/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

"""
Project: NetLink
Filename: logging_config.py
Directory: utils/
"""

import logging


def setup_logging():
    logging.basicConfig(
        filename='data/app.log',
        filemode='w',
        level=logging.DEBUG,
        #format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        format="%(levelname)s - %(name)s - %(message)s",
    )


if __name__ == '__main__':
    pass
