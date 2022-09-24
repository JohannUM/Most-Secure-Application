from cryptography.fernet import Fernet as fern
from required import messageFormating as mf
from required import validation as val
from random import randint
import socket
import base64
import json


DISCONNECT = "Sock It"
PRIVATE_VALUE = randint(1, 10000) # Private value, random for every new client
G = 6143 # Public values
P = 7919

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def connect(json_str):
    if val.validate(json_str):
        json_dict = json.loads(json_str)
        try:
            client.connect((json_dict['server']['ip'], int(json_dict['server']['port'])))
            global key 
            key = exchange_key()
        except TimeoutError:
            print("Incorrect server ip and/or port, please try again.\n")
            return False
        return True
    else:
        print("Incorrect data and/or data format, please try again.\n")
        return False

def exchange_key():
    public_key = (G**PRIVATE_VALUE) % P
    mf.encode_message(str(public_key), client)
    server_public_key = int(mf.decode_message(client))
    private_key = (server_public_key**PRIVATE_VALUE) % P
    return fern(base64.urlsafe_b64encode((private_key).to_bytes(32, byteorder="big"))) # add to message formatting, to allow for sending encrypted messages

# sends a message to the server
def send_message(message):
    mf.encode_message(message, client)
    print(mf.decode_message(client))

def send_message_encrypt(message):
    mf.encrypt_send(message, client, key)
    print(mf.receive_decrypt(client, key))

# collects input that client enters by hand
def collect_client_input():
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


# collects input that client enters by providing a json file
def collect_client_file():
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

connected = False
def choice(connected):
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

connected = choice(connected)

if connected:
    mf.encrypt_send(DISCONNECT, client, key) # Makes it super clean and avoids any potential errors waiting!
