import socket
import threading
import json

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT = "Sock It"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

current_connection_details = {}

def handle_actions(actions):
    pass

def handle_json(msg, conn):
    data = json.loads(msg)
    id = data["id"]
    password = data["password"]
    actions = data["actions"]["steps"]
    delay = data["actions"]["delay"]
    print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
    if id not in current_connection_details:
        current_connection_details[id] = {"password":password}
        handle_actions(actions)
    else:
        conn.send(f"Enter password for {id}: ".encode(FORMAT))
        pLength = conn.recv(HEADER).decode(FORMAT)
        pSent = ""
        if pLength:
            pLength = int(pLength)
            pSent = conn.recv(pLength).decode(FORMAT)
        if current_connection_details[id]["password"] == pSent:
            current_connection_details[id] = {"password":password}
            handle_actions(actions) # Password correct confirmation message.
        else:
            pass #return message about wrong password

def handle_client(conn, addr):
    print(f"New Connection {addr}")
    while True:
        message_length = conn.recv(HEADER).decode(FORMAT)
        if message_length:
            message_length = int(message_length)
            message = conn.recv(message_length).decode(FORMAT)
            if message == DISCONNECT:
                break
            #print(f"{addr}: {message}")
            handle_json(message, conn)
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
