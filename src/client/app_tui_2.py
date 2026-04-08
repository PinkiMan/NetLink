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
Filename: app_tui_2.py
Directory: src/client/
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, ListView, ListItem, Label, Static
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual import events

# Dummy třídy
try:
    from src.shared.networking import Networking
    from src.shared.classes import Message, Address
except ImportError:
    class Address:
        def __init__(self, ip, port): self.ip, self.port = ip, port


    class Message:
        def __init__(self, msg_type, sender, target=None, text=""):
            self.msg_type, self.sender, self.target, self.text = msg_type, sender, target, text

ASCII_LOGO = r"""
  _   _  ______  _______  _      _____  _   _  _   _ 
 | \ | ||  ____||__   __|| |    |_   _|| \ | || | / /
 |  \| || |__      | |   | |      | |  |  \| || |/ / 
 | . ` ||  __|     | |   | |      | |  | . ` ||    \ 
 | |\  || |____    | |   | |____ _| |_ | |\  || |\  \
 |_| \_||______|   |_|   |______||_____||_| \_||_| \_\
 -----------------------------------------------------
 [ TERMINAL INTERFACE v2.0 - SECURE CONNECTION ONLY ]
"""


class DiscordCloneTUI(App):
    TITLE = "NETLINK TERMINAL"

    CSS = """
    Screen {
        background: #000000;
        color: #00ff00;
    }

    #sidebar {
        width: 32;
        background: #000000;
        border-right: double #00ff00;
    }

    /* Odstranění všech okrajů a šedých focusů */
    ListView, ListItem, RichLog {
        background: #000000 !important;
        border: none !important;
    }

    /* Zajištění, že focus nezpůsobí šedý nádech */
    ListView:focus, ListItem:focus, RichLog:focus {
        background: #000000 !important;
    }

    /* POUZE vybraný prvek svítí */
    ListView > ListItem.--highlight {
        background: #00ff00 !important;
        color: #000000 !important;
        text-style: bold;
    }

    .sidebar-title { width: 100%; text-align: center; background: #00ff00; color: #000000; margin-bottom: 1; }

    Input {
        background: #000000;
        color: #ffaf00;
        border: dashed #00ff00;
        margin: 1;
    }

    Input:focus { border: heavy #00ff00; }

    .broadcast-label { color: #ff00ff; }
    .channel-label { color: #00ffff; }
    .user-label { color: #ffff00; }
    """

    def __init__(self, address: Address, username: str):
        super().__init__()
        self.address = address
        self.username = username
        self.active_room_id = "broadcast"

    def compose(self) -> ComposeResult:
        yield Static(ASCII_LOGO)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label(" [ CHANNELS ]", classes="sidebar-title")
                yield ListView(id="unified-list")
            with Vertical(id="chat-area"):
                # can_focus jsme odebrali z initu
                yield RichLog(id="chat-history", wrap=True, markup=True)
                yield Input(placeholder="COMMAND_PROMPT >", id="msg-input")
        yield Footer()

    async def on_mount(self):
        # TADY nastavujeme focus a barvy, aby to nešedlo
        chat = self.query_one("#chat-history", RichLog)
        ulist = self.query_one("#unified-list", ListView)

        # Vypneme schopnost přijmout fokus (tím pádem i nasednout)
        chat.can_focus = False
        ulist.can_focus = False

        # Vynucení černé, aby i 'tint' neměl co zviditelnit
        chat.styles.background = "#000000"
        ulist.styles.background = "#000000"

        await self.setup_dummy_sidebar()

    async def setup_dummy_sidebar(self):
        ulist = self.query_one("#unified-list", ListView)
        rooms = [
            (":: BROADCAST", "broadcast", "broadcast-label"),
            (":: GENERAL", "room_1", "channel-label")
        ]
        for name, r_id, cls in rooms:
            item = ListItem(Label(name, classes=cls), id=r_id)
            item.room_name = name
            # Každý prvek v seznamu taky nesmí šednout
            item.styles.background = "#000000"
            await ulist.append(item)

    async def on_list_view_selected(self, event: ListView.Selected):
        self.active_room_id = event.item.id
        self.query_one("#chat-history").write(f">> LINKED TO {event.item.id}")

    async def on_input_submitted(self, event: Input.Submitted):
        if event.value.strip():
            self.query_one("#chat-history").write(f"<{self.username}> {event.value}")
            event.input.value = ""


if __name__ == "__main__":
    DiscordCloneTUI(Address("127.0.0.1", 8888), "GUEST").run()