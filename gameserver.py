import socket
import sys
import struct
import threading
import pygame
import random
import time

random.seed(time.time())

def full_recv(socket, byte_stream):
    data = b''

    while (len(data) < byte_stream):
        cur_data = socket.recv(byte_stream - len(data))
        data += cur_data
    return data

def client_pos(sock_conn, sock_addr, client_num, clients_dict, hooky_lock):
    print(f"Client {client_num}")
    print(f"connected by {sock_addr}")

    sock_conn.sendall(struct.pack("!f", float(client_num))) #send player number to cur client
    
    while (True):

        pkt = full_recv(sock_conn, 42)
        unpack_pkt = struct.unpack("!ffBffffffffB", pkt)

        (client_mouse_x, client_mouse_y, client_mouse_press,
         client_data_posx, client_data_posy, client_arm_angle,
         client_arm_pivotx, client_arm_pivoty, client_arm_inc_num,
         client_offsetx, client_offsety, client_camera_off
        ) = unpack_pkt

        if (not client_mouse_x):
            break

        if (client_num == 1):
            clients_dict["mouse_posx"][0] = client_mouse_x
            clients_dict["mouse_posy"][0] = client_mouse_y

            clients_dict["mouse_click"][0] = client_mouse_press

            clients_dict["player_posx"][0] = client_data_posx
            clients_dict["player_posy"][0] = client_data_posy

            clients_dict["angle"][0] = client_arm_angle
            clients_dict["pivotx"][0] = client_arm_pivotx
            clients_dict["pivoty"][0] = client_arm_pivoty
            clients_dict["inc_num"][0] = client_arm_inc_num

            clients_dict["offsetx"][0] = client_offsetx
            clients_dict["offsety"][0] = client_offsety

        elif (client_num == 2):
            clients_dict["mouse_posx"][1] = client_mouse_x
            clients_dict["mouse_posy"][1] = client_mouse_y

            clients_dict["mouse_click"][1] = client_mouse_press

            clients_dict["player_posx"][1] = client_data_posx
            clients_dict["player_posy"][1] = client_data_posy

            clients_dict["angle"][1] = client_arm_angle
            clients_dict["pivotx"][1] = client_arm_pivotx
            clients_dict["pivoty"][1] = client_arm_pivoty
            clients_dict["inc_num"][1] = client_arm_inc_num

            clients_dict["offsetx"][1] = client_offsetx
            clients_dict["offsety"][1] = client_offsety


        print(f"Received from clients: {clients_dict['player_posx']}")

        if (client_num == 1):
            sock_conn.sendall(struct.pack("!ffBffffffff", float(clients_dict["mouse_posx"][1]), float(clients_dict["mouse_posy"][1]),
                                                                clients_dict["mouse_click"][1], float(clients_dict["player_posx"][1]),
                                                                float(clients_dict["player_posy"][1]), float(clients_dict["angle"][1]),
                                                                float(clients_dict["pivotx"][1]), float(clients_dict["pivoty"][1]),
                                                                float(clients_dict["inc_num"][1]), float(clients_dict["offsetx"][1]),
                                                                float(clients_dict["offsety"][1])
                                                                ))


        elif (client_num == 2):
            sock_conn.sendall(struct.pack("!ffBffffffff", float(clients_dict["mouse_posx"][0]), float(clients_dict["mouse_posy"][0]),
                                                                clients_dict["mouse_click"][0], float(clients_dict["player_posx"][0]),
                                                                float(clients_dict["player_posy"][0]), float(clients_dict["angle"][0]),
                                                                float(clients_dict["pivotx"][0]), float(clients_dict["pivoty"][0]),
                                                                float(clients_dict["inc_num"][0]), float(clients_dict["offsetx"][0]),
                                                                float(clients_dict["offsety"][0])
                                                                ))

        client_p2_x = sock_conn.recv(4)
        p2_x = struct.unpack("!f", client_p2_x)

        #if (rect_x[0] > p2_x[0]):
        #    clients_dict["prev_far"] = 1

        #with (hooky_lock):
        #    if (camera_off[0] == 0):
        #        clients_dict["hooky"] = random.randrange(200, 500)


        with (hooky_lock):
            sock_conn.sendall(struct.pack("!f", float(clients_dict["hooky"])))

        #if (client_num == 1 and camera_off[0] == 0):
        #    clients_dict["hooky"] = random.randrange(200, 500)
        #elif (client_num == 2 and camera_off[0] == 0):
        #    clients_dict["hooky"] = random.randrange(200, 500)
        


    sock_conn.close()

def hooky_updater(clients_dict, lock):
    while True:
        with lock:
            clients_dict["hooky"] = random.randrange(200, 500)
        time.sleep(1)

def main():

    port = 8080

    #ip = socket.gethostbyname(socket.gethostname())
    ip = "10.0.0.28"

    client_num = 1

    random.seed(time.time())
    rand_y = random.randrange(200, 500)

    clients_dict = {
        "player_posx": [768,400], 
        "player_posy": [432,432],
        "mouse_posx": [0,0],
        "mouse_posy": [0,0],
        "mouse_click": [0,0],
        "angle": [0,0],
        "pivotx": [0,0],
        "pivoty": [0,0],
        "inc_num": [0,0],
        "offsetx": [0,0],
        "offsety": [0,0],
        "hooky": rand_y,
        "prev_far": 0
        }
    
    
    pygame.init()

    desktop_info = pygame.display.Info()
    screen_width = desktop_info.current_w

    total_width = screen_width*20
    seed_num = 0

    hooky_lock = threading.Lock()


    try:

        randy_thread = threading.Thread(target=hooky_updater, args=(clients_dict, hooky_lock), daemon = True)
        randy_thread.start()


        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_sock.bind((ip, port))
        server_sock.listen(2)
        print("Waiting for connections..")

        while(True):

            sock_conn, sock_addr = server_sock.accept()
            server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)

            player_thread = threading.Thread(target=client_pos, args=(sock_conn, sock_addr, client_num, clients_dict, hooky_lock), daemon=True)
            player_thread.start()

            client_num += 1
    except KeyboardInterrupt:
        print("Server closing..")
    finally:
        server_sock.close()

if __name__ == "__main__":
    main()
