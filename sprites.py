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

        self.camera_off = False

        self.screen_x = 0
        self.prev_value = 0
        self.prev_cond = False
        self.prev_cond2 = False

        self.cam_offset_prev = 0
        self.cam_cond = 0

        self.prev_offset_val = 0

    def object_offset(self, objects, player, grab_obj, fall):

        leftwall_rect = objects.left_wall_rect
        coral_rect = objects.red_corals_rect
        grab_rect = grab_obj.grab_rect
        player_rect = player.rect
        floor_rect = objects.floor_rect

        self.offset.x = player_rect.centerx - self.width//2

        self.screen_x = player_rect.x - self.offset.x
        if (player.arm_collide):
            if (self.prev_cond == False):
                self.prev_value = player_rect.x
                self.cam_offset_prev = self.offset.x
                self.prev_cond = True

        if (self.prev_cond == False):
            self.prev_value = player_rect.x
            self.cam_offset_prev = self.offset.x
            self.prev_cond = True

        #if (self.prev_cond == False):
        #    self.prev_value = player_rect.x
        #    self.cam_offset_prev = self.offset.x
        #    self.prev_cond = True

        if (player_rect.x < self.prev_value):
            self.camera_off = True

        elif (player_rect.x > self.prev_value):
            self.camera_off = False
            self.prev_cond = False

