import socket

server_address = ("127.0.0.1", 6980)
BUFFER_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(server_address)
print(f"Connesso al server {server_address}")

while True:
    messaggio = input("Scegli direzione,distanza:   ")
    s.sendall(messaggio.encode())

s.close()