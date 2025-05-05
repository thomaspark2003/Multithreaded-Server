import socket
import sys
import struct

def main():

    port = 8080

    server = socket.gethostbyname(socket.gethostname())

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("localhost", port))
    server_sock.listen(2)

    sock_conn, sock_addr = server_sock.accept()
    print(f"connected by {sock_addr}")

    while(True):
        client_data = sock_conn.recv(1024)
        test_rect_x = struct.unpack("!f", client_data)
        print(f"Received from client: {test_rect_x[0]}")
        if (not client_data):
            break

    sock_conn.close()


if __name__ == "__main__":
    main()
