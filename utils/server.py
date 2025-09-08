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
import sys
import hashlib

from classes import Address, Message


class Server:
    def __init__(self, server_address: Address):
        self.server_address = server_address
        self.clients = {}  # name -> {"reader": reader, "writer": writer}
        self.pending_files = {}  # filename -> {"target": target_name, "data": bytes}
        self.offline_messages = {}  # target_name -> [Message]

    async def handle_client(self, reader, writer):
        name = (await reader.readline()).decode().strip()
        if not name or name in self.clients:
            writer.write(b"Invalid or duplicate name. Connection closed.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        self.clients[name] = {"reader": reader, "writer": writer}
        await self.broadcast(Message(type_="broadcast", text=f"*** {name} has joined the chat ***", sender="Server"), exclude=name)

        # doručení offline zpráv
        if name in self.offline_messages:
            for msg in self.offline_messages[name]:
                writer.write(msg.serialize())
                await writer.drain()
            del self.offline_messages[name]

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                msg = Message.deserialize(data.decode())

                # broadcast
                if msg.type == "broadcast":
                    await self.broadcast(msg, exclude=msg.sender)

                # private
                elif msg.type == "private":
                    target = msg.target
                    if target in self.clients:
                        twriter = self.clients[target]["writer"]
                        twriter.write(msg.serialize())
                        await twriter.drain()
                    else:
                        # offline
                        self.offline_messages.setdefault(target, []).append(msg)

                # file offer (odesílatel posílá soubor)
                elif msg.type == "file_offer":
                    target = msg.target
                    data_bytes = await reader.readexactly(msg.filesize)
                    await reader.readline()  # ENDFILE
                    self.pending_files[msg.filename] = {"target": target, "data": data_bytes}

                    if target in self.clients:
                        # pošleme nabídku příjemci
                        offer = Message(type_="file_offer", sender=msg.sender, target=target,
                                        filename=msg.filename, filesize=msg.filesize)
                        self.clients[target]["writer"].write(offer.serialize())
                        await self.clients[target]["writer"].drain()
                    # pokud offline, doručíme při připojení

                # file accept
                elif msg.type == "file_data":  # klient potvrzuje přijetí
                    fname = msg.filename
                    if fname in self.pending_files and self.pending_files[fname]["target"] == name:
                        data_bytes = self.pending_files[fname]["data"]
                        sha256 = hashlib.sha256(data_bytes).hexdigest()
                        send_msg = Message(type_="file_data", sender=msg.sender, filename=fname,
                                           filesize=len(data_bytes), filehash=sha256)
                        writer.write(send_msg.serialize())
                        writer.write(data_bytes)
                        writer.write(b"--FILEEND--\n")
                        await writer.drain()
                        del self.pending_files[fname]

        finally:
            if name in self.clients:
                del self.clients[name]
                await self.broadcast(Message(type_="broadcast", text=f"*** {name} has left the chat ***", sender="Server"))
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, msg, exclude=None):
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

if __name__ == "__main__":
    server_address = Address("127.0.0.1", 8888)
    server = Server(server_address)
    asyncio.run(server.start())
