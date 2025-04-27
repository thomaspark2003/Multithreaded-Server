import pygame
import sys
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
        self.game_window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.player_image = pygame.image.load('images/player_sprite.png')
  
        self.rect = self.player_image.get_rect()

        self.background_img = pygame.image.load('images/background_doubled.png').convert()

        self.objects = Objects(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.background_img)
        self.char = Player(self.game_window, self.rect, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.objects.grab_rect, self.objects.grab_mask)
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.char.rect, self.game_window, self.objects, self.char)
        
        self.running = True

        self.grab_obj = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 800)
        self.grab_obj2 = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 300)
        self.grab_obj3 = GrabObject(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window, self.camera, self.char, 1300)

    def run(self):
        while self.running:

            self.game_window.fill((2, 0, 68))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN: #ESC to exit
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.clock.tick(60)

            self.char.move(self.objects.floor_rect, self.objects.left_wall_rect, self.objects.left_wall_mask, self.camera)
            self.objects.update(self.camera, self.char)
            self.grab_obj.generateObj()
            self.grab_obj2.generateObj()
            self.grab_obj3.generateObj()
            self.camera.object_offset(self.objects, self.char, self.grab_obj)
            self.camera.object_offset(self.objects, self.char, self.grab_obj2)
            self.camera.object_offset(self.objects, self.char, self.grab_obj3)
            
            pygame.display.update()

def main():
    Game().run()

if __name__ == "__main__":
    main()