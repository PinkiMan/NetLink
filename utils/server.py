__author__ = "Pinkas Matěj - pinka"
__maintainer__ = "Pinkas Matěj - pinka"
__email__ = "pinkas.matej@gmail.com"
__credits__ = []
__created__ = "02/09/2025"
__date__ = "02/09/2025"
__status__ = "Prototype"
__version__ = "0.1.0"
__copyright__ = ""
__license__ = ""

"""
Project: NetLink
Filename: server.py
Directory: utils/
"""

import asyncio
import hashlib

from classes import Address, Message, Networking, User


class Server(Networking):
    def __init__(self, server_address: Address):
        super().__init__()
        self.server_address = server_address
        self.clients = {}  # name -> {"reader": reader, "writer": writer}
        self.pending_files = {}  # filename -> {"target": target_name, "data": bytes}
        self.offline_messages = {}  # target_name -> [Message]
        self.users = {"alice": "secret", "bob": "1234"}     # TODO: Add database of clients


    @staticmethod
    async def close(writer: asyncio.StreamWriter):
        writer.close()
        await writer.wait_closed()

    async def deliver_pending_messages(self, user: User, writer: asyncio.StreamWriter):
        """ delivers all pending/offline messages to user """

        if user.username in self.offline_messages:
            for msg in self.offline_messages[user.username]:
                await self.send_message(msg, writer)
            del self.offline_messages[user.username]

    async def handle_client(self, reader, writer):
        name = (await reader.readline()).decode().strip()

        user = User(username=name)  #REWORK: rework to

        # refuse client if it has no name or name already in connected clients
        if not name or name in self.clients:
            message = Message(msg_type='refused_connection', text="Invalid or duplicate name. Connection closed.")
            await self.send_message(message, writer)

            await self.close(writer)
            return

        self.clients[name] = {"reader": reader, "writer": writer}
        await self.broadcast(Message(msg_type="broadcast", text=f"*** {name} has joined the chat ***", sender="Server"), exclude=name)

        await self.deliver_pending_messages(user=user, writer=writer) # deliver pending/offline messages

        try:
            while True:
                msg = await self.receive_message(reader)

                if msg.msg_type == "broadcast":     #broadcating messages to all clients
                    await self.broadcast(msg, exclude=msg.sender)

                # private
                elif msg.msg_type == "private":
                    target = msg.target
                    if target in self.clients:
                        twriter = self.clients[target]["writer"]
                        twriter.write(msg.serialize())
                        await twriter.drain()
                    else:
                        # offline
                        self.offline_messages.setdefault(target, []).append(msg)

                # file offer (odesílatel posílá soubor)
                elif msg.msg_type == "file_offer":
                    target = msg.target
                    data_bytes = await reader.readexactly(msg.filesize)
                    await reader.readline()  # ENDFILE
                    self.pending_files[msg.filename] = {"target": target, "data": data_bytes}

                    if target in self.clients:
                        # pošleme nabídku příjemci
                        offer = Message(msg_type="file_offer", sender=msg.sender, target=target,
                                        filename=msg.filename, filesize=msg.filesize)
                        self.clients[target]["writer"].write(offer.serialize())
                        await self.clients[target]["writer"].drain()
                    # pokud offline, doručíme při připojení

                # file accept
                elif msg.msg_type == "file_data":  # klient potvrzuje přijetí
                    fname = msg.filename
                    if fname in self.pending_files and self.pending_files[fname]["target"] == name:
                        data_bytes = self.pending_files[fname]["data"]
                        sha256 = hashlib.sha256(data_bytes).hexdigest()
                        send_msg = Message(msg_type="file_data", sender=msg.sender, filename=fname,
                                           filesize=len(data_bytes), filehash=sha256)
                        writer.write(send_msg.serialize())
                        writer.write(data_bytes)
                        writer.write(b"--FILEEND--\n")
                        await writer.drain()
                        del self.pending_files[fname]

        finally:
            if name in self.clients:
                del self.clients[name]
                await self.broadcast(Message(msg_type="broadcast", text=f"*** {name} has left the chat ***", sender="Server"))
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, msg, exclude=None):
        """ broadcast a message to all clients """
        for user, client in list(self.clients.items()):
            if user != exclude:
                try:
                    client["writer"].write(msg.serialize())
                    await client["writer"].drain()
                except:
                    del self.clients[user]

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.server_address.ip, self.server_address.port
        )
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        # oznámíme klientům shutdown
        shutdown_msg = Message(msg_type="broadcast", sender="Server", text="*** Server shutting down ***")
        await self.broadcast(shutdown_msg)

        print("Stopping server...")
        self.server.close()
        await self.server.wait_closed()

        # zavřeme všechny klienty
        for name, client in list(self.clients.items()):
            writer = client["writer"]
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Chyba při zavírání klienta {name}: {e}")
        self.clients.clear()
        print("Server stopped cleanly.")

if __name__ == "__main__":
    server = Server(Address("127.0.0.1", 8888))

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down...")
        asyncio.run(server.stop())
