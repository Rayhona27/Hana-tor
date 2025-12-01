#!/usr/bin/env python3
import threading
import socket
import signal
import sys
import time
import queue
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
from stem.control import Controller
import stem.process
import socks
from cryptography.hazmat.primitives import serialization
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


LOCAL_ADDR = "127.0.0.1"
LOCAL_PORT = 12345
SOCKS_HOST = "127.0.0.1"
SOCKS_PORT = 9050
CONTROL_PORT = 9051
srv_socket = None
tor_process = None
controller = None
hs = None


connections_lock = threading.Lock()
connections = []
recv_threads = []
send_queue = queue.Queue()


def launch_tor_and_hidden_service(local_port=LOCAL_PORT):
    global tor_process, controller, hs
    print("[*] Launching Tor...")
    tor_process = stem.process.launch_tor_with_config(
        config={"SocksPort": str(SOCKS_PORT), "ControlPort": str(CONTROL_PORT)},
        init_msg_handler=lambda m: print("[tor] " + m.strip()),
    )
    controller = Controller.from_port(port=CONTROL_PORT)
    controller.authenticate()
    print("[*] Creating ephemeral hidden service (awaiting publication)")
    hs = controller.create_ephemeral_hidden_service(
        {LOCAL_PORT: local_port}, await_publication=True
    )
    onion = f"{hs.service_id}.onion"
    print(f"[+] Hidden service created: {onion}")
    return onion


def start_listener(local_addr=LOCAL_ADDR, local_port=LOCAL_PORT):
    global srv_socket
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.bind((local_addr, local_port))
    srv_socket.listen()
    print(f"[+] Listening locally on {local_addr}:{local_port}")
    t = threading.Thread(target=_accept_loop, daemon=True)
    t.start()
    return srv_socket


def _accept_loop():
    while True:
        try:
            conn, addr = srv_socket.accept()
        except OSError:
            break
        peer_name = f"{addr[0]}:{addr[1]}"
        print(f"\n[!] Incoming connection from {peer_name}")
        _register_connection(conn, peer_name)


def _register_connection(sock, peer_name):
    with connections_lock:
        connections.append((sock, peer_name))
    t = threading.Thread(target=_recv_loop, args=(sock, peer_name), daemon=True)
    recv_threads.append(t)
    t.start()


def _recv_loop(sock, peer_name):
    try:
        global keys
        private_key=keys[0]
        while True:
            data = sock.recv(4096)
            if not data:
                print(f"\n[-] {peer_name} disconnected")
                break
            try:
                decrypted_message=private_key.decrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA512()),algorithm=hashes.SHA512(),label=None))
                decrypted_message = decrypted_message.decode(errors="replace")
            except Exception:
                text = "<binary data>"
            print(f"\n[{peer_name}] {decrypted_message}")
    except Exception as e:
        print(f"\n[!] Error on recv from {peer_name}: {e}")
    finally:
        _unregister_and_close(sock)


def _unregister_and_close(sock):
    with connections_lock:
        for i, (s, name) in enumerate(connections):
            if s is sock:
                connections.pop(i)
                break
    try:
        sock.close()
    except Exception:
        pass


def connect_to_onion(onion_addr, port=LOCAL_PORT, timeout=60):
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, SOCKS_HOST, SOCKS_PORT, rdns=True)
    s.settimeout(timeout)
    print(f"[*] Connecting to {onion_addr}:{port} via Tor SOCKS5...")
    s.connect((onion_addr, port))
    s.settimeout(None)
    peer_name = f"{onion_addr}:{port}"
    print(f"[+] Connected to {peer_name}")
    _register_connection(s, peer_name)
    return s


def user_input_loop():
    global keys
    public_key=keys[1]
    print("\nCommands:\n  /connect <peer.onion>\n  /list\n  /quit\nType message to send to connected peers.\n")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            line = "/quit"
        if not line:
            continue
        if line.startswith("/connect "):
            _, onion = line.split(" ", 1)
            onion = onion.strip()
            if not onion.endswith(".onion"):
                print("[!] Invalid onion address (must end with .onion)")
                continue
            try:
                connect_to_onion(onion)
            except Exception as e:
                print(f"[!] Could not connect to {onion}: {e}")
            continue
        if line == "/list":
            with connections_lock:
                if not connections:
                    print("[*] No active connections")
                else:
                    print("[*] Active connections:")
                    for _, name in connections:
                        print("  -", name)
            continue
        if line == "/quit":
            print("[*] Quitting...")
            shutdown(0, 0)
            return
        with connections_lock:
            if not connections:
                print("[!] No connected peers to send to. Use /connect <peer.onion>")
                continue
            payload = (line + "\n").encode("utf-8")
            encrypted=public_key.encrypt(payload,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA512()),algorithm=hashes.SHA512(),label=None))
            dead = []
            for s, name in list(connections):
                try:
                    s.sendall(encrypted)
                except Exception as e:
                    print(f"[!] Failed to send to {name}: {e}")
                    dead.append(s)
            for ds in dead:
                _unregister_and_close(ds)


def shutdown(sig, frame):
    global srv_socket, controller, hs, tor_process
    print("\n[*] Shutting down...")
    try:
        if srv_socket:
            srv_socket.close()
    except Exception:
        pass
    with connections_lock:
        for s, _ in list(connections):
            try:
                s.close()
            except Exception:
                pass
        connections.clear()
    try:
        if controller and hs:
            controller.remove_hidden_service(hs.service_id)
            print("[*] Hidden service removed.")
    except Exception as e:
        print("[!] Could not remove hidden service:", e)
    try:
        if tor_process:
            tor_process.terminate()
            tor_process.wait()
    except Exception:
        pass
    print("[*] Cleanup done. Exiting.")
    sys.exit(0)



encryption()
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)
onion_addr = launch_tor_and_hidden_service()
start_listener()
print("\n[*] Share this onion address with your peer:")
print("    ", onion_addr)
user_input_loop()
