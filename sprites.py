import pygame
import time
from debug import debug
import math

class Player:
    def __init__(self, screen, rect, width, height, background_img):
        self.screen = screen
        self.rect = rect
        self.width = width
        self.height = height

        self.mouseposx, self.mouseposy = pygame.mouse.get_pos()

        self.player_image = pygame.image.load('images/player_sprite.png')
        self.arm = pygame.image.load('images/arm_prototype.png')
        self.arm_pivot_img = pygame.image.load('images/arm_pivot_offset.png')

        self.arm_rect = self.arm.get_rect()
        self.arm_limit = 480
        self.inc_scale_arm = 20
        self.arm_collide = False
        self.grab_velocity = pygame.math.Vector2(0,0)
        self.grab_acceleration = 1000
        self.stored_grab = False
        self.stored_coll_grab = False

        self.player_collide = False

        self.left_wall_grab = False
        self.right_wall_grab = False

        self.background_img = background_img
        self.background_rect = self.background_img.get_rect()
        self.background_rect.bottomleft = (0, self.height)

        self.img_pos = [self.width//2, self.height//2]
        self.rect = self.player_image.get_rect()
        self.rect.topleft = round(self.img_pos[0]), round(self.img_pos[1])

        self.collision_count = 0

        self.acceleration_x = 200
        self.velocity_x = 100

        self.velocity_y = 0
        self.acceleration_y = 200
        self.gravity = 1500

        self.jump = False
    
        self.grab_object = pygame.image.load('images/test_grab.png')
        self.grab_rect = self.grab_object.get_rect()
        self.grab_rect.center = (800,200)
        self.grab_mask = pygame.mask.from_surface(self.grab_object)
        self.grab_mask_img = self.grab_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))
        self.grab_coords = [0,0]
        self.grab_lock = False

        self.scroll = 0
        self.previous_time = time.time()
    
    def rotate(self, arm_img, angle, pivot, offset, mouse_key, inc_scale_arm):

        if (mouse_key[0] == True):
            offset.y = inc_scale_arm/2
            
        #self.inc_scale_arm = grab_vec.length()

        rotate_arm_img = pygame.transform.rotozoom(arm_img, -angle, 1)
        rotate_offset = offset.rotate(angle)
        rotate_rect = rotate_arm_img.get_rect(center=pivot+rotate_offset)

        arm_tip_offset = pygame.math.Vector2(0, inc_scale_arm)
        rotate_armtip_offset = arm_tip_offset.rotate(angle)
        arm_tip_vec = pygame.math.Vector2(pivot) + rotate_armtip_offset

        return rotate_arm_img, rotate_rect, arm_tip_vec

    def move(self, floor_rect, leftwall_rect, rightwall_rect, leftwall_mask):

        self.dt = time.time() - self.previous_time
        self.previous_time = time.time()

        key = pygame.key.get_pressed()
        mouse_key = pygame.mouse.get_pressed()

        if self.velocity_y < -600:
            self.jump = False
                
        self.screen.blit(self.background_img, self.background_rect)

        mouse_posx, mouse_posy = pygame.mouse.get_pos()
        self.arm_rect.center = (self.img_pos[0]+10, self.img_pos[1]+48)
        pivot = [self.arm_rect.x, self.arm_rect.y]

        if (self.grab_lock == True):
            pivot2 = pygame.math.Vector2(self.grab_coords[0], self.grab_coords[1])
            grab_vec = pivot2 - pivot
            object_to_arm_len = grab_vec.length()
            angle = -math.degrees(math.atan2(grab_vec.x, grab_vec.y))
        else:
            angle = -math.degrees(math.atan2(-pivot[0] + mouse_posx, -pivot[1] + mouse_posy))
            
        offset = pygame.math.Vector2(0,5)
        
        self.screen.blit(self.player_image, self.rect)
        pygame.draw.rect(self.screen, (255,255,255), self.rect, 2)

        scale_arm = self.arm

        self.screen.blit(self.grab_mask_img, self.grab_rect)

        scale_arm = pygame.transform.scale(self.arm, (int(self.arm.get_width()), self.inc_scale_arm))

        rotate_img, rotate_rect, arm_tip_vec = self.rotate(scale_arm, angle, pivot, offset, mouse_key, self.inc_scale_arm)

        mouse_to_arm_x = mouse_posx - pivot[0]
        mouse_to_arm_y = mouse_posy - pivot[1]
        mouse_length = math.hypot(mouse_to_arm_x,mouse_to_arm_y)

        if (mouse_key[0] == True and self.arm_collide == False):
            if (self.inc_scale_arm >= mouse_length):
                self.inc_scale_arm = mouse_length
                self.stored_grab = True
            
            if (self.stored_grab == True and self.inc_scale_arm > 20):
                self.inc_scale_arm -= 900 * self.dt
            elif (self.stored_grab == False):
                self.inc_scale_arm += 900 * self.dt

        elif (mouse_key[0]== False):
            self.gravity = 1500
            self.inc_scale_arm = 20
            self.arm_collide = False
            self.grab_velocity.x = 0
            self.grab_velocity.y = 0
            self.player_collide = False
            self.grab_lock = False
            self.stored_grab = False

        elif (self.arm_collide == True and mouse_key[0] == True):
            self.gravity = 0
            follow_mouse = pygame.math.Vector2(self.grab_coords[0], self.grab_coords[1])
            player_center = pygame.math.Vector2(self.img_pos[0], self.img_pos[1])
            mouse_dir = (follow_mouse-player_center).normalize()

            self.inc_scale_arm = object_to_arm_len
            self.grab_velocity += mouse_dir * self.grab_acceleration * self.dt
            self.img_pos[0] += self.grab_velocity.x * self.dt
            self.img_pos[1] += self.grab_velocity.y * self.dt



        rotate_mask = pygame.mask.from_surface(rotate_img)
        rotate_mask_img = rotate_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))
        self.screen.blit(rotate_mask_img, rotate_rect)

        self.border_collision('horizontal', leftwall_rect, rightwall_rect, floor_rect, rotate_img, arm_tip_vec, angle, offset, leftwall_mask, rotate_mask, self.grab_mask, rotate_rect)

        if key[pygame.K_a]:
            self.img_pos[0] -= self.acceleration_x * self.dt
            self.rect.x = round(self.img_pos[0])
            self.border_collision('horizontal', leftwall_rect, rightwall_rect, floor_rect, rotate_rect, arm_tip_vec, angle, offset, leftwall_mask, rotate_mask, self.grab_mask, rotate_rect)

        elif key[pygame.K_d]:
            self.img_pos[0] += self.acceleration_x * self.dt
            self.rect.x = round(self.img_pos[0])
            self.border_collision('horizontal', leftwall_rect, rightwall_rect, floor_rect, rotate_rect, arm_tip_vec, angle, offset, leftwall_mask, rotate_mask, self.grab_mask, rotate_rect)

        self.velocity_y += self.gravity  * self.dt
        self.img_pos[1] += self.velocity_y * self.dt
        self.rect.topleft = round(self.img_pos[0]), round(self.img_pos[1])
        self.border_collision('vertical', leftwall_rect, rightwall_rect, floor_rect, rotate_rect, arm_tip_vec, angle, offset, leftwall_mask, rotate_mask, self.grab_mask, rotate_rect)

        #self.screen.blit(rotate_img, rotate_rect)
        #pygame.draw.rect(self.screen, (255,255,255), rotate_rect, 2)

        debug(mouse_length, self.screen)

    def border_collision(self, axis, left_wall_rect, right_wall_rect, floor_rect, arm_rect, arm_tip_vec, angle, offset, leftwall_mask, rotate_mask, grab_mask, rotate_rect):
            
            rotate_mask_img = rotate_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

            self.left_wall_rect = left_wall_rect
            self.right_wall_rect = right_wall_rect
            self.floor_rect = floor_rect

            overlap_count = 0

            if axis == 'horizontal':
                    
                if self.left_wall_rect.colliderect(self.rect):
                    self.rect.left = self.left_wall_rect.right
                    self.img_pos[0] = self.rect.x
                    self.player_collide = True
                
                if self.right_wall_rect.colliderect(self.rect):
                    self.rect.right = self.right_wall_rect.left
                    self.img_pos[0] = self.rect.x
                    self.player_collide = True

                mask_offset_x = rotate_rect.left - self.grab_rect.x
                mask_offset_y = rotate_rect.top - self.grab_rect.y
                if (grab_mask.overlap(rotate_mask, (mask_offset_x, mask_offset_y)) and overlap_count == 0):
                    temp_mask = grab_mask.overlap_mask(rotate_mask, (mask_offset_x, mask_offset_y))
                    self.arm_collide = True

                    overlap_rects = temp_mask.get_bounding_rects()
                    self.grab_coords[0] = overlap_rects[0].x + self.grab_rect.x
                    self.grab_coords[1] = overlap_rects[0].y + self.grab_rect.y
                    self.grab_lock = True
                    overlap_count += 1
                    #self.screen.blit(temp_mask.to_surface(setcolor=(255,0,0,255), unsetcolor=(0,0,0,0)), (self.grab_rect.topleft))

            if axis == 'vertical':
                if self.floor_rect.colliderect(self.rect):
                    if self.rect.bottom >= self.floor_rect.top:
                        self.rect.bottom = self.floor_rect.top
                        self.img_pos[1] = self.rect.y
                        self.velocity_y = 0
                        self.jump = True

