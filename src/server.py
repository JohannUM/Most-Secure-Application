from required import messageFormating as mf
import socket
import threading
import json

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT = "Sock It"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)



current_connection_password = {}
current_connection_counters = {}
conn_details_lock = threading.Lock()

def handle_actions(id, actions):
    for action in actions:
        if "INCREASE" in action:
            amount = [int(s) for s in action.split() if s.isdigit()]
            with conn_details_lock:
                current_connection_counters[id] += amount[0]
        elif "DECREASE" in action:
            amount = [int(s) for s in action.split() if s.isdigit()]
            with conn_details_lock:
                current_connection_counters[id] -= amount[0]

def handle_json(msg, conn):
    data = json.loads(msg)
    id = data["id"]
    password = data["password"]
    actions = data["actions"]["steps"]
    handle_actions(actions)
    delay = data["actions"]["delay"]
    #print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
    """ TODO fix and test properly
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
    """

def handle_client(conn, addr):
    print(f"New Connection {addr}")
    while True:
        message = mf.decode_message(conn)
        if message == DISCONNECT:
            break
        elif message != "":
            #print(f"{addr}: {message}")
            handle_json(message, conn)
            mf.encode_message("Message Received!", conn)
    print(f"Connection closed {addr}")
    conn.close()


def start_server():
    server.listen()
    print(f"Server [{SERVER}:{PORT}] started.")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start_server()
