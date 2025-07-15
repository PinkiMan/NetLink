import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

def prijem(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            print("[KLIENT] Server ukončil spojení.")
            break
        print(f"[SERVER -> KLIENT]: {data.decode()}")

def odesilani(sock):
    while True:
        msg = input()
        sock.sendall(msg.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"[KLIENT] Připojeno k serveru na {HOST}:{PORT}")

    vlakno_recv = threading.Thread(target=prijem, args=(s,))
    vlakno_send = threading.Thread(target=odesilani, args=(s,))
    vlakno_recv.start()
    vlakno_send.start()

    vlakno_recv.join()
    vlakno_send.join()
