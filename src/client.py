from required import messageFormating as mf
import socket
import json

PORT = 5050
SERVER = "192.168.0.100"
ADDR = (SERVER, PORT)
DISCONNECT = "Sock It"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send_message(message):
    mf.encode_message(message, client)
    print(mf.decode_message(client))

while True:
    choice = int(input("Would you like to input json format or create json format step by step? (1/2, 0 to quit): "))
    if choice == 0:
        break
    elif choice == 1:
        while True:
            jsonString = input("Enter json formatted string, press q to quit: ")
            if jsonString == "q":
                send_message(DISCONNECT)
                break
            else:
                send_message(jsonString)
    elif choice == 2:
        id = input("Enter your ID: ")
        password = input("Enter your password: ")
        actions = []
        print("Enter your actions (q to quit): ")
        while True:
            action = input()
            if action == "q":
                break
            actions.append(action)
        delay = int(input("Enter the dealy between actions: "))
        data = {"id":id, "password":password, "server":{"ip":SERVER, "port":PORT}, "actions":{"delay":delay, "steps":actions}}
        json_data = json.dumps(data)
        send_message(json_data)
    else:
        print(f"{choice}, is not either 1/2, try again or press 0 to quit: ")
