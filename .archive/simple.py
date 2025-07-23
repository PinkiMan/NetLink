import socket
import threading
import time

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
CLIENT_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
FORMAT = 'utf-8'


class Server:
    def __init__(self):
        s = socket.socket()
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen(10)

        self.socket = s
        self.client = None

    def main(self):
        client_socket, address = self.socket.accept()

        self.client = client_socket

        while True:
            print(self.receive())

    def receive(self):
        received = self.client.recv(BUFFER_SIZE).decode()
        return received

    def close(self):
        self.socket.close()


class Client:
    def __init__(self):
        s = socket.socket()
        s.connect((SERVER_HOST, CLIENT_PORT))
        self.socket = s

    def send(self, message):
        self.socket.send(f"{message}".encode())

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    server = Server()

    thread = threading.Thread(target=server.main)
    thread.start()

    time.sleep(5)

    client = Client()

    message = 'idk nejaky data'
    send_length = str(message).encode(FORMAT)
    send_length += b' ' * (BUFFER_SIZE - len(send_length))
    client.send(send_length)
    message = server.receive()
    print(message)
