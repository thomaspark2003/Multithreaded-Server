import pygame
import sys
from sprites import Player
from sprites import Objects
import time
from debug import debug

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Orb Jump')
        desktop_info = pygame.display.Info()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = desktop_info.current_w, desktop_info.current_h

        self.clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.player_image = pygame.image.load('images/player_sprite.png')
        self.rect = self.player_image.get_rect()

        self.background_img = pygame.image.load('images/background_doubled.png').convert()

        self.objects = Objects(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game_window)
        self.char = Player(self.game_window, self.rect, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.background_img)
        
        self.running = True

    def run(self):
        while self.running:

            self.game_window.fill((2, 0, 68))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN: #ESC to exit
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.clock.tick(60)

            self.char.move(self.objects.floor_rect, self.objects.left_wall_rect, self.objects.right_wall_rect, self.objects.left_wall_mask)
            self.objects.update()

            pygame.display.update()

def main():
    Game().run()

if __name__ == "__main__":
    main()