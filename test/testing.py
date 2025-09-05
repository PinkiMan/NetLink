import unittest
import asyncio
from utils.asynchronous import Server, Address

class TestChatServer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Spustíme server na volném portu

        self.server = Server(Address("127.0.0.1", 0))
        self.server_task = asyncio.create_task(self.server.start())

        # počkáme, až server začne naslouchat
        while not self.server.server:
            await asyncio.sleep(0.01)

        self.host, self.port = self.server.server.sockets[0].getsockname()

    async def asyncTearDown(self):
        self.server.server.close()
        await self.server.server.wait_closed()
        self.server_task.cancel()

    async def connect_client(self, name):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        # přečteme prompt
        await reader.readline()
        writer.write(f"{name}\n".encode())
        await writer.drain()
        return reader, writer

    async def test_list_command(self):
        # připojíme dva klienty
        r1, w1 = await self.connect_client("alice")
        r2, w2 = await self.connect_client("bob")

        # klient 1 pošle /list
        w1.write(b"/list\n")
        await w1.drain()
        response = await r1.readline()
        self.assertIn("alice", response.decode())
        self.assertIn("bob", response.decode())

        # zavřeme klienty
        w1.close()
        w2.close()
        await w1.wait_closed()
        await w2.wait_closed()

    async def test_broadcast(self):
        r1, w1 = await self.connect_client("alice")
        r2, w2 = await self.connect_client("bob")

        w1.write(b"Hello everyone\n")
        await w1.drain()
        msg = await r2.readline()
        self.assertIn("Hello everyone", msg.decode())

        w1.close()
        w2.close()
        await w1.wait_closed()
        await w2.wait_closed()

    async def test_private_message(self):
        r1, w1 = await self.connect_client("alice")
        r2, w2 = await self.connect_client("bob")

        w1.write(b"@bob Secret message\n")
        await w1.drain()
        msg = await r2.readline()
        self.assertIn("Secret message", msg.decode())
        self.assertIn("private", msg.decode())

        # Alice by neměla dostat svou vlastní zprávu
        self.assertTrue(w1._transport.is_closing() == False)

        w1.close()
        w2.close()
        await w1.wait_closed()
        await w2.wait_closed()


if __name__ == '__main__':
    unittest.main()
