import pygame
import time
from debug import debug
import math
import random

class Camera:
    def __init__(self, width, height, player_rect, game_window, objects, player):
        self.camera_rect = pygame.Rect(0,0,width,height)
        self.rect = player_rect
        self.width = width
        self.height = height
        self.screen = game_window
        self.offset = pygame.math.Vector2(0,0)

        self.grab_velocity_x = 0
        self.grab_velocity_y = 0

        self.scroll_x = 0
        
        self.player_x_offset = int(player_rect.x)
        self.buffer = self.width
        self.object_offset_x = 0
        self.object_offset_y = 0

    def object_offset(self, objects, player, grab_obj):

        leftwall_rect = objects.left_wall_rect
        coral_rect = objects.red_corals_rect
        grab_rect = grab_obj.grab_rect
        player_rect = player.rect
        floor_rect = objects.floor_rect

        self.offset.x = player_rect.centerx - self.width//2
        
        if (player_rect.x < self.offset.x):
            self.offset.x = 0

        
        

class Player:
    def __init__(self, screen, rect, width, height, grab_rect, grab_mask):
        self.screen = screen
        self.rect = rect
        self.width = width
        self.height = height

        self.mouseposx, self.mouseposy = pygame.mouse.get_pos()

        self.player_image = pygame.image.load('images/player_sprite3.png')
        self.arm = pygame.image.load('images/arm_prototype.png')

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

        self.img_pos = [self.width//2, self.height//2]
        self.rect = self.player_image.get_rect()
        self.rect.topleft = round(self.img_pos[0]), round(self.img_pos[1])

        self.collision_count = 0

        self.acceleration_x = 200
        self.velocity_x = 100

        self.velocity_y = 0
        self.acceleration_y = 200
        self.gravity = 1400

        self.jump = False
    
        self.grab_mask = grab_mask
        self.grab_rect= grab_rect
        self.grab_coords = [0,0]
        self.grab_lock = False
        self.let_go = False

        self.rotate_mask = None
        self.rotate_rect = None

        self.overlap_count = 0

        self.mouse_lock = False
        self.mouse_count = True
        self.mouse_lock_vec = pygame.math.Vector2()

        self.scroll_x = 0
        self.previous_time = time.time()

        self.key = None
        self.mouse_key = None
    
    def rotate(self, arm_img, angle, pivot, offset, mouse_key, inc_scale_arm, camera):

        if (mouse_key[0] == True):
            offset.y = inc_scale_arm/2

        rotate_arm_img = pygame.transform.rotozoom(arm_img, -angle, 1)
        rotate_offset = offset.rotate(angle)
        rotate_rect = rotate_arm_img.get_rect(center=pivot+rotate_offset)

        return rotate_arm_img, rotate_rect

    def move(self, floor_rect, leftwall_rect, leftwall_mask, camera):

        self.dt = time.time() - self.previous_time
        self.previous_time = time.time()

        key = pygame.key.get_pressed()
        self.key = key
        mouse_key = pygame.mouse.get_pressed()
        self.mouse_key = mouse_key

        if self.velocity_y < -600:
            self.jump = False

        mouse_posx, mouse_posy = pygame.mouse.get_pos()
        mouse_posx = mouse_posx + camera.offset.x
        self.arm_rect.center = (self.img_pos[0]+15, self.img_pos[1]+48)
        pivot = [self.arm_rect.x, self.arm_rect.y]

        if (self.grab_lock == True):
            pivot2 = pygame.math.Vector2(self.grab_coords[0], self.grab_coords[1])
            grab_vec = pivot2 - pivot

            object_to_arm_len = grab_vec.length()
            angle = -math.degrees(math.atan2(grab_vec.x, grab_vec.y))
        else:
            angle = -math.degrees(math.atan2(-pivot[0] + mouse_posx, -pivot[1] + mouse_posy))
            
        offset = pygame.math.Vector2(0,5)

        scale_arm = self.arm

        scale_arm = pygame.transform.scale(self.arm, (int(self.arm.get_width()), self.inc_scale_arm))

        rotate_img, rotate_rect = self.rotate(scale_arm, angle, pivot, offset, mouse_key, self.inc_scale_arm, camera)
        self.rotate_rect = rotate_rect

        mouse_to_arm_x = mouse_posx - pivot[0]
        mouse_to_arm_y = mouse_posy - pivot[1]
        mouse_length = math.hypot(mouse_to_arm_x,mouse_to_arm_y)

        if (mouse_key[0] == True and self.arm_collide == False):

            self.mouse_lock = True

            if (self.let_go == True and self.grab_velocity.length_squared() > 0.01):

                damping = 0.985
                self.grab_velocity *= damping
                self.img_pos[0] += self.grab_velocity.x * self.dt
                camera.player_x_offset += self.grab_velocity.x * self.dt
                self.img_pos[1] += self.grab_velocity.y * self.dt

            if (self.inc_scale_arm >= mouse_length):
                self.inc_scale_arm = min(mouse_length, 300)
                self.stored_grab = True
            elif (self.inc_scale_arm >= 1000):
                self.inc_scale_arm = 1000
                self.stored_grab = True
            
            if (self.stored_grab == True and self.inc_scale_arm > 20):
                self.inc_scale_arm -= 1200 * self.dt
            elif (self.stored_grab == False):
                self.inc_scale_arm += 1700 * self.dt

        elif (mouse_key[0]== False):
            self.gravity = 1400
            self.inc_scale_arm = 20
            self.arm_collide = False
            self.player_collide = False
            self.grab_lock = False
            self.stored_grab = False
            self.overlap_count = 0
            self.mouse_lock = False
            self.mouse_count = 0

            if (self.inc_scale_arm == 20):
                self.mouse_lock = False

            if (self.let_go == True and self.grab_velocity.length_squared() > 0.01):
                damping = 0.985
                self.grab_velocity *= damping
                self.img_pos[0] += self.grab_velocity.x * self.dt
                self.img_pos[1] += self.grab_velocity.y * self.dt

        elif (self.arm_collide == True and mouse_key[0] == True):
            self.gravity = 0
            self.velocity_y = 0
            follow_mouse = pygame.math.Vector2(self.grab_coords[0], self.grab_coords[1])
            player_center = pygame.math.Vector2(self.img_pos[0], self.img_pos[1])
            to_mouse = follow_mouse-player_center
            distance = to_mouse.length()

            if (distance > 300):
                to_mouse.scale_to_length(300)

            mouse_dir = (to_mouse).normalize()

            self.inc_scale_arm = object_to_arm_len
            self.grab_velocity += mouse_dir * self.grab_acceleration * self.dt
            self.img_pos[0] += self.grab_velocity.x * self.dt
            camera.offset.x += self.grab_velocity.x * self.dt
            self.img_pos[1] += self.grab_velocity.y * self.dt
            self.let_go = True
            self.grab_velocity *= 0.99

 
        if (self.mouse_lock == True):
            if (self.mouse_count == 0):
                self.mouse_lock_vec.x = mouse_posx
                self.mouse_lock_vec.y = mouse_posy
                self.mouse_count += 1

            mouse_to_arm = self.mouse_lock_vec - self.rect.center
            mouse_to_arm_len = mouse_to_arm.length()

            if (self.inc_scale_arm > mouse_to_arm_len):
                self.stored_grab = True
            

        rotate_mask = pygame.mask.from_surface(rotate_img)
        self.rotate_mask = rotate_mask
        rotate_mask_img = rotate_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.screen.blit(rotate_mask_img, (rotate_rect.x-camera.offset.x, rotate_rect.y)) #block transfer rotating arm to screen

        if key[pygame.K_a] and self.arm_collide:
            self.img_pos[0] -= self.acceleration_x * self.dt
            self.rect.x = round(self.img_pos[0])
            self.border_collision('horizontal', leftwall_rect, floor_rect)

        elif key[pygame.K_d] and self.arm_collide:
            self.img_pos[0] += self.acceleration_x * self.dt
            self.rect.x = round(self.img_pos[0])
            self.border_collision('horizontal', leftwall_rect, floor_rect)

        if key[pygame.K_w] and self.jump == True and self.velocity_y > -400:
            self.velocity_y -= 2000 * self.dt
        else:
            self.velocity_y += self.gravity  * self.dt
            self.jump = False

        self.img_pos[1] += self.velocity_y * self.dt
        self.rect.topleft = round(self.img_pos[0]), round(self.img_pos[1])
        self.border_collision('vertical', leftwall_rect, floor_rect)

        self.screen.blit(self.player_image, (self.rect.x-camera.offset.x, self.rect.y))

        self.screen.blit(rotate_img, (rotate_rect.x-camera.offset.x, rotate_rect.y))

    def border_collision(self, axis, left_wall_rect, floor_rect):
        

            self.left_wall_rect = left_wall_rect
            self.floor_rect = floor_rect

            if axis == 'horizontal':
                    
                if self.left_wall_rect.colliderect(self.rect):
                    self.rect.left = self.left_wall_rect.right
                    self.img_pos[0] = self.rect.x
                    self.player_collide = True

            if axis == 'vertical':
                if self.floor_rect.colliderect(self.rect):
                    if self.rect.bottom >= self.floor_rect.top:
                        self.rect.bottom = self.floor_rect.top
                        self.img_pos[1] = self.rect.y
                        self.velocity_y = 0
                        self.jump = True
                        self.let_go = False
                        self.grab_velocity.x = 0
                        self.grab_velocity.y = 0

    def mask_collision(self, rotate_mask, grab_mask, rotate_rect, grab_rect, object_offset_x, camera):

        rotate_mask_img = rotate_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        mask_offset_x = rotate_rect.left - (grab_rect.x+object_offset_x)
        mask_offset_y = rotate_rect.top - grab_rect.y

        if (grab_mask.overlap(rotate_mask, (mask_offset_x, mask_offset_y)) and self.overlap_count == 0):
            
            temp_mask = grab_mask.overlap_mask(rotate_mask, (mask_offset_x, mask_offset_y))
            self.arm_collide = True

            overlap_rects = temp_mask.get_bounding_rects()
            self.grab_coords[0] = overlap_rects[0].x + (grab_rect.x+object_offset_x)
            self.grab_coords[1] = overlap_rects[0].y + grab_rect.y
            self.grab_lock = True
            self.overlap_count += 1

class Objects:
    def __init__(self, width, height, screen, background_img):
        
        self.width = width
        self.height = height

        self.background_img = background_img
        self.background_rect = self.background_img.get_rect()
        self.background_rect.bottomleft = (0, self.height)

        self.screen = screen

        self.left_wall = pygame.image.load('images/sprite_wall_collide.png')
        self.left_wall_rect = self.left_wall.get_rect()
        self.left_wall_rect.x = -50
        self.left_wall_mask = pygame.mask.from_surface(self.left_wall)
        self.left_wall_mask_img = self.left_wall_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.right_wall = pygame.image.load('images/sprite_wall_collide.png')
        self.right_wall_rect = self.left_wall.get_rect()
        self.right_wall_rect.topright = (self.width, 0)

        self.floor = pygame.image.load('images/sprite_floor_collision.jpg')
        self.floor_rect = self.floor.get_rect()
        self.floor_rect.topleft = (-1000, self.height/1.25)

        self.grab_object = pygame.image.load('images/test_grab.png')
        self.grab_rect = self.grab_object.get_rect()
        self.grab_mask = pygame.mask.from_surface(self.grab_object)
        self.grab_rect.x = 800
        self.grab_rect.y = 200
        self.grab_mask_img = self.grab_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.red_corals = pygame.image.load('images/red_corals.png')
        self.red_corals_rect = self.red_corals.get_rect()
        self.red_corals_rect.center = (700, 665)

        self.pillar = pygame.image.load('images/pillar1.png')
        self.pillar_rect = self.pillar.get_rect()
        self.pillar_rect.center = (700, 585)

        self.random_num = random.randrange(200,900)

        self.player_center_offset_x = 0
        self.player_center_offset_y = 0

        self.dict_of_objects = {}

        self.object_offset_x = 0
        self.object_offset_y = 0

        self.camera = None

        self.prev_chunk = 1

        self.new_chunk = False

        self.chunk_offset = self.width//2
        self.store_prev_x = 0

        self.count_obj = 0

    def update(self, camera, player):

        #self.screen.blit(self.background_img, self.background_rect)

        self.screen.blit(self.left_wall, self.left_wall_rect)

        self.screen.blit(self.floor, (self.floor_rect.x-camera.offset.x, self.floor_rect.y))

        self.screen.blit(self.red_corals, (self.red_corals_rect.x-camera.offset.x, self.red_corals_rect.y))

class GrabObject:
    def __init__(self, width, height, screen, camera, player, posx):

        self.width = width
        self.height = height
        self.screen = screen

        self.grab_object = pygame.image.load('images/test_grab.png')
        self.grab_rect = self.grab_object.get_rect()
        self.grab_mask = pygame.mask.from_surface(self.grab_object)
        self.grab_rect.x = posx
        self.rand_y = random.randrange(200, 500)
        self.grab_rect.y = self.rand_y
        self.grab_mask_img = self.grab_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.player = player
        self.camera = camera

        self.object_offset_x = 0
        self.object_offset_y = 0

        self.dict_of_objects = {}


    def generateObj(self):
      
        grab_obj_loc = self.grab_rect.x-self.camera.offset.x

        if (grab_obj_loc < -50):
            self.grab_rect.x += self.width+50

        self.player.mask_collision(self.player.rotate_mask, self.grab_mask, self.player.rotate_rect, self.grab_rect, self.object_offset_x, self.camera)
        self.screen.blit(self.grab_mask_img, ((self.grab_rect.x-self.camera.offset.x), self.grab_rect.y))
        debug(self.player.rect.x, self.screen)