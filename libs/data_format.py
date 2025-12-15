import hashlib
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import base64
import json
import random

def encrypt_blob(data: str, key: str) -> str:
    nonce = "".join([random.choice("AZERTYUIOPMLKJHGFDSQWXCVBN!?%azertyuiopmlkjhgfdsqwxcvbn1234567890") for _ in range(10)])
    data = data.encode()
    key = (key+nonce).encode()
    out = bytearray(len(data))
    for i, b in enumerate(data):
        out[i] = b ^ key[i % len(key)]
    return nonce,base64.b64encode(bytes(out)).decode()

def decrypt_blob(key:str, data: str, nonce: str) -> str:
    data = base64.b64decode(data.encode())
    key = (key+nonce).encode()
    out = bytearray(len(data))
    for i, b in enumerate(data):
        out[i] = b ^ key[i % len(key)]
    output = json.loads(out.decode())
    return output

def encrypt_blob_old(blob:str,encryption_key:str)->tuple:
    m = hashlib.sha256()
    m.update(encryption_key.encode())
    hashed_password = m.digest()
    cipher = ChaCha20.new(key=hashed_password)
    ciphertext = cipher.encrypt(blob.encode())
    nonce = base64.b64encode(cipher.nonce).decode("utf-8")
    ct = base64.b64encode(ciphertext).decode("utf-8")
    return nonce,ct

def decrypt_blob_old(password:str,blob:str,nonce:str):
    m = hashlib.sha256()
    m.update(password.encode())
    hashed_password = m.digest()
    nonce = base64.b64decode(nonce)
    ct = base64.b64decode(blob)
    cipher = ChaCha20.new(key=hashed_password, nonce=nonce)
    plaintext = cipher.decrypt(ct)
    decrypted_blob = json.loads(plaintext)
    return decrypted_blob


def format_command_to_send(command:str,command_id:str,sleep_time:float,encryption_key:str,stage:str)->str:
    content_payload = {"id":command_id,"payload":command.encode().decode(),"sleep_next":sleep_time}
    nonce,encrypted_payload_content = encrypt_blob(json.dumps(content_payload),encryption_key)
    final_payload = base64.b64encode(json.dumps({"stage":stage,"payload":encrypted_payload_content,"type":"command","nonce":str(nonce)}).encode()).decode()
    return final_payload

def generate_id(agent_name:str)->str:
    m = hashlib.sha256()
    m.update(agent_name.encode())
    hashed_password = m.hexdigest()
    id = "".join([random.choice("azertuiopqsdfghjklmwx1234567890cvbn") for _ in range(5)])+hashed_password[:5]+"".join([random.choice("azer1234567890tuiopqsdfghjklmwxcvbn") for _ in range(5)])
    return id
