import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

def prijem(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print("[SERVER] Klient se odpojil.")
            break
        print(f"[KLIENT -> SERVER]: {data.decode()}")

def odesilani(conn):
    while True:
        msg = input()
        conn.sendall(msg.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Čekám na spojení na {HOST}:{PORT}...")
    conn, addr = s.accept()
    print(f"[SERVER] Připojen klient: {addr}")

    vlakno_recv = threading.Thread(target=prijem, args=(conn,))
    vlakno_send = threading.Thread(target=odesilani, args=(conn,))
    vlakno_recv.start()
    vlakno_send.start()

    vlakno_recv.join()
    vlakno_send.join()
