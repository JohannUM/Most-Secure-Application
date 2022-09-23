from cryptography.fernet import Fernet as fern
import sys
from required import messageFormating as mf
from required import validation as val
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
            key = exchange_key()
            f_key = fern(base64.urlsafe_b64encode((key).to_bytes(32, byteorder="big"))) # add to message formatting, to allow for sending encrypted messages
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
    return private_key

# sends a message to the server
def send_message(message):
    #msg = f_key.encrypt(message.encode())
    mf.encode_message(message, client)
    print(mf.decode_message(client))

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


input_choice = input("How would you like to input your data?\n [1] by hand\n [2] JSON file\n [0] to quit\n")
if input_choice == "0":
    pass
elif input_choice == "1":
    json_data = collect_client_input()
    if connect(json_data):
        send_message(json_data)
elif input_choice == "2":
    json_data = collect_client_file()
    if connect(json_data):
        send_message(json_data)
else:
    print(f"{input_choice}, is not either 0/1/2, try again.\n")
