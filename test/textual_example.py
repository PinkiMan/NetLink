__author__ = "Pinkas Matěj"
__maintainer__ = "Pinkas Matěj"
__email__ = "pinkas.matej@gmail.com"
__created__ = "02/11/2025"
__date__ = "02/11/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""
__credits__ = []

"""
Project: NetLink
Filename: textual_example.py
Directory: test/
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from textual.containers import Horizontal, Vertical, VerticalScroll

class ChatApp(App):

    def compose(self) -> ComposeResult:
        # Header nahoře
        yield Header(show_clock=True)

        # Hlavní horizontální layout: levý panel vs pravý panel
        with Horizontal():
            # Levý panel: Rooms nahoře, Users dole
            with Vertical(id="left_panel"):
                yield VerticalScroll(Static("> general\n  dev\n  random"), id="rooms_panel", height=10)
                yield VerticalScroll(Static("pepa\nlucie\nmarek\n(you)"), id="users_panel", height=6)

            # Pravý panel: Chat
            yield VerticalScroll(Static("[12:31] pepa: ahoj všem!\n[12:32] lucie: čau :)"), id="chat_panel", height=16)

        # Input bar dole
        yield Input(placeholder="Type message or command (/join, /msg, /quit)", id="input_bar")

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        if not text:
            return
        chat_widget = self.query_one("#chat_panel", VerticalScroll)
        current = chat_widget.children[0]
        current.update(current.renderable + f"\n[you] {text}")
        event.input.value = ""

if __name__ == "__main__":
    app = ChatApp()
    app.run()



