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

def send_message(message):
    msg = message.encode(FORMAT)
    msg_length = str(len(msg)).encode(FORMAT)
    msg_length += b" " * (HEADER - len(msg_length))
    client.send(msg_length)
    client.send(msg)
    print(client.recv(16).decode(FORMAT))
    password = input(client.recv(28).decode(FORMAT))
    pSend = password.encode(FORMAT)
    pLength = str(len(pSend)).encode(FORMAT)
    pLength += b" " * (HEADER - len(pLength))
    client.send(pLength)
    client.send(pSend)
    
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
