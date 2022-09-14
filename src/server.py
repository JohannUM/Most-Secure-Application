import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT = "Sock It"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"New Connection {addr}")
    while True:
        message_length = conn.recv(HEADER).decode(FORMAT)
        if message_length:
            message_length = int(message_length)
            message = conn.recv(message_length).decode(FORMAT)
            if message == DISCONNECT:
                break
            print(f"{addr}: {message}")
            conn.send("Message received".encode(FORMAT))
    conn.close()


def start_server():
    server.listen()
    print(f"Server [{SERVER}:{PORT}] started.")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start_server()
