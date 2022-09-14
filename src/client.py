from ctypes import FormatError
import socket

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
    
input = str(input())
send_message(input)
send_message(DISCONNECT)
