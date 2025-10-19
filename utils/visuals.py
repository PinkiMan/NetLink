__author__ = "Pinkas Matěj - Pinki"
__maintainer__ = "Pinkas Matěj - Pinki"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "23/09/2025"
__date__ = "23/09/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

"""
Project: NetLink
Filename: visuals.py
Directory: utils/
"""

import sys
import platform
import os

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

class Visuals:
    def __init__(self, client):
        self.client = client

        self.__window_height = 20  # height of console window
        self.__window_width = 80  # width of console window

        self.primary_fg_color = Colors.reset  # primary color of console window
        self.secondary_fg_color = Colors.bold  # secondary color of console window
        self.tertiary_fg_color = Colors.Fg.light_cyan  # tertiary color of console window

        self.do_autoresize = True   #
        self.fps = 10               #

        self.actual_string = ''
        self.last_string = ''

    def print_line(self, text, text_color, border_color):
        line_string = (f"{border_color}┃"
                       f"{text_color}{text.ljust(self.__window_width - 2, ' ')}"
                       f"{border_color}┃{Colors.reset}\n")
        self.actual_string += line_string

    def print_box_start(self, text, border_color):
        line_string = f"{border_color}┏╸{text}╺{'━'*(self.__window_width - 3 - len(text) - 1)}┓{Colors.reset}\n"
        self.actual_string += line_string

    def print_box_end(self, border_color):
        line_string = f"{border_color}┗{'━' * (self.__window_width - 2)}┛{Colors.reset}\n"
        self.actual_string += line_string

    def set_cmd_size(self):
        plt = platform.system()

        if plt == 'Darwin':
            os.system(f"printf \'\e[8;{self.__window_height};{self.__window_width}t\'")
            pass
        elif plt == 'Windows':
            os.system(f"mode con: cols={self.__window_width} lines={self.__window_height}")

    def auto_resize(self):
        size = os.get_terminal_size()
        if size[0] != self.__window_width or size[1] != self.__window_height:
            self.set_cmd_size()

    def update(self):
        self.actual_string = '\n'
        """if self.do_autoresize:
            self.auto_resize()"""

        self.print_box_start('Stats', self.tertiary_fg_color)

        self.print_line(f"Connected as: {self.client.username.ljust(self.__window_width - 13 - 7 -14 -2-1 , ' ')} Server ping: {str(-1).rjust(4)} ms",
                        self.secondary_fg_color,
                        self.tertiary_fg_color)

        self.print_box_end(self.tertiary_fg_color)

        self.print_box_start('Playing', self.primary_fg_color)

        self.print_box_end(self.primary_fg_color)

        if self.last_string != self.actual_string:
            sys.stdout.write(self.actual_string)
            #print(self.actual_string, end='')
            sys.stdout.flush()
            self.last_string = self.actual_string

    def main(self):
        while True:
            self.update()

    def print_logo(self):
        for _ in range(2):
            print()

        offset = 20
        with open('data/logo', 'r') as file:
            for line in file.readlines():
                print(' ' * offset + line, end='')

        for _ in range(1):
            print()

if __name__ == '__main__':
    pass
