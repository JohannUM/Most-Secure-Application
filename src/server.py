from cryptography.fernet import Fernet as fern
from required import messageFormating as mf
from random import randint
import socket
import threading
import base64
import json
import time

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT = "Sock It"
PRIVATE_VALUE = randint(1, 10000) # Private value, random for every new client
G = 6143 # Public values
P = 7919

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

current_connection_passwords = {}
current_connection_counters = {}
current_id_total = {}

conn_details_lock = threading.Lock()
id_total_lock = threading.Lock()

def exchange_key(conn):
    public_key = (G**PRIVATE_VALUE) % P
    mf.encode_message(str(public_key), conn)
    server_public_key = int(mf.decode_message(conn))
    private_key = (server_public_key**PRIVATE_VALUE) % P
    return fern(base64.urlsafe_b64encode((private_key).to_bytes(32, byteorder="big"))) # add to message formatting, to allow for sending encrypted messages, decrypting encrypted messages

def handle_actions(id, actions, delay):
    i = 0
    final = len(actions)
    for action in actions:
        if "INCREASE" in action:
            amount = [int(s) for s in action.split() if s.isdigit()]
            with conn_details_lock:
                current_connection_counters[id] += amount[0]
                with open("logfile.txt", "a") as logfile:
                    logfile.write(f"{id},INCREASE {amount[0]},{current_connection_counters[id]}\n")
                print(f"Increase by {amount[0]} and counter is now: {current_connection_counters[id]}")
        elif "DECREASE" in action:
            amount = [int(s) for s in action.split() if s.isdigit()]
            with conn_details_lock:
                current_connection_counters[id] -= amount[0]
                with open("logfile.txt", "a") as logfile:
                    logfile.write(f"{id},DECREASE {amount[0]},{current_connection_counters[id]}\n")
                print(f"Decrease by {amount[0]} and counter is now: {current_connection_counters[id]}")
        i+=1
        if i < final:
            time.sleep(delay)

def handle_json(msg, conn):
    data = json.loads(msg)
    id = data["id"]
    password = data["password"]
    actions = data["actions"]["steps"]
    delay = int(data["actions"]["delay"])

    if id not in current_connection_passwords:
        with id_total_lock:
            current_id_total[id] = 1
        print(current_id_total)
        add_conn_details(id, password)
        with open("logfile.txt", "a") as logfile:
            logfile.write(f"{id},Logged In,{current_connection_counters[id]}\n")
        handle_actions(id, actions, delay)
        print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
    else:
        if check_password(current_connection_passwords[id], password):
            with id_total_lock:
                current_id_total[id] += 1
            print(current_id_total)
            with open("logfile.txt", "a") as logfile:
                logfile.write(f"{id},Logged In,{current_connection_counters[id]}\n")
            handle_actions(id, actions, delay)
            print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
        else:
            mf.encode_message("\nACCESS DENIED: Another user with same ID already logged in with different password...\n",conn)

    with open("logfile.txt", "a") as logfile:
        logfile.write(f"{id},Logged Out,{current_connection_counters[id]}\n")
    remove_conn_details(id)

def add_conn_details(id, password):
    current_connection_passwords[id] = password
    current_connection_counters[id] = 0

def remove_conn_details(id):
    global current_id_total
    with id_total_lock:
        if current_id_total[id]:
            if current_id_total[id] > 1:
                current_id_total[id] -= 1
            elif current_id_total[id] == 1:
                current_id_total.pop(id)
                current_connection_counters.pop(id)
                current_connection_passwords.pop(id)

def check_password(password1, password2):
    if password1 == password2:
        return True
    else:
        return False

def handle_client(conn, addr):
    global key
    key = exchange_key(conn)
    print(f"New Connection {addr}")   
    while True:
        message = mf.receive_decrypt(conn, key)
        if message == DISCONNECT:
            break
        elif message != "":
            print(f"{addr}: {message}")
            handle_json(message, conn)
            mf.encrypt_send("Message Received!", conn, key)
    print(f"Connection closed {addr}")
    conn.close()

def start_server():
    server.listen()
    print(f"Server [{SERVER}:{PORT}] started.")
    open("logfile.txt", "w").close() # Clear logfile contents from last session
    with open("logfile.txt", "a") as logfile:
        logfile.write("ID:,Action:,Counter Value:\n") # Add header
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start_server()
