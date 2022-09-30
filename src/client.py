from cryptography.fernet import Fernet as fern
from required import messageFormating as mf
from schema import Schema, Use, SchemaError
from random import randint
import ipaddress
import socket
import base64
import json


# The correct schema of the json data
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


def validate_input(json_str: str):
    """Validates the input by the user. Checks if json format is correct and if the ip and the port have the correct format

    Args:
        json_str (str): The JSON data as a string

    Returns:
        bool: True if format is correct, False if not
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

    # check if [ip] is in correct format
    try:
        ipaddress.ip_address(json_dict['server']['ip'])
    except ValueError:
        return False

    # check if [port] is in correct format
    if 1 <= int(json_dict['server']['port']) <= 65535:
        pass
    else:
        return False

    return True


def connect(json_str: str):
    """ Connects the client to the server

    Args:
        json_str (str): The JSON data formatted as a string

    Returns:
        bool: True if connection was successful, False if not
    """
    if validate_input(json_str):
        json_dict = json.loads(json_str)
        try:
            client.connect((json_dict['server']['ip'], int(json_dict['server']['port'])))
            global key
            key = exchange_key()
        except (TimeoutError, ConnectionRefusedError):
            print("Incorrect server ip and/or port, please try again.\n")
            return False
        return True
    else:
        print("Incorrect data and/or data format, please try again.\n")
        return False


def exchange_key():
    """ Performs a Diffie Hellman key exchange with the server

    Returns:
        key: The fernet key
    """
    public_key = (G**PRIVATE_VALUE) % P  # Create the public part to be exchanged.
    mf.encode_message(str(public_key), client)  # Send to server.
    server_public_key = int(mf.decode_message(client))  # Receive public part from server.
    private_key = (server_public_key**PRIVATE_VALUE) % P  # Create the private key using public server part and private value.
    return fern(base64.urlsafe_b64encode(private_key.to_bytes(32, byteorder="big")))  # Return a fernet key generated from the private key.


def send_message(message: str):
    """Sends a provided message to the server

    Args:
        message (str): The JSON data formatted as a string
    """
    mf.encode_message(message, client)
    print(mf.decode_message(client))


def send_message_encrypt(message: str):
    """ Sends a provided message encrypted to the server and receives an answer

    Args:
        message (str): The JSON data formatted as a string
    """

    mf.encrypt_send(message, client, key)
    print(mf.receive_decrypt(client, key))


def collect_client_input():
    """ Collect input from the client using the terminal and formats it to json

    Returns:
        str: A JSON file formatted as a string
    """

    id = input("Enter your ID: ")
    password = input("Enter your password: ")
    server = input("Enter the server IP: ")
    port = input("Enter the server port: ")
    actions = []
    print("Enter your actions (q to quit): ")
    while True:
        action = input()
        if action == "q":
            break
        actions.append(action)
    delay = input("Enter the delay between actions: ")

    data = {
        "id": str(id),
        "password": str(password),
        "server": {
            "ip": str(server),
            "port": str(port)
        },
        "actions": {
            "delay": str(delay),
            "steps": actions
        }
    }
    return json.dumps(data)


def collect_client_file():
    """ Loads a JSON file if provided with a correct directory and file type

    Returns:
        str: A JSON file formatted as a string
    """

    while True:
        file_name = input("Enter filename: ")
        try:
            file = open("../data/" + file_name)
            try:
                data = json.load(file)
                file.close()
                break
            except json.decoder.JSONDecodeError:
                print(f"data/{file_name} cannot be read. It seems to not follow the JSON structure. Please try again.")
                file.close()
        except FileNotFoundError:
            print(f"data/{file_name} does not exist. Please try again.")
    return json.dumps(data)


def choice(connected: bool):
    """ Presents the user with 3 possible choices: 
        - Sending a message to the server using the terminal
        - Sending a message to the server providing a json file
        - Quit

    Args:
        connected (bool): True if connection was already established

    Returns:
        bool: True if connection could be established, False if not
    """

    input_choice = input("How would you like to input your data?\n [1] by hand\n [2] JSON file\n [0] to quit\n")
    if input_choice == "0":
        pass
    elif input_choice == "1":
        json_data = collect_client_input()
        if connect(json_data):
            send_message_encrypt(json_data)
            connected = True
        else:
            choice(False)
    elif input_choice == "2":
        json_data = collect_client_file()
        if connect(json_data):
            send_message_encrypt(json_data)
            connected = True
        else:
            choice(False)
    else:
        print(f"{input_choice} is not 0/1/2, try again!")
        choice(False)
    return connected


if __name__ == "__main__":
    # objects    
    DISCONNECT = "Sock It"
    PRIVATE_VALUE = randint(1, 10000) # Private value, random for every new client
    G = 6143 # Public values
    P = 7919
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get input from user, validate the address and send the message as a json
    connected = choice(False)

    # If the client was able to establish a connection send the disconnect message to the server
    if connected:
        mf.encrypt_send(DISCONNECT, client, key)


