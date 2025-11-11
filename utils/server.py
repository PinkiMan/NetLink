__author__ = "Pinkas Matěj - Pinki"
__maintainer__ = "Pinkas Matěj - Pinki"
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

from utils.classes import Address, Message, Networking, User, ChatRooms, ChatRoom, Users

""" shortcuts:
 - /msg = message sends directly to user to incoming messages
 - /dm  = message sends to dm and saves in chat
 - /grp = message sends to group and saves in chat
 - /all = message sends to all users to incoming messages
"""


class Server(Networking):
    def __init__(self, server_address: Address, headless: bool = True):
        super().__init__()
        self.server = None
        self.server_address = server_address
        self.clients = {}  # name -> {"reader": reader, "writer": writer}
        self.pending_files = {}  # filename -> {"target": target_name, "data": bytes}
        self.offline_messages = {}  # target_name -> [Message]
        self.users = Users()     # TODO: Add database of clients
        self.AUTH_CLIENTS_ONLY = False  # No anonym connections, clients needs to send username and password (if True)
        self.SERVER_AUTH_NEWCOMER = False   # When client want to create profile server must auth client (if True)
        self.END_TO_END_ENCRYPTION = False  #
        self.HEADLESS = headless

        self.direct_chats = []
        self.chat_rooms = ChatRooms()




        chatroom_1 = ChatRoom(name="Room 1")
        self.chat_rooms.chat_rooms.append(chatroom_1)
        chatroom_2 = ChatRoom(name="Room 2")
        self.chat_rooms.chat_rooms.append(chatroom_2)
        chatroom_3 = ChatRoom(name="Room 3")
        self.chat_rooms.chat_rooms.append(chatroom_3)


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

    async def direct_message(self, msg: Message):
        target = msg.target
        if target in self.clients:
            target_writer = self.clients[target]["writer"]
            target_writer.write(msg.serialize(self.ENCODING))
            await target_writer.drain()
        else:
            self.offline_messages.setdefault(target, []).append(msg)    # offline messages REWORK: use dictionary

    async def file_offer(self, msg: Message, reader: asyncio.StreamReader):     #REWORK: outdated function
        target = msg.target
        data_bytes = await reader.readexactly(msg.file_size)
        await reader.readline()

        self.pending_files[msg.filename] = {"target": target, "data": data_bytes}

        if target in self.clients:
            offer = Message(msg_type="file_offer", sender=msg.sender, target=target,
                            filename=msg.filename, file_size=msg.file_size)
            await self.send_message(message=offer, writer=self.clients[target]["writer"])
        # if client is offline, deliver on connection   TODO: add offline deliver

    async def file_data(self, msg: Message, user: User ,writer: asyncio.StreamWriter):
        filename = msg.filename
        if filename in self.pending_files and self.pending_files[filename]["target"] == user.username:
            data_bytes = self.pending_files[filename]["data"]
            sha256 = hashlib.sha256(data_bytes).hexdigest()
            send_msg = Message(msg_type="file_data", sender=msg.sender, filename=filename,
                               file_size=len(data_bytes), filehash=sha256)
            writer.write(send_msg.serialize(self.ENCODING))
            writer.write(data_bytes)
            writer.write(b"--FILEEND--\n")
            await writer.drain()
            del self.pending_files[filename]

    async def auth_client(self, reader: asyncio.StreamReader) -> User:
        if self.AUTH_CLIENTS_ONLY:
            return None     # TODO: add authentication for user
        else:
            msg = await self.receive_message(reader)
            name = msg.text
            user = User(username=name)  # REWORK: rework to
            return user

    async def receive_message_handle(self, reader: asyncio.StreamReader) -> Message:
        pass

    async def handle_client(self, reader, writer):
        user = await self.auth_client(reader=reader)
        name = user.username

        # refuse client if it has no name or name already in connected clients
        if not name or name in self.clients:
            message = Message(msg_type='refused_connection', text="Invalid or duplicate name. Connection closed.")
            await self.send_message(message, writer)

            await self.close(writer)
            return

        self.users.append(user)

        self.clients[name] = {"reader": reader, "writer": writer}
        await self.broadcast(Message(msg_type="broadcast", text=f"*** {name} has joined the chat ***", sender="Server"), exclude=name)

        if self.HEADLESS:
            print(f"*** {name} has joined the chat ***")

        await self.deliver_pending_messages(user=user, writer=writer) # deliver pending/offline messages

        try:
            while True:
                msg = await self.receive_message(reader)
                if msg.is_none():
                    break

                if self.HEADLESS:
                    print(msg.sender, msg.text)

                match msg.msg_type:
                    case "broadcast":
                        await self.broadcast(msg, exclude=msg.sender)
                    case "private":
                        await self.direct_message(msg)





                if msg.msg_type == "broadcast":     #broadcating messages to all clients
                    await self.broadcast(msg, exclude=msg.sender)

                elif msg.msg_type == "private":
                    await self.direct_message(msg)

                elif msg.msg_type == "file_offer":
                    await self.file_offer(msg=msg, reader=reader)

                elif msg.msg_type == "file_data":
                    await self.file_data(msg=msg, user=user, writer=writer)

                elif msg.msg_type == "list_users":
                    pass

                elif msg.msg_type == "ping":
                    new_msg = Message(msg_type="pong", sender="SERVER")
                    await self.send_message(message=new_msg, writer=self.clients[msg.sender]["writer"])

                elif msg.msg_type == "group":
                    pass


        finally:
            if name in self.clients:
                del self.clients[name]
                await self.broadcast(Message(msg_type="broadcast", text=f"*** {name} has left the chat ***", sender="Server"))
                self.users.pop(self.users.index(user))
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, msg, exclude=None):
        """ broadcast a message to all clients """
        for user, client in list(self.clients.items()):
            if user != exclude:
                try:
                    await self.send_message(message=msg, writer=client["writer"])
                except Exception as e:
                    if self.HEADLESS:
                        print(f"Error in sending to {user}: {e}")
                    del self.clients[user]

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, host=self.server_address.ip, port=self.server_address.port
        )

        if self.server.sockets[0].getsockname() != (self.server_address.ip, self.server_address.port):
            raise ConnectionError(f"Could not establish connection on address {self.server_address.ip}:{self.server_address.port} instead of {self.server.sockets[0].getsockname()[0]}:{self.server.sockets[0].getsockname()[1]}")

        if self.HEADLESS:
            print(f"Server started on address {self.server_address.ip}:{self.server_address.port}")

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        # broadcast to all clients about server shutdown
        shutdown_msg = Message(msg_type="broadcast", sender="Server", text="*** Server shutting down ***")
        await self.broadcast(shutdown_msg)

        if self.HEADLESS:
            print("Stopping server...")
        self.server.close()
        await self.server.wait_closed()

        # close all client connections
        for name, client in list(self.clients.items()):
            writer = client["writer"]
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                if self.HEADLESS:
                    print(f"Error in closing client {name}: {e}")
        self.clients.clear()
        if self.HEADLESS:
            print("Server stopped cleanly.")

if __name__ == "__main__":
    server = Server(Address("127.0.0.1", 8888))

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down...")
        asyncio.run(server.stop())
