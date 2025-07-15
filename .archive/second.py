import socket


class Address:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"{self.ip}:{self.port}"


class Client:
    def __init__(self):
        self.server_address = Address('127.0.0.1', 5001)
        self.client_address = Address('127.0.0.1', 5002)

        self.server_socket = None
        self.receiver_socket = None

        self.__connect_to_server()

        self.send_str(f"{self.client_address.ip}:{self.client_address.port}")
        self.__start_receiver()

    def __connect_to_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((self.server_address.ip, self.server_address.port))

    def __start_receiver(self):
        self.hosting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hosting_socket.bind((self.client_address.ip, self.client_address.port))
        self.hosting_socket.listen(1)
        self.receiver_socket, client_address = self.hosting_socket.accept()

    def send_str(self, message_str):
        message = str(message_str).encode('utf-8')
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (1024 - len(send_length))

        self.server_socket.send(send_length)
        self.server_socket.send(message)
        print('send:', message_str)

    def __receive(self, size: int = None):
        if size is None:
            size = 1024
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        message = self.receiver_socket.recv(size).decode('utf-8')
        # TODO: add check if message is empty or user disconnected
        return message

    def receive_message(self):
        length = self.__receive()  # receive (int) len of incoming message
        if length:
            length_int = int(length)
            message = self.__receive(length_int)

            return message
        else:
            return None


class ServerClient:
    def __init__(self, client_socket):
        self.receiver_socket = client_socket

        ip, port = self.receive_message().split(':')
        print(ip, port)

        self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender_socket.connect((ip, int(port)))
        print('connected')

    def __receive(self, size: int = None):
        if size is None:
            size = 1024
        elif type(size) is not int:
            raise TypeError(f"size should be: int not {type(size)}")

        message = self.receiver_socket.recv(size).decode('utf-8')
        # TODO: add check if message is empty or user disconnected
        return message

    def receive_message(self):
        length = self.__receive()  # receive (int) len of incoming message
        if length:
            length_int = int(length)
            message = self.__receive(length_int)

            return message
        else:
            return None

    def send_str(self, message_str):
        message = str(message_str).encode('utf-8')
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (1024 - len(send_length))

        self.sender_socket.send(send_length)
        self.sender_socket.send(message)





class Server:
    def __init__(self):
        self.address = ('127.0.0.1', 5001)
        self.connections_limit = 10

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address[0], self.address[1]))

    def start(self):
        self.socket.listen()
        print('[LISTENING] Server is listening on', self.address)

        self.accept_client()

    def accept_client(self):
        receive_socket, client_address = self.socket.accept()
        print("accepted")

        new_client = ServerClient(receive_socket)

        print(new_client.receive_message())
        #new_client.send_str('cauky')
        print(new_client.receive_message())




if input("server: [y/n]") == 'y':
    print("server")

    serv = Server()
    serv.start()
else:
    print("client")

    client = Client()

    client.send_str('ahojda')
    #print(client.receive_message())
    client.send_str('END')
