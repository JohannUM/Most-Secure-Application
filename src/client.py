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
    delay = int(input("Enter the dealy between actions: "))

    data = {"id":id, "password":password, "server":{"ip":SERVER, "port":PORT}, "actions":{"delay":delay, "steps":actions}}
    return json.dumps(data)


# collects input that client enters by providing a json file
def collect_client_file():
    file = open("../data/"+input("Enter filename: ")) # TODO check for valid file that follows the format given
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
        send_message(json_data)
    elif input_choice == 2:
        json_data = collect_client_file()
        send_message(json_data)
    else:
         print(f"{input_choice}, is not either 0/1/2, try again or press 0 to quit: ")
