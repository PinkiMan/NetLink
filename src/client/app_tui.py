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
Filename: app_tui.py
Directory: src/client/
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, ListView, ListItem, Label, OptionList
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual import events

# Importy tvých modulů (ujisti se, že cesty jsou v PYTHONPATH)
from src.shared.networking import Networking
from src.shared.classes import Message, Address


class DiscordCloneTUI(App):
    """
    Finální verze TUI klienta pro NetLink.
    Obsahuje sjednocený sidebar, broadcast a automatické doplňování příkazů.
    """
    TITLE = "NetLink Command Center"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Ukončit", show=True),
        Binding("ctrl+l", "clear_logs", "Vymazat chat", show=True),
    ]

    CSS = """
    #sidebar {
        width: 30;
        background: $panel;
        border-right: tall $accent;
    }

    .sidebar-title {
        padding: 1;
        background: $boost;
        text-style: bold;
        text-align: center;
        color: $accent;
    }

    #chat-area { 
        width: 1fr; 
    }

    #command-suggestions {
        display: none;
        max-height: 8;
        background: $boost;
        border: tall $accent;
        dock: bottom;
        margin-bottom: 3;
        width: 100%;
    }

    #command-suggestions.visible {
        display: block;
    }

    RichLog {
        background: $surface;
        padding: 1;
    }

    Input {
        dock: bottom;
        margin: 1;
        border: tall $accent;
    }

    .broadcast-label { color: #ffaf00; text-style: bold; }
    .channel-label { color: #5fafff; }
    .user-label { color: #d787ff; }
    """

    def __init__(self, address: Address, username: str):
        super().__init__()
        self.address = address
        self.username = username
        self.network = Networking(address)
        self.active_room_id = "broadcast"  # Výchozí místnost

        self.commands = [
            ("/msg", "<user> <text> - Soukromá zpráva"),
            ("/screen", "- Snímek obrazovky"),
            ("/sendfile", "<path> - Odeslat soubor"),
            ("/ls", "- Výpis souborů"),
            ("/exit", "- Ukončit")
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("KONVERZACE", classes="sidebar-title")
                yield ListView(id="unified-list")

            with Vertical(id="chat-area"):
                yield OptionList(id="command-suggestions")
                yield RichLog(id="chat-history", wrap=True, highlight=True, markup=True)
                yield Input(placeholder="Napiš / pro příkazy...", id="msg-input")
        yield Footer()

    async def on_mount(self) -> None:
        log = self.query_one("#chat-history", RichLog)
        suggestions = self.query_one("#command-suggestions", OptionList)

        for cmd, desc in self.commands:
            suggestions.add_option(f"{cmd} [i]{desc}[/i]")

        log.write("[bold yellow]Navazování spojení...[/bold yellow]")
        try:
            await self.network.connect()
            await self.network.send_message(Message(msg_type="username", sender=self.username))

            response = await self.network.receive_message()
            if response and response.msg_type == "accepted_connection":
                log.write("[bold green]Online.[/bold green]")
                await self.setup_dummy_sidebar()
                self.run_worker(self.listen_worker())
            else:
                log.write("[bold red]Server zamítl přístup.[/bold red]")
        except Exception as e:
            log.write(f"[bold red]Chyba sítě: {e}[/bold red]")

    async def setup_dummy_sidebar(self):
        """Bezpečné naplnění sidebaru s uložením metadat do ListItem."""
        ulist = self.query_one("#unified-list", ListView)
        ulist.clear()

        rooms = [
            ("📢 broadcast", "broadcast", "broadcast-label"),
            ("# obecné", "room_1", "channel-label"),
            ("@ Pavel", "dm_pavel", "user-label")
        ]

        for name, r_id, cls in rooms:
            item = ListItem(Label(name, classes=cls), id=r_id)
            # Uložíme jméno přímo do objektu, abychom ho nemuseli dolovat z Labelu
            item.room_name = name
            await ulist.append(item)

        ulist.index = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        suggestions = self.query_one("#command-suggestions", OptionList)
        if event.value.startswith("/") and " " not in event.value:
            suggestions.add_class("visible")
            typed = event.value.split(" ")[0].lower()
            suggestions.clear_options()
            for cmd, desc in self.commands:
                if cmd.startswith(typed):
                    suggestions.add_option(f"{cmd} [i]{desc}[/i]")
        else:
            suggestions.remove_class("visible")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Vyplnění příkazu a korektní posun kurzoru."""
        inp = self.query_one("#msg-input", Input)
        suggestions = self.query_one("#command-suggestions", OptionList)

        command = str(event.option.prompt).split(" ")[0]
        new_val = f"{command} "

        inp.value = new_val
        inp.cursor_position = len(new_val)  # Klíčové pro správné psaní

        suggestions.remove_class("visible")
        inp.focus()

    def on_key(self, event: events.Key) -> None:
        suggestions = self.query_one("#command-suggestions", OptionList)

        if suggestions.has_class("visible"):
            if event.key == "up":
                suggestions.action_cursor_up()
                event.stop()
            elif event.key == "down":
                suggestions.action_cursor_down()
                event.stop()
            elif event.key == "enter":
                # Zastavíme Enter, aby neodevzdal Input (neposlal zprávu)
                event.prevent_default()
                event.stop()

                # Pokud je něco zvýrazněné v seznamu, vybereme to
                if suggestions.highlighted is not None:
                    suggestions.action_select()

    async def on_list_view_selected(self, event: ListView.Selected):
        """Bezpečné přepnutí místnosti s využitím uloženého room_name."""
        self.active_room_id = event.item.id
        room_name = getattr(event.item, "room_name", self.active_room_id)

        log = self.query_one("#chat-history", RichLog)
        log.clear()

        color = "yellow" if self.active_room_id == "broadcast" else "cyan"
        log.write(f"[bold {color}]--- {room_name} ---[/bold {color}]\n")
        self.query_one("#msg-input", Input).placeholder = f"Zpráva pro {room_name}..."

    async def on_input_submitted(self, event: Input.Submitted):
        val = event.value.strip()
        if not val or not self.active_room_id:
            return

        log = self.query_one("#chat-history", RichLog)

        if val.startswith("/"):
            msg = Message(msg_type="command", sender=self.username, target=self.active_room_id, text=val)
            await self.network.send_message(msg)
            log.write(f"[yellow][Příkaz]: {val}[/yellow]")
        else:
            m_type = "broadcast" if self.active_room_id == "broadcast" else "CHAT"
            msg = Message(msg_type=m_type, sender=self.username, target=self.active_room_id, text=val)
            await self.network.send_message(msg)
            log.write(f"[b]Já:[/b] {val}")

        event.input.value = ""
        self.query_one("#command-suggestions", OptionList).remove_class("visible")

    async def listen_worker(self):
        log = self.query_one("#chat-history", RichLog)
        while True:
            msg = await self.network.receive_message()
            if not msg: break

            # Zobrazení zprávy v aktuálním okně
            if (msg.msg_type == "broadcast" and self.active_room_id == "broadcast") or \
                    (msg.target == self.active_room_id):
                prefix = "[bold yellow][Globální][/bold yellow] " if msg.msg_type == "broadcast" else ""
                log.write(f"{prefix}[b]{msg.sender}:[/b] {msg.text}")

    def action_clear_logs(self):
        self.query_one("#chat-history", RichLog).clear()


if __name__ == "__main__":
    addr = Address("127.0.0.1", 8888)
    DiscordCloneTUI(addr, "Uživatel").run()