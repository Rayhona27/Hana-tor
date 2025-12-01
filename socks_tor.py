import socks
import socket
import threading
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
keys = []

def encryption():
    global keys
    temp = input("Do you have an asymmetric key pair? [y/N]: ").strip().lower()
    if temp == 'y':
        private_pem_file = input("Enter file containing your Private Key in PEM format:\n")
        with open(private_pem_file, "rb") as f:
            private_pem = f.read()
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=None
        )
        peer_public_pem_file = input("Enter .txt file where you saved the other person's Public PEM:\n")
        with open(peer_public_pem_file, "rb") as f:
            peer_public_pem = f.read()
        peer_public_key = serialization.load_pem_public_key(peer_public_pem)
        keys.append(private_key)
        keys.append(peer_public_key)
        return
    elif temp == 'n':
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        print("\nYour Public Key:\n")
        print(public_pem.decode())
        print("\nSave this Public Key in a text file and share it.\n")
        peer_public_pem_file = input("Enter .txt file where you saved the other person's Public PEM:\n")
        with open(peer_public_pem_file, "rb") as f:
            peer_public_pem = f.read()
        peer_public_key = serialization.load_pem_public_key(peer_public_pem)
        keys.append(private_key)
        keys.append(peer_public_key)
        return
    else:
        print("Stopping service...")
        exit()


encryption()
s = socks.socksocket()
s.set_proxy(socks.SOCKS5, "127.0.0.1", 9050, rdns=True)
p = input("Enter the tor .onion address of the other person: ").strip()
if not p.endswith(".onion"):
    p += ".onion"
s.connect((p, 12345))


def receiver(sock):
    global keys
    private_key=keys[0]
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[Disconnected from peer]")
                break
            decrypted_message=private_key.decrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA512()),algorithm=hashes.SHA512(),label=None))
            decrypted_message = decrypted_message.decode(errors="replace")
            print(decrypted_message)
        except Exception as e:
            print("\n[Receiver error]:", e)
            break


threading.Thread(target=receiver, args=(s,), daemon=True).start()
while True:
    public_key=keys[1]
    try:
        msg = input("> ")
        payload = (msg + "\n").encode("utf-8")
        encrypted=public_key.encrypt(payload,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA512()),algorithm=hashes.SHA512(),label=None))
        s.sendall(encrypted)
    except KeyboardInterrupt:
        print("\n[*] Exiting...")
        s.close()
        break
