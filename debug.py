import pygame

pygame.init()

font = pygame.font.Font(None, 30)

def debug(info, display_surf, x=10, y=10):
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft = (x+50,y))
    pygame.draw.rect(display_surf, 'Black', debug_rect)
    display_surf.blit(debug_surf, debug_rect)