class Player:
    def __init__(self, screen, width, height, grab_rect, grab_mask):
        self.screen = screen
        self.width = width
        self.height = height

        self.mouseposx, self.mouseposy = pygame.mouse.get_pos()

        self.player_image = pygame.image.load('images/player_sprite5.png')
        self.player_image = pygame.transform.scale(self.player_image, (50,50))
        self.arm = pygame.image.load('images/arm_prototype.png')

        self.player_mask = pygame.mask.from_surface(self.player_image)
        self.player_mask_img = self.player_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

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
        self.rect.centerx = self.img_pos[0]
        self.rect.y = self.img_pos[1]

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

        pivot = [self.arm_rect.x, self.arm_rect.y]
        mouse_posx, mouse_posy = pygame.mouse.get_pos()

        if (self.grab_lock == True):
            pivot2 = pygame.math.Vector2(self.grab_coords[0], self.grab_coords[1])
            grab_vec = pivot2 - pivot

            object_to_arm_len = grab_vec.length()
            angle = -math.degrees(math.atan2(grab_vec.x, grab_vec.y))
        else:
            angle = -math.degrees(math.atan2(-pivot[0] + mouse_posx, -pivot[1] + mouse_posy))

        offset = pygame.math.Vector2(0,5)
        mouse_key = pygame.mouse.get_pressed()

        self.rotate_mask = None
        self.rotate_img, self.rotate_rect = self.rotate(self.arm, angle, pivot, offset, mouse_key, self.inc_scale_arm)

        self.overlap_count = 0

        self.mouse_lock = False
        self.mouse_count = True
        self.mouse_lock_vec = pygame.math.Vector2()

        self.scroll_x = 0
        self.previous_time = time.time()

        self.key = None
        self.mouse_key = None

        self.store_prev_mouse_x = None
        self.mouse_cond = False

        self.count_fall = 0

        self.arm_pivot = 0
        self.angle = 0
        self.arm_offset = 0

        self.arm_rect.center = (self.img_pos[0]+15, self.img_pos[1]+48)
        self.p2_angle = 0
        self.p2_pivot = 0
        self.p2_offset = 0
        self.p2_mouse_key = 0
        self.p2_inc_scale_arm = 20
        self.p2_img_pos = [0,0]
        self.p2_store_prev_mouse_x = None
    
    def rotate(self, arm_img, angle, pivot, offset, mouse_key, inc_scale_arm):

        if (mouse_key[0] == True):
            offset.y = inc_scale_arm/2

        rotate_arm_img = pygame.transform.rotozoom(arm_img, -angle, 1)
        rotate_offset = offset.rotate(angle)
        rotate_rect = rotate_arm_img.get_rect(center=pivot+rotate_offset)

        return rotate_arm_img, rotate_rect

    def move(self, floor_rect, leftwall_rect, leftwall_mask, camera, fall, player_num):

        self.dt = time.time() - self.previous_time
        self.previous_time = time.time()

        key = pygame.key.get_pressed()
        self.key = key
        mouse_key = pygame.mouse.get_pressed()
        self.mouse_key = mouse_key

        if self.velocity_y < -600:
            self.jump = False

        mouse_posx, mouse_posy = pygame.mouse.get_pos()
        self.store_prev_mouse_x = mouse_posx

        if (camera.camera_off):
            mouse_posx = mouse_posx + camera.cam_offset_prev 
        else:
            mouse_posx = mouse_posx + camera.offset.x
            mouse_posy = mouse_posy

        #self.arm_rect.center = (self.img_pos[0]+15, self.img_pos[1]+48)
        #pivot = [self.arm_rect.x, self.arm_rect.y]
        pivot = pygame.math.Vector2(self.img_pos[0]+12, self.img_pos[1]+34)
        self.arm_pivot = pivot

        if (self.grab_lock == True):
            pivot2 = pygame.math.Vector2(self.grab_coords[0], self.grab_coords[1])
            grab_vec = pivot2 - pivot

            object_to_arm_len = grab_vec.length()
            angle = -math.degrees(math.atan2(grab_vec.x, grab_vec.y))
            self.angle = angle
        else:
            angle = -math.degrees(math.atan2(-pivot[0] + mouse_posx, -pivot[1] + mouse_posy))
            self.angle = angle
            
        offset = pygame.math.Vector2(0,5)
        self.arm_offset = offset

        scale_arm = self.arm

        width = max(1, int(self.arm.get_width()))
        height = max(1, self.inc_scale_arm)
        scale_arm = pygame.transform.scale(self.arm, (width, height))

        self.rotate_img, self.rotate_rect = self.rotate(scale_arm, angle, pivot, offset, mouse_key, self.inc_scale_arm)

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
                self.stored_grab = True
            elif (self.inc_scale_arm >= 1000):
                self.inc_scale_arm = 1000
                self.stored_grab = True
            
            if (self.stored_grab == True and self.inc_scale_arm > 20):
                self.inc_scale_arm -= 800 * self.dt
            if (self.stored_grab == False):
                self.inc_scale_arm += 1200 * self.dt

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

        if (player_num == 1):
            if key[pygame.K_a]:
                self.img_pos[0] -= self.acceleration_x * self.dt
                self.rect.x = round(self.img_pos[0])
                self.border_collision('horizontal', leftwall_rect, floor_rect, camera)

            elif key[pygame.K_d]:
                self.img_pos[0] += self.acceleration_x * self.dt
                self.rect.x = round(self.img_pos[0])
                self.border_collision('horizontal', leftwall_rect, floor_rect, camera)

        if (player_num == 2):
            if key[pygame.K_j]:
                self.img_pos[0] -= self.acceleration_x * self.dt
                self.rect.x = round(self.img_pos[0])
                self.border_collision('horizontal', leftwall_rect, floor_rect, camera)

            elif key[pygame.K_l]:
                self.img_pos[0] += self.acceleration_x * self.dt
                self.rect.x = round(self.img_pos[0])
                self.border_collision('horizontal', leftwall_rect, floor_rect, camera)
        
        self.border_collision('horizontal', leftwall_rect, floor_rect, camera)

        rotate_mask = pygame.mask.from_surface(self.rotate_img)
        mask_outline = rotate_mask.outline()

        self.rotate_mask = rotate_mask
        rotate_mask_img = rotate_mask.to_surface(setcolor=(100, 156, 252), unsetcolor=(0, 0, 0, 0))

        if (camera.camera_off):
            self.screen.blit(self.player_image, (self.rect.x-camera.cam_offset_prev, self.rect.y))

        else:
            self.screen.blit(self.player_image, (self.rect.x-camera.offset.x, self.rect.y))


        if (camera.camera_off):
            self.screen.blit(rotate_mask_img, (self.rotate_rect.x-camera.cam_offset_prev, self.rotate_rect.y))

            for point in range(len(mask_outline)):
                start = (mask_outline[point][0] + self.rotate_rect.x-camera.cam_offset_prev, mask_outline[point][1] + self.rotate_rect.y)
                end = (mask_outline[(point + 1) % len(mask_outline)][0] + self.rotate_rect.x-camera.cam_offset_prev, mask_outline[(point + 1) % len(mask_outline)][1] + self.rotate_rect.y)
                pygame.draw.line(self.screen, (0, 0, 0), start, end, 3)
        else:
            self.screen.blit(rotate_mask_img, (self.rotate_rect.x-camera.offset.x, self.rotate_rect.y)) #block transfer rotating arm to screen

            for point in range(len(mask_outline)):
                start = (mask_outline[point][0] + self.rotate_rect.x-camera.offset.x, mask_outline[point][1] + self.rotate_rect.y)
                end = (mask_outline[(point + 1) % len(mask_outline)][0] + self.rotate_rect.x-camera.offset.x, mask_outline[(point + 1) % len(mask_outline)][1] + self.rotate_rect.y)
                pygame.draw.line(self.screen, (0, 0, 0), start, end, 3)
        
        self.velocity_y += self.gravity  * self.dt
        self.jump = False

        if (not fall):
            self.img_pos[1] += self.velocity_y * self.dt
            self.rect.topleft = round(self.img_pos[0]), round(self.img_pos[1])
            self.border_collision('vertical', leftwall_rect, floor_rect, camera)


    def border_collision(self, axis, left_wall_rect, floor_rect, camera):
        

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

    def mask_collision(self, rotate_mask, grab_mask, rotate_rect, grab_rect, camera):

        rotate_mask_img = rotate_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        if (grab_rect.x > 200):
            mask_offset_x = rotate_rect.left - (grab_rect.x)
            mask_offset_y = rotate_rect.top - grab_rect.y

            if (grab_mask.overlap(rotate_mask, (mask_offset_x, mask_offset_y)) and self.overlap_count == 0):
                
                temp_mask = grab_mask.overlap_mask(rotate_mask, (mask_offset_x, mask_offset_y))
                self.arm_collide = True

                overlap_rects = temp_mask.get_bounding_rects()
                self.grab_coords[0] = overlap_rects[0].x + (grab_rect.x)
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

        self.floor = pygame.image.load('images/floor_cliff.png')
        self.floor = pygame.transform.scale(self.floor, (1920, 500))
        self.floor_rect = self.floor.get_rect()
        #self.floor_rect.x = -1000
        self.floor_rect.y = self.height/1.25

        self.grab_object = pygame.image.load('images/test_grab.png')
        self.grab_rect = self.grab_object.get_rect()
        self.grab_mask = pygame.mask.from_surface(self.grab_object)
        self.grab_rect.x = 800
        self.grab_rect.y = 200
        self.grab_mask_img = self.grab_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.red_corals = pygame.image.load('images/red_corals.png')
        self.red_corals_rect = self.red_corals.get_rect()
        self.red_corals_rect.center = (700, 665)

        self.yellow_corals = pygame.image.load('images/yellow_corals.png')
        self.yellow_corals_rect = self.yellow_corals.get_rect()
        self.yellow_corals_rect.center = (200, 665)

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

        self.screen.blit(self.left_wall, self.left_wall_rect)

        if (camera.camera_off):
            self.screen.blit(self.floor, (self.floor_rect.x-camera.cam_offset_prev, self.floor_rect.y))

            self.screen.blit(self.red_corals, (self.red_corals_rect.x-camera.cam_offset_prev, self.red_corals_rect.y))

            self.screen.blit(self.yellow_corals, (self.yellow_corals_rect.x-camera.cam_offset_prev, self.yellow_corals_rect.y))

        else:
            self.screen.blit(self.floor, (self.floor_rect.x-camera.offset.x, self.floor_rect.y))

            self.screen.blit(self.red_corals, (self.red_corals_rect.x-camera.offset.x, self.red_corals_rect.y))

            self.screen.blit(self.yellow_corals, (self.yellow_corals_rect.x-camera.offset.x, self.yellow_corals_rect.y))
    

