from required import messageFormating as mf
import socket
import threading
import json
import time

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT = "Sock It"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

current_connection_passwords = {}
current_connection_counters = {}
current_id_total = {}

conn_details_lock = threading.Lock()
id_total_lock = threading.Lock()

def handle_actions(id, actions, delay):
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
            logfile.write(f"{id},Logged In,0\n")
        handle_actions(id, actions, delay)
        print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
    else:
        if check_password(current_connection_passwords[id], password):
            with id_total_lock:
                current_id_total[id] += 1
            print(current_id_total)
            with open("logfile.txt", "a") as logfile:
                logfile.write(f"{id},Logged In,0\n")
            handle_actions(id, actions, delay)
            print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
        else:
            mf.encode_message("\nACCESS DENIED: Another user with same ID already logged in with different password...\n",conn)
    remove_conn_details(id)
    with open("logfile.txt", "a") as logfile:
        logfile.write(f"{id},Logged Out,0\n")
    print(current_id_total)

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
    open("logfile.txt", "w").close() # Clear logfile contents from last session
    with open("logfile.txt", "a") as logfile:
        logfile.write("ID:,Action:,Counter Value:\n") # Add header
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start_server()
