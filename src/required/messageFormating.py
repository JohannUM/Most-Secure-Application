FORMAT = 'utf-8'
HEADER = 64

def encode_message(msg, conn):
    encodedMsg = msg.encode(FORMAT)
    msgLength = str(len(encodedMsg)).encode(FORMAT) # Encode length of message.
    msgLength += b' ' * (HEADER - len(msgLength)) # Pad length message to 64 bytes.
    conn.send(msgLength)
    conn.send(encodedMsg)

def decode_message(conn):
    msgLength = conn.recv(HEADER).decode(FORMAT) # Get incoming message's length.
    message = ""
    if msgLength:
        msgLength = int(msgLength)
        message = conn.recv(msgLength).decode(FORMAT) # Decode actual message.
    return message
    
def encrypt_send(msg, conn, f_key):
    encrypted = f_key.encrypt(msg)
    length = str(len(encrypted)).encode(FORMAT)
    length += b' ' * (HEADER - len(length))
    conn.send(length)
    conn.send(encrypted)

def receive_decrypt(conn, f_key):
    length = conn.recv(HEADER).decode(FORMAT)
    encryption = ""
    if length:
        length = int(length)
        encryption = conn.recv(length)
        decrypted = f_key.decrypt(encryption)
    return decrypted
