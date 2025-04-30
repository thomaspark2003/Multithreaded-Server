import pygame
import sys
from sprites import Player
from sprites import Objects
from sprites import Camera
from sprites import GrabObject
from sprites import Enemy
import time
from debug import debug

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Octo Sling')
        desktop_info = pygame.display.Info()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = desktop_info.current_w, desktop_info.current_h

        self.clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)

        self.background_img = pygame.image.load('images/background_doubled.png').convert()

        self.objects = Objects(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.background_img)
        self.char = Player(self.game_window, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.objects.grab_rect, self.objects.grab_mask)
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.char.rect, self.game_window, self.objects, self.char)
        
        self.running = True

        self.fall = False

        self.grab_obj = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 800)
        self.grab_obj2 = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 300)
        self.grab_obj3 = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 1300)

        self.enemy = Enemy(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window)

        self.store_score = 0
        self.store_high_score = 0
        self.store_cond = False
        self.prev_score = 0

        self.prev_grab_x = 0
        self.cur_grab_x = 0

        self.max_grab_x = 0

        self.dict_store_grab = {}
        self.grab_cond = True
        

    def run(self):
        while self.running:

            self.game_window.fill((2, 0, 68))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN: #ESC to exit
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.clock.tick(60)

            if (self.char.rect.y > 1100):
                if (self.store_high_score < self.store_score):
                    self.store_high_score = self.store_score
                self.store_score = 0
                self.max_dist = 0
                self.prev_player_rect_x = 0
                self.max_grab_x = 0
                self.dict_store_grab.clear()
                self.fall = True

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
                
                self.char.move(self.objects.floor_rect, self.objects.left_wall_rect, self.objects.left_wall_mask, self.camera, self.fall)
                self.objects.update(self.camera, self.char)
                self.grab_obj.generateObj()
                self.grab_obj2.generateObj()
                self.grab_obj3.generateObj()
                self.camera.object_offset(self.objects, self.char, self.grab_obj, self.fall)
                self.camera.object_offset(self.objects, self.char, self.grab_obj2, self.fall)
                self.camera.object_offset(self.objects, self.char, self.grab_obj3, self.fall)

                if (self.char.arm_collide and self.store_cond == False):

                    self.prev_grab_x = self.cur_grab_x
                    self.cur_grab_x = self.char.grab_coords[0]

                    if (self.cur_grab_x > self.max_grab_x):
                        self.max_grab_x = self.cur_grab_x

                    for i in range(self.cur_grab_x-40, self.cur_grab_x+40):
                        if i in self.dict_store_grab:
                            self.grab_cond = False

                    if ((abs(self.cur_grab_x - self.prev_grab_x) > 40 and self.prev_grab_x != self.max_grab_x and self.grab_cond) or self.store_score == 0):
                        self.store_score += 1
                        self.dict_store_grab[self.cur_grab_x] = self.store_score

                    self.store_cond = True
                elif (self.char.arm_collide == False):
                    self.store_cond = False
                    self.grab_cond = True

            debug(f"Score: {self.store_score} High Score: {self.store_high_score} max: {self.max_grab_x} cur: {self.cur_grab_x} cond: {self.grab_cond}", self.game_window)

            pygame.display.update()

def main():
    Game().run()

if __name__ == "__main__":
    main()