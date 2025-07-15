# client.py
import socket

HOST = '127.0.0.1'  # IP adresa serveru
PORT = 5001        # Stejný port jako na serveru

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"[KLIENT] Připojeno k serveru na {HOST}:{PORT}")
    while True:
        zprava = input("[KLIENT] Zadej zprávu (nebo 'exit' pro ukončení): ")
        if zprava.lower() == 'exit':
            break
        s.sendall(zprava.encode())
        data = s.recv(1024)
        print(f"[KLIENT] Odpověď od serveru: {data.decode()}")
