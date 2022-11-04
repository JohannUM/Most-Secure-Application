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

def send_encrypted(msg, conn, key):
    encrypted_msg = ""
    for c in msg:
        encrypted_msg += chr(ord(c) + key)
    encrypted_msg = encrypted_msg.encode(FORMAT)
    length = str(len(encrypted_msg)).encode(FORMAT)
    length += b' ' * (HEADER - len(length))
    conn.send(length)
    conn.send(encrypted_msg)

def decrypt_receive(conn, key):
    length = conn.recv(HEADER).decode(FORMAT)
    encrypted_msg = ""
    decrypted_msg = ""
    if length:
        length = int(length)
        encrypted_msg = conn.recv(length).decode(FORMAT)
    for c in encrypted_msg:
        decrypted_msg += chr(ord(c) - key)
    return decrypted_msg
    