class GrabObject:
    def __init__(self, width, height, screen, camera, player, posx):

        self.width = width
        self.height = height
        self.screen = screen
        self.posx = posx

        self.grab_object = pygame.image.load('images/hook_sprite.png')
        self.grab_object = pygame.transform.scale(self.grab_object, (50,50))
        self.grab_rect = self.grab_object.get_rect()
        self.grab_mask = pygame.mask.from_surface(self.grab_object)
        self.grab_rect.x = posx
        self.rand_y = random.randrange(200, 500)
        self.grab_rect.y = self.rand_y
        self.grab_mask_img = self.grab_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.temp_object = pygame.image.load('images/hook_sprite.png')
        self.temp_object = pygame.transform.scale(self.temp_object, (50,50))
        self.temp_rect = self.temp_object.get_rect()
        self.temp_rect.x = self.width//2
        self.temp_rect.y = self.height//2
        self.temp_mask = pygame.mask.from_surface(self.temp_object)
        self.temp_mask_img = self.temp_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.obj_rod = pygame.image.load('images/fish_rod.png')
        self.obj_rod = pygame.transform.scale(self.obj_rod, (50, 500))
        self.rod_rect = self.obj_rod.get_rect()
        self.rod_rect.x = posx+5
        self.rod_rect.y = self.rand_y-492

        self.crab = pygame.image.load('images/crab_sprite2.png')
        self.crab = pygame.transform.scale(self.crab, (30,30))
        self.crab_rect = self.crab.get_rect()
        self.crab_rect.x = posx-5
        self.crab_rect.y = self.rand_y+10

        self.crab_mask = pygame.mask.from_surface(self.crab)
        self.crab_mask_img = self.crab_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0, 0))

        self.player = player
        self.camera = camera

        self.object_offset_x = 0
        self.object_offset_y = 0

        self.dict_of_objects = {}

        self.obtain = False

        self.check_crab_coll = False
        self.verify_coll = False

        self.crab_coll = 0


    def generateObj(self, hook_rect, hook_mask):

        grab_obj_loc = self.grab_rect.x-self.camera.offset.x

        #if (grab_obj_loc < -50):
        #    self.grab_rect.x += self.width+50
        #    self.rod_rect.x += self.width+50
        #    self.crab_rect.x += self.width+50
        #    self.check_crab_coll = False

        self.player.mask_collision(self.player.rotate_mask, hook_mask, self.player.rotate_rect, hook_rect, self.camera)
        #self.player.mask_collision(self.player.rotate_mask, self.temp_mask, self.player.rotate_rect, self.temp_rect, self.object_offset_x, self.camera)

        self.crab_collision()

        
        if (self.grab_rect.x > 800):
            if (self.camera.camera_off):
                self.screen.blit(self.obj_rod,((self.rod_rect.x-self.camera.cam_offset_prev), self.rod_rect.y))
                #self.screen.blit(self.grab_mask_img, ((hook_rect.x-self.camera.cam_offset_prev), hook_rect.y))
                self.screen.blit(self.grab_object, ((hook_rect.x-self.camera.cam_offset_prev), hook_rect.y))

                #self.screen.blit(self.temp_mask_img, ((self.temp_rect.x-self.camera.cam_offset_prev), self.temp_rect.y))

                #if (self.check_crab_coll == False):
                #    self.screen.blit(self.crab_mask_img, ((self.crab_rect.x-self.camera.cam_offset_prev), self.crab_rect.y))
                #   self.screen.blit(self.crab, ((self.crab_rect.x-self.camera.cam_offset_prev), self.crab_rect.y))
            else:
                self.screen.blit(self.obj_rod,((self.rod_rect.x-self.camera.offset.x), self.rod_rect.y))
                #self.screen.blit(self.grab_mask_img, ((hook_rect.x-self.camera.offset.x), hook_rect.y))
                self.screen.blit(self.grab_object, ((hook_rect.x-self.camera.offset.x), hook_rect.y))

                #self.screen.blit(self.temp_mask_img, ((self.temp_rect.x-self.camera.offset.x), self.temp_rect.y))

                #if (self.check_crab_coll == False):
                #    self.screen.blit(self.crab_mask_img, ((self.crab_rect.x-self.camera.offset.x), self.crab_rect.y))
                #    self.screen.blit(self.crab, ((self.crab_rect.x-self.camera.offset.x), self.crab_rect.y))

                #self.screen.blit(self.crab, ((self.crab_rect.x-self.camera.offset.x), self.crab_rect.y))

        #debug(crab_coll, self.screen)

    def crab_collision(self):

        mask_offset_x = self.player.rotate_rect.left - self.crab_rect.x
        mask_offset_y = self.player.rotate_rect.top - self.crab_rect.y

        mask_offset_x2 = self.player.rect.left - self.crab_rect.x
        mask_offset_y2 = self.player.rect.top - self.crab_rect.y

        if (self.crab_mask.overlap(self.player.rotate_mask, (mask_offset_x, mask_offset_y))):
            temp_mask = self.crab_mask.overlap_mask(self.player.rotate_mask, (mask_offset_x, mask_offset_y))
            self.check_crab_coll = True

        if (self.crab_mask.overlap(self.player.player_mask, (mask_offset_x, mask_offset_y))):
            self.check_crab_coll = True
