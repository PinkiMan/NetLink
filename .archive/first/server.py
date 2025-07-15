# server.py
import socket

HOST = '127.0.0.1'  # Lokální IP adresa
PORT = 65432        # Libovolný nepoužitý port

# Vytvoření socketu (IPv4, TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Čekám na spojení na {HOST}:{PORT}...")
    conn, addr = s.accept()

    with conn:
        print(f"[SERVER] Připojeno: {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[SERVER] Přijatá data: {data.decode()}")
            odpoved = f"Echo: {data.decode()}"
            conn.sendall(odpoved.encode())


