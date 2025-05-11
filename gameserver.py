import socket
import sys
import struct
import threading
import pygame
import random
import time

random.seed(time.time())

def client_pos(sock_conn, sock_addr, client_num, clients_dict, hooky_lock):
    print(f"Client {client_num}")
    print(f"connected by {sock_addr}")

    sock_conn.sendall(struct.pack("!f", float(client_num))) #send player number to cur client
    
    while (True):

        client_mouse_x = sock_conn.recv(4)
        client_mouse_y = sock_conn.recv(4)

        client_mouse_press = sock_conn.recv(1)

        client_data_posx = sock_conn.recv(4)
        client_data_posy = sock_conn.recv(4)

        client_arm_angle = sock_conn.recv(4)
        client_arm_pivotx = sock_conn.recv(4)
        client_arm_pivoty = sock_conn.recv(4)
        client_arm_inc_num = sock_conn.recv(4)

        client_offsetx = sock_conn.recv(4)
        client_offsety = sock_conn.recv(4)

        client_camera_off = sock_conn.recv(1)

        if (not client_mouse_x):
            break

        mousex = struct.unpack("!f", client_mouse_x)
        mousey = struct.unpack("!f", client_mouse_y)

        mouse_press = struct.unpack("!B", client_mouse_press)

        rect_x = struct.unpack("!f", client_data_posx)
        rect_y = struct.unpack("!f", client_data_posy)

        arm_angle = struct.unpack("!f", client_arm_angle)
        arm_pivotx = struct.unpack("!f", client_arm_pivotx)
        arm_pivoty = struct.unpack("!f", client_arm_pivoty)
        arm_inc_num = struct.unpack("!f", client_arm_inc_num)

        offsetx = struct.unpack("!f", client_offsetx)
        offsety = struct.unpack("!f", client_offsety)

        camera_off = struct.unpack("!B", client_camera_off)

        #if (client_num == 1 and camera_off[0] == 0):
        #    clients_dict["hooky"] = random.randrange(200, 500)
        #elif (client_num == 2 and camera_off[0] == 0):
        #    clients_dict["hooky"] = random.randrange(200, 500)


        if (client_num == 1):
            clients_dict["mouse_posx"][0] = mousex[0]
            clients_dict["mouse_posy"][0] = mousey[0]

            clients_dict["mouse_click"][0] = client_mouse_press[0]

            clients_dict["player_posx"][0] = rect_x[0]
            clients_dict["player_posy"][0] = rect_y[0]

            clients_dict["angle"][0] = arm_angle[0]
            clients_dict["pivotx"][0] = arm_pivotx[0]
            clients_dict["pivoty"][0] = arm_pivoty[0]
            clients_dict["inc_num"][0] = arm_inc_num[0]

            clients_dict["offsetx"][0] = offsetx[0]
            clients_dict["offsety"][0] = offsety[0]

        elif (client_num == 2):
            clients_dict["mouse_posx"][1] = mousex[0]
            clients_dict["mouse_posy"][1] = mousey[0]

            clients_dict["mouse_click"][1] = client_mouse_press[0]

            clients_dict["player_posx"][1] = rect_x[0]
            clients_dict["player_posy"][1] = rect_y[0]

            clients_dict["angle"][1] = arm_angle[0]
            clients_dict["pivotx"][1] = arm_pivotx[0]
            clients_dict["pivoty"][1] = arm_pivoty[0]
            clients_dict["inc_num"][1] = arm_inc_num[0]

            clients_dict["offsetx"][1] = offsetx[0]
            clients_dict["offsety"][1] = offsety[0]


        print(f"Received from clients: {clients_dict['player_posx']}")

        if (client_num == 1):
            sock_conn.sendall(struct.pack("!f", float(clients_dict["mouse_posx"][1])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["mouse_posy"][1])))

            sock_conn.sendall(struct.pack("!B", clients_dict["mouse_click"][1]))

            sock_conn.sendall(struct.pack("!f", float(clients_dict["player_posx"][1])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["player_posy"][1])))

            sock_conn.sendall(struct.pack("!f", float(clients_dict["angle"][1])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["pivotx"][1])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["pivoty"][1])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["inc_num"][1])))

            sock_conn.sendall(struct.pack("!f", float(clients_dict["offsetx"][1])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["offsety"][1])))


        elif (client_num == 2):
            sock_conn.sendall(struct.pack("!f", float(clients_dict["mouse_posx"][0])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["mouse_posy"][0])))

            sock_conn.sendall(struct.pack("!B", clients_dict["mouse_click"][0]))

            sock_conn.sendall(struct.pack("!f", float(clients_dict["player_posx"][0])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["player_posy"][0])))

            sock_conn.sendall(struct.pack("!f", float(clients_dict["angle"][0])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["pivotx"][0])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["pivoty"][0])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["inc_num"][0])))

            sock_conn.sendall(struct.pack("!f", float(clients_dict["offsetx"][0])))
            sock_conn.sendall(struct.pack("!f", float(clients_dict["offsety"][0])))

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

            player_thread = threading.Thread(target=client_pos, args=(sock_conn, sock_addr, client_num, clients_dict, hooky_lock), daemon=True)
            player_thread.start()

            client_num += 1
    except KeyboardInterrupt:
        print("Server closing..")
    finally:
        server_sock.close()

if __name__ == "__main__":
    main()
