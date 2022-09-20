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



current_connection_passwords = {}
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

    if id not in current_connection_passwords:
        add_conn_details(id, password)
        print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
    else:
        if check_password(current_connection_passwords[id], password):
            print("HERE")
            pass
        else:
            mf.encode_message("\nACCESS DENIED: Another user with same ID already logged in with different password...\n",conn)

def add_conn_details(id, password):
    current_connection_passwords[id] = password
    current_connection_counters[id] = 0

def check_password(password1, password2):
    if password1 == password2:
        return True
    else:
        return False



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