class Objects:
    def __init__(self, width, height, screen):

        self.screen = screen

        self.width = width
        self.height = height

        self.left_wall = pygame.image.load('images/sprite_wall_collide.png')
        self.left_wall_rect = self.left_wall.get_rect()
        self.left_wall_mask = pygame.mask.from_surface(self.left_wall)
        self.left_wall_mask_img = self.left_wall_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.right_wall = pygame.image.load('images/sprite_wall_collide.png')
        self.right_wall_rect = self.left_wall.get_rect()
        self.right_wall_rect.topright = (self.width, 0)

        self.floor = pygame.image.load('images/sprite_floor_collision.jpg')
        self.floor_rect = self.floor.get_rect()
        self.floor_rect.topleft = (0, self.height/1.5)

    def update(self):

        #self.screen.blit(self.left_wall_mask_img, self.left_wall_rect)
        self.screen.blit(self.left_wall, self.left_wall_rect)
        pygame.draw.rect(self.screen, (255,255,255), self.left_wall_rect, 2)

        self.screen.blit(self.right_wall, self.right_wall_rect)
        pygame.draw.rect(self.screen, (255,255,255), self.right_wall_rect, 2)

        self.screen.blit(self.floor, self.floor_rect)
        pygame.draw.rect(self.screen, (255,255,255), self.floor_rect, 2)
