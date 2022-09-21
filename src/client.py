from required import messageFormating as mf
from required import validation as val
import socket
import json

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT = "Sock It"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


# sends a message to the server
def send_message(message):
    mf.encode_message(message, client)
    print(mf.decode_message(client))


# collects input that client enters by hand
def collect_client_input():
    id = input("Enter your ID: ")
    password = input("Enter your password: ")
    actions = []
    print("Enter your actions (q to quit): ")
    while True:
        action = str(input())
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
    file = open("../data/" + input("Enter filename: "))  # TODO check for valid file that follows the format given
    data = json.load(file)
    file.close()
    return json.dumps(data)


while True:
    input_choice = int(input("How would you like to input your data?\n [1] by hand\n [2] JSON file\n [0] to quit\n"))
    if input_choice == 0:
        send_message(DISCONNECT)
        break
    elif input_choice == 1:
        json_data = collect_client_input()
        if val.validate(json_data):
            send_message(json_data)
        else:
            print("Incorrect data format, please try again.")
    elif input_choice == 2:
        json_data = collect_client_file()
        if val.validate(json_data):
            send_message(json_data)
        else:
            print("Incorrect data format, please try again.")
    else:
        print(f"{input_choice}, is not either 0/1/2, try again or press 0 to quit: ")
