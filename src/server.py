from cryptography.fernet import Fernet as fern
from required import messageFormating as mf
from schema import Schema, Use, SchemaError
from random import randint
import socket
import threading
import base64
import json
import time
import re

SCHEMA = Schema({
    'id': str,
    'password': str,
    'server': {
        'ip': str,
        'port': Use(int),
    },
    'actions': {
        'delay': Use(int),
        'steps': list
    }
})


def validate_actions(json_str: str):
    """ Validates the data that was sent to the server. Checks especially if the actions are in the right format

    Args:
        json_str (str): The Json data as a string

    Returns:
        bool: True if the data is valid, False if not
    """
    # check if json_str can be converted to dictionary data type
    try:
        json_dict = json.loads(json_str)
    except json.decoder.JSONDecodeError:
        return False

    # check if json_dict follows SCHEMA
    try:
        SCHEMA.validate(json_dict)
    except SchemaError:
        return False

    # check if [steps] are in correct format
    for step in json_dict['actions']['steps']:
        try:
            if re.compile('INCREASE \\d').match(step) is None and re.compile('DECREASE \\d').match(step) is None:
                return False
        except TypeError:
            return False

    return True


def exchange_key(conn):
    """Performs a Diffie Hellman key exchange

    Args:
        conn (socket): The socket that tries to connect

    Returns:
        key: The fernet key
    """
    public_key = (G ** PRIVATE_VALUE) % P  # Create the public part to be exchanged.
    mf.encode_message(str(public_key), conn)  # Send to client.
    server_public_key = int(mf.decode_message(conn))  # Receive public part from client.
    private_key = (server_public_key ** PRIVATE_VALUE) % P  # Create the private key using public client part and private value.
    return fern(base64.urlsafe_b64encode(private_key.to_bytes(32, byteorder="big")))  # Return a fernet key generated from the private key.


def handle_actions(id: str, actions: list, delay: int):
    """ Handles the actions specified in the json file from the client and operates on the specific counter

    Args:
        id (str): The id of the client
        actions (str): The actions that the client wants to perform. E.g. "Increase 5"
        delay (int): The delay between 2 actions
    """
    i = 0
    final = len(actions)
    for action in actions:
        if "INCREASE" in action:
            amount = [int(s) for s in action.split() if s.isdigit()]
            with conn_details_lock:
                current_connection_counters[id] += amount[0]
                with open("logfile.txt", "a") as logfile:
                    logfile.write(f"{id}\t\tINCREASE {amount[0]}\t\t{current_connection_counters[id]}\n")
                print(f"Increase by {amount[0]} and counter for id - {id} is now: {current_connection_counters[id]}")
        elif "DECREASE" in action:
            amount = [int(s) for s in action.split() if s.isdigit()]
            with conn_details_lock:
                current_connection_counters[id] -= amount[0]
                with open("logfile.txt", "a") as logfile:
                    logfile.write(f"{id}\t\tDECREASE {amount[0]}\t\t{current_connection_counters[id]}\n")
                print(f"Decrease by {amount[0]} and counter for id - {id} is now: {current_connection_counters[id]}")
        i += 1
        if i < final:
            if delay > 1000000: # Stop conversion error with big delays
                delay = 1000000
            time.sleep(delay)


def handle_json(msg: str, conn):
    """ Handles the file that was sent by the client.

    Args:
        msg (str): The message that the client sent
        conn (socket): The socket of the client
    """
    data = json.loads(msg)
    id = data["id"]
    password = data["password"]
    actions = data["actions"]["steps"]
    delay = int(data["actions"]["delay"])

    if id not in current_connection_passwords:
        with id_total_lock:
            current_id_total[id] = 1
        # print(current_id_total)
        add_conn_details(id, password)
        with open("logfile.txt", "a") as logfile:
            logfile.write(f"{id}\t\tLogged In\t\t{current_connection_counters[id]}\n")
        handle_actions(id, actions, delay)
        # print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
    else:
        if check_password(current_connection_passwords[id], password):
            with id_total_lock:
                current_id_total[id] += 1
            # print(current_id_total)
            with open("logfile.txt", "a") as logfile:
                logfile.write(f"{id}\t\tLogged In\t\t{current_connection_counters[id]}\n")
            handle_actions(id, actions, delay)
            # print(f"ID : {id}\nPASSWORD : {password}\nACTIONS : {actions}\nDELAY : {delay}")
        else:
            mf.encode_message(
                "\nACCESS DENIED: Another user with same ID already logged in with different password...\n", conn)

    with open("logfile.txt", "a") as logfile:
        logfile.write(f"{id}\t\tLogged Out\t\t{current_connection_counters[id]}\n")
    remove_conn_details(id)


def add_conn_details(id: str, password: str):
    """ Updates the dictionaries with the details of a new client

    Args:
        id (str): The id of the client
        password (str): The password of the client
    """
    current_connection_passwords[id] = password
    current_connection_counters[id] = 0


def remove_conn_details(id: str):
    """ Removes the details of a client once it disconnects

    Args:
        id (str): The id of the client
    """
    global current_id_total
    with id_total_lock:
        if current_id_total[id]:
            if current_id_total[id] > 1:
                current_id_total[id] -= 1
            elif current_id_total[id] == 1:
                current_id_total.pop(id)
                current_connection_counters.pop(id)
                current_connection_passwords.pop(id)


def check_password(password1: str, password2: str):
    """ Checks if two passwords are matching

    Args:
        password1 (str): The first password
        password2 (str): The second password

    Returns:
        bool: True if passwords match, False if not
    """
    return password1 == password2


def handle_client(conn, addr):
    """ Handles a client once it connects to the server. Each instance of this function is run in a different thread.

    Args:
        conn (socket): The socket of the client
        addr (tuple): The address details of the client
    """

    key = exchange_key(conn)
    print(f"\nNew Connection {addr}\n")
    while True:
        message = mf.receive_decrypt(conn, key)
        if message == DISCONNECT:
            break
        elif message != "":
            # print(f"{addr}: {message}")
            if validate_actions(message):
                handle_json(message, conn)
                mf.encrypt_send("Message Received!", conn, key)
            else:
                mf.encrypt_send("Incorrect data and/or data format, please try again.", conn, key)
    print(f"\nConnection closed {addr}\n")
    conn.close()


def start_server():
    """ Starts the server
    """

    server.listen()
    print(f"Server [{SERVER}:{PORT}] started.")
    open("logfile.txt", "w").close()  # Clear logfile contents from last session
    with open("logfile.txt", "a") as logfile:
        logfile.write("ID\t\t\tAction\t\t\tCounter Value:\n")  # Add header
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    PORT = 5050
    SERVER = "127.0.0.1"
    ADDR = (SERVER, PORT)
    DISCONNECT = "Sock It"
    PRIVATE_VALUE = randint(1, 10000)  # Private value, random for every new client
    G = 6143  # Public values
    P = 7919

    current_connection_passwords = {}
    current_connection_counters = {}
    current_id_total = {}

    conn_details_lock = threading.Lock()
    id_total_lock = threading.Lock()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    start_server()
