from cryptography.fernet import Fernet as fern
from required import messageFormating as mf
from required import validation as val
from random import randint
import socket
import base64
import json

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT = "Sock It"
PRIVATE_VALUE = randint(1, 10000) # Private value, random for every new client
G = 6143 # Public values
P = 7919

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def exchange_key():
    public_key = (G**PRIVATE_VALUE) % P
    mf.encode_message(str(public_key), client)
    server_public_key = int(mf.decode_message(client))
    private_key = (server_public_key**PRIVATE_VALUE) % P
    return private_key

key = exchange_key()
f_key = fern(base64.urlsafe_b64encode((key).to_bytes(32, byteorder="big"))) # add to message formatting, to allow for sending encrypted messages

# sends a message to the server
def send_message(message):
    #msg = f_key.encrypt(message.encode())
    mf.encode_message(message, client)
    print(mf.decode_message(client))

# collects input that client enters by hand
def collect_client_input():
    id = input("Enter your ID: ")
    password = input("Enter your password: ")
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
            "ip": str(SERVER),
            "port": str(PORT)
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

while True:
    input_choice = input("How would you like to input your data?\n [1] by hand\n [2] JSON file\n [0] to quit\n")
    if input_choice == "0":
        send_message(DISCONNECT)
        break
    elif input_choice == "1":
        json_data = collect_client_input()
        if val.validate(json_data):
            send_message(json_data)
        else:
            print("Incorrect data format, please try again.\n")
    elif input_choice == "2":
        json_data = collect_client_file()
        if val.validate(json_data):
            send_message(json_data)
        else:
            print("Incorrect data format, please try again.\n")
    else:
        print(f"{input_choice}, is not either 0/1/2, try again.\n")
