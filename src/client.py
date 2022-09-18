import json
import socket
import sys

PORT = 5050
SERVER = "192.168.0.100"
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT = "Sock It"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


# sends a message to the server
def send_message(message):
    msg = message.encode(FORMAT)
    msg_length = str(len(msg)).encode(FORMAT)
    msg_length += b" " * (HEADER - len(msg_length))
    client.send(msg_length)
    client.send(msg)
    print(client.recv(128).decode(FORMAT))


# collects input that client enters by hand
def collect_client_input():
    id = input("Enter your ID: ")
    password = input("Enter your password: ")
    actions = []
    print("Enter your actions (Q to end): ")
    while True:
        action = input()
        if action == "Q":
            break
        actions.append(action)
    delay = int(input("Enter the dealy between actions: "))

    data = {"id":id, "password":password, "server":{"ip":SERVER, "port":PORT}, "actions":{"delay":delay, "steps":actions}}
    return json.dumps(data)


# collects input that client enters by providing a json file
def collect_client_file():
    file = open("../data/"+input("Enter filename: ")) # TODO check for valid file that follows the format given
    data = json.load(file)
    file.close()
    return json.dumps(data)
    

input_choice = input("How would you like to input your data?\n [1] by hand\n [2] JSON file\n")
if input_choice == "1":
    json_data = collect_client_input()
elif input_choice == "2":
    json_data = collect_client_file()
else:
    pass # TODO what do we want to do in this case? close the program?


send_message(json_data)
send_message(DISCONNECT)
