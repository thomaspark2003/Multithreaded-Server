import pygame
import sys
import socket
import struct
import math
from sprites import Player
from sprites import Objects
from sprites import Camera
from sprites import GrabObject
import time
from debug import debug

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Octo Sling')

        desktop_info = pygame.display.Info()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = desktop_info.current_w, desktop_info.current_h

        self.clock = pygame.time.Clock()
        #self.game_window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.game_window = pygame.display.set_mode((1280, 720))

        self.background_img = pygame.image.load('images/background_water.png').convert()
        self.background_img = pygame.transform.scale(self.background_img, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.back_rect = self.background_img.get_rect()
        self.back_rect.topleft = (0,0)

        self.objects = Objects(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.background_img)
        self.char = Player(self.game_window, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.objects.grab_rect, self.objects.grab_mask)
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.char.rect, self.game_window, self.objects, self.char)
        
        self.running = True

        self.fall = False

        self.grab_obj = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 800)
        self.grab_obj2 = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 300)
        self.grab_obj3 = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 1300)

        #self.char2 = Player(self.game_window, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.objects.grab_rect, self.objects.grab_mask, 2)

        self.char2 = pygame.image.load('images/luffy.png')
        self.char2_rect = self.char2.get_rect()
        self.rotate_img = pygame.image.load('images/arm_prototype.png')
        self.arm_rect = self.rotate_img.get_rect()
        self.rotate_mask = pygame.mask.from_surface(self.rotate_img)
        self.rotate_mask_img = self.rotate_mask.to_surface(setcolor=(100, 156, 252), unsetcolor=(0, 0, 0, 0))

        self.store_score = 0
        self.store_high_score = 0
        self.store_cond = False
        self.prev_score = 0

        self.prev_grab_x = 0
        self.cur_grab_x = 0

        self.max_grab_x = 0

        self.dict_store_grab = {}
        self.grab_cond = True

        self.score_inc = False

        self.list_of_crab = [0,0,0]
        self.score_check = False

        #ip = socket.gethostbyname(socket.gethostname())
        self.ip = "10.0.0.28"

        self.player2_posx = 0
        self.player2_posy = 0

        self.grab_coords = [0,0]

        self.arm_pivotx = 0
        self.arm_pivoty = 0

        self.offsetx = 0
        self.offsety = 0

    def run(self):

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((self.ip, 8080))

        client_num = client_sock.recv(4)
        player_num = struct.unpack("!f", client_num)
        player_num = player_num[0] #use player_num on .move for self.char (could be 1 or 2)

        while self.running:
            mouse_key = pygame.mouse.get_pressed()
            left_key = mouse_key[0]

            mouse_posx, mouse_posy = pygame.mouse.get_pos()
            client_sock.sendall(struct.pack("!f", mouse_posx))
            client_sock.sendall(struct.pack("!f", mouse_posy))

            client_sock.sendall(struct.pack("!B", int(left_key)))

            rect_x = self.char.rect.x
            rect_y = self.char.rect.y

            client_sock.sendall(struct.pack("!f", rect_x))
            client_sock.sendall(struct.pack("!f", rect_y))

            arm_angle = self.char.angle
            client_sock.sendall(struct.pack("!f", arm_angle))
        

            if (self.char.arm_pivot != 0):
                self.arm_pivotx = self.char.arm_pivot[0]
                self.arm_pivoty = self.char.arm_pivot[1]

            client_sock.sendall(struct.pack("!f", self.arm_pivotx))

            client_sock.sendall(struct.pack("!f", self.arm_pivoty))

            arm_inc_num = self.char.inc_scale_arm
            client_sock.sendall(struct.pack("!f", arm_inc_num))

            if (self.char.arm_offset != 0):
                self.offsetx = self.char.arm_offset.x
                self.offsety = self.char.arm_offset.y

            client_sock.sendall(struct.pack("!f", self.offsetx))

            client_sock.sendall(struct.pack("!f", self.offsety))

            player2_mousex = client_sock.recv(4)
            player2_mouse_posx = struct.unpack("!f", player2_mousex)

            player2_mousey = client_sock.recv(4)
            player2_mouse_posy = struct.unpack("!f", player2_mousey)

            player2_mouse_click = client_sock.recv(1)
            player2_mouse_bool = struct.unpack("!B", player2_mouse_click)
            self.char.p2_mouse_key = player2_mouse_bool[0]

            self.player2_posx = client_sock.recv(4)
            player2_locx = struct.unpack("!f", self.player2_posx)

            self.player2_posy = client_sock.recv(4)
            player2_locy = struct.unpack("!f", self.player2_posy)

            player2_angle = client_sock.recv(4)
            p2_angle = struct.unpack("!f", player2_angle)

            player2_pivotx = client_sock.recv(4)
            p2_pivotx = struct.unpack("!f", player2_pivotx)

            player2_pivoty = client_sock.recv(4)
            p2_pivoty = struct.unpack("!f", player2_pivoty)

            player2_inc_num = client_sock.recv(4)
            p2_inc_num = struct.unpack("!f", player2_inc_num)

            player2_offsetx = client_sock.recv(4)
            p2_offsetx = struct.unpack("!f", player2_offsetx)

            player2_offsety = client_sock.recv(4)
            p2_offsety = struct.unpack("!f", player2_offsety)

            self.char2_rect.x = player2_locx[0]
            self.char2_rect.y = player2_locy[0]

            self.char.p2_mouse_key = (bool(player2_mouse_bool[0]),0,0)
            self.char.p2_img_pos[0] = player2_locx[0]
            self.char.p2_img_pos[1] = player2_locy[0]

            self.char.p2_angle = p2_angle[0]
            self.char.p2_pivot = [p2_pivotx[0], p2_pivoty[0]]
            self.char.p2_inc_scale_arm = p2_inc_num[0]

            p2width = max(1, int(self.rotate_img.get_width()))
            p2height = max(1, self.char.p2_inc_scale_arm)
            scale_arm = pygame.transform.scale(self.rotate_img, (p2width, p2height))

            self.char.p2_offset = pygame.math.Vector2(p2_offsetx[0], p2_offsety[0])

            p2_rotate_img, p2_rotate_rect = self.char.rotate(scale_arm, self.char.p2_angle, self.char.p2_pivot, self.char.p2_offset, self.char.p2_mouse_key, self.char.p2_inc_scale_arm)

            self.game_window.fill((2, 0, 68))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN: #ESC to exit
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.clock.tick(60)

            self.game_window.blit(self.background_img, self.back_rect)

            if (self.char.rect.y > 1100):
                if (self.store_high_score < self.store_score):
                    self.store_high_score = self.store_score
                self.store_score = 0
                self.max_dist = 0
                self.prev_player_rect_x = 0
                self.max_grab_x = 0
                self.dict_store_grab.clear()
                self.fall = True
                self.list_of_crab[0] = 0
                self.list_of_crab[1] = 0
                self.list_of_crab[2] = 0

            if (self.fall == True):

                self.prev_grab_x = 0
                self.cur_grab_x = 0

                self.objects_new = Objects(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.background_img)
                self.char_new = Player(self.game_window, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.objects_new.grab_rect, self.objects_new.grab_mask)
                self.camera_new = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.char_new.rect, self.game_window, self.objects, self.char_new)

                self.grab_obj_new = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera_new, self.char_new, 800)
                self.grab_obj2_new = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera_new, self.char_new, 300)
                self.grab_obj3_new = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera_new, self.char_new, 1300)

                self.char_new.velocity_y = 0
                self.char_new.grab_velocity.y = 0
                self.char_new.rect.y = self.SCREEN_HEIGHT//2
                self.char_new.img_pos[1] = self.SCREEN_HEIGHT//2
                self.char_new.img_pos[0] = self.SCREEN_WIDTH//2
                self.camera_new.offset = pygame.math.Vector2(0,0)
                self.camera_new.offset.x = self.char_new.rect.centerx - self.SCREEN_WIDTH // 2

                self.char = self.char_new
                self.objects = self.objects_new
                self.grab_obj = self.grab_obj_new
                self.grab_obj2 = self.grab_obj2_new
                self.grab_obj3 = self.grab_obj3_new
                self.camera = self.camera_new
                
                self.fall = False


            elif(self.fall == False):
                
                self.char.move(self.objects.floor_rect, self.objects.left_wall_rect, self.objects.left_wall_mask, self.camera, self.fall, player_num)
                self.objects.update(self.camera, self.char)
                self.grab_obj.generateObj()
                self.grab_obj2.generateObj()
                self.grab_obj3.generateObj()
                #self.camera.object_offset(self.objects, self.char, self.grab_obj, self.fall)
                #self.camera.object_offset(self.objects, self.char, self.grab_obj2, self.fall)
                #self.camera.object_offset(self.objects, self.char, self.grab_obj3, self.fall)

   
                self.game_window.blit(self.char2, self.char2_rect)

                if (self.char.arm_collide and self.store_cond == False):

                    self.prev_grab_x = self.cur_grab_x
                    self.cur_grab_x = self.char.grab_coords[0]

                    if (self.cur_grab_x > self.max_grab_x):
                        self.max_grab_x = self.cur_grab_x

                    for i in range(self.cur_grab_x-40, self.cur_grab_x+40):
                        if i in self.dict_store_grab:
                            self.grab_cond = False

                    if ((abs(self.cur_grab_x - self.prev_grab_x) > 40 and self.prev_grab_x != self.max_grab_x and self.grab_cond) or self.store_score == 0):
                        self.score_inc = False          
                        self.dict_store_grab[self.cur_grab_x] = self.store_score

                    self.store_cond = True
                elif (self.char.arm_collide == False):
                    self.store_cond = False
                    self.grab_cond = True
                

                if ((self.grab_obj3.check_crab_coll or self.grab_obj2.check_crab_coll or self.grab_obj.check_crab_coll) and self.score_inc == False):
                    self.store_score += 1
                    self.score_inc = True
            
            self.game_window.blit(p2_rotate_img, p2_rotate_rect)

            #debug(f"Score: {self.store_score} High Score: {self.store_high_score}", self.game_window)
            debug([self.char2_rect.y, p2_rotate_rect.y], self.game_window)

            pygame.display.update()


def main():
    Game().run()
 
if __name__ == "__main__":
    main()