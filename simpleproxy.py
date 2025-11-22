import sys
import socket
import threading
from collections import defaultdict

#Usage: simpleproxy.py listen_ip listen_port server_ip server_port
#Simple MITM proxy for minecraft server and client
#example usage for running a server and client on the same computer
# python simpleproxy.py 127.0.0.1 25566 127.0.0.1 25565
#then use direct connect on minecraft to connect to 127.0.0.1 25566

buffer = 4096


def forward(src, dst, direction):
    """
    Contiosuly reads tcp bytes between src and dst. Prints the number of bytes forwrarded
    Runs in its own thread so data traffic can flow in both direcitons simulataneously
    """
    try:
        while True:
            data = src.recv(buffer)
            if not data:
                break
            firstBytes = data[:10].hex()
            print(f"{direction}: {len(data)} bytes | first 10 = {firstBytes}")
            dst.sendall(data)
    except ConnectionResetError:
        pass
    finally:
        try:
            src.close()
        except:
            pass
        try:
            dst.close()
        except:
            pass


def handle_client(client_socket, server_host, server_port):
    """
    Used when a new client connects to the proxy
    Creates a conneciton to the real minecraft server
    starts 2 threads
    - one for client - server packets
    - one for server - client packets
    """
    try:
        server_socket = socket.create_connection((server_host, server_port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        client_socket.close()
        return

    #start threads to forward in both directions and display direciton
    threading.Thread(
        target=forward, args=(client_socket, server_socket, "C->S"), daemon=True
    ).start()
    threading.Thread(
        target=forward, args=(server_socket, client_socket, "S->C"), daemon=True
    ).start()

def main():
    if len(sys.argv) != 5:
        sys.exit(1)

    listen_host = sys.argv[1]
    listen_port = int(sys.argv[2])
    server_host = sys.argv[3]
    server_port = int(sys.argv[4])

    #create listening socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_sock:

        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind((listen_host, listen_port))
        listen_sock.listen()

        print(f"Proxy listening on {listen_host}:{listen_port} -> {server_host}:{server_port}")

        #while socket open, listen for a new client and open a thread using client  function
        while True:
            client_sock, addr = listen_sock.accept()
            print(f"New client from {addr}")
            threading.Thread(
                target=handle_client,
                args=(client_sock, server_host, server_port),
                daemon=True,
            ).start()

if __name__ == "__main__":
    main()