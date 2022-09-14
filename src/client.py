import json
import socket
import sys

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT = "Sock It"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send_message(message):
    msg = message.encode(FORMAT)
    msg_length = str(len(msg)).encode(FORMAT)
    msg_length += b" " * (HEADER - len(msg_length))
    client.send(msg_length)
    client.send(msg)
    print(client.recv(128).decode(FORMAT))
    
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
json_data = json.dumps(data)

send_message(json_data)
send_message(DISCONNECT)
#input = str(input())
#send_message(input)
#send_message(DISCONNECT)
