
import pygame
from pygame.locals import *
import random

pygame.init()

# create the window
width = 700
height = 600
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('VROOM')

# colors
gray = (100, 100, 100)
green = (75, 200, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 230, 0)

# road and marker sizes
road_width = 350
marker_width = 5
marker_height = 45

# lane coordinates
left_lane = 215
center_lane = 370
right_lane = 428
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (80, 0, 525, height)
left_edge_marker = (105, 0, marker_width, height)
left_edge_marker2 = (90, 0, marker_width, height)
right_edge_marker = (590, 0, marker_width, height)
right_edge_marker2 = (575, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = 350
player_y = 400

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 3
score = 0

class Vehicle(pygame.sprite.Sprite):
    
        def __init__(self, image, x, y):
            pygame.sprite.Sprite.__init__(self)
        
            # scale the image down so it's not wider than the lane
            image_scale = 60 / image.get_rect().width
            new_width = image.get_rect().width * image_scale
            new_height = image.get_rect().height * image_scale
            self.image = pygame.transform.scale(image, (new_width, new_height))
        
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]
        
class PlayerVehicle(Vehicle):
    
            def __init__(self, x, y):
                image = pygame.image.load('images/Black_viper.png')
                super().__init__(image, x, y)
        
# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)


# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png', 'Ambulance.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)
    
# load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# game loop
running = True
while running:
    
    clock.tick(fps)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        # move the player's car using the left/right arrow keys
        if event.type == KEYDOWN:
            
            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 116
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 116
            elif event.key == K_UP and player.rect.center[0] > left_lane:
                player.rect.x -= 90
            elif event.key == K_DOWN and player.rect.center[0] < right_lane:
                player.rect.x += 95
                
            # check if there's a side swipe collision after changing lanes
            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    
                    gameover = True
                    
                    # place the player's car next to other vehicle
                    # and determine where to position the crash image
                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            
     # draw the grass
    screen.fill(green)
    
    # draw the road
    pygame.draw.rect(screen, gray, road)
    
    # draw the edge markers
    pygame.draw.rect(screen, white, left_edge_marker)
    pygame.draw.rect(screen, white, left_edge_marker2)
    pygame.draw.rect(screen, white, right_edge_marker)
    pygame.draw.rect(screen, white, right_edge_marker2)
    
    # draw the lane markers
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, yellow, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, yellow, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))       
        
    # draw the player's car
    player_group.draw(screen)
    
    # add a vehicle
    if len(vehicle_group) < 2:
        
        # ensure there's enough gap between vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 2:
                add_vehicle = False
                
        if add_vehicle:
            
            # select a random lane
            lane = random.choice(lanes)
            
            # select a random vehicle image
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)
    
    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        
        # remove vehicle once it goes off screen
        if vehicle.rect.top >= height:
            vehicle.kill()
            
            # add to score
            score += 3
            
            # speed up the game after passing 10 vehicles
            if score > 0 and score % 10 == 0:
                speed += 1
    
    # draw the vehicles
    vehicle_group.draw(screen)
    
    # display the score
    font = pygame.font.Font(pygame.font.get_default_font(), 26)
    text = font.render('Score: ' + str(score), True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (350, 550)
    screen.blit(text, text_rect)
    
    # check if there's a head on collision
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]
            
    # display game over
    if gameover:
        screen.blit(crash, crash_rect)
        
        pygame.draw.rect(screen, red, (0, 275, width, 100))
        
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text = font.render('You crashed! Play again? (Press Spacebar to restart or esc key to quit)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 320)
        screen.blit(text, text_rect)
            
    pygame.display.update()

    # wait for user's input to play again or exit
    while gameover:
        
        clock.tick(fps)
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                gameover = False
                running = False
                
            # get the user's input ('Space' or n)
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    # reset the game
                    gameover = False
                    speed = 3
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_ESCAPE:
                    # exit the loops (Esc)
                    gameover = False
                    running = False

        
pygame.quit()

#VROOM designed by Parampreet Singh Ahedi, Aryan Belsare and Hrishit Panchal
#Sprites taken from https://opengameart.org/content/free-top-down-car-sprites-by-unlucky-studio